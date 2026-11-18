// #region all
import { useState } from "react";
import type { QuestionItem } from "./contracts";
import type { CreateInput } from "./form-model";
import { questions } from "./data";
import { filterQuestions } from "./rules";
import { QuestionList } from "./QuestionList";
import { SearchBox } from "./SearchBox";
import { CreateForm } from "./CreateForm";

export function App() {
// #region states
  const [items, setItems] = useState<QuestionItem[]>(questions);
  const [keyword, setKeyword] = useState("");
  const [lastSubmission, setLastSubmission] = useState<CreateInput | null>(null);
  const visibleQuestions = filterQuestions(items, keyword);
// #endregion states

// #region callbacks
  function handleKeywordChange(value: string) {
    setKeyword(value);
  }
// #region collection
  function reverseItems() {
    setItems((prev) => [...prev].reverse());
  }
  function removeFirst() {
    const first = items[0];
    if (!first) return;
    setItems((prev) => prev.filter((question) => question.id !== first.id));
  }
// #endregion collection
  function handleCreate(input: CreateInput) {
    setLastSubmission(input);
  }
// #endregion callbacks

  return (
    <main>
      <h1>问答页面 · React 本地交互</h1>
      <p>固定数据只在本页内存中变化；表单结果不是数据库记录。</p>
      <SearchBox value={keyword} onValueChange={handleKeywordChange} />
      <p role="status">本地匹配：{visibleQuestions.length} 条</p>
      <button type="button" onClick={reverseItems}>反转本地原列表</button>
      <button type="button" onClick={removeFirst} disabled={items.length === 0}>
        移除原列表第一条
      </button>
      <QuestionList items={visibleQuestions} />
      <CreateForm onCreate={handleCreate} />
      <section aria-label="上次本地提交结果">
        <h2>上次本地提交结果 · 未发送服务器</h2>
        {lastSubmission === null ? (
          <p>尚无本地提交</p>
        ) : (
          <div role="status">
            <p>本地入参已记录；不是服务端成功响应。</p>
            <p>标题：{lastSubmission.title}</p>
            <p className="preserve-text">正文：{lastSubmission.body}</p>
            <p>标签项数：{lastSubmission.tags.length}</p>
          </div>
        )}
      </section>
    </main>
  );
}
// #endregion all
