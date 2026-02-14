"""
Quiz Processor — parse quiz files, send to Ollama, grade results.

Handles:
- Parsing quiz markdown files into question sections and answer keys
- Parsing quiz JSON files (Apollo format) into the same structures
- Sending questions to Ollama (with optional RAG context)
- Grading LLM responses against the answer key
- Writing structured results to output files
- Benchmarking across configurations (mode, RAG, grounded)
"""

import json
import logging
import random
import re
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------

@dataclass
class Question:
    id: str
    qtype: str  # "tf", "sa", or "mc"
    text: str
    choices: List[str] = field(default_factory=list)
    code: Optional[str] = None


@dataclass
class AnswerKeyEntry:
    id: str
    answer: str
    explanation: str = ""


@dataclass
class GradedQuestion:
    question: Question
    llm_answer: str
    llm_extracted: str
    correct_answer: str
    correct_explanation: str
    is_correct: Optional[bool]
    score: float


@dataclass
class BenchmarkResult:
    """Results from a single benchmark run."""
    label: str
    mode: str
    use_rag: bool
    grounded: bool
    total: int
    correct: int
    incorrect: int
    ungraded: int
    accuracy: float  # correct / (total - ungraded), 0-1
    elapsed: float   # seconds
    graded: List[GradedQuestion]


# ---------------------------------------------------------------------------
# Quiz parser — markdown
# ---------------------------------------------------------------------------

class QuizParser:
    """Parse a quiz markdown file into questions and answer key."""

    _QUESTION_ID_RE = re.compile(
        r"^\*\*(?P<id>(?:TF|SA|MC)-\d+)\.\*\*\s*", re.MULTILINE
    )
    _CHOICE_RE = re.compile(r"^\(([a-d])\)\s+(.+)$", re.MULTILINE)
    _TABLE_ROW_RE = re.compile(
        r"^\|\s*(?P<id>(?:TF|SA|MC)-\d+)\s*\|\s*"
        r"\*?\*?\(?(?P<answer>[TFabcd])\)?\*?\*?\s*\|\s*"
        r"(?P<explanation>.*?)\s*\|$",
        re.MULTILINE,
    )

    def parse(self, content: str) -> Tuple[List[Question], List[AnswerKeyEntry]]:
        questions = self._parse_questions(content)
        answer_key = self._parse_answer_key(content)
        return questions, answer_key

    def _parse_questions(self, content: str) -> List[Question]:
        questions: List[Question] = []
        matches = list(self._QUESTION_ID_RE.finditer(content))

        for i, match in enumerate(matches):
            qid = match.group("id")
            start = match.end()
            end = matches[i + 1].start() if i + 1 < len(matches) else len(content)
            body = content[start:end].strip()

            if qid.startswith("TF"):
                qtype = "tf"
            elif qid.startswith("MC"):
                qtype = "mc"
            else:
                qtype = "sa"

            choices: List[str] = []
            if qtype == "mc":
                for cm in self._CHOICE_RE.finditer(body):
                    choices.append(f"({cm.group(1)}) {cm.group(2)}")

            questions.append(Question(id=qid, qtype=qtype, text=body, choices=choices))

        return questions

    def _parse_answer_key(self, content: str) -> List[AnswerKeyEntry]:
        entries: List[AnswerKeyEntry] = []
        for m in self._TABLE_ROW_RE.finditer(content):
            entries.append(
                AnswerKeyEntry(
                    id=m.group("id"),
                    answer=m.group("answer").strip(),
                    explanation=m.group("explanation").strip(),
                )
            )
        return entries


# ---------------------------------------------------------------------------
# Quiz parser — JSON (Apollo format)
# ---------------------------------------------------------------------------

def parse_json_quiz(
    data: dict,
    quiz_id: Optional[str] = None,
) -> Tuple[List[Question], Dict[str, AnswerKeyEntry], dict]:
    """
    Parse an Apollo-format JSON quiz into Question and AnswerKeyEntry objects.

    The JSON structure has:
      { "quizzes": [ { "id", "title", "sections": [ { "type", "questions": [...] } ] } ] }

    Section types: "true_false", "short_answer", "multiple_choice"

    Args:
        data: Parsed JSON dict (the full file with "quizzes" array).
        quiz_id: If the file contains multiple quizzes, select this one.
            If None and only one quiz exists, uses that one.

    Returns:
        (questions, answer_key_dict, quiz_metadata)
    """
    quizzes = data.get("quizzes", [])
    if not quizzes:
        raise ValueError("No quizzes found in JSON file")

    if quiz_id:
        quiz = next((q for q in quizzes if q.get("id") == quiz_id), None)
        if quiz is None:
            available = [q.get("id", "?") for q in quizzes]
            raise ValueError(
                f"Quiz '{quiz_id}' not found. Available: {', '.join(available)}"
            )
    elif len(quizzes) == 1:
        quiz = quizzes[0]
    else:
        available = [q.get("id", "?") for q in quizzes]
        raise ValueError(
            f"Multiple quizzes in file. Specify --quiz-id. "
            f"Available: {', '.join(available)}"
        )

    questions: List[Question] = []
    answer_key: Dict[str, AnswerKeyEntry] = {}

    for section in quiz.get("sections", []):
        sec_type = section.get("type", "")

        for q in section.get("questions", []):
            qid = q.get("id", "")

            if sec_type == "true_false":
                questions.append(Question(
                    id=qid,
                    qtype="tf",
                    text=q.get("question", ""),
                ))
                answer_key[qid] = AnswerKeyEntry(
                    id=qid,
                    answer="T" if q.get("answer") is True else "F",
                    explanation=q.get("explanation", ""),
                )

            elif sec_type == "multiple_choice":
                options = q.get("options", [])
                choices = [
                    f"({chr(ord('a') + i)}) {opt}"
                    for i, opt in enumerate(options)
                ]
                questions.append(Question(
                    id=qid,
                    qtype="mc",
                    text=q.get("question", ""),
                    choices=choices,
                    code=q.get("code"),
                ))
                ans_idx = q.get("answer", 0)
                answer_key[qid] = AnswerKeyEntry(
                    id=qid,
                    answer=chr(ord("a") + int(ans_idx)),
                    explanation=q.get("explanation", ""),
                )

            elif sec_type == "short_answer":
                questions.append(Question(
                    id=qid,
                    qtype="sa",
                    text=q.get("question", ""),
                ))
                answer_key[qid] = AnswerKeyEntry(
                    id=qid,
                    answer=q.get("model_answer", ""),
                    explanation="",
                )

    metadata = {
        "quiz_id": quiz.get("id", ""),
        "title": quiz.get("title", ""),
        "scope": quiz.get("scope", ""),
    }

    return questions, answer_key, metadata


def list_json_quizzes(path: str) -> List[dict]:
    """List all quizzes available in a JSON file."""
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    results = []
    for quiz in data.get("quizzes", []):
        total = sum(
            len(s.get("questions", []))
            for s in quiz.get("sections", [])
        )
        results.append({
            "id": quiz.get("id", "?"),
            "title": quiz.get("title", "?"),
            "questions": total,
        })
    return results


# ---------------------------------------------------------------------------
# Question filtering
# ---------------------------------------------------------------------------

# Map user-friendly names to internal qtype codes
SECTION_ALIASES: Dict[str, str] = {
    "tf": "tf",
    "true_false": "tf",
    "mc": "mc",
    "multiple_choice": "mc",
    "sa": "sa",
    "short_answer": "sa",
}


def filter_questions(
    questions: List[Question],
    answer_key: Dict[str, AnswerKeyEntry],
    sections: Optional[Set[str]] = None,
    limit: Optional[int] = None,
    shuffle: bool = False,
) -> Tuple[List[Question], Dict[str, AnswerKeyEntry]]:
    """
    Filter and optionally limit the question set.

    Args:
        questions: Full list of parsed questions.
        answer_key: Full answer key dict.
        sections: If provided, only include questions whose qtype is in this set.
            Values should be internal codes: {"tf", "mc", "sa"}.
        limit: If provided, take at most this many questions (after section filter).
        shuffle: If True, randomize order before limiting. Useful for sampling.

    Returns:
        (filtered_questions, filtered_answer_key) — answer key is pruned
        to only include entries for the returned questions.
    """
    filtered = questions

    if sections:
        filtered = [q for q in filtered if q.qtype in sections]

    if shuffle:
        filtered = list(filtered)
        random.shuffle(filtered)

    if limit is not None and limit < len(filtered):
        filtered = filtered[:limit]

    # Prune answer key to match
    filtered_ids = {q.id for q in filtered}
    pruned_key = {k: v for k, v in answer_key.items() if k in filtered_ids}

    return filtered, pruned_key


# ---------------------------------------------------------------------------
# Answer extraction
# ---------------------------------------------------------------------------

def extract_answer(llm_response: str, qtype: str) -> str:
    """
    Extract a normalized answer from an LLM response.

    For TF: returns "T" or "F".
    For MC: returns a letter "a"-"d".
    For SA: returns the full response.

    Uses a multi-pass strategy:
      1. Check if response starts with the answer
      2. Scan the first sentence / first few lines for clear signals
      3. Scan the full response for definitive patterns
      4. Fall back to "?" if nothing found
    """
    cleaned = llm_response.strip()
    if not cleaned:
        return "?"

    if qtype == "tf":
        return _extract_tf(cleaned)

    if qtype == "mc":
        return _extract_mc(cleaned)

    return cleaned


def _extract_tf(response: str) -> str:
    """Extract True/False from an LLM response with multi-pass scanning."""
    lower = response.lower()

    # Pass 1: starts with True/False (possibly after whitespace or **)
    stripped_start = re.sub(r"^[\s*#>\-]+", "", lower)
    if stripped_start.startswith("true"):
        return "T"
    if stripped_start.startswith("false"):
        return "F"

    # Pass 2: first line contains a clear verdict
    first_line = lower.split("\n")[0]
    # Patterns like "the answer is true", "this is false", "the statement is true"
    verdict_match = re.search(
        r"\b(?:answer|statement|claim|assertion|this)\s+is\s+(true|false)\b",
        first_line,
    )
    if verdict_match:
        return "T" if verdict_match.group(1) == "true" else "F"

    # "True." or "False." or "True," or "True:" standalone-ish in first line
    tf_word = re.search(r"\b(true|false)\b", first_line)
    if tf_word:
        return "T" if tf_word.group(1) == "true" else "F"

    # Pass 3: scan first 3 lines for "**True**", "**False**", ": True", etc.
    first_lines = "\n".join(lower.split("\n")[:3])

    bold_match = re.search(r"\*\*(true|false)\*\*", first_lines)
    if bold_match:
        return "T" if bold_match.group(1) == "true" else "F"

    colon_match = re.search(r":\s*(true|false)\b", first_lines)
    if colon_match:
        return "T" if colon_match.group(1) == "true" else "F"

    # Pass 4: anywhere in response, look for definitive verdict patterns
    verdict_anywhere = re.search(
        r"\b(?:the\s+)?(?:correct\s+)?answer\s+is\s+(true|false)\b", lower
    )
    if verdict_anywhere:
        return "T" if verdict_anywhere.group(1) == "true" else "F"

    # Pass 5: count occurrences — if the response says "true" or "false"
    # exactly once (outside of quoting the question), that's likely the answer
    true_count = len(re.findall(r"\btrue\b", lower))
    false_count = len(re.findall(r"\bfalse\b", lower))

    if true_count > 0 and false_count == 0:
        return "T"
    if false_count > 0 and true_count == 0:
        return "F"

    return "?"


def _extract_mc(response: str) -> str:
    """Extract multiple choice letter from an LLM response with multi-pass scanning."""
    cleaned = response.strip()
    lower = cleaned.lower()

    # Pass 1: parenthesized letter like (a), (b), etc.
    m = re.search(r"\(([a-d])\)", cleaned)
    if m:
        return m.group(1)

    # Pass 2: "answer is (a)" or "answer is a" patterns
    verdict = re.search(
        r"\b(?:the\s+)?(?:correct\s+)?answer\s+is\s+\(?([a-d])\)?\b", lower
    )
    if verdict:
        return verdict.group(1)

    # Pass 3: bold letter like **a**, **b**
    bold = re.search(r"\*\*\(?([a-d])\)?\*\*", lower)
    if bold:
        return bold.group(1)

    # Pass 4: letter followed by period/colon at start of line — "a. " or "a: "
    line_start = re.search(r"(?:^|\n)\s*([a-d])[.:)\s]", lower)
    if line_start:
        return line_start.group(1)

    # Pass 5: first standalone letter a-d in the response
    for char in cleaned:
        if char.lower() in "abcd":
            return char.lower()

    return "?"


# ---------------------------------------------------------------------------
# Grading
# ---------------------------------------------------------------------------

def grade_question(
    question: Question,
    llm_answer: str,
    answer_key: Dict[str, AnswerKeyEntry],
) -> GradedQuestion:
    entry = answer_key.get(question.id)
    if entry is None:
        return GradedQuestion(
            question=question,
            llm_answer=llm_answer,
            llm_extracted="?",
            correct_answer="?",
            correct_explanation="No answer key entry",
            is_correct=None,
            score=0,
        )

    extracted = extract_answer(llm_answer, question.qtype)

    if question.qtype in ("tf", "mc"):
        is_correct = extracted.upper() == entry.answer.upper()
        score = 1.0 if is_correct else -1.0
    else:
        is_correct = None
        score = 0.0

    return GradedQuestion(
        question=question,
        llm_answer=llm_answer,
        llm_extracted=extracted,
        correct_answer=entry.answer,
        correct_explanation=entry.explanation,
        is_correct=is_correct,
        score=score,
    )


def _score_summary(graded: List[GradedQuestion]) -> Tuple[int, int, int, int, float]:
    """Return (total, correct, incorrect, ungraded, accuracy)."""
    total = len(graded)
    correct = sum(1 for g in graded if g.is_correct is True)
    incorrect = sum(1 for g in graded if g.is_correct is False)
    ungraded = sum(1 for g in graded if g.is_correct is None)
    gradable = total - ungraded
    accuracy = correct / gradable if gradable > 0 else 0.0
    return total, correct, incorrect, ungraded, accuracy


# ---------------------------------------------------------------------------
# Results writer
# ---------------------------------------------------------------------------

def write_results(graded: List[GradedQuestion], output_path: str, metadata: Dict) -> str:
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    total, correct, incorrect, ungraded, accuracy = _score_summary(graded)
    score_sum = sum(g.score for g in graded)

    with open(path, "w", encoding="utf-8") as f:
        f.write("# Quiz Results\n\n")
        if metadata.get("title"):
            f.write(f"- **Quiz:** {metadata['title']}\n")
        f.write(f"- **Mode:** {metadata.get('mode', '?')}\n")
        f.write(f"- **RAG:** {'yes' if metadata.get('use_rag') else 'no'}\n")
        f.write(f"- **Grounded:** {'yes' if metadata.get('grounded', True) else 'no (broad)'}\n")
        if metadata.get("sections"):
            f.write(f"- **Sections:** {metadata['sections']}\n")
        if metadata.get("limit"):
            f.write(f"- **Limit:** {metadata['limit']} questions\n")
        f.write(f"- **Total:** {total}\n")
        f.write(f"- **Correct:** {correct}\n")
        f.write(f"- **Incorrect:** {incorrect}\n")
        f.write(f"- **Ungraded (SA):** {ungraded}\n")
        f.write(f"- **Accuracy:** {accuracy * 100:.0f}%\n")
        f.write(f"- **Score:** {score_sum:.0f}\n\n---\n\n")

        for g in graded:
            icon = "?" if g.is_correct is None else ("+" if g.is_correct else "x")
            f.write(f"## [{icon}] {g.question.id}\n\n")
            f.write(f"**Question:** {g.question.text[:200]}")
            if len(g.question.text) > 200:
                f.write("...")
            f.write("\n\n")
            if g.question.code:
                f.write(f"```\n{g.question.code}\n```\n\n")
            if g.question.choices:
                f.write("Choices:\n")
                for c in g.question.choices:
                    f.write(f"  {c}\n")
                f.write("\n")
            f.write(f"**LLM answer:** {g.llm_extracted}\n\n")
            f.write(f"**Correct:** {g.correct_answer}\n\n")
            if g.correct_explanation:
                f.write(f"**Explanation:** {g.correct_explanation}\n\n")
            if g.question.qtype == "sa":
                f.write(f"**Full LLM response:**\n{g.llm_answer[:500]}\n\n")
            f.write("---\n\n")

    return str(path)


# ---------------------------------------------------------------------------
# Prompt builder for quiz questions
# ---------------------------------------------------------------------------

def build_quiz_prompt(
    question: Question,
    rag_context: Optional[str] = None,
) -> str:
    """
    Build a focused prompt for a quiz question.

    Uses tighter instructions than general chat to get concise,
    extractable answers.
    """
    parts = []

    if rag_context:
        parts.append(f"Documentation context:\n{rag_context}")

    if question.qtype == "tf":
        parts.append(
            "Answer this True/False question. Start your response with "
            "exactly 'True' or 'False', then briefly explain why."
        )
    elif question.qtype == "mc":
        parts.append(
            "Answer this multiple choice question. Start your response with "
            "the letter of the correct choice in parentheses, e.g. (a), "
            "then briefly explain why."
        )
    else:
        parts.append(
            "Answer this short answer question concisely but completely. "
            "Focus on technical accuracy."
        )

    parts.append(question.text)

    if question.code:
        parts.append(f"```\n{question.code}\n```")

    if question.choices:
        parts.append("\n".join(question.choices))

    return "\n\n".join(parts)


# ---------------------------------------------------------------------------
# Load + filter helpers (shared by run_* and benchmark)
# ---------------------------------------------------------------------------

def _load_questions(
    quiz_path: str,
    quiz_id: Optional[str] = None,
) -> Tuple[List[Question], Dict[str, AnswerKeyEntry], dict]:
    """
    Load questions from a .md or .json quiz file.
    Returns (questions, answer_key, metadata).
    """
    path = Path(quiz_path)
    if not path.exists():
        raise FileNotFoundError(f"Quiz file not found: {quiz_path}")

    if path.suffix.lower() == ".json":
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
        questions, answer_key, meta = parse_json_quiz(data, quiz_id=quiz_id)
    else:
        content = path.read_text(encoding="utf-8")
        parser = QuizParser()
        questions, answer_key_list = parser.parse(content)
        answer_key = {e.id: e for e in answer_key_list}
        meta = {"title": path.stem}

    if not questions:
        raise ValueError(f"No questions found in {quiz_path}")

    return questions, answer_key, meta


def _apply_filters(
    questions: List[Question],
    answer_key: Dict[str, AnswerKeyEntry],
    sections: Optional[Set[str]] = None,
    limit: Optional[int] = None,
    shuffle: bool = False,
) -> Tuple[List[Question], Dict[str, AnswerKeyEntry]]:
    """Apply section filter and limit, printing what was filtered."""
    original_count = len(questions)
    questions, answer_key = filter_questions(
        questions, answer_key, sections=sections, limit=limit, shuffle=shuffle
    )
    if sections or limit:
        parts = []
        if sections:
            parts.append(f"sections={','.join(sorted(sections))}")
        if limit:
            parts.append(f"limit={limit}")
        print(f"  Filtered: {original_count} -> {len(questions)} ({', '.join(parts)})")
    return questions, answer_key


# ---------------------------------------------------------------------------
# Main runners
# ---------------------------------------------------------------------------

def run_quiz(
    quiz_path: str,
    output_path: str,
    processor=None,
    mode: str = "quick",
    use_rag: bool = True,
    n_results: int = 4,
    grounded: bool = True,
    sections: Optional[Set[str]] = None,
    limit: Optional[int] = None,
) -> str:
    """Run a full quiz from a markdown file: parse, query LLM, grade, write results."""
    questions, answer_key, meta = _load_questions(quiz_path)
    print(f"Parsed {len(questions)} questions, {len(answer_key)} answer key entries")

    questions, answer_key = _apply_filters(questions, answer_key, sections, limit)

    graded = _run_questions(
        questions, answer_key, processor, mode, use_rag, n_results, grounded
    )

    result_path = write_results(
        graded,
        output_path,
        {
            "mode": mode,
            "use_rag": use_rag,
            "grounded": grounded,
            "sections": ",".join(sorted(sections)) if sections else None,
            "limit": limit,
        },
    )
    return result_path


def run_json_quiz(
    quiz_path: str,
    output_path: str,
    quiz_id: Optional[str] = None,
    processor=None,
    mode: str = "quick",
    use_rag: bool = True,
    n_results: int = 4,
    grounded: bool = True,
    sections: Optional[Set[str]] = None,
    limit: Optional[int] = None,
) -> str:
    """Run a full quiz from a JSON file: parse, query LLM, grade, write results."""
    questions, answer_key, quiz_meta = _load_questions(quiz_path, quiz_id=quiz_id)

    title = quiz_meta.get("title", Path(quiz_path).stem)
    print(f"Quiz: {title}")
    print(f"Parsed {len(questions)} questions, {len(answer_key)} answer key entries")

    questions, answer_key = _apply_filters(questions, answer_key, sections, limit)

    graded = _run_questions(
        questions, answer_key, processor, mode, use_rag, n_results, grounded
    )

    result_path = write_results(
        graded,
        output_path,
        {
            "mode": mode,
            "use_rag": use_rag,
            "grounded": grounded,
            "title": title,
            "quiz_id": quiz_meta.get("quiz_id", ""),
            "sections": ",".join(sorted(sections)) if sections else None,
            "limit": limit,
        },
    )
    return result_path


def _run_questions(
    questions: List[Question],
    answer_key: Dict[str, AnswerKeyEntry],
    processor,
    mode: str,
    use_rag: bool,
    n_results: int,
    grounded: bool,
) -> List[GradedQuestion]:
    """Shared logic: send each question to Ollama, grade, return results."""
    import ollama as _ollama
    from backend.config import CHAT_MODELS, QUIZ_OPTIONS, QUIZ_NUM_PREDICT

    llm_model = CHAT_MODELS.get(mode, CHAT_MODELS["quick"])
    base_options = QUIZ_OPTIONS.get(mode, QUIZ_OPTIONS["quick"])
    graded: List[GradedQuestion] = []

    for i, q in enumerate(questions):
        print(f"  [{i + 1}/{len(questions)}] {q.id}...", end=" ", flush=True)

        # Build RAG context
        rag_context = None
        if use_rag and processor is not None:
            try:
                results = processor.query(q.text, n_results=n_results)
                if results["documents"][0]:
                    rag_context = "\n".join(results["documents"][0][:n_results])
            except Exception as e:
                logger.warning(f"RAG query failed for {q.id}: {e}")

        prompt = build_quiz_prompt(q, rag_context=rag_context)

        # Per-question-type token limit
        options = {
            **base_options,
            "num_predict": QUIZ_NUM_PREDICT.get(q.qtype, 512),
        }

        try:
            response = _ollama.chat(
                model=llm_model,
                messages=[{"role": "user", "content": prompt}],
                options=options,
            )
            llm_answer = response["message"]["content"]
        except Exception as e:
            llm_answer = f"[error: {e}]"

        result = grade_question(q, llm_answer, answer_key)
        graded.append(result)

        icon = "?" if result.is_correct is None else ("+" if result.is_correct else "x")
        print(f"[{icon}]")

    # Print summary
    total, correct, incorrect, ungraded, accuracy = _score_summary(graded)
    print(f"\n  Score: {correct}/{total - ungraded} "
          f"({accuracy * 100:.0f}%)"
          f"  |  {ungraded} SA ungraded")

    return graded


# ---------------------------------------------------------------------------
# Benchmark
# ---------------------------------------------------------------------------

@dataclass
class BenchmarkConfig:
    """A single configuration to test in a benchmark run."""
    mode: str
    use_rag: bool
    grounded: bool

    @property
    def label(self) -> str:
        parts = [self.mode]
        parts.append("rag" if self.use_rag else "no-rag")
        parts.append("grounded" if self.grounded else "broad")
        return " / ".join(parts)


# Default benchmark matrix — tests all meaningful combos
DEFAULT_BENCHMARK_CONFIGS = [
    BenchmarkConfig("quick",   use_rag=True,  grounded=True),
    BenchmarkConfig("quick",   use_rag=True,  grounded=False),
    BenchmarkConfig("quick",   use_rag=False, grounded=False),
    BenchmarkConfig("fast",    use_rag=True,  grounded=True),
    BenchmarkConfig("fast",    use_rag=True,  grounded=False),
    BenchmarkConfig("fast",    use_rag=False, grounded=False),
    BenchmarkConfig("deep",    use_rag=True,  grounded=True),
    BenchmarkConfig("deep",    use_rag=True,  grounded=False),
    BenchmarkConfig("deep",    use_rag=False, grounded=False),
    BenchmarkConfig("general", use_rag=True,  grounded=True),
    BenchmarkConfig("general", use_rag=True,  grounded=False),
    BenchmarkConfig("general", use_rag=False, grounded=False),
]


def run_benchmark(
    quiz_path: str,
    output_path: str,
    processor=None,
    quiz_id: Optional[str] = None,
    configs: Optional[List[BenchmarkConfig]] = None,
    n_results: int = 4,
    sections: Optional[Set[str]] = None,
    limit: Optional[int] = None,
) -> str:
    """
    Run the same quiz across multiple configurations and write a comparison report.

    Each config is a (mode, use_rag, grounded) tuple. The same question set
    is used for all runs to ensure a fair comparison.
    """
    if configs is None:
        configs = DEFAULT_BENCHMARK_CONFIGS

    # Load and filter questions once — all runs use the same set
    questions, answer_key, meta = _load_questions(quiz_path, quiz_id=quiz_id)
    title = meta.get("title", Path(quiz_path).stem)

    print(f"\n{'=' * 60}")
    print(f"  Cosmo Benchmark")
    print(f"{'=' * 60}")
    print(f"  Quiz: {title}")
    print(f"  Total questions: {len(questions)}")

    questions, answer_key = _apply_filters(
        questions, answer_key, sections, limit
    )

    print(f"  Configurations: {len(configs)}")
    print(f"  Estimated inferences: {len(configs) * len(questions)}")
    print(f"{'=' * 60}\n")

    results: List[BenchmarkResult] = []

    for ci, cfg in enumerate(configs):
        print(f"\n--- Run {ci + 1}/{len(configs)}: {cfg.label} ---")

        run_processor = processor if cfg.use_rag else None

        t0 = time.time()
        graded = _run_questions(
            questions, answer_key, run_processor,
            cfg.mode, cfg.use_rag, n_results, cfg.grounded,
        )
        elapsed = time.time() - t0

        total, correct, incorrect, ungraded, accuracy = _score_summary(graded)

        results.append(BenchmarkResult(
            label=cfg.label,
            mode=cfg.mode,
            use_rag=cfg.use_rag,
            grounded=cfg.grounded,
            total=total,
            correct=correct,
            incorrect=incorrect,
            ungraded=ungraded,
            accuracy=accuracy,
            elapsed=elapsed,
            graded=graded,
        ))

    # Write comparison report
    report_path = _write_benchmark_report(results, output_path, title, meta)

    # Print summary table
    _print_benchmark_table(results)

    return report_path


def _print_benchmark_table(results: List[BenchmarkResult]) -> None:
    """Print a formatted comparison table to stdout."""
    print(f"\n{'=' * 80}")
    print(f"  BENCHMARK RESULTS")
    print(f"{'=' * 80}")
    print(f"  {'Config':<35s} {'Acc':>6s} {'Correct':>8s} {'Time':>8s} {'Per-Q':>7s}")
    print(f"  {'-' * 35} {'-' * 6} {'-' * 8} {'-' * 8} {'-' * 7}")

    ranked = sorted(results, key=lambda r: r.accuracy, reverse=True)

    for r in ranked:
        gradable = r.total - r.ungraded
        per_q = r.elapsed / r.total if r.total > 0 else 0
        print(
            f"  {r.label:<35s} "
            f"{r.accuracy * 100:5.1f}% "
            f"{r.correct:>3d}/{gradable:<3d} "
            f"{r.elapsed:>6.1f}s "
            f"{per_q:>5.1f}s"
        )

    print(f"{'=' * 80}\n")


def _write_benchmark_report(
    results: List[BenchmarkResult],
    output_path: str,
    title: str,
    meta: dict,
) -> str:
    """Write a detailed benchmark comparison report."""
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    ranked = sorted(results, key=lambda r: r.accuracy, reverse=True)

    with open(path, "w", encoding="utf-8") as f:
        f.write("# Benchmark Report\n\n")
        f.write(f"**Quiz:** {title}\n\n")

        # Summary table
        f.write("## Summary\n\n")
        f.write("| Rank | Config | Accuracy | Correct | Time | Per-Q |\n")
        f.write("|------|--------|----------|---------|------|-------|\n")

        for rank, r in enumerate(ranked, 1):
            gradable = r.total - r.ungraded
            per_q = r.elapsed / r.total if r.total > 0 else 0
            f.write(
                f"| {rank} | {r.label} | "
                f"{r.accuracy * 100:.1f}% | "
                f"{r.correct}/{gradable} | "
                f"{r.elapsed:.1f}s | "
                f"{per_q:.1f}s |\n"
            )

        f.write("\n---\n\n")

        # Per-question comparison
        f.write("## Per-Question Breakdown\n\n")

        all_qids = [q.question.id for q in results[0].graded]

        f.write("| Question |")
        for r in ranked:
            f.write(f" {r.label} |")
        f.write("\n")
        f.write("|----------|")
        for _ in ranked:
            f.write("------|")
        f.write("\n")

        for qid in all_qids:
            f.write(f"| {qid} |")
            for r in ranked:
                g = next((g for g in r.graded if g.question.id == qid), None)
                if g is None:
                    f.write(" - |")
                elif g.is_correct is None:
                    f.write(" ? |")
                elif g.is_correct:
                    f.write(" + |")
                else:
                    f.write(f" x ({g.llm_extracted}) |")
            f.write("\n")

        f.write("\n---\n\n")

        # Disagreements
        f.write("## Disagreements\n\n")
        f.write("Questions where at least one config got it right and another wrong:\n\n")

        disagreement_count = 0
        for qid in all_qids:
            grades = {}
            for r in results:
                g = next((g for g in r.graded if g.question.id == qid), None)
                if g and g.is_correct is not None:
                    grades[r.label] = g

            if not grades:
                continue

            correct_configs = [la for la, g in grades.items() if g.is_correct]
            wrong_configs = [la for la, g in grades.items() if not g.is_correct]

            if correct_configs and wrong_configs:
                disagreement_count += 1
                sample_g = list(grades.values())[0]
                f.write(f"### {qid}\n\n")
                f.write(f"**Question:** {sample_g.question.text[:200]}\n\n")
                f.write(f"**Correct answer:** {sample_g.correct_answer}\n\n")
                f.write(f"**Got it right:** {', '.join(correct_configs)}\n\n")
                f.write(f"**Got it wrong:** {', '.join(wrong_configs)}\n")
                for wlabel in wrong_configs:
                    g = grades[wlabel]
                    f.write(f"  - {wlabel}: answered {g.llm_extracted}\n")
                f.write("\n")

        if disagreement_count == 0:
            f.write("No disagreements -- all configs agreed on every question.\n\n")

    return str(path)


# ---------------------------------------------------------------------------
# Multi-quiz benchmark
# ---------------------------------------------------------------------------

@dataclass
class QuizBenchmarkSummary:
    """Results from benchmarking a single quiz across all configs."""
    quiz_title: str
    quiz_path: str
    results: List[BenchmarkResult]


def run_multi_benchmark(
    quiz_paths: List[str],
    output_path: str,
    processor=None,
    configs: Optional[List[BenchmarkConfig]] = None,
    n_results: int = 4,
    sections: Optional[Set[str]] = None,
    limit: Optional[int] = None,
) -> str:
    """
    Run benchmarks across multiple quiz files and produce a combined report.

    Each quiz is benchmarked independently with per-quiz scores,
    then an aggregate summary ranks configs across all quizzes.
    """
    if configs is None:
        configs = DEFAULT_BENCHMARK_CONFIGS

    total_quizzes = len(quiz_paths)
    print(f"\n{'=' * 60}")
    print(f"  Cosmo Multi-Quiz Benchmark")
    print(f"{'=' * 60}")
    print(f"  Quiz files: {total_quizzes}")
    print(f"  Configurations: {len(configs)}")
    print(f"{'=' * 60}\n")

    all_summaries: List[QuizBenchmarkSummary] = []

    for qi, qpath in enumerate(quiz_paths):
        path = Path(qpath)
        print(f"\n{'#' * 60}")
        print(f"  Quiz {qi + 1}/{total_quizzes}: {path.name}")
        print(f"{'#' * 60}")

        try:
            questions, answer_key, meta = _load_questions(qpath)
        except (FileNotFoundError, ValueError) as e:
            print(f"  Skipping: {e}")
            continue

        title = meta.get("title", path.stem)
        print(f"  Title: {title}")
        print(f"  Questions: {len(questions)}")

        questions, answer_key = _apply_filters(
            questions, answer_key, sections, limit
        )

        if not questions:
            print(f"  Skipping: no questions after filtering")
            continue

        quiz_results: List[BenchmarkResult] = []

        for ci, cfg in enumerate(configs):
            print(f"\n  --- Run {ci + 1}/{len(configs)}: {cfg.label} ---")

            run_processor = processor if cfg.use_rag else None

            t0 = time.time()
            graded = _run_questions(
                questions, answer_key, run_processor,
                cfg.mode, cfg.use_rag, n_results, cfg.grounded,
            )
            elapsed = time.time() - t0

            total, correct, incorrect, ungraded, accuracy = _score_summary(graded)

            quiz_results.append(BenchmarkResult(
                label=cfg.label,
                mode=cfg.mode,
                use_rag=cfg.use_rag,
                grounded=cfg.grounded,
                total=total,
                correct=correct,
                incorrect=incorrect,
                ungraded=ungraded,
                accuracy=accuracy,
                elapsed=elapsed,
                graded=graded,
            ))

        _print_benchmark_table(quiz_results)
        all_summaries.append(QuizBenchmarkSummary(
            quiz_title=title,
            quiz_path=qpath,
            results=quiz_results,
        ))

    if not all_summaries:
        print("No quizzes were successfully benchmarked.")
        return output_path

    # Write combined report
    report_path = _write_multi_benchmark_report(all_summaries, output_path)

    # Print aggregate table
    _print_aggregate_table(all_summaries)

    return report_path


def _aggregate_by_config(
    summaries: List[QuizBenchmarkSummary],
) -> Dict[str, Dict]:
    """Aggregate results across quizzes, keyed by config label."""
    agg: Dict[str, Dict] = {}

    for summary in summaries:
        for r in summary.results:
            if r.label not in agg:
                agg[r.label] = {
                    "total": 0,
                    "correct": 0,
                    "incorrect": 0,
                    "ungraded": 0,
                    "elapsed": 0.0,
                    "quiz_accuracies": [],
                }
            a = agg[r.label]
            a["total"] += r.total
            a["correct"] += r.correct
            a["incorrect"] += r.incorrect
            a["ungraded"] += r.ungraded
            a["elapsed"] += r.elapsed
            a["quiz_accuracies"].append((summary.quiz_title, r.accuracy))

    for label, a in agg.items():
        gradable = a["total"] - a["ungraded"]
        a["accuracy"] = a["correct"] / gradable if gradable > 0 else 0.0

    return agg


def _print_aggregate_table(summaries: List[QuizBenchmarkSummary]) -> None:
    """Print aggregate results across all quizzes."""
    if not summaries:
        return

    agg = _aggregate_by_config(summaries)
    ranked = sorted(agg.items(), key=lambda kv: kv[1]["accuracy"], reverse=True)

    quiz_titles = [s.quiz_title for s in summaries]

    print(f"\n{'=' * 80}")
    print(f"  AGGREGATE RESULTS ({len(summaries)} quizzes)")
    print(f"{'=' * 80}")
    print(f"  {'Config':<35s} {'Overall':>8s}", end="")
    for title in quiz_titles:
        short = title[:12]
        print(f" {short:>12s}", end="")
    print(f" {'Time':>8s}")
    print(f"  {'-' * 35} {'-' * 8}", end="")
    for _ in quiz_titles:
        print(f" {'-' * 12}", end="")
    print(f" {'-' * 8}")

    for label, a in ranked:
        print(
            f"  {label:<35s} "
            f"{a['accuracy'] * 100:5.1f}%  ",
            end="",
        )
        for _, acc in a["quiz_accuracies"]:
            print(f" {acc * 100:10.1f}%", end="")
        print(f" {a['elapsed']:>7.0f}s")

    print(f"{'=' * 80}\n")


def _write_multi_benchmark_report(
    summaries: List[QuizBenchmarkSummary],
    output_path: str,
) -> str:
    """Write a combined benchmark report with per-quiz and aggregate sections."""
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    agg = _aggregate_by_config(summaries)
    ranked_labels = sorted(agg.items(), key=lambda kv: kv[1]["accuracy"], reverse=True)

    with open(path, "w", encoding="utf-8") as f:
        f.write("# Multi-Quiz Benchmark Report\n\n")
        f.write(f"**Quizzes:** {len(summaries)}\n\n")
        for s in summaries:
            f.write(f"- {s.quiz_title}\n")
        f.write("\n---\n\n")

        # Aggregate summary
        f.write("## Aggregate Summary\n\n")
        f.write("| Rank | Config | Overall |")
        for s in summaries:
            f.write(f" {s.quiz_title[:25]} |")
        f.write(" Total Time |\n")
        f.write("|------|--------|---------|")
        for _ in summaries:
            f.write("------|")
        f.write("------|\n")

        for rank, (label, a) in enumerate(ranked_labels, 1):
            f.write(f"| {rank} | {label} | {a['accuracy'] * 100:.1f}% |")
            for _, acc in a["quiz_accuracies"]:
                f.write(f" {acc * 100:.1f}% |")
            f.write(f" {a['elapsed']:.0f}s |\n")

        f.write("\n---\n\n")

        # Per-quiz detail sections
        for si, summary in enumerate(summaries):
            f.write(f"## Quiz {si + 1}: {summary.quiz_title}\n\n")

            ranked_results = sorted(
                summary.results, key=lambda r: r.accuracy, reverse=True
            )

            f.write("| Rank | Config | Accuracy | Correct | Time | Per-Q |\n")
            f.write("|------|--------|----------|---------|------|-------|\n")

            for rank, r in enumerate(ranked_results, 1):
                gradable = r.total - r.ungraded
                per_q = r.elapsed / r.total if r.total > 0 else 0
                f.write(
                    f"| {rank} | {r.label} | "
                    f"{r.accuracy * 100:.1f}% | "
                    f"{r.correct}/{gradable} | "
                    f"{r.elapsed:.1f}s | "
                    f"{per_q:.1f}s |\n"
                )

            f.write("\n")

            # Per-question breakdown
            if summary.results and summary.results[0].graded:
                all_qids = [g.question.id for g in summary.results[0].graded]

                f.write("| Question |")
                for r in ranked_results:
                    f.write(f" {r.label} |")
                f.write("\n|----------|")
                for _ in ranked_results:
                    f.write("------|")
                f.write("\n")

                for qid in all_qids:
                    f.write(f"| {qid} |")
                    for r in ranked_results:
                        g = next(
                            (g for g in r.graded if g.question.id == qid), None
                        )
                        if g is None:
                            f.write(" - |")
                        elif g.is_correct is None:
                            f.write(" ? |")
                        elif g.is_correct:
                            f.write(" + |")
                        else:
                            f.write(f" x ({g.llm_extracted}) |")
                    f.write("\n")

            f.write("\n---\n\n")

    return str(path)