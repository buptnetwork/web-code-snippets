// #region imports
import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import { App } from "./App";
import { Stage } from "./Stage";
import "./style.css";
// #endregion imports

// 阶段选择只服务教师演示，不作为 Router 教学。
const stage = new URLSearchParams(location.search).get("stage");
const content = stage ? <Stage name={stage} /> : <App />;

// #region mount
const container = document.querySelector("#root");
if (!container) {
  throw new Error("页面缺少 root 容器");
}
createRoot(container).render(
  <StrictMode>{content}</StrictMode>,
);
// #endregion mount
