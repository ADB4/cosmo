import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";
import {
  fetchHealth,
  fetchStats,
  fetchQuizzes,
  fetchQuiz,
  clearHistory,
  ingestFile,
  evaluateAnswer,
  streamChat,
} from "../lib/api";

const mockFetch = vi.fn();

beforeEach(() => {
  vi.stubGlobal("fetch", mockFetch);
});

afterEach(() => {
  vi.restoreAllMocks();
});

function jsonResponse(body: unknown, status = 200) {
  return Promise.resolve({
    ok: status >= 200 && status < 300,
    status,
    statusText: status === 200 ? "OK" : "Error",
    json: () => Promise.resolve(body),
    text: () => Promise.resolve(JSON.stringify(body)),
  });
}

describe("fetchHealth", () => {
  it("returns health data on success", async () => {
    mockFetch.mockReturnValueOnce(
      jsonResponse({ status: "ok", total_chunks: 42, total_documents: 3 }),
    );

    const health = await fetchHealth();

    expect(mockFetch).toHaveBeenCalledWith("/api/health");
    expect(health.status).toBe("ok");
    expect(health.total_chunks).toBe(42);
  });
});

describe("fetchStats", () => {
  it("returns stats on success", async () => {
    const data = { total_chunks: 10, total_documents: 2, sources: {} };
    mockFetch.mockReturnValueOnce(jsonResponse(data));

    const stats = await fetchStats();

    expect(mockFetch).toHaveBeenCalledWith("/api/stats");
    expect(stats.total_chunks).toBe(10);
  });

  it("throws on non-ok response", async () => {
    mockFetch.mockReturnValueOnce(jsonResponse("Not found", 404));

    await expect(fetchStats()).rejects.toThrow();
  });
});

describe("fetchQuizzes", () => {
  it("extracts quizzes array from response", async () => {
    const quizzes = [
      { id: "q1", title: "Quiz 1", total_questions: 10 },
    ];
    mockFetch.mockReturnValueOnce(jsonResponse({ quizzes }));

    const result = await fetchQuizzes();

    expect(result).toEqual(quizzes);
  });
});

describe("fetchQuiz", () => {
  it("fetches quiz by ID with encoded path", async () => {
    const quiz = { id: "test", title: "Test Quiz", sections: [] };
    mockFetch.mockReturnValueOnce(jsonResponse(quiz));

    const result = await fetchQuiz("test");

    expect(mockFetch).toHaveBeenCalledWith("/api/quizzes/test");
    expect(result.title).toBe("Test Quiz");
  });

  it("throws with error message on failure", async () => {
    mockFetch.mockReturnValueOnce(
      jsonResponse({ error: "Quiz not found" }, 404),
    );

    await expect(fetchQuiz("missing")).rejects.toThrow("Quiz not found");
  });
});

describe("clearHistory", () => {
  it("sends POST to history/clear", async () => {
    mockFetch.mockReturnValueOnce(jsonResponse({ status: "ok" }));

    await clearHistory();

    expect(mockFetch).toHaveBeenCalledWith("/api/history/clear", {
      method: "POST",
    });
  });
});

describe("ingestFile", () => {
  it("uploads file via FormData", async () => {
    const file = new File(["content"], "test.pdf", { type: "application/pdf" });
    mockFetch.mockReturnValueOnce(
      jsonResponse({ status: "ok", filename: "test.pdf", chunks_indexed: 5 }),
    );

    const result = await ingestFile(file);

    expect(result.filename).toBe("test.pdf");
    expect(result.chunks_indexed).toBe(5);

    const [url, opts] = mockFetch.mock.calls[0]!;
    expect(url).toBe("/api/ingest");
    expect(opts.method).toBe("POST");
    expect(opts.body).toBeInstanceOf(FormData);
  });

  it("appends force query param when force=true", async () => {
    const file = new File(["x"], "a.pdf");
    mockFetch.mockReturnValueOnce(
      jsonResponse({ status: "ok", filename: "a.pdf", chunks_indexed: 1 }),
    );

    await ingestFile(file, true);

    expect(mockFetch.mock.calls[0]![0]).toBe("/api/ingest?force=true");
  });

  it("throws with server error message on failure", async () => {
    const file = new File(["x"], "bad.txt");
    mockFetch.mockReturnValueOnce(
      jsonResponse({ error: "Invalid file type" }, 400),
    );

    await expect(ingestFile(file)).rejects.toThrow("Invalid file type");
  });
});

describe("evaluateAnswer", () => {
  it("sends question, user answer, and model answer", async () => {
    mockFetch.mockReturnValueOnce(
      jsonResponse({ score: "correct", feedback: "Good answer." }),
    );

    const result = await evaluateAnswer(
      "What is TS?",
      "A typed JS superset",
      "TypeScript is a typed superset of JavaScript",
    );

    expect(result.score).toBe("correct");
    expect(result.feedback).toBe("Good answer.");

    const body = JSON.parse(mockFetch.mock.calls[0]![1].body);
    expect(body.question).toBe("What is TS?");
    expect(body.user_answer).toBe("A typed JS superset");
    expect(body.model_answer).toBe("TypeScript is a typed superset of JavaScript");
    expect(body.mode).toBe("qwen-7b");
  });
});

describe("streamChat", () => {
  it("calls onToken for each SSE token and onDone at the end", async () => {
    const tokens: string[] = [];
    let done = false;

    const encoder = new TextEncoder();
    const stream = new ReadableStream({
      start(controller) {
        controller.enqueue(encoder.encode('data: {"token":"Hello"}\n\n'));
        controller.enqueue(encoder.encode('data: {"token":" world"}\n\n'));
        controller.enqueue(encoder.encode("data: [DONE]\n\n"));
        controller.close();
      },
    });

    mockFetch.mockReturnValueOnce(
      Promise.resolve({ ok: true, body: stream }),
    );

    const controller = streamChat("test", "qwen-7b", 4, {
      onToken: (t) => tokens.push(t),
      onDone: () => { done = true; },
      onError: () => {},
    });

    // Wait for the async IIFE to finish
    await new Promise((r) => setTimeout(r, 50));

    expect(tokens).toEqual(["Hello", " world"]);
    expect(done).toBe(true);
    expect(controller).toBeInstanceOf(AbortController);
  });

  it("calls onError when response is not ok", async () => {
    let errorMsg = "";

    mockFetch.mockReturnValueOnce(
      Promise.resolve({
        ok: false,
        body: null,
        json: () => Promise.resolve({ error: "Server error" }),
      }),
    );

    streamChat("test", "qwen-7b", 4, {
      onToken: () => {},
      onDone: () => {},
      onError: (err) => { errorMsg = err; },
    });

    await new Promise((r) => setTimeout(r, 50));

    expect(errorMsg).toBe("Server error");
  });
});
