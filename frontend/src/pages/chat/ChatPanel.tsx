import { useState, useRef, useEffect, useCallback } from "react";
import type { ChatMessage, ModelMode, HealthResponse } from "../../lib/types";
import { MODE_INFO } from "../../lib/types";
import { streamChat, type ChatTurn } from "../../lib/api";
import MessageBubble from "./MessageBubble";
import KnowledgeBase from "./KnowledgeBase";
import ShortcutsOverlay, { type Shortcut } from "../../components/ShortcutsOverlay";

const CHAT_SHORTCUTS: Shortcut[] = [
  { keys: "Enter", desc: "Send message" },
  { keys: "Shift + Enter", desc: "New line" },
  { keys: "Esc", desc: "Stop streaming" },
];

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
    if (!Array.isArray(parsed)) return [];
    // Drop interrupted assistant turns: empty content with no terminal state
    // (error / no-result / truncated). These are phantoms from a stream that
    // never finished; keeping them would reload as blank "complete" answers.
    return (parsed as ChatMessage[]).filter(
      (m) =>
        m.role !== "assistant" ||
        m.content.length > 0 ||
        !!m.error ||
        !!m.noResults ||
        !!m.truncated,
    );
  } catch {
    return [];
  }
}

/** The last 10 completed assistant turns, as {question, answer} pairs, to send
 *  to the backend as per-request context. Skips errored / no-result / empty
 *  turns so partial or failed answers never poison the next prompt. */
function buildHistory(messages: ChatMessage[]): ChatTurn[] {
  return messages
    .filter(
      (m) =>
        m.role === "assistant" &&
        !!m.question &&
        !m.error &&
        !m.noResults &&
        !m.truncated &&
        m.content.length > 0,
    )
    .slice(-10)
    .map((m) => ({ question: m.question!, answer: m.content }));
}

export default function ChatPanel({ mode, health, onHealthRefresh }: ChatPanelProps) {
  const [messages, setMessages] = useState<ChatMessage[]>(loadStoredMessages);
  const [input, setInput] = useState("");
  const [streaming, setStreaming] = useState(false);
  const [grounded, setGrounded] = useState(true);
  const [filter, setFilter] = useState("");
  const [showShortcuts, setShowShortcuts] = useState(false);
  const abortRef = useRef<AbortController | null>(null);
  const bottomRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLTextAreaElement>(null);
  // Always-current view of `messages` so runQuery can build the history to
  // send without depending on `messages` (which changes on every token).
  const messagesRef = useRef<ChatMessage[]>(messages);
  useEffect(() => {
    messagesRef.current = messages;
  }, [messages]);
  // Id of the assistant message currently streaming, so Stop/unmount can mark
  // it interrupted rather than leaving a partial answer that looks complete.
  const streamingIdRef = useRef<string | null>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  useEffect(() => {
    inputRef.current?.focus();
  }, []);

  // Abort any in-flight stream when the panel unmounts (e.g. switching to the
  // Apollo tab). Without this the fetch keeps running, onToken updates a dead
  // component, and the partial answer could persist as if complete.
  useEffect(() => () => abortRef.current?.abort(), []);

  // Persist the visible transcript (capped) only when NOT streaming. Writing on
  // every token would save a partial answer that reloads as a finished one;
  // persisting on terminal states (done / error / no-result / stop) instead
  // means an unmount mid-stream leaves the last completed transcript intact.
  useEffect(() => {
    if (streaming) return;
    try {
      const capped = messages.slice(-HISTORY_CAP);
      localStorage.setItem(HISTORY_KEY, JSON.stringify(capped));
    } catch {
      // ignore storage failures (private mode, quota)
    }
  }, [messages, streaming]);

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
      streamingIdRef.current = assistantId;

      // Prior completed turns (before this new question) become the server's
      // per-request context. Read from the ref so this stays off runQuery's deps.
      const history = buildHistory(messagesRef.current);

      abortRef.current = streamChat(q, mode, 8, groundedFlag, history, {
        onToken: (token) => {
          setMessages((prev) =>
            prev.map((m) =>
              m.id === assistantId ? { ...m, content: m.content + token } : m,
            ),
          );
        },
        onDone: () => {
          streamingIdRef.current = null;
          setStreaming(false);
          inputRef.current?.focus();
        },
        onError: (err) => {
          streamingIdRef.current = null;
          setMessages((prev) =>
            prev.map((m) =>
              m.id === assistantId ? { ...m, error: err } : m,
            ),
          );
          setStreaming(false);
        },
        onNoResults: () => {
          streamingIdRef.current = null;
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
    } else if (e.key === "Escape" && streaming) {
      e.preventDefault();
      handleStop();
    }
  };

  const handleStop = () => {
    abortRef.current?.abort();
    // Mark the in-flight assistant message interrupted so its partial content
    // is never persisted or reused as a complete answer.
    const id = streamingIdRef.current;
    if (id) {
      setMessages((prev) =>
        prev.map((m) =>
          m.id === id && !m.error && !m.noResults ? { ...m, truncated: true } : m,
        ),
      );
      streamingIdRef.current = null;
    }
    setStreaming(false);
  };

  const handleClear = () => {
    if (streaming) handleStop();
    setMessages([]);
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
            <button
              className="help-btn"
              title="Keyboard shortcuts"
              onClick={() => setShowShortcuts(true)}
            >
              ?
            </button>
          </div>
        </div>
      </div>

      {showShortcuts && (
        <ShortcutsOverlay
          title="Chat shortcuts"
          shortcuts={CHAT_SHORTCUTS}
          onClose={() => setShowShortcuts(false)}
        />
      )}
    </div>
  );
}