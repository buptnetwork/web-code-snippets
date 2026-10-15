// 第 2 课 · 第六单元安全渲染对照（教师预置的隔离演示页）。
// 与最终 app.js 无关：这里故意同时用 innerHTML 与 textContent，只为观察差别。
// 样本是无害标签，不写攻击脚本、不改共享数据库。

const runEl = document.querySelector('#run');
const statusEl = document.querySelector('#render-status');
const htmlBox = document.querySelector('#html-box');
const textBox = document.querySelector('#text-box');

// 同一段来自"用户输入"的字符串，交给两种写法处理。
const sample = '<strong>这是用户输入，不是页面模板</strong>';

function describeFirstNode(box) {
  const first = box.firstChild;
  if (!first) return '（空）';
  return first.nodeType === 1
    ? `元素节点 <${first.tagName.toLowerCase()}>，显示为「${first.textContent}」`
    : `文本节点「${first.textContent}」`;
}

runEl.addEventListener('click', () => {
  htmlBox.innerHTML = sample;
  textBox.textContent = sample;
  statusEl.textContent = '已写入两个容器，请在 Elements 与 Console 中比较';
  console.log('htmlBox 第一个子节点：', describeFirstNode(htmlBox));
  console.log('textBox 第一个子节点：', describeFirstNode(textBox));
});
