import { useState, useMemo, useCallback } from "react";
import type { NormalizedQuestion } from "./types";
import { renderMarkdown } from "./renderMarkdown";

interface Props {
  title: string;
  questions: NormalizedQuestion[];
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

function answerDisplay(q: NormalizedQuestion): string {
  switch (q.sectionType) {
    case "true_false":
      return q.correctAnswer === "true" ? "True" : "False";
    case "multiple_choice": {
      const idx = Number(q.correctAnswer);
      return q.options[idx] ?? q.correctAnswer;
    }
    case "short_answer":
      return q.correctAnswer;
  }
}

export default function StudyMode({ questions, onExit }: Props) {
  const cards = useMemo(() => shuffle(questions), [questions]);
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
      <div className="study-header">
        <button className="study-exit" onClick={onExit}>
          &#10005; Exit Study Mode
        </button>
        <span className="study-counter">
          Card {index + 1} / {total}
        </span>
      </div>

      <div className="study-area">
        <div
          className={`study-card ${flipped ? "study-card--flipped" : ""}`}
          onClick={flip}
        >
          {!flipped ? (
            <>
              <span className="study-card-label">QUESTION</span>
              <div className="study-card-text">{renderMarkdown(card.text)}</div>
              {card.code && (
                <pre className="code-block" data-lang="typescript">
                  <code>{card.code}</code>
                </pre>
              )}
              {card.options.length > 0 && (
                <div className="study-card-choices">
                  {card.options.map((c, i) => (
                    <div key={i} className="study-choice">
                      {renderMarkdown(c)}
                    </div>
                  ))}
                </div>
              )}
              <span className="study-card-hint">Click to flip</span>
            </>
          ) : (
            <>
              <span className="study-card-label">ANSWER</span>
              <div className="study-card-text">{renderMarkdown(answerDisplay(card))}</div>
              {card.explanation && (
                <div className="study-card-explanation">{renderMarkdown(card.explanation)}</div>
              )}
              <span className="study-card-hint">Click to flip back</span>
            </>
          )}
        </div>
      </div>

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