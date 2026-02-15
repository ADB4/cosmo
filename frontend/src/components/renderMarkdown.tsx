import { createElement, Fragment } from "react";
import type { ReactNode, ComponentPropsWithoutRef } from "react";
import Markdown from "react-markdown";
import remarkGfm from "remark-gfm";

/**
 * Markdown renderer powered by react-markdown.
 *
 * Handles the full CommonMark spec (bold, italic, headings, lists, etc.)
 * plus Cosmo-specific features:
 *   - Fenced code blocks → <pre class="code-block" data-lang="...">
 *   - Inline code       → <code class="inline-code">
 *   - [N] citations     → <span class="citation">[N]</span>
 *
 * Drop-in replacement: same signature as the original hand-rolled renderer.
 */

// ---------------------------------------------------------------------------
// Citation handling — injects <span class="citation"> around [N] markers
// ---------------------------------------------------------------------------

const CITATION_RE = /(\[\d+\])/g;

function renderCitations(text: string): ReactNode[] {
  const parts = text.split(CITATION_RE);
  return parts.map((part, i) => {
    if (CITATION_RE.test(part)) {
      // Reset lastIndex since we reuse the regex
      CITATION_RE.lastIndex = 0;
      return (
        <span key={i} className="citation">
          {part}
        </span>
      );
    }
    return part;
  });
}

// ---------------------------------------------------------------------------
// Custom component overrides for react-markdown
// ---------------------------------------------------------------------------

const markdownComponents = {
  // Fenced code blocks: match existing .code-block styling
  pre({ children, ...props }: ComponentPropsWithoutRef<"pre">) {
    return <>{children}</>;
  },

  code({ className, children, ...props }: ComponentPropsWithoutRef<"code">) {
    // react-markdown sets className="language-xyz" for fenced blocks
    const langMatch = className?.match(/language-(\w+)/);

    if (langMatch) {
      // Fenced code block
      return (
        <pre
          className="code-block"
          data-lang={langMatch[1]}
        >
          <code>{children}</code>
        </pre>
      );
    }

    // Inline code
    return (
      <code className="inline-code" {...props}>
        {children}
      </code>
    );
  },

  // Paragraphs: render citations inside text content
  p({ children, ...props }: ComponentPropsWithoutRef<"p">) {
    return <p {...props}>{processChildren(children)}</p>;
  },

  // List items: render citations inside text content
  li({ children, ...props }: ComponentPropsWithoutRef<"li">) {
    return <li {...props}>{processChildren(children)}</li>;
  },

  // Headings — keep them but render citations
  h1({ children, ...props }: ComponentPropsWithoutRef<"h1">) {
    return <h1 {...props}>{processChildren(children)}</h1>;
  },
  h2({ children, ...props }: ComponentPropsWithoutRef<"h2">) {
    return <h2 {...props}>{processChildren(children)}</h2>;
  },
  h3({ children, ...props }: ComponentPropsWithoutRef<"h3">) {
    return <h3 {...props}>{processChildren(children)}</h3>;
  },
};

/**
 * Walk children and apply citation rendering to any raw strings.
 */
function processChildren(children: ReactNode): ReactNode {
  if (typeof children === "string") {
    return <>{renderCitations(children)}</>;
  }
  if (Array.isArray(children)) {
    return (
      <>
        {children.map((child, i) =>
          typeof child === "string" ? (
            <Fragment key={i}>{renderCitations(child)}</Fragment>
          ) : (
            child
          ),
        )}
      </>
    );
  }
  return children;
}

// ---------------------------------------------------------------------------
// Public API — drop-in replacement
// ---------------------------------------------------------------------------

export function renderMarkdown(raw: string): ReactNode[] {
  return [
    <Markdown key="md" remarkPlugins={[remarkGfm]} components={markdownComponents}>
      {raw}
    </Markdown>,
  ];
}