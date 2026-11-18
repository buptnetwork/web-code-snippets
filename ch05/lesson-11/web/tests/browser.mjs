import assert from 'node:assert/strict';
import { mkdir, writeFile } from 'node:fs/promises';
import { chromium } from 'playwright-core';

const base = new URL(process.env.L11_BASE_URL || 'http://127.0.0.1:5181');
assert.ok(base.protocol === 'http:' && ['localhost', '127.0.0.1', '[::1]'].includes(base.hostname), '只对本机 HTTP 教学服务运行');
const out = new URL('../.artifacts/', import.meta.url);
await mkdir(out, { recursive: true });
const results = [];
function equal(actual, expected, label) {
  assert.deepEqual(actual, expected, label);
  results.push(label);
}
function ok(actual, label) { equal(Boolean(actual), true, label); }
const titles = ['SQL 查询从哪里开始？', 'Python 如何读取问题列表？'];
const browser = await chromium.launch({ channel: 'chrome', headless: true });
try {
  const page = await browser.newPage({ viewport: { width: 1440, height: 1000 } });
  const errors = [];
  const logs = [];
  const businessRequests = [];
  page.on('response', (response) => {
    if (response.status() >= 400) errors.push(`资源响应 ${response.status()} ${response.url()}`);
  });
  page.on('pageerror', (error) => errors.push(error.message));
  page.on('console', (message) => {
    if (['error', 'warning'].includes(message.type())) errors.push({ text: message.text(), location: message.location() });
    if (message.text().startsWith('调用')) logs.push(message.text());
  });
  page.on('request', (request) => {
    if (request.method() !== 'GET' || /\/questions(?:[/?]|$)/.test(request.url())) businessRequests.push({ method: request.method(), url: request.url() });
  });
  const open = async (stage = '') => {
    await page.goto(new URL(`/${stage ? `?stage=${stage}` : ''}`, base).href, { waitUntil: 'networkidle' });
    await page.locator('#root > *').first().waitFor();
  };
  const ids = () => page.locator('[data-qid]').evaluateAll((nodes) => nodes.map((n) => Number(n.dataset.qid)));
  const expanded = (id) => page.locator(`[data-qid="${id}"] button`).getAttribute('aria-expanded');
  await open('static');
  equal(await page.locator('h2').textContent(), titles[0], '静态卡片');
  for (const stage of ['props', 'object']) {
    await open(stage);
    equal(await page.locator('h2').allTextContents(), titles, `${stage} 显示两条不同数据`);
  }
  await open('click');
  await page.locator('[data-qid="102"] button').click();
  equal(await expanded(102), 'true', '直接传值独立点击后展开');
  equal(await expanded(101), 'false', '起始版本卡片状态独立');
  await page.locator('[data-qid="102"] button').click();
  equal(await expanded(102), 'false', '直接传值再次点击后收起');
  await open('snapshot');
  await page.getByRole('button', { name: '已收起' }).click();
  equal(logs.splice(0), ['调用前 false', '调用后 false'], '第一次快照日志');
  ok(await page.getByRole('button', { name: '已展开' }).isVisible(), '快照下一次界面');
  await page.getByRole('button', { name: '已展开' }).click();
  equal(logs.splice(0), ['调用前 true', '调用后 true'], '第二次快照日志');
  await open('update');
  await page.getByRole('button', { name: '两次传入下一值' }).click();
  equal(await page.locator('section p').textContent(), '说明用计数：1', '同一事件两次传值为1');
  await page.getByRole('button', { name: '归零' }).click();
  equal(await page.locator('section p').textContent(), '说明用计数：0', '更新对照独立归零');
  await page.getByRole('button', { name: '两次传入更新函数' }).click();
  equal(await page.locator('section p').textContent(), '说明用计数：2', '两次函数式更新为2');
  for (const stage of ['search', 'communication', '']) {
    await open(stage);
    const input = page.getByLabel('关键词', { exact: true });
    for (const [text, expected] of [['  SQL  ', [102]], ['python', [101]], ['数据库', [101]], ['不存在', []], ['  ', [102, 101]], ['', [102, 101]]]) {
      await input.fill(text);
      equal(await ids(), expected, `${stage || 'App'} 筛选：${JSON.stringify(text)}`);
      equal(await input.inputValue(), text, `${stage || 'App'} 保留输入：${JSON.stringify(text)}`);
    }
  }
  await page.locator('[data-qid="101"] button').click();
  equal(await expanded(101), 'true', '卡片101展开');
  equal(await expanded(102), 'false', '最终版本卡片状态独立');
  await page.getByRole('button', { name: '反转本地原列表' }).click();
  equal(await ids(), [101, 102], '反转集合');
  equal(await expanded(101), 'true', '稳定key重排保留身份');
  await open();
  await page.locator('[data-qid="101"] button').click();
  await page.getByRole('button', { name: '移除原列表第一条' }).click();
  equal(await ids(), [101], '移除本地102');
  equal(await expanded(101), 'true', '稳定key删除保留101');
  await page.getByLabel('关键词', { exact: true }).fill('SQL');
  equal(await ids(), [], '筛掉101导致卸载');
  await page.getByLabel('关键词', { exact: true }).fill('');
  equal(await expanded(101), 'false', '重新出现从初值开始');
  equal(await ids(), [101], '清空搜索不恢复已删除的102');
  await page.getByRole('button', { name: '移除原列表第一条' }).click();
  equal(await ids(), [], '移除到空列表');
  ok(await page.getByRole('button', { name: '移除原列表第一条' }).isDisabled(), '空集合禁用移除');
  await page.getByRole('button', { name: '反转本地原列表' }).click();
  equal(await ids(), [], '空集合反转仍为空');
  await open('index');
  await page.locator('[data-qid="101"] button').click();
  await page.getByRole('button', { name: '反转', exact: true }).click();
  equal(await expanded(102), 'true', 'index对照展开跟随位置变成102');
  equal(await expanded(101), 'false', 'index对照101失去展开状态');
  await open();
  equal(await ids(), [102, 101], '刷新恢复种子');
  const result = page.getByRole('region', { name: '上次本地提交结果' });
  const title = page.getByLabel('标题', { exact: true });
  const body = page.getByLabel('正文', { exact: true });
  const submit = page.getByRole('button', { name: '查看本地提交结果' });
  const initialUrl = page.url();
  await submit.click();
  equal(await title.getAttribute('aria-invalid'), 'true', '空标题提交错误');
  equal(await body.getAttribute('aria-invalid'), 'true', '空正文提交错误');
  ok((await result.textContent()).includes('尚无本地提交'), '无效输入未产生结果');
  await title.fill('短');
  const validBody = '希望理解组件状态如何驱动当前页面的变化。';
  await body.fill(validBody);
  await submit.click();
  equal(await body.inputValue(), validBody, '失败保留正文');
  equal(await title.getAttribute('aria-invalid'), 'true', '短标题仍错误');
  const validTitle = '  React 如何更新问题列表？  ';
  await title.fill(validTitle);
  await title.press('Enter');
  ok((await result.textContent()).includes(`标题：${validTitle}`), 'Enter合法提交保留原文');
  ok((await result.textContent()).includes('标签项数：0'), '本地输入tags为空');
  equal(page.url(), initialUrl, '表单提交不导航');
  const previous = await result.textContent();
  await title.fill('这是编辑中的新标题');
  equal(await result.textContent(), previous, '草稿编辑不改历史结果');
  await title.fill('短');
  await submit.click();
  equal(await result.textContent(), previous, '后续非法提交不覆盖上次结果');
  await page.getByRole('button', { name: '清空草稿' }).click();
  equal(await title.inputValue(), '', '普通按钮清空标题');
  equal(await body.inputValue(), '', '普通按钮清空正文');
  equal(await title.getAttribute('aria-invalid'), 'false', '清空恢复未尝试状态');
  equal(await result.textContent(), previous, '清空不提交且保留上次结果');
  await title.fill('<strong>只是文本</strong>');
  await body.fill(validBody);
  await body.press('End');
  await body.press('Enter');
  await body.pressSequentially('这是保留的第二行。');
  equal(await result.textContent(), previous, 'textarea Enter换行而不提交');
  await submit.click();
  ok((await result.textContent()).includes('<strong>只是文本</strong>'), '文本插值保留尖括号');
  equal(await result.locator('strong').count(), 0, '文本插值未创建HTML元素');
  equal(await body.inputValue(), validBody + '\n这是保留的第二行。', '正文保留换行');
  ok((await result.textContent()).includes(validBody + '\n这是保留的第二行。'), '结果仍保留正文换行');
  equal(await ids(), [102, 101], '本地表单未伪造问题记录');
  await page.evaluate(() => document.fonts.ready);
  await page.screenshot({ path: new URL('form-result.png', out).pathname, fullPage: true });
  await result.screenshot({ path: new URL('result-region.png', out).pathname });
  await page.reload({ waitUntil: 'networkidle' });
  equal(await title.inputValue(), '', '刷新清空草稿');
  ok((await result.textContent()).includes('尚无本地提交'), '刷新清空历史结果');
  await open('unknown');
  ok(await title.isVisible(), '未知阶段安全回到完整App');
  equal(businessRequests, [], '交互没有业务请求或写请求');
  equal(errors, [], '浏览器无运行异常、资源错误或React警告');
  const report = { base: base.href, browser: browser.version(), tests: results.length, passed: results, errors, businessRequests, scope: '真实浏览器行为；类型与构建另验，未验证React DevTools' };
  await writeFile(new URL(base.port === '4181' ? 'preview.json' : 'browser.json', out), JSON.stringify(report, null, 2));
  console.log(JSON.stringify(report, null, 2));
} finally {
  await browser.close();
}
