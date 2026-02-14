"""
Quiz Processor — parse quiz markdown, send to Ollama, grade results.

Handles:
- Parsing quiz markdown files into question sections and answer keys
- Sending questions to Ollama (with optional RAG context)
- Grading LLM responses against the answer key
- Writing structured results to output files
"""

import logging
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Tuple

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


# ---------------------------------------------------------------------------
# Quiz parser
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
# Answer extraction
# ---------------------------------------------------------------------------

def extract_answer(llm_response: str, qtype: str) -> str:
    """Extract a normalized answer from an LLM response."""
    cleaned = llm_response.strip()

    if qtype == "tf":
        lower = cleaned.lower()
        if lower.startswith("true") or lower.startswith("t"):
            return "T"
        if lower.startswith("false") or lower.startswith("f"):
            return "F"
        return cleaned[:1].upper() if cleaned else "?"

    if qtype == "mc":
        m = re.search(r"\(([a-d])\)", cleaned)
        if m:
            return m.group(1)
        for char in cleaned:
            if char.lower() in "abcd":
                return char.lower()
        return cleaned[:1] if cleaned else "?"

    return cleaned


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


# ---------------------------------------------------------------------------
# Results writer
# ---------------------------------------------------------------------------

def write_results(graded: List[GradedQuestion], output_path: str, metadata: Dict) -> str:
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    total = len(graded)
    correct = sum(1 for g in graded if g.is_correct is True)
    incorrect = sum(1 for g in graded if g.is_correct is False)
    ungraded = sum(1 for g in graded if g.is_correct is None)
    score_sum = sum(g.score for g in graded)

    with open(path, "w", encoding="utf-8") as f:
        f.write(f"# Quiz Results\n\n")
        f.write(f"- **Mode:** {metadata.get('mode', '?')}\n")
        f.write(f"- **RAG:** {'yes' if metadata.get('use_rag') else 'no'}\n")
        f.write(f"- **Total:** {total}\n")
        f.write(f"- **Correct:** {correct}\n")
        f.write(f"- **Incorrect:** {incorrect}\n")
        f.write(f"- **Ungraded (SA):** {ungraded}\n")
        f.write(f"- **Score:** {score_sum:.0f}\n\n---\n\n")

        for g in graded:
            icon = "?" if g.is_correct is None else ("+" if g.is_correct else "x")
            f.write(f"## [{icon}] {g.question.id}\n\n")
            f.write(f"**Question:** {g.question.text[:200]}...\n\n")
            f.write(f"**LLM answer:** {g.llm_extracted}\n\n")
            f.write(f"**Correct:** {g.correct_answer}\n\n")
            if g.correct_explanation:
                f.write(f"**Explanation:** {g.correct_explanation}\n\n")
            f.write("---\n\n")

    return str(path)


# ---------------------------------------------------------------------------
# Main runner
# ---------------------------------------------------------------------------

def run_quiz(
    quiz_path: str,
    output_path: str,
    processor=None,
    mode: str = "quick",
    use_rag: bool = True,
    n_results: int = 4,
) -> str:
    """Run a full quiz: parse, query LLM, grade, write results."""
    path = Path(quiz_path)
    if not path.exists():
        raise FileNotFoundError(f"Quiz file not found: {quiz_path}")

    content = path.read_text(encoding="utf-8")
    parser = QuizParser()
    questions, answer_key_list = parser.parse(content)

    if not questions:
        raise ValueError(f"No questions found in {quiz_path}")

    answer_key = {e.id: e for e in answer_key_list}
    print(f"Parsed {len(questions)} questions, {len(answer_key)} answer key entries")

    import ollama as _ollama
    from backend.config import CHAT_MODELS

    llm_model = CHAT_MODELS.get(mode, CHAT_MODELS["quick"])
    graded: List[GradedQuestion] = []

    for i, q in enumerate(questions):
        print(f"  [{i + 1}/{len(questions)}] {q.id}...", end=" ", flush=True)

        prompt_parts = [f"Answer this {q.qtype.upper()} question concisely.\n\n{q.text}"]
        if q.choices:
            prompt_parts.append("\n".join(q.choices))

        if use_rag and processor is not None:
            try:
                results = processor.query(q.text, n_results=n_results)
                if results["documents"][0]:
                    context = "\n".join(results["documents"][0][:2])
                    prompt_parts.insert(0, f"Context:\n{context}\n")
            except Exception as e:
                logger.warning(f"RAG query failed for {q.id}: {e}")

        prompt = "\n\n".join(prompt_parts)

        try:
            response = _ollama.chat(
                model=llm_model,
                messages=[{"role": "user", "content": prompt}],
                options={"num_ctx": 4096, "num_thread": 8},
            )
            llm_answer = response["message"]["content"]
        except Exception as e:
            llm_answer = f"[error: {e}]"

        result = grade_question(q, llm_answer, answer_key)
        graded.append(result)

        icon = "?" if result.is_correct is None else ("+" if result.is_correct else "x")
        print(f"[{icon}]")

    result_path = write_results(
        graded,
        output_path,
        {"mode": mode, "use_rag": use_rag},
    )
    return result_path
