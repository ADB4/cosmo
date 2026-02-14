import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";
import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import ChatPanel from "../pages/chat/ChatPanel";

const mockFetch = vi.fn();

beforeEach(() => {
  vi.stubGlobal("fetch", mockFetch);
});

afterEach(() => {
  vi.restoreAllMocks();
});

describe("ChatPanel — initial state", () => {
  it("renders with initial system message", () => {
    render(<ChatPanel mode="qwen-7b" />);
    expect(
      screen.getByText(/Connected to Ollama/),
    ).toBeInTheDocument();
  });

  it("renders the text input and send button", () => {
    render(<ChatPanel mode="qwen-7b" />);
    expect(
      screen.getByPlaceholderText("Ask a question about the documentation..."),
    ).toBeInTheDocument();
    expect(screen.getByText("Send")).toBeInTheDocument();
  });

  it("disables Send when input is empty", () => {
    render(<ChatPanel mode="qwen-7b" />);
    expect(screen.getByText("Send").closest("button")).toBeDisabled();
  });

  it("does not show Clear button initially (only 1 message)", () => {
    render(<ChatPanel mode="qwen-7b" />);
    expect(screen.queryByText("Clear")).toBeNull();
  });
});

describe("ChatPanel — sending a message", () => {
  it("adds user message and enables streaming on send", async () => {
    const encoder = new TextEncoder();
    const stream = new ReadableStream({
      start(controller) {
        controller.enqueue(encoder.encode('data: {"token":"Hello"}\n\n'));
        controller.enqueue(encoder.encode("data: [DONE]\n\n"));
        controller.close();
      },
    });

    mockFetch.mockReturnValueOnce(
      Promise.resolve({ ok: true, body: stream }),
    );

    const user = userEvent.setup();
    render(<ChatPanel mode="qwen-7b" />);

    const input = screen.getByPlaceholderText(
      "Ask a question about the documentation...",
    );
    await user.type(input, "What is TypeScript?");
    await user.click(screen.getByText("Send"));

    // User message should appear
    expect(screen.getByText("What is TypeScript?")).toBeInTheDocument();

    // Wait for streaming to complete and assistant response to appear
    await waitFor(() => {
      expect(screen.getByText("Hello")).toBeInTheDocument();
    });
  });

  it("clears input after sending", async () => {
    const encoder = new TextEncoder();
    const stream = new ReadableStream({
      start(controller) {
        controller.enqueue(encoder.encode("data: [DONE]\n\n"));
        controller.close();
      },
    });

    mockFetch.mockReturnValueOnce(
      Promise.resolve({ ok: true, body: stream }),
    );

    const user = userEvent.setup();
    render(<ChatPanel mode="qwen-7b" />);

    const input = screen.getByPlaceholderText(
      "Ask a question about the documentation...",
    ) as HTMLTextAreaElement;
    await user.type(input, "Test question");
    await user.click(screen.getByText("Send"));

    expect(input.value).toBe("");
  });
});

describe("ChatPanel — clear history", () => {
  it("shows Clear button after sending a message and clears on click", async () => {
    const encoder = new TextEncoder();
    const stream = new ReadableStream({
      start(controller) {
        controller.enqueue(encoder.encode("data: [DONE]\n\n"));
        controller.close();
      },
    });

    // First call: chat stream. Second call: history/clear
    mockFetch
      .mockReturnValueOnce(Promise.resolve({ ok: true, body: stream }))
      .mockReturnValueOnce(
        Promise.resolve({ ok: true, json: () => Promise.resolve({}) }),
      );

    const user = userEvent.setup();
    render(<ChatPanel mode="qwen-7b" />);

    const input = screen.getByPlaceholderText(
      "Ask a question about the documentation...",
    );
    await user.type(input, "Hello");
    await user.click(screen.getByText("Send"));

    // Wait for stream to finish
    await waitFor(() => {
      expect(screen.getByText("Clear")).toBeInTheDocument();
    });

    await user.click(screen.getByText("Clear"));

    // Should reset to single system message
    expect(screen.getByText(/Chat cleared/)).toBeInTheDocument();
  });
});

describe("ChatPanel — keyboard shortcut", () => {
  it("sends on Enter (without Shift)", async () => {
    const encoder = new TextEncoder();
    const stream = new ReadableStream({
      start(controller) {
        controller.enqueue(encoder.encode("data: [DONE]\n\n"));
        controller.close();
      },
    });
    mockFetch.mockReturnValueOnce(
      Promise.resolve({ ok: true, body: stream }),
    );

    const user = userEvent.setup();
    render(<ChatPanel mode="qwen-7b" />);

    const input = screen.getByPlaceholderText(
      "Ask a question about the documentation...",
    );
    await user.type(input, "Hello{Enter}");

    // Message should be sent (input cleared)
    expect((input as HTMLTextAreaElement).value).toBe("");
  });
});
