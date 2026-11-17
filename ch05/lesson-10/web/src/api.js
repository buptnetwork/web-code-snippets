// #region shape
function isRecord(value) {
  return typeof value === "object" && value !== null && !Array.isArray(value);
}

function isQuestion(value) {
  return isRecord(value)
    && Number.isSafeInteger(value.id)
    && typeof value.title === "string"
    && typeof value.body === "string"
    && Array.isArray(value.tags)
    && value.tags.every((tag) => typeof tag === "string")
    && typeof value.created_at === "string";
}
// #endregion shape

// #region page
function readQuestionList(value) {
  if (!isRecord(value)
    || !Array.isArray(value.items)
    || !value.items.every(isQuestion)
    || !Number.isSafeInteger(value.total) || value.total < 0
    || !Number.isSafeInteger(value.page) || value.page < 1) {
    throw new Error("列表响应形状不符合本课约定");
  }
  return { items: value.items, total: value.total, page: value.page };
}
// #endregion page

// #region request
async function requestQuestionList() {
  const response = await fetch("/questions?keyword=&page=1&page_size=20", {
    headers: { Accept: "application/json" },
  });
  if (!response.ok) {
    throw new Error(`HTTP ${response.status}`);
  }
  const contentType = response.headers.get("content-type") || "";
  if (contentType.split(";")[0].trim().toLowerCase() !== "application/json") {
    throw new Error("预期 API JSON；请检查端口、路径与代理");
  }
  const raw = await response.json();
  return readQuestionList(raw);
}
// #endregion request

// #region callbacks
export function loadQuestionList(onSuccess, onFailure) {
  requestQuestionList().then(
    onSuccess,
    (error) => {
      const message = error instanceof Error ? error.message : "请求未完成";
      onFailure(message);
    },
  );
}
// #endregion callbacks
