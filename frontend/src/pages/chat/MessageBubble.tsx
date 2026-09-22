import { renderMarkdown } from "../../components/renderMarkdown";
import type { ChatMessage } from "../../lib/types";

interface Props {
  message: ChatMessage;
  /** Re-issue this question in broad mode (from the no-results state) */
  onAskBroadly?: (question: string) => void;
  /** Re-issue this question after an error */
  onRetry?: (question: string) => void;
}

function formatTime(ts: number): string {
  return new Date(ts).toLocaleTimeString("en-US", {
    hour: "numeric",
    minute: "2-digit",
    hour12: true,
  });
}

export default function MessageBubble({ message, onAskBroadly, onRetry }: Props) {
  const isSystem = message.role === "system";
  const isUser = message.role === "user";
  const isAssistant = message.role === "assistant";

  const roleClass = isSystem
    ? "message--system"
    : isUser
      ? "message--user"
      : "message--assistant";

  const prefix = isSystem ? "# system" : isUser ? ">" : "cosmo";

  return (
    <div className={`message ${roleClass}`}>
      <div className="msg-header">
        <span className="msg-prefix">{prefix}</span>
        <span className="msg-timestamp">{formatTime(message.timestamp)}</span>
        {isAssistant && message.mode && (
          <span className="msg-mode-tag">{message.mode}</span>
        )}
      </div>
      <div className="msg-content">
        {/* Any tokens that streamed before an error/no-result still show */}
        {isAssistant ? renderMarkdown(message.content) : message.content}

        {message.noResults && (
          <div className="msg-noresults">
            <span className="msg-noresults-text">
              The indexed docs have nothing relevant to this question.
            </span>
            {message.question && onAskBroadly && (
              <button
                className="msg-noresults-btn"
                onClick={() => onAskBroadly(message.question!)}
              >
                Ask broadly &#8250;
              </button>
            )}
          </div>
        )}

        {message.error && (
          <div className="msg-error">
            <div className="msg-error-label">error</div>
            <div className="msg-error-text">{message.error}</div>
            {message.question && onRetry && (
              <button
                className="msg-error-btn"
                onClick={() => onRetry(message.question!)}
              >
                &#8635; Retry
              </button>
            )}
          </div>
        )}

        {message.truncated && !message.error && (
          <div className="msg-truncated">
            <span className="msg-truncated-text">
              Response was interrupted before it finished.
            </span>
            {message.question && onRetry && (
              <button
                className="msg-truncated-btn"
                onClick={() => onRetry(message.question!)}
              >
                &#8635; Retry
              </button>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
