"""
Conservative LLM cleanup of raw extracted markdown, before chunking.

This is deliberately NOT a rewrite pass. Because the output feeds a study
tool, hallucination is the primary risk, so the model is constrained to three
mechanical fixes only:

  1. Remove running headers/footers that repeat page after page, and standalone
     page numbers.
  2. Repair broken markdown tables so rows/columns are valid (never changing the
     data in the cells).
  3. Normalize heading levels so the hierarchy is consistent (never renaming a
     heading).

Safeguards:
  * Runs on a small deterministic instruct model (qwen2.5:14b), temperature 0,
    think=False.
  * Processed in windows split at blank lines and never inside a fenced code
    block, so tables/code are not cut mid-structure.
  * Every window is length-checked against its original: if the cleaned text is
    too short (content dropped) or longer (content invented), the ORIGINAL
    window is kept. A window that errors or comes back empty also keeps the
    original. Cleanup can only ever remove boilerplate — it can never lose your
    content.
  * If Ollama is unreachable, cleanup is skipped and the raw markdown is
    returned unchanged.
"""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass
from typing import Callable, List, Optional

import ollama

from backend.config import (
    CLEANUP_MAX_RATIO,
    CLEANUP_MIN_RATIO,
    CLEANUP_MODEL,
    CLEANUP_OPTIONS,
    CLEANUP_WINDOW_CHARS,
)

logger = logging.getLogger(__name__)

_THINK_RE = re.compile(r"<think>.*?</think>", re.DOTALL)


def _strip_think(text: str) -> str:
    """Remove <think>...</think> spans (belt-and-braces; we pass think=False)."""
    cleaned = _THINK_RE.sub("", text)
    if "<think>" in cleaned and "</think>" not in cleaned:
        cleaned = cleaned.split("<think>", 1)[0]
    return cleaned.strip()


def _unwrap_code_fence(text: str) -> str:
    """
    Undo a model that wrapped its ENTIRE answer in one ```...``` fence
    (e.g. ```markdown\n...\n```). Only unwraps when the whole output is a single
    fenced block — an internal code block in a normal answer is left alone.
    """
    stripped = text.strip()
    lines = stripped.split("\n")
    if len(lines) >= 2 and lines[0].startswith("```") and lines[-1].strip() == "```":
        # exactly two fence markers -> the whole thing is one wrapper block
        if sum(1 for ln in lines if ln.lstrip().startswith("```")) == 2:
            return "\n".join(lines[1:-1]).strip()
    return stripped


# ---------------------------------------------------------------------------
# Windowing
# ---------------------------------------------------------------------------


def split_windows(md: str, window_chars: int = CLEANUP_WINDOW_CHARS) -> List[str]:
    """
    Split markdown into windows for per-call cleanup.

    Breaks preferentially at blank lines once a window reaches `window_chars`,
    and never inside a fenced code block. A hard cap at 2x `window_chars`
    bounds pathological runs with no blank lines.
    """
    lines = md.split("\n")
    windows: List[str] = []
    cur: List[str] = []
    cur_len = 0
    in_fence = False

    def flush() -> None:
        nonlocal cur, cur_len
        chunk = "\n".join(cur).strip("\n")
        if chunk.strip():
            windows.append(chunk)
        cur = []
        cur_len = 0

    for line in lines:
        is_fence = line.lstrip().startswith("```")

        # Preferred break: at a blank line once we're over the target size.
        if (not in_fence) and cur_len >= window_chars and line.strip() == "":
            flush()
            continue  # drop the separating blank; windows re-joined with \n\n

        # Hard cap: bound window size even without a blank line.
        if (not in_fence) and cur_len >= 2 * window_chars:
            flush()

        cur.append(line)
        cur_len += len(line) + 1
        if is_fence:
            in_fence = not in_fence

    flush()
    return windows


# ---------------------------------------------------------------------------
# Prompt
# ---------------------------------------------------------------------------

_SYSTEM = (
    "You are a Markdown cleanup tool, not an author. You receive a fragment of "
    "Markdown that was extracted from a PDF. Return the SAME content with only "
    "these mechanical fixes applied:\n"
    "1. Remove running headers and footers that repeat on every page (book or "
    "chapter titles, author names, website URLs) and standalone page numbers.\n"
    "2. Repair broken Markdown tables so the table syntax is valid and columns "
    "align. Never change the data inside the cells.\n"
    "3. Normalize heading levels so the document hierarchy is consistent (for "
    "example a chapter as #, its sections as ##). Never rename a heading.\n\n"
    "Do NOT summarize, rephrase, translate, add, or remove any real content. "
    "Preserve all prose, code blocks, math, lists, and links exactly as written. "
    "Do NOT wrap your answer in a code fence and do NOT add any commentary, "
    "preamble, or explanation. If nothing needs fixing, return the fragment "
    "unchanged.\n\n"
    "Return only the cleaned Markdown fragment."
)


def _clean_window(text: str, model: str, options: dict) -> str:
    resp = ollama.chat(
        model=model,
        messages=[
            {"role": "system", "content": _SYSTEM},
            {"role": "user", "content": text},
        ],
        think=False,
        stream=False,
        options=options,
    )
    content = resp["message"]["content"]
    content = _strip_think(content)
    content = _unwrap_code_fence(content)
    return content.strip()


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


@dataclass
class CleanupResult:
    markdown: str
    model: str
    windows_total: int
    windows_cleaned: int   # windows where the model's output was accepted
    windows_reverted: int  # windows kept as the original (guard tripped/error)
    skipped: bool = False  # True if cleanup was skipped entirely (Ollama down)


def clean_markdown(
    md: str,
    model: str = CLEANUP_MODEL,
    window_chars: int = CLEANUP_WINDOW_CHARS,
    options: Optional[dict] = None,
    min_ratio: float = CLEANUP_MIN_RATIO,
    max_ratio: float = CLEANUP_MAX_RATIO,
    progress: Optional[Callable[[int, int], None]] = None,
) -> CleanupResult:
    """
    Run the conservative cleanup pass over `md`.

    Never raises on model/connection problems: on any per-window failure the
    original window is kept, and if Ollama is unreachable the raw markdown is
    returned unchanged (skipped=True).
    """
    opts = dict(options or CLEANUP_OPTIONS)

    if not md.strip():
        return CleanupResult(md, model, 0, 0, 0, skipped=True)

    # Fail fast and safe if Ollama isn't up — return the raw markdown.
    try:
        ollama.list()
    except Exception as e:  # noqa: BLE001
        logger.warning("Cleanup skipped — Ollama unreachable: %s", e)
        return CleanupResult(md, model, 0, 0, 0, skipped=True)

    windows = split_windows(md, window_chars=window_chars)
    total = len(windows)
    out: List[str] = []
    cleaned_count = 0
    reverted_count = 0

    for i, window in enumerate(windows):
        original = window
        try:
            candidate = _clean_window(original, model, opts)
        except Exception as e:  # noqa: BLE001 - keep original on any error
            logger.warning("Cleanup window %d/%d errored (%s); keeping original",
                           i + 1, total, e)
            out.append(original)
            reverted_count += 1
            if progress:
                progress(i + 1, total)
            continue

        orig_len = len(original)
        cand_len = len(candidate)
        accepted = bool(candidate) and (
            min_ratio * orig_len <= cand_len <= max_ratio * orig_len
        )

        if accepted:
            out.append(candidate)
            cleaned_count += 1
        else:
            reason = "empty" if not candidate else f"ratio {cand_len/max(orig_len,1):.2f}"
            logger.info("Cleanup window %d/%d reverted (%s)", i + 1, total, reason)
            out.append(original)
            reverted_count += 1

        if progress:
            progress(i + 1, total)

    return CleanupResult(
        markdown="\n\n".join(out),
        model=model,
        windows_total=total,
        windows_cleaned=cleaned_count,
        windows_reverted=reverted_count,
        skipped=False,
    )
