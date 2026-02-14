import type {
  Quiz,
  NormalizedQuestion,
  TFQuestion,
  MCQuestion,
  SAQuestion,
} from "./types";

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
          });
        }
        break;
    }
  }

  return out;
}

/**
 * Filter normalized questions to a specific section type.
 */
export function filterBySection(
  questions: NormalizedQuestion[],
  type: "true_false" | "multiple_choice" | "short_answer",
): NormalizedQuestion[] {
  return questions.filter((q) => q.sectionType === type);
}

function shuffle<T>(arr: T[]): T[] {
  const a = [...arr];
  for (let i = a.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [a[i], a[j]] = [a[j], a[i]];
  }
  return a;
}

/**
 * Sample a subset of questions by section type counts.
 * Questions are selected randomly within each section,
 * then concatenated in TF → MC → SA order.
 */
export function sampleQuiz(
  questions: NormalizedQuestion[],
  counts: { tf: number; mc: number; sa: number },
): NormalizedQuestion[] {
  const tf = shuffle(filterBySection(questions, "true_false")).slice(0, counts.tf);
  const mc = shuffle(filterBySection(questions, "multiple_choice")).slice(0, counts.mc);
  const sa = shuffle(filterBySection(questions, "short_answer")).slice(0, counts.sa);
  return [...tf, ...mc, ...sa];
}