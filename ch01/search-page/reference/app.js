// 第 2 课完整参考（课后对照，不作为学生练习起点）。
// = 教师提供的 elements + readQuestions + renderQuestions
//   + 学生补齐的 setState + loadQuestions（busy 串行、finally 恢复）+ 唯一提交入口。
// 与 static/app.js 的差异只在 region four-state 与 region submit；其余完全相同。

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

// region four-state
let busy = false;

function setState(state, message) {
  statusEl.dataset.state = state;
  statusEl.textContent = message;
  listEl.setAttribute('aria-busy', String(state === 'loading'));
}

async function loadQuestions(keyword) {
  if (busy) return;
  busy = true;
  inputEl.disabled = true;
  buttonEl.disabled = true;
  listEl.replaceChildren();
  setState('loading', '正在加载……');
  try {
    const items = await readQuestions(keyword);
    renderQuestions(items);
    setState(items.length ? 'success' : 'empty',
      items.length ? `本页显示 ${items.length} 条结果` : '没有找到相关问题');
  } catch (error) {
    listEl.replaceChildren();
    setState('error', error instanceof Error ? error.message : '搜索失败，请稍后重试');
    console.error('搜索处理失败：', error);
  } finally {
    busy = false;
    inputEl.disabled = false;
    buttonEl.disabled = false;
    listEl.setAttribute('aria-busy', 'false');
  }
}
// endregion four-state

// region submit
// 最终只保留这一个提交监听器；鼠标点击与输入框回车走同一入口。
formEl.addEventListener('submit', event => {
  event.preventDefault();
  void loadQuestions(inputEl.value);
});
// endregion submit
