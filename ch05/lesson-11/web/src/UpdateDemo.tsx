// #region all
import { useState } from "react";

export function UpdateDemo() {
// #region updates
  const [count, setCount] = useState(0);
  function replaceTwice() {
    setCount(count + 1);
    setCount(count + 1);
  }
  function updateTwice() {
    setCount((prev) => prev + 1);
    setCount((prev) => prev + 1);
  }
// #endregion updates
  return (
    <section>
      <p>说明用计数：{count}</p>
      <button type="button" onClick={replaceTwice}>两次传入下一值</button>
      <button type="button" onClick={updateTwice}>两次传入更新函数</button>
      <button type="button" onClick={() => setCount(0)}>归零</button>
    </section>
  );
}
// #endregion all
