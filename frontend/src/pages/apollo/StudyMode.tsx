import { useState, useMemo, useCallback } from "react";
import type { NormalizedQuestion } from "../../lib/types";
import { filterByTags, collectTags, TAG_CATEGORIES } from "../../lib/normalizeQuiz";
import { renderMarkdown } from "../../components/renderMarkdown";

interface Props {
  title: string;
  questions: NormalizedQuestion[];
  onExit: () => void;
}

function shuffle<T>(arr: T[]): T[] {
  const a = [...arr];
  for (let i = a.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [a[i], a[j]] = [a[j]!, a[i]!];
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

/** Pretty-print a kebab-case tag */
function formatTag(tag: string): string {
  return tag.replace(/-/g, " ");
}

export default function StudyMode({ questions, onExit }: Props) {
  const [selectedTags, setSelectedTags] = useState<Set<string>>(new Set());
  const [filterOpen, setFilterOpen] = useState(false);
  const [index, setIndex] = useState(0);
  const [flipped, setFlipped] = useState(false);

  // All tags present in this quiz's question pool
  const availableTags = useMemo(() => collectTags(questions), [questions]);

  // Group tags by category, only showing categories/tags that exist in the data
  const groupedTags = useMemo(() => {
    const tagSet = new Set(availableTags);
    const groups: { category: string; tags: string[] }[] = [];

    for (const [category, tags] of Object.entries(TAG_CATEGORIES)) {
      const present = tags.filter((t) => tagSet.has(t));
      if (present.length > 0) groups.push({ category, tags: present });
      for (const t of present) tagSet.delete(t);
    }

    const remaining = [...tagSet].sort();
    if (remaining.length > 0) {
      groups.push({ category: "Other", tags: remaining });
    }

    return groups;
  }, [availableTags]);

  // Filtered + shuffled deck (re-shuffles when tag selection changes)
  const cards = useMemo(
    () => shuffle(filterByTags(questions, selectedTags)),
    [questions, selectedTags],
  );

  const total = cards.length;
  const card = cards[index] as NormalizedQuestion | undefined;

  const toggleTag = useCallback((tag: string) => {
    setSelectedTags((prev) => {
      const next = new Set(prev);
      if (next.has(tag)) next.delete(tag);
      else next.add(tag);
      return next;
    });
    setIndex(0);
    setFlipped(false);
  }, []);

  const clearTags = useCallback(() => {
    setSelectedTags(new Set());
    setIndex(0);
    setFlipped(false);
  }, []);

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
        <div className="study-header-right">
          <button
            className={`study-filter-toggle ${filterOpen ? "study-filter-toggle--active" : ""}`}
            onClick={() => setFilterOpen((o) => !o)}
            title="Filter by topic"
          >
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <polygon points="22 3 2 3 10 12.46 10 19 14 21 14 12.46 22 3" />
            </svg>
            {selectedTags.size > 0 && (
              <span className="study-filter-badge">{selectedTags.size}</span>
            )}
          </button>
          <span className="study-counter">
            {total > 0 ? `${index + 1} / ${total}` : "0 / 0"}
          </span>
        </div>
      </div>

      {filterOpen && (
        <div className="study-filter-panel">
          <div className="study-filter-header">
            <span className="study-filter-title">Filter by topic</span>
            {selectedTags.size > 0 && (
              <button className="study-filter-clear" onClick={clearTags}>
                Clear all
              </button>
            )}
          </div>
          <div className="study-filter-groups">
            {groupedTags.map(({ category, tags }) => (
              <div key={category} className="study-filter-group">
                <span className="study-filter-group-label">{category}</span>
                <div className="study-filter-tags">
                  {tags.map((tag) => (
                    <button
                      key={tag}
                      className={`study-filter-tag ${selectedTags.has(tag) ? "study-filter-tag--active" : ""}`}
                      onClick={() => toggleTag(tag)}
                    >
                      {formatTag(tag)}
                    </button>
                  ))}
                </div>
              </div>
            ))}
          </div>
          {selectedTags.size > 0 && (
            <div className="study-filter-summary">
              {total} card{total !== 1 ? "s" : ""} match
            </div>
          )}
        </div>
      )}

      <div className="study-area">
        {card ? (
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
                {card.tags.length > 0 && (
                  <div className="study-card-tags">
                    {card.tags.map((t) => (
                      <span key={t} className="study-card-tag">{formatTag(t)}</span>
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
        ) : (
          <div className="study-card study-card--empty">
            <span className="study-card-label">NO CARDS</span>
            <div className="study-card-text">
              No questions match the selected tags. Try broadening your filter.
            </div>
          </div>
        )}
      </div>

      <div className="study-nav">
        <button className="study-nav-btn" onClick={prev} disabled={!card || index === 0}>
          &#8249; Previous
        </button>
        <button className="study-nav-btn study-nav-btn--flip" onClick={flip} disabled={!card}>
          &#8635; Flip Card
        </button>
        <button className="study-nav-btn" onClick={next} disabled={!card || index === total - 1}>
          Next &#8250;
        </button>
      </div>
    </div>
  );
}