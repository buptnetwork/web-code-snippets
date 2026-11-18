// #region all
// #region types
export interface CreateDraft {
  title: string;
  body: string;
}

export interface CreateInput {
  title: string;
  body: string;
  tags: string[];
}
// #endregion types

// #region validate
export function validateDraft(draft: CreateDraft) {
  const titleLength = Array.from(draft.title.trim()).length;
  const bodyLength = Array.from(draft.body.trim()).length;
  return {
    title: titleLength < 5 || titleLength > 200
      ? "标题去首尾空白后需 5–200 个字符" : "",
    body: bodyLength < 10 || bodyLength > 20000
      ? "正文去首尾空白后需 10–20000 个字符" : "",
  };
}
// #endregion validate
// #endregion all
