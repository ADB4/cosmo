#!/usr/bin/env python3
"""
Cosmo CLI — command-line interface for the RAG study companion.

Usage:
    python -m backend.cli ingest --dir docs/
    python -m backend.cli ask -q "How do I type a useState hook?"
    python -m backend.cli interactive
    python -m backend.cli quiz --input quizzes/w1.md
    python -m backend.cli list
"""

import argparse
import sys

from backend.document_processor import (
    ChatHistory,
    DocumentProcessor,
    OllamaConnectionError,
)


def _get_processor(args) -> DocumentProcessor:
    try:
        return DocumentProcessor(persist_dir=args.db_path)
    except OllamaConnectionError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


# ===================================================================
# Commands
# ===================================================================

def ingest_command(args) -> int:
    processor = _get_processor(args)

    if args.path:
        from pathlib import Path

        p = Path(args.path)
        if not p.exists():
            print(f"Error: File not found: {args.path}", file=sys.stderr)
            return 1
        ext = p.suffix.lower()
        try:
            if ext == ".pdf":
                processor.ingest_pdf(str(p), force=args.force)
            elif ext in (".md", ".markdown"):
                processor.ingest_markdown(str(p), force=args.force)
            else:
                print(f"Error: Unsupported file type: {ext}", file=sys.stderr)
                return 1
        except Exception as e:
            print(f"Error: {e}", file=sys.stderr)
            return 1

    elif args.dir:
        from pathlib import Path

        d = Path(args.dir)
        if not d.exists() or not d.is_dir():
            print(f"Error: Directory not found: {args.dir}", file=sys.stderr)
            return 1

        pdf_files = sorted(d.glob("**/*.pdf"))
        md_files = sorted(
            list(d.glob("**/*.md")) + list(d.glob("**/*.markdown"))
        )
        if not pdf_files and not md_files:
            print(f"No supported files found in {args.dir}", file=sys.stderr)
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
    processor = _get_processor(args)
    if not args.question:
        print("Error: Must provide --question", file=sys.stderr)
        return 1

    print(f"\nQuestion: {args.question}\n")
    print("Searching documentation...\n")

    try:
        for token in processor.ask_stream(
            args.question, mode=args.mode, n_results=args.results
        ):
            sys.stdout.write(token)
            sys.stdout.flush()
        print()
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    return 0


def list_command(args) -> int:
    processor = _get_processor(args)
    try:
        stats = processor.get_stats()
    except Exception as e:
        print(f"Error retrieving stats: {e}", file=sys.stderr)
        return 1

    print(f"\n{'=' * 60}")
    print("Knowledge Base Statistics")
    print(f"{'=' * 60}")
    print(f"Total chunks: {stats['total_chunks']}")
    print(f"Total documents: {stats['total_documents']}")
    print(f"\nIndexed Documents:")
    print(f"{'-' * 60}")
    for source, info in sorted(stats["sources"].items()):
        print(f"  {source}")
        print(f"    Type: {info['type']}, Chunks: {info['chunks']}")
    print(f"{'=' * 60}\n")
    return 0


def quiz_command(args) -> int:
    from backend.quiz_processor import run_quiz
    from pathlib import Path

    processor = None
    use_rag = not args.no_rag

    if use_rag:
        processor = _get_processor(args)
        stats = processor.get_stats()
        if stats["total_chunks"] == 0:
            print("Warning: No documents indexed. Running without RAG context.")
            use_rag = False
            processor = None
    else:
        _get_processor(args)  # just verify Ollama is up

    input_path = Path(args.input)
    output_path = args.output or f"results/{input_path.stem}-results.md"

    try:
        result_path = run_quiz(
            quiz_path=str(input_path),
            output_path=output_path,
            processor=processor,
            mode=args.mode,
            use_rag=use_rag,
            n_results=args.results,
        )
        print(f"\nDone. Results at: {result_path}")
        return 0
    except (FileNotFoundError, ValueError) as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"Error during quiz: {e}", file=sys.stderr)
        return 1


def interactive_command(args) -> int:
    processor = _get_processor(args)
    history = ChatHistory(max_turns=args.history)

    print(f"\n{'=' * 60}")
    print("Cosmo — Interactive Mode")
    print(f"{'=' * 60}")
    print("Commands:")
    print("  Ask a question directly")
    print("  'mode <quick|deep|general|fast>' - Switch model")
    print("  'clear' - Clear conversation history")
    print("  'stats' - Show knowledge base stats")
    print("  'quit' or 'exit' - Exit")
    print(f"Conversation history: last {args.history} exchanges")
    print(f"{'=' * 60}\n")

    mode = args.mode

    while True:
        try:
            question = input(f"\n[{mode}] Question: ").strip()
            if not question:
                continue
            if question.lower() in ("quit", "exit", "q"):
                print("Goodbye!")
                break
            if question.lower() == "stats":
                list_command(args)
                continue
            if question.lower() == "clear":
                history.clear()
                print("Conversation history cleared.")
                continue
            if question.lower().startswith("mode "):
                parts = question.split(maxsplit=1)
                if len(parts) == 2 and parts[1] in ("quick", "deep", "general", "fast"):
                    mode = parts[1]
                    print(f"Switched to {mode} mode")
                else:
                    print("Invalid mode. Choose: quick, deep, general, fast")
                continue

            print("\nSearching...\n")
            for token in processor.ask_stream(
                question, mode=mode, n_results=args.results, history=history
            ):
                sys.stdout.write(token)
                sys.stdout.flush()
            print()

        except KeyboardInterrupt:
            print("\n\nGoodbye!")
            break
        except EOFError:
            print("\nGoodbye!")
            break
        except Exception as e:
            print(f"Error: {e}", file=sys.stderr)

    return 0


# ===================================================================
# Argument parser
# ===================================================================

def main():
    parser = argparse.ArgumentParser(
        description="Cosmo — RAG-powered documentation Q&A",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""\
Examples:
  python -m backend.cli ingest --path docs/react-handbook.pdf
  python -m backend.cli ingest --dir docs/
  python -m backend.cli ask -q "How do I type a useState hook?"
  python -m backend.cli quiz --input quizzes/w1.md
  python -m backend.cli interactive
  python -m backend.cli list
""",
    )

    parser.add_argument(
        "--db-path",
        default="./chroma_db",
        help="Path to ChromaDB database directory (default: ./chroma_db)",
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # ingest
    ingest_p = subparsers.add_parser("ingest", help="Ingest documents")
    ingest_p.add_argument("--path", help="Path to single file")
    ingest_p.add_argument("--dir", help="Directory to ingest")
    ingest_p.add_argument("--force", action="store_true", help="Force re-indexing")

    # ask
    ask_p = subparsers.add_parser("ask", help="Ask a question")
    ask_p.add_argument("--question", "-q", required=True, help="Question text")
    ask_p.add_argument("--mode", "-m", default="quick", choices=["quick", "deep", "general", "fast"])
    ask_p.add_argument("--results", "-n", type=int, default=4)

    # quiz
    quiz_p = subparsers.add_parser("quiz", help="Take a quiz")
    quiz_p.add_argument("--input", "-i", required=True, help="Quiz markdown file")
    quiz_p.add_argument("--output", "-o", default=None, help="Output path")
    quiz_p.add_argument("--mode", "-m", default="quick", choices=["quick", "deep", "general", "fast"])
    quiz_p.add_argument("--no-rag", action="store_true", help="Skip RAG context")
    quiz_p.add_argument("--results", "-n", type=int, default=4)

    # list
    subparsers.add_parser("list", help="List indexed documents")

    # interactive
    int_p = subparsers.add_parser("interactive", help="Interactive Q&A session")
    int_p.add_argument("--mode", "-m", default="quick", choices=["quick", "deep", "general", "fast"])
    int_p.add_argument("--results", "-n", type=int, default=4)
    int_p.add_argument("--history", type=int, default=5)

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 1

    commands = {
        "ingest": ingest_command,
        "ask": ask_command,
        "list": list_command,
        "interactive": interactive_command,
        "quiz": quiz_command,
    }
    return commands[args.command](args)


if __name__ == "__main__":
    sys.exit(main())
