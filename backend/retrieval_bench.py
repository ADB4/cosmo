#!/usr/bin/env python3
"""
Cosmo Retrieval Benchmark — evaluate retrieval quality and LLM responses
for open-ended questions.

Usage:
    python -m backend.retrieval_bench -i retrieval-test-questions.json
    python -m backend.retrieval_bench -i retrieval-test-questions.json --mode qwen-7b
    python -m backend.retrieval_bench -i retrieval-test-questions.json --modes qwen-7b,gemma2-9b
    python -m backend.retrieval_bench -i retrieval-test-questions.json --retrieval-only
    python -m backend.retrieval_bench -i retrieval-test-questions.json --category rtl
"""

import argparse
import json
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Set

from backend.document_processor import DocumentProcessor, OllamaConnectionError
from backend.config import CHAT_MODELS, CHAT_OPTIONS


# ---------------------------------------------------------------------------
# Data structures
# ---------------------------------------------------------------------------

@dataclass
class RetrievalResult:
    """Result for a single question's retrieval + LLM response."""
    question: str
    category: str
    expected_sources: List[str]
    retrieved_sources: List[str]        # source filenames from top-N
    retrieved_breadcrumbs: List[str]    # full breadcrumb labels
    source_hit: bool                    # did any expected source appear?
    llm_responses: Dict[str, str] = field(default_factory=dict)  # mode -> response
    elapsed: Dict[str, float] = field(default_factory=dict)      # mode -> seconds


# ---------------------------------------------------------------------------
# Core logic
# ---------------------------------------------------------------------------

def run_retrieval_bench(
    test_path: str,
    processor: DocumentProcessor,
    n_results: int = 8,
    modes: Optional[List[str]] = None,
    retrieval_only: bool = False,
    category_filter: Optional[str] = None,
) -> List[RetrievalResult]:
    """Run the retrieval benchmark and optionally collect LLM responses."""

    with open(test_path, "r") as f:
        data = json.load(f)

    tests = data.get("retrieval_tests", [])
    results: List[RetrievalResult] = []

    for group in tests:
        cat = group["category"]
        if category_filter and cat != category_filter:
            continue

        expected = group.get("expected_sources", [])
        questions = group["questions"]

        print(f"\n{'=' * 60}")
        print(f"  Category: {cat} ({len(questions)} questions)")
        print(f"  Expected sources: {expected}")
        print(f"{'=' * 60}")

        for qi, question in enumerate(questions):
            print(f"\n  [{qi + 1}/{len(questions)}] {question}")

            # -- Retrieval --
            query_results = processor.query(question, n_results=n_results)

            sources = []
            breadcrumbs = []
            for meta in query_results["metadatas"][0]:
                src = meta.get("source", "unknown")
                bc = meta.get("breadcrumb", "")
                heading = meta.get("heading", "")
                page = meta.get("page", "")

                if bc:
                    label = f"{src} > {bc}"
                elif heading:
                    label = f"{src} > {heading}"
                elif page:
                    label = f"{src}, page {page}"
                else:
                    label = src

                sources.append(src)
                breadcrumbs.append(label)

            # Check if any expected source appears in retrieved sources
            if expected == ["mixed"]:
                hit = True  # cross-cutting questions don't have strict source expectations
            else:
                hit = any(
                    any(exp.lower() in src.lower() for exp in expected)
                    for src in sources
                )

            icon = "+" if hit else "x"
            print(f"    Retrieval [{icon}]: {sources[:4]}...")

            result = RetrievalResult(
                question=question,
                category=cat,
                expected_sources=expected,
                retrieved_sources=sources,
                retrieved_breadcrumbs=breadcrumbs,
                source_hit=hit,
            )

            # -- LLM responses --
            if not retrieval_only and modes:
                for mode in modes:
                    print(f"    Generating response ({mode})...", end=" ", flush=True)
                    t0 = time.time()

                    full_response = ""
                    try:
                        for token in processor.ask_question(
                            question, mode=mode, n_results=n_results
                        ):
                            full_response += token
                    except Exception as e:
                        full_response = f"[error: {e}]"

                    elapsed = time.time() - t0
                    result.llm_responses[mode] = full_response
                    result.elapsed[mode] = elapsed
                    print(f"({elapsed:.1f}s)")

            results.append(result)

    return results


# ---------------------------------------------------------------------------
# Report generation
# ---------------------------------------------------------------------------

def write_report(
    results: List[RetrievalResult],
    output_path: str,
    modes: List[str],
    n_results: int,
    retrieval_only: bool,
) -> str:
    """Write a markdown report with retrieval stats and LLM responses."""

    Path(output_path).parent.mkdir(parents=True, exist_ok=True)

    categories = {}
    for r in results:
        categories.setdefault(r.category, []).append(r)

    total = len(results)
    total_hits = sum(1 for r in results if r.source_hit)

    lines = []
    lines.append("# Retrieval Benchmark Report\n")
    lines.append(f"**n_results:** {n_results}  ")
    lines.append(f"**Total questions:** {total}  ")
    lines.append(f"**Retrieval hit rate:** {total_hits}/{total} "
                 f"({total_hits / total * 100:.0f}%)\n")

    if modes and not retrieval_only:
        lines.append(f"**Models tested:** {', '.join(modes)}\n")

    # -- Summary table --
    lines.append("## Summary by Category\n")
    lines.append("| Category | Questions | Hits | Hit Rate |")
    lines.append("|----------|-----------|------|----------|")
    for cat, cat_results in categories.items():
        cat_total = len(cat_results)
        cat_hits = sum(1 for r in cat_results if r.source_hit)
        pct = cat_hits / cat_total * 100 if cat_total > 0 else 0
        lines.append(f"| {cat} | {cat_total} | {cat_hits} | {pct:.0f}% |")
    lines.append("")

    # -- Retrieval misses --
    misses = [r for r in results if not r.source_hit]
    if misses:
        lines.append("## Retrieval Misses\n")
        lines.append("Questions where expected sources did not appear in top results:\n")
        for r in misses:
            lines.append(f"**Q:** {r.question}  ")
            lines.append(f"**Expected:** {r.expected_sources}  ")
            lines.append(f"**Got:** {r.retrieved_sources[:5]}  ")
            lines.append("")

    # -- Per-question detail --
    lines.append("## Per-Question Detail\n")

    for cat, cat_results in categories.items():
        lines.append(f"### {cat}\n")

        for r in cat_results:
            icon = "PASS" if r.source_hit else "MISS"
            lines.append(f"#### [{icon}] {r.question}\n")
            lines.append("**Retrieved sources:**\n")
            for i, bc in enumerate(r.retrieved_breadcrumbs):
                lines.append(f"  [{i + 1}] {bc}  ")
            lines.append("")

            # LLM responses
            if r.llm_responses:
                for mode, response in r.llm_responses.items():
                    elapsed = r.elapsed.get(mode, 0)
                    lines.append(f"**{mode}** ({elapsed:.1f}s):\n")
                    lines.append(f"{response}\n")
                    lines.append("")

        lines.append("---\n")

    report = "\n".join(lines)
    with open(output_path, "w") as f:
        f.write(report)

    return output_path


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main() -> int:
    parser = argparse.ArgumentParser(
        description="Cosmo Retrieval Benchmark",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python -m backend.retrieval_bench -i retrieval-test-questions.json
  python -m backend.retrieval_bench -i retrieval-test-questions.json --modes qwen-7b,gemma2-9b
  python -m backend.retrieval_bench -i retrieval-test-questions.json --retrieval-only
  python -m backend.retrieval_bench -i retrieval-test-questions.json --category rtl
""",
    )

    parser.add_argument("--input", "-i", required=True, help="Retrieval test JSON file")
    parser.add_argument("--output", "-o", default=None, help="Output report path")
    parser.add_argument("--db-path", default="./chroma_db", help="ChromaDB path")
    parser.add_argument("--results", "-n", type=int, default=8, help="n_results for retrieval")
    parser.add_argument("--modes", default="qwen-7b",
                        help="Comma-separated models to test (default: qwen-7b)")
    parser.add_argument("--retrieval-only", action="store_true",
                        help="Only test retrieval, skip LLM responses")
    parser.add_argument("--category", "-c", default=None,
                        help="Only run a specific category (typescript, vitest_api, rtl, cross_cutting)")

    args = parser.parse_args()

    input_path = Path(args.input)
    if not input_path.exists():
        print(f"Error: Not found: {args.input}", file=sys.stderr)
        return 1

    try:
        processor = DocumentProcessor(persist_dir=args.db_path)
    except OllamaConnectionError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1

    modes = [m.strip() for m in args.modes.split(",")] if not args.retrieval_only else []

    # Validate modes
    for mode in modes:
        if mode not in CHAT_MODELS:
            print(f"Error: Unknown mode '{mode}'. Valid: {', '.join(CHAT_MODELS.keys())}",
                  file=sys.stderr)
            return 1

    output_path = args.output or f"results/{input_path.stem}-retrieval.md"

    print(f"\n{'=' * 60}")
    print(f"  Cosmo Retrieval Benchmark")
    print(f"{'=' * 60}")
    print(f"  Input:    {input_path}")
    print(f"  n_results: {args.results}")
    if args.retrieval_only:
        print(f"  Mode:     retrieval only (no LLM)")
    else:
        print(f"  Models:   {', '.join(modes)}")
    if args.category:
        print(f"  Category: {args.category}")
    print(f"{'=' * 60}")

    results = run_retrieval_bench(
        str(input_path),
        processor,
        n_results=args.results,
        modes=modes,
        retrieval_only=args.retrieval_only,
        category_filter=args.category,
    )

    report_path = write_report(
        results, output_path, modes, args.results, args.retrieval_only,
    )

    # Print summary
    total = len(results)
    hits = sum(1 for r in results if r.source_hit)
    print(f"\n{'=' * 60}")
    print(f"  Retrieval hit rate: {hits}/{total} ({hits / total * 100:.0f}%)")
    print(f"  Report: {report_path}")
    print(f"{'=' * 60}\n")

    return 0


if __name__ == "__main__":
    sys.exit(main())