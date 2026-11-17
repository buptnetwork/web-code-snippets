// 单文件阶段快照；不导入模块，不同时运行其他阶段入口。
// #region data
const questions = [
  {
    id: 102,
    title: "SQL 查询从哪里开始？",
    body: "希望先弄清表和记录再逐步学习查询语句。",
    tags: ["python"],
    created_at: "2026-09-01T08:00:00Z",
  },
  {
    id: 101,
    title: "Python 如何读取问题列表？",
    body: "希望理解列表查询如何从数据库取出问题。",
    tags: ["python", "sql"],
    created_at: "2026-09-01T08:00:00Z",
  },
];
// #endregion data

// #region format
function formatCount(count) {
  if (count === 0) {
    return "没有匹配问题";
  }
  return `共 ${count} 条问题`;
}
// #endregion format

// #region normalize
function normalizeKeyword(value) {
  return value.trim().toLowerCase();
}
// #endregion normalize

// #region filter
function filterQuestions(items, keyword) {
  const needle = normalizeKeyword(keyword);
  return items.filter((question) => {
    const titleMatches = question.title.toLowerCase().includes(needle);
    const bodyMatches = question.body.toLowerCase().includes(needle);
    return titleMatches || bodyMatches;
  });
}
// #endregion filter

// #region select
const form = document.querySelector("#search-form");
const input = document.querySelector("#keyword");
const list = document.querySelector("#question-list");
const summary = document.querySelector("#summary");

if (!form || !input || !list || !summary) {
  throw new Error("页面缺少搜索表单、输入框、列表或摘要节点");
}
// #endregion select

// #region node
function createQuestionNode(question) {
  const item = document.createElement("li");
  item.className = "question-card";
  const title = document.createElement("h2");
  title.textContent = question.title;
  const body = document.createElement("p");
  body.textContent = question.body;
  const tags = document.createElement("p");
  tags.className = "muted";
  tags.textContent = `标签：${question.tags.join("、")}`;
  item.append(title, body, tags);
  return item;
}
// #endregion node

// #region render
function renderQuestions(items) {
  const nodes = items.map(createQuestionNode);
  list.replaceChildren(...nodes);
  summary.textContent = `本地固定数据：${formatCount(items.length)}`;
}
// #endregion render

// #region event
function handleSubmit(event) {
  event.preventDefault();
  const keyword = input.value;
  const visibleQuestions = filterQuestions(questions, keyword);
  renderQuestions(visibleQuestions);
}

form.addEventListener("submit", handleSubmit);
renderQuestions(questions);
// #endregion event
