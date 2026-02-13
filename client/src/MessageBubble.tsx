import type { ChatMessage } from "./types";

interface Props {
  message: ChatMessage;
}

/**
 * Very lightweight markdown-ish renderer:
 * - Fenced code blocks (```lang ... ```) → <pre><code>
 * - Inline backticks → <code>
 * - [N] citations highlighted
 * - Newlines preserved
 *
 * Intentionally not pulling in a full markdown lib — keeps the bundle tiny.
 */
function renderContent(raw: string): React.ReactNode[] {
  const nodes: React.ReactNode[] = [];
  // Split on fenced code blocks
  const parts = raw.split(/(```[\s\S]*?```)/g);

  parts.forEach((part, pi) => {
    if (part.startsWith("```")) {
      // Extract language hint and body
      const firstNewline = part.indexOf("\n");
      const lang = part.slice(3, firstNewline).trim();
      const body = part.slice(firstNewline + 1, part.length - 3);
      nodes.push(
        <pre key={pi} className="code-block" data-lang={lang || undefined}>
          <code>{body}</code>
        </pre>,
      );
    } else {
      // Process inline elements
      const inlineParts = part.split(/(`[^`]+`)/g);
      inlineParts.forEach((seg, si) => {
        if (seg.startsWith("`") && seg.endsWith("`")) {
          nodes.push(
            <code key={`${pi}-${si}`} className="inline-code">
              {seg.slice(1, -1)}
            </code>,
          );
        } else {
          // Highlight citation markers like [1], [2]
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

export default function MessageBubble({ message }: Props) {
  const isUser = message.role === "user";

  return (
    <div className={`message message--${message.role}`}>
      <div className="message-avatar">
        {isUser ? (
          <svg width="18" height="18" viewBox="0 0 18 18" fill="none">
            <circle cx="9" cy="6" r="3" stroke="currentColor" strokeWidth="1.5" />
            <path d="M2.5 16c0-3.5 2.9-6 6.5-6s6.5 2.5 6.5 6" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" />
          </svg>
        ) : (
          <svg width="18" height="18" viewBox="0 0 18 18" fill="none">
            <circle cx="9" cy="9" r="2" fill="currentColor" />
            <circle cx="9" cy="9" r="5" stroke="currentColor" strokeWidth="1" opacity="0.5" />
            <circle cx="9" cy="9" r="8" stroke="currentColor" strokeWidth="0.6" opacity="0.3" />
          </svg>
        )}
      </div>
      <div className="message-body">
        {isUser ? (
          <p>{message.content}</p>
        ) : (
          <div className="assistant-text">{renderContent(message.content)}</div>
        )}
        {message.mode && !isUser && (
          <span className="message-mode">{message.mode}</span>
        )}
      </div>
    </div>
  );
}
