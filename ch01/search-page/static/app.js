// 第 2 课学生工作文件（ served at /static/app.js ）。
// 教师已提供：元素引用、readQuestions、renderQuestions 与一个最小提交入口。
// 学生任务：在下方 region task 内补齐 loading/success/empty/error 四态与恢复，
//          并用它替换最小入口——最终只保留一个提交监听器。

// region elements
const formEl = document.querySelector('#search-form');
const inputEl = document.querySelector('#keyword');
const buttonEl = formEl.querySelector('button');
const statusEl = document.querySelector('#status');
const listEl = document.querySelector('#results');
// endregion elements

// region readQuestions
async function readQuestions(keyword) {
  const query = new URLSearchParams({
    keyword: keyword.trim(), page: '1', page_size: '20',
  });
  let response;
  try {
    response = await fetch(`/questions?${query}`);
  } catch {
    throw new Error('未获得可用响应，请检查连接或稍后重试');
  }
  if (!response.ok) {
    throw new Error(`服务返回 HTTP ${response.status}`);
  }
  let data;
  try {
    data = await response.json();
  } catch {
    throw new Error('响应正文读取或 JSON 解析失败');
  }
  if (!data || !Array.isArray(data.items)
      || !data.items.every(q => q && Number.isInteger(q.id)
        && typeof q.title === 'string' && typeof q.body === 'string')) {
    throw new Error('响应数据结构不符合本页约定');
  }
  return data.items;
}
// endregion readQuestions

// region renderQuestions
function renderQuestions(items) {
  const fragment = document.createDocumentFragment();
  for (const q of items) {
    const li = document.createElement('li');
    const title = document.createElement('h2');
    const body = document.createElement('p');
    title.textContent = q.title;
    body.textContent = q.body;
    li.append(title, body);
    fragment.append(li);
  }
  listEl.replaceChildren(fragment);
}
// endregion renderQuestions

// region task
// 教师阶段的最小入口：只证明正常读取接通，还不是完整四态答案。
// 学生请用 setState + loadQuestions（含 busy 串行与 finally 恢复）替换它；
// 完整参考见 ../reference/app.js，独立尝试后再对照。
formEl.addEventListener('submit', async event => {
  event.preventDefault();
  try {
    const items = await readQuestions(inputEl.value);
    renderQuestions(items);
  } catch (error) {
    statusEl.textContent = error.message;
  }
});
// endregion task
