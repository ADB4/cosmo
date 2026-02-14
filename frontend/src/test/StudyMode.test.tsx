import { describe, it, expect, beforeEach, vi } from "vitest";
import { render, screen, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import StudyMode from "../pages/apollo/StudyMode";
import { MOCK_NORMALIZED } from "./fixtures";

const noop = () => {};

/** Helper: open the filter panel and return a scoped query object for it */
async function openFilter(user: ReturnType<typeof userEvent.setup>) {
  await user.click(screen.getByTitle("Filter by topic"));
  const panel = document.querySelector(".study-filter-panel")!;
  return within(panel as HTMLElement);
}

describe("StudyMode", () => {
  beforeEach(() => {
    render(
      <StudyMode title="Test Quiz" questions={MOCK_NORMALIZED} onExit={noop} />,
    );
  });

  it("renders the exit button and card counter", () => {
    expect(screen.getByText(/Exit Study Mode/)).toBeInTheDocument();
    expect(screen.getByText(/\/ 5/)).toBeInTheDocument();
  });

  it("shows a question card with QUESTION label", () => {
    expect(screen.getByText("QUESTION")).toBeInTheDocument();
  });

  it("shows tag chips on the question face", () => {
    const tags = document.querySelectorAll(".study-card-tag");
    expect(tags.length).toBeGreaterThan(0);
  });
});

describe("StudyMode — card flipping", () => {
  it("flips card to show answer on click", async () => {
    const user = userEvent.setup();
    render(
      <StudyMode title="Test" questions={MOCK_NORMALIZED} onExit={noop} />,
    );

    await user.click(screen.getByText("Click to flip"));

    expect(screen.getByText("ANSWER")).toBeInTheDocument();
    expect(screen.getByText("Click to flip back")).toBeInTheDocument();
  });

  it("flips card via the Flip Card button", async () => {
    const user = userEvent.setup();
    render(
      <StudyMode title="Test" questions={MOCK_NORMALIZED} onExit={noop} />,
    );

    await user.click(screen.getByText(/Flip Card/));
    expect(screen.getByText("ANSWER")).toBeInTheDocument();
  });
});

describe("StudyMode — navigation", () => {
  it("Previous is disabled on first card", () => {
    render(
      <StudyMode title="Test" questions={MOCK_NORMALIZED} onExit={noop} />,
    );
    expect(screen.getByText(/Previous/)).toBeDisabled();
  });

  it("navigates to next card and updates counter", async () => {
    const user = userEvent.setup();
    render(
      <StudyMode title="Test" questions={MOCK_NORMALIZED} onExit={noop} />,
    );

    expect(screen.getByText(/1 \/ 5/)).toBeInTheDocument();
    await user.click(screen.getByText(/Next/));
    expect(screen.getByText(/2 \/ 5/)).toBeInTheDocument();
  });

  it("resets flip state when navigating", async () => {
    const user = userEvent.setup();
    render(
      <StudyMode title="Test" questions={MOCK_NORMALIZED} onExit={noop} />,
    );

    await user.click(screen.getByText(/Flip Card/));
    expect(screen.getByText("ANSWER")).toBeInTheDocument();

    await user.click(screen.getByText(/Next/));
    expect(screen.getByText("QUESTION")).toBeInTheDocument();
  });
});

describe("StudyMode — tag filtering", () => {
  it("opens filter panel when filter button is clicked", async () => {
    const user = userEvent.setup();
    render(
      <StudyMode title="Test" questions={MOCK_NORMALIZED} onExit={noop} />,
    );

    expect(screen.queryByText("Filter by topic")).toBeNull();
    await user.click(screen.getByTitle("Filter by topic"));
    expect(screen.getByText("Filter by topic")).toBeInTheDocument();
  });

  it("shows tag buttons grouped by category", async () => {
    const user = userEvent.setup();
    render(
      <StudyMode title="Test" questions={MOCK_NORMALIZED} onExit={noop} />,
    );
    const panel = await openFilter(user);

    expect(panel.getByText("typescript basics")).toBeInTheDocument();
    expect(panel.getByText("any type")).toBeInTheDocument();
    expect(panel.getByText("generics")).toBeInTheDocument();
  });

  it("filters cards when a tag is selected", async () => {
    const user = userEvent.setup();
    render(
      <StudyMode title="Test" questions={MOCK_NORMALIZED} onExit={noop} />,
    );
    const panel = await openFilter(user);

    // Select "utility-types" — only MC-2 has this tag
    await user.click(panel.getByText("utility types"));

    expect(screen.getByText("1 card match")).toBeInTheDocument();
    expect(screen.getByText("1 / 1")).toBeInTheDocument();
  });

  it("OR logic: selecting multiple tags unions results", async () => {
    const user = userEvent.setup();
    render(
      <StudyMode title="Test" questions={MOCK_NORMALIZED} onExit={noop} />,
    );
    const panel = await openFilter(user);

    // typeof-operator matches MC-1, utility-types matches MC-2
    await user.click(panel.getByText("typeof operator"));
    await user.click(panel.getByText("utility types"));

    expect(screen.getByText("2 cards match")).toBeInTheDocument();
  });

  it("deselecting a tag removes the filter", async () => {
    const user = userEvent.setup();
    render(
      <StudyMode title="Test" questions={MOCK_NORMALIZED} onExit={noop} />,
    );
    const panel = await openFilter(user);

    await user.click(panel.getByText("utility types"));
    expect(screen.getByText("1 card match")).toBeInTheDocument();

    // Click again to deselect — scoped to filter panel
    await user.click(panel.getByText("utility types"));
    expect(screen.getByText(/\/ 5/)).toBeInTheDocument();
  });

  it("Clear all button resets all tag filters", async () => {
    const user = userEvent.setup();
    render(
      <StudyMode title="Test" questions={MOCK_NORMALIZED} onExit={noop} />,
    );
    const panel = await openFilter(user);

    await user.click(panel.getByText("utility types"));
    expect(screen.getByText("Clear all")).toBeInTheDocument();

    await user.click(screen.getByText("Clear all"));
    expect(screen.getByText(/\/ 5/)).toBeInTheDocument();
    expect(screen.queryByText("Clear all")).toBeNull();
  });

  it("shows badge count on filter toggle when tags are active", async () => {
    const user = userEvent.setup();
    render(
      <StudyMode title="Test" questions={MOCK_NORMALIZED} onExit={noop} />,
    );
    const panel = await openFilter(user);

    await user.click(panel.getByText("utility types"));
    await user.click(panel.getByText("any type"));

    const badge = document.querySelector(".study-filter-badge");
    expect(badge).not.toBeNull();
    expect(badge!.textContent).toBe("2");
  });
});

describe("StudyMode — exit callback", () => {
  it("calls onExit when exit button is clicked", async () => {
    const user = userEvent.setup();
    const onExit = vi.fn();

    render(
      <StudyMode title="Test" questions={MOCK_NORMALIZED} onExit={onExit} />,
    );

    await user.click(screen.getByText(/Exit Study Mode/));
    expect(onExit).toHaveBeenCalledOnce();
  });
});