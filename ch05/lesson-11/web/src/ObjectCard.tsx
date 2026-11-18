// #region all
import type { QuestionItem } from "./contracts";

interface ObjectCardProps {
  question: QuestionItem;
}

export function ObjectCard({ question }: ObjectCardProps) {
  return (
    <article className="question-card" data-qid={question.id}>
      <h2>{question.title}</h2>
      <p>标签：{question.tags.join("、")}</p>
      <p>{question.body}</p>
    </article>
  );
}
// #endregion all
