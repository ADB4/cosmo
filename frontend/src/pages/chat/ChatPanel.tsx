import { useState, useRef, useEffect, useCallback } from "react";
import type { ChatMessage, ModelMode } from "../../lib/types";
import { streamChat, clearHistory } from "../../lib/api";
import MessageBubble from "./MessageBubble";

interface ChatPanelProps {
  mode: ModelMode;
}

let nextId = 0;
function uid(): string {
  return `msg_${Date.now()}_${nextId++}`;
}

export default function ChatPanel({ mode }: ChatPanelProps) {
  const [messages, setMessages] = useState<ChatMessage[]>([
    {
      id: uid(),
      role: "user",
      content: "Connected to Ollama. Ready to answer questions about your documentation.",
      timestamp: Date.now(),
    },
  ]);
  const [input, setInput] = useState("");
  const [streaming, setStreaming] = useState(false);
  const [grounded, setGrounded] = useState(true);
  const abortRef = useRef<AbortController | null>(null);
  const bottomRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLTextAreaElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

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

    abortRef.current = streamChat(q, mode, 4, grounded, {
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
              ? { ...m, content: m.content + `\n\n[error: ${err}]` }
              : m,
          ),
        );
        setStreaming(false);
      },
    });
  }, [input, mode, streaming, grounded]);

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
    setMessages([
      {
        id: uid(),
        role: "user",
        content: "Chat cleared. Ready for new questions.",
        timestamp: Date.now(),
      },
    ]);
    await clearHistory();
  };

  const hasConversation = messages.length > 1;

  return (
    <div className="chat-panel">
      <div className="chat-messages">
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

      <div className="chat-input-area">
        <textarea
          ref={inputRef}
          className="chat-input"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Ask a question about the documentation..."
          rows={1}
          disabled={streaming}
        />
        <div className="input-footer">
          <span className="input-hint">
            Press Enter to send, Shift+Enter for new line
          </span>
          <div className="input-actions">
            <button
              className={`grounded-toggle ${!grounded ? "grounded-toggle--broad" : ""}`}
              onClick={() => setGrounded((g) => !g)}
              title={grounded
                ? "Docs only — answers strictly from indexed documentation"
                : "Broad — supplements with LLM knowledge when docs are insufficient"
              }
            >
              {grounded ? "Docs only" : "Broad"}
            </button>
            {streaming ? (
              <button className="send-btn send-btn--stop" onClick={handleStop}>
                <span className="send-btn-icon">&#9632;</span>
                Stop
              </button>
            ) : (
              <button
                className="send-btn"
                onClick={handleSend}
                disabled={!input.trim()}
              >
                <span className="send-btn-icon">&#9654;</span>
                Send
              </button>
            )}
            {hasConversation && (
              <button className="topbar-btn" onClick={handleClear}>
                Clear
              </button>
            )}
            <button className="help-btn" title="Keyboard shortcuts">?</button>
          </div>
        </div>
      </div>
    </div>
  );
}