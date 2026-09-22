/** Modes the backend supports for LLM selection */
export type ModelMode = "qwen3-coder-30b" | "qwen3.6-27b" | "gpt-oss-20b" | "gemma4-12b";

/** A single message in the chat history (client-side) */
export interface ChatMessage {
  id: string;
  role: "user" | "assistant" | "system";
  content: string;
  mode?: ModelMode;
  timestamp: number;
  /** The originating question (on assistant messages) — used to retry / re-ask broadly */
  question?: string;
  /** Grounded search returned nothing relevant; render the "no docs" state + Ask broadly */
  noResults?: boolean;
  /** Stream failed; render an error block with a Retry button instead of an answer */
  error?: string;
  /** Stream was stopped/interrupted before completing; render a note + Retry and
   *  never treat the partial content as a finished answer. */
  truncated?: boolean;
}

/** Stats returned by /api/stats */
export interface KBStats {
  total_chunks: number;
  total_documents: number;
  sources: Record<string, { type: string; chunks: number }>;
}

/** Health response */
export interface HealthResponse {
  status: "ok" | "error";
  message?: string;
  total_chunks?: number;
  total_documents?: number;
}

/** Ingest response for a single file */
export interface IngestResponse {
  status: string;
  filename: string;
  chunks_indexed: number;
}

/** Describes model modes for display */
export const MODE_INFO: Record<ModelMode, { label: string; description: string }> = {
  "qwen3-coder-30b": { label: "qwen3-coder:30b · fast default", description: "MoE, ~19 GB — fast default" },
  "qwen3.6-27b":     { label: "qwen3.6:27b · deep",             description: "Dense quality mode — slow, deep" },
  "gpt-oss-20b":     { label: "gpt-oss:20b · reasoning",        description: "MoE reasoning, ~13 GB" },
  "gemma4-12b":      { label: "gemma4:12b · explanations",      description: "~8 GB — general explanations" },
};

/* ============================================================
   Apollo — Quiz / Study types
   ============================================================ */

export type SectionType = "true_false" | "multiple_choice" | "short_answer";

export interface TFQuestion {
  id: string;
  question: string;
  answer: boolean;
  explanation: string;
  tags?: string[];
}

export interface MCQuestion {
  id: string;
  question: string;
  code?: string;
  options: string[];
  answer: number;
  explanation: string;
  tags?: string[];
}

export interface SAQuestion {
  id: string;
  question: string;
  model_answer: string;
  tags?: string[];
}

export interface QuizSection {
  type: SectionType;
  title: string;
  questions: TFQuestion[] | MCQuestion[] | SAQuestion[];
}

export interface Quiz {
  id: string;
  title: string;
  scope: string;
  readings: string[];
  scoring_note: string;
  sections: QuizSection[];
}

export interface QuizSummary {
  file: string;
  id: string;
  title: string;
  scope: string;
  module: string;
  /** Optional explicit sort key from the quiz JSON; falls back to filename. */
  order?: number | null;
  total_questions: number;
  sections: { type: SectionType; count: number }[];
}

export interface NormalizedQuestion {
  id: string;
  sectionType: SectionType;
  text: string;
  code?: string;
  options: string[];
  correctAnswer: string;
  explanation: string;
  tags: string[];
}

export type ApolloView = "select" | "study" | "quiz-config" | "quiz" | "debug";

export interface QuizPreset {
  label: string;
  tf: number;
  mc: number;
  sa: number;
}