import type { HealthResponse, KBStats, IngestResponse, ModelMode, QuizSummary, Quiz } from "./types";

const BASE = "/api";

export async function fetchHealth(): Promise<HealthResponse> {
  const res = await fetch(`${BASE}/health`);
  return res.json();
}

export async function fetchStats(): Promise<KBStats> {
  const res = await fetch(`${BASE}/stats`);
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}

export async function ingestFile(file: File, force = false): Promise<IngestResponse> {
  const form = new FormData();
  form.append("file", file);
  const url = force ? `${BASE}/ingest?force=true` : `${BASE}/ingest`;
  const res = await fetch(url, { method: "POST", body: form });
  if (!res.ok) {
    const body = await res.json().catch(() => ({ error: res.statusText }));
    throw new Error(body.error ?? "Upload failed");
  }
  return res.json();
}

export async function ingestDirectory(
  path: string,
  force = false,
): Promise<{ status: string; files: Array<{ file: string; chunks?: number; error?: string }> }> {
  const res = await fetch(`${BASE}/ingest/directory`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ path, force }),
  });
  if (!res.ok) {
    const body = await res.json().catch(() => ({ error: res.statusText }));
    throw new Error(body.error ?? "Ingest failed");
  }
  return res.json();
}

export async function clearHistory(): Promise<void> {
  await fetch(`${BASE}/history/clear`, { method: "POST" });
}

/** Mode keys whose underlying Ollama model is installed. Empty array if
 *  the endpoint is unavailable (caller should fall back to all modes). */
export async function fetchInstalledModes(): Promise<string[]> {
  try {
    const res = await fetch(`${BASE}/models`);
    if (!res.ok) return [];
    const data = await res.json();
    return (data.modes as { mode: string }[]).map((m) => m.mode);
  } catch {
    return [];
  }
}

export async function fetchModules(): Promise<string[]> {
  const res = await fetch(`${BASE}/modules`);
  if (!res.ok) throw new Error(await res.text());
  const data = await res.json();
  return data.modules;
}

export async function createModule(name: string): Promise<{ status: string; module: string }> {
  const res = await fetch(`${BASE}/modules`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ name }),
  });
  if (!res.ok) {
    const body = await res.json().catch(() => ({ error: res.statusText }));
    throw new Error(body.error ?? "Could not create module");
  }
  return res.json();
}

export async function fetchQuizzes(): Promise<QuizSummary[]> {
  const res = await fetch(`${BASE}/quizzes`);
  if (!res.ok) throw new Error(await res.text());
  const data = await res.json();
  // Sort by an optional numeric `order` field, then by filename. Quizzes
  // without an `order` sort after those that have one. (No more parsing
  // "Week N" out of the title, which mis-sorted "Unit 1" and "Weeks 5–6".)
  return (data.quizzes as QuizSummary[]).sort((a, b) => {
    const oa = a.order ?? Number.POSITIVE_INFINITY;
    const ob = b.order ?? Number.POSITIVE_INFINITY;
    if (oa !== ob) return oa - ob;
    return a.file.localeCompare(b.file, undefined, { numeric: true });
  });
}

export async function fetchQuiz(module: string, quizId: string): Promise<Quiz> {
  const res = await fetch(
    `${BASE}/quizzes/${encodeURIComponent(module)}/${encodeURIComponent(quizId)}`,
  );
  if (!res.ok) {
    const body = await res.json().catch(() => ({ error: res.statusText }));
    throw new Error(body.error ?? "Quiz not found");
  }
  return res.json();
}

export async function ingestQuiz(
  file: File,
  module: string,
): Promise<{ status: string; filename: string; module: string; quiz_ids: string[]; total_questions: number }> {
  const form = new FormData();
  form.append("file", file);
  const res = await fetch(`${BASE}/quizzes/ingest?module=${encodeURIComponent(module)}`, {
    method: "POST",
    body: form,
  });
  if (!res.ok) {
    const body = await res.json().catch(() => ({ error: res.statusText }));
    throw new Error(body.error ?? "Upload failed");
  }
  return res.json();
}

export async function ingestQuizPath(
  path: string,
  module: string,
): Promise<{ status: string; filename: string; module: string; quiz_ids: string[]; total_questions: number }> {
  const res = await fetch(`${BASE}/quizzes/ingest?module=${encodeURIComponent(module)}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ path }),
  });
  if (!res.ok) {
    const body = await res.json().catch(() => ({ error: res.statusText }));
    throw new Error(body.error ?? "Ingest failed");
  }
  return res.json();
}

export async function evaluateAnswer(
  question: string,
  userAnswer: string,
  modelAnswer: string,
  mode = "qwen-7b",
): Promise<{ score: "correct" | "partial" | "incorrect"; feedback: string }> {
  const res = await fetch(`${BASE}/quizzes/evaluate`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ question, user_answer: userAnswer, model_answer: modelAnswer, mode }),
  });
  if (!res.ok) {
    const body = await res.json().catch(() => ({ error: res.statusText }));
    throw new Error(body.error ?? "Evaluation failed");
  }
  return res.json();
}

export async function deleteQuestions(
  module: string,
  quizId: string,
  questionIds: string[],
): Promise<{ status: string; removed: string[]; remaining: number }> {
  const res = await fetch(
    `${BASE}/quizzes/${encodeURIComponent(module)}/${encodeURIComponent(quizId)}/questions`,
    {
      method: "DELETE",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ question_ids: questionIds }),
    },
  );
  if (!res.ok) {
    const body = await res.json().catch(() => ({ error: res.statusText }));
    throw new Error(body.error ?? "Delete failed");
  }
  return res.json();
}

/**
 * Send a question and receive streamed tokens via SSE.
 *
 * @param grounded - If true, answers strictly from docs. If false,
 *   the LLM supplements with its own knowledge when docs are insufficient.
 */
export function streamChat(
  question: string,
  mode: ModelMode,
  nResults: number,
  grounded: boolean,
  callbacks: {
    onToken: (token: string) => void;
    onDone: () => void;
    onError: (err: string) => void;
    /** Grounded mode found nothing above the relevance cutoff. */
    onNoResults?: () => void;
  },
): AbortController {
  const controller = new AbortController();

  (async () => {
    try {
      const res = await fetch(`${BASE}/chat`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          question,
          mode,
          n_results: nResults,
          grounded,
        }),
        signal: controller.signal,
      });

      if (!res.ok || !res.body) {
        const body = await res.json().catch(() => ({ error: res.statusText }));
        callbacks.onError(body.error ?? "Request failed");
        return;
      }

      const reader = res.body.getReader();
      const decoder = new TextDecoder();
      let buffer = "";

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split("\n");
        buffer = lines.pop() ?? "";

        for (const line of lines) {
          const trimmed = line.trim();
          if (!trimmed.startsWith("data: ")) continue;
          const payload = trimmed.slice(6);
          if (payload === "[DONE]") {
            callbacks.onDone();
            return;
          }
          try {
            const parsed = JSON.parse(payload);
            if (parsed.error) {
              callbacks.onError(parsed.error);
              return;
            }
            if (parsed.no_results) {
              callbacks.onNoResults?.();
              continue;
            }
            if (parsed.token != null) {
              callbacks.onToken(parsed.token);
            }
          } catch {
            // ignore malformed JSON
          }
        }
      }

      callbacks.onDone();
    } catch (err: unknown) {
      if (err instanceof DOMException && err.name === "AbortError") return;
      callbacks.onError(err instanceof Error ? err.message : "Unknown error");
    }
  })();

  return controller;
}