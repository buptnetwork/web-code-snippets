// #region all
import { useState } from "react";
import type { FormEvent } from "react";
import { validateDraft } from "./form-model";
import type { CreateDraft, CreateInput } from "./form-model";

interface CreateFormProps {
  onCreate: (input: CreateInput) => void;
}

export function CreateForm({ onCreate }: CreateFormProps) {
// #region states
  const [draft, setDraft] = useState<CreateDraft>({ title: "", body: "" });
  const [attempted, setAttempted] = useState(false);
  const errors = validateDraft(draft);
// #endregion states

// #region submit
  function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setAttempted(true);
    if (errors.title || errors.body) return;
    onCreate({ title: draft.title, body: draft.body, tags: [] });
  }
// #endregion submit

// #region clear
  function clearDraft() {
    setDraft({ title: "", body: "" });
    setAttempted(false);
  }
// #endregion clear

  return (
    <form noValidate onSubmit={handleSubmit}>
      <h2>创建输入 · 仅本地演示</h2>
      <label htmlFor="create-title">标题</label>
      <input
        id="create-title"
        value={draft.title}
        aria-invalid={attempted && Boolean(errors.title)}
        aria-describedby="title-hint"
        onChange={(event) => {
          const value = event.currentTarget.value;
          setDraft((prev) => ({ ...prev, title: value }));
        }}
      />
      <p id="title-hint">
        {attempted && errors.title ? errors.title : "标题去首尾空白后 5–200 个字符"}
      </p>
      <label htmlFor="create-body">正文</label>
      <textarea
        id="create-body"
        value={draft.body}
        aria-invalid={attempted && Boolean(errors.body)}
        aria-describedby="body-hint"
        onChange={(event) => {
          const value = event.currentTarget.value;
          setDraft((prev) => ({ ...prev, body: value }));
        }}
      />
      <p id="body-hint">
        {attempted && errors.body ? errors.body : "正文去首尾空白后 10–20000 个字符"}
      </p>
      <button type="submit">查看本地提交结果</button>
      <button type="button" onClick={clearDraft}>清空草稿</button>
      {attempted && Boolean(errors.title || errors.body) && (
        <p role="alert">请按字段提示修改，输入内容已保留。</p>
      )}
    </form>
  );
}
// #endregion all
