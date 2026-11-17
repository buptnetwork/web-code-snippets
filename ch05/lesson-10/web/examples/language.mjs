// 独立语法示例；每个块使用自己的局部绑定，不接入页面入口。
import { questions } from "../stages/03-modules/data.js";
import { formatCount } from "../stages/03-modules/rules.js";

{
  // #region values
  let keyword = "SQL";
  keyword = "Python";
  const pageSize = 20;
  const hasResults = true;
  let selectedId = null;
  let lastKeyword;
  // #endregion values
  console.log(keyword, pageSize, hasResults, selectedId, lastKeyword);
}
{
  // #region access
  const firstQuestion = questions[0];
  console.log(firstQuestion.id);       // 102
  console.log(firstQuestion.title);    // SQL 查询从哪里开始？
  console.log(firstQuestion["title"]); // 同一个标题
  console.log(firstQuestion.tags[0]);  // python
  console.log(questions.length);       // 2
  console.log(questions[2]);           // undefined
  // #endregion access
}
{
  // #region condition
  const count = questions.length;
  console.log(count > 0);         // true
  console.log(102 === 102);       // true
  console.log(102 === "102");     // false
  let message;
  if (count === 0) {
    message = "没有匹配问题";
  } else {
    message = `共 ${count} 条问题`;
  }
  console.log(message);          // 共 2 条问题
  // #endregion condition
}
{
  const count = 2;
  // #region ternary
  const message = count === 0 ? "没有匹配问题" : `共 ${count} 条问题`;
  // #endregion ternary
  console.log(message);
}
{
  // #region arrow
  const normalizeKeyword = (value) => value.trim().toLowerCase();
  console.log(normalizeKeyword("  SQL  ")); // sql
  // #endregion arrow
}
// #region callback
function showResult(value, formatter) {
  const text = formatter(value);
  console.log(text);
}
showResult(2, formatCount); // 共 2 条问题
// #endregion callback

export function callbackError() {
  // #region callback-error
  showResult(2, formatCount(2)); // 预期 TypeError
  // #endregion callback-error
}
{
  // #region map
  const titles = questions.map((question) => question.title);
  console.log(titles);
  // ["SQL 查询从哪里开始？", "Python 如何读取问题列表？"]
  console.log(titles.join(" / "));
  // SQL 查询从哪里开始？ / Python 如何读取问题列表？
  // #endregion map
}
{
  // #region missing-return
  const titles = questions.map((question) => { question.title; });
  console.log(titles); // [undefined, undefined]
  // #endregion missing-return
}
{
  // #region find
  const found = questions.find((question) => question.id === 101);
  console.log(found.title); // Python 如何读取问题列表？
  const missing = questions.find((question) => question.id === 999);
  if (missing === undefined) {
    console.log("没有找到这条问题");
  } else {
    console.log(missing.title);
  }
  // #endregion find
}
{
  // #region alias
  const original = { title: "原标题", tags: ["python"] };
  const alias = original;
  alias.title = "改后的标题";
  console.log(original.title);     // 改后的标题
  console.log(alias === original); // true
  // #endregion alias
}
{
  // #region normal-access
  const question = questions[0];
  const id = question.id;
  const title = question.title;
  const first = questions[0];
  // #endregion normal-access
  console.log(id, title, first.id);
}
{
  // #region destructure
  const question = questions[0];
  const { id, title } = question;
  const [first] = questions;
  // #endregion destructure
  console.log(id, title, first === questions[0]);
}
{
  // #region shallow
  const original = { title: "原标题", tags: ["python"] };
  const shallow = { ...original, title: "新标题" };
  console.log(original.title);                  // 原标题
  console.log(shallow === original);            // false
  console.log(shallow.tags === original.tags);  // true
  shallow.tags.push("sql");
  console.log(original.tags);                   // ["python", "sql"]
  // #endregion shallow
}
{
  // #region nested-copy
  const original = { title: "原标题", tags: ["python"] };
  const independent = {
    ...original,
    title: "新标题",
    tags: [...original.tags, "sql"],
  };
  console.log(original.tags);    // ["python"]
  console.log(independent.tags); // ["python", "sql"]
  // #endregion nested-copy
}
{
  // #region array-copy
  const copied = [...questions];
  console.log(copied === questions);       // false
  console.log(copied[0] === questions[0]);  // true
  // #endregion array-copy
}
