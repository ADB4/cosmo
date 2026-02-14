import { describe, it, expect } from "vitest";
import {
  normalizeQuiz,
  filterBySection,
  filterByTags,
  collectTags,
  sampleQuiz,
  TAG_CATEGORIES,
} from "../lib/normalizeQuiz";
import { MOCK_QUIZ, MOCK_QUIZ_NO_TAGS, MOCK_NORMALIZED } from "./fixtures";

describe("normalizeQuiz", () => {
  it("flattens all sections into a single array", () => {
    const result = normalizeQuiz(MOCK_QUIZ);
    expect(result).toHaveLength(5);
  });

  it("normalizes true/false questions correctly", () => {
    const result = normalizeQuiz(MOCK_QUIZ);
    const tf = result.filter((q) => q.sectionType === "true_false");
    expect(tf).toHaveLength(2);
    expect(tf[0]!.correctAnswer).toBe("true");
    expect(tf[1]!.correctAnswer).toBe("false");
  });

  it("normalizes multiple choice questions with string answer index", () => {
    const result = normalizeQuiz(MOCK_QUIZ);
    const mc = result.filter((q) => q.sectionType === "multiple_choice");
    expect(mc).toHaveLength(2);
    expect(mc[0]!.correctAnswer).toBe("0");
    expect(mc[0]!.options).toHaveLength(4);
  });

  it("preserves code field on MC questions", () => {
    const result = normalizeQuiz(MOCK_QUIZ);
    const withCode = result.find((q) => q.id === "MC-2");
    expect(withCode?.code).toContain("Partial");
  });

  it("normalizes short answer with model_answer as correctAnswer", () => {
    const result = normalizeQuiz(MOCK_QUIZ);
    const sa = result.find((q) => q.sectionType === "short_answer");
    expect(sa?.correctAnswer).toContain("unknown requires type narrowing");
    expect(sa?.explanation).toBe("");
  });

  it("carries tags through normalization", () => {
    const result = normalizeQuiz(MOCK_QUIZ);
    const tf1 = result.find((q) => q.id === "TF-1");
    expect(tf1?.tags).toEqual(["typescript-basics"]);

    const mc1 = result.find((q) => q.id === "MC-1");
    expect(mc1?.tags).toEqual(["type-narrowing", "typeof-operator"]);
  });

  it("defaults tags to empty array when missing", () => {
    const result = normalizeQuiz(MOCK_QUIZ_NO_TAGS);
    expect(result[0]!.tags).toEqual([]);
  });
});

describe("filterBySection", () => {
  it("returns only true_false questions", () => {
    const tf = filterBySection(MOCK_NORMALIZED, "true_false");
    expect(tf).toHaveLength(2);
    expect(tf.every((q) => q.sectionType === "true_false")).toBe(true);
  });

  it("returns only multiple_choice questions", () => {
    const mc = filterBySection(MOCK_NORMALIZED, "multiple_choice");
    expect(mc).toHaveLength(2);
  });

  it("returns only short_answer questions", () => {
    const sa = filterBySection(MOCK_NORMALIZED, "short_answer");
    expect(sa).toHaveLength(1);
  });
});

describe("filterByTags", () => {
  it("returns all questions when no tags selected", () => {
    const result = filterByTags(MOCK_NORMALIZED, new Set());
    expect(result).toHaveLength(5);
  });

  it("filters to questions matching a single tag", () => {
    const result = filterByTags(MOCK_NORMALIZED, new Set(["any-type"]));
    expect(result).toHaveLength(2); // TF-2 and SA-1
    expect(result.map((q) => q.id).sort()).toEqual(["SA-1", "TF-2"]);
  });

  it("uses OR logic across multiple tags", () => {
    const result = filterByTags(
      MOCK_NORMALIZED,
      new Set(["typeof-operator", "utility-types"]),
    );
    expect(result).toHaveLength(2); // MC-1 and MC-2
  });

  it("returns empty array when no questions match", () => {
    const result = filterByTags(MOCK_NORMALIZED, new Set(["nonexistent-tag"]));
    expect(result).toHaveLength(0);
  });
});

describe("collectTags", () => {
  it("returns all unique tags sorted alphabetically", () => {
    const tags = collectTags(MOCK_NORMALIZED);
    expect(tags).toEqual([
      "any-type",
      "generics",
      "type-narrowing",
      "typeof-operator",
      "typescript-basics",
      "unknown-type",
      "utility-types",
    ]);
  });

  it("returns empty array for tagless questions", () => {
    const tagless = MOCK_NORMALIZED.map((q) => ({ ...q, tags: [] }));
    expect(collectTags(tagless)).toEqual([]);
  });
});

describe("sampleQuiz", () => {
  it("samples the requested number of each type", () => {
    const result = sampleQuiz(MOCK_NORMALIZED, { tf: 1, mc: 1, sa: 1 });
    expect(result).toHaveLength(3);

    const types = result.map((q) => q.sectionType);
    expect(types.filter((t) => t === "true_false")).toHaveLength(1);
    expect(types.filter((t) => t === "multiple_choice")).toHaveLength(1);
    expect(types.filter((t) => t === "short_answer")).toHaveLength(1);
  });

  it("clamps to available questions when count exceeds pool", () => {
    const result = sampleQuiz(MOCK_NORMALIZED, { tf: 100, mc: 100, sa: 100 });
    expect(result).toHaveLength(5);
  });

  it("returns empty array when all counts are zero", () => {
    const result = sampleQuiz(MOCK_NORMALIZED, { tf: 0, mc: 0, sa: 0 });
    expect(result).toHaveLength(0);
  });
});

describe("TAG_CATEGORIES", () => {
  it("has expected top-level categories", () => {
    const keys = Object.keys(TAG_CATEGORIES);
    expect(keys).toContain("Fundamentals");
    expect(keys).toContain("Advanced");
    expect(keys).toContain("Narrowing");
  });

  it("contains no duplicate tags across categories", () => {
    const allTags = Object.values(TAG_CATEGORIES).flat();
    const unique = new Set(allTags);
    expect(allTags.length).toBe(unique.size);
  });
});
