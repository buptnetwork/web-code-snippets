# 第 11 次课教学底稿
## React 组件与渲染机制：状态、引用与身份

---

## 〇、给 PPT 制作团队的全局说明

本次课 100 分钟，留 5 分钟缓冲。**本次课是学生第一次真正理解"框架替我做了什么、又要求我遵守什么"。**

第 10 次课把工程环境搭好了：React + TS 工程可用、`api.d.ts` 就位、`tsc` 和 ESLint 已进 CI。**今天零配置时间，开场即写组件。**

**本次课的核心思想，请让它贯穿始终，并在单元 2、4、6、8 各回引一次**：

> **React 判断"变没变"，靠的是引用比较，不是内容比较。**
>
> **React 判断"是不是同一个东西"，靠的是 key，不是位置。**
>
> **今天的四个 bug，全部来自违反这两条约定。**

这两句要做成开场后的封面级素材。它们不是"两个知识点"，是**同一件事的两面**：React 用两条廉价的判等规则（`Object.is` 和 key 匹配）换来了 O(n) 的 diff，代价是**你必须遵守约定**。

**本次课有三个高光，按重要性排序**：

1. **`key={index}` 导致的内容错位（单元 6，15 分钟）**。这是现场必做。戏剧性在于：界面上的文字和它背后的数据**完全对不上**，而代码里没有任何一行是"错"的——`tsc` 全绿、ESLint 不报、控制台没有警告。这是"类型护栏抓不到的那一类错误"最好的标本。
2. **`useState` 是队列不是变量（单元 5，10 分钟）**。连点三次 `setCount(count+1)` 只加 1。这个演示只要 30 秒，但它颠覆的是学生对"变量"的基本直觉。**快照心智建立不起来，后面的 `useEffect`、闭包陷阱全部讲不通。**
3. **渲染次数守卫（单元 8.5，5 分钟）**。把"渲染次数不随列表长度增长"写成断言——**和第 7/9 次课的 SQL 计数断言结构完全一样**。这一页把三层 N+1 统一起来，是全课程"判据可迁移"这条线的又一次兑现。

**第四处值得重点制作的**：单元 4.5 的 `readonly` 类型。**用类型系统把"不可变约定"从纪律变成编译错误**——这是第 10 次课"类型是最便宜的护栏"的直接应用，也是本次课唯一一处"把纪律变成结构"的落点。作业三要求学生亲手做一遍并量化收益。

**一个必须守住的边界**：本次课**不讲 `useEffect`**。数据获取、副作用、清理函数全部留给后续课次。**看到需要副作用的地方，用"这是下次课的内容"一句带过。** 原因：`useEffect` 的心智依赖今天的快照模型，今天的模型没建立好，讲 `useEffect` 只会制造更多困惑。

**若时间不够的压缩顺序**：先压单元 9 的 C 档卡（整体移课后）→ 再压单元 8 的第三步优化与测试代码（只留思路与 8.5 那张三层表）→ 再压单元 7.3 的"完整做法"（只给判据）。**单元 2、4、5、6 不能压缩。**

---

## 一、开场：从"操作界面"到"描述界面"

**约 4 分钟。**

### 1.1 回到第 2 次课那个页面

**先放第 2 次课的一段代码（学生自己写过的）**：

```js
// 第 2 次课：命令式
function addQuestion(q) {
  const li = document.createElement("li");
  li.textContent = q.title;
  li.dataset.id = q.id;
  list.appendChild(li);
  counter.textContent = `共 ${list.children.length} 条`;   // ← 别忘了更新计数
}

function removeQuestion(id) {
  document.querySelector(`[data-id="${id}"]`)?.remove();
  counter.textContent = `共 ${list.children.length} 条`;   // ← 这里也要
  if (list.children.length === 0) emptyHint.style.display = "block";   // ← 还有这里
}
```

讲：

> 这段代码有一个结构性问题，和它写得好不好无关：
>
> **你在维护两份状态——数据在一处，界面在另一处，而保持它们同步是你的工作。**
>
> 每加一个交互，你都要重新想一遍"它会影响界面的哪些部分"。加到第五个交互，你一定会漏掉一处。
>
> **这不是能力问题，是结构问题。** n 个交互 × m 个界面元素，你要维护 n×m 条更新路径。

**React 的承诺（封面级素材）**：

> **你不操作界面，你只修改状态。界面由状态算出来。**
>
> ```
> UI = f(state)
> ```
>
> 一份状态，一个函数。**n×m 条路径塌缩成 n 次状态修改。**

### 1.2 但这个承诺有前提

停顿，然后：

> 听起来很美。但 React 是一个 JavaScript 库，它没有魔法。
>
> **它怎么知道你的状态变了？**
>
> 答案是：**它不知道，除非你告诉它。而"告诉它"这件事，有两条你必须遵守的约定。**
>
> 今天这节课，一半时间在讲这两条约定是什么，另一半时间在演示违反它们会发生什么。

**开场自检表（醒目页）**：

| 你可能以为 | 今天会看到 |
|---|---|
| `setState` 之后，state 立刻变了 | **单元 5** |
| 改了数组内容，React 会发现 | **单元 2、4** |
| `key` 随便给个 index 就行 | **单元 6** |
| 组件重渲染 = DOM 重建 | **单元 4.2** |
| `memo` 包一下就不重渲染了 | **单元 2、8.3** |

> 这五条里，**前四条是理解问题，第五条是性能问题**。前四条会产生 bug，第五条只会让页面变慢。
>
> 所以今天的顺序是：**先把前四条讲透，最后 12 分钟再谈性能。**

### 1.3 本次课要回答的问题

- JSX 到底是什么？它执行的时候发生了什么？
- 组件函数什么时候会被调用？调用了就一定操作 DOM 吗？
- 为什么 `arr.push()` 之后界面不动？
- 为什么 `setCount(count+1)` 写三遍只加 1？
- `key` 到底是干什么的？为什么 `index` 不行？
- 前端校验和后端 Pydantic 的规则，怎么保证不漂移？
- **AI 写 React 代码时犯的错，和它写 SQL 时犯的错，是同一类吗？**

---

## 二、解剖台：AI 写的标签编辑器

**约 13 分钟。四个演示都要做。**

### 情境设定

> 你对 AI 说："用 React 做一个问题编辑页，要能编辑标题、正文，还要能增删标签。"
>
> 它给了你一套组件。`npm run dev`，页面渲染出来了，样式也不错。
>
> **`tsc --noEmit` 零错误，ESLint 零警告，CI 全绿。**
>
> 然后你开始点。

### 代码（tag: `v11-broken`）

```tsx
// src/components/TagEditor.tsx —— AI 原样产出
export function TagEditor() {
  const [tags, setTags] = useState<string[]>(["前端", "React", "构建"]);
  const [input, setInput] = useState("");

  function addTag() {
    tags.push(input);        // ①
    setTags(tags);
    setInput("");
  }

  return (
    <div>
      <ul>
        {tags.map((tag, index) => (
          <TagRow key={index} tag={tag}                     // ③
                  onRemove={() => setTags(tags.filter((_, i) => i !== index))} />
        ))}
      </ul>
      <input value={input} onChange={e => setInput(e.target.value)} />
      <button onClick={addTag}>添加标签</button>
    </div>
  );
}

function TagRow({ tag, onRemove }: { tag: string; onRemove: () => void }) {
  const [draft, setDraft] = useState(tag);        // ← 行内可编辑
  return (
    <li>
      <input value={draft} onChange={e => setDraft(e.target.value)} />
      <button onClick={onRemove}>删除</button>
    </li>
  );
}
```

```tsx
// src/components/DraftForm.tsx
export function DraftForm() {
  const [draft, setDraft] = useState({ title: "", body: "" });

  function onTitleChange(e: React.ChangeEvent<HTMLInputElement>) {
    draft.title = e.target.value;        // ②
    setDraft(draft);
  }

  return <input value={draft.title} onChange={onTitleChange} />;
}
```

```tsx
// src/components/Counter.tsx
export function Counter() {
  const [count, setCount] = useState(0);
  function addThree() {
    setCount(count + 1);       // ④
    setCount(count + 1);
    setCount(count + 1);
  }
  return <button onClick={addThree}>+3（当前 {count}）</button>;
}
```

```tsx
// src/components/QuestionList.tsx
const QuestionCard = memo(function QuestionCard({ q, onSelect }: Props) {
  return <li onClick={() => onSelect(q.id)}>{q.title}</li>;
});

export function QuestionList({ questions }: { questions: QuestionOut[] }) {
  const [selected, setSelected] = useState<number | null>(null);
  const [keyword, setKeyword] = useState("");
  return (
    <>
      <input value={keyword} onChange={e => setKeyword(e.target.value)} />
      <ul>
        {questions.map(q => (
          <QuestionCard key={q.id} q={q}
                        onSelect={(id) => setSelected(id)} />   {/* ⑤ */}
        ))}
      </ul>
    </>
  );
}
```

先让学生看 60 秒，问：**你觉得哪里有问题？**

**学生通常能指出 `push`，偶尔有人说 `key={index}`。几乎没有人能说清为什么。**

### 演示一：`push` 之后什么都没发生

输入"测试"，点"添加标签"。

**界面：毫无反应。**

打开 console：

```tsx
function addTag() {
  tags.push(input);
  console.log("数组里有了吗：", tags);   // ["前端","React","构建","测试"]  ← 有了
  setTags(tags);
}
```

> **数组里确实有了。界面就是不动。**
>
> 而且注意：**没有报错、没有警告、控制台干干净净。**
>
> 这类 bug 最难查，因为它不留痕迹。

### 演示二：输入框打不出字

在标题输入框里敲键盘。

**一个字都打不出来。**

> 这个更诡异——`onChange` 明明触发了（可以加 log 证明），`draft.title` 也确实被改了。
>
> **但输入框的 `value` 是 `draft.title`，而组件没有重渲染，所以 `value` 还是旧的空字符串。**
>
> **React 把你打的字"顶回去"了。**

**停下来，把两个演示放在一起**：

```tsx
tags.push(input);  setTags(tags);           // 演示一
draft.title = v;   setDraft(draft);         // 演示二
```

> 这两行结构完全一样：**修改原对象，然后把原对象传回去。**
>
> React 收到 `setTags(tags)` 之后，做的第一件事是：
>
> ```js
> if (Object.is(newValue, oldValue)) return;      // ← 一样，什么都不做
> ```
>
> 你传进去的还是**同一个引用**。React 看不出任何变化，直接跳过。
>
> **它没有比较数组的内容。它只比了引用。**

### 演示三：连点三次，只加一

点一下 `+3` 按钮。

```
+3（当前 1）        ← 不是 3
```

> `setCount(count + 1)` 写了三遍，只加了 1。
>
> 加日志看得更清楚：

```tsx
function addThree() {
  console.log("A", count);   // 0
  setCount(count + 1);
  console.log("B", count);   // 0   ← 还是 0
  setCount(count + 1);
  console.log("C", count);   // 0   ← 还是 0
}
```

> **`setCount` 没有改变 `count`。**
>
> 这不是异步的问题，也不是"延迟生效"的问题。
>
> **`count` 在这次渲染里就是一个常量 `0`。** 它不可能变。
>
> 单元 5 会讲清楚这是怎么回事。现在只记一句：**`setState` 不是赋值。**

### 演示四：`memo` 了，还是全部重渲染

打开 React DevTools → Components → 设置 → 勾上 **Highlight updates when components render**。

在搜索框里敲一个字符。

**1000 个卡片全部闪蓝框。**

> `QuestionCard` 已经用 `memo` 包起来了。**为什么没用？**
>
> 看这一行：
>
> ```tsx
> <QuestionCard q={q} onSelect={(id) => setSelected(id)} />
> ```
>
> `(id) => setSelected(id)` 是一个**箭头函数字面量**。每次 `QuestionList` 渲染，这一行都会**创建一个全新的函数对象**。
>
> `memo` 做的是**浅比较 props**：
>
> ```js
> Object.is(prevProps.onSelect, nextProps.onSelect)   // false，永远 false
> ```
>
> 于是浅比较失败，`memo` 认为 props 变了，照样渲染。

### 四个演示的共同点（**封面级素材，本次课的技术主轴**）

| # | 现象 | 表面看是 | **真正的原因** |
|---|---|---|---|
| ① | push 后界面不动 | 用了 push | **引用没变** |
| ② | 输入框打不出字 | 直接改了属性 | **引用没变** |
| ③ | 三次 +1 只加 1 | 连续调用 | **读的是同一次渲染的快照** |
| ④ | memo 完全无效 | memo 不好使 | **props 里的函数每次都是新引用** |

**然后打出核心句**：

> **React 判断"变没变"，靠的是引用比较（`Object.is`），不是内容比较。**
>
> 这一条规则，解释了今天四个 bug 里的三个。**而且它们的方向是相反的：**
>
> | 方向 | 现象 | 后果 |
> |---|---|---|
> | **内容变了，引用没变** | ①② | React 以为没变 → **该更新的不更新** |
> | **内容没变，引用变了** | ④ | React 以为变了 → **不该更新的白更新** |
>
> 第一种产生 bug，第二种产生性能问题。
>
> **两者的根都在同一条规则上。理解了这条规则，两类问题一起解决。**

### 为什么 React 要这么设计（**必须讲，否则学生只当它是坑**）

| 方案 | 每次比较的成本 | 问题 |
|---|---|---|
| 深比较内容 | **O(n)**，n = 数据规模 | 函数、Symbol、循环引用无法比较；大对象极慢；**每次渲染都要做** |
| **引用比较** | **O(1)** | **要求你遵守不可变约定** |
| Proxy 拦截（Vue 的做法） | 中等（每次属性访问有开销） | 需要包装对象；代理的边界问题 |

> **判据：React 把"每次 O(n) 的比较"换成了"一条你必须遵守的约定"。**
>
> 这是一个明确的取舍，不是疏漏。它换来的是：状态再大，判等都是一次指针比较。
>
> 但请注意——**这门课一直在批评"依赖人记得的规则"。React 的不可变约定，恰恰就是这样一条规则。**
>
> 那能不能把它变成结构？**能，部分能。单元 4.5 会做一次。**

### 欠账清单

| 问题 | 本次课处理 | 何时还 |
|---|---|---|
| 引用比较 / 不可变更新 | **单元 4** | — |
| 把不可变变成类型错误 | **单元 4.5** | — |
| `setState` 是队列 | **单元 5** | — |
| `key={index}` | **单元 6** | — |
| `memo` / `useCallback` | **单元 8.3** | — |
| 受控表单、校验对齐 | **单元 7** | — |
| 渲染次数守卫 | **单元 8.5** | — |
| `useEffect` 与数据获取 | **不讲** | **第 12 次课** |
| `useRef` / `useReducer` / `useContext` | 单元 9 结论卡 | 课后自读 |
| 状态管理库 | 单元 9 结论卡 | 课后自读 |
| 虚拟滚动 | 单元 8.4 提及 | 课后自读 |
| React Compiler | 单元 9 结论卡 | — |

---

## 三、JSX 是什么；声明式心智

**约 10 分钟。**

### 3.1 现场打印一个 JSX

**回收第 3 次课的手法，第四次使用。**

```tsx
console.log(<div className="card">hi</div>);
```

```js
{
  $$typeof: Symbol(react.element),
  type: "div",
  key: null,
  props: { className: "card", children: "hi" },
  ...
}
```

> **它是一个普通的 JavaScript 对象。**
>
> 不是 DOM 节点，不是 HTML 字符串，**就是一个对象**。

**看构建工具做了什么（回收第 10 次课）**：

```tsx
// 你写的
<div className="card" onClick={handleClick}>
  <h3>{q.title}</h3>
</div>
```

```js
// esbuild 转译后
jsx("div", {
  className: "card",
  onClick: handleClick,
  children: jsx("h3", { children: q.title })
})
```

> 第 10 次课说"浏览器不认 JSX 语法，所以必须构建"。**现在你看到它被转成了什么：普通的函数调用。**
>
> **回收第 3 次课那条判据（第四次）：**
>
> | 次课 | 被打印出来的东西 | 它是 |
> |---|---|---|
> | 第 3 次课 | `app.routes` | 一个列表 |
> | 第 9 次课 | `app.dependency_overrides` | 一个字典 |
> | 第 9 次课 | `app.openapi()` | 一个 dict |
> | **第 11 次课** | **`<div/>`** | **一个对象** |
>
> **框架没有魔法，只有你还没打印出来的数据结构。**

### 3.2 由"它是函数调用"直接推出三条结论

**醒目页**：

| 结论 | 为什么 |
|---|---|
| **组件名必须大写开头** | 小写 → 编译成字符串 `"div"`（当作 HTML 标签）；大写 → 编译成变量引用 `QuestionCard` |
| **`{}` 里只能放表达式，不能放 `if` / `for`** | 它是函数参数的位置。参数位置不能写语句 |
| **`return <div/>` 不操作任何 DOM** | 它只是造了个对象。**操作 DOM 是后面 commit 阶段的事** |

第三条要专门停一下：

> 很多人以为 `return <div>...</div>` 是"画出一个 div"。
>
> **不是。它是"描述这里应该有个 div"。**
>
> 描述完了交给 React，React 拿它和上一次的描述比较，**算出最小的 DOM 操作**，然后才去动真正的 DOM。
>
> 这个区别在单元 4.2 会变得非常重要。

**顺带解决"条件渲染和列表怎么写"**（不单独讲，就在这里带过）：

```tsx
{isLoading && <Spinner />}                        {/* 条件 */}
{error ? <Error msg={error} /> : <List />}        {/* 二选一 */}
{items.map(it => <Item key={it.id} {...it} />)}   {/* 列表：就是数组 */}
```

> 为什么用 `&&` 和三元而不是 `if`？**因为这是表达式位置。** 这不是"React 的语法"，是 JavaScript 的规则。
>
> 一个坑：`{count && <List/>}`，当 `count` 是 `0` 时，页面上会渲染出一个 **`0`**。用 `{count > 0 && ...}`。

### 3.3 声明式心智：不要问"怎么改界面"

**封面级素材，与 1.1 的命令式代码对照**：

| | 命令式（第 2 次课） | 声明式（React） |
|---|---|---|
| 你写的是 | "点击时，找到那个 li，把 textContent 改成 X" | "列表应该长这样" |
| 你维护几份状态 | **两份**（数据 + DOM） | **一份** |
| 加一个交互要想 | 它对现有 DOM 的**所有**影响 | 它怎么改状态 |
| 典型 bug | **两份状态不同步** | 状态算错了 |
| 复杂度 | **n 个交互 × m 个元素** | **n 个交互** |

**判据（本单元核心）**：

> **不要问"我该怎么改界面"，问"什么状态能让界面长成这样"。**

**给一个具体例子，让判据落地**：

> 需求：点删除时弹出确认框。
>
> | 思路 | 做法 |
> |---|---|
> | 命令式 | 点删除 → `dialog.style.display = 'block'` → 记住要删的是哪个 → 点确认 → 删除 → 隐藏 dialog |
> | **声明式** | **加一个状态 `pendingDeleteId: number \| null`**，界面根据它渲染 |
>
> ```tsx
> const [pendingDeleteId, setPendingDeleteId] = useState<number | null>(null);
>
> <button onClick={() => setPendingDeleteId(q.id)}>删除</button>
> {pendingDeleteId !== null && (
>   <ConfirmDialog onConfirm={() => { doDelete(pendingDeleteId); setPendingDeleteId(null); }}
>                  onCancel={() => setPendingDeleteId(null)} />
> )}
> ```
>
> 注意 `pendingDeleteId` 一个状态同时表达了两件事：**"要不要显示对话框"** 和 **"要删的是哪个"**。
>
> 这两件事**本来就不可能独立变化**——把它们放进一个状态，就消除了"显示了对话框但不知道删谁"这种非法状态。
>
> **回收第 8 次课的可辨识联合：让非法状态在类型上就无法表示。** 这里是同一条判据的轻量版。

### 3.4 完整的那条链

**醒目页，本次课后面所有内容都挂在这条链上**：

```
你调用 setState
   ↓
React 把你的组件函数【重新调用一遍】          ← render
   ↓
得到一棵新的 JSX 对象树
   ↓
和上一次的对象树比对                          ← reconciliation
   ↓
算出最小的 DOM 操作，执行                     ← commit
```

> **最关键的一句：你的组件函数会被反复调用。**
>
> 不是"构造一次然后一直活着"，是**每次渲染都从头跑一遍**。
>
> 这一点如果没接受，单元 5 的快照心智就永远建立不起来——
> 因为你会一直以为 `count` 是"一个活的变量"，而它其实是"这一次函数调用里的一个局部常量"。

---

## 四、重渲染的触发条件与不可变更新

**约 13 分钟。**

### 4.1 什么时候会重渲染

**醒目页**：

| 触发条件 | 说明 |
|---|---|
| **自己的 state 变了** | 调用了 `setState`，**且新值与旧值引用不同** |
| **父组件重渲染了** | **无条件跟着渲染，不管 props 变没变** |
| 使用的 context 值变了 | — |

**第二行必须强调**：

> **父组件重渲染，所有子组件默认都会重渲染。哪怕 props 一模一样、哪怕根本没传 props。**
>
> 这解释了演示四的一半——`QuestionList` 因为 `keyword` 变了而重渲染，1000 个 `QuestionCard` 就全都跟着渲染。
>
> **为什么 React 这么设计？**
>
> 因为"判断 props 变没变"本身有成本（要逐个属性比较），而**大部分组件渲染一次不到 0.1 毫秒**。
>
> **默认全部渲染 + 需要时手工优化**，总成本低于**默认全部比较**。
>
> 判据：**这是一个"默认不优化"的设计。想优化要显式声明（`memo`），而且你要为它付出代价（单元 8.4）。**

### 4.2 "重渲染"不等于"重建 DOM"（**最大的误解，必须讲清**）

**醒目页**：

| 阶段 | 做什么 | 成本 |
|---|---|---|
| **render（渲染）** | 调用你的组件函数，产生 JSX 对象 | **便宜**——就是跑一遍 JS 函数 |
| **reconciliation（协调）** | 新旧对象树逐层比对 | 中等 |
| **commit（提交）** | **真正操作 DOM** | **最贵** |

> 所以这句话要说准确：
>
> **"组件渲染了 1000 次"不一定是问题。"DOM 更新了 1000 次"才是问题。**
>
> React 的整个设计就是为了让前两步尽量便宜，从而**把第三步压到最小**。
>
> 一个 1000 项的列表，如果只有一项的标题变了，commit 阶段只会执行**一次** `textContent` 赋值。前面 999 次组件函数调用确实白跑了——但那是几毫秒的 JS 执行，不是几百次布局重排。

**这条判据在单元 8 会直接用到**：

> DevTools 的 highlight updates 和 Profiler，量的都是 **render**，不是 commit。
>
> **所以"看到一片蓝框"要先判断：这些渲染真的贵吗？** 不贵就不用管。

### 4.3 diff 的两条规则（给结论，不讲实现）

> 完整的树 diff 是 O(n³)。React 用**两条启发式规则**把它压到 O(n)：

**醒目页**：

> **规则一：类型不同，整棵子树销毁重建。**
>
> ```tsx
> <div><Counter/></div>   →   <span><Counter/></span>
> ```
> `div` 变 `span`，React 不会"把 div 改成 span"，而是**删掉整棵子树，重新建一棵**。里面 `Counter` 的 state **全部丢失**。
>
> **规则二：同一层级的列表，按 `key` 匹配。没有 key 就按位置匹配。**
>
> **→ 这条是单元 6 的全部内容。**

**规则一的一个实际后果**：

```tsx
// ❌ 切换时 input 会被重建，光标位置、输入法状态全丢
{isEditing ? <input value={v} onChange={f}/> : <input value={v} readOnly/>}
// ↑ 这个其实是同类型，不会重建

// ❌ 真正会重建的：
{isEditing ? <EditPanel data={d}/> : <ViewPanel data={d}/>}
// ↑ 不同组件类型，EditPanel 里所有 state 在切换时清零
```

> 这个性质有时候**正是你想要的**（切换时想重置状态），有时候是 bug。
>
> **想主动利用它**：给组件加一个会变的 `key`，就能强制重建。
>
> ```tsx
> <EditForm key={currentQuestionId} question={q} />
> ```
> 切换问题时，`key` 变了 → 整个表单重建 → 草稿状态清零。**这是 key 的另一个用途。**

### 4.4 不可变更新速查表

**醒目页，学生会截图带走的一页**：

```tsx
// ── 数组 ──────────────────────────────
setTags([...tags, newTag]);                              // 追加
setTags([newTag, ...tags]);                              // 前插
setTags(tags.filter(t => t.id !== targetId));            // 删除
setTags(tags.map(t => t.id === id ? { ...t, text: v } : t));  // 修改某一项
setTags([...tags].sort((a, b) => a.order - b.order));    // 排序（注意先复制！）
setTags([...tags.slice(0, i), newItem, ...tags.slice(i)]); // 插入

// ── 对象 ──────────────────────────────
setDraft({ ...draft, title: newTitle });                 // 改一个字段
setDraft({ ...draft, author: { ...draft.author, name: n } });  // 改嵌套字段
const { removed, ...rest } = draft; setDraft(rest);      // 删一个字段
```

**原地修改的陷阱清单（醒目页）**：

| 会原地修改（危险） | 返回新数组（安全） |
|---|---|
| `push` / `pop` / `shift` / `unshift` | `[...a, x]` / `a.slice(0, -1)` |
| `splice` | `a.toSpliced(...)` / `filter` / `slice` 拼接 |
| **`sort`** | `[...a].sort()` / `a.toSorted()` |
| **`reverse`** | `[...a].reverse()` / `a.toReversed()` |
| `fill` / `copyWithin` | `map` |

> **`sort` 和 `reverse` 是最阴险的两个**，因为它们**有返回值**——看起来像纯函数，实际上原地改了，返回的还是同一个引用。
>
> ```js
> const b = a.sort();
> b === a;        // true ！
> ```
>
> `toSorted` / `toReversed` / `toSpliced` 是较新的方法，**先确认你的目标浏览器支持**（回收第 10 次课的 browserslist）。

**关于嵌套的一句提醒**：

> 嵌套三层以上时，展开写法会变得很难读：
>
> ```tsx
> setState({ ...s, a: { ...s.a, b: { ...s.a.b, c: v } } });
> ```
>
> 这通常是**状态结构设计得太深**的信号。先考虑拍平状态，再考虑上 Immer。
>
> 判据：**要写三层展开的时候，先问"这个状态能不能拆成两个"。**

### 4.5 把不可变从纪律变成类型错误（**本单元最重要的一段**）

**先把问题挑明**：

> 上面那两张表，本质上是**一份"要记得"的清单**。
>
> 而这门课从第 2 次课起就在说同一件事：**依赖人记得的规则，迟早会被违反。**
>
> **那能不能让它变成机制？**

**方案一：`readonly` 类型（今天就做）**

```tsx
// 原来
const [tags, setTags] = useState<string[]>([]);
tags.push("x");                 // ✅ tsc 不报错

// 改成
const [tags, setTags] = useState<readonly string[]>([]);
tags.push("x");
// ❌ Property 'push' does not exist on type 'readonly string[]'.
```

对象也一样：

```tsx
interface Draft {
  readonly title: string;
  readonly body: string;
  readonly tags: readonly string[];
}

draft.title = "x";
// ❌ Cannot assign to 'title' because it is a read-only property.
```

**现场演示红-绿两步（回收第 9 次课的方法论）**：

1. 改成 `readonly`，`npm run check` → **报错，指向演示一那行 `tags.push`**
2. 改成 `setTags([...tags, input])` → 绿

**要讲的四点（醒目页）**：

> **一、这是第 10 次课那条判据的直接应用。**
>
> 第 10 次课：*"类型检查一次性配置，边际成本为零，覆盖 AI 最常犯的那一类错误。"*
>
> 今天发现它还能覆盖**框架的运行时约定**——只要那条约定能被类型表达。
>
> **二、`readonly` 是浅的。**
>
> ```ts
> readonly Tag[]        // 不能 push，但可以 tags[0].text = "x"
> ```
> 要深层只读，每一层都得标（或用工具类型 `DeepReadonly`）。**大多数情况浅的就够——因为最常见的错误就是 push 和顶层赋值。**
>
> **三、它只存在于编译期（回收第 10 次课 7.1④）。**
>
> `readonly` 编译后就没了，运行时**没有任何东西阻止你修改**。它是给你（和 AI）看的，不是给运行时看的。
>
> **四、它抓不到什么。**
>
> ```tsx
> setTags(tags);                    // 引用没变，readonly 抓不到
> const copy = tags as string[];    // as 断言绕过，抓不到
> ```
>
> **判据：`readonly` 抓住的是"最常见的那种写法"，不是"所有可能的违反"。**
>
> 这条判据回收第 9 次课 5.2：**检查的严谨程度要配得上问题的严重程度和检查的成本。** 加一个 `readonly` 的成本是零，能拦住 80% 的情况——非常划算。

**方案二：ESLint（补充）**

```js
// eslint.config.js
"react-hooks/exhaustive-deps": "warn",       // 依赖数组
"no-param-reassign": ["error", { props: true }],
```

**方案三：Immer（记一笔，不现场做）**

> 让你"写起来像原地改，实际产生新引用"：
>
> ```ts
> setTags(produce(draft => { draft.push(newTag); }));
> ```
>
> **它把心智负担转移到了库上。** 什么时候值得引入：状态结构深、展开写法已经难读。**不要一开始就上。**

### 材料

- **封面级素材**：4.1 的三条触发条件（第二行高亮）。
- **封面级素材**：4.2 的 render / reconciliation / commit 三阶段表。
- **封面级素材**：4.4 的不可变速查表 + 原地修改陷阱清单（`sort`/`reverse` 标红）。
- **封面级素材**：4.5 的 `readonly` 红-绿演示 + 四条说明。
- 高光图：4.3 的两条 diff 规则。
- 截图：`readonly` 下 `push` 的 tsc 报错原文。
- 截图：`const b = a.sort(); b === a` 在 console 里返回 `true`。

---

## 五、`useState` 是队列，不是变量

**约 10 分钟。**

### 5.1 回到演示三，加满日志

```tsx
function addThree() {
  console.log("渲染时 count =", count);   // 0
  setCount(count + 1);
  console.log("第一次 set 后 =", count);  // 0
  setCount(count + 1);
  console.log("第二次 set 后 =", count);  // 0
  setCount(count + 1);
  console.log("第三次 set 后 =", count);  // 0
}
```

> **四次打印全是 0。**
>
> 这不是异步问题，不是"稍后才生效"。
>
> **`count` 在这次函数调用里就是一个常量。** `setCount` 没有、也不可能改变它——**它是一个 `const`**。

### 5.2 快照心智（**封面级素材**）

> **每一次渲染，都是组件函数的一次独立调用。**
>
> **这次调用里的 `count`、`props`、你创建的每个事件处理函数，全部是"这一次渲染的快照"。它们在这次渲染期间永远不变。**

**画图**：

```
渲染 #1
  ├─ count = 0                      （这次调用里的常量）
  ├─ addThree = () => {             （这个函数闭包捕获了 count = 0）
  │     setCount(0 + 1);
  │     setCount(0 + 1);
  │     setCount(0 + 1);
  │  }
  └─ 用户点击
        ↓
     更新队列：[ 设为 1, 设为 1, 设为 1 ]
        ↓
     React 依次处理 → 最终 1
        ↓
渲染 #2
  ├─ count = 1                      （新的一次调用，新的常量）
  └─ addThree = () => { setCount(1+1); ... }   （新的函数，捕获 1）
```

> 三次 `setCount(count + 1)` 展开就是三次 `setCount(1)`。**结果当然是 1。**

### 5.3 函数式更新

```tsx
setCount(c => c + 1);
setCount(c => c + 1);
setCount(c => c + 1);
```

```
更新队列：[ c=>c+1, c=>c+1, c=>c+1 ]
处理：0 → 1 → 2 → 3
```

> 传函数进去，React 在处理队列时把**队列里的最新值**交给你。
>
> **判据（醒目页）**：
>
> | 新值 | 怎么写 |
> |---|---|
> | **依赖旧值** | **`setX(prev => ...)`** |
> | 不依赖旧值 | `setX(newValue)` 直接写 |
>
> 例子：
>
> ```tsx
> setCount(c => c + 1);                          // 依赖旧值 ✅
> setTags(prev => [...prev, newTag]);            // 依赖旧值 ✅
> setForm(f => ({ ...f, [name]: value }));       // 依赖旧值 ✅
> setKeyword(e.target.value);                    // 不依赖  ✅
> setSelected(null);                             // 不依赖  ✅
> ```

**再补一个更隐蔽的场景**：

```tsx
// 一个"每秒 +1"的计时器（下次课会正式讲 useEffect，这里只看现象）
setInterval(() => setCount(count + 1), 1000);
```

> 这个计时器**永远只会让 count 变成 1**，因为回调闭包里的 `count` 永远是创建它那次渲染的快照。
>
> 改成 `setCount(c => c + 1)` 就对了。
>
> **这是快照心智最常见的翻车点，也是 AI 写定时器/异步回调时最常犯的错。**

### 5.4 批处理

```tsx
function handleSubmit() {
  setSubmitting(true);
  setError(null);
  setTouched(true);
}
// 组件只重渲染【一次】，不是三次
```

> React 18 起，**所有更新都会批处理**——包括 `setTimeout`、`Promise.then`、原生事件回调里的。
>
> 好处：**没有中间态闪烁，没有无谓的渲染。**
>
> 代价：**你不能指望 `setState` 之后立刻读到新值。**

### 5.5 最常见的那个坑

```tsx
async function load() {
  const data = await fetchItems();
  setItems(data);
  console.log(items.length);      // ❌ 还是旧的（通常是 0）
  if (items.length > 0) { ... }   // ❌ 判断用的是旧值
}
```

> **这个模式在 AI 生成的代码里出现频率极高。**
>
> 正确写法：**用你手上已有的那个值，不要去读 state。**
>
> ```tsx
> const data = await fetchItems();
> setItems(data);
> if (data.length > 0) { ... }      // ✅ 用 data，不用 items
> ```
>
> **判据：`setState` 之后，同一个函数里不要再读那个 state。** 需要用新值，就用你传进去的那个值。
>
> 如果确实需要"状态更新完成后做点什么"——那是 `useEffect` 的场景，**下次课讲。**

### 材料

- **封面级素材**：5.2 的快照心智 + 渲染 #1/#2 的图。
- **封面级素材**：5.3 的"依赖旧值就用函数式"判据表。
- 高光图：5.5 的"setState 后不要读 state"。
- 截图：四行 console.log 全是 0。
- 截图：`setInterval` 版本的计数器停在 1。

---

## 六、现场必做：`key={index}` 与身份

**约 15 分钟。本次课最高光。**

### 6.1 先建立一个错误预期

问学生：**`key` 是干什么的？**

常见回答："React 要求的，不给会在控制台警告。"

> 对，**不给就警告。那我给 `key={index}`，警告就消失了。**
>
> 这是最省事的做法，很多教程这么写，Stack Overflow 上到处都是，**AI 也经常这么写**。
>
> 今天看看这么干会发生什么。

### 6.2 复现（**逐步操作，每步都停**）

当前页面：`TagEditor`，三个标签，每行一个可编辑输入框 + 删除按钮。

```
[前端      ] [删除]
[React     ] [删除]
[构建      ] [删除]
```

**第 1 步**：把第一行改成 `前端工程化`。

```
[前端工程化 ] [删除]
[React     ] [删除]
[构建      ] [删除]
```

**第 2 步**：点**第一行**的删除。

**停下来，先让学生预测：现在应该显示什么？**

正确答案应该是：
```
[React     ] [删除]
[构建      ] [删除]
```

**第 3 步**：点下去。

**实际显示**：
```
[前端工程化 ] [删除]      ← 被删掉的那个的内容，还在
[React     ] [删除]      ← "构建"呢？
```

**让这个画面停留 15 秒。**

> **界面上的文字，和它背后的数据，完全对不上。**
>
> 数据是 `["React", "构建"]`，界面显示的是 `前端工程化 / React`。
>
> 而且：
> - **`tsc --noEmit` 零错误**
> - **ESLint 零警告**
> - **控制台干干净净，连个 warning 都没有**
> - **单元测试如果只测数据层，也会全绿**

### 6.3 讲清 key 匹配算法（**封面级素材**）

```
删除前：
  数据：   ["前端",      "React",  "构建"]
  key：      0            1          2
  组件实例： A            B          C
  实例内部 state（draft）：
           "前端工程化"   "React"    "构建"
              ↑ 用户改过

删除后：
  数据：   ["React", "构建"]
  key：      0         1

  React 的匹配过程：
    key=0 → 上次也有 key=0 → 【同一个组件】→ 复用实例 A，只更新 props
    key=1 → 上次也有 key=1 → 【同一个组件】→ 复用实例 B，只更新 props
    key=2 → 上次有，这次没有 → 卸载实例 C

  结果：
    实例 A 还活着，它的内部 state draft = "前端工程化"   ← 没有被重置
    实例 B 还活着，它的内部 state draft = "React"        ← 没有被重置

    而 props 变成了 tag="React" 和 tag="构建"
    但 draft 是 useState(tag) 初始化的，【只在挂载时用一次】
    → 界面显示的是 draft，不是 tag
```

**核心句（封面级素材）**：

> **`key` 告诉 React 的是："这是同一个东西。"**
>
> 用 `index` 当 key，等于在说：**"第 0 个位置上的东西，永远是同一个东西。"**
>
> 但列表一变，第 0 个位置上**换人了**。你还在跟 React 说它是同一个，**React 就把旧实例连同它的 state 一起，留给了新数据。**

**再补一句，把它和第 6 次课连起来**：

> **`key` 和数据库主键，解决的是同一个问题：如何唯一标识一个实体。**
>
> | | 数据库主键 | React key |
> |---|---|---|
> | 回答什么问题 | 这两行是不是同一条记录 | 这两次渲染里，这是不是同一个组件 |
> | 用位置行不行 | **不行**（行序会变） | **不行**（列表会变） |
> | 用内容行不行 | 不行（内容会改） | 不行（内容会改） |
> | 正确答案 | **稳定的、唯一的 id** | **稳定的、唯一的 id** |
>
> 第 6 次课我们给每张表都加了主键，当时的理由是"没有主键就没法稳定地指认一行"。
>
> **今天是同一条理由，换了一层。**

### 6.4 修复

```diff
- const [tags, setTags] = useState<string[]>(["前端", "React", "构建"]);
+ interface Tag { readonly id: string; readonly text: string; }
+ const [tags, setTags] = useState<readonly Tag[]>([
+   { id: crypto.randomUUID(), text: "前端" },
+   ...
+ ]);

- {tags.map((tag, index) => <TagRow key={index} tag={tag} ... />)}
+ {tags.map(tag => <TagRow key={tag.id} tag={tag.text} ... />)}
```

重跑一次同样的操作步骤：**正确了。**

> 注意修复的**真正内容**不是"把 `key={index}` 改成 `key={tag.id}`"，而是——
>
> **给数据加上了身份。**
>
> 原来的数据是 `string[]`，**它根本没有身份**。两个相同的字符串就是同一个东西，你想给 key 也给不出来。
>
> **判据：如果你发现"找不到合适的 key"，问题通常在数据结构，不在 React。**

**顺带回收 4.5**：

> 注意这里的类型是 `readonly Tag[]` 和 `readonly id`。**这是单元 4.5 那道护栏，现在它顺手保护了 key 的稳定性**——`id` 是 readonly，没人能改它。

### 6.5 什么时候 index 是安全的（**必须给，否则学生走极端**）

**醒目页**：

| 条件 | index 能用吗 |
|---|---|
| 列表永不重排、永不增删（纯静态） | ✅ 安全 |
| 只在**末尾**追加，不删不排 | ✅ 基本安全 |
| 列表项**完全无状态**（纯展示，无内部 state、无非受控输入、无动画） | ⚠️ 不会错位，但可能有多余 DOM 操作 |
| **有任何删除、插入、重排、筛选** | ❌ **危险** |
| **列表项有内部 state / 非受控输入 / 焦点 / 动画** | ❌ **危险** |

> **判据：拿不准就用真 id。用 index 只在你能说清"为什么这个列表是稳定的"的时候。**

**另外两个反面写法，必须点名**：

```tsx
<Item key={Math.random()} />      // ❌ 每次渲染都是新 key
<Item key={Date.now()} />         // ❌ 同上
```

> 后果：**每次渲染都销毁旧实例、创建新实例。** state 全丢、焦点全丢、性能灾难。
>
> 这个写法也在 AI 的输出里出现过——**它"解决"了警告，同时制造了最糟的情况。**

```tsx
<Item key={item.name} />          // ⚠️ name 会重复吗？
```

> 用业务字段当 key，要确认它**真的唯一且稳定**。用户名可以改，标题可以重复。
>
> **这一类 ESLint 抓不到。**

### 6.6 能不能变成检查（**回收第 9、10 次课的固定动作**）

```js
// eslint.config.js
"react/no-array-index-key": "warn",       // ← 注意是 warn 不是 error
```

**红-绿演示**：

```
web/src/components/TagEditor.tsx
  14:20  warning  Do not use Array index in keys  react/no-array-index-key
```

**然后讲透它的边界（醒目页）**：

> **这条规则的误报率是中等的**——6.5 表里前三行的情况它都会报，而那些情况其实是安全的。
>
> **回收第 9 次课 5.6 的判据：宁可少几条检查，也不要有一条会误报的检查。**
>
> 所以这里的处理是：
>
> | 做法 | 理由 |
> |---|---|
> | 设为 `warn` 而非 `error` | 不阻断 CI，但每次都看得见 |
> | **豁免必须写注释说明"为什么这个列表是稳定的"** | 把判断留痕，供评审 |
>
> ```tsx
> // eslint-disable-next-line react/no-array-index-key
> // 理由：这是渲染表头，固定 4 列，永不增删重排
> {HEADERS.map((h, i) => <th key={i}>{h}</th>)}
> ```

**然后兑现第 10 次课末尾的伏笔（封面级素材）**：

> 第 10 次课那张表，今天要加一行。**这一行就是今天这个 bug 所属的类别：**

| 错误类型 | AI 犯的频率 | 类型能抓吗 | 谁来抓 |
|---|---|---|---|
| 字段名猜错 | 高 | ✅ | tsc |
| 函数签名对不上 | 高 | ✅ | tsc |
| 可空没处理 | 高 | ✅ | tsc |
| 结构假设错 | 高 | ✅ | tsc |
| 用了不存在的包 | 中 | ❌ | `npm view` |
| 业务规则漏了 | 中高 | ❌ | 测试 + 评审 |
| 边界差一 | 中 | ❌ | 测试 |
| 权限判断漏了 | 中 | ❌ | 测试 + 评审 |
| N+1 / 性能 | 中 | ❌ | 性能守卫 |
| **框架的运行时约定**<br>（key、不可变、hooks 规则、快照） | **高** | **部分**（`readonly` 能抓一部分） | **ESLint 插件 + 理解机制** |

> 新增的这一行有一个前九行都没有的性质：
>
> **它既不是"缺少你的项目信息"，也不能靠给 AI 更多上下文来解决。**
>
> 因为 `key={index}` 这种写法，**在训练数据里是多数**。AI 不是不知道 id 更好，它是在**模仿多数**。
>
> **→ 作业三会专门做这件事。**

### 材料

- **录屏（本次课最关键的素材）**：改第一行 → 删第一行 → 界面错位。**一镜到底，中间在"删除前"暂停 3 秒给观众预测。**
- **封面级素材**：6.3 的 key 匹配过程图（删除前/后两栏对照）。
- **封面级素材**：6.3 的"key 告诉 React 这是同一个东西"核心句。
- **封面级素材**：6.3 的"key 与数据库主键"四行对照表。
- **封面级素材**：6.6 的"AI 错误类型"十行表（**第十行新增，用不同颜色**）。
- 高光图：6.5 的"index 什么时候安全"五行表。
- 截图：错位状态下，DevTools Components 面板里 `TagRow` 的 props `tag="React"` 与 state `draft="前端工程化"` **并列显示**（**这张图最能说明问题**）。
- 截图：`tsc` 全绿 + ESLint 只有 warn + 控制台无报错（**三个全绿同屏**）。
- 截图：`react/no-array-index-key` 的 warning 输出。
- tag `v11-key-fixed`。

---

## 七、受控表单与校验对齐

**约 13 分钟。**

### 7.1 受控与非受控

**醒目页**：

| | 受控 | 非受控 |
|---|---|---|
| 值存在哪 | **React state** | **DOM 节点里** |
| 写法 | `value={v} onChange={...}` | `defaultValue={v}` + `ref` |
| 实时校验 | ✅ 容易 | 麻烦 |
| 根据输入禁用按钮 | ✅ 容易 | 麻烦 |
| 程序化设值（重置、填充） | ✅ 改 state 即可 | 要操作 ref |
| 单元 6 的错位 | 不会（值由数据驱动） | **会** |

> **判据：默认用受控。**
>
> 只有两种情况考虑非受控：
> 1. 超大表单（几百个字段）且实测有性能问题
> 2. 要对接非 React 的第三方输入组件
>
> 顺便：**单元 6 那个 bug 之所以那么严重，一部分原因就是 `TagRow` 用了内部 state**。
> 如果值完全由父组件的数据驱动（纯受控），即使 key 用错，显示的内容也会被 props 纠正——**只是焦点和光标位置还是会跳。**

### 7.2 统一的 handleChange

**不要每个字段写一个 handler**：

```tsx
interface FormState {
  readonly title: string;
  readonly body: string;
  readonly tags: string;
}

const [form, setForm] = useState<FormState>({ title: "", body: "", tags: "" });

function handleChange(
  e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>
) {
  const { name, value } = e.target;
  setForm(f => ({ ...f, [name]: value }));      // ← 函数式更新（单元 5.3）
}

<input    name="title" value={form.title} onChange={handleChange} />
<textarea name="body"  value={form.body}  onChange={handleChange} />
```

**三个要点**：

| 要点 | 回收自 |
|---|---|
| `name` 必须和 state 的键一致 | — |
| 用**函数式更新**（新值依赖旧值） | 单元 5.3 |
| 展开产生**新引用** | 单元 4 |

**`name` 写错怎么办？**

```tsx
// name="titel"  → 会往 state 里塞一个 titel 字段，静默出错
```

> 这个 TypeScript 默认抓不到（因为 `e.target.name` 是 `string`）。
>
> 收紧一点：
>
> ```tsx
> const { name, value } = e.target as { name: keyof FormState; value: string };
> ```
> **但这是 `as` 断言，只是把错误挪到了运行时。** 更彻底的做法是给每个 input 传一个受类型约束的 name——**成本 vs 收益自己权衡，这是一个真实的取舍**。

### 7.3 前端校验与后端 Pydantic 对齐（**本单元核心**）

**先把原则说清（封面级素材）**：

> **前端校验是体验，后端校验是安全。**

| | 前端校验 | 后端校验 |
|---|---|---|
| 目的 | **即时反馈**，少发无效请求 | **保证数据正确** |
| 能被绕过吗 | ✅ 改 JS、直接发请求、用 curl | ❌ |
| 能省掉吗 | 可以（体验变差） | **绝对不能** |
| 是谁的权威 | 无 | **唯一权威** |

> **判据：前端校验永远不能替代后端校验。** 但它能省掉 90% 的往返。

**然后是真正的问题**：

> 后端 Pydantic 写了 `min_length=5, max_length=200`。
>
> **前端要不要再写一遍？**

| 做法 | 问题 |
|---|---|
| 前端完全不校验 | 用户打完 200 字才被告知超长；每次都要等一个往返 |
| **前端手写一遍规则** | **两处真相，必然漂移**——后端改成 300，前端还卡在 200 |
| **从 OpenAPI 里拿约束** | 需要一点工程 |

**回收第 8 次课的判据，并把它推进一步（封面级素材）**：

> 第 8 次课：**"契约必须只有一个真相来源，其余全部生成。"**
>
> 当时生成的是**类型**。今天发现：**约束也应该生成。**
>
> 因为 OpenAPI 的 schema 里**本来就带着这些约束**：

```json
"QuestionCreate": {
  "required": ["title", "body"],
  "properties": {
    "title": { "type": "string", "minLength": 5,  "maxLength": 200 },
    "body":  { "type": "string", "minLength": 10 }
  }
}
```

> 第 8 次课的 `openapi-typescript` 只把 `type` 转成了 TS 类型，**`minLength` 这些运行时约束被丢掉了**——因为 TS 类型表达不了"字符串至少 5 个字符"。
>
> **它们不是不存在，是我们没去取。**

**做法一：生成常量（简单，今天做）**

```python
# scripts/gen_constraints.py
import json
from app.main import app

schemas = app.openapi()["components"]["schemas"]
out = {}
for name, s in schemas.items():
    props = {}
    for field, spec in s.get("properties", {}).items():
        c = {k: spec[k] for k in ("minLength", "maxLength", "minimum", "maximum", "pattern")
             if k in spec}
        if field in s.get("required", []):
            c["required"] = True
        if c:
            props[field] = c
    if props:
        out[name] = props

print("// 本文件由 scripts/gen_constraints.py 生成，请勿手改")
print(f"export const CONSTRAINTS = {json.dumps(out, indent=2)} as const;")
```

```ts
// src/constraints.gen.ts  ← 生成物
export const CONSTRAINTS = {
  QuestionCreate: {
    title: { minLength: 5, maxLength: 200, required: true },
    body:  { minLength: 10, required: true },
  },
} as const;
```

```tsx
const C = CONSTRAINTS.QuestionCreate;

<input name="title" value={form.title} onChange={handleChange}
       minLength={C.title.minLength} maxLength={C.title.maxLength} required />

{errors.title && <p role="alert" className="error">{errors.title}</p>}
```

**接进第 8/9/10 次课那条生成链**：

```bash
# npm run gen
python scripts/dump_openapi.py > /tmp/openapi.json
npx openapi-typescript /tmp/openapi.json -o src/api.d.ts
python scripts/gen_constraints.py > src/constraints.gen.ts
```

```bash
# scripts/check_contract.sh 里已有的那行，现在多护一个文件
git diff --exit-code src/api.d.ts src/constraints.gen.ts
```

> **第 9 次课那条契约一致性检查，一个字不用改，自动就把新文件管上了。**
>
> 这是"把纪律变成结构"的复利：**基础设施建好之后，新的约定接进去几乎是零成本。**

**做法二：生成 zod schema（完整，记一笔）**

```ts
const result = QuestionCreateSchema.safeParse(form);
if (!result.success) setErrors(mapZodErrors(result.error));
```

> 工具：`openapi-zod-client`、`orval` 等。
>
> **什么时候值得上**：表单多、约束复杂（正则、条件必填、跨字段校验）。
> **什么时候不值得**：三个表单、每个三个字段——做法一够了。

### 7.4 提交状态与错误展示

**回收第 8 次课的三态，扩展成四态**：

```tsx
type SubmitState =
  | { kind: "idle" }
  | { kind: "submitting" }
  | { kind: "error"; message: string; fields?: Record<string, string> }
  | { kind: "success"; id: number };

const [submit, setSubmit] = useState<SubmitState>({ kind: "idle" });
```

```tsx
<button type="submit" disabled={!isValid || submit.kind === "submitting"}>
  {submit.kind === "submitting" ? "提交中…" : "发布"}
</button>

{submit.kind === "error" && (
  <div role="alert">
    {submit.message}
    {submit.requestId && <small>（{submit.requestId}）</small>}
  </div>
)}
```

**两件必须讲的事**：

> **一、`disabled` 防不住重复提交。**
>
> 它只防"用户手快点两下"。它防不住：
> - 用户在 DevTools 里删掉 `disabled`
> - 网络层重试
> - 用户刷新后重新提交
>
> **回收第 3 次课：POST 不幂等。** 真正的防重必须在后端——唯一约束（第 6 次课已经有了：标题唯一）或者幂等键。
>
> **判据：前端的 `disabled` 是体验，后端的约束是保证。** 和 7.3 的判据是同一条。
>
> **二、422 的字段级错误要落到对应的字段下面。**

**回收第 3 次课的 422 结构**：

```tsx
// 后端 422 的 detail: [{ loc: ["body","title"], msg: "...", type: "string_too_short" }]
function mapFieldErrors(detail: ValidationErrorItem[]): Record<string, string> {
  return Object.fromEntries(
    detail
      .filter(e => e.loc[0] === "body")
      .map(e => [String(e.loc.at(-1)), e.msg])
  );
}
```

> 注意用的是 `e.loc` 和 `e.type`，**不是 `e.msg` 的文本匹配**。
>
> **回收"依赖稳定标识，不依赖人类可读文案"——这是本课程第六次用到它。**
>
> （前五次：422 的 `type`、数据库约束名、错误 `code`、前端错误分支、测试断言。）

### 材料

- **封面级素材**：7.1 的受控/非受控六行对照表。
- **封面级素材**：7.3 的"前端校验是体验，后端校验是安全"四行表。
- **封面级素材**：7.3 的"从生成类型推进到生成约束"——第 8 次课那张生成链图，**加上 `constraints.gen.ts` 一支**。
- 高光图：7.4 的四态定义 + 按钮/错误展示代码。
- 高光图：`mapFieldErrors` 与"第六次使用稳定标识"的标注。
- 截图：改后端 `min_length` → `npm run gen` → CI 的 `git diff --exit-code` 变红。
- 截图：前端实时提示"标题至少 5 个字"，以及提交后 422 字段级错误落位。

---

## 八、B 档：Profiler 与渲染次数守卫

**约 12 分钟。时间紧可只保留 8.1、8.4、8.5。**

### 8.1 先看见：highlight updates

场景：1000 条问题的列表 + 顶部一个搜索框。

DevTools → Components → 设置 → **Highlight updates when components render**。

在搜索框里敲一个字符：

**整屏 1000 个卡片全部闪蓝框。**

> 你只改了搜索框里的一个字符。**原因是单元 4.1 第二行：父组件重渲染，子组件无条件跟着渲染。**

### 8.2 量一下：Profiler

DevTools → Profiler → 录制 → 敲一个字 → 停止。

```
App                       48.2 ms
├─ SearchBox               0.3 ms
└─ QuestionList           47.1 ms
   └─ QuestionCard × 1000 45.8 ms
```

> **48 毫秒。** 一帧的预算是 16.7ms（60fps）。**打字会明显卡顿。**
>
> 注意 Profiler 量的是 **render 阶段**（单元 4.2）——**它不代表 DOM 更新了 1000 次**。
> 实际 commit 阶段可能只改了搜索框一个节点。
>
> **但 45.8ms 的 JS 执行本身就是问题。**

### 8.3 三步优化

**第一步：`memo`**

```tsx
const QuestionCard = memo(function QuestionCard({ q, onSelect }: Props) { ... });
```

重测 → **还是全闪。**

> 演示四的答案：
>
> ```tsx
> <QuestionCard q={q} onSelect={(id) => setSelected(id)} />
> //                            ^^^^^^^^^^^^^^^^^^^^^^^ 每次渲染新建
> ```
>
> **回到单元 2 的主轴：内容没变但引用变了 → React 以为变了 → 白更新。**

**第二步：`useCallback`**

```tsx
const handleSelect = useCallback((id: number) => setSelected(id), []);
<QuestionCard q={q} onSelect={handleSelect} />
```

重测 → **不闪了。**

```
App                     1.8 ms
├─ SearchBox            0.3 ms
└─ QuestionList         1.2 ms
   └─ （1000 个卡片全部跳过）
```

> 依赖数组 `[]` 表示"这个函数永远不需要重建"。
> `setSelected` 是 React 保证引用稳定的，**不需要放进依赖数组**。

**第三步：`useMemo` 缓存派生数据**

```tsx
const filtered = useMemo(
  () => questions.filter(q => q.title.includes(keyword)),
  [questions, keyword]
);
```

> 如果 `filter` 本身很贵（或者结果要作为 props 传给 memo 组件），这一步有意义。
> **如果只是过滤 1000 条字符串，不值得——比较依赖数组的成本可能和 filter 差不多。**

### 8.4 判据：什么时候该优化（**必须给，否则学生到处套 memo**）

**醒目页**：

> **默认不要加 `memo` / `useCallback` / `useMemo`。**

| 手段 | 它的代价 |
|---|---|
| `memo` | 每次渲染都要做一遍浅比较；多一层组件包装 |
| `useCallback` / `useMemo` | 每次都要比较依赖数组；**依赖写错会产生难查的 bug**；代码噪音 |

> 大部分组件渲染一次不到 0.1ms。**比较的成本可能比渲染还高。**
>
> **判据：先量，再优化。Profiler 显示某次交互超过 16ms，才去找原因。**

**找到原因之后，优化手段的优先级（醒目页）**：

| 优先级 | 手段 | 说明 |
|---|---|---|
| **1** | **减少要渲染的东西** | 分页、虚拟滚动。1000 条为什么要全渲染？ |
| **2** | **把状态下移** | 见下 |
| **3** | 拆分组件，让变化局部化 | 把频繁变的部分独立出来 |
| 4 | `memo` + `useCallback` | 最后才用 |

**第 2 条要展开**，因为它最有效也最常被忽略：

```tsx
// ❌ keyword 放在父组件 → 每次打字父组件渲染 → 1000 个孩子跟着渲染
function QuestionList({ questions }) {
  const [keyword, setKeyword] = useState("");
  return <><input value={keyword} onChange={...}/> ...1000 cards... </>;
}

// ✅ keyword 放进 SearchBox 内部，只在"确认搜索"时通知父组件
function SearchBox({ onSearch }: { onSearch: (k: string) => void }) {
  const [keyword, setKeyword] = useState("");     // ← 状态下移
  return <input value={keyword}
                onChange={e => setKeyword(e.target.value)}
                onKeyDown={e => e.key === "Enter" && onSearch(keyword)} />;
}
```

> **与其让 1000 个孩子跳过渲染，不如让父组件根本不渲染。**
>
> 判据：**状态应该放在"需要它的最小范围"里。** 状态放得越高，跟着渲染的东西越多。
>
> 这条判据和第 4 次课的"分层"、第 7 次课的"事务边界"是同构的：**范围越小越好，除非有明确理由放大。**

### 8.5 把它变成断言（**本单元收口，最重要的回收**）

**封面级素材，本次课最好的一页**：

> 第 7 次课我们写了一个 SQL 计数器，第 9 次课把它变成了断言：
>
> ```python
> assert a["n"] == b["n"], "SQL 条数随页面大小变化，说明存在 N+1"
> ```
>
> 当时的判据是：**能断言性质就不要断言数值。**
>
> **前端可以做一模一样的事。**

```tsx
// src/devtools/renderSpy.ts
export const renderCounts: Record<string, number> = {};

export function trackRender(name: string) {
  if (import.meta.env.MODE !== "production") {          // ← 生产里被 tree-shake
    renderCounts[name] = (renderCounts[name] ?? 0) + 1;
  }
}
```

```tsx
const QuestionCard = memo(function QuestionCard(props: Props) {
  trackRender("QuestionCard");
  ...
});
```

```tsx
// tests/render-guards.test.tsx
test("输入搜索词时，卡片渲染次数不随列表长度变化", async () => {
  const results: number[] = [];

  for (const n of [10, 200]) {
    cleanup();
    render(<QuestionListPage questions={makeQuestions(n)} />);
    renderCounts.QuestionCard = 0;                      // 清零
    await userEvent.type(screen.getByRole("searchbox"), "a");
    results.push(renderCounts.QuestionCard);
  }

  expect(results[0]).toBe(results[1]);                  // ← 断言性质
});
```

**红-绿两步**：

```
# 去掉 useCallback
AssertionError: expected 10 to be 200
```

```
# 加回 useCallback
✓ 输入搜索词时，卡片渲染次数不随列表长度变化
```

**然后打出这张表（封面级素材）**：

| 层 | 守卫什么 | 断言的形式 | 哪次课 |
|---|---|---|---|
| **数据库** | N+1 查询 | SQL 条数 **不随 page size 变化** | 第 7、9 次课 |
| **网络** | 前端 N+1 | 列表页 API 请求数 ≤ 2 | 第 8、9 次课 |
| **渲染** | 无谓重渲染 | 渲染次数 **不随列表长度变化** | **第 11 次课** |

> **三层，三个不同的技术栈，同一个判据：**
>
> **某个动作的次数，不应该随数据量增长。**
>
> 这三件事其实是同一件事——**它们都是某种形式的 N+1。**
>
> 而且三次都遵循同一条元判据：**断言"性质"，不断言"数值"。**
>
> - 断言"SQL ≤ 3 条" → 加一个正常的 eager load 就误红
> - 断言"SQL 条数不随 size 变化" → **只有真的出现 N+1 才红**
>
> 判据：**一个好的性能守卫，应该对"正常演进"免疫，只对"复杂度退化"敏感。**

### 8.6 一句关于数值断言的补充

> 那能不能断言绝对值（"渲染不超过 5 次"、"耗时不超过 16ms"）？
>
> | 断言 | 问题 |
> |---|---|
> | 渲染次数 ≤ N | 加一个合理的状态就要改 N，**最后变成走形式** |
> | 耗时 ≤ N ms | **机器不同、负载不同，数字会抖** → flaky 测试 |
>
> **回收第 9 次课的 C 档卡：遇到 flaky 测试，先查共享状态和时间依赖，不要加 retry。**
>
> 耗时断言是 flaky 的经典来源。**在 CI 里断言耗时，基本上是在制造噪音。**
>
> 判据：**把"性能"翻译成"可数的、确定的量"，再去断言它。** 次数可数，耗时不可靠。

### 材料

- **封面级素材**：8.5 的三层 N+1 守卫表（三行用三种颜色，对应三次课）。
- **封面级素材**：8.4 的优化优先级四行表（1、2 高亮）。
- 高光图：8.4 的 memo/useCallback 代价表。
- 高光图：8.4 的"状态下移"前后代码对照。
- **录屏**：highlight updates 下 1000 个卡片全闪 → 加 memo 仍全闪 → 加 useCallback 后不闪。**一镜到底。**
- 截图：Profiler 火焰图优化前（48.2ms）/ 优化后（1.8ms）并排。
- 截图：渲染次数断言的红 / 绿两态。

---

## 九、C 档结论卡

**约 3 分钟。时间不够整体跳过。**

### 9.1 本次课没讲的 hooks

| hook | 一句话 | 何时学 |
|---|---|---|
| **`useEffect`** | **不是"状态变了就做事"，是"和 React 之外的系统同步"** | **第 12 次课** |
| `useRef` | 存一个"跨渲染保持、但改了不触发渲染"的值；或拿 DOM 节点 | 自读 |
| `useReducer` | 状态转移复杂时替代 `useState`。**它让"非法转移"更容易被禁止** | 自读 |
| `useContext` | 跨层传值。**不要当状态管理用**——context 变化会让所有消费者重渲染 | 自读 |
| `useId` | 生成稳定的无障碍 id。**不要用它当列表 key** | 自读 |

> `useEffect` 那句话值得记住：**很多人把它当成"监听状态变化"的钩子，那是误用。**
> 判据：如果一件事可以在事件处理函数里做，**就不要放进 `useEffect`**。

### 9.2 一句话结论卡

| 问题 | 结论 |
|---|---|
| 状态管理库（Redux / Zustand / Jotai）什么时候需要 | **当"状态需要在很多不相关的组件间共享"时**。三五个组件用 props 传就够 |
| 服务端状态（React Query / SWR） | 它们解决的是**缓存、去重、重试、失效**，不是"状态管理"。**第 12 次课会遇到这个需求** |
| React Compiler 会自动加 memo，那还要学这些吗 | **要**。它改变的是"优化手段"，不改变"状态驱动 + 引用判等"的心智模型。key 和不可变它一样帮不了你 |
| 严格模式（StrictMode）下组件渲染两次 | **开发期故意的**，用来暴露副作用不纯的问题。生产不会 |
| 为什么 hooks 不能写在 `if` 里 | React 按**调用顺序**匹配 hook 与状态槽位。顺序变了就错位——**和 key 的问题同构** |
| SSR / Server Components | 改变的是"在哪渲染"，本次课的心智仍然适用 |
| 虚拟滚动 | 只渲染视口内的行。**1000 行以上列表的首选方案**，优先级高于 memo |
| CSS-in-JS / Tailwind | 取舍问题，不是对错问题 |
| 动画与 key | 元素进出动画依赖 key 稳定。**key 错了动画也会错** |

### 9.3 跨框架对照（**值得讲，30 秒**）

| | React | Vue 3 | Svelte |
|---|---|---|---|
| **怎么知道状态变了** | **你调 `setState`** | **Proxy 拦截属性赋值** | **编译时给赋值语句插桩** |
| 要不要不可变 | **必须** | 不必，可原地改 | 不必 |
| 重渲染粒度 | 组件 | 组件（依赖追踪更细） | **精确到 DOM 节点** |
| 代价在哪 | **心智约定**（今天这节课） | **运行时 Proxy 开销** | **和编译器强耦合** |

> **判据：三者是在"运行时成本 / 编译期复杂度 / 心智约定"之间做不同取舍。没有免费的方案。**
>
> React 选择把成本放在**你身上**（约定），换取运行时简单和编译器解耦。
>
> **知道这一点，你就不会觉得"不可变约定"是 React 的缺陷——它是一个被明确定价的选择。**

---

## 十、作业与欠账

**约 5 分钟。**

### 10.1 作业一：组件化重写（主线，必交）

把第 2 次课那个命令式页面，完整重写为 React 组件。

| # | 要求 | 自检 |
|---|---|---|
| 1 | 至少拆出 5 个组件，每个有明确的单一职责 | 交一张组件树图 |
| 2 | **所有 props 类型来自 `api.d.ts`**，不手写 interface 描述后端数据 | grep 检查 |
| 3 | 所有列表的 `key` 使用稳定 id；**如有 index，必须注释说明理由** | ESLint |
| 4 | **所有 state 类型标注为 `readonly`**（数组用 `readonly T[]`，对象字段用 `readonly`） | grep |
| 5 | 表单全部受控，用统一 `handleChange` | — |
| 6 | 提交状态用可辨识联合四态 | — |
| 7 | 前端校验约束**从 `constraints.gen.ts` 读取**，不硬编码数字 | grep 数字字面量 |
| 8 | 422 响应的字段级错误落到对应字段下方 | 截图 |
| 9 | `npm run check` + `npm run lint` 零 error | CI 截图 |
| 10 | **零 `any`、零 `as`**（有则注释说明） | grep |

**`decisions.md` 新增两条**：
- 你的组件树是怎么划分的？**划分依据是什么？**（按"数据边界"还是按"视觉区块"？）
- 有哪些状态你**决定不放在父组件**（状态下移）？为什么？

### 10.2 作业二：key bug 复现与性能守卫（必交）

**第一部分：key bug**

| # | 要求 |
|---|---|
| 1 | 在你自己的项目里**构造一个** `key={index}` 导致的可见 bug（不能照抄课上的标签编辑器） |
| 2 | 录一段 10 秒的复现录屏或三张连续截图 |
| 3 | 写一段说明：**为什么会错位**（要画出 key 匹配过程，像 6.3 那样） |
| 4 | 修复，并说明**你修的到底是什么**（提示：不只是那一行 key） |

**第二部分：性能守卫**

| # | 要求 |
|---|---|
| 5 | 造一个 1000 行的列表，用 Profiler 量一次，交优化前火焰图 |
| 6 | 至少做**两处**优化，其中**至少一处不是 memo/useCallback**（必须用 8.4 优先级 1–3 里的手段） |
| 7 | 交优化后火焰图 |
| 8 | **写一条渲染次数断言**（8.5 的形式），并交红/绿两张截图 |

**必答三问**：

1. 你写的那条渲染断言，是断言**数值**还是断言**性质**？如果是数值，改成性质该怎么写？
2. 8.4 说"先量再优化"。**你有没有做了优化但 Profiler 显示没有明显改善的？** 说说是哪一处、为什么。
3. 如果把你的断言改成"渲染耗时不超过 16ms"，**会发生什么？** 结合第 9 次课关于 flaky 测试的结论回答。

> 第 2 问是重点。**能诚实地报告"我优化了但没用"，比交十张漂亮的火焰图更说明你在用工具而不是在猜。**

### 10.3 作业三：AI 的 React 代码审查（**课程主题作业**）

**第一部分：拿到样本**

向 AI 提一个需求（不要给它任何额外约束）：

> 用 React + TypeScript 写一个可编辑的待办列表组件：能添加、删除、勾选完成、行内编辑标题，还要有一个"全部完成"按钮。

**原样保存输出。**

**第二部分：逐条审查**

对照本次课内容，逐项检查并填表：

| # | 检查项 | 它的写法 | 违反了吗 | 后果 |
|---|---|---|---|---|
| 1 | 列表 `key` 用了什么 | | | |
| 2 | 数组更新用了 `push`/`splice`/`sort` 吗 | | | |
| 3 | 对象更新是原地改还是展开 | | | |
| 4 | 依赖旧值的 `setState` 用函数式了吗 | | | |
| 5 | `setState` 之后有没有立刻读那个 state | | | |
| 6 | 输入框是受控还是非受控 | | | |
| 7 | 有没有乱套 `memo` / `useCallback` | | | |
| 8 | "全部完成"是怎么实现的（一次 setState 还是循环 setState） | | | |

**第三部分：量化工具能抓住多少（本作业核心）**

| 步骤 | 做什么 | 记录 |
|---|---|---|
| ① | 原样跑 `tsc --noEmit` | 抓到 ___ 条 |
| ② | 原样跑 `eslint` | 抓到 ___ 条 |
| ③ | **把所有 state 类型改成 `readonly`**，再跑 `tsc` | **多抓到 ___ 条** |
| ④ | 开启 `react/no-array-index-key`，再跑 eslint | 多抓到 ___ 条 |
| ⑤ | 统计：第二部分找出 ___ 条问题，工具总共抓住 ___ 条 | **抓住率 ___%** |

**第四部分：必答四问（评分重点）**

| # | 问题 |
|---|---|
| 1 | 第三部分第 ③ 步，加一个 `readonly` **多抓住了几条？** 加这个 `readonly` 花了你多长时间？**用第 10 次课"护栏成本/收益"的框架评价这笔投入** |
| 2 | 有哪些问题是**任何工具都抓不到**的？列出来，并说明你打算靠什么机制发现它们 |
| 3 | **AI 在 React 上犯的错，和它在 SQL / 契约 / 包名上犯的错，性质一样吗？** 如果不一样，差别在哪 |
| 4 | 基于第 3 问，给出一条"让 AI 写 React 代码"的操作规则。**这条规则要和你在第 8、10 次课总结的那两条放在一起不冲突** |

> **第 3 问是本次作业的核心，也是本次课在课程 AI 主线上的推进。**
>
> 提示一个答案方向——**前面几次遇到的 AI 错误，和今天这次，来源不同**：

**封面级素材（讲作业时打出）**：

| AI 错误的来源 | 典型例子 | 它为什么会错 | 对策 |
|---|---|---|---|
| **缺少项目特定信息** | 猜字段名（第 8 次课）<br>漏业务约束（第 6 次课）<br>编造包名（第 10 次课） | **它不掌握这些事实** | **给它信息**：契约、schema、约束文档 |
| **训练数据里错误写法是多数** | `key={index}`<br>`arr.push()` 后 setState<br>`setState` 后立刻读 state | **它知道，但它在模仿多数** | **给它约束**：`readonly` 类型、lint 规则、明确的禁止清单 |

> 第二类是新的，而且**给更多上下文没用**——你把 React 官方文档整篇贴给它，它下一次还是会写 `key={index}`，因为互联网上这么写的代码比正确写法多。
>
> **判据：**
> - 面对第一类，**补充信息**；
> - 面对第二类，**施加约束**。
>
> 这两类的应对方式不同，**先判断是哪一类，再决定怎么做。**

### 10.4 本次课新增的欠账登记

| 欠账 | 何时还 |
|---|---|
| `useEffect` 与数据获取、加载态、竞态 | **第 12 次课** |
| 服务端状态缓存（React Query / SWR） | **第 12 次课** |
| 生产环境跨域（第 10 次课记账，仍未还） | **第 12 次课** |
| 路由与页面拆分 | **第 12 次课** |
| 认证态在组件树里怎么传（context 的正当用法） | **第 14 次课** |
| `dangerouslySetInnerHTML` 与富文本消毒 | **第 15 次课** |
| 前端构建产物部署、缓存头 | **第 16 次课** |
| `useRef` / `useReducer` / `useContext` | 课后自读 |
| 虚拟滚动 | 课后自读 |
| Immer 与深层状态 | 课后自读 |
| React Compiler | 课后自读 |

**一项需要说明的欠账调整**：

> 第 9 次课曾把"耗时类性能基线"和"缓存引入后的测试策略"登记到第 11 次课。
>
> **今天兑现了其中一半**：单元 8.5 把性能守卫从后端（SQL 条数）扩展到了前端（渲染次数），并在 8.6 给出了"为什么不断言耗时"的判据。
>
> **另一半（后端缓存与耗时基线）顺延**，因为它属于后端性能专题，**不应该塞进一节 React 课**。
>
> 这本身也是一条判据：**欠账登记是给自己的约束，但当课次内容不匹配时，正确的做法是重新登记，不是硬塞。** 硬塞的后果是两边都讲不透。

---

## 十一、素材清单与制作说明

### 必需素材

| 素材 | 说明 |
|---|---|
| tag `v11-broken` | 起始版：四个问题齐备。**`tsc` 和 ESLint 必须真的全绿**，这是解剖台戏剧性的来源 |
| tag `v11-immutable` | 单元 4 结束：`readonly` 就位、不可变更新改完 |
| tag `v11-key-fixed` | 单元 6 结束：Tag 有 id、key 修复 |
| tag `v11-form` | 单元 7 结束：受控表单 + 约束生成 |
| tag `v11-perf` | 单元 8 结束：优化 + 渲染断言 |
| tag `v11-final` | 作业参考交付 |
| `scripts/gen_constraints.py` | 完整可用，接进 `npm run gen` |
| `src/devtools/renderSpy.ts` + `tests/render-guards.test.tsx` | 完整可用，含红/绿两态 |
| **封面级 A** | 单元 1.1 的 `UI = f(state)` + 命令式代码对照 |
| **封面级 B** | 单元 2 的四个演示共同点表 + **"React 靠引用比较，不靠内容比较"**（两个方向的对照） |
| **封面级 C** | 单元 2 的"为什么用引用比较"三方案取舍表 |
| **封面级 D** | 单元 3.1 的"四次打印"表（`app.routes` / `dependency_overrides` / `openapi()` / `<div/>`） |
| **封面级 E** | 单元 3.3 的命令式/声明式五行对照表 |
| **封面级 F** | 单元 3.4 的四阶段链条图 |
| **封面级 G** | 单元 4.1 的三条触发条件（第二行高亮） |
| **封面级 H** | 单元 4.2 的 render / reconciliation / commit 三阶段表 |
| **封面级 I** | 单元 4.4 的不可变速查表 + 陷阱清单（`sort`/`reverse` 标红） |
| **封面级 J** | 单元 4.5 的 `readonly` 四条说明 |
| **封面级 K** | 单元 5.2 的快照心智图（渲染 #1 / #2 两栏） |
| **封面级 L** | 单元 5.3 的"依赖旧值就用函数式"判据表 |
| **封面级 M** | 单元 6.3 的 key 匹配过程图（**本次课最重要的一张图**） |
| **封面级 N** | 单元 6.3 的"key 与数据库主键"四行对照 |
| **封面级 O** | 单元 6.6 的"AI 错误类型"十行表（**第十行新增，不同颜色**） |
| **封面级 P** | 单元 7.3 的"前端校验是体验，后端校验是安全" |
| **封面级 Q** | 单元 7.3 的生成链图（第 8 次课那张 + `constraints.gen.ts` 新增分支） |
| **封面级 R** | 单元 8.4 的优化优先级四行表 |
| **封面级 S** | 单元 8.5 的**三层 N+1 守卫表**（三行三色） |
| **封面级 T** | 单元 10.3 的"AI 错误两类来源"表 |
| 高光图 U | 单元 4.3 的两条 diff 规则 |
| 高光图 V | 单元 5.5 的"setState 后不要读 state" |
| 高光图 W | 单元 6.5 的"index 什么时候安全" |
| 高光图 X | 单元 7.1 的受控/非受控对照 |
| 高光图 Y | 单元 8.4 的"状态下移"代码对照 |
| 高光图 Z | 单元 9.3 的三框架取舍表 |
| **录屏 1（最关键）** | key bug 复现：改第一行 → **暂停 3 秒让观众预测** → 删第一行 → 错位 |
| **录屏 2** | highlight updates：全闪 → 加 memo 仍全闪 → 加 useCallback 不闪 |
| 截图 | `console.log(<div/>)` 的对象结构 |
| 截图 | 演示一：数组里有了但界面不动（console + 界面同屏） |
| 截图 | 演示三：四行 log 全是 0 |
| 截图 | `const b = a.sort(); b === a` 返回 `true` |
| 截图 | `readonly` 下 `push` 的 tsc 报错 |
| 截图 | 错位时 DevTools 里 `props.tag="React"` 与 `state.draft="前端工程化"` 并列 |
| 截图 | **`tsc` 全绿 + ESLint 全绿 + 控制台干净，而界面是错的**（三窗同屏） |
| 截图 | Profiler 优化前 48.2ms / 优化后 1.8ms 并排 |
| 截图 | 渲染次数断言的红 / 绿两态 |
| 截图 | 改后端 `min_length` → `constraints.gen.ts` 的 `git diff` 变红 |

### 可后补

- C 档结论卡与跨框架对照（纯文字）。
- 单元 8.3 第三步 `useMemo` 的截图（若压缩则不需要）。

### 备用材料

| 风险 | 备用方案 |
|---|---|
| **React DevTools 版本差异导致 highlight updates 位置变**（高风险） | 备录屏；同时准备 8.5 的 `renderSpy` 数值版作为替代证据（**它不依赖 DevTools**） |
| StrictMode 下开发期渲染两次，干扰计数演示 | **课前在演示工程里关掉 StrictMode**，并在单元 9.2 说明原因 |
| Profiler 数字在教室机器上和课件对不上 | 所有数字标注"实测于某配置，**关键是倍数关系不是绝对值**" |
| key bug 演示时学生看不清哪里错了 | 准备一个**加了背景色标注**的版本：每行显示 `props.tag` 和 `state.draft` 两个值 |
| `crypto.randomUUID()` 在非 HTTPS 的旧环境不可用 | 备一个自增 id 工具函数 |
| `toSorted` / `toReversed` 环境不支持 | 演示用 `[...a].sort()`，`toSorted` 只在表里提及 |
| AI 现场调用失败（作业三演示） | 预录一份输出。**必须真实包含 `key={index}` 和至少一处 push**，不要人工编造 |
| 时间超支 | 按单元〇压缩顺序；单元 8 有自读材料 `docs/react-perf.md` |

### 环境与运行条件

延用第 10 次课环境。**新增**：React DevTools 浏览器扩展、`@testing-library/react`、`@testing-library/user-event`、`vitest`（若前序未装）。

**演示开始时的初始状态**：`web/` 在 tag `v11-broken`，`npm run dev` 已启动；浏览器已打开页面，**DevTools 的 Components 面板已打开**；第二个浏览器标签开着 Profiler；一个终端跑 `npm run check`。

**复位方式**：`git checkout v11-broken -- web/src`（热更新会自动生效，无需重启）。

---

## 十二、与前后课的衔接

**本次课回收的前序埋点**：

| 来源 | 埋点 | 回收位置 |
|---|---|---|
| 第 2 次课 | 命令式 DOM 操作、两份状态同步 | **单元 1.1、3.3**（声明式的对照面） |
| 第 3 次课 | "框架没有魔法，打印出来看" | **单元 3.1**（第四次使用） |
| 第 3 次课 | 422 响应的 `loc` / `type` 结构 | 单元 7.4（字段级错误映射） |
| 第 3 次课 | POST 不幂等 | 单元 7.4（`disabled` 防不住重复提交） |
| 第 3 次课 | 依赖稳定标识不依赖文案 | 单元 7.4（**第六次出现**） |
| 第 4 次课 | 分层：范围越小越好 | 单元 8.4（状态下移是同构判据） |
| 第 6 次课 | 每张表必须有主键 | **单元 6.3**（key 与主键是同一个问题） |
| 第 7 次课 | SQL 计数器 | **单元 8.5**（渲染计数是它的前端同构物） |
| 第 7 次课 | 事务边界越小越好 | 单元 8.4 |
| 第 8 次课 | 可辨识联合 `State<T>` | 单元 3.3、7.4 |
| 第 8 次课 | 契约只有一个真相来源，其余全部生成 | **单元 7.3**（从生成类型推进到生成约束） |
| 第 8 次课 | 列表页请求数 ≤ 2 | 单元 8.5（三层 N+1 的第二层） |
| 第 9 次课 | "红-绿两步"方法论 | 单元 4.5、6.6、8.5 各执行一次 |
| 第 9 次课 | 断言性质优于断言数值 | **单元 8.5、8.6** |
| 第 9 次课 | 宁可少几条检查，也不要有一条会误报 | 单元 6.6（`no-array-index-key` 设 warn） |
| 第 9 次课 | 检查的严谨程度配得上问题的严重程度 | 单元 4.5（`readonly` 是浅的但够用） |
| 第 9 次课 | flaky 测试先查共享状态和时间依赖 | 单元 8.6（为什么不断言耗时） |
| 第 9 次课 | 契约一致性检查（`git diff --exit-code`） | 单元 7.3（新文件零成本接入） |
| 第 10 次课 | 必须构建：浏览器不认 JSX | **单元 3.1**（看到它被转成了什么） |
| 第 10 次课 | 类型只存在于编译期 | 单元 4.5（`readonly` 运行时不存在） |
| 第 10 次课 | 类型是最便宜的护栏 | **单元 4.5、作业三第 1 问** |
| 第 10 次课 | "AI 错误类型 vs 谁能抓"十行表 | **单元 6.6 新增第十行**（如约兑现） |
| 第 10 次课 | `dangerouslySetInnerHTML` | 单元 10.4 记账（第 15 次课） |
| 第 10 次课 | 生成的 `api.d.ts` | 作业一第 2 条（props 类型来源） |

**本次课埋下、后面必须回引的五处**（请在课件中明显标记）：

- **单元 5.2 的快照心智** → 第 12 次课讲 `useEffect` 时，**闭包捕获旧值**是最大的坑，必须回到这张图；
- **单元 5.4 的批处理** → 第 12 次课讲异步数据获取的**竞态问题**时会用到；
- **单元 4.1 第二行（父渲染子无条件渲染）** → 第 14 次课把认证态放进 context 时，要回引说明"为什么 context 值变化代价大"；
- **单元 8.5 的三层 N+1 表** → 后续每引入一层（缓存、队列），都应该问"这一层的 N+1 长什么样、怎么断言"；
- **单元 10.3 的"AI 错误两类来源"表** → 第 15 次课的安全问题大多属于第二类（**训练数据里不安全的写法是多数**），要回引。

**本次课不承担、请勿提前引入**：`useEffect` 与副作用（第 12 次课）、数据获取与竞态（第 12 次课）、路由（第 12 次课）、CORS 生产解法（第 12 次课）、认证态与 context（第 14 次课）、XSS 与富文本（第 15 次课）、部署（第 16 次课）。

**给第 12 次课的提示**：

本次课把**同步的心智模型**建立完整了：`UI = f(state)`、引用判等、key 匹配、快照。

第 12 次课引入 `useEffect` 和异步数据获取时，**所有困难都来自"异步打破了快照的直觉"**：

| 第 12 次课会遇到的坑 | 它的根在今天哪一节 |
|---|---|
| `useEffect` 里读到旧的 state / props | **单元 5.2 快照心智** |
| 依赖数组写错导致不更新或死循环 | 单元 4（引用判等）+ 单元 5 |
| 快速切换时旧请求的响应覆盖新的（竞态） | 单元 5.2 + 5.4 |
| 每次渲染都发请求 | 单元 4.1（触发条件） |
| 卸载后 setState 警告 | 单元 3.4（组件生命周期） |

**建议第 12 次课开场就把单元 5.2 那张快照图再打一次**，并宣布："今天所有的坑，都是这张图在异步下的推论。"

另外，本次课留下了一个**尚未兑现的判断**，值得在后续检验：单元 8.4 说"默认不要加 memo，先量再优化"。随着项目变复杂，学生会遇到第一个**真正需要优化的场景**——那时候要回引 8.4 的优先级表，**检查他们是不是直接跳到了第 4 级**。如果是，这正是把"先量再优化"讲成习惯的最好时机。