// #region all
import type { QuestionItem } from "./contracts";

export function filterQuestions(
  items: QuestionItem[],
  keyword: string,
): QuestionItem[] {
  const needle = keyword.trim().toLowerCase();
  return items.filter((question) => {
    const titleMatches = question.title.toLowerCase().includes(needle);
    const bodyMatches = question.body.toLowerCase().includes(needle);
    return titleMatches || bodyMatches;
  });
}
// #endregion all
