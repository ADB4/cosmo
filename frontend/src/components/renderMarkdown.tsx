import type { ReactNode } from "react";

/**
 * Lightweight markdown renderer.
 * Handles fenced code blocks, inline code, and [N] citation markers.
 * No external dependencies.
 */
export function renderMarkdown(raw: string): ReactNode[] {
  const nodes: ReactNode[] = [];
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
