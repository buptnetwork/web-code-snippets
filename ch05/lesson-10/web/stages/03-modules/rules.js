// #region normalize
function normalizeKeyword(value) {
  return value.trim().toLowerCase();
}
// #endregion normalize

// #region filter
export function filterQuestions(items, keyword) {
  const needle = normalizeKeyword(keyword);
  return items.filter((question) => {
    const titleMatches = question.title.toLowerCase().includes(needle);
    const bodyMatches = question.body.toLowerCase().includes(needle);
    return titleMatches || bodyMatches;
  });
}
// #endregion filter

// #region format
export function formatCount(count) {
  if (count === 0) {
    return "没有匹配问题";
  }
  return `共 ${count} 条问题`;
}
// #endregion format
