import { useState, useEffect, useCallback, useMemo } from "react";
import type { ApolloView, QuizSummary, NormalizedQuestion, QuizPreset, ModelMode } from "../../lib/types";
import { fetchQuizzes, fetchQuiz, fetchModules } from "../../lib/api";
import { normalizeQuiz, filterBySection, sampleQuiz } from "../../lib/normalizeQuiz";
import StudyMode from "./StudyMode";
import QuizMode from "./QuizMode";
import DebugMode from "./DebugMode";
import DeckControls from "./DeckControls";

const PRESETS: (QuizPreset & { id: string })[] = [
  { id: "short",  label: "Short",  tf: 12, mc: 10, sa: 4 },
  { id: "medium", label: "Medium", tf: 20, mc: 16, sa: 6 },
  { id: "long",   label: "Long",   tf: 32, mc: 32, sa: 12 },
];

/** Capitalize first letter of module name for display */
function formatModuleName(name: string): string {
  return name.charAt(0).toUpperCase() + name.slice(1);
}

interface ApolloProps {
  /** Currently selected model mode, used for AI short-answer grading. */
  mode: ModelMode;
}

export default function Apollo({ mode }: ApolloProps) {
  const [view, setView] = useState<ApolloView>("select");
  const [quizzes, setQuizzes] = useState<QuizSummary[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Module selection
  const [selectedModule, setSelectedModule] = useState<string | null>(null);

  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [allQuestions, setAllQuestions] = useState<NormalizedQuestion[]>([]);
  const [quizTitle, setQuizTitle] = useState("");
  const [quizQuestions, setQuizQuestions] = useState<NormalizedQuestion[]>([]);
  const [deckLoading, setDeckLoading] = useState(false);
  const [deckError, setDeckError] = useState<string | null>(null);

  const [tfCount, setTfCount] = useState(12);
  const [mcCount, setMcCount] = useState(10);
  const [saCount, setSaCount] = useState(4);

  // Modules that exist as folders on disk (may be empty of decks)
  const [diskModules, setDiskModules] = useState<string[]>([]);

  const available = useMemo(() => ({
    tf: filterBySection(allQuestions, "true_false").length,
    mc: filterBySection(allQuestions, "multiple_choice").length,
    sa: filterBySection(allQuestions, "short_answer").length,
  }), [allQuestions]);

  // When a deck loads, clamp the quiz-length counts to what's actually
  // available (the Short preset, capped) so a small deck never shows
  // "12 / 1" or "26 questions selected".
  useEffect(() => {
    if (allQuestions.length === 0) return;
    const short = PRESETS.find((p) => p.id === "short")!;
    setTfCount(Math.min(short.tf, available.tf));
    setMcCount(Math.min(short.mc, available.mc));
    setSaCount(Math.min(short.sa, available.sa));
  }, [available, allQuestions.length]);

  // Modules = folders on disk (from /api/modules) merged with modules
  // derived from quizzes, so empty folders still show with "0 decks".
  const modules = useMemo(() => {
    const moduleMap = new Map<string, { deckCount: number; questionCount: number }>();
    for (const m of diskModules) {
      if (!moduleMap.has(m)) moduleMap.set(m, { deckCount: 0, questionCount: 0 });
    }
    for (const q of quizzes) {
      const existing = moduleMap.get(q.module);
      if (existing) {
        existing.deckCount += 1;
        existing.questionCount += q.total_questions;
      } else {
        moduleMap.set(q.module, { deckCount: 1, questionCount: q.total_questions });
      }
    }
    return moduleMap;
  }, [quizzes, diskModules]);

  const moduleNames = useMemo(() => [...modules.keys()].sort(), [modules]);

  // Quizzes filtered to the selected module
  const moduleQuizzes = useMemo(() => {
    if (!selectedModule) return [];
    return quizzes.filter((q) => q.module === selectedModule);
  }, [quizzes, selectedModule]);

  const loadQuizzes = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const [qs, mods] = await Promise.all([
        fetchQuizzes(),
        fetchModules().catch(() => [] as string[]),
      ]);
      setQuizzes(qs);
      setDiskModules(mods);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Failed to load quizzes");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => { loadQuizzes(); }, [loadQuizzes]);

  const handleSelectQuiz = useCallback(async (module: string, id: string) => {
    setSelectedModule(module);
    setSelectedId(id);
    setAllQuestions([]);
    setDeckError(null);
    setDeckLoading(true);
    try {
      const quiz = await fetchQuiz(module, id);
      setQuizTitle(quiz.title);
      const normalized = normalizeQuiz(quiz);
      setAllQuestions(normalized);
    } catch (e) {
      setDeckError(e instanceof Error ? e.message : "Failed to load quiz");
    } finally {
      setDeckLoading(false);
    }
  }, []);

  const handleExit = useCallback(() => {
    setView("select");
    setQuizQuestions([]);
  }, []);

  const handleDebugSaved = useCallback(async (removedIds: Set<string>) => {
    setAllQuestions((prev) => prev.filter((q) => !removedIds.has(q.id)));
    loadQuizzes();
  }, [loadQuizzes]);

  const handleBackToModules = useCallback(() => {
    setSelectedModule(null);
    setSelectedId(null);
  }, []);

  const handleBackToQuizList = useCallback(() => {
    setSelectedId(null);
    setAllQuestions([]);
    setDeckError(null);
    setDeckLoading(false);
  }, []);

  const totalSelected = tfCount + mcCount + saCount;

  const applyPreset = (p: QuizPreset) => {
    setTfCount(Math.min(p.tf, available.tf));
    setMcCount(Math.min(p.mc, available.mc));
    setSaCount(Math.min(p.sa, available.sa));
  };

  const applyHalf = () => {
    setTfCount(Math.ceil(available.tf / 2));
    setMcCount(Math.ceil(available.mc / 2));
    setSaCount(Math.ceil(available.sa / 2));
  };

  const applyFull = () => {
    setTfCount(available.tf);
    setMcCount(available.mc);
    setSaCount(available.sa);
  };

  const startQuiz = () => {
    const sampled = sampleQuiz(allQuestions, { tf: tfCount, mc: mcCount, sa: saCount });
    setQuizQuestions(sampled);
    setView("quiz");
  };

  // ---- Study mode ----
  if (view === "study" && allQuestions.length > 0) {
    return <StudyMode title={quizTitle} questions={allQuestions} onExit={handleExit} />;
  }

  // ---- Debug mode ----
  if (view === "debug" && allQuestions.length > 0 && selectedId && selectedModule) {
    return (
      <DebugMode
        title={quizTitle}
        module={selectedModule}
        quizId={selectedId}
        fileName={
          quizzes.find((q) => q.id === selectedId && q.module === selectedModule)?.file ??
          `${selectedId}.json`
        }
        questions={allQuestions}
        onExit={handleExit}
        onSaved={handleDebugSaved}
      />
    );
  }

  // ---- Quiz mode ----
  if (view === "quiz" && quizQuestions.length > 0) {
    return <QuizMode title={quizTitle} questions={quizQuestions} mode={mode} onExit={handleExit} />;
  }

  // ---- Quiz config ----
  if (view === "quiz-config") {
    return (
      <div className="quiz-config">
        <div className="quiz-config-body">
          <button className="apollo-back" onClick={() => setView("select")}>
            &#8249; Back
          </button>
          <h3 className="quiz-config-title">Quiz Length</h3>
          <p className="quiz-config-subtitle">
            {available.tf + available.mc + available.sa} questions available
          </p>

          <div className="quiz-config-presets">
            {PRESETS.map((p) => (
              <button key={p.id} className="quiz-config-preset" onClick={() => applyPreset(p)}>
                <span className="preset-label">{p.label}</span>
                <span className="preset-detail">{p.tf} T/F, {p.mc} MC, {p.sa} SA</span>
              </button>
            ))}
            <button className="quiz-config-preset" onClick={applyHalf}>
              <span className="preset-label">Half</span>
              <span className="preset-detail">
                {Math.ceil(available.tf / 2)} T/F, {Math.ceil(available.mc / 2)} MC, {Math.ceil(available.sa / 2)} SA
              </span>
            </button>
            <button className="quiz-config-preset" onClick={applyFull}>
              <span className="preset-label">Full</span>
              <span className="preset-detail">
                {available.tf} T/F, {available.mc} MC, {available.sa} SA
              </span>
            </button>
          </div>

          <div className="quiz-config-sliders">
            <QuizSlider label="True / False" value={tfCount} max={available.tf} onChange={setTfCount} />
            <QuizSlider label="Multiple Choice" value={mcCount} max={available.mc} onChange={setMcCount} />
            <QuizSlider label="Short Answer" value={saCount} max={available.sa} onChange={setSaCount} />
          </div>

          <div className="quiz-config-footer">
            <span className="quiz-config-total">
              {totalSelected} question{totalSelected !== 1 ? "s" : ""} selected
            </span>
            <button className="quiz-config-start" onClick={startQuiz} disabled={totalSelected === 0}>
              Start Quiz
            </button>
          </div>
        </div>
      </div>
    );
  }

  // ---- Select view (module picker -> quiz list -> mode picker) ----
  const selected = quizzes.find(
    (q) => q.id === selectedId && q.module === selectedModule,
  );

  return (
    <div className="apollo-select">
      {loading ? (
        <p className="apollo-loading">Loading quizzes...</p>
      ) : error ? (
        <p className="apollo-error">{error}</p>
      ) : modules.size === 0 ? (
        <div className="apollo-picker">
          <h2 className="apollo-title">Apollo</h2>
          <p className="apollo-desc">
            No modules yet. Create one, then upload a deck JSON to get started.
          </p>
          <DeckControls existingModules={moduleNames} onChanged={loadQuizzes} />
        </div>
      ) : (
        <>
          {/* ── Module picker ── */}
          {!selectedModule && (
            <div className="apollo-picker">
              <h2 className="apollo-title">Apollo</h2>
              <p className="apollo-desc">Choose a module</p>
              <div className="apollo-module-list">
                {[...modules.entries()].map(([name, info]) => (
                  <button
                    key={name}
                    className="apollo-module-item"
                    onClick={() => setSelectedModule(name)}
                  >
                    <span className="apollo-module-item-title">{formatModuleName(name)}</span>
                    <span className="apollo-module-item-meta">
                      {info.deckCount} deck{info.deckCount !== 1 ? "s" : ""} &middot; {info.questionCount} questions
                    </span>
                  </button>
                ))}
              </div>
              <DeckControls existingModules={moduleNames} onChanged={loadQuizzes} />
            </div>
          )}

          {/* ── Quiz list (within selected module) ── */}
          {selectedModule && !selectedId && (
            <div className="apollo-picker">
              <button className="apollo-back" onClick={handleBackToModules}>
                &#8249; All Modules
              </button>
              <h2 className="apollo-title">{formatModuleName(selectedModule)}</h2>
              <p className="apollo-desc">Choose a deck to study or test</p>
              {moduleQuizzes.length === 0 ? (
                <p className="apollo-count">No decks in this module yet — upload one below.</p>
              ) : (
                <div className="apollo-quiz-list">
                  {moduleQuizzes.map((q) => (
                    <button key={q.id} className="apollo-quiz-item" onClick={() => handleSelectQuiz(q.module, q.id)}>
                      <span className="apollo-quiz-item-title">{q.title}</span>
                      <span className="apollo-quiz-item-meta">{q.total_questions} questions</span>
                    </button>
                  ))}
                </div>
              )}
              <DeckControls
                existingModules={moduleNames}
                onChanged={loadQuizzes}
                initialModule={selectedModule}
              />
            </div>
          )}

          {/* ── Mode picker (after selecting a quiz) ── */}
          {selectedId && selected && (
            <div className="apollo-mode-select">
              <button className="apollo-back" onClick={handleBackToQuizList}>
                &#8249; Back
              </button>
              <div className="apollo-hero">
                <h2 className="apollo-title">{selected.title}</h2>
                {selected.scope && <p className="apollo-desc">{selected.scope}</p>}
                <p className="apollo-count">{selected.total_questions} questions</p>
              </div>

              {deckError ? (
                <p className="apollo-error">{deckError}</p>
              ) : deckLoading || allQuestions.length === 0 ? (
                <p className="apollo-loading">Loading deck...</p>
              ) : (
                <>
                  <div className="apollo-cards apollo-cards--two">
                    <button className="apollo-card" onClick={() => setView("study")}>
                      <svg className="apollo-card-icon" width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.2">
                        <path d="M2 3h6a4 4 0 0 1 4 4v14a3 3 0 0 0-3-3H2z" />
                        <path d="M22 3h-6a4 4 0 0 0-4 4v14a3 3 0 0 1 3-3h7z" />
                      </svg>
                      <span className="apollo-card-title">Study Mode</span>
                      <span className="apollo-card-desc">Flip through flashcards in order</span>
                    </button>

                    <button className="apollo-card" onClick={() => setView("quiz-config")}>
                      <svg className="apollo-card-icon" width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.2">
                        <path d="M6 9H4.5a2.5 2.5 0 0 1 0-5C5.88 4 7 5.12 7 6.5V9" />
                        <path d="M18 9h1.5a2.5 2.5 0 0 0 0-5C18.12 4 17 5.12 17 6.5V9" />
                        <path d="M4 22h16" />
                        <path d="M10 14.66V17c0 .55-.47.98-.97 1.21C7.85 18.75 7 20 7 22" />
                        <path d="M14 14.66V17c0 .55.47.98.97 1.21C16.15 18.75 17 20 17 22" />
                        <path d="M18 2H6v7a6 6 0 0 0 12 0V2Z" />
                      </svg>
                      <span className="apollo-card-title">Quiz Mode</span>
                      <span className="apollo-card-desc">Test yourself and get scored</span>
                    </button>
                  </div>

                  <button className="apollo-edit-link" onClick={() => setView("debug")}>
                    &#9998; Edit deck (review &amp; remove questions)
                  </button>
                </>
              )}
            </div>
          )}
        </>
      )}
    </div>
  );
}

// ---- Slider sub-component ----

function QuizSlider({
  label,
  value,
  max,
  onChange,
}: {
  label: string;
  value: number;
  max: number;
  onChange: (n: number) => void;
}) {
  const shown = Math.min(value, max);
  return (
    <div className="quiz-slider">
      <div className="quiz-slider-header">
        <span className="quiz-slider-label">{label}</span>
        <span className="quiz-slider-value">
          {shown} / {max}
        </span>
      </div>
      <input
        type="range"
        className="quiz-slider-input"
        min={0}
        max={max}
        value={shown}
        onChange={(e) => onChange(Number(e.target.value))}
        disabled={max === 0}
      />
    </div>
  );
}