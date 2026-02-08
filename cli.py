#!/usr/bin/env python3
"""
Command-line interface for React/TypeScript Study Companion
"""

import argparse
import sys
from pathlib import Path
from document_processor import DocumentProcessor, OllamaConnectionError


def _get_processor(args) -> DocumentProcessor:
    """
    Create a DocumentProcessor, handling connection errors cleanly.
    
    Raises SystemExit with a helpful message if Ollama isn't running.
    """
    try:
        return DocumentProcessor(persist_dir=args.db_path)
    except OllamaConnectionError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


def ingest_command(args) -> int:
    """Handle document ingestion"""
    processor = _get_processor(args)
    
    if args.path:
        path = Path(args.path)
        if not path.exists():
            print(f"Error: {args.path} does not exist", file=sys.stderr)
            return 1
        
        if path.suffix.lower() == '.pdf':
            processor.ingest_pdf(str(path), force=args.force)
        elif path.suffix.lower() in ['.md', '.markdown']:
            processor.ingest_markdown(str(path), force=args.force)
        else:
            print(f"Unsupported file type: {path.suffix}", file=sys.stderr)
            return 1
    
    elif args.dir:
        dir_path = Path(args.dir)
        if not dir_path.exists():
            print(f"Error: {args.dir} does not exist", file=sys.stderr)
            return 1
        
        pdf_files = list(dir_path.glob('**/*.pdf'))
        md_files = list(dir_path.glob('**/*.md')) + list(dir_path.glob('**/*.markdown'))
        
        total = len(pdf_files) + len(md_files)
        if total == 0:
            print(f"No PDF or markdown files found in {args.dir}", file=sys.stderr)
            return 1
        
        print(f"Found {len(pdf_files)} PDFs and {len(md_files)} markdown files")
        
        for pdf in pdf_files:
            try:
                processor.ingest_pdf(str(pdf), force=args.force)
            except Exception as e:
                print(f"Error processing {pdf.name}: {e}", file=sys.stderr)
        
        for md in md_files:
            try:
                processor.ingest_markdown(str(md), force=args.force)
            except Exception as e:
                print(f"Error processing {md.name}: {e}", file=sys.stderr)
    
    else:
        print("Error: Must specify --path or --dir", file=sys.stderr)
        return 1
    
    return 0


def ask_command(args) -> int:
    """Handle question answering"""
    processor = _get_processor(args)
    
    if not args.question:
        print("Error: Must provide --question", file=sys.stderr)
        return 1
    
    print(f"\nQuestion: {args.question}\n")
    print("Searching documentation...\n")
    
    try:
        for token in processor.ask_stream(
            args.question,
            mode=args.mode,
            n_results=args.results
        ):
            sys.stdout.write(token)
            sys.stdout.flush()
        print()  # Final newline
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    
    return 0


def list_command(args) -> int:
    """List indexed documents"""
    processor = _get_processor(args)
    
    try:
        stats = processor.get_stats()
    except Exception as e:
        print(f"Error retrieving stats: {e}", file=sys.stderr)
        return 1
    
    print(f"\n{'='*60}")
    print(f"Knowledge Base Statistics")
    print(f"{'='*60}")
    print(f"Total chunks: {stats['total_chunks']}")
    print(f"Total documents: {stats['total_documents']}")
    print(f"\nIndexed Documents:")
    print(f"{'-'*60}")
    
    for source, info in sorted(stats['sources'].items()):
        print(f"  {source}")
        print(f"    Type: {info['type']}, Chunks: {info['chunks']}")
    
    print(f"{'='*60}\n")
    return 0


def interactive_command(args) -> int:
    """Start interactive Q&A session"""
    processor = _get_processor(args)
    
    print("\n" + "="*60)
    print("React/TypeScript Study Companion - Interactive Mode")
    print("="*60)
    print("Commands:")
    print("  Ask a question directly")
    print("  'mode <quick|deep|general|fast>' - Switch model")
    print("  'stats' - Show knowledge base stats")
    print("  'quit' or 'exit' - Exit")
    print("="*60 + "\n")
    
    mode = args.mode
    
    while True:
        try:
            question = input(f"\n[{mode}] Question: ").strip()
            
            if not question:
                continue
            
            if question.lower() in ['quit', 'exit', 'q']:
                print("Goodbye!")
                break
            
            if question.lower() == 'stats':
                list_command(args)
                continue
            
            if question.lower().startswith('mode '):
                parts = question.split(maxsplit=1)
                if len(parts) == 2 and parts[1] in ['quick', 'deep', 'general', 'fast']:
                    mode = parts[1]
                    print(f"Switched to {mode} mode")
                else:
                    print("Invalid mode. Choose: quick, deep, general, fast")
                continue
            
            print("\nSearching...\n")
            for token in processor.ask_stream(question, mode=mode, n_results=args.results):
                sys.stdout.write(token)
                sys.stdout.flush()
            print()  # Final newline
            
        except KeyboardInterrupt:
            print("\n\nGoodbye!")
            break
        except EOFError:
            print("\nGoodbye!")
            break
        except Exception as e:
            print(f"Error: {e}", file=sys.stderr)
    
    return 0


def main():
    parser = argparse.ArgumentParser(
        description='React/TypeScript Study Companion - RAG-powered documentation Q&A',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Ingest a single PDF
  %(prog)s ingest --path docs/react-handbook.pdf
  
  # Ingest all docs in a directory
  %(prog)s ingest --dir docs/
  
  # Ask a question
  %(prog)s ask --question "How do I type a useState hook?"
  
  # Ask with deep mode (slower, better quality)
  %(prog)s ask --question "Explain discriminated unions" --mode deep
  
  # Interactive session
  %(prog)s interactive
  
  # List indexed documents
  %(prog)s list
        """
    )
    
    parser.add_argument(
        '--db-path',
        default='./chroma_db',
        help='Path to ChromaDB database directory (default: ./chroma_db)'
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Ingest command
    ingest_parser = subparsers.add_parser('ingest', help='Ingest documents into the knowledge base')
    ingest_parser.add_argument('--path', help='Path to single file (PDF or markdown)')
    ingest_parser.add_argument('--dir', help='Directory containing documents to ingest')
    ingest_parser.add_argument('--force', action='store_true',
                               help='Force re-indexing of already processed files')
    
    # Ask command
    ask_parser = subparsers.add_parser('ask', help='Ask a question')
    ask_parser.add_argument('--question', '-q', required=True, help='Question to ask')
    ask_parser.add_argument('--mode', '-m', default='quick',
                           choices=['quick', 'deep', 'general', 'fast'],
                           help='Model mode (default: quick)')
    ask_parser.add_argument('--results', '-n', type=int, default=4,
                           help='Number of context chunks to retrieve (default: 4)')
    
    # List command
    subparsers.add_parser('list', help='List indexed documents')
    
    # Interactive command
    interactive_parser = subparsers.add_parser('interactive',
                                               help='Start interactive Q&A session')
    interactive_parser.add_argument('--mode', '-m', default='quick',
                                   choices=['quick', 'deep', 'general', 'fast'],
                                   help='Initial model mode (default: quick)')
    interactive_parser.add_argument('--results', '-n', type=int, default=4,
                                   help='Number of context chunks to retrieve (default: 4)')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    commands = {
        'ingest': ingest_command,
        'ask': ask_command,
        'list': list_command,
        'interactive': interactive_command,
    }
    
    handler = commands.get(args.command)
    if handler:
        return handler(args)
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
