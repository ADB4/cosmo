import type { HealthResponse, KBStats, IngestResponse, ModelMode } from "./types";

const BASE = "/api";

/** Check backend health */
export async function fetchHealth(): Promise<HealthResponse> {
  const res = await fetch(`${BASE}/health`);
  return res.json();
}

/** Get knowledge-base stats */
export async function fetchStats(): Promise<KBStats> {
  const res = await fetch(`${BASE}/stats`);
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}

/** Upload and ingest a single file */
export async function ingestFile(
  file: File,
  force = false,
): Promise<IngestResponse> {
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

/** Ingest all files from a local directory on the server */
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

/** Clear server-side conversation history */
export async function clearHistory(): Promise<void> {
  await fetch(`${BASE}/history/clear`, { method: "POST" });
}

/**
 * Send a question and receive streamed tokens via SSE.
 *
 * Returns an AbortController so the caller can cancel, and calls
 * onToken for each incoming token string, onDone when finished,
 * and onError on failure.
 */
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
        body: JSON.stringify({
          question,
          mode,
          n_results: nResults,
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
        // Keep the last partial line in the buffer
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
