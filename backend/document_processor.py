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
import pymupdf4llm

from backend.config import (
    CHAT_MODELS,
    CHAT_OPTIONS,
    CHUNK_OVERLAP,
    CHUNK_SIZE,
    DB_PATH,
    EMBED_MODEL,
    EMBEDDING_BATCH_SIZE,
)

logger = logging.getLogger(__name__)


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

    @property
    def breadcrumb_path(self) -> str:
        """Slash-separated breadcrumb for metadata storage."""
        return " > ".join(self.breadcrumb)


@dataclass
class ChunkWithMetadata:
    """A text chunk with all the metadata needed for ChromaDB storage."""

    text: str
    metadata: Dict[str, str]


def parse_markdown_sections(content: str) -> List[MarkdownSection]:
    """
    Parse markdown into sections split by headings, preserving hierarchy.

    Handles:
    - ATX headings (# through ######)
    - Content before the first heading (assigned level 0, heading "Introduction")
    - Nested heading breadcrumbs (an h3 under an h2 under an h1 gets all three)
    - Headings inside fenced code blocks are skipped
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

    # Second pass: extract sections with body text
    sections: List[MarkdownSection] = []

    # Handle content before first heading
    first_heading_line = heading_positions[0][0] if heading_positions else len(lines)
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

    for idx, (line_num, level, text) in enumerate(heading_positions):
        # Determine where this section's body ends
        if idx + 1 < len(heading_positions):
            next_line = heading_positions[idx + 1][0]
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

        sections.append(MarkdownSection(
            heading="#" * level + " " + text,
            heading_text=text,
            heading_level=level,
            body=body,
            breadcrumb=breadcrumb,
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
) -> List[ChunkWithMetadata]:
    """
    Full pipeline: parse markdown into sections, chunk each section,
    and attach rich metadata to every chunk.
    """
    sections = parse_markdown_sections(content)
    results: List[ChunkWithMetadata] = []

    for section_idx, section in enumerate(sections):
        chunks = chunk_section(section, max_size=max_size, overlap=overlap)

        for chunk_in_section_idx, chunk_text in enumerate(chunks):
            results.append(ChunkWithMetadata(
                text=chunk_text,
                metadata={
                    "source": filename,
                    "file_hash": file_hash,
                    "doc_type": "markdown",
                    "heading": section.heading_text,
                    "heading_level": str(section.heading_level),
                    "breadcrumb": section.breadcrumb_path,
                    "chunk_index_in_section": str(chunk_in_section_idx),
                    "section_index": str(section_idx),
                },
            ))

    return results


# ---------------------------------------------------------------------------
# Document processor
# ---------------------------------------------------------------------------


class DocumentProcessor:
    """Process, index, and query technical documentation via RAG."""

    EMBEDDING_BATCH_SIZE = EMBEDDING_BATCH_SIZE

    def __init__(self, persist_dir: str | None = None):
        self._check_ollama_connection()
        self.client = chromadb.PersistentClient(path=persist_dir or DB_PATH)
        self.collection = self.client.get_or_create_collection(
            name="react_typescript_docs",
            metadata={"hnsw:space": "cosine"},
        )
        self.models = CHAT_MODELS
        self.embed_model = EMBED_MODEL

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

    @staticmethod
    def pdf_to_markdown(pdf_path: str) -> str:
        """
        Convert a PDF to markdown using pymupdf4llm.

        Preserves headings, code blocks, tables, and lists far better than
        naive text extraction. The resulting markdown is then suitable for
        the heading-hierarchy chunker.
        """
        return pymupdf4llm.to_markdown(pdf_path)

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
        """
        Generate embeddings for a batch of texts.
        Tries the batch API first (ollama.embed), falls back to
        one-at-a-time if not available.
        """
        try:
            response = ollama.embed(model=self.embed_model, input=texts)
            return response["embeddings"]
        except (AttributeError, TypeError, KeyError):
            pass
        embeddings = []
        for text in texts:
            response = ollama.embeddings(model=self.embed_model, prompt=text)
            embeddings.append(response["embedding"])
        return embeddings

    # -- ingestion ----------------------------------------------------------

    def ingest_pdf(self, pdf_path: str, force: bool = False) -> int:
        """
        Convert PDF to markdown via pymupdf4llm, then process with the
        heading-hierarchy-aware markdown chunker.

        This gives PDFs the same rich metadata (headings, breadcrumbs,
        section-aware overlap) that native markdown files get.
        """
        file_hash = self.get_file_hash(pdf_path)

        if not force and self.is_already_indexed(file_hash):
            print(f"{Path(pdf_path).name} already indexed (use --force to re-index)")
            return 0

        if force:
            self._delete_existing_chunks(file_hash)

        print(f"Processing: {Path(pdf_path).name}")
        filename = Path(pdf_path).name

        # Convert PDF to markdown -- this is where pymupdf4llm does the
        # heavy lifting: extracting headings, code blocks, tables, lists
        print(f"  Converting PDF to markdown...")
        try:
            md_content = self.pdf_to_markdown(pdf_path)
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

    def ingest_markdown(self, md_path: str, force: bool = False) -> int:
        """
        Process markdown with heading-hierarchy-aware chunking.

        Splits on heading hierarchy, preserves heading text/level/breadcrumb
        path in metadata, and applies section-aware overlap that never bleeds
        across heading boundaries.
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
        )
        return results

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
        sources_block = "\n\n---\nSources:\n" + "\n".join(sources_parts)

        history_block = ""
        if history and len(history) > 0:
            history_block = history.format_for_prompt() + "\n\n"

        if grounded:
            system_instruction = (
                "You are a React/TypeScript study companion. Answer the question "
                "based primarily on the provided documentation excerpts. Cite "
                "sources using [1], [2], etc. If the documentation doesn't fully "
                "address the question, say so."
            )
        else:
            system_instruction = (
                "You are a React/TypeScript study companion. Use the provided "
                "documentation excerpts as your primary source and cite them "
                "using [1], [2], etc. where relevant. If the excerpts don't "
                "fully cover the question, supplement with your own knowledge "
                "to give the most accurate and complete answer possible. Do "
                "not refuse to answer just because the documentation is "
                "incomplete."
            )

        prompt = (
            f"{system_instruction}\n\n"
            f"{history_block}"
            f"Documentation excerpts:\n{context}\n\n"
            f"Question: {question}"
        )

        return prompt, sources_block

    def ask_question(
        self,
        question: str,
        mode: str = "qwen-7b",
        n_results: int = 5,
        history: Optional[ChatHistory] = None,
        grounded: bool = True,
    ) -> Generator[str, None, str]:
        """
        Answer a question using RAG with streaming.
        Yields tokens as they arrive from Ollama.
        The sources block is yielded at the end.

        Args:
            grounded: If True (default), answers strictly from docs.
                If False, supplements with LLM knowledge when docs
                are insufficient. Use grounded=False for quizzes.
        """
        results = self.query(question, n_results=n_results)

        if not results["documents"][0]:
            if grounded:
                yield "No relevant documents found in the knowledge base."
                return "No relevant documents found in the knowledge base."
            else:
                # In ungrounded mode, still try to answer from LLM knowledge
                results = {"documents": [[]], "metadatas": [[]]}

        prompt, sources = self._build_rag_prompt(
            question, results, history, grounded=grounded
        )
        model = self.models.get(mode, self.models["qwen-7b"])
        options = dict(CHAT_OPTIONS.get(mode, CHAT_OPTIONS["qwen-7b"]))

        # Bump context for long conversations or many results
        if n_results > 4 and options["num_ctx"] < 8192:
            options["num_ctx"] = 8192
        if history and len(history) > 0 and options["num_ctx"] < 8192:
            options["num_ctx"] = 8192

        full_answer = ""

        try:
            stream = ollama.chat(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                stream=True,
                options=options,
            )

            for chunk in stream:
                token = chunk["message"]["content"]
                full_answer += token
                yield token

        except Exception as e:
            error_msg = (
                f"Error generating response: {e}\n\n"
                f"Make sure '{model}' is installed: ollama pull {model}"
            )
            yield error_msg
            return error_msg

        if history is not None:
            history.add(question, full_answer)

        yield sources
        return full_answer + sources

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