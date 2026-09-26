# 第 11 次课教学底稿（第四版）
## React 组件：props、state 与列表身份

> **备课基线**：[第四版大纲](../syllabus-v4.md)第 11 课与[第 10 课交接](lesson-10.md#83-下一课明确接收什么)。本稿未归档，定义教学内容与配套工程要求，不代表正式课程包、React DevTools 证据或最终 Slidev 已交付。`web/` 指学生问答工程，不是本 Slidev 仓库根目录。

## 〇、这次课学会什么

**讲给学生的目标句**：你能做出一个可交互的问题列表，并解释每一份状态属于哪个组件实例。

核心解释目标只有一个：**组件身份与状态归属——state 属于哪个实例，列表变化后它还属于原来的问题吗？** 支撑它的最小快照概念是：本次 render 创建的事件处理函数，读取的是本次 render 的 state 值。

**前置卡**：函数、箭头函数、map、解构、事件。第 10 课已提供能运行的 React 外壳，但未教授 hooks；本课从正确卡片开始，不从多组缺陷、引用比较口诀或性能基准开场。

### 80 分钟教学 + 15 分钟小测 + 5 分钟缓冲

| 分钟 | 教学单元 | 当场产出 |
|---|---|---|
| 5 | 回顾与目标 | 源码→React→DOM，固定练习数据与责任 |
| 15 | ①卡片→②props→③局部 state／事件 | 一个能展开正文的正确组件 |
| 12 | ④受控输入与本次 render 的值 | 可编辑草稿与一次 setter 前后预测 |
| 25 | ⑤学生任务：交互列表与稳定 key | 状态归属选择、删除／重排后的正确结果 |
| 15 | ⑥index key 对照与迁移检查 | 行内／父级按 id／父级按位置三种存法 |
| 8 | 常用写法卡、一个作业包与交接 | 解释核对与表单 UI 课后边界 |
| **80** | **教学合计** | **不含小测和缓冲** |
| 15 | 小测：3 题 | 正例阅读、身份迁移、边界判断 |
| 5 | 缓冲 | 总计 100 分钟 |

严格按①→⑥递进；完整状态更新队列、批处理与并发渲染进参考层，不承诺第 12 课系统补讲。最小函数式更新到第 16 课流式累积首次需要时再讲。AI 保持**阶段一：解释器**，不布置 React 最佳实践评审或必须找错。

### 模板与理解边界

| 内容 | 标注 | 学生承担什么 |
|---|---|---|
| 卡片、props、state、事件、value/onChange、map/key | 要求解释 | 写局部交互，说明状态拥有者与更新结果 |
| 固定 JSON、样式、Vite／TS／ESLint 与原门禁 | 教师提供，要求会用 | 不修改公开 API，不现场选依赖或搭 CI |
| 三种草稿存法的核心绑定与删除操作 | 要求解释 | 先预测，再按给定条件解释差异 |
| 实验选页、完整重载、测试驱动设施 | 黑盒 | 会复位，不开发测试平台、不进口试内部 |
| 表单字段与 UI 三态 | 要求解释 | 课后完成受控输入、即时提示与模拟反馈 |
| 表单请求占位控制器 | **黑盒** | 原样调用，不修改或解释其内部；第 12 课才接真实请求 |
| React DevTools | 要求会用 | 教师课前配置；学生核对 props 与 state 所属组件，不背面板布局 |

## 一、交接：今天只操作本地练习列表

**课堂 5 分钟。** 第 10 课解释源码如何成为浏览器执行的 JS；本课解释 React 如何根据 props/state 计算界面，以及如何保留组件状态。组件函数产生界面描述，React DOM 将结果提交到 DOM；重新执行组件函数不等于整页 DOM 全部重建，也不保证每次调用都产生一次可见提交。

教师提供本地固定 JSON。这里的 `author` 是**练习展示字段**，不是第 10 课公开列表 API 新增的字段。删除、重排、草稿都只是内存 UI 操作，不发送 DELETE、PATCH 或 POST。

`web/src/questions.ts`：

<!-- lesson11: questions -->
```ts
export interface LessonQuestion {
  id: number;
  title: string;
  author: string;
  body: string;
}

export const QUESTION_SEED: LessonQuestion[] = [
  { id: 101, title: "甲问题：模块如何连接", author: "小林", body: "这是一段用于展开演示的甲问题正文。" },
  { id: 102, title: "乙问题：类型如何检查", author: "小周", body: "这是一段用于展开演示的乙问题正文。" },
  { id: 103, title: "丙问题：配置如何公开", author: "小陈", body: "这是一段用于展开演示的丙问题正文。" },
];
```

本课不覆盖 `contracts.ts`：原 GET 仍是 keyword/page/page_size、items/total/page、每项 id/title/body/tags/created_at 五字段。详情／创建／PATCH 七字段、投票与版本、四字段错误、HTML／healthz、服务提交和 001→002 均不变。也不假称已有 `api.d.ts` 或约束自动生成链。

## 二、教师构建：先有卡片，再有输入与状态

**课堂 15 分钟。①写死卡片 4 分钟，②props 5 分钟，③局部 state／事件 6 分钟。** 三份阶段文件独立运行，不把同名定义同时粘入一个文件。

### 2.1 ①写死卡片：组件是界面的组织单位

`web/src/StaticCard.tsx`：

<!-- lesson11: static_card -->
```tsx
export function StaticCard() {
  return (
    <article>
      <h2>甲问题：模块如何连接</h2>
      <p>作者：小林</p>
      <p>这是一段用于展开演示的甲问题正文。</p>
    </article>
  );
}
```

- `StaticCard` 是组件函数；通过 `<StaticCard />` 放入树，不在父组件里手动调用它。
- 大写开头表示组件引用；小写标签通常表示 DOM 元素。JSX 的 `{}` 放 JavaScript 表达式；条件也可以在 return 之前用普通 if 处理。
- JSX 不是 HTML 字符串，也不是已经创建好的 DOM 节点。构建工具转换 JSX，React 处理描述；不背内部对象字段或固定 `$$typeof` 值。
- 组件函数在模块顶层定义，不嵌在父组件函数里每次重新定义，以免组件类型变化意外重置状态。

### 2.2 ②标题、作者作为 props 传入

`web/src/PropsCard.tsx`：

<!-- lesson11: props_card -->
```tsx
interface PropsCardProps {
  title: string;
  author: string;
  body: string;
}

export function PropsCard({ title, author, body }: PropsCardProps) {
  return (
    <article>
      <h2>{title}</h2>
      <p>作者：{author}</p>
      <p>{body}</p>
    </article>
  );
}
```

父组件调用节选：

```tsx
<PropsCard title="甲问题：模块如何连接" author="小林" body="甲问题正文。" />
<PropsCard title="乙问题：类型如何检查" author="小周" body="乙问题正文。" />
```

同一个组件定义可以产生多个位置上的实例。props 是父组件传来的输入，不是子组件可随意修改的数据；标题变动应由拥有它的上层提供新值。普通文本插值不会把正文当 HTML 执行，不引入富文本渲染。

### 2.3 ③展开正文：状态属于使用它的组件实例

`web/src/ExpandableCard.tsx`：

<!-- lesson11: expandable_card -->
```tsx
import { useState } from "react";
import type { LessonQuestion } from "./questions";

export function ExpandableCard({ question }: { question: LessonQuestion }) {
  const [expanded, setExpanded] = useState(false);
  return (
    <article data-qid={question.id}>
      <h2>{question.title}</h2>
      <p>作者：{question.author}</p>
      <button type="button" aria-expanded={expanded}
        onClick={() => setExpanded(!expanded)}>
        {expanded ? "收起正文" : "展开正文"}
      </button>
      {expanded && <p>{question.body}</p>}
    </article>
  );
}
```

先挂两张固定卡片，点击甲：只展开甲，乙仍收起。`useState(false)` 不是每次 render 都把状态改回 false；React 为当前实例保留状态，下次调用提供当前值。这里的“实例”指树中的组件身份，不要求它是 JavaScript class 对象。

`setExpanded` 请求更新，`onClick` 收到函数而非 `setExpanded(...)` 的执行结果。本例每个独立点击只切换一次，不引入循环 setter、定时器或异步竞争。`useState` 在组件顶层、稳定顺序调用，不放 if／循环／事件函数内部。

## 三、受控输入：草稿是谁的，读到的是哪次值

**课堂 12 分钟。6 分钟输入，4 分钟快照预测，2 分钟边界。**

### 3.1 ④让输入框有明确的数据来源

从上面的卡片加一个草稿。最终可复用的 `web/src/QuestionCard.tsx` 如下；此时先单独挂一张，下一单元才 map 成列表。

<!-- lesson11: question_card -->
```tsx
import { useState } from "react";
import type { LessonQuestion } from "./questions";

interface QuestionCardProps {
  question: LessonQuestion;
  onRemove: () => void;
}

export function QuestionCard({ question, onRemove }: QuestionCardProps) {
  const [expanded, setExpanded] = useState(false);
  const [draft, setDraft] = useState(question.title);
  return (
    <li data-qid={question.id}>
      <h3>{question.title}</h3>
      <p>作者：{question.author}</p>
      <button type="button" aria-expanded={expanded}
        onClick={() => setExpanded(!expanded)}>
        {expanded ? "收起正文" : "展开正文"}
      </button>
      {expanded && <p>{question.body}</p>}
      <label>草稿
        <input value={draft} onChange={(event) => setDraft(event.currentTarget.value)} />
      </label>
      <p>草稿预览：{draft}</p>
      <button type="button" onClick={onRemove}>移除本地行</button>
    </li>
  );
}
```

单卡阶段放在 `<ul>` 中，教师给 `onRemove={() => {}}` 占位；下一单元才接真正的内存删除。不是请求删除的黑盒 API。

`value={draft}` 决定显示，onChange 把本次输入写回 state；初值始终为字符串，不在 undefined 与字符串之间切换。输入框受控，**不代表状态必须在父组件**：本例的控制值就在行组件自己的 state。

`useState(question.title)` 只为新的组件身份提供初始状态，不是 props→state 持续同步器。现存实例收到新的 question 时，draft 不会自动改成新标题；这正是下一组身份对照必须写清的条件。普通 JS 表达式仍可能每次求值，不能把“初值被忽略”说成“表达式永远只执行一次”。

### 3.2 观察点一：setter 不改写当前处理函数读到的值

完整条件：初始 expanded=false，页面已提交；一次真实点击，处理函数只执行下面一次，没有其他写者、计时器或跨次保存的旧 handler。`web/src/SnapshotDemo.tsx`：

<!-- lesson11: snapshot -->
```tsx
import { useState } from "react";

export function SnapshotDemo() {
  const [expanded, setExpanded] = useState(false);
  function toggle() {
    const next = !expanded;
    console.log("调用前", expanded);
    setExpanded(next);
    console.log("调用后仍读取", expanded);
  }
  return <button type="button" onClick={toggle}>{expanded ? "已展开" : "已收起"}</button>;
}
```

先预测两条日志与下一次可见按钮文字，再运行。

| 时点 | 结果与解释 |
|---|---|
| 第一次点击内，两条日志 | false、false；当前 handler 读取的是此次 render 的值 |
| 更新提交后 | 按钮为“已展开”；新的 render 得到 true |
| 看见更新后再独立点击 | 日志 true、true，随后显示“已收起” |

```text
render A：expanded=false → handler A 读取 false → 请求设为 true
                                                   ↓
render B：expanded=true  → handler B 读取 true → 新界面
```

原因不是“因为声明成 const 所以 React 更新不了”，换成局部 let 也不会让 setter 改写该绑定。快照也不等于深拷贝／冻结对象：props/state 中的对象必须按不可变约定使用。可以读取旧值做比较，不能误把它当已更新的新值；不立“调用 setter 后一律禁止读取”的规则。

完整更新队列与批处理不进入本次预测。这里的同步事件足以支持下个单元；第 12 课在 Effect 中回收“闭包读到哪次 render”，第 16 课才讲持续累积所需的最小函数式更新。

## 四、学生任务：把卡片做成可交互列表

**课堂 25 分钟。3 分钟决定归属，12 分钟实现，5 分钟删除／重排验证，3 分钟解释归属，2 分钟记录 AI 核对素材。**

### 4.1 固定需求与自主决定

- 使用上述三条 JSON，id 不改、不临时随机生成；标题与作者通过 props 传递。
- 每行至少有一个局部状态：展开或草稿。即使草稿提升到父组件，也保留行内 expanded 供观察。
- 实现移除本地行和反转顺序；保留问题的业务身份，不增加服务端字段／端点。
- 草稿可以留在行内，也可以在父组件按 id 保存。先写一句理由：谁需要读／改它，是否需要在行卸载后继续保留？本课两种正确选择均可。
- 正确版必须使用稳定业务 id 作为 key，再进入教师提供的 index 对照。自主设计测试输入，不自主改变公开契约。

### 4.2 正确参考：列表拥有集合，卡片拥有展开与草稿

`web/src/QuestionList.tsx`：

<!-- lesson11: question_list -->
```tsx
import { useState } from "react";
import { QUESTION_SEED } from "./questions";
import { QuestionCard } from "./QuestionCard";

export function QuestionList() {
  const [questions, setQuestions] = useState(QUESTION_SEED);
  function remove(id: number) {
    setQuestions(questions.filter((question) => question.id !== id));
  }
  return (
    <section>
      <h2>本地问题列表</h2>
      <button type="button" onClick={() => setQuestions([...questions].reverse())}>
        反转顺序
      </button>
      {questions.length === 0 && <p>列表为空</p>}
      <ul>
        {questions.map((question) => (
          <QuestionCard key={question.id} question={question}
            onRemove={() => remove(question.id)} />
        ))}
      </ul>
    </section>
  );
}
```

map 返回组件描述，key 放在 map 直接返回的元素上；它用于 React 匹配，不作为普通 props 传入。需要 id 时显式使用 question.id。

filter 返回新数组；反转先展开复制，不直接 reverse 原 state。数组浅拷贝不会复制其中的对象，若修改对象字段，还须为被改对象创建新对象。不可变是使用约定，不承诺运行时冻结；不要求全量 readonly、DeepReadonly 或新增扫描器。

以上每个事件读当前已提交 render 的集合，并进行一次更新；不推广到异步循环／同一处理函数多次叠加的情境。

### 4.3 正确版先验收

初始顺序 101、102、103。将草稿分别改成 `甲草稿*`、`乙草稿*`、`丙草稿*`，只展开 102，等页面更新后操作：

| 操作 | 预期 |
|---|---|
| 移除 101 | 剩下 102／103；各自草稿不变，102 仍展开 |
| 从该结果反转 | 顺序 103／102；草稿与展开仍跟各自 id |
| 再逐项移除 | 出现空列表；无不存在的业务请求 |
| 完整刷新 | 重取固定数据与初值；本课未承诺持久化 |

不要用 HMR 保留的旧状态代替干净起点，不在错误版残留状态上直接改 key 再截图。key 一变可造成重挂载；验证修复必须复位后重新输入。

### 4.4 画出真正的状态拥有者

```text
QuestionList：questions（有哪些行、什么顺序）
  ├─ QuestionCard key=101：props.question=甲；state.expanded／draft
  ├─ QuestionCard key=102：props.question=乙；state.expanded／draft
  └─ QuestionCard key=103：props.question=丙；state.expanded／draft
```

标题、作者、正文是给定数据；草稿是尚未提交的 UI 输入，不能每次敲字就覆盖原 question.title。当前需要一起协调的状态放到共同父组件；只属于一行的可以留在行内。上移或下移不是一律更好，按读写与保留需求选择。

## 五、index key：位置身份和业务身份何时分离

**课堂 15 分钟。5 分钟行内对照，5 分钟父级两种存法，3 分钟迁移，2 分钟边界。** 先预测再揭晓；下表为教师答案，不应在预测前全部展示。

### 5.1 所有对照共同的完整条件

- 四个独立副本从同一固定三条数据开始；同一父列表、同一种行组件类型，父级结构不切换，期间没有 HMR／刷新／其他写者。
- 所有输入都是 `value + onChange` 受控；没有 Effect 同步 props，没有 key 随机数，也没有从 DOM 读回草稿。
- 将三个草稿依次改成甲草稿*／乙草稿*／丙草稿*，只展开 102；每一步等 UI 更新。然后移除 **101**，剩余业务数据为 102、103。
- **父级按位置组**的删除明确只更新 questions，不删除、移动或重新配对 drafts 数组；反转也只反转 questions。若同步修改两份数组，那是另一套实现，不沿用本题答案。
- 新场景完整刷新；同一浏览器里不切配置后继续用上一组状态。行内初值取 question.title；父级草稿的初值来自同一标题。

### 5.2 观察点二：行内草稿，唯一变量是 key

| 存法与 key | 删除后 102 输入 | 删除后 103 输入 | 展开的行 |
|---|---|---|---|
| 行内 state，key=id（正确基线） | `乙草稿*` | `丙草稿*` | 102 |
| 行内 state，key=index（已知缺陷） | `甲草稿*` | `乙草稿*` | **103** |

“原第二行”指业务 id=102，不是删除后仍占第二个位置的行。两种组别中 h3 都显示正确的乙／丙标题，因为 props 已更新；错的是被复用实例保留的局部状态，不是数据库内容凭空改变。

```text
删除前：key 0 → 实例 A（101，甲草稿*，收起）
        key 1 → 实例 B（102，乙草稿*，展开）
        key 2 → 实例 C（103，丙草稿*，收起）
删除后：key 0 → 实例 A 收到 102 的 props，保留甲草稿*／收起
        key 1 → 实例 B 收到 103 的 props，保留乙草稿*／展开
        key 2 → 不再渲染，实例 C 被卸载
```

React 没有“认错业务 id”；我们提供的 key 在告诉它按照位置延续身份。`useState(question.title)` 不会在 props 改变时重新初始化已有状态。

### 5.3 观察点三：提升状态是否足够

两组都保持 **key=index**，都把草稿作为 props 传给输入行；但其拥有者与寻址方式不同：

```tsx
// 组 A：父组件按业务 id 保存
const [drafts, setDrafts] = useState<Record<number, string>>(initialById);
value={drafts[question.id] ?? ""}
// 编辑时：setDrafts({ ...drafts, [question.id]: value })

// 组 B：父组件按位置保存
const [drafts, setDrafts] = useState<string[]>(initialByPosition);
value={drafts[index] ?? ""}
// 编辑时：setDrafts(drafts.map((old, i) => i === index ? value : old))
```

这是绑定节选，不可连在一起当作完整组件；可运行对照见 §9.1。

| key 都是 index | 删除后 102／103 的输入 | 行内 expanded 的结果 |
|---|---|---|
| 父级按 id 取草稿 | `乙草稿*`／`丙草稿*` | 仍跟位置复用，**103 展开** |
| 父级按位置取草稿，删除不改草稿数组 | `甲草稿*`／`乙草稿*` | 同样 **103 展开** |

结论：**草稿放在哪里，和草稿按什么身份查找，是两件事。** 父级按 id 能让这个受控 value 正确，不证明 index key 已经适合其他局部状态、焦点或第三方组件。焦点／选择区的具体表现另测，不在此无条件预测“必跳到某行”。

父级位置数组若与列表同步删除／重排，某些操作也可得到正确文字；必须维护对应关系，且不能自动修复行内身份。本课正确提交统一使用稳定业务 key；不得用 Effect 把每次 props 都覆盖回草稿来掩盖错位，那可能覆盖未提交输入。

### 5.4 迁移检查：换成联系人也能解释吗

给定联系人 `[201:小林, 202:小周]`，同一父列表、同一种行组件，每行局部 `useState(contact.name)` 初始化受控备注。将备注改为 `林备注*`／`周备注*`，等 UI 更新后删除 201，仅更新联系人集合；没有 Effect、其他写者或树结构切换。index／id 两组各从干净状态重做。先分别预测 **202 的备注**，再解释父级 `Record<id, note>` 会改变什么。

答案：index 留下“林备注*”，id 留下“周备注*”；父级按 id 受控显示可正确，但仍需判断其他局部状态是否错配。只换领域名称，沿用同一套身份推理，不另开发联系人系统。

### 5.5 key 的保证范围

- 匹配发生在同一父级的兄弟集合，结合元素／组件类型；key 不是全局主键，不能保证跨父树移动仍保留状态。
- 稳定 key 支持正确保留身份，**不等于不会重渲染**。React 可重新调用组件而保留其 state。
- 行不再渲染时局部 state 会丢失；以后重新插入相同 id 不等于复活旧实例。需要保留草稿须另有仍存活的拥有者或持久化策略。
- 不在 render 中生成随机 key，不用可编辑标题冒充稳定身份。真正固定不重排的展示序列可按位置；本课可删除／重排列表不满足该条件。
- TypeScript 与当前 ESLint 通过，不证明身份正确；不虚构“开启了所有 React 检查”。若后续加插件，须核对实际规则与 `--max-warnings 0`，warning 也可能阻断门禁。

## 六、收尾：卡片与一个作业包

**课堂 8 分钟。3 分钟卡片，3 分钟交付，2 分钟说明课后表单与下一课。**

### 常用写法卡 #11

| 写法 | React／工具替你做什么 | 必须知道的边界 |
|---|---|---|
| 顶层函数组件与 JSX | 组织界面描述、更新 DOM | 函数重新执行不等于整棵 DOM 重建 |
| props 向下传、事件回调向上通知 | 连接组件输入与动作 | props 不是子组件任意修改的共享变量 |
| useState＋事件 | 为组件身份保留局部值并请求更新 | setter 不改写当前 handler 读到的值 |
| value＋onChange | 用 React 中的值控制输入 | 受控可以是行内 state，不等于父级所有 |
| map＋稳定业务 id key | 关联前后两次列表中的组件身份 | 只在适用父级／类型边界内匹配，不保证跳过 render |
| 展开、filter、map | 构造新的数组／对象更新 | 展开是浅拷贝，不能继续改原嵌套对象 |
| 选择状态拥有者与 id 寻址 | 让读写者共享正确一份状态 | 上移本身不修复位置错配，也不自动持久化 |
| 表单提示与 disabled | 提供即时反馈、约束当前交互 | 不替代后端校验、授权、并发或防重机制 |

### A 档：一个可交互列表与表单 UI 包

1. 正确列表源码、依赖锁定与版本说明；固定数据、稳定 key、至少一项行内状态、删除／重排可用。没有组件数量指标。
2. key 实验记录：行内 id 正例、行内 index 缺陷、父级按 id／按位置两种存法的结果；写清操作、草稿与 expanded 分别归谁，不只交“改了一行 key”。
3. 一张组件／状态归属图和联系人迁移解释；学生所选草稿位置有理由即可，不要求统一提升或统一下移。
4. 一次 **AI 解释 vs 实际运行**：让 AI 解释自己刚完成的一段，用 React DevTools Components 核对实例的 props、expanded、draft；正确解释可直接接受。没有扩展或未核对时如实标缺口，不把 DOM 截图冒充 DevTools。
5. 下节前完成 §8 的表单 UI、即时提示、模拟 pending／成功／失败；附 check／lint／build 结果，原统一门禁不删减。

阶段一概念三问并入同一记录：这份草稿由谁拥有？删除后哪个身份被保留？受控／key／前端校验各不保证什么？卡片补例复用记录，不另交审计报告、抓错率、1000 行优化或渲染次数守卫。

## 七、15 分钟小测：3 题，共 10 分

题目只覆盖课堂已教内容。给学生题干与必要代码，教师答案另置备注／答案页；不能用隐藏的模板内部实现出题。

### 题 1：读正确组件（3 分）

两个固定同父级的 ExpandableCard 分别展示 101／102，初始都收起。仅点击 101 一次，事件内先读取 expanded、调用 `setExpanded(!expanded)`、再读取 expanded。没有其他更新。

问：谁的状态发生更新？两次读取各是什么？下一次可见界面是什么？

**教师答案**：更新 101 对应实例（1 分）；false／false（1 分）；101 展开、102 收起，setter 请求下一次 render 的值，不改写当前绑定（1 分）。不要求解释队列或调用次数。

### 题 2：迁移到购物车（4 分）

顺序为 `[501:水杯, 502:书包, 503:台灯]`。同父列表、同一种行组件、key=index；每行 `useState(product.name)` 初始化受控备注，无 Effect。用户改成“杯备注*／包备注*／灯备注*”，等 UI 更新后删除 501，仅更新 products。

问：业务商品 502／503 下显示什么备注？为什么？改成 id key 后从干净状态重做，结果是什么？

**教师答案**：杯备注*／包备注*（1 分）；key=0／1 的旧实例复用且局部 state 不随 props 自动重置（2 分）；包备注*／灯备注*（1 分）。不接受仅答“React 缓存有问题”。

### 题 3：两份“修好了”的说法（3 分）

延续题 2，所有行仍 key=index、每行另有局部 expanded。方案 A 的备注存在父级 `Record<id, string>`；方案 B 存在父级数组，按当前 index 取值，删除商品时不改备注数组。另有人说：“输入受控，发布按钮有 disabled，所以后端可以不校验。”

**教师答案**：A 的备注显示可正确，但局部 expanded 仍可能跟错身份（1 分）；B 的备注仍错配，提升位置不等于修复寻址（1 分）；拒绝省略后端校验，前端交互可绕过且不构成业务／安全保证（1 分）。

## 八、课后表单 UI 与第 12 课交接

### 8.1 教师给模板，学生只完成 UI 和本地状态

表单标题／正文保持原输入文本，用即时提示帮助用户；本课只传 title/body/tags，其中 tags 固定为 []，不提前教标签编辑器。没有 author_id、vote_count 或 version 输入。

提示规则参考批准的创建契约：title 清理首尾空白后 5–200、body 10–20000。附录的最小提示使用 JS trim 与 Unicode 码点计数，不使用原始 UTF-16 length 冒充所有字符计数；**不宣称与后端 Python strip 在全部 Unicode 空白上同构**。完整输入合法性仍由后端负责，本课无 HTTP 提交，不生成新约束文件或改变后端规则。

教师提供：字段布局、CreateForm 接口、模拟请求占位控制器、正确参考与未完成 UI 起点。学生实现受控字段、提示、pending 时禁用、成功／失败反馈与重置；控制器内部为黑盒，不要求开发 Promise 调度、定时器、Effect 或请求库。

本例采用**手动完成模拟**：合法提交→pending→点击教师控制区的“模拟成功／模拟失败”。这样 pending 可稳定观察，不靠网络延迟。模拟成功不创建任何资源，不伪造 201、Location 或 request-id；失败不冒充真实 422／409。

验收条件：

- 空值／越界给字段提示；初值是字符串，label 关联正确。
- 合法输入提交到占位函数，pending 可见、字段和提交按钮禁用；不能仅把按钮文字改掉。
- 成功与失败都保留原草稿供观察；修改字段或重置后回到 idle。不得声称刷新后仍保留。
- 失败可恢复到一次新的模拟提交；重置清空输入。不需要自动重试或缓存失效。
- Network 没有因表单操作发起业务请求；不把“模拟成功”截图当真实创建验收。

### 8.2 下一课明确接收什么

第 12 课接收正确列表、状态归属解释、最小事件快照心智、表单 UI 与模拟反馈。它从正确读取和 Effect 闭包出发，再教过期结果保护、Query key、mutation、422／409 映射、成功后的失效与回读；本课未完成这些内容。

完整更新队列、批处理和并发渲染仍是参考；最小函数式更新在第 16 课首次需要时现场讲。Router／URL 查询状态归第 13 课，完整 CORS／部署归第 16 课。旧第 12 课仍带多缺陷开场、生产跨域欠账与提前的路由任务，须另行按 v4 重写；本轮不改该课。

### 8.3 B 档与参考层

B 档只选一次真实交互的 Profiler 观察并尝试 memo；允许无改善，说明相同功能／数据／构建模式／设备下的测量。没有真实卡顿就如实记录，不必造满 1000 行或两处优化。不把 render 次数等同 DOM 操作，也不与 SQL N+1 混称同一缺陷。

完整更新队列、批处理、并发调度、useCallback／useMemo、readonly 的浅层限制、React Compiler 与深层状态管理只作参考。不得把性能时长、固定 render 次数或某个内部对象形状列成课堂必背保证。

## 九、教师附录：可运行对照与模板

本附录不占课堂逐行抄写时间。沿用第 10 课已核验 Vite／TS／React 与脚本；本轮不另装 React 编译器、Fast Refresh 或 hooks lint，也不把“沿用基线”当依赖仍受支持的证明。正式发包前须处理第 10 课记录的 ESLint 支持警告并核验锁文件。阶段组件、列表与表单必须能各自打开。

### 9.1 完整 key 对照

`web/src/KeyLab.tsx`。行内草稿组直接复用上面的 QuestionCard；父级存法的输入行保留自己的 expanded，以便区分“文字正确”和“整个实例身份正确”。

<!-- lesson11: key_lab -->
```tsx
import { useState } from "react";
import { QUESTION_SEED } from "./questions";
import type { LessonQuestion } from "./questions";
import { QuestionCard } from "./QuestionCard";

export type LabMode = "local-id" | "local-index" | "parent-id" | "parent-position";
const INITIAL_BY_ID = Object.fromEntries(QUESTION_SEED.map((q) => [q.id, q.title]));
const INITIAL_BY_POSITION = QUESTION_SEED.map((q) => q.title);

function ParentDraftRow({ question, draft, onDraft, onRemove }: {
  question: LessonQuestion;
  draft: string;
  onDraft: (value: string) => void;
  onRemove: () => void;
}) {
  const [expanded, setExpanded] = useState(false);
  return (
    <li data-qid={question.id}>
      <h3>{question.title}</h3>
      <p>作者：{question.author}</p>
      <button type="button" aria-expanded={expanded}
        onClick={() => setExpanded(!expanded)}>{expanded ? "收起正文" : "展开正文"}</button>
      {expanded && <p>{question.body}</p>}
      <label>草稿<input value={draft} onChange={(event) => onDraft(event.currentTarget.value)} /></label>
      <p>草稿预览：{draft}</p>
      <button type="button" onClick={onRemove}>移除本地行</button>
    </li>
  );
}

export function KeyLab({ mode }: { mode: LabMode }) {
  const [questions, setQuestions] = useState(QUESTION_SEED);
  const [byId, setById] = useState<Record<number, string>>(INITIAL_BY_ID);
  const [byPosition, setByPosition] = useState(INITIAL_BY_POSITION);
  function remove(id: number) {
    setQuestions(questions.filter((q) => q.id !== id));
  }
  return (
    <section>
      <h2>身份对照：{mode}</h2>
      <p>删除／反转只改变 questions；父级草稿容器不随之删除或重排。</p>
      <button type="button" onClick={() => setQuestions([...questions].reverse())}>反转顺序</button>
      <ul>
        {questions.map((question, index) => {
          if (mode === "local-id" || mode === "local-index") {
            return <QuestionCard key={mode === "local-id" ? question.id : index}
              question={question} onRemove={() => remove(question.id)} />;
          }
          return <ParentDraftRow key={index} question={question}
            draft={mode === "parent-id" ? (byId[question.id] ?? "") : (byPosition[index] ?? "")}
            onDraft={(value) => {
              if (mode === "parent-id") setById({ ...byId, [question.id]: value });
              else setByPosition(byPosition.map((old, i) => i === index ? value : old));
            }}
            onRemove={() => remove(question.id)} />;
        })}
      </ul>
    </section>
  );
}
```

这个父级为了并列对照保留了两个草稿容器，不是要求学生正式组件同时维护两份状态。mode 在一次实验中固定；切场景须整页重新加载。保留已移除 id 的草稿只是本例条件，不是默认的隐私／持久化策略。

### 9.2 表单类型与即时提示

`web/src/form-model.ts`，教师提供参考规则，学生要求会用；不考 Unicode 或生成器内部。

<!-- lesson11: form_model -->
```ts
export interface CreateDraft { title: string; body: string }
export interface CreateInput extends CreateDraft { tags: string[] }
export type SubmitState =
  | { kind: "idle" }
  | { kind: "pending" }
  | { kind: "success" }
  | { kind: "error"; message: string };

export function validateDraft(draft: CreateDraft) {
  const titleLength = Array.from(draft.title.trim()).length;
  const bodyLength = Array.from(draft.body.trim()).length;
  return {
    title: titleLength < 5 || titleLength > 200 ? "标题去首尾空白后需 5–200 个字符" : "",
    body: bodyLength < 10 || bodyLength > 20000 ? "正文去首尾空白后需 10–20000 个字符" : "",
  };
}
```

### 9.3 表单 UI 正确参考

`web/src/CreateForm.tsx`。这里给完整参考，不以省略的占位代码声称可运行；学生起点由教师在独立副本留出 UI 练习位置。

<!-- lesson11: create_form -->
```tsx
import { useState } from "react";
import { validateDraft } from "./form-model";
import type { CreateDraft, CreateInput, SubmitState } from "./form-model";

export function CreateForm({ submit, onSubmit, onReset }: {
  submit: SubmitState;
  onSubmit: (input: CreateInput) => void;
  onReset: () => void;
}) {
  const [draft, setDraft] = useState<CreateDraft>({ title: "", body: "" });
  const errors = validateDraft(draft);
  const pending = submit.kind === "pending";
  const valid = !errors.title && !errors.body;
  return (
    <form noValidate onSubmit={(event) => {
      event.preventDefault();
      if (!valid || pending) return;
      onSubmit({ ...draft, tags: [] });
    }}>
      <h2>创建表单 UI（不发送请求）</h2>
      <label htmlFor="create-title">标题</label>
      <input id="create-title" value={draft.title} disabled={pending}
        aria-invalid={Boolean(errors.title)} aria-describedby="title-hint"
        onChange={(event) => { setDraft({ ...draft, title: event.currentTarget.value }); onReset(); }} />
      <p id="title-hint">{errors.title}</p>
      <label htmlFor="create-body">正文</label>
      <textarea id="create-body" value={draft.body} disabled={pending}
        aria-invalid={Boolean(errors.body)} aria-describedby="body-hint"
        onChange={(event) => { setDraft({ ...draft, body: event.currentTarget.value }); onReset(); }} />
      <p id="body-hint">{errors.body}</p>
      <button type="submit" disabled={!valid || pending}>{pending ? "模拟提交中…" : "模拟发布"}</button>
      <button type="button" disabled={pending} onClick={() => {
        setDraft({ title: "", body: "" }); onReset();
      }}>重置表单</button>
      {submit.kind === "pending" && <p role="status">等待教师控制区完成模拟</p>}
      {submit.kind === "success" && <p role="status">模拟成功，未创建后端资源</p>}
      {submit.kind === "error" && <p role="alert">{submit.message}</p>}
    </form>
  );
}
```

没有设置 HTML maxLength 来截断原文；即时提示不改变原输入。页面只挂一份该表单，因此静态 label id 不重复。若复用多份表单，教师应提供独立 id 前缀等接线，不把可访问性问题留给复制粘贴。

### 9.4 请求占位控制器：黑盒，不是网络适配器

`web/src/MockCreatePage.tsx`。学生只按 §9.3 的接口使用；本轮没有任何 fetch／请求库调用，按钮控制代替真实网络完成。

<!-- lesson11: mock_create -->
```tsx
import { useState } from "react";
import { CreateForm } from "./CreateForm";
import type { CreateInput, SubmitState } from "./form-model";

export function MockCreatePage() {
  const [submit, setSubmit] = useState<SubmitState>({ kind: "idle" });
  const [lastInput, setLastInput] = useState<CreateInput | null>(null);
  function begin(input: CreateInput) {
    if (submit.kind === "pending") return;
    setLastInput(input);
    setSubmit({ kind: "pending" });
  }
  return (
    <section>
      <CreateForm submit={submit} onSubmit={begin} onReset={() => setSubmit({ kind: "idle" })} />
      <fieldset>
        <legend>教师模拟控制区（不是真实服务器）</legend>
        <button type="button" disabled={submit.kind !== "pending"} onClick={() => {
          if (submit.kind === "pending") setSubmit({ kind: "success" });
        }}>模拟成功</button>
        <button type="button" disabled={submit.kind !== "pending"} onClick={() => {
          if (submit.kind === "pending") setSubmit({ kind: "error", message: "模拟失败，请修改或再次模拟提交" });
        }}>模拟失败</button>
      </fieldset>
      <p>当前模拟状态：<output data-submit-state>{submit.kind}</output></p>
      <pre data-last-input>{lastInput ? JSON.stringify(lastInput, null, 2) : "尚无模拟输入"}</pre>
    </section>
  );
}
```

lastInput 是教师观察用的**上次模拟入参快照**，重置表单不抹去它；不得当成当前字段值或服务器存储。第 12 课替换这个控制器并重新验证真实异步生命周期，不以本控制器证明重复请求、取消或错误码处理正确。

### 9.5 环境、证据与复位

- 教师发正确阶段文件、固定数据、缺陷对照和表单 UI 起点，不依赖不存在的 Git tag，不强制 checkout 覆盖学生代码。
- dev 固定本机 5173、strictPort；本课不启动后端，不占用 8000。第 10 课代理配置可以保留，但本课教学页不引用 api.ts、不发业务请求。
- 正确版先 check／lint／build，仍接第 9／10 课的统一入口。隔离已知缺陷可以类型与 lint 通过，不由此推断 ESLint 所有配置都不能检查 index key。
- 样式和启动页由教师提供；本课不考 CSS。组件练习不得改变 Slidev 根的 Vue 依赖或全局样式。
- 复位用本实验页面完整刷新或独立副本；确保没有 HMR 残留。开发 StrictMode 可能有额外调用，不把 console render 次数当身份判据，也不要求为凑次数关闭保护。
- 证据至少包含业务 id／标题、草稿值、expanded 和操作顺序；React DevTools 核对 props/state。没有 DevTools 时可用标注的教师录屏备用，但须说明不是学生本机现场证据。
- 课前核验浏览器扩展、依赖缓存与录屏；网络或 AI 不可用时用注明来源的材料。正确 AI 解释可以接受，不强求现场生成错误。

## 十、制作与验证状态

- **隔离源码检查已通过**：本稿 11 个标记代码块逐一提取并与临时源码核对一致；`npm run verify` 中 check／lint／build 均退出 0，浏览器测试驱动另跑 `tsc --noEmit -p tsconfig.verify.json` 退出 0。课时核对为 80 教学＋15 小测＋5 缓冲。临时工程为 `.build-check/l11-6828ee14-6abb-4a9e-8f6a-6224c4e8daf9/`，工具记录在其中的 `tool-results.json`；验证入口为 `.build-check/validate_lesson11.mjs`。沿用第 10 课已安装的临时依赖，本轮未独立 npm install／ci；Node 22.14.0、React／React DOM 19.2.0、TypeScript 5.9.3、Vite 8.2.2、ESLint 9.39.1。不是正式课程包或依赖支持验收。
- **浏览器自动机制检查已通过**：Qoder 内嵌 Chromium 148.0.7778.97 的 `verify.html` 实际报告 **78 通过、0 失败、failure=null**：递进正例 6、受控与初始化 5、事件快照 4、正确列表 9、key 删除矩阵 16、key 重排矩阵 12、不可变边界 1、即时提示 9、表单模拟 14、边界 2。使用真实浏览器 React DOM 与 act 驱动的程序化输入／点击，覆盖同身份新 props、新 key、卸载后重挂、StrictMode、四组删除／重排、表单原文与模拟状态；不是人工鼠标操作或 React DevTools 证据。自动阶段未观察到业务 fetch/XHR，控制台 error／warn 为 0；不以此替代普通教学页的人工 Network 验收。
- **人工可视核验待补**：浏览器视图返回 `NATIVE_BROWSER_VIEWPORT_UNAVAILABLE`（hidden／未附着），普通列表首个输入操作超时且值未改变。因此列表／表单的人工流程、可见布局、截图、人工 Network 与 React DevTools Components 均未验收；本轮没有生成截图。课前须在可见浏览器完成 §4.3、§5 和 §8.1 的操作，并核对组件 props/state 拥有者。
- **正式课程包待制作**：受支持依赖组合与锁文件、学生未完成 UI 起点、实验入口、原统一门禁接线、React DevTools 证据及备用材料。底稿完整参考不等于正式课程工程已交付。
- **试讲待验收**：本课是 v4 首轮试讲对象。记录 25 分钟列表任务完成情况、能否独立迁移 key 推理、是否误把受控等同父级状态、三种存法是否能在 15 分钟讲清；保留 15 分钟小测，不用参考专题挤占。
- **范围边界**：本轮不改后端／数据库／公开契约，不实现真实创建／Query／Router，不运行远端 CI／部署，不制作最终 Slidev／PDF。

参考：[React 状态快照](https://react.dev/learn/state-as-a-snapshot)、[保留和重置状态](https://react.dev/learn/preserving-and-resetting-state)、[列表渲染](https://react.dev/learn/rendering-lists)、[受控 input](https://react.dev/reference/react-dom/components/input)。最终 Slidev 中教师时间、答案揭晓、制作与备用说明进备注；学生理解所需条件、任务、结果与边界留正文。
