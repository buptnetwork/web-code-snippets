// #region imports
import { questions } from "./data.js";
import { filterQuestions, formatCount } from "./rules.js";
// #endregion imports

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
