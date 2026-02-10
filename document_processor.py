"""
Document Processor for React/TypeScript Study Companion
Handles ingestion of large PDFs and markdown files into a RAG system
"""

import ollama
import chromadb
from pypdf import PdfReader
import hashlib
from pathlib import Path
from typing import Iterator, Generator, Optional, Dict, List, Tuple
from collections import deque
import re
import logging

logger = logging.getLogger(__name__)


class OllamaConnectionError(Exception):
    """Raised when Ollama is not reachable"""
    pass


class ChatHistory:
    """
    Rolling window of conversation exchanges for multi-turn context.
    
    Stores the last N question/answer pairs. Each pair is stored as
    a tuple of (question, answer) strings. The history is formatted
    into the prompt so the LLM can reference prior exchanges.
    
    Args:
        max_turns: Maximum number of Q&A pairs to retain
    """
    
    def __init__(self, max_turns: int = 5):
        self.max_turns = max_turns
        self._history: deque[Tuple[str, str]] = deque(maxlen=max_turns)
    
    def add(self, question: str, answer: str) -> None:
        """Record a question/answer exchange"""
        self._history.append((question, answer))
    
    def clear(self) -> None:
        """Clear all history"""
        self._history.clear()
    
    def format_for_prompt(self) -> str:
        """
        Format history as a readable block for inclusion in the prompt.
        
        Returns:
            Formatted string of prior exchanges, or empty string if no history
        """
        if not self._history:
            return ""
        
        parts = []
        for q, a in self._history:
            # Truncate long answers to keep the prompt manageable
            truncated_a = a[:600] + "..." if len(a) > 600 else a
            parts.append(f"User: {q}\nAssistant: {truncated_a}")
        
        return "Previous conversation:\n" + "\n\n".join(parts)
    
    @property
    def turn_count(self) -> int:
        return len(self._history)
    
    def __len__(self) -> int:
        return len(self._history)


class DocumentProcessor:
    """Main class for processing and querying technical documentation"""
    
    # Batch size for embedding generation
    EMBEDDING_BATCH_SIZE = 50
    
    def __init__(self, persist_dir: str = "./chroma_db"):
        """
        Initialize the document processor with persistent storage
        
        Args:
            persist_dir: Directory to store the ChromaDB database
        """
        # Verify Ollama is running before proceeding
        self._check_ollama_connection()
        
        # Use PersistentClient for data that survives between sessions
        self.client = chromadb.PersistentClient(path=persist_dir)
        
        # Get or create collection
        self.collection = self.client.get_or_create_collection(
            name="react_typescript_docs",
            metadata={"hnsw:space": "cosine"}
        )
        
        # Model configurations
        self.models = {
            'quick': 'qwen2.5-coder:7b',
            'deep': 'qwen2.5-coder:14b',
            'general': 'llama3.1:8b',
            'fast': 'mistral:7b'
        }
        
        self.embed_model = 'nomic-embed-text'
    
    def _check_ollama_connection(self) -> None:
        """Verify Ollama is running and reachable"""
        try:
            ollama.list()
        except Exception as e:
            raise OllamaConnectionError(
                "Cannot connect to Ollama. Make sure it's running:\n"
                "  ollama serve\n"
                f"Original error: {e}"
            )
    
    def extract_pdf_pages(self, pdf_path: str) -> Iterator[tuple[int, str]]:
        """
        Extract text from PDF page by page.
        
        Note: PdfReader loads the full PDF structure on construction.
        Page-by-page iteration avoids holding all extracted text in memory
        simultaneously, but the PDF itself is fully parsed upfront.
        For typical technical PDFs (<100MB) this is fine on 32GB machines.
        
        Args:
            pdf_path: Path to PDF file
            
        Yields:
            Tuple of (page_number, page_text)
        """
        reader = PdfReader(pdf_path)
        for i, page in enumerate(reader.pages):
            text = page.extract_text()
            if text and text.strip():
                yield i, text
    
    def smart_chunk(self, text: str, max_size: int = 800, overlap: int = 150) -> List[str]:
        """
        Chunk text intelligently respecting document structure
        
        Strategy:
        - Prefer breaking on double newlines (paragraphs)
        - Then single newlines
        - Then sentences
        - Finally words as fallback
        
        Args:
            text: Text to chunk
            max_size: Maximum characters per chunk
            overlap: Characters to overlap between chunks
            
        Returns:
            List of text chunks
        """
        chunks: List[str] = []
        
        # Split on paragraphs first
        paragraphs = re.split(r'\n\s*\n', text)
        
        current_chunk = ""
        for para in paragraphs:
            if len(current_chunk) + len(para) < max_size:
                current_chunk += para + "\n\n"
            else:
                if current_chunk:
                    chunks.append(current_chunk.strip())
                
                # If paragraph itself is too long, split by words
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
        
        # Add character-based overlap between chunks
        overlapped: List[str] = []
        for i, chunk in enumerate(chunks):
            if i > 0:
                prev_text = chunks[i - 1]
                # Take last `overlap` characters from previous chunk
                overlap_text = prev_text[-overlap:]
                # Snap to a word boundary to avoid cutting mid-word
                space_idx = overlap_text.find(' ')
                if space_idx != -1:
                    overlap_text = overlap_text[space_idx + 1:]
                chunk = overlap_text + " " + chunk
            overlapped.append(chunk)
        
        return overlapped if overlapped else chunks
    
    def get_file_hash(self, filepath: str) -> str:
        """
        Hash file contents in chunks to avoid loading large files into memory
        
        Args:
            filepath: Path to file
            
        Returns:
            MD5 hash of file contents
        """
        h = hashlib.md5()
        with open(filepath, 'rb') as f:
            for block in iter(lambda: f.read(8192), b''):
                h.update(block)
        return h.hexdigest()
    
    def is_already_indexed(self, file_hash: str) -> bool:
        """
        Check if document is already in the database
        
        Args:
            file_hash: Hash of the file
            
        Returns:
            True if file is already indexed
        """
        try:
            results = self.collection.get(
                where={"file_hash": file_hash},
                limit=1
            )
            return len(results['ids']) > 0
        except Exception as e:
            logger.warning(f"Error checking index status: {e}")
            return False
    
    def _generate_embeddings_batch(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for a batch of texts.
        
        Tries the batch API first (ollama.embed), falls back to 
        one-at-a-time if not available.
        
        Args:
            texts: List of text strings to embed
            
        Returns:
            List of embedding vectors
        """
        # Try batch embedding first (ollama >= 0.2.0 with embed endpoint)
        try:
            response = ollama.embed(
                model=self.embed_model,
                input=texts
            )
            return response['embeddings']
        except (AttributeError, TypeError, KeyError):
            # Fall back to one-at-a-time for older ollama versions
            pass
        
        embeddings = []
        for text in texts:
            response = ollama.embeddings(
                model=self.embed_model,
                prompt=text
            )
            embeddings.append(response['embedding'])
        return embeddings
    
    def _delete_existing_chunks(self, file_hash: str) -> None:
        """
        Remove all chunks for a given file hash from the collection.
        Used during force re-indexing.
        
        Args:
            file_hash: Hash of the file to remove
        """
        try:
            self.collection.delete(where={"file_hash": file_hash})
        except Exception as e:
            logger.warning(f"Error deleting existing chunks: {e}")
    
    def ingest_pdf(self, pdf_path: str, force: bool = False) -> int:
        """
        Process PDF page by page and index into vector store.
        
        Note: PdfReader parses the full PDF upfront. Page-by-page text
        extraction avoids holding all text in memory simultaneously.
        
        Args:
            pdf_path: Path to PDF file
            force: Force re-indexing even if already processed
            
        Returns:
            Number of chunks indexed
        """
        file_hash = self.get_file_hash(pdf_path)
        
        if not force and self.is_already_indexed(file_hash):
            print(f"{Path(pdf_path).name} already indexed (use --force to re-index)")
            return 0
        
        # Clean up old chunks if force re-indexing
        if force:
            self._delete_existing_chunks(file_hash)
        
        print(f"Processing: {Path(pdf_path).name}")
        filename = Path(pdf_path).name
        
        # Collect all chunks with metadata first, then batch embed
        all_chunks: List[str] = []
        all_ids: List[str] = []
        all_metadatas: List[Dict] = []
        
        for page_num, page_text in self.extract_pdf_pages(pdf_path):
            chunks = self.smart_chunk(page_text)
            
            for chunk_idx, chunk in enumerate(chunks):
                doc_id = f"{file_hash}_{page_num}_{chunk_idx}"
                all_chunks.append(chunk)
                all_ids.append(doc_id)
                all_metadatas.append({
                    "source": filename,
                    "page": page_num + 1,
                    "chunk": chunk_idx,
                    "file_hash": file_hash,
                    "doc_type": "pdf"
                })
            
            if page_num > 0 and page_num % 10 == 0:
                print(f"  Extracted text from {page_num + 1} pages...")
        
        if not all_chunks:
            print(f"  No text extracted from {filename}")
            return 0
        
        # Generate embeddings in batches
        chunk_count = 0
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
                metadatas=batch_meta
            )
            chunk_count += len(batch_ids)
            
            if batch_end < len(all_chunks):
                print(f"  Embedded {batch_end}/{len(all_chunks)} chunks...")
        
        print(f"Indexed {chunk_count} chunks from {filename}")
        return chunk_count
    
    def ingest_markdown(self, md_path: str, force: bool = False) -> int:
        """
        Process markdown with header-aware chunking
        
        Args:
            md_path: Path to markdown file
            force: Force re-indexing even if already processed
            
        Returns:
            Number of chunks indexed
        """
        file_hash = self.get_file_hash(md_path)
        
        if not force and self.is_already_indexed(file_hash):
            print(f"{Path(md_path).name} already indexed (use --force to re-index)")
            return 0
        
        # Clean up old chunks if force re-indexing
        if force:
            self._delete_existing_chunks(file_hash)
        
        print(f"Processing: {Path(md_path).name}")
        filename = Path(md_path).name
        
        with open(md_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Split on headers to maintain document structure
        # The regex captures headers as separate elements in the list
        sections = re.split(r'\n(#{1,6}\s+.+)\n', content)
        
        # Build complete sections: each header + its body
        built_sections: List[str] = []
        current_section = ""
        
        for i, part in enumerate(sections):
            if part.startswith('#'):
                # Flush the previous section before starting a new one
                if current_section.strip():
                    built_sections.append(current_section.strip())
                current_section = part + "\n"
            else:
                current_section += part
        
        # Don't forget the last section
        if current_section.strip():
            built_sections.append(current_section.strip())
        
        # Chunk each section and collect for batch embedding
        all_chunks: List[str] = []
        all_ids: List[str] = []
        all_metadatas: List[Dict] = []
        chunk_count = 0
        
        for section in built_sections:
            chunks = self.smart_chunk(section)
            for chunk_idx, chunk in enumerate(chunks):
                doc_id = f"{file_hash}_{chunk_count}"
                all_chunks.append(chunk)
                all_ids.append(doc_id)
                all_metadatas.append({
                    "source": filename,
                    "section": chunk_count,
                    "file_hash": file_hash,
                    "doc_type": "markdown"
                })
                chunk_count += 1
        
        if not all_chunks:
            print(f"  No content extracted from {filename}")
            return 0
        
        # Generate embeddings in batches
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
                metadatas=batch_meta
            )
            indexed += len(batch_ids)
        
        print(f"Indexed {indexed} chunks from {filename}")
        return indexed
    
    def query(self, question: str, n_results: int = 5,
              filter_source: Optional[str] = None) -> Dict:
        """
        Query the vector database for relevant chunks
        
        Args:
            question: Query string
            n_results: Number of results to return
            filter_source: Optional filter by source filename
            
        Returns:
            Query results from ChromaDB
        """
        where_clause = None
        if filter_source:
            where_clause = {"source": filter_source}
        
        query_embedding = ollama.embeddings(
            model=self.embed_model,
            prompt=question
        )['embedding']
        
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results,
            where=where_clause
        )
        
        return results
    
    def _build_rag_prompt(self, question: str, results: Dict,
                         history: Optional[ChatHistory] = None) -> tuple[str, str]:
        """
        Build the RAG prompt and source citation block from query results.
        
        Args:
            question: The user's question
            results: ChromaDB query results
            history: Optional conversation history for multi-turn context
            
        Returns:
            Tuple of (prompt string, sources citation block)
        """
        context_parts = []
        for i, (doc, metadata) in enumerate(zip(
            results['documents'][0],
            results['metadatas'][0]
        )):
            source = metadata.get('source', 'unknown')
            page = metadata.get('page', metadata.get('section', '?'))
            context_parts.append(f"[{i+1}] From {source}, page {page}:\n{doc}")
        
        context = "\n\n".join(context_parts)
        
        # Build history block if available
        history_block = ""
        if history and len(history) > 0:
            history_block = f"""

{history.format_for_prompt()}

"""
        
        prompt = f"""You are a React/TypeScript study companion. Answer the question based primarily on the provided documentation excerpts. Cite sources using [1], [2], etc. If the documentation doesn't fully address the question, say so.{history_block}
Documentation:
{context}

Question: {question}

Answer with citations:"""
        
        sources = "\n\nSources:\n"
        for i, metadata in enumerate(results['metadatas'][0]):
            source = metadata.get('source', 'unknown')
            page = metadata.get('page', metadata.get('section', '?'))
            sources += f"[{i+1}] {source}, page {page}\n"
        
        return prompt, sources
    
    def ask(self, question: str, mode: str = 'quick', n_results: int = 4,
            history: Optional[ChatHistory] = None) -> str:
        """
        RAG query with cited sources (non-streaming, returns complete answer).
        
        Use this for programmatic/API access. For CLI use, prefer ask_stream.
        
        Args:
            question: Question to ask
            mode: Model mode - 'quick', 'deep', 'general', or 'fast'
            n_results: Number of context chunks to retrieve
            history: Optional conversation history for follow-up questions
            
        Returns:
            Answer with citations
        """
        results = self.query(question, n_results=n_results)
        
        if not results['documents'][0]:
            return "No relevant documents found in the knowledge base."
        
        prompt, sources = self._build_rag_prompt(question, results, history)
        model = self.models.get(mode, self.models['quick'])
        
        # Scale context window: base need + extra for history
        num_ctx = 4096 if n_results <= 4 else 8192
        if history and len(history) > 0:
            num_ctx = 8192
        
        try:
            response = ollama.chat(
                model=model,
                messages=[{'role': 'user', 'content': prompt}],
                options={
                    'num_ctx': num_ctx,
                    'num_thread': 8,
                }
            )
        except Exception as e:
            return (
                f"Error generating response: {e}\n\n"
                f"Make sure '{model}' is installed: ollama pull {model}"
            )
        
        answer = response['message']['content']
        
        # Record this exchange in history if provided
        if history is not None:
            history.add(question, answer)
        
        return answer + sources
    
    def ask_stream(self, question: str, mode: str = 'quick',
                   n_results: int = 4,
                   history: Optional[ChatHistory] = None) -> Generator[str, None, str]:
        """
        RAG query with streaming token output.
        
        Yields tokens as they arrive from Ollama, so the CLI can print
        them immediately. The sources block is yielded at the end.
        If a ChatHistory is provided, the exchange is recorded after
        the full response is generated.
        
        Args:
            question: Question to ask
            mode: Model mode - 'quick', 'deep', 'general', or 'fast'
            n_results: Number of context chunks to retrieve
            history: Optional conversation history for follow-up questions
            
        Yields:
            Individual token strings as they arrive
            
        Returns:
            Complete answer with sources (via StopIteration value)
        """
        results = self.query(question, n_results=n_results)
        
        if not results['documents'][0]:
            yield "No relevant documents found in the knowledge base."
            return "No relevant documents found in the knowledge base."
        
        prompt, sources = self._build_rag_prompt(question, results, history)
        model = self.models.get(mode, self.models['quick'])
        
        # Scale context window: base need + extra for history
        num_ctx = 4096 if n_results <= 4 else 8192
        if history and len(history) > 0:
            num_ctx = 8192
        
        full_response = ""
        
        try:
            stream = ollama.chat(
                model=model,
                messages=[{'role': 'user', 'content': prompt}],
                stream=True,
                options={
                    'num_ctx': num_ctx,
                    'num_thread': 8,
                }
            )
            
            for chunk in stream:
                token = chunk['message']['content']
                full_response += token
                yield token
            
        except Exception as e:
            error_msg = (
                f"Error generating response: {e}\n\n"
                f"Make sure '{model}' is installed: ollama pull {model}"
            )
            yield error_msg
            return error_msg
        
        # Record this exchange in history if provided
        if history is not None:
            history.add(question, full_response)
        
        # Yield the sources block at the end
        yield sources
        return full_response + sources
    
    def get_stats(self) -> Dict:
        """
        Get statistics about indexed documents.
        
        Uses count() for the total and only pulls metadata
        for the source breakdown.
        
        Returns:
            Dictionary with stats
        """
        total = self.collection.count()
        
        if total == 0:
            return {
                'total_chunks': 0,
                'total_documents': 0,
                'sources': {}
            }
        
        # Pull only metadata (no embeddings or documents)
        results = self.collection.get(include=["metadatas"])
        
        sources: Dict[str, Dict] = {}
        for metadata in results['metadatas']:
            source = metadata.get('source', 'unknown')
            doc_type = metadata.get('doc_type', 'unknown')
            
            if source not in sources:
                sources[source] = {'type': doc_type, 'chunks': 0}
            sources[source]['chunks'] += 1
        
        return {
            'total_chunks': total,
            'total_documents': len(sources),
            'sources': sources
        }
