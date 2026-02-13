"""
Quiz Processor for React/TypeScript Study Companion

Handles:
- Parsing quiz markdown files into question sections and answer keys
- Sending questions to Ollama (with optional RAG context)
- Grading LLM responses against the answer key
- Writing structured results to output files
"""

import re
import logging
from pathlib import Path
from typing import Optional, Dict, List, Tuple
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------

@dataclass
class Question:
    """A single quiz question with its identifier, type, and text."""
    id: str              # e.g. "TF-1", "SA-3", "MC-7"
    qtype: str           # "tf", "sa", or "mc"
    text: str            # Full question text including code blocks
    choices: List[str] = field(default_factory=list)  # MC choices if applicable


@dataclass
class AnswerKeyEntry:
    """A single entry from the answer key."""
    id: str
    answer: str          # "T", "F", "(b)", or free-text for SA
    explanation: str = ""


@dataclass
class GradedQuestion:
    """A question with the LLM's response and grading result."""
    question: Question
    llm_answer: str
    llm_extracted: str        # Normalized extracted answer (T/F, letter, etc.)
    correct_answer: str
    correct_explanation: str
    is_correct: Optional[bool]  # None if not auto-gradeable (SA)
    score: float               # +1, -1, or 0


# ---------------------------------------------------------------------------
# Quiz parser
# ---------------------------------------------------------------------------

class QuizParser:
    """Parse a quiz markdown file into questions and answer key."""

    # Matches question IDs like TF-1, SA-12, MC-3
    _QUESTION_ID_RE = re.compile(
        r'^\*\*(?P<id>(?:TF|SA|MC)-\d+)\.\*\*\s*',
        re.MULTILINE
    )

    # Matches MC choices like (a) ..., (b) ...
    _CHOICE_RE = re.compile(r'^\(([a-d])\)\s+(.+)$', re.MULTILINE)

    # Matches answer key table rows: | TF-1 | **T** | explanation |
    _TABLE_ROW_RE = re.compile(
        r'^\|\s*(?P<id>(?:TF|SA|MC)-\d+)\s*\|\s*'
        r'\*?\*?\(?(?P<answer>[TFabcd])\)?\*?\*?\s*\|\s*'
        r'(?P<explanation>.*?)\s*\|$',
        re.MULTILINE
    )

    def parse(self, content: str) -> Tuple[List[Question], List[AnswerKeyEntry]]:
        """
        Parse quiz markdown into questions and answer key.

        Args:
            content: Full markdown text of the quiz file

        Returns:
            Tuple of (questions list, answer key entries list)
        """
        questions = self._parse_questions(content)
        answer_key = self._parse_answer_key(content)
        return questions, answer_key

    def _parse_questions(self, content: str) -> List[Question]:
        """Extract all questions from the quiz body."""
        # Split at the answer key so we only parse questions
        parts = re.split(r'^##\s+Answer\s+Key', content, flags=re.MULTILINE)
        question_section = parts[0]

        questions: List[Question] = []
        matches = list(self._QUESTION_ID_RE.finditer(question_section))

        for i, match in enumerate(matches):
            qid = match.group('id')
            start = match.end()
            end = matches[i + 1].start() if i + 1 < len(matches) else len(question_section)

            # Get the raw text between this question ID and the next
            raw_text = question_section[start:end].strip()
            # Remove trailing --- separators
            raw_text = re.sub(r'\n---\s*$', '', raw_text).strip()

            qtype = self._id_to_type(qid)
            choices: List[str] = []

            if qtype == 'mc':
                choices = self._CHOICE_RE.findall(raw_text)
                # choices is list of (letter, text) tuples
                choices = [f"({letter}) {text}" for letter, text in choices]

            questions.append(Question(
                id=qid,
                qtype=qtype,
                text=raw_text,
                choices=choices
            ))

        return questions

    def _parse_answer_key(self, content: str) -> List[AnswerKeyEntry]:
        """Extract answer key entries from the file."""
        # Find the answer key section
        key_match = re.search(r'^##\s+Answer\s+Key', content, flags=re.MULTILINE)
        if not key_match:
            return []

        key_section = content[key_match.start():]
        entries: List[AnswerKeyEntry] = []

        # Parse table rows for T/F and MC
        for m in self._TABLE_ROW_RE.finditer(key_section):
            entries.append(AnswerKeyEntry(
                id=m.group('id'),
                answer=m.group('answer').strip(),
                explanation=m.group('explanation').strip()
            ))

        # Parse SA answers (formatted as **SA-N.** followed by text)
        sa_blocks = re.finditer(
            r'\*\*(?P<id>SA-\d+)\.\*\*\s*\n(?P<body>.*?)(?=\n\*\*SA-\d+\.\*\*|\n---\s*\n###|\Z)',
            key_section,
            re.DOTALL
        )
        for m in sa_blocks:
            body = m.group('body').strip()
            # Remove trailing --- separators
            body = re.sub(r'\n---\s*$', '', body).strip()
            entries.append(AnswerKeyEntry(
                id=m.group('id'),
                answer=body,
                explanation=""
            ))

        return entries

    @staticmethod
    def _id_to_type(qid: str) -> str:
        prefix = qid.split('-')[0].upper()
        return {'TF': 'tf', 'SA': 'sa', 'MC': 'mc'}.get(prefix, 'unknown')


# ---------------------------------------------------------------------------
# Quiz taker — sends questions to the LLM
# ---------------------------------------------------------------------------

class QuizTaker:
    """Send quiz questions to an LLM and collect answers."""

    def __init__(self, processor=None):
        """
        Args:
            processor: A DocumentProcessor instance (for RAG context).
                       If None, operates in standalone (no-RAG) mode.
        """
        self.processor = processor

    def take_quiz(
        self,
        questions: List[Question],
        mode: str = 'quick',
        use_rag: bool = True,
        n_results: int = 4
    ) -> Dict[str, str]:
        """
        Answer all questions using the LLM.

        Groups questions by type and sends them in batches to reduce
        API calls. T/F and MC are batched together; SA questions are
        sent individually for better quality.

        Args:
            questions: List of parsed Question objects
            mode: Model mode ('quick', 'deep', 'general', 'fast')
            use_rag: Whether to include RAG context from indexed docs
            n_results: Number of RAG context chunks per query

        Returns:
            Dict mapping question ID to the LLM's raw answer string
        """
        import ollama as _ollama

        if self.processor is None:
            use_rag = False

        model = self._get_model(mode)
        answers: Dict[str, str] = {}

        # Group questions by type
        tf_questions = [q for q in questions if q.qtype == 'tf']
        mc_questions = [q for q in questions if q.qtype == 'mc']
        sa_questions = [q for q in questions if q.qtype == 'sa']

        # Batch T/F questions
        if tf_questions:
            print(f"  Answering {len(tf_questions)} True/False questions...")
            batch_answers = self._answer_tf_batch(tf_questions, model, use_rag, n_results)
            answers.update(batch_answers)

        # Batch MC questions
        if mc_questions:
            print(f"  Answering {len(mc_questions)} Multiple Choice questions...")
            batch_answers = self._answer_mc_batch(mc_questions, model, use_rag, n_results)
            answers.update(batch_answers)

        # SA questions individually
        if sa_questions:
            print(f"  Answering {len(sa_questions)} Short Answer questions...")
            for i, q in enumerate(sa_questions):
                print(f"    SA {i + 1}/{len(sa_questions)}: {q.id}")
                answer = self._answer_sa_single(q, model, use_rag, n_results)
                answers[q.id] = answer

        return answers

    def _answer_tf_batch(
        self, questions: List[Question], model: str,
        use_rag: bool, n_results: int
    ) -> Dict[str, str]:
        """Answer T/F questions in a batch."""
        import ollama as _ollama

        # Build the question block
        q_block = "\n\n".join(
            f"{q.id}. {q.text}" for q in questions
        )

        rag_context = ""
        if use_rag and self.processor:
            # Use a summary query to get broad context
            topics = " ".join(q.text[:80] for q in questions[:5])
            rag_context = self._get_rag_context(topics, n_results)

        prompt = f"""You are taking a TypeScript/React quiz. Answer each True/False question.

IMPORTANT: For each question, respond with EXACTLY this format:
<question_id>: <T or F> — <brief explanation>

Example:
TF-1: T — TypeScript is indeed a superset of JavaScript.
TF-2: F — Types are erased at compile time, not enforced at runtime.

Do not skip any questions. Do not add extra commentary.
{rag_context}
Questions:
{q_block}

Your answers:"""

        response = _ollama.chat(
            model=model,
            messages=[{'role': 'user', 'content': prompt}],
            options={'num_ctx': 8192, 'num_thread': 8}
        )

        return self._parse_batch_response(response['message']['content'], questions)

    def _answer_mc_batch(
        self, questions: List[Question], model: str,
        use_rag: bool, n_results: int
    ) -> Dict[str, str]:
        """Answer MC questions in a batch."""
        import ollama as _ollama

        q_block = "\n\n".join(
            f"{q.id}. {q.text}" for q in questions
        )

        rag_context = ""
        if use_rag and self.processor:
            topics = " ".join(q.text[:80] for q in questions[:5])
            rag_context = self._get_rag_context(topics, n_results)

        prompt = f"""You are taking a TypeScript/React quiz. Answer each Multiple Choice question.

IMPORTANT: For each question, respond with EXACTLY this format:
<question_id>: (<letter>) — <brief explanation>

Example:
MC-1: (b) — number[] is the inferred type for a let array literal.
MC-2: (a) — "five" is a string, not assignable to number.

Do not skip any questions. Do not add extra commentary.
{rag_context}
Questions:
{q_block}

Your answers:"""

        response = _ollama.chat(
            model=model,
            messages=[{'role': 'user', 'content': prompt}],
            options={'num_ctx': 8192, 'num_thread': 8}
        )

        return self._parse_batch_response(response['message']['content'], questions)

    def _answer_sa_single(
        self, question: Question, model: str,
        use_rag: bool, n_results: int
    ) -> str:
        """Answer a single SA question."""
        import ollama as _ollama

        rag_context = ""
        if use_rag and self.processor:
            rag_context = self._get_rag_context(question.text, n_results)

        prompt = f"""You are taking a TypeScript/React quiz. Answer this short answer question.

Be concise — 1-4 sentences or a short code snippet as appropriate. Write valid TypeScript if code is requested.
{rag_context}
Question ({question.id}):
{question.text}

Your answer:"""

        response = _ollama.chat(
            model=model,
            messages=[{'role': 'user', 'content': prompt}],
            options={'num_ctx': 8192, 'num_thread': 8}
        )

        return response['message']['content'].strip()

    def _get_rag_context(self, query: str, n_results: int) -> str:
        """Retrieve RAG context from indexed documents."""
        if not self.processor:
            return ""

        try:
            results = self.processor.query(query, n_results=n_results)
            if not results['documents'][0]:
                return ""

            parts = []
            for i, (doc, meta) in enumerate(zip(
                results['documents'][0], results['metadatas'][0]
            )):
                source = meta.get('source', 'unknown')
                parts.append(f"[Reference {i+1} from {source}]:\n{doc}")

            return "\n\nRelevant documentation:\n" + "\n\n".join(parts) + "\n"
        except Exception as e:
            logger.warning(f"RAG context retrieval failed: {e}")
            return ""

    def _parse_batch_response(
        self, response: str, questions: List[Question]
    ) -> Dict[str, str]:
        """Parse a batch LLM response into per-question answers."""
        answers: Dict[str, str] = {}

        for q in questions:
            # Try to find "TF-1:" or "MC-1:" in the response
            pattern = re.compile(
                rf'{re.escape(q.id)}\s*[:\.]\s*(.+?)(?=\n(?:TF|MC|SA)-\d+\s*[:\.]|\Z)',
                re.DOTALL
            )
            match = pattern.search(response)
            if match:
                answers[q.id] = match.group(1).strip()
            else:
                answers[q.id] = "[No answer parsed]"

        return answers

    def _get_model(self, mode: str) -> str:
        models = {
            'quick': 'qwen2.5-coder:7b',
            'deep': 'qwen2.5-coder:14b',
            'general': 'llama3.1:8b',
            'fast': 'mistral:7b'
        }
        return models.get(mode, models['quick'])


# ---------------------------------------------------------------------------
# Grader — compares LLM answers to the answer key
# ---------------------------------------------------------------------------

class QuizGrader:
    """Grade LLM answers against an answer key."""

    # Extract T or F from the start of an answer
    _TF_RE = re.compile(r'^(T(?:rue)?|F(?:alse)?)\b', re.IGNORECASE)

    # Extract (a), (b), etc. from the start of an answer
    _MC_RE = re.compile(r'^\(?([a-d])\)?', re.IGNORECASE)

    def grade(
        self,
        questions: List[Question],
        llm_answers: Dict[str, str],
        answer_key: List[AnswerKeyEntry]
    ) -> List[GradedQuestion]:
        """
        Grade all questions.

        T/F and MC are auto-graded. SA questions are marked as
        "manual review needed" with the reference answer shown.

        Args:
            questions: Parsed questions
            llm_answers: Dict of question ID -> LLM's raw answer
            answer_key: Parsed answer key entries

        Returns:
            List of GradedQuestion results
        """
        key_map = {entry.id: entry for entry in answer_key}
        results: List[GradedQuestion] = []

        for q in questions:
            llm_raw = llm_answers.get(q.id, "[No answer]")
            key_entry = key_map.get(q.id)

            if key_entry is None:
                results.append(GradedQuestion(
                    question=q,
                    llm_answer=llm_raw,
                    llm_extracted="?",
                    correct_answer="[Not in answer key]",
                    correct_explanation="",
                    is_correct=None,
                    score=0.0
                ))
                continue

            if q.qtype == 'tf':
                graded = self._grade_tf(q, llm_raw, key_entry)
            elif q.qtype == 'mc':
                graded = self._grade_mc(q, llm_raw, key_entry)
            else:
                graded = self._grade_sa(q, llm_raw, key_entry)

            results.append(graded)

        return results

    def _grade_tf(
        self, q: Question, llm_raw: str, key: AnswerKeyEntry
    ) -> GradedQuestion:
        match = self._TF_RE.search(llm_raw)
        extracted = ""
        if match:
            extracted = "T" if match.group(1)[0].upper() == 'T' else "F"

        correct = key.answer.upper()
        is_correct = (extracted == correct) if extracted else None
        score = 1.0 if is_correct is True else (-1.0 if is_correct is False else 0.0)

        return GradedQuestion(
            question=q,
            llm_answer=llm_raw,
            llm_extracted=extracted or "?",
            correct_answer=correct,
            correct_explanation=key.explanation,
            is_correct=is_correct,
            score=score
        )

    def _grade_mc(
        self, q: Question, llm_raw: str, key: AnswerKeyEntry
    ) -> GradedQuestion:
        match = self._MC_RE.search(llm_raw)
        extracted = ""
        if match:
            extracted = match.group(1).lower()

        correct = key.answer.lower()
        is_correct = (extracted == correct) if extracted else None
        score = 1.0 if is_correct is True else (-1.0 if is_correct is False else 0.0)

        return GradedQuestion(
            question=q,
            llm_answer=llm_raw,
            llm_extracted=f"({extracted})" if extracted else "?",
            correct_answer=f"({correct})",
            correct_explanation=key.explanation,
            is_correct=is_correct,
            score=score
        )

    def _grade_sa(
        self, q: Question, llm_raw: str, key: AnswerKeyEntry
    ) -> GradedQuestion:
        return GradedQuestion(
            question=q,
            llm_answer=llm_raw,
            llm_extracted="[SA - manual review]",
            correct_answer=key.answer,
            correct_explanation=key.explanation,
            is_correct=None,  # Can't auto-grade SA
            score=0.0
        )


# ---------------------------------------------------------------------------
# Report writer — formats results to markdown
# ---------------------------------------------------------------------------

class QuizReportWriter:
    """Write graded quiz results to a markdown file."""

    def write(
        self,
        results: List[GradedQuestion],
        output_path: str,
        quiz_title: str = "Quiz Results",
        mode: str = "quick",
        use_rag: bool = True
    ) -> str:
        """
        Write a graded quiz report to a markdown file.

        Creates parent directories if they don't exist.

        Args:
            results: List of GradedQuestion objects
            output_path: Path to write the report
            quiz_title: Title for the report header
            mode: Model mode used
            use_rag: Whether RAG was used

        Returns:
            The absolute path of the written file
        """
        path = Path(output_path)
        path.parent.mkdir(parents=True, exist_ok=True)

        # Compute summary stats
        tf_results = [r for r in results if r.question.qtype == 'tf']
        mc_results = [r for r in results if r.question.qtype == 'mc']
        sa_results = [r for r in results if r.question.qtype == 'sa']

        tf_correct = sum(1 for r in tf_results if r.is_correct is True)
        tf_wrong = sum(1 for r in tf_results if r.is_correct is False)
        tf_skipped = sum(1 for r in tf_results if r.is_correct is None)

        mc_correct = sum(1 for r in mc_results if r.is_correct is True)
        mc_wrong = sum(1 for r in mc_results if r.is_correct is False)
        mc_skipped = sum(1 for r in mc_results if r.is_correct is None)

        # Penalty scoring: right - wrong
        tf_score = tf_correct - tf_wrong
        mc_score = mc_correct - mc_wrong
        total_auto = tf_score + mc_score
        max_auto = len(tf_results) + len(mc_results)

        lines: List[str] = []
        lines.append(f"# {quiz_title}\n")
        lines.append(f"**Model mode:** {mode}  ")
        lines.append(f"**RAG context:** {'Yes' if use_rag else 'No'}  ")
        lines.append("")

        # Summary table
        lines.append("## Summary\n")
        lines.append("| Section | Correct | Wrong | Skipped | Score (right - wrong) | Max |")
        lines.append("|---------|---------|-------|---------|-----------------------|-----|")
        lines.append(f"| True/False | {tf_correct} | {tf_wrong} | {tf_skipped} | {tf_score} | {len(tf_results)} |")
        lines.append(f"| Multiple Choice | {mc_correct} | {mc_wrong} | {mc_skipped} | {mc_score} | {len(mc_results)} |")
        lines.append(f"| Short Answer | — | — | — | Manual review | {len(sa_results)} |")
        lines.append(f"| **Auto-graded Total** | **{tf_correct + mc_correct}** | **{tf_wrong + mc_wrong}** | **{tf_skipped + mc_skipped}** | **{total_auto}** | **{max_auto}** |")
        lines.append("")

        if max_auto > 0:
            pct = (total_auto / max_auto) * 100
            lines.append(f"**Auto-graded score: {total_auto}/{max_auto} ({pct:.1f}%)**\n")

        # T/F detail
        if tf_results:
            lines.append("---\n")
            lines.append("## Part A: True/False — Detailed Results\n")
            lines.append("| # | LLM Answer | Correct | Result | Explanation |")
            lines.append("|---|------------|---------|--------|-------------|")
            for r in tf_results:
                icon = self._result_icon(r.is_correct)
                # Truncate explanation for table
                expl = r.correct_explanation[:120] + "..." if len(r.correct_explanation) > 120 else r.correct_explanation
                lines.append(
                    f"| {r.question.id} | {r.llm_extracted} | "
                    f"{r.correct_answer} | {icon} | {expl} |"
                )
            lines.append("")

        # MC detail
        if mc_results:
            lines.append("---\n")
            lines.append("## Part C: Multiple Choice — Detailed Results\n")
            lines.append("| # | LLM Answer | Correct | Result | Explanation |")
            lines.append("|---|------------|---------|--------|-------------|")
            for r in mc_results:
                icon = self._result_icon(r.is_correct)
                expl = r.correct_explanation[:120] + "..." if len(r.correct_explanation) > 120 else r.correct_explanation
                lines.append(
                    f"| {r.question.id} | {r.llm_extracted} | "
                    f"{r.correct_answer} | {icon} | {expl} |"
                )
            lines.append("")

        # SA detail — full text for manual review
        if sa_results:
            lines.append("---\n")
            lines.append("## Part B: Short Answer — Manual Review Required\n")
            for r in sa_results:
                lines.append(f"### {r.question.id}\n")
                lines.append(f"**Question:** {r.question.text[:200]}{'...' if len(r.question.text) > 200 else ''}\n")
                lines.append(f"**LLM Answer:**\n")
                lines.append(f"{r.llm_answer}\n")
                lines.append(f"**Reference Answer:**\n")
                lines.append(f"{r.correct_answer}\n")
                lines.append("---\n")

        # Wrong answers review section
        wrong = [r for r in results if r.is_correct is False]
        if wrong:
            lines.append("## Missed Questions — Review These\n")
            for r in wrong:
                lines.append(f"**{r.question.id}** — Answered {r.llm_extracted}, correct is {r.correct_answer}")
                if r.correct_explanation:
                    lines.append(f"  > {r.correct_explanation}")
                lines.append("")

        content = "\n".join(lines)
        path.write_text(content, encoding='utf-8')
        print(f"Results written to: {path}")
        return str(path.resolve())

    @staticmethod
    def _result_icon(is_correct: Optional[bool]) -> str:
        if is_correct is True:
            return "CORRECT"
        elif is_correct is False:
            return "WRONG"
        return "SKIP"


# ---------------------------------------------------------------------------
# High-level orchestrator
# ---------------------------------------------------------------------------

def run_quiz(
    quiz_path: str,
    output_path: str,
    processor=None,
    mode: str = 'quick',
    use_rag: bool = True,
    n_results: int = 4
) -> str:
    """
    End-to-end: parse quiz, take it, grade it, write results.

    Args:
        quiz_path: Path to the quiz markdown file
        output_path: Path to write the graded results
        processor: Optional DocumentProcessor for RAG context
        mode: Model mode
        use_rag: Whether to use RAG context
        n_results: Number of RAG context chunks

    Returns:
        Path to the output file
    """
    # Read quiz file
    quiz_file = Path(quiz_path)
    if not quiz_file.exists():
        raise FileNotFoundError(f"Quiz file not found: {quiz_path}")

    content = quiz_file.read_text(encoding='utf-8')
    quiz_title = quiz_file.stem

    # Extract a nicer title from the first H1 if present
    h1_match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
    if h1_match:
        quiz_title = h1_match.group(1).strip()

    print(f"Parsing quiz: {quiz_file.name}")

    # Parse
    parser = QuizParser()
    questions, answer_key = parser.parse(content)

    print(f"  Found {len(questions)} questions, {len(answer_key)} answer key entries")

    if not questions:
        raise ValueError("No questions found in the quiz file. "
                         "Questions should be formatted as **TF-N.**, **SA-N.**, or **MC-N.**")

    if not answer_key:
        print("  WARNING: No answer key found. Will take quiz but cannot grade.")

    # Take the quiz
    print(f"\nTaking quiz (mode: {mode}, RAG: {'on' if use_rag else 'off'})...")
    taker = QuizTaker(processor=processor if use_rag else None)
    llm_answers = taker.take_quiz(questions, mode=mode, use_rag=use_rag, n_results=n_results)

    # Grade
    if answer_key:
        print("\nGrading...")
        grader = QuizGrader()
        results = grader.grade(questions, llm_answers, answer_key)
    else:
        # No answer key — produce ungraded results
        results = [
            GradedQuestion(
                question=q,
                llm_answer=llm_answers.get(q.id, "[No answer]"),
                llm_extracted="?",
                correct_answer="[No answer key]",
                correct_explanation="",
                is_correct=None,
                score=0.0
            )
            for q in questions
        ]

    # Write report
    print(f"\nWriting results...")
    writer = QuizReportWriter()
    return writer.write(
        results,
        output_path,
        quiz_title=f"{quiz_title} — Graded Results",
        mode=mode,
        use_rag=use_rag
    )