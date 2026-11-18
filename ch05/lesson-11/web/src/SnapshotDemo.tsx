// #region all
import { useState } from "react";

export function SnapshotDemo() {
  const [expanded, setExpanded] = useState(false);
  function toggle() {
    console.log("调用前", expanded);
    setExpanded(!expanded);
    console.log("调用后", expanded);
  }
  return (
    <button type="button" onClick={toggle}>
      {expanded ? "已展开" : "已收起"}
    </button>
  );
}
// #endregion all
