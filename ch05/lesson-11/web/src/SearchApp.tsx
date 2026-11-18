// #region all
import { useState } from "react";
import { questions } from "./data";
import { filterQuestions } from "./rules";
import { SearchBox } from "./SearchBox";
import { QuestionList } from "./QuestionList";

export function App() {
  const [keyword, setKeyword] = useState("");
  const visibleQuestions = filterQuestions(questions, keyword);

  function handleKeywordChange(value: string) {
    setKeyword(value);
  }

  return (
    <main>
      <h1>问题列表与受控搜索</h1>
      <SearchBox value={keyword} onValueChange={handleKeywordChange} />
      <p>本地匹配：{visibleQuestions.length} 条</p>
      <QuestionList items={visibleQuestions} />
    </main>
  );
}
// #endregion all
