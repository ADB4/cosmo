"""
Document Processor — core RAG engine for Cosmo.

Handles ingestion of PDFs and markdown files into a ChromaDB vector store,
querying with semantic search, and streaming LLM answers via Ollama.
"""

import hashlib
import logging
import re
from collections import deque
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, Generator, List, Optional, Tuple

import chromadb
import ollama

from backend.config import (
    CHAT_MODELS,
    CHAT_OPTIONS,
    CHUNK_OVERLAP,
    CHUNK_SIZE,
    CLEANUP_ENABLED,
    CLEANUP_MODEL,
    DB_PATH,
    DEFAULT_MODE,
    EMBED_MODEL,
    EMBEDDING_BATCH_SIZE,
    EXTRACT_CACHE_DIR,
    EXTRACT_CACHE_ENABLED,
    PDF_ENGINE,
    PDF_FALLBACK_ENGINE,
)
from backend.md_cleanup import clean_markdown
from backend.pdf_extract import MarkerExtractor, extract_pdf_markdown

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Reasoning-token stripping
#
# Qwen3 and gemma4 emit chain-of-thought by default. We pass think=False to
# every ollama.chat call, but as a defence-in-depth measure we also strip any
# <think>...</think> spans that leak into the visible content — both from the
# streamed chat tokens (via ThinkStripper, which handles tags split across
# chunk boundaries) and from the one-shot grader response (via strip_think).
# ---------------------------------------------------------------------------

_THINK_OPEN = "<think>"
_THINK_CLOSE = "</think>"
_THINK_RE = re.compile(r"<think>.*?</think>", re.DOTALL)


def strip_think(text: str) -> str:
    """Remove complete <think>...</think> spans from a whole (non-streamed) string."""
    cleaned = _THINK_RE.sub("", text)
    # Drop a dangling open tag with no close (truncated reasoning).
    if _THINK_OPEN in cleaned and _THINK_CLOSE not in cleaned:
        cleaned = cleaned.split(_THINK_OPEN, 1)[0]
    return cleaned.strip()


def _safe_tail_len(buf: str, tag: str) -> int:
    """Length of the longest suffix of `buf` that is a proper prefix of `tag`."""
    maxk = min(len(tag) - 1, len(buf))
    for k in range(maxk, 0, -1):
        if buf[-k:] == tag[:k]:
            return k
    return 0


class ThinkStripper:
    """
    Streaming filter that removes <think>...</think> spans from a token
    sequence. Buffers just enough to catch a tag split across chunk
    boundaries; everything outside think spans is emitted as soon as it is
    unambiguous. Call flush() at end-of-stream to release any trailing text.
    """

    def __init__(self) -> None:
        self._buf = ""
        self._in_think = False

    def feed(self, token: str) -> str:
        self._buf += token
        out = ""
        while True:
            if not self._in_think:
                idx = self._buf.find(_THINK_OPEN)
                if idx == -1:
                    keep = _safe_tail_len(self._buf, _THINK_OPEN)
                    emit_to = len(self._buf) - keep
                    out += self._buf[:emit_to]
                    self._buf = self._buf[emit_to:]
                    break
                out += self._buf[:idx]
                self._buf = self._buf[idx + len(_THINK_OPEN):]
                self._in_think = True
            else:
                idx = self._buf.find(_THINK_CLOSE)
                if idx == -1:
                    keep = _safe_tail_len(self._buf, _THINK_CLOSE)
                    self._buf = self._buf[len(self._buf) - keep:]
                    break
                self._buf = self._buf[idx + len(_THINK_CLOSE):]
                self._in_think = False
        return out

    def flush(self) -> str:
        out = "" if self._in_think else self._buf
        self._buf = ""
        return out


# ---------------------------------------------------------------------------
# Exceptions
# ---------------------------------------------------------------------------


class OllamaConnectionError(Exception):
    """Raised when Ollama is not reachable."""


# ---------------------------------------------------------------------------
# Chat history
# ---------------------------------------------------------------------------


class ChatHistory:
    """Rolling window of conversation exchanges for multi-turn context."""

    def __init__(self, max_turns: int = 5):
        self.max_turns = max_turns
        self._history: deque[Tuple[str, str]] = deque(maxlen=max_turns)

    def add(self, question: str, answer: str) -> None:
        self._history.append((question, answer))

    def clear(self) -> None:
        self._history.clear()

    def format_for_prompt(self) -> str:
        if not self._history:
            return ""
        parts = []
        for q, a in self._history:
            truncated_a = a[:600] + "..." if len(a) > 600 else a
            parts.append(f"User: {q}\nAssistant: {truncated_a}")
        return "Previous conversation:\n" + "\n\n".join(parts)

    @property
    def turn_count(self) -> int:
        return len(self._history)

    def __len__(self) -> int:
        return len(self._history)


# ---------------------------------------------------------------------------
# Markdown section parsing
# ---------------------------------------------------------------------------


@dataclass
class MarkdownSection:
    """A logical section extracted from a markdown file."""

    heading: str          # e.g. "## Props and State"
    heading_text: str     # e.g. "Props and State"
    heading_level: int    # e.g. 2
    body: str             # The text content under this heading
    breadcrumb: List[str] # e.g. ["React Basics", "Components", "Props and State"]
    item_number: Optional[str] = None   # e.g. "23" if heading matches Item pattern
    item_title: Optional[str] = None    # e.g. "Create Objects All at Once"

    @property
    def breadcrumb_path(self) -> str:
        """Slash-separated breadcrumb for metadata storage."""
        return " > ".join(self.breadcrumb)


@dataclass
class ChunkWithMetadata:
    """A text chunk with all the metadata needed for ChromaDB storage."""

    text: str
    metadata: Dict[str, str]


# Regex for "Item 23: Create Objects All at Once" pattern
_ITEM_PATTERN = re.compile(r"^Item\s+(\d+):\s+(.+)$")


def parse_markdown_sections(
    content: str,
    top_level_only: bool = False,
) -> List[MarkdownSection]:
    """
    Parse markdown into sections split by headings, preserving hierarchy.

    Args:
        content: Raw markdown text.
        top_level_only: If True, only split on level-1 and level-2 headings.
            All deeper headings (###, ####, etc.) are kept as part of
            the parent section's body. Useful for book-style documents
            where each ## is a self-contained chapter or "Item".

    Handles:
    - ATX headings (# through ######)
    - Content before the first heading (assigned level 0, heading "Introduction")
    - Nested heading breadcrumbs (an h3 under an h2 under an h1 gets all three)
    - Headings inside fenced code blocks are skipped
    - "Item N: Title" pattern extraction into metadata fields
    """
    lines = content.split("\n")
    heading_pattern = re.compile(r"^(#{1,6})\s+(.+)$")

    # First pass: identify all heading positions
    heading_positions: List[Tuple[int, int, str]] = []  # (line_idx, level, text)
    in_code_block = False

    for i, line in enumerate(lines):
        if line.strip().startswith("```"):
            in_code_block = not in_code_block
            continue
        if in_code_block:
            continue

        match = heading_pattern.match(line)
        if match:
            level = len(match.group(1))
            text = match.group(2).strip()
            heading_positions.append((i, level, text))

    # When top_level_only is True, only level-1 and level-2 headings
    # become section split points. Deeper headings stay in the body text.
    if top_level_only:
        split_positions = [
            (line_num, level, text)
            for line_num, level, text in heading_positions
            if level <= 2
        ]
    else:
        split_positions = heading_positions

    # Second pass: extract sections with body text
    sections: List[MarkdownSection] = []

    # Handle content before first heading
    first_heading_line = split_positions[0][0] if split_positions else len(lines)
    preamble = "\n".join(lines[:first_heading_line]).strip()
    if preamble:
        sections.append(MarkdownSection(
            heading="",
            heading_text="Introduction",
            heading_level=0,
            body=preamble,
            breadcrumb=["Introduction"],
        ))

    # Build breadcrumb stack: tracks the most recent heading at each level
    breadcrumb_stack: Dict[int, str] = {}

    for idx, (line_num, level, text) in enumerate(split_positions):
        # Determine where this section's body ends
        if idx + 1 < len(split_positions):
            next_line = split_positions[idx + 1][0]
        else:
            next_line = len(lines)

        body = "\n".join(lines[line_num + 1 : next_line]).strip()

        # Update breadcrumb: set this level, clear anything deeper
        breadcrumb_stack[level] = text
        for deeper_level in list(breadcrumb_stack.keys()):
            if deeper_level > level:
                del breadcrumb_stack[deeper_level]

        # Build ordered breadcrumb from the stack
        breadcrumb = [
            breadcrumb_stack[lvl]
            for lvl in sorted(breadcrumb_stack.keys())
        ]

        # Check for "Item N: Title" pattern
        item_match = _ITEM_PATTERN.match(text)
        item_number = item_match.group(1) if item_match else None
        item_title = item_match.group(2).strip() if item_match else None

        sections.append(MarkdownSection(
            heading="#" * level + " " + text,
            heading_text=text,
            heading_level=level,
            body=body,
            breadcrumb=breadcrumb,
            item_number=item_number,
            item_title=item_title,
        ))

    return sections


def chunk_section(
    section: MarkdownSection,
    max_size: int = CHUNK_SIZE,
    overlap: int = CHUNK_OVERLAP,
) -> List[str]:
    """
    Chunk a single section's body text, respecting paragraph boundaries.
    Overlap is applied only within the section (never across headings).

    The heading line is prepended to the FIRST chunk so the embedding
    captures what section the content belongs to.
    """
    body = section.body
    if not body.strip():
        return []

    paragraphs = body.split("\n\n")
    raw_chunks: List[str] = []
    current = ""

    for para in paragraphs:
        para = para.strip()
        if not para:
            continue

        if len(current) + len(para) + 2 <= max_size:
            current += ("" if not current else "\n\n") + para
        else:
            if current:
                raw_chunks.append(current)
            # Handle paragraphs longer than max_size
            if len(para) > max_size:
                words = para.split()
                temp = ""
                for word in words:
                    if len(temp) + len(word) + 1 <= max_size:
                        temp += ("" if not temp else " ") + word
                    else:
                        if temp:
                            raw_chunks.append(temp)
                        temp = word
                current = temp
            else:
                current = para

    if current:
        raw_chunks.append(current)

    if not raw_chunks:
        return []

    # Apply overlap: prepend tail of previous chunk to current chunk
    overlapped: List[str] = []
    for i, chunk in enumerate(raw_chunks):
        if i == 0:
            # Prepend the heading to the first chunk for embedding context
            prefix = section.heading + "\n\n" if section.heading else ""
            overlapped.append(prefix + chunk)
        else:
            prev_text = raw_chunks[i - 1]
            # Take the last `overlap` characters, snapped to a word boundary
            tail = prev_text[-overlap:]
            first_space = tail.find(" ")
            if first_space != -1:
                tail = tail[first_space + 1 :]
            overlapped.append(f"[...] {tail}\n\n{chunk}")

    return overlapped


def chunk_markdown_file(
    content: str,
    filename: str,
    file_hash: str,
    max_size: int = CHUNK_SIZE,
    overlap: int = CHUNK_OVERLAP,
    top_level_only: bool = False,
) -> List[ChunkWithMetadata]:
    """
    Full pipeline: parse markdown into sections, chunk each section,
    and attach rich metadata to every chunk.

    Args:
        top_level_only: Passed through to parse_markdown_sections.
            When True, only splits on level-1/2 headings — useful for
            book-style documents like Effective TypeScript.
    """
    sections = parse_markdown_sections(content, top_level_only=top_level_only)
    results: List[ChunkWithMetadata] = []

    for section_idx, section in enumerate(sections):
        chunks = chunk_section(section, max_size=max_size, overlap=overlap)

        for chunk_in_section_idx, chunk_text in enumerate(chunks):
            metadata = {
                "source": filename,
                "file_hash": file_hash,
                "doc_type": "markdown",
                "heading": section.heading_text,
                "heading_level": str(section.heading_level),
                "breadcrumb": section.breadcrumb_path,
                "chunk_index_in_section": str(chunk_in_section_idx),
                "section_index": str(section_idx),
            }

            # Add Item metadata when present
            if section.item_number is not None:
                metadata["item_number"] = section.item_number
            if section.item_title is not None:
                metadata["item_title"] = section.item_title

            results.append(ChunkWithMetadata(
                text=chunk_text,
                metadata=metadata,
            ))

    return results


# ---------------------------------------------------------------------------
# Document processor
# ---------------------------------------------------------------------------


def collection_name_for(embed_model: str) -> str:
    """
    Map an embedding-model tag to its Chroma collection name.

    nomic-embed-text keeps the historical name so the existing chroma_db is
    reused as-is (no re-ingest needed). Every other embedder gets its own
    `docs_<model>` collection, so switching models via COSMO_EMBED_MODEL never
    queries vectors from an incompatible space.
    """
    if embed_model == "nomic-embed-text":
        return "react_typescript_docs"
    safe = embed_model.replace(":", "-").replace("/", "-")
    return f"docs_{safe}"


class DocumentProcessor:
    """Process, index, and query technical documentation via RAG."""

    EMBEDDING_BATCH_SIZE = EMBEDDING_BATCH_SIZE

    def __init__(self, persist_dir: str | None = None, embed_model: str | None = None):
        import tiktoken
        self._tokenizer = tiktoken.get_encoding("cl100k_base")
        self._check_ollama_connection()
        self.client = chromadb.PersistentClient(path=persist_dir or DB_PATH)
        self.embed_model = embed_model or EMBED_MODEL
        # Name the collection after the embedding model so switching embedders
        # never mixes incompatible vector spaces. The historical nomic
        # collection is preserved under its stable name.
        self.collection = self.client.get_or_create_collection(
            name=collection_name_for(self.embed_model),
            metadata={"hnsw:space": "cosine"},
        )
        self.models = CHAT_MODELS
        # Lazily-created, reused across a batch so Marker loads its models once.
        self._marker: MarkerExtractor | None = None

    # -- connection check ---------------------------------------------------

    @staticmethod
    def _check_ollama_connection() -> None:
        try:
            ollama.list()
        except Exception as e:
            raise OllamaConnectionError(
                "Cannot connect to Ollama. "
                "Make sure it's running:\n"
                f"  ollama serve\nOriginal error: {e}"
            )

    # -- PDF to markdown conversion -----------------------------------------

    def _get_marker(self) -> MarkerExtractor:
        """The processor's reusable Marker extractor (models load once)."""
        if self._marker is None:
            self._marker = MarkerExtractor()
        return self._marker

    def release_extractor(self) -> None:
        """
        Free the Marker models / MPS memory. The CLI calls this at the end of a
        batch; the Flask server calls it after each ingest so several GB of
        extractor memory does not sit resident next to a large chat model.
        """
        if self._marker is not None:
            self._marker.release()

    @staticmethod
    def _extract_cache_path(file_hash: str, engine: str, cleanup: bool):
        """On-disk path for cached extracted markdown, keyed so a different
        engine or cleanup setting never collides."""
        stage = "clean" if cleanup else "raw"
        return EXTRACT_CACHE_DIR / f"{file_hash}.{engine}.{stage}.md"

    def pdf_to_markdown(
        self,
        pdf_path: str,
        engine: str | None = None,
        cleanup: bool = False,
    ) -> str:
        """
        Convert a PDF to markdown via the pluggable extractor (Marker by
        default, automatic pymupdf4llm fallback). Extraction only unless
        `cleanup=True`, which additionally runs the conservative LLM cleanup
        pass (and therefore needs Ollama).

        This is a thin wrapper over `extract_pdf_markdown`; ingestion uses the
        cache-aware `_get_pdf_markdown` instead.
        """
        result = extract_pdf_markdown(
            pdf_path,
            engine=engine or PDF_ENGINE,
            allow_fallback=True,
            marker=self._get_marker(),
        )
        md = result.markdown
        if cleanup and md.strip():
            md = clean_markdown(md).markdown
        return md

    def _get_pdf_markdown(
        self,
        pdf_path: str,
        file_hash: str,
        engine: str,
        cleanup: bool,
        reextract: bool,
    ) -> str:
        """
        Extract (+ optionally clean) a PDF to markdown, using the on-disk cache
        so Marker and the cleanup pass are not re-run for an unchanged file.
        """
        cache_path = self._extract_cache_path(file_hash, engine, cleanup)

        if EXTRACT_CACHE_ENABLED and not reextract and cache_path.exists():
            print(f"  Using cached extraction: {cache_path.name}")
            return cache_path.read_text(encoding="utf-8")

        print(f"  Extracting with {engine} (auto-fallback: {PDF_FALLBACK_ENGINE})...")
        result = extract_pdf_markdown(
            pdf_path,
            engine=engine,
            allow_fallback=True,
            marker=self._get_marker(),
        )
        for note in result.notes:
            print(f"    note: {note}")
        if result.fell_back:
            print(f"  Fell back to {result.engine_used}")
        else:
            print(f"  Extracted with {result.engine_used}"
                  f"{f' ({result.pages} pages)' if result.pages else ''}")

        md = result.markdown
        if not md.strip():
            return md

        if cleanup:
            print(f"  Cleaning markdown with {CLEANUP_MODEL} (conservative pass)...")
            cres = clean_markdown(md, progress=self._cleanup_progress)
            if cres.skipped:
                print("    cleanup skipped (Ollama unreachable) — using raw extraction")
            else:
                print(f"    cleaned {cres.windows_cleaned}/{cres.windows_total} windows "
                      f"({cres.windows_reverted} kept unchanged)")
            md = cres.markdown

        if EXTRACT_CACHE_ENABLED:
            try:
                cache_path.parent.mkdir(parents=True, exist_ok=True)
                cache_path.write_text(md, encoding="utf-8")
            except Exception as e:  # noqa: BLE001 - cache is best-effort
                logger.warning(f"Could not write extraction cache: {e}")

        return md

    @staticmethod
    def _cleanup_progress(done: int, total: int) -> None:
        if total and (done == total or done % 10 == 0):
            print(f"    cleanup {done}/{total} windows...")

    # -- hashing / dedup ----------------------------------------------------

    @staticmethod
    def get_file_hash(filepath: str) -> str:
        h = hashlib.md5()
        with open(filepath, "rb") as f:
            for block in iter(lambda: f.read(8192), b""):
                h.update(block)
        return h.hexdigest()

    def is_already_indexed(self, file_hash: str) -> bool:
        try:
            results = self.collection.get(where={"file_hash": file_hash}, limit=1)
            return len(results["ids"]) > 0
        except Exception as e:
            logger.warning(f"Error checking index status: {e}")
            return False

    def _delete_existing_chunks(self, file_hash: str) -> None:
        try:
            self.collection.delete(where={"file_hash": file_hash})
        except Exception as e:
            logger.warning(f"Error deleting existing chunks: {e}")

    # -- embedding ----------------------------------------------------------
    def _generate_embeddings_batch(self, texts: List[str]) -> List[List[float]]:
        from backend.config import EMBED_MAX_TOKENS

        truncated = []
        for text in texts:
            tokens = self._tokenizer.encode(text)
            if len(tokens) > EMBED_MAX_TOKENS:
                tokens = tokens[:EMBED_MAX_TOKENS]
                truncated.append(self._tokenizer.decode(tokens))
            else:
                truncated.append(text)

        try:
            response = ollama.embed(model=self.embed_model, input=truncated)
            return response["embeddings"]
        except Exception as e:
            logger.debug(f"Batch embed failed ({e}), falling back to one-at-a-time")

        embeddings = []
        for i, text in enumerate(truncated):
            try:
                response = ollama.embeddings(model=self.embed_model, prompt=text)
                embeddings.append(response["embedding"])
            except Exception as e:
                # Log the problem chunk and skip it with a zero vector
                token_count = len(self._tokenizer.encode(text))
                logger.warning(
                    f"Embedding failed for chunk {i} ({token_count} tokens, "
                    f"{len(text)} chars): {e}"
                )
                # Return a zero vector so indexing can continue
                if embeddings:
                    embeddings.append([0.0] * len(embeddings[0]))
                else:
                    # Need to get dimension from a successful embedding first
                    dummy = ollama.embeddings(model=self.embed_model, prompt="test")
                    dim = len(dummy["embedding"])
                    embeddings.append([0.0] * dim)
        return embeddings

    # -- ingestion ----------------------------------------------------------

    def ingest_pdf(
        self,
        pdf_path: str,
        force: bool = False,
        top_level_only: bool = False,
        engine: str | None = None,
        cleanup: bool | None = None,
        reextract: bool = False,
    ) -> int:
        """
        Convert PDF to markdown via the pluggable extractor (Marker by default,
        automatic pymupdf4llm fallback), optionally run the conservative LLM
        cleanup pass, then process with the heading-hierarchy-aware chunker.

        This gives PDFs the same rich metadata (headings, breadcrumbs,
        section-aware overlap) that native markdown files get.

        Args:
            top_level_only: Only split on level-1/2 headings. Useful for
                book-style PDFs like Effective TypeScript.
            engine: "marker" or "pymupdf4llm" (default: config PDF_ENGINE).
            cleanup: Run the markdown cleanup pass (default: config
                CLEANUP_ENABLED).
            reextract: Ignore the extraction cache and re-run extraction.
        """
        engine = engine or PDF_ENGINE
        cleanup = CLEANUP_ENABLED if cleanup is None else cleanup

        file_hash = self.get_file_hash(pdf_path)

        if not force and self.is_already_indexed(file_hash):
            print(f"{Path(pdf_path).name} already indexed (use --force to re-index)")
            return 0

        if force:
            self._delete_existing_chunks(file_hash)

        print(f"Processing: {Path(pdf_path).name}")
        filename = Path(pdf_path).name

        # Extract (+ optional cleanup) to markdown, reusing the on-disk cache
        # so Marker / cleanup are not re-run for an unchanged file.
        try:
            md_content = self._get_pdf_markdown(
                pdf_path, file_hash, engine, cleanup, reextract
            )
        except Exception as e:
            print(f"  Error converting PDF to markdown: {e}")
            return 0

        if not md_content.strip():
            print(f"  No content extracted from {filename}")
            return 0

        # Use the same heading-hierarchy chunker as native markdown files.
        # Source metadata still shows the original .pdf filename so you
        # know where the content came from.
        chunks_with_meta = chunk_markdown_file(
            content=md_content,
            filename=filename,
            file_hash=file_hash,
            max_size=CHUNK_SIZE,
            overlap=CHUNK_OVERLAP,
            top_level_only=top_level_only,
        )

        # Override doc_type so stats/filtering can distinguish PDFs
        for c in chunks_with_meta:
            c.metadata["doc_type"] = "pdf"

        if not chunks_with_meta:
            print(f"  No chunks produced from {filename}")
            return 0

        # Prepare batch arrays
        all_chunks = [c.text for c in chunks_with_meta]
        all_ids = [f"{file_hash}_{i}" for i in range(len(chunks_with_meta))]
        all_metadatas = [c.metadata for c in chunks_with_meta]

        # Generate embeddings in batches and store
        indexed = 0
        for batch_start in range(0, len(all_chunks), self.EMBEDDING_BATCH_SIZE):
            batch_end = min(batch_start + self.EMBEDDING_BATCH_SIZE, len(all_chunks))
            batch_texts = all_chunks[batch_start:batch_end]
            batch_ids = all_ids[batch_start:batch_end]
            batch_meta = all_metadatas[batch_start:batch_end]

            try:
                batch_embeddings = self._generate_embeddings_batch(batch_texts)
            except Exception as e:
                print(f"  Error generating embeddings for batch {batch_start}-{batch_end}: {e}")
                continue

            self.collection.add(
                ids=batch_ids,
                embeddings=batch_embeddings,
                documents=batch_texts,
                metadatas=batch_meta,
            )
            indexed += len(batch_ids)

            if batch_end < len(all_chunks):
                print(f"  Embedded {batch_end}/{len(all_chunks)} chunks...")

        print(f"Indexed {indexed} chunks from {filename}")
        return indexed

    def ingest_markdown(self, md_path: str, force: bool = False, top_level_only: bool = False) -> int:
        """
        Process markdown with heading-hierarchy-aware chunking.

        Splits on heading hierarchy, preserves heading text/level/breadcrumb
        path in metadata, and applies section-aware overlap that never bleeds
        across heading boundaries.

        Args:
            top_level_only: Only split on level-1/2 headings. Useful for
                book-style markdown where each ## is a chapter or Item.
        """
        file_hash = self.get_file_hash(md_path)

        if not force and self.is_already_indexed(file_hash):
            print(f"{Path(md_path).name} already indexed (use --force to re-index)")
            return 0

        if force:
            self._delete_existing_chunks(file_hash)

        print(f"Processing: {Path(md_path).name}")
        filename = Path(md_path).name

        with open(md_path, "r", encoding="utf-8") as f:
            content = f.read()

        chunks_with_meta = chunk_markdown_file(
            content=content,
            filename=filename,
            file_hash=file_hash,
            max_size=CHUNK_SIZE,
            overlap=CHUNK_OVERLAP,
            top_level_only=top_level_only,
        )

        if not chunks_with_meta:
            print(f"  No content extracted from {filename}")
            return 0

        # Prepare batch arrays
        all_chunks = [c.text for c in chunks_with_meta]
        all_ids = [f"{file_hash}_{i}" for i in range(len(chunks_with_meta))]
        all_metadatas = [c.metadata for c in chunks_with_meta]

        # Generate embeddings in batches and store
        indexed = 0
        for batch_start in range(0, len(all_chunks), self.EMBEDDING_BATCH_SIZE):
            batch_end = min(batch_start + self.EMBEDDING_BATCH_SIZE, len(all_chunks))
            batch_texts = all_chunks[batch_start:batch_end]
            batch_ids = all_ids[batch_start:batch_end]
            batch_meta = all_metadatas[batch_start:batch_end]

            try:
                batch_embeddings = self._generate_embeddings_batch(batch_texts)
            except Exception as e:
                print(f"  Error generating embeddings for batch {batch_start}-{batch_end}: {e}")
                continue

            self.collection.add(
                ids=batch_ids,
                embeddings=batch_embeddings,
                documents=batch_texts,
                metadatas=batch_meta,
            )
            indexed += len(batch_ids)

            if batch_end < len(all_chunks):
                print(f"  Embedded {batch_end}/{len(all_chunks)} chunks...")

        print(f"Indexed {indexed} chunks from {filename}")
        return indexed

    # -- querying -----------------------------------------------------------

    def query(
        self,
        question: str,
        n_results: int = 5,
        filter_source: Optional[str] = None,
    ) -> Dict:
        """Query the vector database for relevant chunks."""
        where_clause = None
        if filter_source:
            where_clause = {"source": filter_source}

        query_embedding = ollama.embeddings(
            model=self.embed_model, prompt=question
        )["embedding"]

        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results,
            where=where_clause,
            include=["documents", "metadatas", "distances"],
        )
        return results

    @staticmethod
    def _filter_by_distance(results: Dict, max_distance: float) -> Dict:
        """
        Return a copy of a Chroma query result keeping only the chunks whose
        distance is within `max_distance`. Preserves the [[...]] nesting shape
        that the rest of the code expects.
        """
        docs = results.get("documents", [[]])[0]
        metas = results.get("metadatas", [[]])[0]
        dists = results.get("distances", [[]])[0] if results.get("distances") else []

        kept_docs: List[str] = []
        kept_metas: List[Dict] = []
        kept_dists: List[float] = []
        for i, doc in enumerate(docs):
            dist = dists[i] if i < len(dists) else None
            if dist is None or dist <= max_distance:
                kept_docs.append(doc)
                kept_metas.append(metas[i])
                if dist is not None:
                    kept_dists.append(dist)

        return {
            "documents": [kept_docs],
            "metadatas": [kept_metas],
            "distances": [kept_dists],
        }

    def _build_rag_prompt(
        self,
        question: str,
        results: Dict,
        history: Optional[ChatHistory] = None,
        grounded: bool = True,
    ) -> Tuple[str, str]:
        """
        Build the RAG prompt and source citation block from query results.
        Uses breadcrumb metadata for richer citations when available.

        Args:
            grounded: If True (default), the LLM is told to answer based
                primarily on the documentation and to say so if the docs
                don't cover the question. If False, the LLM is told to
                use the docs as a primary source but supplement with its
                own knowledge when the docs are insufficient. Use
                grounded=False for quiz/test scenarios where you want the
                best possible answer regardless of retrieval gaps.
        """
        context_parts = []
        sources_parts = []

        for i, (doc, metadata) in enumerate(
            zip(results["documents"][0], results["metadatas"][0])
        ):
            source = metadata.get("source", "unknown")

            # Use breadcrumb for markdown, page number for PDFs
            breadcrumb = metadata.get("breadcrumb", "")
            heading = metadata.get("heading", "")
            page = metadata.get("page", "")

            if breadcrumb:
                label = f"{source} > {breadcrumb}"
            elif heading:
                label = f"{source} > {heading}"
            elif page:
                label = f"{source}, page {page}"
            else:
                label = source

            context_parts.append(f"[{i + 1}] From {label}:\n{doc}")
            sources_parts.append(f"[{i + 1}] {label}")

        context = "\n\n".join(context_parts)
        # Only cite sources that actually made it into the context (i.e. passed
        # the relevance cutoff). No chunks -> no Sources block at all.
        sources_block = (
            "\n\n---\nSources:\n" + "\n".join(sources_parts) if sources_parts else ""
        )

        history_block = ""
        if history and len(history) > 0:
            history_block = history.format_for_prompt() + "\n\n"

        if grounded:
            system_instruction = (
                "You are a study companion for a React/TypeScript/testing curriculum. "
                "You will receive documentation excerpts numbered [1], [2], etc.\n\n"
                "Rules:\n"
                "- Read ALL excerpts carefully. The answer is almost always contained "
                "in one or more of them.\n"
                "- Extract and present the relevant information directly in your answer. "
                "Do not tell the user to 'refer to' or 'check' a source — include the "
                "details yourself.\n"
                "- When an excerpt contains a list, priority order, or step-by-step "
                "process, reproduce it in your answer.\n"
                "- Cite sources inline like [1] or [3] after the claim they support.\n"
                "- If the excerpts genuinely do not contain the answer, state briefly "
                "that the documentation does not cover it. Do NOT fall back to general "
                "knowledge — answer only from the excerpts above.\n"
                "- Keep answers concise and direct. No preamble like 'Great question' "
                "or 'Based on the documentation provided'."
            )
        else:
            system_instruction = (
                "You are a study companion for a React/TypeScript/testing curriculum. "
                "You will receive documentation excerpts numbered [1], [2], etc. "
                "Use them as your primary source and cite them inline like [1] or [3] "
                "where relevant. If the excerpts don't fully cover the question, "
                "supplement with your own knowledge to give the most accurate and "
                "complete answer possible. Do not refuse to answer just because the "
                "documentation is incomplete. Keep answers concise and direct."
            )

        prompt = (
            f"{system_instruction}\n\n"
            f"{history_block}"
            f"Documentation excerpts:\n{context}\n\n"
            f"Question: {question}"
        )

        return prompt, sources_block

    # Sentinel yielded (in grounded mode) when nothing passes the relevance
    # cutoff. server.py translates this into a `no_results` SSE event and does
    # NOT surface it as answer text. Chosen to never collide with real tokens.
    NO_RESULTS_SIGNAL = "\x00__COSMO_NO_RESULTS__\x00"

    def ask_question(
        self,
        question: str,
        mode: str = DEFAULT_MODE,
        n_results: int = 5,
        history: Optional[ChatHistory] = None,
        grounded: bool = True,
    ) -> Generator[str, None, str]:
        """
        Answer a question using RAG with streaming.
        Yields tokens as they arrive from Ollama.
        The sources block is yielded at the end.

        Args:
            grounded: If True (default), answers strictly from docs. Chunks
                beyond RETRIEVAL_MAX_DISTANCE are dropped, and if none pass
                the cutoff the LLM is NOT called — a no-results sentinel is
                yielded instead. If False, supplements with LLM knowledge
                when docs are insufficient. Use grounded=False for quizzes.
        """
        from backend.config import RETRIEVAL_MAX_DISTANCE

        raw_results = self.query(question, n_results=n_results)

        if grounded:
            # Keep only chunks that clear the relevance cutoff. If nothing
            # does, refuse to answer rather than cite irrelevant pages.
            results = self._filter_by_distance(raw_results, RETRIEVAL_MAX_DISTANCE)
            if not results["documents"][0]:
                yield self.NO_RESULTS_SIGNAL
                return self.NO_RESULTS_SIGNAL
        else:
            # Broad mode: use whatever was retrieved (may be empty) and let
            # the LLM supplement from its own knowledge.
            results = raw_results if raw_results["documents"][0] else {
                "documents": [[]], "metadatas": [[]], "distances": [[]],
            }

        prompt, sources = self._build_rag_prompt(
            question, results, history, grounded=grounded
        )
        model = self.models.get(mode, self.models[DEFAULT_MODE])
        options = dict(CHAT_OPTIONS.get(mode, CHAT_OPTIONS[DEFAULT_MODE]))

        # Bump context for long conversations or many results
        if n_results > 4 and options["num_ctx"] < 8192:
            options["num_ctx"] = 8192
        if history and len(history) > 0 and options["num_ctx"] < 8192:
            options["num_ctx"] = 8192

        full_answer = ""
        stripper = ThinkStripper()

        try:
            stream = ollama.chat(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                stream=True,
                think=False,  # suppress reasoning tokens (qwen3, gemma4)
                options=options,
            )

            for chunk in stream:
                token = chunk["message"]["content"]
                # Belt-and-braces: strip any <think> spans that leak through
                # despite think=False, without breaking on tags split across
                # streamed chunks.
                visible = stripper.feed(token)
                if visible:
                    full_answer += visible
                    yield visible

            tail = stripper.flush()
            if tail:
                full_answer += tail
                yield tail

        except Exception as e:
            # Raise a structured error instead of yielding the message as
            # answer tokens (which rendered as a normal reply). server.py
            # turns this into a distinct `{"error": ...}` SSE event.
            raise RuntimeError(
                f"Error generating response: {e}. "
                f"Make sure '{model}' is installed: ollama pull {model}"
            ) from e

        if history is not None:
            history.add(question, full_answer)

        if sources:
            yield sources
        return full_answer + sources

    # Alias used by interactive CLI
    ask_stream = ask_question

    # -- stats --------------------------------------------------------------

    def get_stats(self) -> Dict:
        """Get statistics about indexed documents."""
        count = self.collection.count()
        if count == 0:
            return {"total_chunks": 0, "total_documents": 0, "sources": {}}

        all_data = self.collection.get(include=["metadatas"])
        sources: Dict[str, Dict] = {}
        for meta in all_data["metadatas"]:
            src = meta.get("source", "unknown")
            if src not in sources:
                sources[src] = {"type": meta.get("doc_type", "unknown"), "chunks": 0}
            sources[src]["chunks"] += 1

        return {
            "total_chunks": count,
            "total_documents": len(sources),
            "sources": sources,
        }