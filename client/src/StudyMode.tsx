import { useState, useMemo, useCallback } from "react";
import type { QuizData } from "./types";

interface Props {
  quiz: QuizData;
  onExit: () => void;
}

function shuffle<T>(arr: T[]): T[] {
  const a = [...arr];
  for (let i = a.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [a[i], a[j]] = [a[j], a[i]];
  }
  return a;
}

export default function StudyMode({ quiz, onExit }: Props) {
  const cards = useMemo(() => shuffle(quiz.questions), [quiz.questions]);
  const [index, setIndex] = useState(0);
  const [flipped, setFlipped] = useState(false);

  const card = cards[index];
  const total = cards.length;

  const flip = useCallback(() => setFlipped((f) => !f), []);
  const prev = useCallback(() => {
    setFlipped(false);
    setIndex((i) => Math.max(0, i - 1));
  }, []);
  const next = useCallback(() => {
    setFlipped(false);
    setIndex((i) => Math.min(total - 1, i + 1));
  }, [total]);

  return (
    <div className="study">
      {/* Sub-header */}
      <div className="study-header">
        <button className="study-exit" onClick={onExit}>
          &#10005; Exit Study Mode
        </button>
        <span className="study-counter">
          Card {index + 1} / {total}
        </span>
      </div>

      {/* Card */}
      <div className="study-area">
        <div
          className={`study-card ${flipped ? "study-card--flipped" : ""}`}
          onClick={flip}
        >
          {!flipped ? (
            <>
              <span className="study-card-label">QUESTION</span>
              <p className="study-card-text">{card.text}</p>
              {card.choices.length > 0 && (
                <div className="study-card-choices">
                  {card.choices.map((c, i) => (
                    <div key={i} className="study-choice">
                      {c}
                    </div>
                  ))}
                </div>
              )}
              <span className="study-card-hint">Click to flip</span>
            </>
          ) : (
            <>
              <span className="study-card-label">ANSWER</span>
              <p className="study-card-text">
                {card.qtype === "tf"
                  ? card.answer === "T"
                    ? "True"
                    : "False"
                  : card.qtype === "mc"
                    ? card.choices[
                        card.answer.replace(/[()]/g, "").charCodeAt(0) - 97
                      ] ?? card.answer
                    : card.answer}
              </p>
              {card.explanation && (
                <p className="study-card-explanation">{card.explanation}</p>
              )}
              <span className="study-card-hint">Click to flip back</span>
            </>
          )}
        </div>
      </div>

      {/* Navigation */}
      <div className="study-nav">
        <button
          className="study-nav-btn"
          onClick={prev}
          disabled={index === 0}
        >
          &#8249; Previous
        </button>
        <button className="study-nav-btn study-nav-btn--flip" onClick={flip}>
          &#8635; Flip Card
        </button>
        <button
          className="study-nav-btn"
          onClick={next}
          disabled={index === total - 1}
        >
          Next &#8250;
        </button>
      </div>
    </div>
  );
}