import { useState, useCallback, useRef, useEffect } from "react";
import type { NormalizedQuestion } from "../../lib/types";
import { evaluateAnswer } from "../../lib/api";
import { renderMarkdown } from "../../components/renderMarkdown";
import ShortcutsOverlay, { isTypingTarget, type Shortcut } from "../../components/ShortcutsOverlay";

const QUIZ_SHORTCUTS: Shortcut[] = [
  { keys: "1 – 4", desc: "Select a multiple-choice option" },
  { keys: "T / F", desc: "Answer true / false" },
  { keys: "Enter", desc: "Next / Finish" },
  { keys: "Cmd/Ctrl + Enter", desc: "Submit while typing a short answer" },
];

interface Props {
  title: string;
  questions: NormalizedQuestion[];
  /** Model mode used for AI short-answer grading. */
  mode: string;
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
  correct: boolean | null;
  saScore?: Score;
  saFeedback?: string;
  /** Set when AI grading was attempted and failed; the item is "ungraded". */
  saError?: string;
}

function gradeLocal(q: NormalizedQuestion, given: string): boolean | null {
  if (q.sectionType === "short_answer") return null;
  if (q.sectionType === "true_false") return given === q.correctAnswer;
  const correctIdx = Number(q.correctAnswer);
  const givenIdx = q.options.indexOf(given);
  return givenIdx === correctIdx;
}

export default function QuizMode({ questions, mode, onExit }: Props) {
  const [index, setIndex] = useState(0);
  const [answers, setAnswers] = useState<Answer[]>([]);
  const [selected, setSelected] = useState<string | null>(null);
  const [saInput, setSaInput] = useState("");
  const [results, setResults] = useState<Result[] | null>(null);
  const [grading, setGrading] = useState(false);
  const [viewIndex, setViewIndex] = useState(0);
  const [showShortcuts, setShowShortcuts] = useState(false);

  // Short-answer grading promises, fired as the user presses Next (so grading
  // overlaps with the rest of the quiz) and resolved on the results screen.
  const saPromises = useRef<Map<string, Promise<{ score: Score; feedback: string }>>>(
    new Map(),
  );

  const q = questions[index];
  if (!q) return null;

  const total = questions.length;
  const progress = ((index + 1) / total) * 100;

  // Kick off (but don't await) grading for one short answer, caching the
  // promise so the results screen can resolve it later.
  const fireEval = useCallback(
    (question: NormalizedQuestion, given: string) => {
      const p = evaluateAnswer(question.text, given, question.correctAnswer, mode);
      p.catch(() => {}); // avoid unhandled-rejection warnings; handled on resolve
      saPromises.current.set(question.id, p);
      return p;
    },
    [mode],
  );

  const submitAnswer = useCallback(() => {
    const currentQ = questions[index];
    if (!currentQ) return;

    const value =
      currentQ.sectionType === "short_answer" ? saInput.trim() : selected ?? "";
    if (!value) return;

    // Fire short-answer grading now, as the user advances, instead of
    // waiting until Finish to grade them all at once.
    if (currentQ.sectionType === "short_answer") {
      fireEval(currentQ, value);
    }

    const newAnswers = [...answers, { questionId: currentQ.id, value }];
    setAnswers(newAnswers);
    setSelected(null);
    setSaInput("");

    if (index + 1 < total) {
      setIndex(index + 1);
    } else {
      finishQuiz(newAnswers);
    }
  }, [questions, selected, saInput, answers, index, total, fireEval]);

  /**
   * Grade the short-answer results at the given array indices via the LLM.
   * A rejected evaluation leaves saScore undefined and records saError so
   * the item shows as "ungraded" (never silent half credit) and can be
   * retried later. When `useCache` is set, the promises fired on Next are
   * awaited instead of starting fresh requests.
   */
  const gradeIndices = useCallback(
    async (base: Result[], targetIdxs: number[], useCache = false) => {
      if (targetIdxs.length === 0) return;
      setGrading(true);

      // Clear any prior error on the items about to be re-graded
      setResults((prev) => {
        if (!prev) return prev;
        const cleared = [...prev];
        for (const i of targetIdxs) {
          const item = cleared[i];
          if (item) cleared[i] = { ...item, saError: undefined };
        }
        return cleared;
      });

      const evaluations = await Promise.allSettled(
        targetIdxs.map((i) => {
          const r = base[i]!;
          const cached = useCache ? saPromises.current.get(r.question.id) : undefined;
          return cached ?? fireEval(r.question, r.given);
        }),
      );

      setResults((prev) => {
        if (!prev) return prev;
        const updated = [...prev];
        targetIdxs.forEach((i, k) => {
          const item = updated[i];
          if (!item) return;
          const eval_ = evaluations[k];
          if (eval_ && eval_.status === "fulfilled") {
            updated[i] = {
              ...item,
              saScore: eval_.value.score,
              saFeedback: eval_.value.feedback,
              saError: undefined,
              correct:
                eval_.value.score === "correct"
                  ? true
                  : eval_.value.score === "incorrect"
                    ? false
                    : null,
            };
          } else {
            const reason =
              eval_ && eval_.status === "rejected"
                ? eval_.reason instanceof Error
                  ? eval_.reason.message
                  : String(eval_.reason)
                : "Evaluation failed";
            updated[i] = {
              ...item,
              saScore: undefined,
              saFeedback: undefined,
              saError: reason,
              correct: null,
            };
          }
        });
        return updated;
      });

      setGrading(false);
    },
    [fireEval],
  );

  const finishQuiz = useCallback(
    async (finalAnswers: Answer[]) => {
      const initial: Result[] = questions.map((question) => {
        const a = finalAnswers.find((ans) => ans.questionId === question.id);
        return {
          question,
          given: a?.value ?? "",
          correct: a ? gradeLocal(question, a.value) : false,
        };
      });

      setResults(initial);

      const saIdxs = initial
        .map((r, i) => ({ r, i }))
        .filter(({ r }) => r.question.sectionType === "short_answer" && r.given)
        .map(({ i }) => i);

      // Resolve the grading promises already fired on Next.
      await gradeIndices(initial, saIdxs, true);
    },
    [questions, gradeIndices],
  );

  const retryGrading = useCallback(() => {
    if (!results || grading) return;
    const failedIdxs = results
      .map((r, i) => ({ r, i }))
      .filter(({ r }) => r.question.sectionType === "short_answer" && r.given && r.saError)
      .map(({ i }) => i);
    // Fresh requests (don't reuse the failed cached promises).
    gradeIndices(results, failedIdxs, false);
  }, [results, grading, gradeIndices]);

  // Keyboard shortcuts for the question screen: 1-4 select an option, T/F
  // answer true/false, Enter next/finish. While the short-answer textarea is
  // focused, only Cmd/Ctrl+Enter acts (other keys type into the field).
  useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      if (showShortcuts || results) return;
      const cq = questions[index];
      if (!cq) return;

      if (e.key === "Enter" && (e.metaKey || e.ctrlKey)) {
        e.preventDefault();
        submitAnswer();
        return;
      }
      if (isTypingTarget(e.target)) return; // typing a short answer

      if (cq.sectionType === "true_false") {
        if (e.key === "t" || e.key === "T") { e.preventDefault(); setSelected("true"); }
        else if (e.key === "f" || e.key === "F") { e.preventDefault(); setSelected("false"); }
        else if (e.key === "Enter") { e.preventDefault(); submitAnswer(); }
      } else if (cq.sectionType === "multiple_choice") {
        const n = Number(e.key);
        if (Number.isInteger(n) && n >= 1 && n <= cq.options.length) {
          e.preventDefault();
          setSelected(cq.options[n - 1]!);
        } else if (e.key === "Enter") {
          e.preventDefault();
          submitAnswer();
        }
      } else if (e.key === "Enter") {
        e.preventDefault();
        submitAnswer();
      }
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [questions, index, results, showShortcuts, submitAnswer]);

  // ---- Results screen ----
  if (results) {
    const autoGraded = results.filter(
      (r) => r.question.sectionType !== "short_answer",
    );
    const correctCount = autoGraded.filter((r) => r.correct === true).length;
    const totalAuto = autoGraded.length;

    const saResultsList = results.filter(
      (r) => r.question.sectionType === "short_answer",
    );
    const saCorrect = saResultsList.filter((r) => r.saScore === "correct").length;
    const saPartial = saResultsList.filter((r) => r.saScore === "partial").length;
    const saIncorrect = saResultsList.filter((r) => r.saScore === "incorrect").length;
    const saGradedCount = saResultsList.filter((r) => r.saScore != null).length;
    // Ungraded = SA answered but grading failed (has saError, no score)
    const saUngraded = saResultsList.filter((r) => r.given && r.saError && r.saScore == null);
    const saPending = saResultsList.length - saGradedCount - saUngraded.length;

    // Percentage denominator excludes ungraded questions entirely.
    const totalScored = totalAuto + saGradedCount;
    const totalCorrect = correctCount + saCorrect + saPartial * 0.5;
    const pct =
      totalScored > 0 ? Math.round((totalCorrect / totalScored) * 100) : 0;

    const r = results[viewIndex];
    if (!r) return null;

    const isSA = r.question.sectionType === "short_answer";

    const getResultClass = (res: Result) => {
      const sa = res.question.sectionType === "short_answer";
      if (sa) {
        if (res.saError && res.saScore == null) return "ungraded";
        if (grading && res.saScore == null) return "grading";
        if (res.saScore === "correct") return "correct";
        if (res.saScore === "incorrect") return "wrong";
        if (res.saScore === "partial") return "partial";
        return "grading";
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
              onClick={() =>
                setViewIndex((i) => Math.min(results.length - 1, i + 1))
              }
              disabled={viewIndex === results.length - 1}
            >
              &#8250;
            </button>
          </div>
        </div>

        <div className="quiz-results-layout">
          <div className="quiz-results-sidebar">
            <span className="quiz-score-pct-big">
              {grading && saResultsList.length > 0 ? "..." : `${pct}%`}
            </span>
            {totalAuto > 0 && (
              <span className="quiz-score-detail">
                T/F + MC: {correctCount}/{totalAuto} correct
              </span>
            )}
            {saResultsList.length > 0 && (
              <span className="quiz-score-detail">
                {grading
                  ? `Grading ${saPending} short answer${saPending !== 1 ? "s" : ""}...`
                  : `SA: ${saCorrect} correct, ${saPartial} partial, ${saIncorrect} incorrect`}
              </span>
            )}
            {!grading && saUngraded.length > 0 && (
              <span className="quiz-score-detail quiz-score-detail--warn">
                {saUngraded.length} ungraded (excluded from score)
              </span>
            )}
            <span className="quiz-score-detail quiz-score-detail--model">
              grader: {mode}
            </span>
            {!grading && saUngraded.length > 0 && (
              <button className="quiz-retry-grading" onClick={retryGrading}>
                &#8635; Retry grading ({saUngraded.length})
              </button>
            )}

            <div className="quiz-results-qlist">
              {results.map((res, i) => {
                const cls = getResultClass(res);
                return (
                  <button
                    key={res.question.id}
                    className={`quiz-results-qitem quiz-results-qitem--${cls} ${i === viewIndex ? "quiz-results-qitem--active" : ""}`}
                    onClick={() => setViewIndex(i)}
                  >
                    <span className="quiz-results-qitem-id">
                      {res.question.id}
                    </span>
                    <span
                      className={`quiz-results-qitem-dot quiz-results-qitem-dot--${cls}`}
                    />
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

          <div className="quiz-results-detail">
            <div className={`quiz-detail-card quiz-detail-card--${currentCls}`}>
              <div className="quiz-detail-header">
                <span className="quiz-detail-id">{r.question.id}</span>
                <span
                  className={`quiz-detail-badge quiz-detail-badge--${currentCls}`}
                >
                  {isSA
                    ? r.saError && r.saScore == null
                      ? "ungraded"
                      : grading && r.saScore == null
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

              {!isSA && (
                <div className="quiz-detail-answers">
                  <div className="quiz-detail-row">
                    <span className="quiz-result-field-label">
                      Your answer:
                    </span>{" "}
                    <span
                      className={
                        r.correct === false
                          ? "quiz-result-val--wrong"
                          : "quiz-result-val--correct"
                      }
                    >
                      {renderMarkdown(r.given)}
                    </span>
                  </div>
                  {r.correct === false && (
                    <div className="quiz-detail-row">
                      <span className="quiz-result-field-label">Correct:</span>{" "}
                      <span className="quiz-result-val--correct">
                        {renderMarkdown(
                          r.question.sectionType === "true_false"
                            ? r.question.correctAnswer === "true"
                              ? "true"
                              : "false"
                            : r.question.options[
                                Number(r.question.correctAnswer)
                              ] ?? r.question.correctAnswer,
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

              {isSA && (
                <div className="quiz-detail-answers">
                  {r.saError && r.saScore == null && (
                    <div className="quiz-detail-ungraded">
                      Not graded — {r.saError}. Use "Retry grading" to try again.
                    </div>
                  )}
                  {r.saFeedback && (
                    <div className="quiz-detail-explanation">
                      {renderMarkdown(r.saFeedback)}
                    </div>
                  )}
                  {r.given && (
                    <div className="quiz-detail-row">
                      <span className="quiz-result-field-label">
                        Your answer:
                      </span>{" "}
                      {renderMarkdown(r.given)}
                    </div>
                  )}
                  {r.question.correctAnswer && (
                    <div className="quiz-detail-row quiz-detail-answer-key">
                      <span className="quiz-result-field-label">
                        Answer key:
                      </span>{" "}
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
        <div className="study-header-right">
          <span className="study-counter">
            Question {index + 1} / {total}
          </span>
          <button
            className="help-btn help-btn--apollo"
            title="Keyboard shortcuts"
            onClick={() => setShowShortcuts(true)}
          >
            ?
          </button>
        </div>
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

      {showShortcuts && (
        <ShortcutsOverlay
          title="Quiz shortcuts"
          shortcuts={QUIZ_SHORTCUTS}
          onClose={() => setShowShortcuts(false)}
        />
      )}
    </div>
  );
}