/** Modes the backend supports for LLM selection */
export type ModelMode = "quick" | "deep" | "general" | "fast";

/** A single message in the chat history (client-side) */
export interface ChatMessage {
  id: string;
  role: "user" | "assistant";
  content: string;
  mode?: ModelMode;
  timestamp: number;
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
  quick: { label: "Quick — qwen2.5-coder:7b", description: "fast, good quality" },
  deep: { label: "Deep — qwen2.5-coder:14b", description: "slower, best quality" },
  general: { label: "General — llama3.1:8b", description: "non-code topics" },
  fast: { label: "Fast — mistral:7b", description: "fastest responses" },
};

/* ============================================================
   Apollo — Quiz / Study types
   Mirrors the quizzes.json schema from the backend
   ============================================================ */

export type SectionType = "true_false" | "multiple_choice" | "short_answer";

/** A single T/F question from the JSON */
export interface TFQuestion {
  id: string;
  question: string;
  answer: boolean;
  explanation: string;
}

/** A single MC question from the JSON */
export interface MCQuestion {
  id: string;
  question: string;
  code?: string;
  options: string[];
  answer: number; // 0-3
  explanation: string;
}

/** A single SA question from the JSON */
export interface SAQuestion {
  id: string;
  question: string;
  model_answer: string;
}

/** A section within a quiz */
export interface QuizSection {
  type: SectionType;
  title: string;
  questions: TFQuestion[] | MCQuestion[] | SAQuestion[];
}

/** Full quiz object returned by GET /api/quizzes/:id */
export interface Quiz {
  id: string;
  title: string;
  scope: string;
  readings: string[];
  scoring_note: string;
  sections: QuizSection[];
}

/** Summary returned by GET /api/quizzes (list) */
export interface QuizSummary {
  file: string;
  id: string;
  title: string;
  scope: string;
  total_questions: number;
  sections: { type: SectionType; count: number }[];
}

/**
 * Normalized question used by Study and Quiz mode components.
 * Flattened from the section-based JSON structure so components
 * can iterate a single array.
 */
export interface NormalizedQuestion {
  id: string;
  sectionType: SectionType;
  text: string;
  code?: string;
  options: string[];        // empty for T/F and SA
  correctAnswer: string;    // "true"/"false", option index as string, or model answer
  explanation: string;
}

export type ApolloView = "select" | "study" | "quiz-config" | "quiz";

/** Quiz length preset */
export interface QuizPreset {
  label: string;
  tf: number;
  mc: number;
  sa: number;
}