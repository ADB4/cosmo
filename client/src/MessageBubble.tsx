import type { ChatMessage } from "./types";

interface Props {
  message: ChatMessage;
  time: string;
}

/**
 * Lightweight code-block and citation renderer.
 * No markdown lib — just fenced blocks, inline code, and [N] markers.
 */
function renderContent(raw: string): React.ReactNode[] {
  const nodes: React.ReactNode[] = [];
  const parts = raw.split(/(```[\s\S]*?```)/g);

  parts.forEach((part, pi) => {
    if (part.startsWith("```")) {
      const firstNewline = part.indexOf("\n");
      const lang = part.slice(3, firstNewline).trim();
      const body = part.slice(firstNewline + 1, part.length - 3);
      nodes.push(
        <pre key={pi} className="code-block" data-lang={lang || undefined}>
          <code>{body}</code>
        </pre>,
      );
    } else {
      const inlineParts = part.split(/(`[^`]+`)/g);
      inlineParts.forEach((seg, si) => {
        if (seg.startsWith("`") && seg.endsWith("`")) {
          nodes.push(
            <code key={`${pi}-${si}`} className="inline-code">
              {seg.slice(1, -1)}
            </code>,
          );
        } else {
          const withCitations = seg.split(/(\[\d+\])/g);
          withCitations.forEach((cs, ci) => {
            if (/^\[\d+\]$/.test(cs)) {
              nodes.push(
                <span key={`${pi}-${si}-${ci}`} className="citation">
                  {cs}
                </span>,
              );
            } else if (cs) {
              nodes.push(<span key={`${pi}-${si}-${ci}`}>{cs}</span>);
            }
          });
        }
      });
    }
  });

  return nodes;
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
  // Determine the visual role — we overload "user" role for system messages
  // by checking the content for our known system messages
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
        {isAssistant ? renderContent(message.content) : message.content}
      </div>
    </div>
  );
}