import { useState, useRef, useEffect, useCallback } from "react";
import type { ChatMessage, ModelMode, HealthResponse } from "../../lib/types";
import { MODE_INFO } from "../../lib/types";
import { streamChat, clearHistory } from "../../lib/api";
import MessageBubble from "./MessageBubble";
import KnowledgeBase from "./KnowledgeBase";

interface ChatPanelProps {
  mode: ModelMode;
  health: HealthResponse | null;
  onHealthRefresh: () => void;
}

let nextId = 0;
function uid(): string {
  return `msg_${Date.now()}_${nextId++}`;
}

const HISTORY_KEY = "cosmo.chat.messages";
const HISTORY_CAP = 200;

function loadStoredMessages(): ChatMessage[] {
  try {
    const raw = localStorage.getItem(HISTORY_KEY);
    if (!raw) return [];
    const parsed = JSON.parse(raw);
    return Array.isArray(parsed) ? (parsed as ChatMessage[]) : [];
  } catch {
    return [];
  }
}

export default function ChatPanel({ mode, health, onHealthRefresh }: ChatPanelProps) {
  const [messages, setMessages] = useState<ChatMessage[]>(loadStoredMessages);
  const [input, setInput] = useState("");
  const [streaming, setStreaming] = useState(false);
  const [grounded, setGrounded] = useState(true);
  const [filter, setFilter] = useState("");
  const abortRef = useRef<AbortController | null>(null);
  const bottomRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLTextAreaElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  useEffect(() => {
    inputRef.current?.focus();
  }, []);

  // Persist the visible message list (capped) so a reload keeps it.
  // Server-side history is unaffected (still managed via /history/clear).
  useEffect(() => {
    try {
      const capped = messages.slice(-HISTORY_CAP);
      localStorage.setItem(HISTORY_KEY, JSON.stringify(capped));
    } catch {
      // ignore storage failures (private mode, quota)
    }
  }, [messages]);

  // Core send routine. `showUserMsg` is false when re-issuing an existing
  // question (Ask broadly / Retry) so we don't duplicate the user's turn.
  const runQuery = useCallback(
    (q: string, groundedFlag: boolean, showUserMsg: boolean) => {
      if (!q || streaming) return;

      const assistantMsg: ChatMessage = {
        id: uid(),
        role: "assistant",
        content: "",
        mode,
        timestamp: Date.now(),
        question: q,
      };

      setMessages((prev) => {
        if (!showUserMsg) return [...prev, assistantMsg];
        const userMsg: ChatMessage = {
          id: uid(),
          role: "user",
          content: q,
          mode,
          timestamp: Date.now(),
        };
        return [...prev, userMsg, assistantMsg];
      });
      setStreaming(true);

      const assistantId = assistantMsg.id;

      abortRef.current = streamChat(q, mode, 8, groundedFlag, {
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
              m.id === assistantId ? { ...m, error: err } : m,
            ),
          );
          setStreaming(false);
        },
        onNoResults: () => {
          setMessages((prev) =>
            prev.map((m) =>
              m.id === assistantId ? { ...m, noResults: true } : m,
            ),
          );
          setStreaming(false);
          inputRef.current?.focus();
        },
      });
    },
    [mode, streaming],
  );

  const handleSend = useCallback(() => {
    const q = input.trim();
    if (!q || streaming || health?.status === "error") return;
    setInput("");
    runQuery(q, grounded, true);
  }, [input, streaming, grounded, runQuery, health]);

  const handleAskBroadly = useCallback(
    (question: string) => {
      if (streaming) return;
      runQuery(question, false, false);
    },
    [streaming, runQuery],
  );

  const handleRetry = useCallback(
    (question: string) => {
      if (streaming) return;
      runQuery(question, grounded, false);
    },
    [streaming, grounded, runQuery],
  );

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

  const hasConversation = messages.length > 0;

  // ── Status line derived from real health (never fabricated) ──
  const healthError = health?.status === "error";
  const docsCount = health?.total_documents ?? 0;
  const chunksCount = health?.total_chunks ?? 0;
  const emptyKb = health?.status === "ok" && docsCount === 0;

  let statusNode: React.ReactNode;
  if (!health) {
    statusNode = <span className="chat-status-text">Connecting to backend…</span>;
  } else if (healthError) {
    const msg = health.message ?? "Backend unavailable";
    const mentionsOllama = /ollama/i.test(msg);
    const hint = mentionsOllama
      ? "start Ollama with `ollama serve`"
      : "start the backend with `./scripts/start-dev.sh`";
    statusNode = (
      <span className="chat-status-text chat-status-text--error">
        Offline — {msg.split("\n")[0]} · {hint}
      </span>
    );
  } else if (emptyKb) {
    statusNode = (
      <span className="chat-status-text">
        Ready · no documents indexed yet — add some in the{" "}
        <strong>Knowledge base</strong> panel above · {MODE_INFO[mode].label}
      </span>
    );
  } else {
    statusNode = (
      <span className="chat-status-text">
        Ready · {docsCount} document{docsCount !== 1 ? "s" : ""} · {chunksCount} chunks ·{" "}
        {MODE_INFO[mode].label}
      </span>
    );
  }

  const trimmedFilter = filter.trim().toLowerCase();
  const displayedMessages = trimmedFilter
    ? messages.filter(
        (m) =>
          m.content.toLowerCase().includes(trimmedFilter) ||
          (m.question?.toLowerCase().includes(trimmedFilter) ?? false) ||
          (m.error?.toLowerCase().includes(trimmedFilter) ?? false),
      )
    : messages;

  return (
    <div className="chat-panel">
      <KnowledgeBase onIngested={onHealthRefresh} defaultOpen={emptyKb} />
      <div className={`chat-status ${healthError ? "chat-status--error" : ""}`}>
        {statusNode}
      </div>
      {messages.length > 0 && (
        <div className="chat-filter">
          <input
            className="chat-filter-input"
            type="text"
            value={filter}
            onChange={(e) => setFilter(e.target.value)}
            placeholder="Filter messages…"
          />
          {trimmedFilter && (
            <span className="chat-filter-count">
              {displayedMessages.length} / {messages.length}
            </span>
          )}
        </div>
      )}
      <div className="chat-messages">
        {displayedMessages.map((msg) => (
          <MessageBubble
            key={msg.id}
            message={msg}
            onAskBroadly={handleAskBroadly}
            onRetry={handleRetry}
          />
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
          placeholder={
            healthError
              ? "Backend offline — start it to ask questions"
              : "Ask a question about the documentation..."
          }
          rows={1}
          disabled={streaming || healthError}
        />
        <div className="input-footer">
          <span className="input-hint">
            {healthError
              ? "Send is disabled while the backend is offline"
              : "Press Enter to send, Shift+Enter for new line"}
          </span>
          <div className="input-actions">
            <button
              className={`grounded-toggle ${!grounded ? "grounded-toggle--broad" : ""}`}
              onClick={() => setGrounded((g) => !g)}
              title={grounded
                ? "Docs only — answers only from indexed docs above the relevance cutoff; if nothing matches, says so instead of guessing"
                : "Broad — answers from the model's own knowledge, using any indexed docs as supporting context"
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
                disabled={!input.trim() || healthError}
                title={healthError ? "Backend is offline" : undefined}
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