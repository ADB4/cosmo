#!/usr/bin/env python3
"""
Example usage of the Document Processor API
"""

from document_processor import DocumentProcessor
import sys


def example_basic_usage():
    """Basic usage example"""
    print("=" * 60)
    print("Example 1: Basic Usage")
    print("=" * 60)
    
    # Initialize processor
    processor = DocumentProcessor()
    
    # Ingest a document (only happens once, cached after that)
    print("\n1. Ingesting document...")
    # processor.ingest_markdown("docs/example.md")
    
    # Ask a question
    print("\n2. Asking question...")
    answer = processor.ask(
        "What are TypeScript generics?",
        mode='quick'
    )
    print(f"\nAnswer:\n{answer}")


def example_batch_ingestion():
    """Batch ingestion example"""
    print("\n" + "=" * 60)
    print("Example 2: Batch Ingestion")
    print("=" * 60)
    
    processor = DocumentProcessor()
    
    import glob
    
    # Ingest all PDFs
    pdf_files = glob.glob("docs/**/*.pdf", recursive=True)
    print(f"\nFound {len(pdf_files)} PDF files")
    
    for pdf in pdf_files[:2]:  # Just first 2 for demo
        print(f"Processing: {pdf}")
        processor.ingest_pdf(pdf)


def example_different_modes():
    """Demonstrate different query modes"""
    print("\n" + "=" * 60)
    print("Example 3: Different Query Modes")
    print("=" * 60)
    
    processor = DocumentProcessor()
    
    question = "Explain React hooks"
    
    print(f"\nQuestion: {question}\n")
    
    # Quick mode
    print("--- Quick Mode (fast, good quality) ---")
    answer = processor.ask(question, mode='quick', n_results=3)
    print(answer[:200] + "...\n")
    
    # Deep mode (commented out - slower)
    # print("--- Deep Mode (slower, best quality) ---")
    # answer = processor.ask(question, mode='deep', n_results=5)
    # print(answer[:200] + "...\n")


def example_stats():
    """Show knowledge base statistics"""
    print("\n" + "=" * 60)
    print("Example 4: Knowledge Base Stats")
    print("=" * 60)
    
    processor = DocumentProcessor()
    
    stats = processor.get_stats()
    
    print(f"\nTotal documents: {stats['total_documents']}")
    print(f"Total chunks: {stats['total_chunks']}")
    print("\nDocuments:")
    
    for source, info in sorted(stats['sources'].items()):
        print(f"  - {source}: {info['chunks']} chunks ({info['type']})")


def example_direct_query():
    """Direct query without RAG answer generation"""
    print("\n" + "=" * 60)
    print("Example 5: Direct Vector Search")
    print("=" * 60)
    
    processor = DocumentProcessor()
    
    # Just retrieve relevant chunks without generating answer
    results = processor.query(
        "TypeScript interfaces",
        n_results=3
    )
    
    print("\nTop 3 relevant chunks:\n")
    for i, (doc, meta) in enumerate(zip(
        results['documents'][0],
        results['metadatas'][0]
    ), 1):
        print(f"{i}. From {meta['source']} (page {meta.get('page', '?')})")
        print(f"   {doc[:150]}...\n")


def example_filtered_search():
    """Search within specific document"""
    print("\n" + "=" * 60)
    print("Example 6: Filtered Search")
    print("=" * 60)
    
    processor = DocumentProcessor()
    
    # Get stats to see available sources
    stats = processor.get_stats()
    
    if stats['sources']:
        # Pick first source
        source = list(stats['sources'].keys())[0]
        print(f"\nSearching only in: {source}")
        
        results = processor.query(
            "types",
            n_results=2,
            filter_source=source
        )
        
        print(f"\nFound {len(results['documents'][0])} results")


def main():
    """Run all examples"""
    print("\n" + "=" * 70)
    print("React/TypeScript Study Companion - Usage Examples")
    print("=" * 70)
    
    try:
        # Run examples
        # example_basic_usage()
        # example_batch_ingestion()
        # example_different_modes()
        example_stats()
        # example_direct_query()
        # example_filtered_search()
        
        print("\n" + "=" * 70)
        print("Examples completed!")
        print("=" * 70)
        
        print("\nNext steps:")
        print("1. Ingest your documents: python cli.py ingest --dir docs/")
        print("2. Try interactive mode: python cli.py interactive")
        print("3. Or use the API directly in your own scripts")
        
    except Exception as e:
        print(f"\nError running examples: {e}")
        print("\nMake sure you have:")
        print("1. Ollama running with models installed")
        print("2. Documents ingested into the knowledge base")
        print("3. All dependencies installed (pip install -r requirements.txt)")
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
