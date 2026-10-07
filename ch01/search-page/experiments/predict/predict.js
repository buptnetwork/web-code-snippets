// 第 2 课 · 第五单元预测实验（教师预置的异步入口）。
// 与最终 app.js 无关：这里故意不检查 res.ok、不检查结构、不渲染列表。
// 固定条件：目标状态元素存在、正文完整可读、JSON 场景语法合法。

const runEl = document.querySelector('#run');
const statusEl = document.querySelector('#predict-status');

async function runPrediction() {
  statusEl.textContent = '等待响应';
  try {
    const data = await (await fetch('/questions?keyword=react')).json();
    statusEl.textContent = '已完成 JSON 解析';
    console.log(data);
  } catch {
    statusEl.textContent = '进入 catch';
  }
}

runEl.addEventListener('click', () => { void runPrediction(); });
