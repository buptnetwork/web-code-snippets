import assert from "node:assert/strict";
import test from "node:test";
import { readFile } from "node:fs/promises";
import { fileURLToPath } from "node:url";
import vm from "node:vm";
import ts from "typescript";
import { ESLint } from "eslint";
import { transformWithOxc } from "vite";
import { questions } from "../stages/03-modules/data.js";
import { filterQuestions, formatCount } from "../stages/03-modules/rules.js";
import { loadQuestionList } from "../src/api.js";
import config from "../vite.config.js";

const root = new URL("../", import.meta.url);
const read = (name) => readFile(new URL(name, root), "utf8");
const ids = (items) => items.map((item) => item.id);
async function loadTs(name) {
  const source = await read(name);
  const { outputText } = ts.transpileModule(source, {
    compilerOptions: { module: ts.ModuleKind.ESNext, target: ts.ScriptTarget.ES2022 },
  });
  return import(`data:text/javascript;base64,${Buffer.from(outputText).toString("base64")}`);
}
const tsRules = await loadTs("src/rules.ts");
const tsData = await loadTs("src/data.ts");

for (const [keyword, expected] of [
  ["", [102, 101]], ["  ", [102, 101]], ["  SQL  ", [102]],
  ["python", [101]], ["数据库", [101]], ["不存在", []],
]) {
  test(`JS / TS 筛选结果一致：${JSON.stringify(keyword)}`, () => {
    assert.deepEqual(ids(filterQuestions(questions, keyword)), expected);
    assert.deepEqual(ids(tsRules.filterQuestions(tsData.questions, keyword)), expected);
    assert.deepEqual(ids(questions), [102, 101]);
  });
}
test("JS 与 TS 固定数据一致；文案与数组身份", () => {
  assert.deepEqual(questions, tsData.questions);
  for (const [count, expected] of [[0, "没有匹配问题"], [2, "共 2 条问题"]]) {
    assert.equal(formatCount(count), expected);
    assert.equal(tsRules.formatCount(count), expected);
  }
  const filtered = filterQuestions(questions, "SQL");
  assert.notEqual(filtered, questions);
  assert.equal(filtered[0], questions[0]);
  assert.equal(questions.find((q) => q.id === 101), questions[1]);
  assert.equal(questions.find((q) => q.id === 999), undefined);
});

test("单文件、模块与最终版的 DOM 接线逐区段一致", async () => {
  const single = await read("stages/02-single/main.js");
  const module = await read("stages/03-modules/main.js");
  const final = await read("src/main.js");
  for (const region of ["select", "node", "render", "event"]) {
    const expression = new RegExp(`// #region ${region}\\n([\\s\\S]*?)// #endregion ${region}`);
    assert.equal(single.match(expression)[1], module.match(expression)[1]);
    assert.equal(single.match(expression)[1], final.match(expression)[1]);
  }
});

test("单文件真实源码：节点、提交、清空、文本边界（模拟 DOM）", async () => {
  // 仅是最小 DOM 替身；浏览器交互另验，不把本项称为浏览器验收。
  class Node {
    children = [];
    textContent = "";
    value = "";
    append(...nodes) { this.children.push(...nodes); }
    replaceChildren(...nodes) { this.children = nodes; }
    addEventListener(name, callback) { this[name] = callback; }
  }
  const elements = Object.fromEntries(
    ["#search-form", "#keyword", "#question-list", "#summary"].map((id) => [id, new Node()]),
  );
  const context = vm.createContext({
    document: { querySelector: (id) => elements[id], createElement: () => new Node() },
  });
  vm.runInContext(await read("stages/02-single/main.js"), context);
  assert.equal(elements["#question-list"].children.length, 2);
  for (const [value, count] of [["SQL", 1], ["不存在", 0], ["", 2]]) {
    let prevented = false;
    elements["#keyword"].value = value;
    elements["#search-form"].submit({ preventDefault() { prevented = true; } });
    assert.equal(prevented, true);
    assert.equal(elements["#question-list"].children.length, count);
  }
  const text = "<strong>不是标签</strong>";
  const node = vm.runInContext(`createQuestionNode({title:${JSON.stringify(text)},body:"正文",tags:[]})`, context);
  assert.equal(node.children[0].textContent, text);
  assert.equal(node.children[0].children.length, 0);
});

test("独立语言片段的输出、共享引用与预期 TypeError", async () => {
  const source = (await read("examples/language.mjs"))
    .replace(/^import .*;$/gm, "").replace("export function callbackError", "function callbackError");
  const output = [];
  const context = vm.createContext({ questions, formatCount, console: { log: (...args) => output.push(args) } });
  vm.runInContext(source, context);
  assert.ok(output.some((args) => args[0] === "改后的标题"));
  assert.ok(output.some((args) => Array.isArray(args[0]) && args[0].length === 2 && args[0].every((x) => x === undefined)));
  assert.throws(() => vm.runInContext("callbackError()", context), { name: "TypeError" });
  assert.deepEqual(ids(questions), [102, 101]);
});

test("故障 TS 得到 TS2322；Vite 转换仍成功", async () => {
  const filename = fileURLToPath(new URL("examples/type-error.ts", root));
  const program = ts.createProgram([filename], { strict: true, noEmit: true, skipLibCheck: true });
  assert.ok(ts.getPreEmitDiagnostics(program).some((diagnostic) => diagnostic.code === 2322));
  const result = await transformWithOxc(await read("examples/type-error.ts"), filename);
  assert.match(result.code, /demoCount\s*=\s*["']2["']/);
  assert.doesNotMatch(result.code, /: number/);
  const options = { strict: true, noEmit: true, skipLibCheck: true };
  const host = ts.createCompilerHost(options);
  const originalRead = host.readFile.bind(host);
  const corrected = (await read("examples/type-error.ts")).replace('= "2"', '= 2');
  host.readFile = (path) => path === filename ? corrected : originalRead(path);
  const fixed = ts.createProgram([filename], options, host);
  assert.equal(ts.getPreEmitDiagnostics(fixed).length, 0);
});

test("ESLint 诊断拼写错误，恢复拼写后通过同一规则", async () => {
  const eslint = new ESLint({ cwd: fileURLToPath(root) });
  const text = await read("examples/lint-error.js");
  const [bad] = await eslint.lintText(text, { filePath: "src/diagnostic.js" });
  assert.ok(bad.messages.some((m) => m.ruleId === "no-undef" && m.message.includes("summmary")));
  const [good] = await eslint.lintText(text.replace("summmary", "summary"), { filePath: "src/diagnostic.js" });
  assert.equal(good.errorCount, 0);
});

test("代理仅匹配问题路径；preview 不继承代理", () => {
  const [pattern] = Object.keys(config.server.proxy);
  const regex = new RegExp(pattern);
  for (const path of ["/questions", "/questions?page=1", "/questions/101"]) assert.ok(regex.test(path));
  assert.equal(regex.test("/questions-extra"), false);
  assert.deepEqual(config.preview.proxy, {});
  const base = "http://127.0.0.1:5173";
  assert.equal(new URL("/questions", base).origin, base);
  for (const url of ["http://127.0.0.1:8000", "http://localhost:5173", "https://127.0.0.1:5173"]) {
    assert.notEqual(new URL(url).origin, base);
  }
});

// 替换 fetch 验证适配器边界，不访问后端，也不伪称 FastAPI 联调。
const page = { items: questions, total: 2, page: 1 };
for (const [name, response, success, fragment] of [
  ["合法列表", () => Response.json(page), true, ""],
  ["空列表", () => Response.json({ items: [], total: 0, page: 1 }), true, ""],
  ["HTTP 错误", () => new Response("失败", { status: 503 }), false, "HTTP 503"],
  ["HTML 回退", () => new Response("<html></html>", { headers: { "Content-Type": "text/html" } }), false, "预期 API JSON"],
  ["错误 JSON", () => new Response("{", { headers: { "Content-Type": "application/json" } }), false, ""],
  ["网络失败", () => { throw new Error("网络不可达"); }, false, "网络不可达"],
  ...[null, [], {}, { ...page, page: 0 }, { ...page, total: -1 },
    { ...page, items: [{ ...questions[0], tags: [1] }] },
    { ...page, items: [{ ...questions[0], id: "102" }] },
  ].map((bad, index) => [`错误形状${index + 1}`, () => Response.json(bad), false, "形状不符合"]),
]) {
  test(`适配器：${name}`, async (t) => {
    t.mock.method(globalThis, "fetch", async (url, options) => {
      assert.equal(url, "/questions?keyword=&page=1&page_size=20");
      assert.equal(options.headers.Accept, "application/json");
      return response();
    });
    const result = await new Promise((resolve) => {
      const immediate = loadQuestionList(
        (value) => resolve({ success: true, value }),
        (value) => resolve({ success: false, value }),
      );
      assert.equal(immediate, undefined);
    });
    assert.equal(result.success, success);
    if (success) assert.ok(Array.isArray(result.value.items));
    else assert.ok(result.value.includes(fragment));
  });
}
