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
   ============================================================ */

export type QuestionType = "tf" | "mc" | "sa";

export interface QuizQuestion {
  id: string;
  qtype: QuestionType;
  text: string;
  choices: string[];
  answer: string;          // "T", "F", "(b)", or free-text
  explanation: string;
}

export interface QuizData {
  title: string;
  description: string;
  questions: QuizQuestion[];
}

export type ApolloView = "select" | "study" | "quiz";