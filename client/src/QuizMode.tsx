import { useState, useCallback } from "react";
import type { NormalizedQuestion } from "./types";
import { evaluateAnswer } from "./api";
import { renderMarkdown } from "./renderMarkdown";

interface Props {
  title: string;
  questions: NormalizedQuestion[];
  onExit: () => void;
}

interface Answer {
  questionId: string;
  value: string;
}

type Score = "correct" | "partial" | "incorrect";

interface Result {
  question: NormalizedQuestion;
  given: string;
  correct: boolean | null;      // null = SA pending/evaluated separately
  saScore?: Score;               // AI evaluation result
  saFeedback?: string;           // AI feedback text
}

function gradeLocal(q: NormalizedQuestion, given: string): boolean | null {
  if (q.sectionType === "short_answer") return null;
  if (q.sectionType === "true_false") return given === q.correctAnswer;
  const correctIdx = Number(q.correctAnswer);
  const givenIdx = q.options.indexOf(given);
  return givenIdx === correctIdx;
}

export default function QuizMode({ questions, onExit }: Props) {
  const [index, setIndex] = useState(0);
  const [answers, setAnswers] = useState<Answer[]>([]);
  const [selected, setSelected] = useState<string | null>(null);
  const [saInput, setSaInput] = useState("");
  const [results, setResults] = useState<Result[] | null>(null);
  const [grading, setGrading] = useState(false);
  const [viewIndex, setViewIndex] = useState(0);

  const q = questions[index];
  const total = questions.length;
  const progress = ((index + 1) / total) * 100;

  const submitAnswer = useCallback(() => {
    const value =
      q.sectionType === "short_answer" ? saInput.trim() : selected ?? "";
    if (!value) return;

    const newAnswers = [...answers, { questionId: q.id, value }];
    setAnswers(newAnswers);
    setSelected(null);
    setSaInput("");

    if (index + 1 < total) {
      setIndex(index + 1);
    } else {
      finishQuiz(newAnswers);
    }
  }, [q, selected, saInput, answers, index, total, questions]);

  const finishQuiz = useCallback(
    async (finalAnswers: Answer[]) => {
      // Build initial results — SA questions marked as null
      const initial: Result[] = questions.map((question) => {
        const a = finalAnswers.find((ans) => ans.questionId === question.id);
        return {
          question,
          given: a?.value ?? "",
          correct: a ? gradeLocal(question, a.value) : false,
        };
      });

      setResults(initial);

      // Find SA questions that need AI evaluation
      const saResults = initial.filter(
        (r) => r.question.sectionType === "short_answer" && r.given,
      );

      if (saResults.length === 0) return;

      setGrading(true);

      // Evaluate SA answers in parallel
      const evaluations = await Promise.allSettled(
        saResults.map((r) =>
          evaluateAnswer(
            r.question.text,
            r.given,
            r.question.correctAnswer,
          ),
        ),
      );

      // Merge evaluations back into results
      setResults((prev) => {
        if (!prev) return prev;
        const updated = [...prev];
        let evalIdx = 0;
        for (let i = 0; i < updated.length; i++) {
          if (
            updated[i].question.sectionType === "short_answer" &&
            updated[i].given
          ) {
            const eval_ = evaluations[evalIdx];
            if (eval_.status === "fulfilled") {
              updated[i] = {
                ...updated[i],
                saScore: eval_.value.score,
                saFeedback: eval_.value.feedback,
                correct:
                  eval_.value.score === "correct"
                    ? true
                    : eval_.value.score === "incorrect"
                      ? false
                      : null,
              };
            } else {
              updated[i] = {
                ...updated[i],
                saScore: "partial",
                saFeedback: "Evaluation failed — could not reach Ollama.",
              };
            }
            evalIdx++;
          }
        }
        return updated;
      });

      setGrading(false);
    },
    [questions],
  );

  // ---- Results screen ----
  if (results) {
    // T/F + MC stats
    const autoGraded = results.filter(
      (r) => r.question.sectionType !== "short_answer",
    );
    const correctCount = autoGraded.filter((r) => r.correct === true).length;
    const totalAuto = autoGraded.length;

    // SA stats
    const saResults = results.filter(
      (r) => r.question.sectionType === "short_answer",
    );
    const saCorrect = saResults.filter((r) => r.saScore === "correct").length;
    const saPartial = saResults.filter((r) => r.saScore === "partial").length;
    const saIncorrect = saResults.length - saCorrect - saPartial;
    const saGradedCount = saResults.filter((r) => r.saScore != null).length;

    // Overall percentage
    const totalQuestions = totalAuto + saResults.length;
    const totalCorrect = correctCount + saCorrect + saPartial * 0.5;
    const pct =
      totalQuestions > 0
        ? Math.round((totalCorrect / totalQuestions) * 100)
        : 0;

    const r = results[viewIndex];
    const isSA = r.question.sectionType === "short_answer";

    const getResultClass = (res: Result) => {
      const sa = res.question.sectionType === "short_answer";
      if (sa) {
        if (grading && !res.saScore) return "grading";
        if (res.saScore === "correct") return "correct";
        if (res.saScore === "incorrect") return "wrong";
        return "partial";
      }
      return res.correct === true ? "correct" : "wrong";
    };

    const currentCls = getResultClass(r);

    return (
      <div className="quiz">
        <div className="quiz-header">
          <button className="study-exit" onClick={onExit}>
            &#10005; Exit Quiz
          </button>
          <div className="quiz-results-nav">
            <button
              className="quiz-results-nav-btn"
              onClick={() => setViewIndex((i) => Math.max(0, i - 1))}
              disabled={viewIndex === 0}
            >
              &#8249;
            </button>
            <span className="quiz-results-nav-label">
              {viewIndex + 1} / {results.length}
            </span>
            <button
              className="quiz-results-nav-btn"
              onClick={() => setViewIndex((i) => Math.min(results.length - 1, i + 1))}
              disabled={viewIndex === results.length - 1}
            >
              &#8250;
            </button>
          </div>
        </div>

        <div className="quiz-results-layout">
          {/* Sidebar: score + question list */}
          <div className="quiz-results-sidebar">
            <span className="quiz-score-pct-big">
              {grading && saResults.length > 0 ? "..." : `${pct}%`}
            </span>
            {totalAuto > 0 && (
              <span className="quiz-score-detail">
                T/F + MC: {correctCount}/{totalAuto} correct
              </span>
            )}
            {saResults.length > 0 && (
              <span className="quiz-score-detail">
                {grading
                  ? `Grading ${saResults.length - saGradedCount} short answer${saResults.length - saGradedCount !== 1 ? "s" : ""}...`
                  : `SA: ${saCorrect} correct, ${saPartial} partial, ${saIncorrect} incorrect`}
              </span>
            )}

            {/* Scrollable question list */}
            <div className="quiz-results-qlist">
              {results.map((res, i) => {
                const cls = getResultClass(res);
                return (
                  <button
                    key={res.question.id}
                    className={`quiz-results-qitem quiz-results-qitem--${cls} ${i === viewIndex ? "quiz-results-qitem--active" : ""}`}
                    onClick={() => setViewIndex(i)}
                  >
                    <span className="quiz-results-qitem-id">{res.question.id}</span>
                    <span className={`quiz-results-qitem-dot quiz-results-qitem-dot--${cls}`} />
                  </button>
                );
              })}
            </div>

            <div className="quiz-results-actions">
              <button className="study-nav-btn" onClick={onExit}>
                Done
              </button>
            </div>
          </div>

          {/* Detail view */}
          <div className="quiz-results-detail">
            <div className={`quiz-detail-card quiz-detail-card--${currentCls}`}>
              <div className="quiz-detail-header">
                <span className="quiz-detail-id">{r.question.id}</span>
                <span className={`quiz-detail-badge quiz-detail-badge--${currentCls}`}>
                  {isSA
                    ? grading && !r.saScore
                      ? "grading..."
                      : r.saScore ?? "pending"
                    : r.correct
                      ? "correct"
                      : "incorrect"}
                </span>
              </div>

              <div className="quiz-detail-question">
                {renderMarkdown(r.question.text)}
              </div>

              {r.question.code && (
                <pre className="code-block" data-lang="typescript">
                  <code>{r.question.code}</code>
                </pre>
              )}

              {/* T/F and MC answers */}
              {!isSA && (
                <div className="quiz-detail-answers">
                  <div className="quiz-detail-row">
                    <span className="quiz-result-field-label">Your answer:</span>{" "}
                    <span className={r.correct === false ? "quiz-result-val--wrong" : "quiz-result-val--correct"}>
                      {renderMarkdown(r.given)}
                    </span>
                  </div>
                  {r.correct === false && (
                    <div className="quiz-detail-row">
                      <span className="quiz-result-field-label">Correct:</span>{" "}
                      <span className="quiz-result-val--correct">
                        {renderMarkdown(
                          r.question.sectionType === "true_false"
                            ? r.question.correctAnswer === "true" ? "true" : "false"
                            : r.question.options[Number(r.question.correctAnswer)] ?? r.question.correctAnswer
                        )}
                      </span>
                    </div>
                  )}
                  {r.correct === false && r.question.explanation && (
                    <div className="quiz-detail-explanation">
                      {renderMarkdown(r.question.explanation)}
                    </div>
                  )}
                </div>
              )}

              {/* SA answers */}
              {isSA && (
                <div className="quiz-detail-answers">
                  {r.saFeedback && (
                    <div className="quiz-detail-explanation">
                      {renderMarkdown(r.saFeedback)}
                    </div>
                  )}
                  {r.given && (
                    <div className="quiz-detail-row">
                      <span className="quiz-result-field-label">Your answer:</span>{" "}
                      {renderMarkdown(r.given)}
                    </div>
                  )}
                  {r.question.correctAnswer && (
                    <div className="quiz-detail-row quiz-detail-answer-key">
                      <span className="quiz-result-field-label">Answer key:</span>{" "}
                      {renderMarkdown(r.question.correctAnswer)}
                    </div>
                  )}
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    );
  }

  // ---- Question screen ----
  const typeLabel =
    q.sectionType === "true_false"
      ? "TRUE FALSE"
      : q.sectionType === "multiple_choice"
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

      <div className="quiz-progress">
        <div className="quiz-progress-fill" style={{ width: `${progress}%` }} />
      </div>

      <div className="quiz-area">
        <span className="quiz-type-label">{typeLabel}</span>
        <div className="quiz-question-text">{renderMarkdown(q.text)}</div>

        {q.code && (
          <pre className="code-block" data-lang="typescript">
            <code>{q.code}</code>
          </pre>
        )}

        {q.sectionType === "true_false" && (
          <div className="quiz-options">
            {(["true", "false"] as const).map((val) => (
              <button
                key={val}
                className={`quiz-option ${selected === val ? "quiz-option--selected" : ""}`}
                onClick={() => setSelected(val)}
              >
                {val === "true" ? "True" : "False"}
              </button>
            ))}
          </div>
        )}

        {q.sectionType === "multiple_choice" && (
          <div className="quiz-options">
            {q.options.map((c) => (
              <button
                key={c}
                className={`quiz-option ${selected === c ? "quiz-option--selected" : ""}`}
                onClick={() => setSelected(c)}
              >
                {renderMarkdown(c)}
              </button>
            ))}
          </div>
        )}

        {q.sectionType === "short_answer" && (
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
              q.sectionType === "short_answer"
                ? !saInput.trim()
                : selected === null
            }
          >
            {index + 1 < total ? "Next" : "Finish"}
          </button>
        </div>
      </div>
    </div>
  );
}