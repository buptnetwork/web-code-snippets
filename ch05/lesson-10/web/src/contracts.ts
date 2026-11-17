// #region question
export interface QuestionItem {
  id: number;
  title: string;
  body: string;
  tags: string[];
  created_at: string;
}
// #endregion question

// #region page
export interface QuestionListOut {
  items: QuestionItem[];
  total: number;
  page: number;
}
// #endregion page
