import type { QuestionItem } from "./contracts";

// #region rename
export function rename102(questions: QuestionItem[]) {
  return questions.map((question) =>
    question.id === 102
      ? { ...question, title: "SQL 查询的第一步" }
      : question,
  );
}
// #endregion rename

// #region tags
export function addTag102(questions: QuestionItem[]) {
  return questions.map((question) =>
    question.id === 102
      ? { ...question, tags: [...question.tags, "sql"] }
      : question,
  );
}
// #endregion tags
