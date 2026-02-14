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

export async function fetchQuizzes(): Promise<QuizSummary[]> {
  const res = await fetch(`${BASE}/quizzes`);
  if (!res.ok) throw new Error(await res.text());
  const data = await res.json();
  return data.quizzes;
}

export async function fetchQuiz(quizId: string): Promise<Quiz> {
  const res = await fetch(`${BASE}/quizzes/${encodeURIComponent(quizId)}`);
  if (!res.ok) {
    const body = await res.json().catch(() => ({ error: res.statusText }));
    throw new Error(body.error ?? "Quiz not found");
  }
  return res.json();
}

export async function ingestQuiz(
  file: File,
): Promise<{ status: string; filename: string; quiz_ids: string[]; total_questions: number }> {
  const form = new FormData();
  form.append("file", file);
  const res = await fetch(`${BASE}/quizzes/ingest`, { method: "POST", body: form });
  if (!res.ok) {
    const body = await res.json().catch(() => ({ error: res.statusText }));
    throw new Error(body.error ?? "Upload failed");
  }
  return res.json();
}

export async function ingestQuizPath(
  path: string,
): Promise<{ status: string; filename: string; quiz_ids: string[]; total_questions: number }> {
  const res = await fetch(`${BASE}/quizzes/ingest`, {
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
  mode = "quick",
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

export function streamChat(
  question: string,
  mode: ModelMode,
  nResults: number,
  callbacks: {
    onToken: (token: string) => void;
    onDone: () => void;
    onError: (err: string) => void;
  },
): AbortController {
  const controller = new AbortController();

  (async () => {
    try {
      const res = await fetch(`${BASE}/chat`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question, mode, n_results: nResults }),
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
      callbacks.onError(err instanceof Error ? err.message : String(err));
    }
  })();

  return controller;
}
