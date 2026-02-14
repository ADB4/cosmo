/** Modes the backend supports for LLM selection */
export type ModelMode = "qwen-7b" | "qwen-14b" | "llama" | "mistral";

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
  "qwen-7b":  { label: "qwen2.5-coder:7b",  description: "7B, best all-round" },
  "qwen-14b": { label: "qwen2.5-coder:14b", description: "14B, highest accuracy" },
  "llama":    { label: "llama3.1:8b",        description: "8B, general purpose" },
  "mistral":  { label: "mistral:7b",         description: "7B, good instruction following" },
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