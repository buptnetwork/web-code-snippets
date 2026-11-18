import assert from 'node:assert/strict';
import { test } from 'node:test';
import { readFile } from 'node:fs/promises';
import { fileURLToPath } from 'node:url';
import ts from 'typescript';
import { ESLint } from 'eslint';

// 纯计算模块仅含类型导入；转换后执行真实源码，类型检查另由 tsc 完成。
async function loadModule(file) {
  const source = await readFile(new URL(`../src/${file}`, import.meta.url), 'utf8');
  const { outputText } = ts.transpileModule(source, {
    compilerOptions: { target: ts.ScriptTarget.ES2022, module: ts.ModuleKind.ESNext },
  });
  return import(`data:text/javascript;base64,${Buffer.from(outputText).toString('base64')}`);
}
const { questions } = await loadModule('data.ts');
const { filterQuestions } = await loadModule('rules.ts');
const { validateDraft } = await loadModule('form-model.ts');
const { rename102, addTag102 } = await loadModule('immutable.ts');
const frozen = Object.freeze(questions.map((q) => Object.freeze({
  ...q, tags: Object.freeze([...q.tags]),
})));

test('固定数据只有五个约定字段，顺序为 102、101', () => {
  assert.deepEqual(questions, [
    { id: 102, title: 'SQL 查询从哪里开始？', body: '希望先弄清表和记录再逐步学习查询语句。', tags: ['python'], created_at: '2026-09-01T08:00:00Z' },
    { id: 101, title: 'Python 如何读取问题列表？', body: '希望理解列表查询如何从数据库取出问题。', tags: ['python', 'sql'], created_at: '2026-09-01T08:00:00Z' },
  ]);
});
for (const [keyword, ids] of [['', [102, 101]], ['  ', [102, 101]], ['  SQL  ', [102]], ['python', [101]], ['数据库', [101]], ['不存在', []]]) {
  test(`纯筛选 ${JSON.stringify(keyword)}，不修改冻结输入`, () => {
    const result = filterQuestions(frozen, keyword);
    assert.deepEqual(result.map((q) => q.id), ids);
    assert.notEqual(result, frozen);
    for (const q of result) assert.equal(q, frozen.find((item) => item.id === q.id));
  });
}
test('修改标题仅复制数组与目标对象，未改标签复用引用', () => {
  const result = rename102(frozen);
  assert.notEqual(result, frozen);
  assert.notEqual(result[0], frozen[0]);
  assert.equal(result[0].title, 'SQL 查询的第一步');
  assert.equal(result[0].tags, frozen[0].tags);
  assert.equal(result[1], frozen[1]);
  assert.equal(frozen[0].title, 'SQL 查询从哪里开始？');
});
test('嵌套更新复制到目标标签数组，旧数据不变', () => {
  const result = addTag102(frozen);
  assert.notEqual(result, frozen);
  assert.notEqual(result[0], frozen[0]);
  assert.notEqual(result[0].tags, frozen[0].tags);
  assert.deepEqual(result[0].tags, ['python', 'sql']);
  assert.deepEqual(frozen[0].tags, ['python']);
  assert.equal(result[1], frozen[1]);
});
for (const length of [0, 4, 5, 200, 201]) {
  test(`标题长度边界 ${length}`, () => {
    assert.equal(Boolean(validateDraft({ title: '甲'.repeat(length), body: '乙'.repeat(10) }).title), length < 5 || length > 200);
  });
}
for (const length of [0, 9, 10, 20000, 20001]) {
  test(`正文长度边界 ${length}`, () => {
    assert.equal(Boolean(validateDraft({ title: '甲'.repeat(5), body: '乙'.repeat(length) }).body), length < 10 || length > 20000);
  });
}
test('校验不写回 trim 结果，码点不等于 UTF-16 码元', () => {
  const draft = Object.freeze({ title: '  甲乙丙丁戊  ', body: ' 正文共有十个汉字测试 ' });
  assert.deepEqual(validateDraft(draft), { title: '', body: '' });
  assert.equal(draft.title, '  甲乙丙丁戊  ');
  assert.ok(validateDraft({ title: '𝒜'.repeat(4), body: '乙'.repeat(10) }).title);
  assert.equal(validateDraft({ title: '𝒜'.repeat(5), body: '乙'.repeat(10) }).title, '');
});
const root = fileURLToPath(new URL('../', import.meta.url));
const eslint = new ESLint({ cwd: root });
test('TSX 条件 Hook 由本包实际配置拒绝', async () => {
  const [result] = await eslint.lintText('import { useState } from "react"; export function Bad({ flag }: { flag: boolean }) { if (flag) useState(0); return <p />; }', { filePath: 'src/ExpectedFailure.tsx' });
  assert.ok(result.messages.some((m) => m.ruleId === 'react-hooks/rules-of-hooks'));
  assert.ok(!result.messages.some((m) => m.fatal));
});
test('依赖规则在独立片段中报告缺失依赖，不污染正确入口', async () => {
  const [result] = await eslint.lintText('import { useEffect } from "react"; export function Bad({ value }: { value: string }) { useEffect(() => { console.log(value); }, []); return <p />; }', { filePath: 'src/ExpectedDependency.tsx' });
  assert.ok(result.messages.some((m) => m.ruleId === 'react-hooks/exhaustive-deps'));
});
test('TypeScript 使用本包配置拒绝错误的对象 props', () => {
  const configPath = fileURLToPath(new URL('../tsconfig.json', import.meta.url));
  const config = ts.readConfigFile(configPath, ts.sys.readFile);
  assert.equal(config.error, undefined);
  const parsed = ts.parseJsonConfigFileContent(config.config, ts.sys, root);
  assert.deepEqual(parsed.errors, []);
  const filename = fileURLToPath(new URL('../src/ExpectedTypeFailure.tsx', import.meta.url));
  const source = 'import { ObjectCard } from "./ObjectCard"; export const bad = <ObjectCard question="wrong" />;';
  const host = ts.createCompilerHost(parsed.options);
  const original = host.getSourceFile.bind(host);
  host.getSourceFile = (path, ...args) => path === filename
    ? ts.createSourceFile(path, source, parsed.options.target, true, ts.ScriptKind.TSX)
    : original(path, ...args);
  const program = ts.createProgram([...parsed.fileNames, filename], parsed.options, host);
  const errors = ts.getPreEmitDiagnostics(program);
  assert.ok(errors.some((error) => error.file?.fileName === filename && error.code === 2322));
  assert.ok(errors.every((error) => error.file?.fileName === filename));
});
