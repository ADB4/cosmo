import { useState, useMemo, useCallback, useEffect } from "react";
import type { NormalizedQuestion } from "../../lib/types";
import { filterByTags, collectTags, TAG_CATEGORIES } from "../../lib/normalizeQuiz";
import { renderMarkdown } from "../../components/renderMarkdown";
import ShortcutsOverlay, { isTypingTarget, type Shortcut } from "../../components/ShortcutsOverlay";

const STUDY_SHORTCUTS: Shortcut[] = [
  { keys: "Space / Enter", desc: "Flip card" },
  { keys: "←", desc: "Previous card" },
  { keys: "→", desc: "Next card" },
];

interface Props {
  title: string;
  questions: NormalizedQuestion[];
  /** Ids missed on the last quiz attempt for this deck, if any. */
  missedIds?: Set<string>;
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

/**
 * Deterministic Fisher–Yates shuffle seeded by `seed` (mulberry32 PRNG).
 *
 * Using a fixed seed instead of Math.random means the arrangement is a pure
 * function of (arr, seed): re-running it during an unrelated parent re-render
 * (the 10s health poll) reproduces the SAME order rather than reshuffling the
 * deck under the user. A fresh order is produced only when the seed changes
 * (an explicit order pick) or the filtered set changes.
 */
function seededShuffle<T>(arr: T[], seed: number): T[] {
  const a = [...arr];
  let s = seed >>> 0;
  const rand = () => {
    s = (s + 0x6d2b79f5) | 0;
    let t = Math.imul(s ^ (s >>> 15), 1 | s);
    t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
  for (let i = a.length - 1; i > 0; i--) {
    const j = Math.floor(rand() * (i + 1));
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

export default function StudyMode({ questions, missedIds, onExit }: Props) {
  const [selectedTags, setSelectedTags] = useState<Set<string>>(new Set());
  const [selectedTypes, setSelectedTypes] = useState<Set<string>>(new Set());
  const [order, setOrder] = useState<OrderMode>("sequential");
  const [index, setIndex] = useState(0);
  const [flipped, setFlipped] = useState(false);
  const [showShortcuts, setShowShortcuts] = useState(false);
  const [missedOnly, setMissedOnly] = useState(false);
  // Seed for the shuffle. Held in state so the arrangement is stable across
  // re-renders; a fresh value (a new shuffle) is produced only when the user
  // picks an order in changeOrder.
  const [shuffleSeed, setShuffleSeed] = useState(() => (Math.random() * 2 ** 31) | 0);

  const hasMissed = (missedIds?.size ?? 0) > 0;

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

  // Deterministic filtering step (tags -> type -> missed-only). Kept separate
  // from ordering so the arrangement only changes when the *contents* change.
  const filtered = useMemo(() => {
    let f = filterByTags(questions, selectedTags);
    if (selectedTypes.size > 0) {
      f = f.filter((q) => selectedTypes.has(q.sectionType));
    }
    if (missedOnly && missedIds) {
      f = f.filter((q) => missedIds.has(q.id));
    }
    return f;
  }, [questions, selectedTags, selectedTypes, missedOnly, missedIds]);

  // Apply ordering. The shuffle is seeded, so this memo is a pure function of
  // (filtered, order, shuffleSeed) — a parent re-render can't reshuffle it, and
  // even if React drops the memoized value it recomputes to the same order. A
  // new arrangement happens only when the filtered set changes or the user
  // picks an order (which bumps shuffleSeed).
  const cards = useMemo(() => {
    switch (order) {
      case "sequential":
        return filtered;
      case "shuffle-within-type": {
        const tf = seededShuffle(filtered.filter((q) => q.sectionType === "true_false"), shuffleSeed);
        const mc = seededShuffle(filtered.filter((q) => q.sectionType === "multiple_choice"), shuffleSeed ^ 0x9e3779b9);
        const sa = seededShuffle(filtered.filter((q) => q.sectionType === "short_answer"), shuffleSeed ^ 0x85ebca6b);
        return [...tf, ...mc, ...sa];
      }
      case "shuffle-all":
        return seededShuffle(filtered, shuffleSeed);
    }
  }, [filtered, order, shuffleSeed]);

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
    // Re-seed so each explicit order pick yields a fresh arrangement (and
    // re-picking "Shuffled" reshuffles). Between picks the seed is stable, so
    // unrelated re-renders never change the order.
    setShuffleSeed((Math.random() * 2 ** 31) | 0);
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

  // Keyboard shortcuts: Space/Enter flip, ArrowLeft/Right prev/next.
  useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      if (showShortcuts) return;
      if (isTypingTarget(e.target)) return;
      switch (e.key) {
        case " ":
        case "Enter":
          e.preventDefault();
          flip();
          break;
        case "ArrowLeft":
          e.preventDefault();
          prev();
          break;
        case "ArrowRight":
          e.preventDefault();
          next();
          break;
      }
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [flip, prev, next, showShortcuts]);

  return (
    <div className="study">
      <div className="study-header">
        <button className="study-exit" onClick={onExit}>
          &#10005; Exit Study Mode
        </button>
        <div className="study-header-right">
          <span className="study-counter">
            {total > 0 ? `${index + 1} / ${total}` : "0 / 0"}
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

      <div className="study-body">
        {/* ── Left sidebar ── */}
        <div className="study-sidebar">
          {/* Missed last quiz (only when there's attempt data) */}
          {hasMissed && (
            <div className="study-sidebar-section">
              <button
                className={`study-missed-chip ${missedOnly ? "study-missed-chip--active" : ""}`}
                onClick={() => {
                  setMissedOnly((m) => !m);
                  resetPosition();
                }}
              >
                {missedOnly ? "✓ " : ""}Missed last quiz ({missedIds!.size})
              </button>
            </div>
          )}

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

      {showShortcuts && (
        <ShortcutsOverlay
          title="Study shortcuts"
          shortcuts={STUDY_SHORTCUTS}
          onClose={() => setShowShortcuts(false)}
        />
      )}
    </div>
  );
}