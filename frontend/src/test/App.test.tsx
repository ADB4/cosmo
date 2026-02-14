import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";
import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import App from "../App";

const mockFetch = vi.fn();

function stubFetch(overrides: Record<string, () => Promise<unknown>> = {}) {
  mockFetch.mockImplementation((url: string) => {
    if (overrides[url]) {
      return overrides[url]().then((body) => ({
        ok: true,
        json: () => Promise.resolve(body),
      }));
    }
    // Defaults
    if (url === "/api/health") {
      return Promise.resolve({
        ok: true,
        json: () =>
          Promise.resolve({ status: "ok", total_chunks: 10, total_documents: 2 }),
      });
    }
    if (url === "/api/quizzes") {
      return Promise.resolve({
        ok: true,
        json: () => Promise.resolve({ quizzes: [] }),
      });
    }
    return Promise.resolve({
      ok: true,
      json: () => Promise.resolve({}),
    });
  });
}

beforeEach(() => {
  vi.stubGlobal("fetch", mockFetch);
  stubFetch();
});

afterEach(() => {
  vi.restoreAllMocks();
});

describe("App — layout", () => {
  it("renders the topbar with COSMO and APOLLO tabs", async () => {
    render(<App />);
    expect(screen.getByText("COSMO")).toBeInTheDocument();
    expect(screen.getByText("APOLLO")).toBeInTheDocument();
  });

  it("shows Ready status after successful health check", async () => {
    render(<App />);
    await waitFor(() => {
      expect(screen.getByText("Ready")).toBeInTheDocument();
    });
  });

  it("shows Offline status when health check fails", async () => {
    stubFetch({
      "/api/health": () => Promise.reject(new Error("Network")),
    });

    render(<App />);
    await waitFor(() => {
      expect(screen.getByText("Offline")).toBeInTheDocument();
    });
  });
});

describe("App — tab switching", () => {
  it("switches to COSMO tab and shows chat input", async () => {
    const user = userEvent.setup();
    render(<App />);

    await user.click(screen.getByText("COSMO"));

    expect(
      screen.getByPlaceholderText("Ask a question about the documentation..."),
    ).toBeInTheDocument();
  });

  it("switches to APOLLO tab and shows Apollo view", async () => {
    const user = userEvent.setup();
    render(<App />);

    await user.click(screen.getByText("APOLLO"));

    // Apollo loads quizzes — either shows the picker or loading
    await waitFor(() => {
      expect(
        screen.queryByText("Loading quizzes...") ||
          screen.queryByText("Upload Quiz JSON"),
      ).toBeTruthy();
    });
  });

  it("switches between tabs", async () => {
    const user = userEvent.setup();
    render(<App />);

    await user.click(screen.getByText("COSMO"));
    expect(
      screen.getByPlaceholderText("Ask a question about the documentation..."),
    ).toBeInTheDocument();

    await user.click(screen.getByText("APOLLO"));
    expect(
      screen.queryByPlaceholderText("Ask a question about the documentation..."),
    ).toBeNull();
  });
});

describe("App — model selector", () => {
  it("shows model selector on COSMO tab", async () => {
    const user = userEvent.setup();
    render(<App />);

    await user.click(screen.getByText("COSMO"));
    const select = document.querySelector(".model-select") as HTMLSelectElement;
    expect(select).not.toBeNull();
    expect(select.value).toBe("qwen-7b");
  });

  it("hides model selector on APOLLO tab", async () => {
    const user = userEvent.setup();
    render(<App />);

    await user.click(screen.getByText("APOLLO"));
    expect(document.querySelector(".model-select")).toBeNull();
  });

  it("allows switching model mode", async () => {
    const user = userEvent.setup();
    render(<App />);

    await user.click(screen.getByText("COSMO"));
    const select = document.querySelector(".model-select") as HTMLSelectElement;
    await user.selectOptions(select, "qwen-14b");
    expect(select.value).toBe("qwen-14b");
  });
});