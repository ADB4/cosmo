import { renderMarkdown } from "../../components/renderMarkdown";
import type { ChatMessage } from "../../lib/types";

interface Props {
  message: ChatMessage;
}

function formatTime(ts: number): string {
  return new Date(ts).toLocaleTimeString("en-US", {
    hour: "numeric",
    minute: "2-digit",
    second: "2-digit",
    hour12: true,
  });
}

export default function MessageBubble({ message }: Props) {
  const isSystem =
    message.content.startsWith("Connected to Ollama") ||
    message.content.startsWith("Chat cleared");
  const isUser = !isSystem && message.role === "user";
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
        {isAssistant ? renderMarkdown(message.content) : message.content}
      </div>
    </div>
  );
}
