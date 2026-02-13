import { useState, useRef, useEffect, useCallback } from "react";
import type { ChatMessage, ModelMode } from "./types";
import { streamChat, clearHistory } from "./api";
import MessageBubble from "./MessageBubble";

interface ChatPanelProps {
  mode: ModelMode;
}

let nextId = 0;
function uid(): string {
  return `msg_${Date.now()}_${nextId++}`;
}

export default function ChatPanel({ mode }: ChatPanelProps) {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState("");
  const [streaming, setStreaming] = useState(false);
  const abortRef = useRef<AbortController | null>(null);
  const bottomRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLTextAreaElement>(null);

  // Auto-scroll to bottom when messages change
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  // Focus input on mount
  useEffect(() => {
    inputRef.current?.focus();
  }, []);

  const handleSend = useCallback(() => {
    const q = input.trim();
    if (!q || streaming) return;

    const userMsg: ChatMessage = {
      id: uid(),
      role: "user",
      content: q,
      mode,
      timestamp: Date.now(),
    };

    const assistantMsg: ChatMessage = {
      id: uid(),
      role: "assistant",
      content: "",
      mode,
      timestamp: Date.now(),
    };

    setMessages((prev) => [...prev, userMsg, assistantMsg]);
    setInput("");
    setStreaming(true);

    const assistantId = assistantMsg.id;

    abortRef.current = streamChat(q, mode, 4, {
      onToken: (token) => {
        setMessages((prev) =>
          prev.map((m) =>
            m.id === assistantId ? { ...m, content: m.content + token } : m,
          ),
        );
      },
      onDone: () => {
        setStreaming(false);
        inputRef.current?.focus();
      },
      onError: (err) => {
        setMessages((prev) =>
          prev.map((m) =>
            m.id === assistantId
              ? { ...m, content: m.content + `\n\n[Error: ${err}]` }
              : m,
          ),
        );
        setStreaming(false);
      },
    });
  }, [input, mode, streaming]);

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const handleStop = () => {
    abortRef.current?.abort();
    setStreaming(false);
  };

  const handleClear = async () => {
    if (streaming) handleStop();
    setMessages([]);
    await clearHistory();
  };

  const isEmpty = messages.length === 0;

  return (
    <div className="chat-panel">
      {/* Message area */}
      <div className="chat-messages">
        {isEmpty && (
          <div className="chat-empty">
            <div className="chat-empty-orb" />
            <h2>cosmo</h2>
            <p>
              Ask anything about your indexed React, TypeScript, and MUI
              documentation.
            </p>
            <div className="chat-empty-hints">
              <button onClick={() => setInput("What are TypeScript generics?")}>
                What are TypeScript generics?
              </button>
              <button onClick={() => setInput("Explain discriminated unions with examples")}>
                Explain discriminated unions
              </button>
              <button onClick={() => setInput("How do I type React component props?")}>
                Typing React props
              </button>
            </div>
          </div>
        )}

        {messages.map((msg) => (
          <MessageBubble key={msg.id} message={msg} />
        ))}

        {streaming && (
          <div className="chat-streaming-indicator">
            <span className="dot" />
            <span className="dot" />
            <span className="dot" />
          </div>
        )}

        <div ref={bottomRef} />
      </div>

      {/* Input bar */}
      <div className="chat-input-bar">
        {messages.length > 0 && (
          <button className="clear-btn" onClick={handleClear} title="Clear chat">
            <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
              <path d="M2 4h12M5.33 4V2.67a1.33 1.33 0 011.34-1.34h2.66a1.33 1.33 0 011.34 1.34V4m2 0v9.33a1.33 1.33 0 01-1.34 1.34H4.67a1.33 1.33 0 01-1.34-1.34V4h9.34z" stroke="currentColor" strokeWidth="1.2" strokeLinecap="round" strokeLinejoin="round"/>
            </svg>
          </button>
        )}

        <div className="chat-input-wrap">
          <textarea
            ref={inputRef}
            className="chat-input"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Ask a question... (Enter to send, Shift+Enter for newline)"
            rows={1}
            disabled={streaming}
          />
        </div>

        {streaming ? (
          <button className="send-btn send-btn--stop" onClick={handleStop}>
            <svg width="16" height="16" viewBox="0 0 16 16" fill="currentColor">
              <rect x="3" y="3" width="10" height="10" rx="1.5" />
            </svg>
          </button>
        ) : (
          <button
            className="send-btn"
            onClick={handleSend}
            disabled={!input.trim()}
          >
            <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
              <path
                d="M14.5 1.5l-6 13-2.5-5.5L.5 6.5l14-5z"
                stroke="currentColor"
                strokeWidth="1.2"
                strokeLinejoin="round"
              />
              <path
                d="M14.5 1.5L6 9"
                stroke="currentColor"
                strokeWidth="1.2"
                strokeLinecap="round"
              />
            </svg>
          </button>
        )}
      </div>
    </div>
  );
}
