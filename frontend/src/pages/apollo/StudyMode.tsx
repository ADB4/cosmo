import { useState, useMemo, useCallback } from "react";
import type { NormalizedQuestion } from "../../lib/types";
import { filterByTags, collectTags, TAG_CATEGORIES } from "../../lib/normalizeQuiz";
import { renderMarkdown } from "../../components/renderMarkdown";

interface Props {
  title: string;
  questions: NormalizedQuestion[];
  onExit: () => void;
}

type OrderMode = "sequential" | "shuffle-within-type" | "shuffle-all";

const ORDER_LABELS: Record<OrderMode, string> = {
  sequential: "Sequential",
  "shuffle-within-type": "Shuffled (within type)",
  "shuffle-all": "Shuffled (all)",
};

const TYPE_LABELS: Record<string, string> = {
  true_false: "True/False",
  multiple_choice: "Multiple Choice",
  short_answer: "Short Answer",
};

const SECTION_TYPES = ["true_false", "multiple_choice", "short_answer"] as const;

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
  const [selectedTypes, setSelectedTypes] = useState<Set<string>>(new Set());
  const [order, setOrder] = useState<OrderMode>("sequential");
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

  // Filter by tags, then by question type, then apply ordering
  const cards = useMemo(() => {
    let filtered = filterByTags(questions, selectedTags);

    if (selectedTypes.size > 0) {
      filtered = filtered.filter((q) => selectedTypes.has(q.sectionType));
    }

    switch (order) {
      case "sequential":
        return filtered;
      case "shuffle-within-type": {
        const tf = shuffle(filtered.filter((q) => q.sectionType === "true_false"));
        const mc = shuffle(filtered.filter((q) => q.sectionType === "multiple_choice"));
        const sa = shuffle(filtered.filter((q) => q.sectionType === "short_answer"));
        return [...tf, ...mc, ...sa];
      }
      case "shuffle-all":
        return shuffle(filtered);
    }
  }, [questions, selectedTags, selectedTypes, order]);

  const total = cards.length;
  const card = cards[index] as NormalizedQuestion | undefined;

  const hasFilters = selectedTags.size > 0 || selectedTypes.size > 0;

  const resetPosition = useCallback(() => {
    setIndex(0);
    setFlipped(false);
  }, []);

  const toggleTag = useCallback((tag: string) => {
    setSelectedTags((prev) => {
      const next = new Set(prev);
      if (next.has(tag)) next.delete(tag);
      else next.add(tag);
      return next;
    });
    resetPosition();
  }, [resetPosition]);

  const clearTags = useCallback(() => {
    setSelectedTags(new Set());
    resetPosition();
  }, [resetPosition]);

  const toggleType = useCallback((type: string) => {
    setSelectedTypes((prev) => {
      const next = new Set(prev);
      if (next.has(type)) next.delete(type);
      else next.add(type);
      return next;
    });
    resetPosition();
  }, [resetPosition]);

  const clearTypes = useCallback(() => {
    setSelectedTypes(new Set());
    resetPosition();
  }, [resetPosition]);

  const changeOrder = useCallback((mode: OrderMode) => {
    setOrder(mode);
    resetPosition();
  }, [resetPosition]);

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
          {total > 0 ? `${index + 1} / ${total}` : "0 / 0"}
        </span>
      </div>

      <div className="study-body">
        {/* ── Left sidebar ── */}
        <div className="study-sidebar">
          {/* Order */}
          <div className="study-sidebar-section">
            <span className="study-filter-title">Order</span>
            <div className="study-order-options">
              {(Object.keys(ORDER_LABELS) as OrderMode[]).map((mode) => (
                <button
                  key={mode}
                  className={`study-order-btn ${order === mode ? "study-order-btn--active" : ""}`}
                  onClick={() => changeOrder(mode)}
                >
                  {ORDER_LABELS[mode]}
                </button>
              ))}
            </div>
          </div>

          {/* Filter by topic */}
          <div className="study-sidebar-section">
            <div className="study-filter-header">
              <span className="study-filter-title">Filter by topic</span>
              {selectedTags.size > 0 && (
                <button className="study-filter-clear" onClick={clearTags}>
                  Clear
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
          </div>

          {/* Filter by question type */}
          <div className="study-sidebar-section">
            <div className="study-filter-header">
              <span className="study-filter-title">Question type</span>
              {selectedTypes.size > 0 && (
                <button className="study-filter-clear" onClick={clearTypes}>
                  Clear
                </button>
              )}
            </div>
            <div className="study-filter-tags">
              {SECTION_TYPES.map((type) => (
                <button
                  key={type}
                  className={`study-filter-tag ${selectedTypes.has(type) ? "study-filter-tag--active" : ""}`}
                  onClick={() => toggleType(type)}
                >
                  {TYPE_LABELS[type]}
                </button>
              ))}
            </div>
          </div>

          {/* Filter summary */}
          {hasFilters && (
            <div className="study-filter-summary">
              {total} card{total !== 1 ? "s" : ""} match
            </div>
          )}
        </div>

        {/* ── Main area ── */}
        <div className="study-main">
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
                  No questions match the selected filters. Try broadening your selection.
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
      </div>
    </div>
  );
}