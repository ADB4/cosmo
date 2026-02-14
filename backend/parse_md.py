#!/usr/bin/env python3
"""
parse_quizzes.py

Parses Week 13 and Week 14 quiz markdown files into structured JSON.
Incorporates review corrections identified during the quality audit.

Usage:
    python parse_quizzes.py w13.md w14.md

Outputs:
    w13.json, w14.json
"""

import json
import re
import sys
from pathlib import Path


# ─── Review Corrections ──────────────────────────────────────────────────────
# These dicts define corrections identified during the review audit.
# The parser applies them automatically during extraction.

W13_TF_CORRECTIONS = {
    11: {
        "explanation": (
            "False. This describes a false negative — the test fails to "
            "detect a real bug (the test passes, giving you false confidence). "
            "A false positive is when a test fails even though the behavior is "
            "correct (the test cries wolf)."
        )
    },
    24: {
        "explanation": (
            "True. `toBe` uses `Object.is()` for comparison, which behaves "
            "like `===` for most practical testing values. The technical "
            "difference: `Object.is(NaN, NaN)` is `true` (whereas `NaN === NaN` "
            "is `false`) and `Object.is(-0, +0)` is `false` (whereas "
            "`-0 === +0` is `true`). For everyday testing, the distinction "
            "rarely matters, but `Object.is()` is the actual mechanism."
        )
    },
}

W13_MC_CORRECTIONS = {
    4: {
        "explanation": (
            "A false negative means the test fails when the behavior is actually "
            "correct — the test falsely signals failure. Following KCD's convention: "
            "'negative' refers to the test outcome (fail), and 'false' means the "
            "outcome is wrong."
        )
    },
    5: {
        "explanation": (
            "A false positive means the test passes when the behavior is actually "
            "broken — the test falsely signals success. Following KCD's convention: "
            "'positive' refers to the test outcome (pass), and 'false' means the "
            "outcome is wrong."
        )
    },
    18: {
        "answer": 3,  # 0-indexed: option (d)
        "explanation": (
            "`toBe` uses `Object.is()` for comparison. While `Object.is()` "
            "behaves like `===` for most values, they differ on edge cases: "
            "`Object.is(NaN, NaN)` is `true` (unlike `===`), and "
            "`Object.is(-0, +0)` is `false` (unlike `===`). Since option (d) "
            "is the precise mechanism Vitest uses, it is the best answer."
        ),
    },
    33: {
        "options_replace": {
            1: "Never — they are tree-shaken from the production build when properly configured"
        }
    },
}

W13_SA_CORRECTIONS = {
    3: {
        "model_answer_append": (
            "\n\nNote: These definitions follow KCD's convention where 'positive' "
            "means the test passes and 'negative' means the test fails. Some sources "
            "reverse these terms. The key insight: a test that misses a real bug is "
            "the more dangerous failure mode."
        )
    },
}

W14_TF_CORRECTIONS = {
    9: {
        "explanation": (
            "False. RTL automatically calls `cleanup` after each test when it "
            "detects a supported framework. With Vitest, this works out of the "
            "box with no manual cleanup required. (`setupFiles` are typically "
            "used for other global setup like importing `@testing-library/jest-dom` "
            "matchers, not for cleanup.)"
        )
    },
    20: {
        "question": (
            "A `<select>` element without a `multiple` attribute and without "
            "a `size` attribute greater than 1 has an implicit ARIA role of "
            "`\"combobox\"`."
        ),
        "explanation": (
            "True. Per the HTML Accessibility API Mappings spec, a single-select "
            "`<select>` (no `multiple`, no `size > 1`) maps to the `combobox` role. "
            "A `<select>` with `multiple` or `size > 1` maps to `listbox` instead."
        ),
    },
    41: {
        "answer": False,
        "explanation": (
            "False. `user-event` is preferred for simulating user interactions "
            "(clicks, typing, tabbing), but `fireEvent` remains appropriate for "
            "non-user events like `resize`, `scroll`, or custom DOM events, and "
            "for cases where you need to dispatch a specific synthetic event. For "
            "the vast majority of component tests, `user-event` is the right choice."
        ),
    },
}

W14_MC_CORRECTIONS = {
    7: {
        "question": "What is the implicit ARIA role of a single-select `<select>` element?",
        "explanation": (
            "A single-select `<select>` element (no `multiple` attribute, no "
            "`size > 1`) has the implicit ARIA role `combobox`. A `<select>` "
            "with `multiple` or `size > 1` has the role `listbox`."
        ),
    },
}


# ─── Tag Inference ────────────────────────────────────────────────────────────

W13_TAG_KEYWORDS = {
    "testing-philosophy": [
        "testing trophy", "test behavior", "implementation detail",
        "false positive", "false negative", "confidence", "not too many",
        "mostly integration", "kent c. dodds", "kcd", "code coverage",
        "test worth", "not a goal", "100%",
    ],
    "testing-trophy": [
        "testing trophy", "testing pyramid", "static analysis", "unit test",
        "integration test", "end-to-end", "e2e", "layer", "base",
        "largest portion", "confidence", "cost",
    ],
    "vitest-config": [
        "vitest", "vite.config", "vitest.config", "globals", "setupfiles",
        "include", "test environment", "environment", "configuration",
        "config option",
    ],
    "vitest-api": [
        "describe", "it(", "test(", "expect", "beforeeach", "aftereach",
        "beforeall", "afterall", "it.skip", "it.only", "it.todo",
        "lifecycle hook", "watch mode", "vitest run", "test suite",
    ],
    "matchers": [
        "tobe", "toequal", "tostrictequal", "tobetruthy", "tobenull",
        "tobeundefined", "tothrow", "tocontain", "tohavelength",
        "tomatchobject", "tobegreaterthan", "tomatch", "expect.any",
        "expect.stringcontaining", "expect.assertions", "asymmetric matcher",
    ],
    "test-environments": [
        "jsdom", "happy-dom", "node", "dom environment", "document.createelement",
        "dom api", "@vitest-environment",
    ],
    "in-source-testing": [
        "in-source", "import.meta.vitest", "tree-shaken", "production build",
        "source file",
    ],
    "esbuild": [
        "esbuild", "typescript transform", "compilation step",
    ],
}

W14_TAG_KEYWORDS = {
    "rtl-philosophy": [
        "guiding principle", "resemble the way", "implementation detail",
        "test behavior", "isolation", "real children",
    ],
    "rtl-queries": [
        "getby", "queryby", "findby", "getallby", "queryallby",
        "screen", "query priority", "query hierarchy",
    ],
    "accessible-queries": [
        "getbyrole", "getbylabeltext", "getbytext", "getbytestid",
        "getbyplaceholdertext", "getbydisplayvalue", "getbyalttext",
        "getbytitle", "accessible name", "aria role", "aria-label",
        "implicit role",
    ],
    "aria-roles": [
        "aria role", "implicit role", "button", "textbox", "link",
        "heading", "checkbox", "combobox", "listbox", "listitem",
        "navigation", "dialog", "img", "level",
    ],
    "user-event": [
        "user-event", "userevent", "user.click", "user.type",
        "user.clear", "user.tab", "user.selectoptions", "user.keyboard",
        "user.hover", "fireevent", "character by character",
    ],
    "async-testing": [
        "waitfor", "findby", "waitforelementtoberemoved", "async",
        "promise", "timeout",
    ],
    "rtl-utilities": [
        "screen.debug", "logroles", "within", "cleanup", "wrapper",
        "render", "act(",
    ],
    "jest-dom": [
        "tobeinthedocument", "jest-dom", "custom matcher",
        "tohavetextcontent",
    ],
    "common-mistakes": [
        "common mistake", "kcd", "destructur", "act()", "fireevent",
        "gettestid",
    ],
}


def infer_tags(text: str, keyword_map: dict) -> list[str]:
    """Infer tags from question + explanation text using keyword matching."""
    lower = text.lower()
    tags = []
    for tag, keywords in keyword_map.items():
        for kw in keywords:
            if kw in lower:
                tags.append(tag)
                break
    return tags if tags else ["general"]


# ─── Markdown Parsing ─────────────────────────────────────────────────────────

def extract_tf_questions(lines: list[str]) -> list[dict]:
    """Extract True/False questions from the question section."""
    questions = []
    pattern = re.compile(r"^\*\*TF-(\d+)\.\*\*\s+(.*)")
    i = 0
    while i < len(lines):
        m = pattern.match(lines[i])
        if m:
            num = int(m.group(1))
            text = m.group(2).strip()
            # Continuation lines
            i += 1
            while i < len(lines) and lines[i].strip() and not pattern.match(lines[i]) and not lines[i].startswith("---") and not lines[i].startswith("##"):
                text += " " + lines[i].strip()
                i += 1
            questions.append({"num": num, "question": text})
        else:
            i += 1
    return questions


def extract_tf_answers(lines: list[str]) -> dict:
    """Extract TF answers from the answer key table."""
    answers = {}
    pattern = re.compile(r"^\|\s*TF-(\d+)\s*\|\s*\*\*(T|F)\*\*\s*\|\s*(.*?)\s*\|")
    for line in lines:
        m = pattern.match(line)
        if m:
            num = int(m.group(1))
            ans = m.group(2) == "T"
            expl = m.group(3).strip()
            answers[num] = {"answer": ans, "explanation": expl}
    return answers


def extract_sa_questions(lines: list[str]) -> list[dict]:
    """Extract Short Answer questions."""
    questions = []
    i = 0
    pattern = re.compile(r"^\*\*SA-(\d+)\.\*\*\s*(.*)")
    while i < len(lines):
        m = pattern.match(lines[i])
        if m:
            num = int(m.group(1))
            text = m.group(2).strip()
            i += 1
            # Collect continuation lines and code blocks
            while i < len(lines) and lines[i].strip() and not lines[i].startswith("---"):
                text += "\n" + lines[i]
                i += 1
            # Also grab code blocks that follow
            if i < len(lines) and i + 1 < len(lines):
                # Look ahead for code block
                j = i
                while j < len(lines) and not lines[j].strip():
                    j += 1
                if j < len(lines) and lines[j].strip().startswith("```"):
                    code = ""
                    code += lines[j] + "\n"
                    j += 1
                    while j < len(lines) and not lines[j].strip().startswith("```"):
                        code += lines[j] + "\n"
                        j += 1
                    if j < len(lines):
                        code += lines[j]
                    text += "\n\n" + code
                    i = j + 1
            questions.append({"num": num, "question": text.strip()})
        else:
            i += 1
    return questions


def extract_sa_answers(lines: list[str]) -> dict:
    """Extract SA model answers from the answer key section."""
    answers = {}
    i = 0
    pattern = re.compile(r"^\*\*SA-(\d+)\.\*\*")
    while i < len(lines):
        m = pattern.match(lines[i])
        if m:
            num = int(m.group(1))
            i += 1
            text = ""
            while i < len(lines) and not (lines[i].startswith("---") and lines[i].strip() == "---"):
                text += lines[i] + "\n"
                i += 1
            answers[num] = text.strip()
            i += 1  # skip the ---
        else:
            i += 1
    return answers


def extract_mc_questions(lines: list[str]) -> list[dict]:
    """Extract Multiple Choice questions with options."""
    questions = []
    i = 0
    q_pattern = re.compile(r"^\*\*MC-(\d+)\.\*\*\s+(.*)")
    opt_pattern = re.compile(r"^\(([a-d])\)\s+(.*)")

    while i < len(lines):
        m = q_pattern.match(lines[i])
        if m:
            num = int(m.group(1))
            text = m.group(2).strip()
            i += 1

            # Continuation of question text (non-blank, non-option, non-code, non-separator)
            while i < len(lines) and lines[i].strip() and not opt_pattern.match(lines[i]) and not lines[i].strip().startswith("```") and not lines[i].strip() == "---":
                text += " " + lines[i].strip()
                i += 1

            # Skip blank lines between question text and code/options
            while i < len(lines) and not lines[i].strip():
                i += 1

            # Check for code block
            code = None
            if i < len(lines) and lines[i].strip().startswith("```"):
                code_lines = []
                code_lines.append(lines[i])
                i += 1
                while i < len(lines) and not lines[i].strip().startswith("```"):
                    code_lines.append(lines[i])
                    i += 1
                if i < len(lines):
                    code_lines.append(lines[i])
                    i += 1
                code = "\n".join(code_lines)

            # Skip blank lines before options
            while i < len(lines) and not lines[i].strip():
                i += 1

            # Extract options
            options = []
            while i < len(lines):
                om = opt_pattern.match(lines[i])
                if om:
                    opt_text = om.group(2).strip()
                    i += 1
                    # Multi-line options
                    while i < len(lines) and lines[i].strip() and not opt_pattern.match(lines[i]) and not lines[i].startswith("---") and not q_pattern.match(lines[i]):
                        opt_text += " " + lines[i].strip()
                        i += 1
                    options.append(opt_text)
                else:
                    break

            q = {"num": num, "question": text, "options": options}
            if code:
                q["code"] = code
            questions.append(q)
        else:
            i += 1
    return questions


def extract_mc_answers(lines: list[str]) -> dict:
    """Extract MC answers from the answer key table."""
    answers = {}
    pattern = re.compile(r"^\|\s*MC-(\d+)\s*\|\s*\*\*\(([a-d])\)\*\*\s*\|\s*(.*?)\s*\|")
    for line in lines:
        m = pattern.match(line)
        if m:
            num = int(m.group(1))
            letter = m.group(2)
            expl = m.group(3).strip()
            answer_idx = ord(letter) - ord('a')
            answers[num] = {"answer": answer_idx, "explanation": expl}
    return answers


def parse_metadata(lines: list[str]) -> dict:
    """Extract scope, readings, and scoring from the header."""
    meta = {"scope": "", "readings": [], "scoring_note": ""}
    full = "\n".join(lines)

    # Scope
    scope_match = re.search(r"\*\*Scope:\*\*\s*(.*?)(?=\n\n|\n\*\*)", full, re.DOTALL)
    if scope_match:
        meta["scope"] = " ".join(scope_match.group(1).split())

    # Readings
    reading_section = re.search(r"\*\*Assigned Readings:\*\*\n(.*?)(?=\n\n|\n\*\*Scoring)", full, re.DOTALL)
    if reading_section:
        for line in reading_section.group(1).strip().split("\n"):
            line = line.strip()
            if line.startswith("- "):
                meta["readings"].append(line[2:].strip())

    # Scoring
    scoring_match = re.search(r"\*\*Scoring:\*\*\s*(.*?)(?=\n\n|\n---)", full, re.DOTALL)
    if scoring_match:
        meta["scoring_note"] = " ".join(scoring_match.group(1).split())

    return meta


def find_section_boundaries(lines: list[str]) -> dict:
    """Find line indices for each major section."""
    boundaries = {}
    answer_key_found = False
    for i, line in enumerate(lines):
        stripped = line.strip()
        if stripped.startswith("## Answer Key"):
            boundaries["answer_key_start"] = i
            answer_key_found = True
        elif not answer_key_found:
            # Question sections (before answer key)
            if "Part A: True / False" in stripped and stripped.startswith("##"):
                boundaries["tf_start"] = i
            elif "Part B: Short Answer" in stripped and stripped.startswith("##"):
                boundaries["sa_start"] = i
            elif "Part C: Multiple Choice" in stripped and stripped.startswith("##"):
                boundaries["mc_start"] = i
        else:
            # Answer key sections (after answer key header)
            if "Part A: True / False" in stripped:
                boundaries["tf_answer_start"] = i
            elif "Part B: Short Answer" in stripped:
                boundaries["sa_answer_start"] = i
            elif "Part C: Multiple Choice" in stripped:
                boundaries["mc_answer_start"] = i
    return boundaries


def parse_quiz_file(filepath: str, quiz_id: str, title: str,
                    tf_corrections: dict, mc_corrections: dict,
                    sa_corrections: dict, tag_keywords: dict) -> dict:
    """Parse a single quiz markdown file into structured JSON."""
    text = Path(filepath).read_text(encoding="utf-8")
    lines = text.split("\n")

    meta = parse_metadata(lines[:30])
    bounds = find_section_boundaries(lines)

    # ── Extract questions ──
    tf_questions = extract_tf_questions(lines[bounds["tf_start"]:bounds.get("sa_start", len(lines))])
    sa_questions = extract_sa_questions(lines[bounds["sa_start"]:bounds.get("mc_start", len(lines))])
    mc_questions = extract_mc_questions(lines[bounds["mc_start"]:bounds.get("answer_key_start", len(lines))])

    # ── Extract answers ──
    tf_answers = extract_tf_answers(lines[bounds.get("tf_answer_start", 0):bounds.get("sa_answer_start", len(lines))])
    sa_answers = extract_sa_answers(lines[bounds.get("sa_answer_start", 0):bounds.get("mc_answer_start", len(lines))])
    mc_answers = extract_mc_answers(lines[bounds.get("mc_answer_start", 0):])

    # ── Build TF section ──
    tf_items = []
    for q in tf_questions:
        num = q["num"]
        ans_data = tf_answers.get(num, {"answer": True, "explanation": ""})

        # Apply corrections
        correction = tf_corrections.get(num, {})
        question_text = correction.get("question", q["question"])
        answer = correction.get("answer", ans_data["answer"])
        explanation = correction.get("explanation", ans_data["explanation"])

        tags = infer_tags(question_text + " " + explanation, tag_keywords)

        tf_items.append({
            "id": f"TF-{num}",
            "question": question_text,
            "answer": answer,
            "explanation": explanation,
            "tags": tags,
        })

    # ── Build SA section ──
    sa_items = []
    for q in sa_questions:
        num = q["num"]
        model_answer = sa_answers.get(num, "")

        correction = sa_corrections.get(num, {})
        if "model_answer_append" in correction:
            model_answer += correction["model_answer_append"]

        tags = infer_tags(q["question"] + " " + model_answer, tag_keywords)

        sa_items.append({
            "id": f"SA-{num}",
            "question": q["question"],
            "model_answer": model_answer,
            "tags": tags,
        })

    # ── Build MC section ──
    mc_items = []
    for q in mc_questions:
        num = q["num"]
        ans_data = mc_answers.get(num, {"answer": 0, "explanation": ""})

        correction = mc_corrections.get(num, {})
        question_text = correction.get("question", q["question"])
        answer = correction.get("answer", ans_data["answer"])
        explanation = correction.get("explanation", ans_data["explanation"])

        options = list(q.get("options", []))
        if "options_replace" in correction:
            for idx, new_text in correction["options_replace"].items():
                if idx < len(options):
                    options[idx] = new_text

        tags = infer_tags(question_text + " " + explanation, tag_keywords)

        item = {
            "id": f"MC-{num}",
            "question": question_text,
            "options": options,
            "answer": answer,
            "explanation": explanation,
            "tags": tags,
        }
        if "code" in q:
            item["code"] = q["code"]

        mc_items.append(item)

    # ── Assemble final structure ──
    return {
        "version": "1.0",
        "quizzes": [
            {
                "id": quiz_id,
                "title": title,
                "scope": meta["scope"],
                "readings": meta["readings"],
                "scoring_note": meta["scoring_note"],
                "sections": [
                    {
                        "type": "true_false",
                        "count": len(tf_items),
                        "questions": tf_items,
                    },
                    {
                        "type": "short_answer",
                        "count": len(sa_items),
                        "questions": sa_items,
                    },
                    {
                        "type": "multiple_choice",
                        "count": len(mc_items),
                        "questions": mc_items,
                    },
                ],
            }
        ],
    }


def main():
    if len(sys.argv) < 3:
        print("Usage: python parse_quizzes.py <w13.md> <w14.md>")
        print("  Parses quiz markdown files into JSON with review corrections applied.")
        sys.exit(1)

    w13_path = sys.argv[1]
    w14_path = sys.argv[2]

    # Parse Week 13
    w13 = parse_quiz_file(
        w13_path,
        quiz_id="week13",
        title="Week 13: Testing Philosophy and Vitest Fundamentals",
        tf_corrections=W13_TF_CORRECTIONS,
        mc_corrections=W13_MC_CORRECTIONS,
        sa_corrections=W13_SA_CORRECTIONS,
        tag_keywords=W13_TAG_KEYWORDS,
    )

    # Parse Week 14
    w14 = parse_quiz_file(
        w14_path,
        quiz_id="week14",
        title="Week 14: React Testing Library — Rendering, Queries, and user-event",
        tf_corrections=W14_TF_CORRECTIONS,
        mc_corrections=W14_MC_CORRECTIONS,
        sa_corrections={},
        tag_keywords=W14_TAG_KEYWORDS,
    )

    # Write outputs
    w13_out = Path(w13_path).stem + ".json"
    w14_out = Path(w14_path).stem + ".json"

    with open(w13_out, "w", encoding="utf-8") as f:
        json.dump(w13, f, indent=2, ensure_ascii=False)
    print(f"Wrote {w13_out}: {len(w13['quizzes'][0]['sections'][0]['questions'])} TF, "
          f"{len(w13['quizzes'][0]['sections'][1]['questions'])} SA, "
          f"{len(w13['quizzes'][0]['sections'][2]['questions'])} MC")

    with open(w14_out, "w", encoding="utf-8") as f:
        json.dump(w14, f, indent=2, ensure_ascii=False)
    print(f"Wrote {w14_out}: {len(w14['quizzes'][0]['sections'][0]['questions'])} TF, "
          f"{len(w14['quizzes'][0]['sections'][1]['questions'])} SA, "
          f"{len(w14['quizzes'][0]['sections'][2]['questions'])} MC")


if __name__ == "__main__":
    main()