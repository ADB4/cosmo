import { useState, useEffect, useCallback, useRef, useMemo } from "react";
import type { ApolloView, QuizSummary, NormalizedQuestion, QuizPreset } from "../../lib/types";
import { fetchQuizzes, fetchQuiz, ingestQuiz } from "../../lib/api";
import { normalizeQuiz, filterBySection, sampleQuiz } from "../../lib/normalizeQuiz";
import StudyMode from "./StudyMode";
import QuizMode from "./QuizMode";

const PRESETS: (QuizPreset & { id: string })[] = [
  { id: "short",  label: "Short",  tf: 12, mc: 10, sa: 4 },
  { id: "medium", label: "Medium", tf: 20, mc: 16, sa: 6 },
  { id: "long",   label: "Long",   tf: 32, mc: 32, sa: 12 },
];

export default function Apollo() {
  const [view, setView] = useState<ApolloView>("select");
  const [quizzes, setQuizzes] = useState<QuizSummary[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [allQuestions, setAllQuestions] = useState<NormalizedQuestion[]>([]);
  const [quizTitle, setQuizTitle] = useState("");
  const [quizQuestions, setQuizQuestions] = useState<NormalizedQuestion[]>([]);

  const [tfCount, setTfCount] = useState(12);
  const [mcCount, setMcCount] = useState(10);
  const [saCount, setSaCount] = useState(4);

  const [uploading, setUploading] = useState(false);
  const [uploadMsg, setUploadMsg] = useState<string | null>(null);
  const fileRef = useRef<HTMLInputElement>(null);

  const available = useMemo(() => ({
    tf: filterBySection(allQuestions, "true_false").length,
    mc: filterBySection(allQuestions, "multiple_choice").length,
    sa: filterBySection(allQuestions, "short_answer").length,
  }), [allQuestions]);

  const loadQuizzes = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      setQuizzes(await fetchQuizzes());
    } catch (e) {
      setError(e instanceof Error ? e.message : "Failed to load quizzes");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => { loadQuizzes(); }, [loadQuizzes]);

  const handleSelectQuiz = useCallback(async (id: string) => {
    setSelectedId(id);
    try {
      const quiz = await fetchQuiz(id);
      setQuizTitle(quiz.title);
      const normalized = normalizeQuiz(quiz);
      setAllQuestions(normalized);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Failed to load quiz");
    }
  }, []);

  const handleUpload = useCallback(async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    setUploading(true);
    setUploadMsg(null);
    try {
      const result = await ingestQuiz(file);
      setUploadMsg(`Loaded ${result.total_questions} questions from ${result.filename}`);
      loadQuizzes();
    } catch (err) {
      setUploadMsg(`Error: ${err instanceof Error ? err.message : String(err)}`);
    } finally {
      setUploading(false);
      if (fileRef.current) fileRef.current.value = "";
    }
  }, [loadQuizzes]);

  const handleExit = useCallback(() => {
    setView("select");
    setQuizQuestions([]);
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

  // ---- Quiz mode ----
  if (view === "quiz" && quizQuestions.length > 0) {
    return <QuizMode title={quizTitle} questions={quizQuestions} onExit={handleExit} />;
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

  // ---- Select view ----
  const selected = quizzes.find((q) => q.id === selectedId);

  return (
    <div className="apollo-select">
      {loading ? (
        <p className="apollo-loading">Loading quizzes...</p>
      ) : error ? (
        <p className="apollo-error">{error}</p>
      ) : quizzes.length === 0 ? (
        <div className="apollo-empty">
          <p className="apollo-empty-text">
            No quizzes loaded yet. Upload a quiz JSON to get started.
          </p>
        </div>
      ) : (
        <>
          {!selectedId && (
            <div className="apollo-picker">
              <h2 className="apollo-title">Apollo</h2>
              <p className="apollo-desc">Choose a quiz to study or test</p>
              <div className="apollo-quiz-list">
                {quizzes.map((q) => (
                  <button key={q.id} className="apollo-quiz-item" onClick={() => handleSelectQuiz(q.id)}>
                    <span className="apollo-quiz-item-title">{q.title}</span>
                    <span className="apollo-quiz-item-meta">{q.total_questions} questions</span>
                  </button>
                ))}
              </div>
            </div>
          )}

          {selectedId && selected && (
            <div className="apollo-mode-select">
              <button className="apollo-back" onClick={() => setSelectedId(null)}>
                &#8249; Back
              </button>
              <div className="apollo-hero">
                <h2 className="apollo-title">{selected.title}</h2>
                {selected.scope && <p className="apollo-desc">{selected.scope}</p>}
                <p className="apollo-count">{selected.total_questions} questions</p>
              </div>

              <div className="apollo-cards">
                <button className="apollo-card" onClick={() => setView("study")}>
                  <svg className="apollo-card-icon" width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.2">
                    <path d="M2 3h6a4 4 0 0 1 4 4v14a3 3 0 0 0-3-3H2z" />
                    <path d="M22 3h-6a4 4 0 0 0-4 4v14a3 3 0 0 1 3-3h7z" />
                  </svg>
                  <span className="apollo-card-title">Study Mode</span>
                  <span className="apollo-card-desc">Review flashcards in random order</span>
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
            </div>
          )}
        </>
      )}

      <div className="apollo-upload-area">
        <label className={`apollo-upload-btn ${uploading ? "apollo-upload-btn--busy" : ""}`}>
          {uploading ? "Processing..." : "Upload Quiz JSON"}
          <input ref={fileRef} type="file" accept=".json" onChange={handleUpload} disabled={uploading} hidden />
        </label>
        {uploadMsg && (
          <span className={`apollo-upload-msg ${uploadMsg.startsWith("Error") ? "apollo-upload-msg--error" : ""}`}>
            {uploadMsg}
          </span>
        )}
      </div>
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
  return (
    <div className="quiz-slider">
      <div className="quiz-slider-header">
        <span className="quiz-slider-label">{label}</span>
        <span className="quiz-slider-value">
          {value} / {max}
        </span>
      </div>
      <input
        type="range"
        className="quiz-slider-input"
        min={0}
        max={max}
        value={value}
        onChange={(e) => onChange(Number(e.target.value))}
      />
    </div>
  );
}
