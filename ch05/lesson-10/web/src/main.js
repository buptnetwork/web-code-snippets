// #region imports
import { questions } from "./data.ts";
import { filterQuestions, formatCount } from "./rules.ts";
// #endregion imports
import { loadQuestionList } from "./api.js";
import { courseName } from "./public-config.js";

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

// #region api-nodes
const apiButton = document.querySelector("#load-api");
const apiResult = document.querySelector("#api-result");
if (!apiButton || !apiResult) {
  throw new Error("页面缺少后端演示区域");
}
// #endregion api-nodes

// #region api-start
if (import.meta.env.DEV) {
  apiButton.addEventListener("click", () => {
    apiButton.disabled = true;
    apiResult.textContent = "正在读取后端列表……";
// #endregion api-start
    // #region api-callbacks
    loadQuestionList(
      (page) => {
        const ids = page.items.map((question) => question.id).join("、");
        apiResult.textContent = `后端：第 ${page.page} 页，共 ${page.total} 条；本页 ID：${ids}`;
        apiButton.disabled = false;
      },
      (message) => {
        apiResult.textContent = `后端读取未完成：${message}`;
        apiButton.disabled = false;
      },
    );
    // #endregion api-callbacks
// #region api-preview
  });
} else {
  apiButton.disabled = true;
  apiResult.textContent = "静态预览只核对页面；真实 API 演示使用 dev 服务";
}
// #endregion api-preview

// #region config
const configNote = document.createElement("p");
configNote.textContent = `公开配置：${courseName || "未设置课程名称"}`;
summary.after(configNote);
// #endregion config
