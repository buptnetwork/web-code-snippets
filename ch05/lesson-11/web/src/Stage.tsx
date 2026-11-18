import { useState } from "react";
import { App } from "./App";
import { StaticCard } from "./StaticCard";
import { PropsCard } from "./PropsCard";
import { ObjectCard } from "./ObjectCard";
import { QuestionCard } from "./QuestionCard";
import { ClickCard } from "./ClickCard";
import { SnapshotDemo } from "./SnapshotDemo";
import { UpdateDemo } from "./UpdateDemo";
import { SearchDemo } from "./SearchDemo";
import { App as SearchApp } from "./SearchApp";
import { questions } from "./data";

// #region index-demo
function IndexDemo() {
  const [items, setItems] = useState(questions);
  return (
    <>
      <button type="button"
        onClick={() => setItems((prev) => [...prev].reverse())}>
        反转
      </button>
      <ul>{items.map((question, index) => (
        <li key={index}><QuestionCard question={question} /></li>
      ))}</ul>
    </>
  );
}
// #endregion index-demo

// #region props-demo
function PropsDemo() {
  return (
    <>
      {questions.map((question) => (
        <PropsCard key={question.id}
          title={question.title} body={question.body} />
      ))}
    </>
  );
}
// #endregion props-demo

export function Stage({ name }: { name: string }) {
  if (name === "static") return <main><StaticCard /></main>;
  if (name === "props") return <main><PropsDemo /></main>;
  if (name === "object") return <main>{questions.map((question) => (
    <ObjectCard key={question.id} question={question} />
  ))}</main>;
  if (name === "click") return <main>{questions.map((question) => (
    <ClickCard key={question.id} question={question} />
  ))}</main>;
  if (name === "snapshot") return <main><SnapshotDemo /></main>;
  if (name === "update") return <main><UpdateDemo /></main>;
  if (name === "search") return <main><SearchDemo /></main>;
  if (name === "communication") return <SearchApp />;
  if (name === "index") return <main><IndexDemo /></main>;
  return <App />;
}
