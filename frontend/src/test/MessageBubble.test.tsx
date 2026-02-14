import { describe, it, expect } from "vitest";
import { render, screen } from "@testing-library/react";
import MessageBubble from "../pages/chat/MessageBubble";
import type { ChatMessage } from "../lib/types";

function msg(overrides: Partial<ChatMessage> = {}): ChatMessage {
  return {
    id: "test-msg",
    role: "user",
    content: "Hello",
    timestamp: 1700000000000,
    ...overrides,
  };
}

describe("MessageBubble", () => {
  it("renders user messages with the user class and prefix", () => {
    render(<MessageBubble message={msg({ content: "My question" })} />);
    const el = document.querySelector(".message--user");
    expect(el).not.toBeNull();
    expect(screen.getByText(">")).toBeInTheDocument();
    expect(screen.getByText("My question")).toBeInTheDocument();
  });

  it("renders assistant messages with assistant class and cosmo prefix", () => {
    render(
      <MessageBubble
        message={msg({ role: "assistant", content: "My answer", mode: "qwen-7b" })}
      />,
    );
    const el = document.querySelector(".message--assistant");
    expect(el).not.toBeNull();
    expect(screen.getByText("cosmo")).toBeInTheDocument();
  });

  it("renders system messages for 'Connected to Ollama' content", () => {
    render(
      <MessageBubble
        message={msg({ content: "Connected to Ollama. Ready." })}
      />,
    );
    expect(document.querySelector(".message--system")).not.toBeNull();
    expect(screen.getByText("# system")).toBeInTheDocument();
  });

  it("shows mode tag on assistant messages", () => {
    render(
      <MessageBubble
        message={msg({ role: "assistant", content: "response", mode: "qwen-14b" })}
      />,
    );
    expect(screen.getByText("qwen-14b")).toBeInTheDocument();
  });

  it("does not show mode tag on user messages", () => {
    render(
      <MessageBubble message={msg({ content: "question", mode: "qwen-7b" })} />,
    );
    expect(document.querySelector(".msg-mode-tag")).toBeNull();
  });

  it("renders a formatted timestamp", () => {
    render(<MessageBubble message={msg({ timestamp: 1700000000000 })} />);
    // Just verify a timestamp element is present (locale-dependent)
    expect(document.querySelector(".msg-timestamp")).not.toBeNull();
  });
});
