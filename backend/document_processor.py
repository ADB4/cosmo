"""
Document Processor — core RAG engine for Cosmo.

Handles ingestion of PDFs and markdown files into a ChromaDB vector store,
querying with semantic search, and streaming LLM answers via Ollama.
"""

import hashlib
import logging
import re
from collections import deque
from pathlib import Path
from typing import Dict, Generator, Iterator, List, Optional, Tuple

import chromadb
import ollama
from pypdf import PdfReader

from backend.config import (
    CHAT_MODELS,
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
# Document processor
# ---------------------------------------------------------------------------

class DocumentProcessor:
    """Process, index, and query technical documentation via RAG."""

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
                "Cannot connect to Ollama. Make sure it's running:\n"
                f"  ollama serve\nOriginal error: {e}"
            )

    # -- PDF extraction -----------------------------------------------------

    def extract_pdf_pages(self, pdf_path: str) -> Iterator[Tuple[int, str]]:
        reader = PdfReader(pdf_path)
        for i, page in enumerate(reader.pages):
            text = page.extract_text() or ""
            if text.strip():
                yield i + 1, text

    # -- chunking -----------------------------------------------------------

    @staticmethod
    def smart_chunk(
        text: str,
        max_size: int = CHUNK_SIZE,
        overlap: int = CHUNK_OVERLAP,
    ) -> List[str]:
        paragraphs = text.split("\n\n")
        chunks: List[str] = []
        current_chunk = ""

        for para in paragraphs:
            para = para.strip()
            if not para:
                continue
            if len(current_chunk) + len(para) + 2 < max_size:
                current_chunk += para + "\n\n"
            else:
                if current_chunk.strip():
                    chunks.append(current_chunk.strip())
                if len(para) > max_size:
                    words = para.split()
                    temp_chunk = ""
                    for word in words:
                        if len(temp_chunk) + len(word) + 1 < max_size:
                            temp_chunk += word + " "
                        else:
                            if temp_chunk:
                                chunks.append(temp_chunk.strip())
                            temp_chunk = word + " "
                    current_chunk = temp_chunk
                else:
                    current_chunk = para + "\n\n"

        if current_chunk.strip():
            chunks.append(current_chunk.strip())

        overlapped: List[str] = []
        for i, chunk in enumerate(chunks):
            if i > 0:
                prev_text = chunks[i - 1]
                overlap_text = prev_text[-overlap:]
                space_idx = overlap_text.find(" ")
                if space_idx != -1:
                    overlap_text = overlap_text[space_idx + 1:]
                chunk = overlap_text + " " + chunk
            overlapped.append(chunk)

        return overlapped if overlapped else chunks

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
        file_hash = self.get_file_hash(pdf_path)
        if not force and self.is_already_indexed(file_hash):
            print(f"{Path(pdf_path).name} already indexed (use --force to re-index)")
            return 0
        if force:
            self._delete_existing_chunks(file_hash)

        print(f"Processing: {Path(pdf_path).name}")
        filename = Path(pdf_path).name

        all_chunks: List[str] = []
        all_ids: List[str] = []
        all_metadatas: List[Dict] = []
        chunk_count = 0

        for page_num, text in self.extract_pdf_pages(pdf_path):
            chunks = self.smart_chunk(text)
            for chunk in chunks:
                doc_id = f"{file_hash}_{chunk_count}"
                all_chunks.append(chunk)
                all_ids.append(doc_id)
                all_metadatas.append({
                    "source": filename,
                    "page": page_num,
                    "file_hash": file_hash,
                    "doc_type": "pdf",
                })
                chunk_count += 1

        if not all_chunks:
            print(f"  No content extracted from {filename}")
            return 0

        indexed = 0
        for batch_start in range(0, len(all_chunks), EMBEDDING_BATCH_SIZE):
            batch_end = min(batch_start + EMBEDDING_BATCH_SIZE, len(all_chunks))
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

        sections = re.split(r"\n(#{1,6}\s+.+)\n", content)
        built_sections: List[str] = []
        current_section = ""
        for part in sections:
            if part.startswith("#"):
                if current_section.strip():
                    built_sections.append(current_section.strip())
                current_section = part + "\n"
            else:
                current_section += part
        if current_section.strip():
            built_sections.append(current_section.strip())

        all_chunks: List[str] = []
        all_ids: List[str] = []
        all_metadatas: List[Dict] = []
        chunk_count = 0
        for section in built_sections:
            chunks = self.smart_chunk(section)
            for chunk in chunks:
                doc_id = f"{file_hash}_{chunk_count}"
                all_chunks.append(chunk)
                all_ids.append(doc_id)
                all_metadatas.append({
                    "source": filename,
                    "section": chunk_count,
                    "file_hash": file_hash,
                    "doc_type": "markdown",
                })
                chunk_count += 1

        if not all_chunks:
            print(f"  No content extracted from {filename}")
            return 0

        indexed = 0
        for batch_start in range(0, len(all_chunks), EMBEDDING_BATCH_SIZE):
            batch_end = min(batch_start + EMBEDDING_BATCH_SIZE, len(all_chunks))
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

        print(f"Indexed {indexed} chunks from {filename}")
        return indexed

    # -- query --------------------------------------------------------------

    def query(
        self,
        question: str,
        n_results: int = 5,
        filter_source: Optional[str] = None,
    ) -> Dict:
        where_clause = None
        if filter_source:
            where_clause = {"source": filter_source}
        query_embedding = ollama.embeddings(
            model=self.embed_model, prompt=question
        )["embedding"]
        return self.collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results,
            where=where_clause,
        )

    # -- prompt building ----------------------------------------------------

    def _build_rag_prompt(
        self,
        question: str,
        results: Dict,
        history: Optional[ChatHistory] = None,
    ) -> Tuple[str, str]:
        context_parts = []
        for i, (doc, metadata) in enumerate(
            zip(results["documents"][0], results["metadatas"][0])
        ):
            source = metadata.get("source", "unknown")
            page = metadata.get("page", metadata.get("section", "?"))
            context_parts.append(f"[{i + 1}] From {source}, page {page}:\n{doc}")

        context = "\n\n".join(context_parts)

        history_block = ""
        if history and len(history) > 0:
            history_block = f"\n\n{history.format_for_prompt()}\n\n"

        prompt = (
            "You are a React/TypeScript study companion. Answer the question "
            "based primarily on the provided documentation excerpts. Cite "
            "sources using [1], [2], etc. If the documentation doesn't fully "
            f"address the question, say so.{history_block}\n"
            f"Documentation:\n{context}\n\n"
            f"Question: {question}\n\n"
            "Answer with citations:"
        )

        sources = "\n\nSources:\n"
        for i, metadata in enumerate(results["metadatas"][0]):
            source = metadata.get("source", "unknown")
            page = metadata.get("page", metadata.get("section", "?"))
            sources += f"[{i + 1}] {source}, page {page}\n"

        return prompt, sources

    # -- answer -------------------------------------------------------------

    def ask(
        self,
        question: str,
        mode: str = "quick",
        n_results: int = 4,
        history: Optional[ChatHistory] = None,
    ) -> str:
        results = self.query(question, n_results=n_results)
        if not results["documents"][0]:
            return "No relevant documents found in the knowledge base."

        prompt, sources = self._build_rag_prompt(question, results, history)
        model = self.models.get(mode, self.models["quick"])

        response = ollama.chat(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            options={"num_ctx": 8192, "num_thread": 8},
        )
        answer = response["message"]["content"]

        if history is not None:
            history.add(question, answer)

        return answer + sources

    def ask_stream(
        self,
        question: str,
        mode: str = "quick",
        n_results: int = 4,
        history: Optional[ChatHistory] = None,
    ) -> Generator[str, None, None]:
        results = self.query(question, n_results=n_results)
        if not results["documents"][0]:
            yield "No relevant documents found in the knowledge base."
            return

        prompt, sources = self._build_rag_prompt(question, results, history)
        model = self.models.get(mode, self.models["quick"])

        full_answer = ""
        for chunk in ollama.chat(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            stream=True,
            options={"num_ctx": 8192, "num_thread": 8},
        ):
            token = chunk["message"]["content"]
            full_answer += token
            yield token

        yield sources

        if history is not None:
            history.add(question, full_answer)

    # -- stats --------------------------------------------------------------

    def get_stats(self) -> Dict:
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
