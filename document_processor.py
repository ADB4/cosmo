"""
Document Processor for React/TypeScript Study Companion
Handles ingestion of large PDFs and markdown files into a RAG system
"""

import ollama
import chromadb
from chromadb.config import Settings
from pypdf import PdfReader
import hashlib
from pathlib import Path
from typing import Iterator, Optional, Dict, List
import re


class DocumentProcessor:
    """Main class for processing and querying technical documentation"""
    
    def __init__(self, persist_dir="./chroma_db"):
        """
        Initialize the document processor with persistent storage
        
        Args:
            persist_dir: Directory to store the ChromaDB database
        """
        # Persistent ChromaDB
        self.client = chromadb.Client(Settings(
            persist_directory=persist_dir,
            anonymized_telemetry=False
        ))
        
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
    
    def extract_pdf_pages(self, pdf_path: str) -> Iterator[tuple[int, str]]:
        """
        Stream pages from PDF without loading entire file into memory
        
        Args:
            pdf_path: Path to PDF file
            
        Yields:
            Tuple of (page_number, page_text)
        """
        reader = PdfReader(pdf_path)
        for i, page in enumerate(reader.pages):
            text = page.extract_text()
            if text.strip():  # Skip empty pages
                yield i, text
    
    def smart_chunk(self, text: str, max_size=800, overlap=150) -> List[str]:
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
        chunks = []
        
        # Try to split on paragraphs first
        paragraphs = re.split(r'\n\s*\n', text)
        
        current_chunk = ""
        for para in paragraphs:
            if len(current_chunk) + len(para) < max_size:
                current_chunk += para + "\n\n"
            else:
                if current_chunk:
                    chunks.append(current_chunk.strip())
                
                # If paragraph itself is too long, split it
                if len(para) > max_size:
                    words = para.split()
                    temp_chunk = ""
                    for word in words:
                        if len(temp_chunk) + len(word) < max_size:
                            temp_chunk += word + " "
                        else:
                            chunks.append(temp_chunk.strip())
                            temp_chunk = word + " "
                    current_chunk = temp_chunk
                else:
                    current_chunk = para + "\n\n"
        
        if current_chunk:
            chunks.append(current_chunk.strip())
        
        # Add overlap between chunks
        overlapped = []
        for i, chunk in enumerate(chunks):
            if i > 0:
                # Take last ~30 words from previous chunk
                prev_words = chunks[i-1].split()[-overlap//5:]
                chunk = " ".join(prev_words) + " " + chunk
            overlapped.append(chunk)
        
        return overlapped if overlapped else chunks
    
    def get_file_hash(self, filepath: str) -> str:
        """
        Hash file to track if already processed
        
        Args:
            filepath: Path to file
            
        Returns:
            MD5 hash of file contents
        """
        with open(filepath, 'rb') as f:
            return hashlib.md5(f.read()).hexdigest()
    
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
        except:
            return False
    
    def ingest_pdf(self, pdf_path: str, force: bool = False) -> int:
        """
        Process large PDF page by page, streaming to avoid memory issues
        
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
        
        print(f"Processing: {Path(pdf_path).name}")
        filename = Path(pdf_path).name
        
        chunk_count = 0
        for page_num, page_text in self.extract_pdf_pages(pdf_path):
            chunks = self.smart_chunk(page_text)
            
            for chunk_idx, chunk in enumerate(chunks):
                # Generate embedding on-the-fly with Ollama
                try:
                    embedding = ollama.embeddings(
                        model=self.embed_model,
                        prompt=chunk
                    )['embedding']
                except Exception as e:
                    print(f"  Error generating embedding: {e}")
                    continue
                
                doc_id = f"{file_hash}_{page_num}_{chunk_idx}"
                
                self.collection.add(
                    ids=[doc_id],
                    embeddings=[embedding],
                    documents=[chunk],
                    metadatas=[{
                        "source": filename,
                        "page": page_num + 1,
                        "chunk": chunk_idx,
                        "file_hash": file_hash,
                        "doc_type": "pdf"
                    }]
                )
                chunk_count += 1
            
            if page_num % 10 == 0:
                print(f"  Processed {page_num + 1} pages...")
        
        print(f"Indexed {chunk_count} chunks from {Path(pdf_path).name}")
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
        
        print(f"Processing: {Path(md_path).name}")
        filename = Path(md_path).name
        
        with open(md_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Split on headers first to maintain document structure
        sections = re.split(r'\n(#{1,6}\s+.+)\n', content)
        
        chunk_count = 0
        current_section = ""
        
        for i, section in enumerate(sections):
            if section.startswith('#'):
                # This is a header
                current_section = section + "\n"
            else:
                current_section += section
                
                # Process section if it's large enough or we're at the end
                if len(current_section) > 500 or i == len(sections) - 1:
                    if current_section.strip():
                        chunks = self.smart_chunk(current_section)
                        
                        for chunk_idx, chunk in enumerate(chunks):
                            try:
                                embedding = ollama.embeddings(
                                    model=self.embed_model,
                                    prompt=chunk
                                )['embedding']
                            except Exception as e:
                                print(f"  Error generating embedding: {e}")
                                continue
                            
                            doc_id = f"{file_hash}_{chunk_count}"
                            
                            self.collection.add(
                                ids=[doc_id],
                                embeddings=[embedding],
                                documents=[chunk],
                                metadatas=[{
                                    "source": filename,
                                    "section": chunk_count,
                                    "file_hash": file_hash,
                                    "doc_type": "markdown"
                                }]
                            )
                            chunk_count += 1
                    
                    current_section = ""
        
        print(f"Indexed {chunk_count} chunks from {Path(md_path).name}")
        return chunk_count
    
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
        
        # Get query embedding
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
    
    def ask(self, question: str, mode: str = 'quick', n_results: int = 4) -> str:
        """
        RAG query with cited sources
        
        Args:
            question: Question to ask
            mode: Model mode - 'quick', 'deep', 'general', or 'fast'
            n_results: Number of context chunks to retrieve
            
        Returns:
            Answer with citations
        """
        results = self.query(question, n_results=n_results)
        
        if not results['documents'][0]:
            return "No relevant documents found in the knowledge base."
        
        # Build context with citations
        context_parts = []
        for i, (doc, metadata) in enumerate(zip(
            results['documents'][0], 
            results['metadatas'][0]
        )):
            source = metadata.get('source', 'unknown')
            page = metadata.get('page', metadata.get('section', '?'))
            context_parts.append(f"[{i+1}] From {source}, page {page}:\n{doc}")
        
        context = "\n\n".join(context_parts)
        
        # Build prompt
        prompt = f"""You are a React/TypeScript study companion. Answer the question using ONLY the provided documentation excerpts. Cite sources using [1], [2], etc.

Documentation:
{context}

Question: {question}

Answer with citations:"""
        
        model = self.models.get(mode, self.models['quick'])
        
        try:
            response = ollama.chat(
                model=model,
                messages=[{'role': 'user', 'content': prompt}],
                options={
                    'num_ctx': 4096,
                    'num_thread': 8,
                }
            )
        except Exception as e:
            return f"Error generating response: {e}\n\nMake sure '{model}' is installed: ollama pull {model}"
        
        # Append source list
        sources = "\n\nSources:\n"
        for i, metadata in enumerate(results['metadatas'][0]):
            source = metadata.get('source', 'unknown')
            page = metadata.get('page', metadata.get('section', '?'))
            sources += f"[{i+1}] {source}, page {page}\n"
        
        return response['message']['content'] + sources
    
    def get_stats(self) -> Dict:
        """
        Get statistics about indexed documents
        
        Returns:
            Dictionary with stats
        """
        results = self.collection.get()
        
        sources = {}
        for metadata in results['metadatas']:
            source = metadata.get('source', 'unknown')
            doc_type = metadata.get('doc_type', 'unknown')
            
            if source not in sources:
                sources[source] = {'type': doc_type, 'chunks': 0}
            sources[source]['chunks'] += 1
        
        return {
            'total_chunks': len(results['ids']),
            'total_documents': len(sources),
            'sources': sources
        }
