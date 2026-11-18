// #region all
import type { QuestionItem } from "./contracts";
import { QuestionCard } from "./QuestionCard";

interface QuestionListProps {
  items: QuestionItem[];
}

export function QuestionList({ items }: QuestionListProps) {
  if (items.length === 0) {
    return <p>没有匹配问题</p>;
  }
  return (
    <ul id="question-list">
      {items.map((question) => (
        <li key={question.id}>
          <QuestionCard question={question} />
        </li>
      ))}
    </ul>
  );
}
// #endregion all
