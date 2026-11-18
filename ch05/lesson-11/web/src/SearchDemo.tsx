// #region all
import { useState } from "react";
import { questions } from "./data";
import { filterQuestions } from "./rules";
import { QuestionList } from "./QuestionList";

export function SearchDemo() {
  const [keyword, setKeyword] = useState("");
  const visibleQuestions = filterQuestions(questions, keyword);
  return (
    <section>
      <label htmlFor="demo-keyword">关键词</label>
      <input
        id="demo-keyword"
        value={keyword}
        onChange={(event) => setKeyword(event.currentTarget.value)}
      />
      <p>本地匹配：{visibleQuestions.length} 条</p>
      <QuestionList items={visibleQuestions} />
    </section>
  );
}
// #endregion all
