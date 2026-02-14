import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import QuizMode from "../pages/apollo/QuizMode";
import { MOCK_NORMALIZED } from "./fixtures";

const mockFetch = vi.fn();

beforeEach(() => {
  vi.stubGlobal("fetch", mockFetch);
});

afterEach(() => {
  vi.restoreAllMocks();
});

const noop = () => {};

// Use a small subset: 1 TF + 1 MC for fast tests
const TWO_QUESTIONS = MOCK_NORMALIZED.filter(
  (q) => q.id === "TF-1" || q.id === "MC-1",
);

describe("QuizMode — question rendering", () => {
  it("shows the first question with type label and progress", () => {
    render(
      <QuizMode title="Test" questions={TWO_QUESTIONS} onExit={noop} />,
    );
    expect(screen.getByText("TRUE FALSE")).toBeInTheDocument();
    expect(screen.getByText(/Question 1 \/ 2/)).toBeInTheDocument();
  });

  it("shows True/False options for TF questions", () => {
    render(
      <QuizMode title="Test" questions={TWO_QUESTIONS} onExit={noop} />,
    );
    expect(screen.getByText("True")).toBeInTheDocument();
    expect(screen.getByText("False")).toBeInTheDocument();
  });

  it("disables Next button until an answer is selected", () => {
    render(
      <QuizMode title="Test" questions={TWO_QUESTIONS} onExit={noop} />,
    );
    expect(screen.getByText("Next")).toBeDisabled();
  });
});

describe("QuizMode — answering and navigation", () => {
  it("enables Next after selecting an answer", async () => {
    const user = userEvent.setup();
    render(
      <QuizMode title="Test" questions={TWO_QUESTIONS} onExit={noop} />,
    );

    await user.click(screen.getByText("True"));
    expect(screen.getByText("Next")).not.toBeDisabled();
  });

  it("advances to the next question on submit", async () => {
    const user = userEvent.setup();
    render(
      <QuizMode title="Test" questions={TWO_QUESTIONS} onExit={noop} />,
    );

    await user.click(screen.getByText("True"));
    await user.click(screen.getByText("Next"));

    // Now on MC question
    expect(screen.getByText("MULTIPLE CHOICE")).toBeInTheDocument();
    expect(screen.getByText(/Question 2 \/ 2/)).toBeInTheDocument();
  });

  it("shows Finish on the last question", async () => {
    const user = userEvent.setup();
    render(
      <QuizMode title="Test" questions={TWO_QUESTIONS} onExit={noop} />,
    );

    // Answer first question
    await user.click(screen.getByText("True"));
    await user.click(screen.getByText("Next"));

    // Last question should show "Finish"
    expect(screen.getByText("Finish")).toBeInTheDocument();
  });
});

describe("QuizMode — results screen", () => {
  it("shows results after finishing all questions", async () => {
    const user = userEvent.setup();
    render(
      <QuizMode title="Test" questions={TWO_QUESTIONS} onExit={noop} />,
    );

    // Answer TF-1 correctly (True)
    await user.click(screen.getByText("True"));
    await user.click(screen.getByText("Next"));

    // Answer MC-1 correctly (typeof)
    await user.click(screen.getByText("typeof"));
    await user.click(screen.getByText("Finish"));

    // Should show results with 100%
    expect(screen.getByText("100%")).toBeInTheDocument();
    expect(screen.getByText(/2\/2 correct/)).toBeInTheDocument();
  });

  it("shows incorrect results for wrong answers", async () => {
    const user = userEvent.setup();
    render(
      <QuizMode title="Test" questions={TWO_QUESTIONS} onExit={noop} />,
    );

    // Answer TF-1 wrong (False)
    await user.click(screen.getByText("False"));
    await user.click(screen.getByText("Next"));

    // Answer MC-1 wrong (keyof)
    await user.click(screen.getByText("keyof"));
    await user.click(screen.getByText("Finish"));

    expect(screen.getByText("0%")).toBeInTheDocument();
  });
});

describe("QuizMode — exit", () => {
  it("calls onExit when exit button is clicked", async () => {
    const user = userEvent.setup();
    const onExit = vi.fn();
    render(
      <QuizMode title="Test" questions={TWO_QUESTIONS} onExit={onExit} />,
    );

    await user.click(screen.getByText(/Exit Quiz/));
    expect(onExit).toHaveBeenCalledOnce();
  });
});

describe("QuizMode — short answer", () => {
  const SA_ONLY = MOCK_NORMALIZED.filter((q) => q.id === "SA-1");

  it("renders textarea for short answer questions", () => {
    render(<QuizMode title="Test" questions={SA_ONLY} onExit={noop} />);
    expect(screen.getByText("SHORT ANSWER")).toBeInTheDocument();
    expect(screen.getByPlaceholderText("Type your answer...")).toBeInTheDocument();
  });

  it("disables Finish until text is entered", () => {
    render(<QuizMode title="Test" questions={SA_ONLY} onExit={noop} />);
    expect(screen.getByText("Finish")).toBeDisabled();
  });

  it("enables Finish after typing an answer", async () => {
    const user = userEvent.setup();
    render(<QuizMode title="Test" questions={SA_ONLY} onExit={noop} />);

    await user.type(
      screen.getByPlaceholderText("Type your answer..."),
      "unknown requires narrowing",
    );

    expect(screen.getByText("Finish")).not.toBeDisabled();
  });
});
