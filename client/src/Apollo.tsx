import { useState } from "react";
import type { ApolloView, QuizData } from "./types";
import StudyMode from "./StudyMode";
import QuizMode from "./QuizMode";
import SAMPLE_QUIZ from "./sampleQuiz";

export default function Apollo() {
  const [view, setView] = useState<ApolloView>("select");
  const [quizData] = useState<QuizData>(SAMPLE_QUIZ);

  if (view === "study") {
    return <StudyMode quiz={quizData} onExit={() => setView("select")} />;
  }

  if (view === "quiz") {
    return <QuizMode quiz={quizData} onExit={() => setView("select")} />;
  }

  return (
    <div className="apollo-select">
      <div className="apollo-hero">
        <h2 className="apollo-title">{quizData.title}</h2>
        <p className="apollo-desc">{quizData.description}</p>
        <p className="apollo-count">{quizData.questions.length} questions</p>
      </div>

      <div className="apollo-cards">
        <button className="apollo-card" onClick={() => setView("study")}>
          <svg
            className="apollo-card-icon"
            width="32"
            height="32"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth="1.2"
          >
            <path d="M2 3h6a4 4 0 0 1 4 4v14a3 3 0 0 0-3-3H2z" />
            <path d="M22 3h-6a4 4 0 0 0-4 4v14a3 3 0 0 1 3-3h7z" />
          </svg>
          <span className="apollo-card-title">Study Mode</span>
          <span className="apollo-card-desc">
            Review flashcards in random order to reinforce your knowledge
          </span>
        </button>

        <button className="apollo-card" onClick={() => setView("quiz")}>
          <svg
            className="apollo-card-icon"
            width="32"
            height="32"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth="1.2"
          >
            <path d="M6 9H4.5a2.5 2.5 0 0 1 0-5C5.88 4 7 5.12 7 6.5V9" />
            <path d="M18 9h1.5a2.5 2.5 0 0 0 0-5C18.12 4 17 5.12 17 6.5V9" />
            <path d="M4 22h16" />
            <path d="M10 14.66V17c0 .55-.47.98-.97 1.21C7.85 18.75 7 20 7 22" />
            <path d="M14 14.66V17c0 .55.47.98.97 1.21C16.15 18.75 17 20 17 22" />
            <path d="M18 2H6v7a6 6 0 0 0 12 0V2Z" />
          </svg>
          <span className="apollo-card-title">Quiz Mode</span>
          <span className="apollo-card-desc">
            Test yourself and get scored on your answers
          </span>
        </button>
      </div>

      <div className="apollo-tip">
        <span className="apollo-tip-label">Tip:</span> Upload your own quiz
        JSON file to customize the questions
      </div>
    </div>
  );
}