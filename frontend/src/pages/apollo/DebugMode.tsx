import { useState, useMemo, useCallback } from "react";
import type { NormalizedQuestion } from "../../lib/types";
import { filterByTags, collectTags, TAG_CATEGORIES } from "../../lib/normalizeQuiz";
import { deleteQuestions } from "../../lib/api";
import { renderMarkdown } from "../../components/renderMarkdown";

interface Props {
  title: string;
  quizId: string;
  questions: NormalizedQuestion[];
  onExit: () => void;
  /** Called after a successful save so Apollo can refresh its data */
  onSaved: (remainingIds: Set<string>) => void;
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

function formatTag(tag: string): string {
  return tag.replace(/-/g, " ");
}

export default function DebugMode({ title, quizId, questions, onExit, onSaved }: Props) {
  const [selectedTags, setSelectedTags] = useState<Set<string>>(new Set());
  const [filterOpen, setFilterOpen] = useState(false);
  const [index, setIndex] = useState(0);
  const [flipped, setFlipped] = useState(false);

  // IDs marked for removal (not yet persisted)
  const [markedForRemoval, setMarkedForRemoval] = useState<Set<string>>(new Set());
  const [saving, setSaving] = useState(false);
  const [saveMsg, setSaveMsg] = useState<string | null>(null);

  const availableTags = useMemo(() => collectTags(questions), [questions]);

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

  // Cards: filtered by tags, NOT shuffled (stable order for debug), excluding already-marked
  const cards = useMemo(() => {
    const tagged = filterByTags(questions, selectedTags);
    return tagged.filter((q) => !markedForRemoval.has(q.id));
  }, [questions, selectedTags, markedForRemoval]);

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

  const markRemove = useCallback(() => {
    if (!card) return;
    setMarkedForRemoval((prev) => {
      const next = new Set(prev);
      next.add(card.id);
      return next;
    });
    setSaveMsg(null);
    // After removing, stay at same index (next card slides in) or clamp
    setFlipped(false);
    setIndex((i) => {
      const newTotal = total - 1;
      if (newTotal === 0) return 0;
      return Math.min(i, newTotal - 1);
    });
  }, [card, total]);

  const undoRemove = useCallback((id: string) => {
    setMarkedForRemoval((prev) => {
      const next = new Set(prev);
      next.delete(id);
      return next;
    });
    setSaveMsg(null);
  }, []);

  const handleSave = useCallback(async () => {
    if (markedForRemoval.size === 0) return;
    setSaving(true);
    setSaveMsg(null);
    try {
      const result = await deleteQuestions(quizId, [...markedForRemoval]);
      setSaveMsg(`Removed ${result.removed.length} question${result.removed.length !== 1 ? "s" : ""}. ${result.remaining} remaining in file.`);
      // Notify parent so it can refresh
      onSaved(markedForRemoval);
      setMarkedForRemoval(new Set());
    } catch (err) {
      setSaveMsg(`Error: ${err instanceof Error ? err.message : String(err)}`);
    } finally {
      setSaving(false);
    }
  }, [quizId, markedForRemoval, onSaved]);

  const markedList = useMemo(
    () => questions.filter((q) => markedForRemoval.has(q.id)),
    [questions, markedForRemoval],
  );

  return (
    <div className="study">
      <div className="study-header">
        <button className="study-exit" onClick={onExit}>
          &#10005; Exit Debug Mode
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
                <span className="study-card-label">
                  <span className="debug-id">{card.id}</span> — {card.sectionType.replace(/_/g, " ").toUpperCase()}
                </span>
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
                <span className="study-card-label">ANSWER — {card.id}</span>
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
              {markedForRemoval.size > 0
                ? "All visible cards marked for removal."
                : "No questions match the selected tags."}
            </div>
          </div>
        )}
      </div>

      {/* Navigation + Remove button */}
      <div className="study-nav">
        <button className="study-nav-btn" onClick={prev} disabled={!card || index === 0}>
          &#8249; Previous
        </button>
        <button
          className="study-nav-btn debug-remove-btn"
          onClick={markRemove}
          disabled={!card}
          title="Mark this question for removal"
        >
          &#10005; Remove
        </button>
        <button className="study-nav-btn" onClick={next} disabled={!card || index === total - 1}>
          Next &#8250;
        </button>
      </div>

      {/* Removal queue + Save JSON */}
      {markedForRemoval.size > 0 && (
        <div className="debug-queue">
          <div className="debug-queue-header">
            <span className="debug-queue-title">
              {markedForRemoval.size} question{markedForRemoval.size !== 1 ? "s" : ""} marked for removal
            </span>
            <button
              className="debug-save-btn"
              onClick={handleSave}
              disabled={saving}
            >
              {saving ? "Saving..." : "Save JSON"}
            </button>
          </div>
          <div className="debug-queue-list">
            {markedList.map((q) => (
              <div key={q.id} className="debug-queue-item">
                <span className="debug-queue-item-id">{q.id}</span>
                <span className="debug-queue-item-text">
                  {q.text.length > 80 ? q.text.slice(0, 80) + "..." : q.text}
                </span>
                <button
                  className="debug-queue-undo"
                  onClick={() => undoRemove(q.id)}
                  title="Undo removal"
                >
                  undo
                </button>
              </div>
            ))}
          </div>
          {saveMsg && (
            <div className={`debug-save-msg ${saveMsg.startsWith("Error") ? "debug-save-msg--error" : ""}`}>
              {saveMsg}
            </div>
          )}
        </div>
      )}
    </div>
  );
}