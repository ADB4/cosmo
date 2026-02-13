import type { QuizData } from "./types";

const SAMPLE_QUIZ: QuizData = {
  title: "React Fundamentals",
  description: "Test your knowledge of React basics",
  questions: [
    {
      id: "TF-1",
      qtype: "tf",
      text: "React uses a virtual DOM to optimize rendering performance.",
      choices: [],
      answer: "T",
      explanation:
        "React maintains a lightweight in-memory representation of the UI (virtual DOM) and uses a diffing algorithm to minimize actual DOM updates.",
    },
    {
      id: "MC-1",
      qtype: "mc",
      text: "Which hook is used to manage component state in React?",
      choices: ["useEffect", "useState", "useContext", "useReducer"],
      answer: "(b)",
      explanation:
        "useState is the primary hook for adding local state to a function component. useReducer also manages state but is intended for more complex state logic.",
    },
    {
      id: "TF-2",
      qtype: "tf",
      text: "useEffect runs before the browser paints the screen.",
      choices: [],
      answer: "F",
      explanation:
        "useEffect runs after paint. useLayoutEffect runs synchronously after DOM mutations but before paint.",
    },
    {
      id: "MC-2",
      qtype: "mc",
      text: "What does the React Compiler (v1.0) primarily automate?",
      choices: [
        "Server-side rendering",
        "Memoization of components and values",
        "Bundle splitting",
        "Type checking",
      ],
      answer: "(b)",
      explanation:
        "The React Compiler automatically applies memoization (the equivalent of React.memo, useMemo, useCallback) so developers don't need to do it manually.",
    },
    {
      id: "SA-1",
      qtype: "sa",
      text: "Explain the difference between controlled and uncontrolled components in React.",
      choices: [],
      answer:
        "A controlled component has its form value driven by React state via value + onChange. An uncontrolled component stores its own state in the DOM and is read via refs.",
      explanation: "",
    },
  ],
};

export default SAMPLE_QUIZ;