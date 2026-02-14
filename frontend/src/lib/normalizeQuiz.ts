import type {
  Quiz,
  NormalizedQuestion,
  TFQuestion,
  MCQuestion,
  SAQuestion,
} from "./types";

/** Tag categories for grouped display in the filter UI */
export const TAG_CATEGORIES: Record<string, string[]> = {
  Fundamentals: [
    "typescript-basics",
    "compilation",
    "strict-mode",
    "type-inference",
    "type-annotations",
    "contextual-typing",
    "primitive-types",
    "literal-types",
    "structural-typing",
  ],
  "Type Constructs": [
    "union-types",
    "intersection-types",
    "type-aliases",
    "interfaces",
    "object-types",
    "array-types",
    "tuple-types",
  ],
  "Special Types": [
    "any-type",
    "unknown-type",
    "void-type",
    "never-type",
    "null-undefined",
  ],
  "Object Features": [
    "optional-properties",
    "readonly",
    "excess-property-checking",
  ],
  Narrowing: [
    "type-narrowing",
    "type-guards",
    "typeof-operator",
    "truthiness",
    "equality-narrowing",
    "in-operator",
    "instanceof",
    "type-assertions",
    "non-null-assertion",
  ],
  Functions: [
    "functions",
    "return-types",
    "optional-parameters",
    "rest-parameters",
    "function-overloads",
  ],
  Advanced: [
    "generics",
    "generic-constraints",
    "utility-types",
    "mapped-types",
    "conditional-types",
    "keyof",
    "indexed-access",
    "template-literal-types",
    "satisfies",
    "discriminated-unions",
    "distributive",
  ],
};

/**
 * Flatten the section-based quiz structure into a single array of
 * NormalizedQuestion that StudyMode and QuizMode can iterate over.
 */
export function normalizeQuiz(quiz: Quiz): NormalizedQuestion[] {
  const out: NormalizedQuestion[] = [];

  for (const section of quiz.sections) {
    switch (section.type) {
      case "true_false":
        for (const q of section.questions as TFQuestion[]) {
          out.push({
            id: q.id,
            sectionType: "true_false",
            text: q.question,
            options: [],
            correctAnswer: q.answer ? "true" : "false",
            explanation: q.explanation,
            tags: q.tags ?? [],
          });
        }
        break;
      case "multiple_choice":
        for (const q of section.questions as MCQuestion[]) {
          out.push({
            id: q.id,
            sectionType: "multiple_choice",
            text: q.question,
            code: q.code,
            options: q.options,
            correctAnswer: String(q.answer),
            explanation: q.explanation,
            tags: q.tags ?? [],
          });
        }
        break;
      case "short_answer":
        for (const q of section.questions as SAQuestion[]) {
          out.push({
            id: q.id,
            sectionType: "short_answer",
            text: q.question,
            options: [],
            correctAnswer: q.model_answer,
            explanation: "",
            tags: q.tags ?? [],
          });
        }
        break;
    }
  }

  return out;
}

export function filterBySection(
  questions: NormalizedQuestion[],
  type: "true_false" | "multiple_choice" | "short_answer",
): NormalizedQuestion[] {
  return questions.filter((q) => q.sectionType === type);
}

/**
 * Filter questions that match ANY of the selected tags (OR logic).
 * Returns all questions if selectedTags is empty.
 */
export function filterByTags(
  questions: NormalizedQuestion[],
  selectedTags: Set<string>,
): NormalizedQuestion[] {
  if (selectedTags.size === 0) return questions;
  return questions.filter((q) =>
    q.tags.some((t) => selectedTags.has(t)),
  );
}

/** Extract all unique tags present in a question set, sorted alphabetically */
export function collectTags(questions: NormalizedQuestion[]): string[] {
  const tags = new Set<string>();
  for (const q of questions) {
    for (const t of q.tags) tags.add(t);
  }
  return [...tags].sort();
}

function shuffle<T>(arr: T[]): T[] {
  const a = [...arr];
  for (let i = a.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [a[i], a[j]] = [a[j]!, a[i]!];
  }
  return a;
}

export function sampleQuiz(
  questions: NormalizedQuestion[],
  counts: { tf: number; mc: number; sa: number },
): NormalizedQuestion[] {
  const tf = shuffle(filterBySection(questions, "true_false")).slice(0, counts.tf);
  const mc = shuffle(filterBySection(questions, "multiple_choice")).slice(0, counts.mc);
  const sa = shuffle(filterBySection(questions, "short_answer")).slice(0, counts.sa);
  return [...tf, ...mc, ...sa];
}