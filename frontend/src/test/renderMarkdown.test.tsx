import { describe, it, expect } from "vitest";
import { render, screen } from "@testing-library/react";
import { renderMarkdown } from "../components/renderMarkdown";

/** Helper: render the ReactNode[] returned by renderMarkdown inside a container */
function renderMd(input: string) {
  return render(<div data-testid="md">{renderMarkdown(input)}</div>);
}

describe("renderMarkdown", () => {
  it("renders plain text as-is", () => {
    renderMd("Hello world");
    expect(screen.getByTestId("md")).toHaveTextContent("Hello world");
  });

  it("renders inline code with the inline-code class", () => {
    renderMd("Use `useState` for state");
    const code = document.querySelector(".inline-code");
    expect(code).not.toBeNull();
    expect(code!.textContent).toBe("useState");
  });

  it("renders fenced code blocks with the code-block class", () => {
    renderMd('```typescript\nconst x = 1;\n```');
    const block = document.querySelector(".code-block");
    expect(block).not.toBeNull();
    expect(block!.getAttribute("data-lang")).toBe("typescript");
    expect(block!.textContent).toContain("const x = 1;");
  });

  it("renders code blocks without a language", () => {
    renderMd("```\nplain code\n```");
    const block = document.querySelector(".code-block");
    expect(block).not.toBeNull();
    expect(block!.getAttribute("data-lang")).toBeNull();
  });

  it("renders citation markers with the citation class", () => {
    renderMd("According to [1] the answer is correct [2].");
    const citations = document.querySelectorAll(".citation");
    expect(citations).toHaveLength(2);
    expect(citations[0]!.textContent).toBe("[1]");
    expect(citations[1]!.textContent).toBe("[2]");
  });

  it("handles mixed inline code and citations", () => {
    renderMd("The `typeof` operator [3] narrows types");
    expect(document.querySelector(".inline-code")!.textContent).toBe("typeof");
    expect(document.querySelector(".citation")!.textContent).toBe("[3]");
  });

  it("returns empty array for empty string", () => {
    const result = renderMarkdown("");
    expect(result).toHaveLength(0);
  });
});
