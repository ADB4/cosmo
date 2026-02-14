import type { Quiz, NormalizedQuestion, ChatMessage } from "../lib/types";

export const MOCK_QUIZ: Quiz = {
  id: "test-quiz",
  title: "TypeScript Fundamentals",
  scope: "Weeks 1-2",
  readings: ["handbook.md"],
  scoring_note: "Standard scoring",
  sections: [
    {
      type: "true_false",
      title: "True / False",
      questions: [
        {
          id: "TF-1",
          question: "TypeScript is a superset of JavaScript.",
          answer: true,
          explanation: "TypeScript extends JavaScript with static types.",
          tags: ["typescript-basics"],
        },
        {
          id: "TF-2",
          question: "The `any` type provides type safety.",
          answer: false,
          explanation: "any disables type checking entirely.",
          tags: ["any-type", "typescript-basics"],
        },
      ],
    },
    {
      type: "multiple_choice",
      title: "Multiple Choice",
      questions: [
        {
          id: "MC-1",
          question: "Which keyword narrows a type at runtime?",
          options: ["typeof", "keyof", "infer", "extends"],
          answer: 0,
          explanation: "typeof is a runtime operator that narrows types.",
          tags: ["type-narrowing", "typeof-operator"],
        },
        {
          id: "MC-2",
          question: "What does `Partial<T>` do?",
          code: "type P = Partial<{ a: number; b: string }>;",
          options: [
            "Makes all properties optional",
            "Makes all properties required",
            "Removes all properties",
            "Freezes the type",
          ],
          answer: 0,
          explanation: "Partial makes every property in T optional.",
          tags: ["utility-types", "generics"],
        },
      ],
    },
    {
      type: "short_answer",
      title: "Short Answer",
      questions: [
        {
          id: "SA-1",
          question: "Explain the difference between `unknown` and `any`.",
          model_answer:
            "unknown requires type narrowing before use; any disables all checks.",
          tags: ["unknown-type", "any-type"],
        },
      ],
    },
  ],
};

/** Quiz with no tags on any questions */
export const MOCK_QUIZ_NO_TAGS: Quiz = {
  id: "no-tags-quiz",
  title: "Legacy Quiz",
  scope: "Week 0",
  readings: [],
  scoring_note: "",
  sections: [
    {
      type: "true_false",
      title: "True / False",
      questions: [
        {
          id: "TF-X",
          question: "JavaScript has types.",
          answer: true,
          explanation: "JS has dynamic types.",
        },
      ],
    },
  ],
};

export const MOCK_NORMALIZED: NormalizedQuestion[] = [
  {
    id: "TF-1",
    sectionType: "true_false",
    text: "TypeScript is a superset of JavaScript.",
    options: [],
    correctAnswer: "true",
    explanation: "TypeScript extends JavaScript with static types.",
    tags: ["typescript-basics"],
  },
  {
    id: "TF-2",
    sectionType: "true_false",
    text: "The `any` type provides type safety.",
    options: [],
    correctAnswer: "false",
    explanation: "any disables type checking entirely.",
    tags: ["any-type", "typescript-basics"],
  },
  {
    id: "MC-1",
    sectionType: "multiple_choice",
    text: "Which keyword narrows a type at runtime?",
    options: ["typeof", "keyof", "infer", "extends"],
    correctAnswer: "0",
    explanation: "typeof is a runtime operator that narrows types.",
    tags: ["type-narrowing", "typeof-operator"],
  },
  {
    id: "MC-2",
    sectionType: "multiple_choice",
    text: "What does `Partial<T>` do?",
    code: "type P = Partial<{ a: number; b: string }>;",
    options: [
      "Makes all properties optional",
      "Makes all properties required",
      "Removes all properties",
      "Freezes the type",
    ],
    correctAnswer: "0",
    explanation: "Partial makes every property in T optional.",
    tags: ["utility-types", "generics"],
  },
  {
    id: "SA-1",
    sectionType: "short_answer",
    text: "Explain the difference between `unknown` and `any`.",
    options: [],
    correctAnswer:
      "unknown requires type narrowing before use; any disables all checks.",
    explanation: "",
    tags: ["unknown-type", "any-type"],
  },
];

export const MOCK_MESSAGES: ChatMessage[] = [
  {
    id: "msg-1",
    role: "user",
    content: "Connected to Ollama. Ready to answer questions about your documentation.",
    timestamp: 1700000000000,
  },
  {
    id: "msg-2",
    role: "user",
    content: "What is TypeScript?",
    mode: "qwen-7b",
    timestamp: 1700000001000,
  },
  {
    id: "msg-3",
    role: "assistant",
    content: "TypeScript is a typed superset of JavaScript that compiles to plain JavaScript.",
    mode: "qwen-7b",
    timestamp: 1700000002000,
  },
];
