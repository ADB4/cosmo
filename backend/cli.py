#!/usr/bin/env python3
"""
Cosmo CLI — command-line interface for the RAG study companion.

Usage:
    python -m backend.cli ingest --dir docs/
    python -m backend.cli ask -q "How do I type a useState hook?"
    python -m backend.cli interactive
    python -m backend.cli quiz --input quizzes/w13.json
    python -m backend.cli quiz --input quizzes/w13.json --sections tf,mc --limit 10
    python -m backend.cli benchmark --input quizzes/w13.json --sections tf --limit 15
    python -m backend.cli list
"""

import argparse
import sys

from backend.document_processor import (
    ChatHistory,
    DocumentProcessor,
    OllamaConnectionError,
)
from backend.config import CHAT_MODELS, QUIZ_OPTIONS, DOCS_DIR, DB_PATH


def _get_processor(args) -> DocumentProcessor:
    try:
        return DocumentProcessor(persist_dir=args.db_path)
    except OllamaConnectionError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


def _parse_sections(raw: str | None) -> set[str] | None:
    """Parse a comma-separated section string into a set of qtype codes."""
    if not raw:
        return None
    from backend.quiz_processor import SECTION_ALIASES
    codes = set()
    for token in raw.split(","):
        token = token.strip().lower()
        if token in SECTION_ALIASES:
            codes.add(SECTION_ALIASES[token])
        else:
            print(f"Warning: unknown section '{token}', ignoring. "
                  f"Valid: tf, mc, sa", file=sys.stderr)
    return codes if codes else None


# ===================================================================
# Commands
# ===================================================================

def ingest_command(args) -> int:
    processor = _get_processor(args)

    if args.path:
            from pathlib import Path

            p = Path(args.path)
            if not p.exists():
                print(f"Error: Not found: {args.path}", file=sys.stderr)
                return 1

            # If --path points to a directory, treat it like --dir
            if p.is_dir():
                args.dir = args.path
                args.path = None
                return ingest_command(args)

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
        for token in processor.ask_question(
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
    from backend.quiz_processor import run_quiz, run_json_quiz, list_json_quizzes
    from pathlib import Path

    input_path = Path(args.input)
    if not input_path.exists():
        print(f"Error: File not found: {args.input}", file=sys.stderr)
        return 1

    is_json = input_path.suffix.lower() == ".json"
    grounded = not args.broad
    sections = _parse_sections(args.sections)
    limit = args.limit

    # --list flag: show available quizzes in a JSON file and exit
    if args.list_quizzes:
        if not is_json:
            print("Error: --list only works with JSON quiz files", file=sys.stderr)
            return 1
        try:
            quizzes = list_json_quizzes(str(input_path))
            print(f"\nQuizzes in {input_path.name}:")
            print(f"{'-' * 50}")
            for q in quizzes:
                print(f"  {q['id']:20s}  {q['title']}  ({q['questions']} questions)")
            print()
            return 0
        except Exception as e:
            print(f"Error: {e}", file=sys.stderr)
            return 1

    # Set up RAG processor
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

    output_path = args.output or f"results/{input_path.stem}-results.md"

    print(f"\n{'=' * 60}")
    print(f"  Cosmo Quiz Runner")
    print(f"{'=' * 60}")
    print(f"  Input:    {input_path}")
    print(f"  Mode:     {args.mode}")
    print(f"  RAG:      {'yes' if use_rag else 'no'}")
    print(f"  Grounded: {'yes (docs only)' if grounded else 'no (broad)'}")
    if sections:
        print(f"  Sections: {','.join(sorted(sections))}")
    if limit:
        print(f"  Limit:    {limit} questions")
    if is_json and args.quiz_id:
        print(f"  Quiz ID:  {args.quiz_id}")
    print(f"{'=' * 60}\n")

    try:
        if is_json:
            result_path = run_json_quiz(
                quiz_path=str(input_path),
                output_path=output_path,
                quiz_id=args.quiz_id,
                processor=processor,
                mode=args.mode,
                use_rag=use_rag,
                n_results=args.results,
                grounded=grounded,
                sections=sections,
                limit=limit,
            )
        else:
            result_path = run_quiz(
                quiz_path=str(input_path),
                output_path=output_path,
                processor=processor,
                mode=args.mode,
                use_rag=use_rag,
                n_results=args.results,
                grounded=grounded,
                sections=sections,
                limit=limit,
            )
        print(f"\nDone. Results at: {result_path}")
        return 0
    except (FileNotFoundError, ValueError) as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"Error during quiz: {e}", file=sys.stderr)
        return 1


def benchmark_command(args) -> int:
    from backend.quiz_processor import run_benchmark, run_multi_benchmark, BenchmarkConfig
    from pathlib import Path

    sections = _parse_sections(args.sections)
    limit = args.limit

    # Always need the processor for RAG configs
    processor = _get_processor(args)
    stats = processor.get_stats()
    if stats["total_chunks"] == 0:
        print("Warning: No documents indexed. RAG configs will run without context.")

    # Build config list: either from --configs or use defaults
    configs = None
    if args.configs:
        configs = _parse_benchmark_configs(args.configs)
        if not configs:
            return 1

    # Determine single file vs directory
    input_val = args.input or args.dir
    if not input_val:
        print("Error: Must specify --input or --dir", file=sys.stderr)
        return 1

    input_path = Path(input_val)
    if not input_path.exists():
        print(f"Error: Not found: {input_val}", file=sys.stderr)
        return 1

    try:
        if input_path.is_dir():
            # Multi-quiz: glob for .json and .md quiz files
            quiz_files = sorted(
                list(input_path.glob("*.json")) + list(input_path.glob("*.md"))
            )
            if not quiz_files:
                print(f"Error: No .json or .md files found in {input_path}",
                      file=sys.stderr)
                return 1

            print(f"Found {len(quiz_files)} quiz files in {input_path}")
            output_path = args.output or f"results/multi-benchmark.md"

            result_path = run_multi_benchmark(
                quiz_paths=[str(f) for f in quiz_files],
                output_path=output_path,
                processor=processor,
                configs=configs,
                n_results=args.results,
                sections=sections,
                limit=limit,
            )
        else:
            # Single quiz
            output_path = args.output or f"results/{input_path.stem}-benchmark.md"

            result_path = run_benchmark(
                quiz_path=str(input_path),
                output_path=output_path,
                processor=processor,
                quiz_id=args.quiz_id,
                configs=configs,
                n_results=args.results,
                sections=sections,
                limit=limit,
            )

        print(f"\nBenchmark report: {result_path}")
        return 0
    except (FileNotFoundError, ValueError) as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"Error during benchmark: {e}", file=sys.stderr)
        return 1


def _parse_benchmark_configs(raw: str) -> list | None:
    """
    Parse a compact config string into BenchmarkConfig objects.

    Format: "mode:rag|no-rag[:grounded|broad],..."
    The grounded/broad part is optional and defaults to broad.

    Examples:
        "qwen-7b:rag,qwen-14b:rag,mistral:no-rag"
        "qwen-7b:rag,qwen-7b:no-rag"
    """
    from backend.quiz_processor import BenchmarkConfig
    from backend.config import VALID_MODES

    configs = []
    for token in raw.split(","):
        parts = [p.strip().lower() for p in token.split(":")]
        if len(parts) not in (2, 3):
            print(f"Error: invalid config '{token}'. "
                  f"Expected format 'mode:rag|no-rag' or 'mode:rag|no-rag:grounded|broad'",
                  file=sys.stderr)
            return None

        mode = parts[0]
        rag_str = parts[1]
        ground_str = parts[2] if len(parts) == 3 else "broad"

        if mode not in VALID_MODES:
            print(f"Error: invalid mode '{mode}'. "
                  f"Valid: {', '.join(VALID_MODES)}", file=sys.stderr)
            return None

        if rag_str == "rag":
            use_rag = True
        elif rag_str == "no-rag":
            use_rag = False
        else:
            print(f"Error: invalid rag setting '{rag_str}'. "
                  f"Use 'rag' or 'no-rag'", file=sys.stderr)
            return None

        if ground_str == "grounded":
            grounded = True
        elif ground_str == "broad":
            grounded = False
        else:
            print(f"Error: invalid grounded setting '{ground_str}'. "
                  f"Use 'grounded' or 'broad'", file=sys.stderr)
            return None

        configs.append(BenchmarkConfig(mode=mode, use_rag=use_rag, grounded=grounded))

    return configs


def interactive_command(args) -> int:
    processor = _get_processor(args)
    history = ChatHistory(max_turns=args.history)

    print(f"\n{'=' * 60}")
    print("Cosmo — Interactive Mode")
    print(f"{'=' * 60}")
    print("Commands:")
    print("  Ask a question directly")
    print("  'mode <qwen-7b|qwen-14b|llama|mistral>' - Switch model")
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
                if len(parts) == 2 and parts[1] in ("qwen-7b", "qwen-14b", "llama", "mistral"):
                    mode = parts[1]
                    print(f"Switched to {mode} mode")
                else:
                    print("Invalid mode. Choose: qwen-7b, qwen-14b, llama, mistral")
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

  # Quiz with section filter and question limit
  python -m backend.cli quiz -i quizzes/w13.json --sections tf,mc --limit 10
  python -m backend.cli quiz -i quizzes/w13.json --quiz-id week13 --broad
  python -m backend.cli quiz -i quizzes/w13.json --sections sa
  python -m backend.cli quiz -i quizzes/w13.json --list

  # Benchmark across all model/rag combos (8 configs)
  python -m backend.cli benchmark -i quizzes/w13.json --sections tf --limit 15
  python -m backend.cli benchmark -i quizzes/w13.json --configs "qwen-7b:rag,qwen-14b:rag,mistral:no-rag"

  # Benchmark across all quiz files in a directory
  python -m backend.cli benchmark --dir quizzes/ --sections tf,mc
  python -m backend.cli benchmark --dir quizzes/ --configs "qwen-7b:rag,qwen-14b:rag" --limit 20

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
    ask_p.add_argument("--mode", "-m", default="qwen-7b", choices=list(CHAT_MODELS.keys()))
    ask_p.add_argument("--results", "-n", type=int, default=4)

    # quiz
    quiz_p = subparsers.add_parser("quiz", help="Take a quiz (supports .md and .json)")
    quiz_p.add_argument("--input", "-i", required=True, help="Quiz file (.md or .json)")
    quiz_p.add_argument("--output", "-o", default=None, help="Output results path")
    quiz_p.add_argument("--mode", "-m", default="qwen-7b", choices=list(QUIZ_OPTIONS.keys()))
    quiz_p.add_argument("--no-rag", action="store_true", help="Skip RAG context")
    quiz_p.add_argument("--broad", action="store_true",
                        help="Use broad mode (LLM supplements with own knowledge)")
    quiz_p.add_argument("--results", "-n", type=int, default=4)
    quiz_p.add_argument("--quiz-id", default=None,
                        help="Quiz ID to run (for JSON files with multiple quizzes)")
    quiz_p.add_argument("--list", dest="list_quizzes", action="store_true",
                        help="List available quizzes in a JSON file and exit")
    quiz_p.add_argument("--sections", "-s", default=None,
                        help="Comma-separated question types to include: tf,mc,sa")
    quiz_p.add_argument("--limit", "-l", type=int, default=None,
                        help="Max number of questions to run (sampled from filtered set)")

    # benchmark
    bench_p = subparsers.add_parser("benchmark",
                                    help="Compare quiz performance across configurations")
    bench_input = bench_p.add_mutually_exclusive_group(required=True)
    bench_input.add_argument("--input", "-i", default=None,
                             help="Single quiz file (.md or .json)")
    bench_input.add_argument("--dir", "-d", default=None,
                             help="Directory of quiz files (runs all, produces combined report)")
    bench_p.add_argument("--output", "-o", default=None, help="Output report path")
    bench_p.add_argument("--quiz-id", default=None,
                         help="Quiz ID (for single JSON files with multiple quizzes)")
    bench_p.add_argument("--results", "-n", type=int, default=4)
    bench_p.add_argument("--sections", "-s", default=None,
                         help="Comma-separated question types: tf,mc,sa")
    bench_p.add_argument("--limit", "-l", type=int, default=None,
                         help="Max questions per quiz per run")
    bench_p.add_argument("--configs", default=None,
                         help="Custom configs: 'mode:rag|no-rag:grounded|broad,...' "
                              "(default: all 8 model/rag combos)")

    # list
    subparsers.add_parser("list", help="List indexed documents")

    # interactive
    int_p = subparsers.add_parser("interactive", help="Interactive Q&A session")
    int_p.add_argument("--mode", "-m", default="qwen-7b", choices=list(QUIZ_OPTIONS.keys()))
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
        "benchmark": benchmark_command,
    }
    return commands[args.command](args)


if __name__ == "__main__":
    sys.exit(main())