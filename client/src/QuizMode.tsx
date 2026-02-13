import { useState, useCallback } from "react";
import type { QuizData, QuizQuestion } from "./types";

interface Props {
  quiz: QuizData;
  onExit: () => void;
}

interface Answer {
  questionId: string;
  value: string;
}

interface Result {
  question: QuizQuestion;
  given: string;
  correct: boolean | null; // null = SA, needs manual review
}

function normalizeAnswer(q: QuizQuestion, given: string): boolean | null {
  if (q.qtype === "sa") return null;
  if (q.qtype === "tf") {
    const g = given.toUpperCase();
    return g === q.answer.toUpperCase();
  }
  // mc: answer is like "(b)", given is the choice text — match by index
  const correctIdx = q.answer.replace(/[()]/g, "").charCodeAt(0) - 97;
  const givenIdx = q.choices.indexOf(given);
  return givenIdx === correctIdx;
}

export default function QuizMode({ quiz, onExit }: Props) {
  const [index, setIndex] = useState(0);
  const [answers, setAnswers] = useState<Answer[]>([]);
  const [selected, setSelected] = useState<string | null>(null);
  const [saInput, setSaInput] = useState("");
  const [results, setResults] = useState<Result[] | null>(null);

  const q = quiz.questions[index];
  const total = quiz.questions.length;
  const progress = ((index + 1) / total) * 100;

  const submitAnswer = useCallback(() => {
    const value =
      q.qtype === "sa" ? saInput.trim() : selected ?? "";
    if (!value) return;

    const newAnswers = [...answers, { questionId: q.id, value }];
    setAnswers(newAnswers);
    setSelected(null);
    setSaInput("");

    if (index + 1 < total) {
      setIndex(index + 1);
    } else {
      // Grade
      const graded: Result[] = quiz.questions.map((question) => {
        const a = newAnswers.find((ans) => ans.questionId === question.id);
        return {
          question,
          given: a?.value ?? "",
          correct: a ? normalizeAnswer(question, a.value) : false,
        };
      });
      setResults(graded);
    }
  }, [q, selected, saInput, answers, index, total, quiz.questions]);

  // Results screen
  if (results) {
    const autoGraded = results.filter((r) => r.correct !== null);
    const correctCount = autoGraded.filter((r) => r.correct === true).length;
    const totalAuto = autoGraded.length;
    const pct = totalAuto > 0 ? Math.round((correctCount / totalAuto) * 100) : 0;

    return (
      <div className="quiz">
        <div className="quiz-header">
          <button className="study-exit" onClick={onExit}>
            &#10005; Exit Quiz
          </button>
          <span className="study-counter">Results</span>
        </div>

        <div className="quiz-results">
          <div className="quiz-results-score">
            <span className="quiz-score-num">
              {correctCount}/{totalAuto}
            </span>
            <span className="quiz-score-pct">{pct}%</span>
          </div>

          <div className="quiz-results-list">
            {results.map((r) => {
              const icon =
                r.correct === true
                  ? "\u2713"
                  : r.correct === false
                    ? "\u2717"
                    : "?";
              const cls =
                r.correct === true
                  ? "quiz-result--correct"
                  : r.correct === false
                    ? "quiz-result--wrong"
                    : "quiz-result--manual";

              return (
                <div key={r.question.id} className={`quiz-result-row ${cls}`}>
                  <span className="quiz-result-icon">{icon}</span>
                  <div className="quiz-result-body">
                    <span className="quiz-result-id">{r.question.id}</span>
                    <span className="quiz-result-text">
                      {r.question.text.slice(0, 100)}
                      {r.question.text.length > 100 ? "..." : ""}
                    </span>
                    {r.correct === false && r.question.explanation && (
                      <span className="quiz-result-expl">
                        {r.question.explanation}
                      </span>
                    )}
                  </div>
                  <span className="quiz-result-answer">
                    {r.given.slice(0, 40)}
                  </span>
                </div>
              );
            })}
          </div>

          <button className="study-nav-btn" onClick={onExit}>
            Done
          </button>
        </div>
      </div>
    );
  }

  // Question screen
  const typeLabel =
    q.qtype === "tf"
      ? "TRUE FALSE"
      : q.qtype === "mc"
        ? "MULTIPLE CHOICE"
        : "SHORT ANSWER";

  return (
    <div className="quiz">
      <div className="quiz-header">
        <button className="study-exit" onClick={onExit}>
          &#10005; Exit Quiz
        </button>
        <span className="study-counter">
          Question {index + 1} / {total}
        </span>
      </div>

      {/* Progress bar */}
      <div className="quiz-progress">
        <div className="quiz-progress-fill" style={{ width: `${progress}%` }} />
      </div>

      {/* Question */}
      <div className="quiz-area">
        <span className="quiz-type-label">{typeLabel}</span>
        <p className="quiz-question-text">{q.text}</p>

        {q.qtype === "tf" && (
          <div className="quiz-options">
            {["True", "False"].map((opt) => (
              <button
                key={opt}
                className={`quiz-option ${selected === opt ? "quiz-option--selected" : ""}`}
                onClick={() => setSelected(opt === "True" ? "T" : "F")}
              >
                {opt}
              </button>
            ))}
          </div>
        )}

        {q.qtype === "mc" && (
          <div className="quiz-options">
            {q.choices.map((c) => (
              <button
                key={c}
                className={`quiz-option ${selected === c ? "quiz-option--selected" : ""}`}
                onClick={() => setSelected(c)}
              >
                {c}
              </button>
            ))}
          </div>
        )}

        {q.qtype === "sa" && (
          <textarea
            className="quiz-sa-input"
            value={saInput}
            onChange={(e) => setSaInput(e.target.value)}
            placeholder="Type your answer..."
            rows={4}
          />
        )}

        <div className="quiz-submit-row">
          <button
            className="quiz-submit"
            onClick={submitAnswer}
            disabled={
              q.qtype === "sa" ? !saInput.trim() : selected === null
            }
          >
            {index + 1 < total ? "Next" : "Finish"}
          </button>
        </div>
      </div>
    </div>
  );
}