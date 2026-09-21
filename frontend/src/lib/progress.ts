/**
 * Per-deck quiz progress, persisted in localStorage keyed by module/quizId.
 * Stores the most recent attempt so the deck list can show last score/date,
 * the results screen can offer "Retry missed", and Study Mode can filter to
 * the questions missed last time.
 */

export interface MissedQuestion {
  id: string;
  tags: string[];
}

export interface QuizAttempt {
  timestamp: number;
  percentage: number;
  /** Scored-correct count and scored total (ungraded excluded). */
  correct: number;
  total: number;
  /** Questions answered wrong or left ungraded, with their tags. */
  missed: MissedQuestion[];
}

const PREFIX = "cosmo.progress.";

function keyFor(module: string, quizId: string): string {
  return `${PREFIX}${module}/${quizId}`;
}

export function getAttempt(module: string, quizId: string): QuizAttempt | null {
  try {
    const raw = localStorage.getItem(keyFor(module, quizId));
    if (!raw) return null;
    const parsed = JSON.parse(raw);
    if (parsed && typeof parsed.timestamp === "number") return parsed as QuizAttempt;
    return null;
  } catch {
    return null;
  }
}

export function saveAttempt(module: string, quizId: string, attempt: QuizAttempt): void {
  try {
    localStorage.setItem(keyFor(module, quizId), JSON.stringify(attempt));
  } catch {
    // ignore storage failures (private mode, quota)
  }
}

/** Format a timestamp as a short "Mar 3" style date for the deck list. */
export function formatAttemptDate(ts: number): string {
  try {
    return new Date(ts).toLocaleDateString("en-US", { month: "short", day: "numeric" });
  } catch {
    return "";
  }
}
