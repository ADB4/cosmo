"""
Pluggable PDF -> markdown extraction for Cosmo.

Two engines behind one interface:

  * MarkerExtractor    — layout-aware (VikParuchuri/marker + Surya models).
                         Loads its models once and reuses them across a batch.
                         Best headings/tables/reading-order. Heavy: torch on
                         MPS, several GB resident. Optional dependency.
  * PyMuPDFExtractor   — pymupdf4llm. Fast, no ML models, always available
                         (it is a core requirement). The fallback engine.

`extract_pdf_markdown()` runs the requested engine (Marker by default) and,
when `allow_fallback` is set, AUTOMATICALLY drops to pymupdf4llm if Marker
raises, is not installed, or returns degenerate output (near-empty per page —
the "unexpected scan" signal, since the corpus is all text-native and there is
no OCR path).

Docling is intentionally not implemented; the interface leaves room for a
`DoclingExtractor` with the same `.name` / `.extract()` shape.
"""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional

from backend.config import (
    EXTRACT_MIN_CHARS_PER_PAGE,
    PDF_ENGINE,
    PDF_FALLBACK_ENGINE,
)

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Result
# ---------------------------------------------------------------------------


@dataclass
class ExtractionResult:
    """Outcome of a PDF -> markdown extraction."""

    markdown: str
    engine_used: str           # the engine that actually produced `markdown`
    engine_requested: str      # what the caller asked for
    fell_back: bool            # True if the requested engine failed/degenerate
    pages: Optional[int]       # page count, when known
    notes: List[str] = field(default_factory=list)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def page_count(pdf_path: str) -> Optional[int]:
    """Best-effort page count via pymupdf (a pymupdf4llm dependency)."""
    try:
        import pymupdf  # noqa: PLC0415  (fitz)

        with pymupdf.open(pdf_path) as doc:
            return doc.page_count
    except Exception:  # pragma: no cover - diagnostics only
        try:
            import fitz  # older name

            with fitz.open(pdf_path) as doc:
                return doc.page_count
        except Exception:
            return None


def _is_degenerate(markdown: str, pages: Optional[int]) -> bool:
    """
    True when extracted text is implausibly sparse for the page count — the
    signal that the engine failed on this document (e.g. an unexpected scan).
    """
    text = markdown.strip()
    if not text:
        return True
    if pages and pages > 0:
        return (len(text) / pages) < EXTRACT_MIN_CHARS_PER_PAGE
    # Unknown page count: only reject if essentially empty.
    return len(text) < EXTRACT_MIN_CHARS_PER_PAGE


# ---------------------------------------------------------------------------
# Engines
# ---------------------------------------------------------------------------


class PyMuPDFExtractor:
    """Fast, model-free extraction via pymupdf4llm. Always available."""

    name = "pymupdf4llm"

    def extract(self, pdf_path: str) -> str:
        import pymupdf4llm  # noqa: PLC0415

        return pymupdf4llm.to_markdown(pdf_path)

    def release(self) -> None:  # nothing to free
        pass


class MarkerExtractor:
    """
    Layout-aware extraction via marker-pdf. Loads Surya models once on first
    use and reuses them for every subsequent document, so a batch pays the
    (large) model-load cost a single time.

    marker-pdf is optional; importing it is deferred to `extract()` so the rest
    of Cosmo runs without it. `release()` drops the models and frees MPS memory
    — the Flask server calls it after an ingest so several GB of extractor
    memory does not sit resident next to a large chat model.
    """

    name = "marker"

    # Markdown image references (Marker still emits these even with image
    # extraction disabled — the target files are never written, so the refs are
    # dead noise in a study-tool chunk).
    _IMG_REF_RE = re.compile(r"!\[[^\]]*\]\([^)]*\)")

    def __init__(self) -> None:
        self._converter = None
        self._models = None

    def _ensure_loaded(self) -> None:
        if self._converter is not None:
            return
        # Import here so a missing marker-pdf only affects the Marker path.
        from marker.converters.pdf import PdfConverter  # noqa: PLC0415
        from marker.models import create_model_dict  # noqa: PLC0415

        logger.info("Loading Marker models (first PDF only)...")
        self._models = create_model_dict()  # auto-selects MPS on Apple Silicon
        self._converter = PdfConverter(
            artifact_dict=self._models,
            # Text-native corpus: we don't consume extracted images, and
            # skipping them keeps the run leaner.
            config={"disable_image_extraction": True},
        )

    def extract(self, pdf_path: str) -> str:
        self._ensure_loaded()
        from marker.output import text_from_rendered  # noqa: PLC0415

        rendered = self._converter(str(pdf_path))
        text, _ext, _images = text_from_rendered(rendered)
        return self._strip_dead_image_refs(text)

    @classmethod
    def _strip_dead_image_refs(cls, text: str) -> str:
        """Remove dead ![](...) image references and any blank lines left
        behind, without touching normal links or text."""
        text = cls._IMG_REF_RE.sub("", text)
        # Collapse runs of 3+ newlines created by removed image-only lines.
        text = re.sub(r"\n[ \t]*\n[ \t]*\n+", "\n\n", text)
        return text

    def release(self) -> None:
        """Drop the models and free MPS/torch memory."""
        self._converter = None
        self._models = None
        try:
            import gc

            gc.collect()
            import torch  # noqa: PLC0415

            if torch.backends.mps.is_available():
                torch.mps.empty_cache()
        except Exception:  # pragma: no cover - best effort
            pass


# ---------------------------------------------------------------------------
# Top-level extraction with automatic fallback
# ---------------------------------------------------------------------------


def _resolve_engine(name: str, marker: Optional[MarkerExtractor]):
    """Return a usable extractor instance for an engine name."""
    if name == "marker":
        return marker or MarkerExtractor()
    if name == "pymupdf4llm":
        return PyMuPDFExtractor()
    raise ValueError(
        f"Unknown PDF engine '{name}'. Valid: marker, pymupdf4llm."
    )


def extract_pdf_markdown(
    pdf_path: str,
    engine: Optional[str] = None,
    allow_fallback: bool = True,
    marker: Optional[MarkerExtractor] = None,
) -> ExtractionResult:
    """
    Extract a PDF to markdown using `engine` (default: config PDF_ENGINE),
    falling back to pymupdf4llm when the primary engine fails or returns
    degenerate output.

    Args:
        pdf_path: Path to the PDF.
        engine: "marker" or "pymupdf4llm". Defaults to config.PDF_ENGINE.
        allow_fallback: If True (default), silently drop to the fallback engine
            on error / degenerate output. If False, surface the error.
        marker: A preloaded MarkerExtractor to reuse across a batch (avoids
            reloading models per file). Created on demand when omitted.

    Returns:
        ExtractionResult with the markdown and which engine produced it.
    """
    requested = engine or PDF_ENGINE
    pages = page_count(pdf_path)
    notes: List[str] = []

    # -- primary engine ---------------------------------------------------
    primary = _resolve_engine(requested, marker)
    primary_md = ""
    primary_failed = False
    try:
        primary_md = primary.extract(pdf_path)
    except ImportError as e:
        primary_failed = True
        notes.append(f"{requested} not installed ({e}); using {PDF_FALLBACK_ENGINE}.")
        logger.warning("Engine '%s' unavailable: %s", requested, e)
    except Exception as e:  # noqa: BLE001 - any extractor error -> fallback
        primary_failed = True
        notes.append(f"{requested} failed ({e}); using {PDF_FALLBACK_ENGINE}.")
        logger.warning("Engine '%s' failed on %s: %s", requested, pdf_path, e)

    if not primary_failed and _is_degenerate(primary_md, pages):
        primary_failed = True
        notes.append(
            f"{requested} returned degenerate output "
            f"({len(primary_md.strip())} chars / {pages or '?'} pages); "
            f"using {PDF_FALLBACK_ENGINE}."
        )
        logger.warning(
            "Engine '%s' degenerate on %s (%d chars, %s pages)",
            requested, pdf_path, len(primary_md.strip()), pages,
        )

    if not primary_failed:
        return ExtractionResult(
            markdown=primary_md,
            engine_used=requested,
            engine_requested=requested,
            fell_back=False,
            pages=pages,
            notes=notes,
        )

    # -- fallback ---------------------------------------------------------
    if not allow_fallback or requested == PDF_FALLBACK_ENGINE:
        # No fallback available/allowed — return whatever the primary gave.
        return ExtractionResult(
            markdown=primary_md,
            engine_used=requested,
            engine_requested=requested,
            fell_back=False,
            pages=pages,
            notes=notes,
        )

    fallback = _resolve_engine(PDF_FALLBACK_ENGINE, None)
    fallback_md = fallback.extract(pdf_path)
    return ExtractionResult(
        markdown=fallback_md,
        engine_used=PDF_FALLBACK_ENGINE,
        engine_requested=requested,
        fell_back=True,
        pages=pages,
        notes=notes,
    )
