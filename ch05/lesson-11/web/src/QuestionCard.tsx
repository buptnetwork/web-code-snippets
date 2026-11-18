// #region all
import { useState } from "react";
import type { QuestionItem } from "./contracts";

interface QuestionCardProps {
  question: QuestionItem;
}

export function QuestionCard({ question }: QuestionCardProps) {
// #region state
  const [expanded, setExpanded] = useState(false);
  function toggle() {
    setExpanded((prev) => !prev);
  }
// #endregion state
  return (
// #region view
    <article className="question-card" data-qid={question.id}>
      <h2>{question.title}</h2>
      <p>标签：{question.tags.join("、")}</p>
      <button type="button" aria-expanded={expanded} onClick={toggle}>
        {expanded ? "收起正文" : "展开正文"}
      </button>
      {expanded && <p>{question.body}</p>}
    </article>
// #endregion view
  );
}
// #endregion all
