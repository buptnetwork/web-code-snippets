# 第 12 次课教学底稿
## 副作用、数据获取与跨域：异步打破了快照

---

## 〇、给 PPT 制作团队的全局说明

本次课 100 分钟，留 5 分钟缓冲。**本次课把第 11 次课建立的同步心智推到异步，并清掉两笔拖了两节课的欠账（生产跨域、服务端状态）。**

**本次课的核心思想，请让它贯穿始终**：

> **第 11 次课的快照心智：每一次渲染的 `state`、`props`、你创建的每个函数，都是那一次渲染的快照。**
>
> **今天的全部困难，都是这句话遇上"响应会晚一点到"之后的推论。**

开场第一页就要把第 11 次课单元 5.2 的快照图**原样再打一次**，然后宣布这句话。后面单元 3、4、5 每一节结束时回引一次。

**本次课有三个高光，按重要性排序**：

1. **竞态现场复现（单元 5，15 分钟）**。这是现场必做。戏剧性在于：**URL 栏显示 `id=2`，标题显示"问题 1"**——而且它只在特定时序下发生，本地开发几乎碰不到。这是本课程第一个**"同样的输入不产生同样的输出"**的 bug，它打破了前面九节课所有检查手段的共同前提。这个方法论冲击比 bug 本身更重要。
2. **CORS 的真相（单元 6，15 分钟）**。戏剧性在于：浏览器一片红，**后端日志里躺着一个 200**。请求到了、处理了、返回了，是浏览器把响应扣下了。这一刻讲清"同源策略限制的是读取响应，不是发出请求"，第 15 次课的 CSRF 就有了地基。
3. **`queryKey` 是 key 的第三次出现（单元 8.3，5 分钟）**。数据库主键 → React key → 缓存 key，三层、三个技术栈、同一个问题：**如何唯一标识一个东西**。这一页是全课程"判据可迁移"这条线最漂亮的一次兑现。

**第四处值得重点制作的**：单元 3.5 的 **StrictMode 是一道护栏**。React 在开发期故意把 effect 执行两次，就是为了让"漏写 cleanup"和"effect 不可重入"当场暴露。**框架主动把一条纪律变成了会出声的机制**——这是本课程主题在框架内部的一次印证。它是第十道结构性护栏，且拦截时机是全新的"**开发期**"。

**一个必须守住的边界**：本次课**不讲认证**。token 放哪、cookie 的 `SameSite`、登录态怎么在组件树里传，全部留给第 14 次课。CORS 单元会讲到 `allow_credentials`，**只讲机制，不展开认证方案**。

**若时间不够的压缩顺序**：先压单元 9 的 C 档卡（整体移课后）→ 再压单元 7 的路由（只留"能放进 URL 的状态就放进 URL"这条判据 + `useSearchParams` 一段代码）→ 再压单元 8.4 的 mutation 与失效（移作业）。**单元 3、4、5、6 不能压缩。**

---

## 一、开场：同步的世界结束了

**约 4 分钟。**

### 1.1 先把第 11 次课那张图打回来

**原样重放第 11 次课单元 5.2 的快照图**：

```
渲染 #1
  ├─ count = 0                      （这次调用里的常量）
  ├─ handleClick = () => {          （闭包捕获了 count = 0）
  │     setCount(0 + 1);
  │  }
  └─ ...

渲染 #2
  ├─ count = 1                      （新的一次调用，新的常量）
  └─ handleClick = () => { ... }    （新的函数，捕获 1）
```

讲：

> 上节课我们建立了这个模型，然后用它解释了四个 bug。
>
> 但上节课所有的例子有一个共同点：**所有事情都在一瞬间完成。** 点击 → setState → 重渲染，中间没有等待。
>
> **今天引入一件事：等待。**

**封面级素材**：

> **发起请求的那一刻，你捕获的是一份快照。**
>
> **响应回来的那一刻，世界已经变了。**
>
> **今天所有的坑，都是这两句话之间的落差。**

### 1.2 今天要清的两笔账

> 除了异步，今天还要还两笔欠了两节课的账：

| 欠账 | 第几次课记的 | 当时说了什么 |
|---|---|---|
| **生产环境的跨域** | 第 8 次课记账，第 10 次课补了原因 | "proxy 只在开发期有效，因为它是 dev server 的功能" |
| **服务端状态的缓存** | 第 9 次课记账，第 11 次课顺延 | "它不属于 React 课的内容" |

> 这两笔今天一起还。而且你会发现：**它们和异步是同一个主题的三个侧面。**
>
> 异步的本质是：**你要的数据不在你这里，你得去拿，拿的过程中时间会流逝。**
>
> - 时间流逝 → **竞态**（单元 5）
> - 数据在别的域 → **跨域**（单元 6）
> - 拿回来的东西会过期 → **缓存与失效**（单元 8）

### 1.3 本次课要回答的问题

- `useEffect` 到底是干什么的？它是"监听状态变化"吗？
- 依赖数组写错会怎样？为什么 lint 老是警告？
- 为什么我切换得快一点，页面就显示错的内容？
- 为什么浏览器报 CORS 错误，后端日志却是 200？
- 为什么我的 POST 请求在 Network 里变成了两条？
- 分页参数该放 `useState` 还是放 URL？
- **什么时候该上一个库，什么时候是在过度工程？**

---

## 二、解剖台：AI 写的数据获取

**约 12 分钟。四个演示都要做。**

### 情境设定

> 你对 AI 说："把问题列表和详情页接上后端，要有加载状态，切换问题时能刷新。"
>
> 它给了你一套组件。看起来非常标准——**这种写法在教程里、在 Stack Overflow 上、在 AI 的输出里，出现过几百万次。**
>
> `tsc` 零错误。ESLint 有几条 warning，**但大部分人会忽略它们。**

### 代码（tag: `v12-broken`）

```tsx
// src/pages/QuestionDetail.tsx —— AI 原样产出
export function QuestionDetail({ id }: { id: number }) {
  const [question, setQuestion] = useState<QuestionOut | null>(null);

  useEffect(() => {
    fetch(`/api/questions/${id}`)
      .then(r => r.json())
      .then(setQuestion);                    // ③ 无竞态保护
  }, [id]);

  if (!question) return <div>加载中…</div>;   // ② 二态，错误态没有了
  return <h1>{question.title}</h1>;
}
```

```tsx
// src/pages/QuestionList.tsx
export function QuestionList() {
  const [items, setItems] = useState<QuestionOut[]>([]);
  const [page, setPage] = useState(1);
  const [sort, setSort] = useState<"latest" | "views">("latest");

  const params = { page, sort, size: 20 };     // ④ 每次渲染都是新对象

  useEffect(() => {
    fetch(`/api/questions?${new URLSearchParams(params as any)}`)
      .then(r => r.json())
      .then(d => setItems(d.items));
  }, [params]);                                 // ④ 对象依赖

  return <ul>{items.map(q => <li key={q.id}>{q.title}</li>)}</ul>;
}
```

```tsx
// src/components/Poller.tsx
export function Poller() {
  const [count, setCount] = useState(0);

  useEffect(() => {
    setInterval(() => {
      setCount(count + 1);                     // ⑤ 闭包捕获旧值
    }, 1000);
  }, []);                                       // ⑤ 没有 cleanup

  return <span>已刷新 {count} 次</span>;
}
```

```tsx
// src/components/Stats.tsx
export function Stats({ items }: { items: QuestionOut[] }) {
  const [total, setTotal] = useState(0);

  useEffect(() => {                             // ⑥ 派生状态用了 effect
    setTotal(items.reduce((s, q) => s + q.answer_count, 0));
  }, [items]);

  return <p>共 {total} 条回答</p>;
}
```

先让学生看 60 秒，问：**哪几段代码你觉得有问题？**

**典型反应：`Poller` 大家能看出问题（上节课刚讲过闭包），其余三段没人说得出。第二段的 `params` 尤其隐蔽。**

### 演示一：Network 面板炸了

打开 `QuestionList`，看 Network：

```
/api/questions?page=1&sort=latest&size=20     ← 第 1 条
/api/questions?page=1&sort=latest&size=20     ← 第 2 条
/api/questions?page=1&sort=latest&size=20     ← 第 3 条
...
（每秒几十条，一直在涨）
```

**让它滚 10 秒，让学生看着数字往上跳。**

> **无限循环。**
>
> 链条是这样的：
>
> ```
> 渲染 → params 是新对象 → 依赖变了 → effect 跑 → setItems → 重渲染
>   ↑                                                              │
>   └──────────────────────────────────────────────────────────────┘
> ```
>
> `const params = { page, sort, size: 20 }` 这一行，**每次渲染都在创建一个新对象**。
>
> 这正是上节课演示四的翻版——`memo` 失效是因为 props 里的函数每次都是新引用，**今天 effect 无限循环是因为依赖数组里的对象每次都是新引用。**
>
> **同一条规则，第三次出现。** 单元 4 会把三次并排放出来。

**然后指出关键一点**：

> ESLint 其实报了：
>
> ```
> warning  The 'params' object makes the dependencies of useEffect Hook change on every render.
>          Move it inside the useEffect callback.   react-hooks/exhaustive-deps
> ```
>
> **它说得一字不差。但它是 warning，而且这个项目里有一堆 warning。**
>
> 这就是第 9 次课那条判据的反面教材：**一个会被忽略的警告，等于没有警告。**

### 演示二：后端挂了，页面永远转圈

把后端的详情接口临时改成返回 500，刷新详情页：

```
加载中…
```

**永远。**

> `.then(setQuestion)` 后面没有 `.catch`。请求失败了，`question` 永远是 `null`，于是永远显示"加载中"。
>
> 用户看到的是：**页面卡住了。** 他不知道是网慢、是自己网络问题、还是系统坏了。
>
> **回收第 8 次课**：当时我们做过一个 `State<T>` 四态（loading / error / empty / success），并且说过一句话：
>
> **"二态是一个陷阱：它把'失败'和'还没回来'混为一谈。"**
>
> AI 这次又退回二态了。**而且注意：它退回去的时候，类型是完全正确的**——`QuestionOut | null` 没有任何问题。

### 演示三：切换快一点就错乱（**先演一次，单元 5 完整展开**）

快速点击"问题 1" → "问题 2"。

**画面：先出现问题 2，然后跳回问题 1。**

**停 5 秒，只说一句**：

> URL 是 2，内容是 1。
>
> **这个演示是今天的现场必做，单元 5 完整讲。现在只记一件事：它不是每次都发生。**

### 演示四：轮询只涨到 1，还停不下来

打开 `Poller`：

```
已刷新 1 次
```

**永远停在 1。**

> 上节课讲过：`setInterval` 回调里的 `count` 是**创建它那次渲染的快照**，永远是 0，所以永远 `setCount(1)`。
>
> 修法上节课也讲过：`setCount(c => c + 1)`。
>
> **但今天有第二个问题，上节课没有：**

切到别的页面，再打开 console：

```
（每秒仍在打印）
```

> **组件已经卸载了，定时器还在跑。**
>
> `useEffect` 没有返回清理函数，这个 `setInterval` 永远不会被清掉。切十次页面，就有十个定时器在后台跑。
>
> 如果里面是 `fetch`，那就是**十倍的后端请求**。

### 演示五：一个不该存在的状态

`Stats` 组件：

```tsx
const [total, setTotal] = useState(0);
useEffect(() => { setTotal(items.reduce(...)); }, [items]);
```

> 这段代码**能跑，结果也对**。但它有三个问题：
>
> | 问题 | 说明 |
> |---|---|
> | 多一次渲染 | 先渲染出 `total=0`，effect 跑完再渲染一次正确值 |
> | **有一帧是错的** | 用户可能看到"共 0 条回答"闪一下 |
> | **两份真相** | `items` 和 `total` 可能不同步 |
>
> 正确写法是一行：
>
> ```tsx
> const total = items.reduce((s, q) => s + q.answer_count, 0);
> ```
>
> **判据：能算出来的，不要存起来。存起来就要同步，同步就会漂移。**
>
> 这条判据你已经见过两次了：第 6 次课"不要存冗余字段，要能从源数据算出来"；第 8 次课"契约只有一个真相来源，其余全部生成"。**今天是第三次，换到了组件状态上。**

### 五个演示的归类（**封面级素材**）

| # | 现象 | 根源 | 上节课的哪条规则 |
|---|---|---|---|
| ① | 无限请求 | **依赖数组里放了每次都新建的对象** | 引用判等 |
| ② | 永远加载中 | 没有错误态 | —（第 8 次课的三态/四态） |
| ③ | 内容错乱 | **响应顺序 ≠ 请求顺序** | 快照 |
| ④ | 计数停在 1 | **闭包捕获了快照** | 快照 |
| ④' | 卸载后还在跑 | **没有清理函数** | — |
| ⑤ | 多一帧错误值 | 用 effect 做派生状态 | — |

**然后打出核心句**：

> ①③④ 全部来自上节课的两条规则。**它们不是新知识，是旧规则在"有等待"的世界里的推论。**
>
> 而 ②④'⑤ 是三件新东西：**错误态、清理、以及"什么不该用 effect 做"。**

### 欠账清单

| 问题 | 本次课处理 | 何时还 |
|---|---|---|
| effect 的正确用途 | **单元 3** | — |
| 清理函数 / StrictMode | **单元 3.4、3.5** | — |
| 依赖数组 | **单元 4** | — |
| 竞态 | **单元 5** | — |
| 完整的加载状态机 | **单元 5.5** | — |
| 生产跨域 | **单元 6** | — |
| URL 作为状态 | **单元 7** | — |
| 缓存、去重、失效 | **单元 8** | — |
| 认证 token 怎么带 | 单元 6.5 点到为止 | **第 14 次课** |
| SPA 路由刷新 404 | 单元 7.4 记账 | **第 16 次课** |
| CSRF | 单元 6.2 埋点 | **第 15 次课** |
| 乐观更新、无限滚动 | 单元 9 结论卡 | 课后自读 |

---

## 三、`useEffect` 是同步，不是监听

**约 11 分钟。**

### 3.1 最常见的误解

问学生：**`useEffect(fn, [x])` 是什么意思？**

典型回答："监听 x，x 变了就执行 fn。"

> **这个理解会让你写出一大堆错误代码。**
>
> 正确的理解是：

**封面级素材**：

> **React 管理的是 UI 树。有些东西不在它的管辖范围内。**
>
> **`useEffect` 的职责是：让那些外部系统的状态，和你的 state 保持一致。**
>
> **它的名字应该读作"同步"，不是"监听"。**

**哪些是"React 之外的系统"**：

| 外部系统 | 例子 |
|---|---|
| 网络 | 发请求拿数据 |
| 浏览器 API | `document.title`、`localStorage`、`IntersectionObserver` |
| 定时器 | `setInterval`、`setTimeout` |
| 第三方库实例 | 地图、图表、富文本编辑器 |
| 订阅 | WebSocket、事件总线 |

### 3.2 判据：什么该放 effect，什么不该

**封面级素材，学生会截图带走的一页**：

| 需求 | 放哪 | 理由 |
|---|---|---|
| 点按钮发 POST | **事件处理函数** | 它由用户动作触发，不是由状态触发 |
| 提交成功后跳转 | **事件处理函数** | 同上 |
| 关闭弹窗后聚焦某个输入框 | **事件处理函数** | 同上 |
| 根据 `items` 算 `total` | **渲染时直接算** | 能算出来的不要存（演示五） |
| 根据 `keyword` 过滤列表 | **渲染时直接算**（贵就 `useMemo`） | 同上 |
| 组件出现时拉取数据 | **useEffect** | 由"组件存在"这件事触发 |
| 筛选条件变了重新拉取 | **useEffect**（依赖筛选条件） | 由状态触发 |
| 同步 `document.title` | **useEffect** | 外部系统 |
| 订阅/退订 WebSocket | **useEffect + cleanup** | 外部系统 |

**一条总判据**：

> **能在事件处理函数里做的事，不要放进 `useEffect`。**
>
> 为什么？因为事件处理函数里你**确切知道发生了什么**（"用户点了提交"），而 effect 里你只知道**某个值变了**——你得反过来推测是什么导致的。
>
> 举个具体的：

```tsx
// ❌ 用 effect 响应一个事件
const [submitted, setSubmitted] = useState(false);
useEffect(() => {
  if (submitted) navigate("/done");
}, [submitted]);

// ✅ 事件就在事件里处理
async function handleSubmit() {
  await createQuestion(form);
  navigate("/done");
}
```

> 上面那个写法额外制造了一个状态 `submitted`，而这个状态**除了触发跳转没有任何用处**。它是一个"为了用 effect 而存在的状态"。
>
> **判据：如果一个状态的唯一用途是触发某个 effect，那它和那个 effect 都不该存在。**

### 3.3 那"拉数据"为什么可以放 effect？

> 因为它的触发源确实是"组件存在"和"某个参数变了"，而不是某个具体的用户动作。
>
> 用户可能是：点了链接进来、刷新了页面、从后退按钮回来、直接粘贴 URL 打开。
>
> **这四种情况都要拉数据，但它们不是同一个事件。** 它们的共同点是"现在需要 id=5 的数据"。
>
> **这正是"同步"而不是"监听"的含义：不管怎么来的，让数据和 id 对上就行。**

### 3.4 清理函数：不是"卸载时执行"

**这是本单元第二个关键点，必须讲准确。**

```tsx
useEffect(() => {
  const timer = setInterval(tick, 1000);
  return () => clearInterval(timer);      // ← 清理函数
}, []);
```

**醒目页**：

> **清理函数的执行时机有两个，不是一个：**
>
> 1. **组件卸载时**
> 2. **每一次 effect 重新执行之前**
>
> 第 2 条最容易被忽略，**而它正是解决竞态的关键**（单元 5）。

**画一条时间线**：

```
id = 1
  ├─ effect 执行 #1：发请求 A
  │
id = 2（依赖变了）
  ├─ 【先执行 #1 的清理】     ← 很多人不知道有这一步
  ├─ effect 执行 #2：发请求 B
  │
组件卸载
  └─ 执行 #2 的清理
```

> 所以正确的心智是：**每一次 effect 执行，都伴随一次对应的清理。它们成对出现。**
>
> **判据：写 effect 时，先问"这次执行建立了什么？它需要被拆掉吗？"**
>
> | effect 建立了 | 需要清理吗 |
> |---|---|
> | 定时器 | ✅ `clearInterval` |
> | 事件监听 | ✅ `removeEventListener` |
> | WebSocket 连接 | ✅ `close()` |
> | 第三方库实例 | ✅ `destroy()` |
> | **一个进行中的请求** | ✅ **见单元 5** |
> | 只读了一下 `localStorage` | ❌ |
> | 设置了 `document.title` | ⚠️ 看情况 |

### 3.5 StrictMode 是一道护栏（**本单元最重要的一段**）

**先把第 11 次课关掉的东西打开**：

```tsx
// src/main.tsx
createRoot(root).render(
  <StrictMode>          {/* ← 上节课为了演示方便关掉了，今天打开 */}
    <App />
  </StrictMode>
);
```

刷新页面，看 Network：

```
/api/questions/1
/api/questions/1        ← 两条！
```

**学生的第一反应一定是"这是 bug"。**

> **不是 bug，是故意的。**
>
> React 在**开发环境**下，会对每个 effect 做一件事：
>
> ```
> 执行 effect → 立刻执行清理 → 再执行一次 effect
> ```
>
> **它在故意考你：你的 effect 经得起"执行两次"吗？**

**醒目页**：

> **StrictMode 检查的是一条纪律：effect 必须可重入。**
>
> 具体来说：
> - **漏了清理函数** → 第二次执行会叠加（两个定时器、两个订阅）
> - **effect 里有不该有的副作用** → 会执行两遍（比如发了两次 POST）
> - **清理函数写错了** → 第二次执行后状态不对

**拿演示四实证**：

```tsx
// 没有 cleanup 的 Poller，在 StrictMode 下
useEffect(() => {
  setInterval(() => setCount(c => c + 1), 1000);
}, []);
```

```
已刷新 2 次      ← 一秒涨 2，因为有两个定时器
已刷新 4 次
已刷新 6 次
```

> **数字一秒跳 2。这就是"漏了清理"的信号，而且是一眼能看出来的信号。**

加上清理：

```tsx
  return () => clearInterval(timer);
```

```
已刷新 1 次
已刷新 2 次      ← 恢复正常
```

**然后把这件事提到方法论高度（封面级素材）**：

> 这门课从第 2 次课开始就在讲同一件事：
>
> **"把依赖人记得的规则，换成会出声的机制。"**
>
> 而 StrictMode 就是 **React 自己对自己做的这件事**。
>
> "effect 要写清理函数"本来是一条纪律，靠人记得。StrictMode 把它变成了**开发期一眼可见的现象**。
>
> 这是我们见过的第十道结构性护栏，**而且它的拦截时机是全新的**：

**护栏累加表（封面级素材，新增两行）**：

| 次课 | 护栏 | 拦住什么 | 拦截时机 |
|---|---|---|---|
| 第 3 次课 | `response_model` | 字段泄漏 | 运行时 |
| 第 4 次课 | 全局异常处理器 | 内部信息泄漏 | 运行时 |
| 第 5 次课 | Jinja2 自动转义 | 输入变 HTML | 运行时 |
| 第 6 次课 | 数据库约束 | 脏数据写入 | 运行时 |
| 第 7 次课 | `lazy="raise"` | 静默 N+1 | 运行时 |
| 第 8 次课 | 生成的类型 | 字段名写错 | 编译期 |
| 第 9 次课 | CI 检查 | 违反任何约定 | 合并前 |
| 第 10 次课 | lockfile + `npm ci` | "装了什么"不确定 | 安装时 |
| 第 10 次课 | 产物机密扫描 | 密钥随产物发出 | 构建后 |
| **第 11 次课** | **`readonly` 类型** | **原地修改 state** | **编译期** |
| **第 12 次课** | **StrictMode** | **effect 不可重入 / 漏清理** | **开发期** |

> 十一道护栏，**七个不同的拦截时机**。
>
> 判据：**好的护栏体系，不是同一时机堆很多道，而是在每一个"错误可能溜过去"的时机上都有一道。**

**最后给一条操作纪律**：

> **StrictMode 永远开着。**
>
> 如果某个 effect 在 StrictMode 下表现异常，**那不是 StrictMode 的问题，是那个 effect 的问题**。
>
> 上节课我为了演示方便关掉了它——**那是一个教学妥协，不是推荐做法。今天起它一直开着。**

### 材料

- **封面级素材**：3.1 的"同步不是监听"核心句 + 外部系统清单。
- **封面级素材**：3.2 的"什么该放 effect"九行判据表。
- **封面级素材**：3.4 的清理函数时间线图（"重新执行之前"高亮）。
- **封面级素材**：3.5 的"StrictMode 是 React 自己做的那件事" + 护栏累加表（新增两行，"开发期"用新颜色）。
- 高光图：3.4 的"建立了什么需要拆掉吗"七行表。
- 截图：StrictMode 下 Network 出现两条同样的请求。
- 录屏：无 cleanup 时计数一秒跳 2 → 加上 cleanup 后恢复正常。

---

## 四、依赖数组：引用判等的第三次出现

**约 10 分钟。**

### 4.1 三次出现，同一条规则

**封面级素材**：

| 场景 | 比较什么 | 用什么比 | 哪次课 |
|---|---|---|---|
| 要不要重渲染 | 新旧 state | `Object.is` | 第 11 次课单元 2 |
| `memo` 要不要跳过 | 新旧 props（逐个浅比较） | `Object.is` | 第 11 次课单元 8 |
| **effect 要不要重跑** | **新旧依赖数组（逐项）** | **`Object.is`** | **今天** |

> **三个完全不同的功能，用的是同一条判等规则。**
>
> 所以演示一的无限循环，和上节课 `memo` 失效，是**同一个 bug 的两个面孔**：
>
> | | 上节课 | 今天 |
> |---|---|---|
> | 每次渲染新建的东西 | 箭头函数 `onSelect` | 对象 `params` |
> | React 看到 | props 变了 | 依赖变了 |
> | 后果 | 白渲染 1000 次 | **无限请求** |
>
> 上节课的后果是"慢"，今天的后果是"炸"。**同一条规则，代价升级了。**

### 4.2 三种依赖数组

**醒目页**：

| 写法 | 什么时候执行 | 典型用途 |
|---|---|---|
| **不写** | **每次渲染后都执行** | 几乎总是 bug |
| `[]` | 只在挂载后执行一次 | 订阅、一次性初始化 |
| `[a, b]` | `a` 或 `b` 的**引用**变了就执行 | 大多数情况 |

> 第一行要特别警告：**不写依赖数组 + effect 里调 setState = 无限循环**。
>
> 而且它一定会无限循环，不是"可能"。

### 4.3 修演示一：三种改法

```tsx
// 病灶
const params = { page, sort, size: 20 };
useEffect(() => { fetch(...) }, [params]);
```

| 改法 | 代码 | 评价 |
|---|---|---|
| **① 拆成原始值** | `useEffect(() => { fetch(...) }, [page, sort])` | ✅ **首选，最简单** |
| ② 对象移进 effect | 在 effect 内部构造 `params` | ✅ 也好 |
| ③ `useMemo` 包住 | `const params = useMemo(() => ({page, sort}), [page, sort])` | ⚠️ 多绕一圈，除非 `params` 还要传给别处 |

**给出判据（醒目页）**：

> **依赖数组里尽量只放原始值（number / string / boolean）。**
>
> 对象、数组、函数的引用稳定性需要你**额外维护**，而维护它的成本通常大于把它拆开的成本。
>
> 推论：**能移进 effect 内部的东西，就移进去。移进去它就不是依赖了。**

**函数依赖的同款问题**：

```tsx
// ❌
function load() { fetch(`/api/questions/${id}`).then(...); }
useEffect(() => { load(); }, [load]);      // load 每次渲染都是新的

// ✅ 移进去
useEffect(() => {
  fetch(`/api/questions/${id}`).then(...);
}, [id]);

// ✅ 或者 useCallback（当 load 还要传给子组件时）
const load = useCallback(() => { ... }, [id]);
useEffect(() => { load(); }, [load]);
```

### 4.4 `exhaustive-deps`：这条规则几乎总是对的

```js
// eslint.config.js
"react-hooks/exhaustive-deps": "warn",
```

**它报的两类警告**：

```
① 'filter' is missing from the dependency array.
   → 你漏了一个依赖，effect 可能读到旧值

② The 'params' object makes the dependencies change on every render.
   → 你的依赖不稳定，effect 会一直跑
```

**封面级素材，本单元最重要的判据**：

> **`exhaustive-deps` 报警时，问题几乎总在"这个依赖为什么不稳定"，不在"这条规则太严"。**
>
> **绝对不要用 `// eslint-disable-next-line` 去消掉它。** 那不是修 bug，那是把 bug 藏起来。

**给一个具体的对照**：

```tsx
// 错误做法：屏蔽警告
useEffect(() => {
  fetch(url).then(...);
  // eslint-disable-next-line react-hooks/exhaustive-deps
}, []);                      // ← url 变了 effect 不会重跑 → 显示旧数据

// 正确做法：把依赖加上，然后解决"为什么它不稳定"
useEffect(() => {
  fetch(url).then(...);
}, [url]);                   // ← 如果 url 每次都新建，去修那个地方
```

**但也要诚实地给出例外**：

| 例外 | 怎么处理 |
|---|---|
| 只想在挂载时执行一次（比如发一条埋点） | 这通常说明它不该是 effect；真要这么做，**写注释说明理由** |
| 依赖里有 `setState` 函数 | React 保证它引用稳定，**可以不加**（lint 也知道） |
| 想用最新的值但不想触发重跑 | 这是 `useEffectEvent` 的场景（实验性），**或者用 ref 存**（单元 9） |

> 判据（回收第 9 次课）：**宁可少几条检查，也不要有一条会误报的检查。**
>
> `exhaustive-deps` 的误报率**很低**，所以它值得保留为 warn。
> 但它的**被忽略率很高**——演示一就是活例子。
>
> **所以给一条操作纪律：`exhaustive-deps` 的 warning 数量必须是 0。** 不是"不管它"，是"必须清零"。
> 需要豁免的地方，用 `eslint-disable` **加一行理由注释**，让它变成一个可被评审的决定。

**接进 CI（第 9 次课的固定动作）**：

```yaml
- run: cd web && npx eslint . --max-warnings 0
```

> 第 9 次课那条判据：**"一个跑了但可以忽略的检查，等于没有检查。"**
>
> `--max-warnings 0` 就是把 warning 提升成 error 的开关。

### 材料

- **封面级素材**：4.1 的"引用判等三次出现"表。
- **封面级素材**：4.4 的"问题在依赖为什么不稳定"判据 + 正误对照代码。
- 高光图：4.2 的三种依赖数组。
- 高光图：4.3 的三种改法对照。
- 截图：ESLint 对演示一报出的那条完整警告文本。
- 截图：`--max-warnings 0` 下 CI 变红。
- tag `v12-deps-fixed`。

---

## 五、现场必做：竞态

**约 15 分钟。本次课最高光。**

### 5.1 准备一个可复现的环境

**先交代这是怎么做到稳定复现的，不要藏**：

```python
# app/middleware/dev_delay.py —— 仅开发环境挂载
@app.middleware("http")
async def dev_delay(request: Request, call_next):
    if settings.env == "dev" and request.url.path.startswith("/questions/"):
        qid = int(request.url.path.rsplit("/", 1)[-1])
        await asyncio.sleep(0.8 if qid % 2 == 1 else 0.05)   # 奇数慢、偶数快
    return await call_next(request)
```

> **这不是造假。真实网络里的延迟抖动就是这个效果**——不同的请求，回来的时间不一样。
>
> 我只是把"随机"换成了"可预测"，这样课堂上能稳定复现。
>
> **顺便：这也是你以后测这类 bug 的标准手法——人为制造不利时序。** 单元 5.6 会把它写成测试。

### 5.2 复现（**逐步操作，每步都停**）

页面：左边一列问题，右边详情面板。

**第 1 步**：点"问题 1"。等它加载完。

```
URL:  /questions/1
标题: 问题 1 的标题
```

正常。

**第 2 步**：点"问题 1"，**然后立刻点"问题 2"**。

**先让学生预测：最终应该显示什么？**

正确答案显然是问题 2。

**第 3 步**：操作。

```
t=0ms    点问题 1 → 发请求 A（会花 800ms）
t=100ms  点问题 2 → 发请求 B（会花 50ms）
t=150ms  响应 B 到达 → 显示"问题 2 的标题"     ✅ 看起来对了
t=800ms  响应 A 到达 → 显示"问题 1 的标题"     ❌ 被覆盖！
```

**最终画面**：

```
URL:  /questions/2
左侧: "问题 2" 高亮
右侧: 问题 1 的标题、正文、作者
```

**让这个画面停留 15 秒。**

> **URL 说 2，选中态说 2，内容说 1。**
>
> 而且：
> - **控制台没有任何报错**
> - **`tsc` 全绿**
> - **`eslint --max-warnings 0` 全绿**（依赖数组写对了）
> - **它不是每次都发生**——慢慢点就不会

### 5.3 讲清根因（**封面级素材**）

```
effect 执行 #1（id=1）
  ├─ 闭包里 id = 1
  └─ 发请求 A
        └─ .then(setQuestion)   ← 这个回调捕获的是 #1 的快照

effect 执行 #2（id=2）
  ├─ 闭包里 id = 2
  └─ 发请求 B
        └─ .then(setQuestion)   ← 这个回调捕获的是 #2 的快照

响应 B 先到 → 执行 #2 的回调 → setQuestion(问题2)
响应 A 后到 → 执行 #1 的回调 → setQuestion(问题1)   ← 谁也没拦它
```

**核心句**：

> **请求是有顺序的，响应没有。**
>
> 你发出请求 A、B，**你不能假设响应会按 A、B 的顺序回来。**
>
> 而 `.then(setQuestion)` 这个回调，**不知道自己已经过期了**。它是 #1 那次渲染的快照，它只知道"我拿到数据了，我要去设置状态"。

**再往上抽象一层**：

> 上节课的快照心智说：**每次渲染的闭包变量是独立的一份。**
>
> 今天的竞态说：**那些独立的闭包，会在不确定的时刻醒过来。**
>
> **它们醒过来的时候，不知道自己是不是最新的那一份。**
>
> 所以解决方案只能是：**给每一份闭包一个办法，让它知道自己过期了。**

### 5.4 两种修法

**修法一：过期标记（`stale` flag）**

```tsx
useEffect(() => {
  let stale = false;                        // ← 每次执行有自己的一份

  fetch(`/api/questions/${id}`)
    .then(r => r.json())
    .then(data => {
      if (!stale) setQuestion(data);        // ← 过期了就不设置
    });

  return () => { stale = true; };           // ← 清理函数：标记自己过期
}, [id]);
```

**画时间线，和 3.4 的清理函数时机对上**：

```
id=1 → effect #1：stale₁ = false，发请求 A
id=2 → 【执行 #1 的清理】stale₁ = true      ← 3.4 说的"重新执行之前"
     → effect #2：stale₂ = false，发请求 B
响应 B 到 → 检查 stale₂ = false → setQuestion ✅
响应 A 到 → 检查 stale₁ = true  → 跳过      ✅
```

> **关键在于 `stale` 是 effect 内部的局部变量，每次执行都有自己的一份。**
>
> 这不是巧合——**这正是闭包的正确用法**。上节课闭包是坑，今天闭包是解药。**同一个机制，看你用它做什么。**

**修法二：AbortController（更好）**

```tsx
useEffect(() => {
  const ac = new AbortController();

  fetch(`/api/questions/${id}`, { signal: ac.signal })
    .then(r => r.json())
    .then(setQuestion)
    .catch(e => {
      if (e.name !== "AbortError") setError(e);    // ← 必须过滤掉取消
    });

  return () => ac.abort();
}, [id]);
```

**两者的区别（醒目页）**：

| | 过期标记 | AbortController |
|---|---|---|
| 旧请求还在跑吗 | **还在跑**，只是结果不用 | **真的取消了** |
| 省带宽 | ❌ | ✅ |
| 省后端资源 | ❌ | ✅（连接断开，后端可感知） |
| 额外负担 | 无 | **必须过滤 `AbortError`**，忘了就会显示假错误 |
| 兼容性 | 任何异步都能用 | 需要底层支持 `signal` |

> **判据：能 abort 就 abort。** 尤其是搜索框这种"每个字符发一次请求"的场景，不取消就是在浪费。
>
> 但**必须记得过滤 `AbortError`**——不过滤的话，每次切换都会闪一个"加载失败"。
>
> 这是一个典型的"**修了一个 bug，引入一个新 bug**"的陷阱。作业里会要求你验证这一点。

### 5.5 顺手补完状态机

**回收第 8 次课的四态，这次加上"过期"的概念**：

```tsx
type Async<T> =
  | { kind: "idle" }
  | { kind: "loading" }
  | { kind: "error"; message: string; requestId?: string }
  | { kind: "success"; data: T };

export function QuestionDetail({ id }: { id: number }) {
  const [state, setState] = useState<Async<QuestionOut>>({ kind: "idle" });

  useEffect(() => {
    const ac = new AbortController();
    setState({ kind: "loading" });

    client.GET("/questions/{qid}", {
      params: { path: { qid: id } },
      signal: ac.signal,
    })
      .then(({ data, error, response }) => {
        if (error) {
          setState({
            kind: "error",
            message: error.message,
            requestId: response.headers.get("X-Request-Id") ?? undefined,
          });
        } else {
          setState({ kind: "success", data: data! });
        }
      })
      .catch(e => {
        if (e.name === "AbortError") return;        // ← 被取消，什么都不做
        setState({ kind: "error", message: "网络错误" });
      });

    return () => ac.abort();
  }, [id]);

  switch (state.kind) {
    case "idle":
    case "loading": return <Skeleton />;
    case "error":   return <ErrorBox message={state.message} requestId={state.requestId} />;
    case "success": return <Article q={state.data} />;
  }
}
```

**要点三条**：

| 要点 | 回收自 |
|---|---|
| 可辨识联合：**漏处理一个分支就编译报错** | 第 8 次课、第 11 次课 |
| `X-Request-Id` 展示给用户，便于报障 | 第 4 次课 |
| `client.GET` 用生成的类型，路径和参数都有检查 | 第 8 次课 |

> 注意一件事：**这段代码已经 30 行了，而它只做了"拉一条数据"这一件事。**
>
> **记住这个长度。单元 8 会回到它。**

### 5.6 把它变成测试（**方法论最重要的一段**）

**先讲清这类 bug 的特殊性（封面级素材）**：

> **前面九节课，我们所有的检查手段都建立在同一个前提上：**
>
> **同样的输入，产生同样的输出。**
>
> - 类型检查：同样的代码，同样的类型错误
> - 测试：同样的输入，同样的断言结果
> - CI：同样的提交，同样的红绿
>
> **竞态打破了这个前提。** 同样的代码、同样的操作，**这次对、下次错**，取决于两个响应谁先到。
>
> 于是：
>
> | 手段 | 对竞态有效吗 |
> |---|---|
> | `tsc` | ❌ 类型完全正确 |
> | ESLint | ❌ 依赖数组写对了 |
> | 普通测试 | ❌ **测试里的时序是确定的，而且通常是顺序的** |
> | 手工测试 | ❌ **本地 localhost 几乎没有延迟** |
> | 线上监控 | ⚠️ 用户会报"有时候显示错的"，**但你复现不了** |

**三条对策（醒目页）**：

> **① 结构上消除，不要指望测出来。**
>
> 清理函数、abort、或者用一个天生处理了这件事的库（单元 8）。
> **这是主要手段。**
>
> **② 人为制造不利时序来验证。**
>
> 我们刚才那个 dev 延迟中间件就是这个思路。在测试里对应的是控制 mock 的返回时机。
>
> **③ 把"检查"降级为"验证"。**
>
> 这条测试不是用来"发现竞态"的——它是用来**确认你的修复真的有效**，以及**防止以后有人改回去**。

**测试怎么写**：

```tsx
// tests/race.test.tsx
test("慢的旧响应不会覆盖新内容", async () => {
  const resolvers: Record<number, (v: any) => void> = {};
  vi.spyOn(globalThis, "fetch").mockImplementation((url: any) => {
    const id = Number(String(url).match(/questions\/(\d+)/)![1]);
    return new Promise(res => {                       // ← 手工控制何时 resolve
      resolvers[id] = () => res(jsonResponse({ id, title: `问题 ${id}` }));
    }) as any;
  });

  const { rerender } = render(<QuestionDetail id={1} />);
  rerender(<QuestionDetail id={2} />);                // 切到 2

  resolvers[2]();                                     // 2 先回来
  await screen.findByText("问题 2");

  resolvers[1]();                                     // 1 后回来（迟到的旧响应）
  await new Promise(r => setTimeout(r, 20));

  expect(screen.getByRole("heading")).toHaveTextContent("问题 2");   // ← 关键断言
});
```

**红-绿两步（第 9 次课的方法论）**：

```
# 去掉 return () => ac.abort()
AssertionError: expected "问题 1" to contain "问题 2"
```

```
# 加回来
✓ 慢的旧响应不会覆盖新内容
```

**最后给出判据**：

> 注意这条测试的断言形式：**"迟到的响应到达之后，内容仍然是新的。"**
>
> 它断言的是一个**性质**，不是一个数值或时刻。
>
> **回收第 9 次课、第 11 次课：断言性质，不断言数值。** 这是第三次用同一条判据。
>
> | 层 | 断言的性质 |
> |---|---|
> | 数据库 | SQL 条数不随 page size 变化 |
> | 渲染 | 渲染次数不随列表长度变化 |
> | **异步** | **旧响应到达后，内容不变** |

### 材料

- **录屏（本次课最关键的素材）**：点问题 1 → 立刻点问题 2 → **在 t=150ms 暂停 3 秒**（此时显示正确，让观众以为没事）→ 继续 → t=800ms 跳回问题 1。**一镜到底。**
- **截图（杀手级）**：最终状态下，**URL 栏 `/questions/2` + 左侧"问题 2"高亮 + 右侧"问题 1 的标题"** 同屏。
- **封面级素材**：5.3 的两个 effect 执行的闭包示意图。
- **封面级素材**：5.3 的"请求是有顺序的，响应没有"。
- **封面级素材**：5.4 的过期标记时间线图。
- **封面级素材**：5.6 的"竞态打破了'同样输入同样输出'"五行表。
- **封面级素材**：5.6 的三条对策。
- 高光图：5.4 的两种修法对照表。
- 高光图：5.6 的"三层断言性质"表。
- 截图：竞态测试的红 / 绿两态。
- 截图：忘记过滤 `AbortError` 时，切换问题闪出"加载失败"（**这张图很有说服力**）。
- tag `v12-race-fixed`。

---

## 六、CORS：把第 8、10 次课的账还上

**约 15 分钟。**

### 6.1 先制造现场

**把第 8 次课那个 proxy 删掉**：

```diff
// vite.config.ts
  export default defineConfig({
-   server: {
-     proxy: { "/api": { target: "http://localhost:8000", rewrite: p => p.replace(/^\/api/, "") } }
-   }
  });
```

```diff
- const BASE = "/api";
+ const BASE = "http://localhost:8000";
```

刷新页面：

```
Access to fetch at 'http://localhost:8000/questions' from origin
'http://localhost:5173' has been blocked by CORS policy:
No 'Access-Control-Allow-Origin' header is present on the requested resource.
```

> 这个报错每个前端都见过。**大部分人的反应是去搜一段配置粘上去。**
>
> 今天我们先搞清楚发生了什么。

### 6.2 关键一刻：后端日志里有 200

**切到后端终端**：

```
INFO:  127.0.0.1:52134 - "GET /questions?page=1 HTTP/1.1" 200 OK
```

**停下来，让这一行停留 10 秒。**

> **请求到了。后端处理了。查了数据库。返回了 200 和完整的 JSON。**
>
> **是浏览器把响应扣下了，没交给你的 JavaScript。**

**再用 curl 实证一次**：

```bash
curl -i http://localhost:8000/questions
```

```
HTTP/1.1 200 OK
content-type: application/json
{"items": [...]}
```

> **curl 拿得到。浏览器拿不到。**
>
> 区别不在服务器，**在客户端**。

**封面级素材**：

> **同源策略是浏览器的规则，不是服务器的规则。**
>
> **它限制的是"你的 JS 能不能读到响应"，不是"请求能不能发出去"。**

**为什么浏览器要管这件事**：

```
你登录了 bank.com，浏览器存了 cookie

你打开了 evil.com，它的 JS 执行：
    fetch("https://bank.com/api/balance")       ← 浏览器会自动带上 bank.com 的 cookie！

如果没有同源策略：
    evil.com 的 JS 就能读到你的余额
```

> **同源策略保护的是"用户浏览器里的凭证"。**
>
> 它假设的威胁模型是：**你访问了一个恶意网站，而你的浏览器里有其他网站的登录态。**

**埋一个第 15 次课的点（重要）**：

> 请注意一个细节：**请求还是发出去了。**
>
> 也就是说，如果那个请求本身就有副作用（比如 `POST /transfer?to=attacker&amount=1000`），**同源策略拦不住它**——它只拦住了"读响应"。
>
> **这就是 CSRF 存在的原因。→ 第 15 次课。**

### 6.3 同源的定义，和预检

**同源 = 协议 + 主机 + 端口，三者全同**：

```
http://localhost:5173  →  http://localhost:8000     ❌ 端口不同
https://a.com          →  http://a.com              ❌ 协议不同
https://a.com          →  https://api.a.com         ❌ 主机不同
https://a.com/x        →  https://a.com/y           ✅ 路径不算
```

**然后是预检。现场演示**：

配好 CORS 之后，看 Network 面板发一个 POST：

```
OPTIONS  /questions      204    ← 多出来一条！
POST     /questions      201
```

**醒目页**：

> **什么请求不需要预检（"简单请求"）：**
>
> - 方法是 `GET` / `HEAD` / `POST`
> - **`Content-Type` 只能是** `application/x-www-form-urlencoded`、`multipart/form-data`、`text/plain`
> - 没有自定义请求头
>
> **注意第二条：`application/json` 不在列表里。**
>
> **所以我们所有的 JSON POST / PATCH / DELETE，全部都要预检。**

**预检的内容**：

```http
OPTIONS /questions HTTP/1.1
Origin: http://localhost:5173
Access-Control-Request-Method: POST
Access-Control-Request-Headers: content-type

HTTP/1.1 204 No Content
Access-Control-Allow-Origin: http://localhost:5173
Access-Control-Allow-Methods: GET, POST, PATCH, DELETE
Access-Control-Allow-Headers: content-type
Access-Control-Max-Age: 600
```

> **判据：预检是一次真实的额外往返。**
>
> 跨域的写操作，**延迟是同源的两倍**。
>
> `Access-Control-Max-Age` 能缓存预检结果（浏览器有自己的上限），**但它只对相同的 method + headers 组合有效**。

### 6.4 配置，以及两个必踩的坑

```python
# app/main.py
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,          # ["http://localhost:5173"]
    allow_credentials=True,
    allow_methods=["GET", "POST", "PATCH", "DELETE"],
    allow_headers=["Content-Type", "Authorization"],
    expose_headers=["X-Request-Id"],              # ← 坑二
    max_age=600,
)
```

**坑一：`allow_origins=["*"]` 和 `allow_credentials=True` 不能共存**

```
The value of the 'Access-Control-Allow-Origin' header in the response must not be
the wildcard '*' when the request's credentials mode is 'include'.
```

> 浏览器直接拒绝。**这是规范强制的**，不是实现差异。
>
> 理由很好理解：`*` 的意思是"任何网站都能读我的响应"，而 credentials 的意思是"请带上用户的登录态"。**两者同时成立 = 任何网站都能用用户的身份读你的数据。**
>
> **判据：生产环境的 `allow_origins` 必须是明确的白名单。** 写 `*` 只在"完全公开、无认证的 API"上才成立。

**坑二：默认情况下 JS 读不到自定义响应头（回收第 4 次课）**

```tsx
response.headers.get("X-Request-Id")     // → null ！
```

> 跨域时，**浏览器默认只让 JS 读到 7 个"安全"响应头**：
> `Cache-Control`、`Content-Language`、`Content-Length`、`Content-Type`、`Expires`、`Last-Modified`、`Pragma`。
>
> 第 4 次课我们精心设计的 `X-Request-Id`——**在跨域下前端读不到。**
>
> 必须显式声明：
>
> ```python
> expose_headers=["X-Request-Id"]
> ```
>
> **这个坑非常常见，而且它的症状是"没有症状"**——`get()` 返回 `null`，代码不报错，只是报障页面上少了一个 ID。
>
> **回收第 5 次课的判据：静默失败比响亮失败更危险。**

**加一条检查（第 9 次课的固定动作）**：

```python
# tests/test_conventions.py
def test_request_id_is_exposed_cross_origin(client):
    res = client.get("/questions", headers={"Origin": "http://localhost:5173"})
    exposed = res.headers.get("access-control-expose-headers", "")
    assert "X-Request-Id" in exposed, "跨域下前端读不到 request id"
```

### 6.5 生产的三种拓扑（**本单元最重要的判据**）

**封面级素材**：

| 方案 | 怎么做 | 有跨域吗 | 优点 | 缺点 |
|---|---|---|---|---|
| **① 同源部署** | 反向代理：`/` → 前端静态文件，`/api` → 后端 | **没有** | **无预检；cookie 天然可用；配置最少** | 需要一个反代（nginx / Caddy / 云服务） |
| ② CORS | 后端配 CORSMiddleware | 有 | 前后端可以部署到完全不同的域 | **每个写操作多一次往返**；配置容易出错 |
| ③ BFF | 前端有自己的服务端，它去调真 API | 前端侧没有 | 可以藏密钥（回收第 10 次课） | 多一层，多一套运维 |

```nginx
# 方案①：一个 nginx 配置就够了
server {
    listen 80;
    location /api/ { proxy_pass http://backend:8000/; }
    location /     { root /usr/share/nginx/html; try_files $uri /index.html; }
}
```

**判据（醒目页）**：

> **能同源就同源。**
>
> 跨域是要付代价的（预检往返、配置复杂度、credentials 的各种规则），**而这个代价没有换来任何功能。**
>
> 除非你有明确的理由必须分开部署（比如 API 要给多个不同的站点用），否则同源部署是默认答案。

**然后是一条更重要的判据**：

> 再看一眼方案①的 nginx 配置，和第 8 次课那个 Vite proxy：
>
> ```ts
> proxy: { "/api": { target: "http://localhost:8000" } }
> ```
>
> **它们是同一件事。**
>
> **dev 用 proxy，就是在模拟同源部署。**
>
> 于是有两个推论：
>
> | 你的生产拓扑 | 那 dev 应该 |
> |---|---|
> | **同源部署** | 用 proxy ✅ **dev 和 prod 行为一致** |
> | **CORS** | **也应该关掉 proxy、用 CORS** ⚠️ |
>
> 第二行要强调：**如果生产用 CORS，而 dev 用 proxy，那 proxy 就在掩盖问题。** 所有的 CORS 坑（预检、credentials、expose_headers）你都会在**上线当天第一次遇到**。
>
> **判据：开发环境的网络拓扑，应该和生产一致。** 任何"只在开发期有效"的便利，都是在推迟问题，不是在解决问题。
>
> 〔第 10 次课讲 `vite preview` 时给过一条同构的判据："提交前至少跑一次 preview，它跑的是真正要上线的产物。"**今天是网络层的版本。**〕

### 6.6 认证相关的部分，今天只点到

> 你会看到很多关于 CORS + cookie 的配置：`credentials: "include"`、`SameSite`、`Secure`……
>
> **这些属于认证方案，第 14 次课讲。**
>
> 今天只要知道一件事：**`allow_credentials=True` 打开了"请求可以带上 cookie"这个开关，而这个开关一旦打开，`allow_origins` 就绝对不能是 `*`。**

### 材料

- **封面级素材**：6.2 的"同源策略是浏览器的规则" + **浏览器红色报错与后端 200 日志并排截图**（本单元最关键的一张）。
- **封面级素材**：6.3 的"简单请求条件" + `application/json` 触发预检那一行标红。
- **封面级素材**：6.5 的三种拓扑表。
- **封面级素材**：6.5 的"dev 的 proxy 就是在模拟同源部署" + 两个推论表。
- 高光图：同源定义四行示例。
- 高光图：预检请求/响应报文全文。
- 高光图：6.4 的两个坑。
- 截图：Network 面板里 OPTIONS + POST 两条记录。
- 截图：`curl` 能拿到而浏览器拿不到（**两个终端并排**）。
- 截图：`allow_origins=["*"]` + credentials 的浏览器报错。
- 截图：没配 `expose_headers` 时 `headers.get("X-Request-Id")` 返回 `null`。
- `nginx.conf` + `docker-compose.yml`（作业二要用）。
- tag `v12-cors`。

---

## 七、路由：URL 是状态的一部分

**约 8 分钟。B 档，时间紧只保留 7.1 和 7.3。**

### 7.1 一条判据先行

**封面级素材**：

> **能放进 URL 的状态，就放进 URL。**

为什么：

| 放进 URL 的好处 | 说明 |
|---|---|
| **可分享** | 复制链接发给同事，他看到的是同一个页面 |
| **可刷新** | F5 之后状态还在 |
| **可后退** | 浏览器的后退按钮就是历史记录 |
| **可收藏** | — |
| **可被搜索引擎索引** | 如果做了 SSR |

**什么该放、什么不该放**：

| 该放 URL | 不该放 |
|---|---|
| 当前在哪个页面 | 弹窗开着没开 |
| 详情页的 id | 表单草稿 |
| **分页的 page / size** | 鼠标悬停在哪 |
| **排序、筛选条件** | 动画进度 |
| 搜索关键词 | 输入框里还没提交的内容 |

> 判据的反面：**如果一个状态"刷新后丢掉也无所谓"，它就不该在 URL 里。**

### 7.2 最小集

```tsx
// src/main.tsx
<BrowserRouter>
  <Routes>
    <Route path="/" element={<Layout />}>
      <Route index element={<QuestionList />} />
      <Route path="questions/:qid" element={<QuestionDetail />} />
      <Route path="*" element={<NotFound />} />
    </Route>
  </Routes>
</BrowserRouter>
```

```tsx
// 路径参数
const { qid } = useParams();          // string | undefined
const id = Number(qid);
if (!Number.isInteger(id) || id <= 0) return <NotFound />;   // ← 入口闸门
```

> **注意 `useParams` 返回的是 `string | undefined`，不是 `number`。**
>
> 路径参数来自 URL，**URL 里可以是任何东西**——用户能手输 `/questions/abc`。
>
> **回收第 3 次课的入口闸门 + 第 9 次课那个 `qid: int = Path(gt=0)`：** 不可信的输入，在最外层就要收窄。
>
> 前端和后端**各自都要做这件事**，理由和第 11 次课单元 7.3 一样：**前端是体验，后端是安全。**

### 7.3 用 `useSearchParams` 替代 `useState`（**本单元核心操作**）

**回收第 7 次课的分页参数**：

```diff
- const [page, setPage] = useState(1);
- const [sort, setSort] = useState<"latest" | "views">("latest");
+ const [sp, setSp] = useSearchParams();
+ const page = Number(sp.get("page") ?? 1);
+ const sort = (sp.get("sort") ?? "latest") as Sort;
+
+ function go(next: Partial<{ page: number; sort: Sort }>) {
+   setSp(prev => {
+     const n = new URLSearchParams(prev);
+     Object.entries(next).forEach(([k, v]) => n.set(k, String(v)));
+     return n;
+   });
+ }
```

**现场演示效果**：

1. 点"按浏览量排序"，翻到第 3 页
2. **URL 变成 `/?page=3&sort=views`**
3. 复制 URL，新开一个标签粘贴 → **完全一样的页面**
4. 点后退 → 回到第 2 页

> **一行 `useState` 换成 `useSearchParams`，白送了分享、刷新、后退三个能力。**

**但要指出一个真实的代价**：

> `sort` 从 URL 里读出来是 `string`，我们用 `as Sort` 断言了——**这是一个第 10 次课明令禁止的 `as`。**
>
> 诚实的做法是校验：
>
> ```tsx
> const SORTS = ["latest", "oldest", "views"] as const;
> const raw = sp.get("sort");
> const sort: Sort = SORTS.includes(raw as any) ? (raw as Sort) : "latest";
> ```
>
> **回收第 7 次课的排序白名单：** 后端用 `Literal` 做了白名单，前端这里是同一道闸门的前移。
>
> **判据：从 URL 读出来的任何东西，都要当成用户输入对待。**

### 7.4 路由级代码拆分（回收第 10 次课）

```tsx
const QuestionDetail = lazy(() => import("./pages/QuestionDetail"));

<Suspense fallback={<Skeleton />}>
  <Routes>...</Routes>
</Suspense>
```

> 第 10 次课单元 8.2 做过一次动态 `import()`。**按路由拆分是它最标准的用法**——列表页的用户不需要下载详情页的代码。

**记一笔欠账**：

> 一个必踩的坑：**部署之后，直接访问 `/questions/5` 会 404。**
>
> 因为服务器上根本没有 `/questions/5` 这个文件——路由是前端 JS 在跑的。
>
> 解法是让服务器把所有未知路径都返回 `index.html`（6.5 那个 nginx 配置里的 `try_files $uri /index.html` 就是干这个的）。
>
> **→ 第 16 次课正式处理。** 今天记账。

### 材料

- **封面级素材**：7.1 的"能放 URL 就放 URL" + 该放/不该放两列表。
- 高光图：7.3 的 `useState` → `useSearchParams` diff。
- 高光图：7.3 的排序白名单校验（标注"第 7 次课的前移"）。
- 录屏：改排序 → URL 变化 → 复制到新标签 → 同样的页面 → 后退。
- 截图：直接访问 `/questions/5` 在 `vite preview` 下 404（**为第 16 次课埋点**）。

---

## 八、服务端状态：为什么你需要一个库

**约 13 分钟。**

### 8.1 先把痛点摆出来

> 回到单元 5.5 那段代码。**30 行，只为了拉一条数据。**
>
> 现在数一数，我们的项目里有几个地方要这么写：

```
列表页        30 行
详情页        30 行
标签列表      30 行
用户信息      30 行
统计数字      30 行
```

**然后问五个问题（醒目页）**：

| 问题 | 现在的答案 |
|---|---|
| 两个组件要同一份数据，会发几次请求？ | **两次** |
| 从详情页返回列表，列表要重新拉吗？ | **要，全部重拉** |
| 发了 POST 创建问题后，列表怎么更新？ | **手动再拉一次**（而且要记得） |
| 请求失败了要重试吗？ | **没有** |
| 用户切到别的标签页十分钟回来，数据还新鲜吗？ | **不知道，也不会刷新** |

> 这五个问题，**每一个都要你写代码去解决**。而且每个组件都要写一遍。
>
> **你已经在写一个缓存层了，只是你还没意识到。**

### 8.2 服务端状态不是客户端状态（**本单元核心**）

**封面级素材**：

| | 客户端状态 | **服务端状态** |
|---|---|---|
| 谁拥有它 | **你** | **服务器** |
| 它会过期吗 | 不会 | **会** |
| 别人会改它吗 | 不会 | **会**（其他用户、后台任务） |
| 需要同步吗 | 不需要 | **需要** |
| 丢了会怎样 | 用户体验受损 | **重新拉一次就行** |
| 例子 | 弹窗开关、表单草稿、选中项 | 问题列表、用户资料、统计数字 |

> **`useState` 是为客户端状态设计的。**
>
> 它的模型是："这个值归我管，我改它，没人会在背后改它。"
>
> **服务端状态完全不满足这个假设。** 它是一份**远端数据的本地副本**——也就是说，**它是缓存**。
>
> 而缓存有自己的一整套问题：**什么时候失效、怎么去重、过期了怎么办、多处使用怎么共享。**

**回收第 2 次课**：

> 第 2 次课讲 HTTP 缓存时，我们讨论过 `Cache-Control` 和 `ETag`——**那是浏览器在帮你管一层缓存。**
>
> 今天这一层是**在你的 JS 里**。同样的问题，换了一个地方。
>
> **判据：只要你在本地存了一份远端数据，你就在做缓存，就要回答缓存的那几个问题。** 区别只是你自己写，还是用一个库。

### 8.3 `queryKey`：key 的第三次出现（**本次课最漂亮的一页**）

```tsx
const { data, isPending, error } = useQuery({
  queryKey: ["questions", { page, sort }],          // ← 这是什么
  queryFn: ({ signal }) =>
    client.GET("/questions", { params: { query: { page, sort } }, signal }),
});
```

**封面级素材**：

| 层 | 要回答的问题 | 答案叫什么 | 哪次课 |
|---|---|---|---|
| **数据库** | 这两行是不是同一条记录 | **主键** | 第 6 次课 |
| **UI 树** | 这两次渲染里是不是同一个组件实例 | **`key`** | 第 11 次课 |
| **缓存** | **这两次请求要不要的是同一份数据** | **`queryKey`** | **今天** |

> **三层、三个技术栈、同一个问题：如何唯一标识一个东西。**
>
> 而且三者的错误模式也一样：
>
> | | 标识错了会怎样 |
> |---|---|
> | 数据库主键 | 更新错了行 |
> | React key | **组件 state 串到别的数据上**（第 11 次课那个错位） |
> | queryKey | **缓存串了**：换了筛选条件，显示的还是旧筛选的结果 |

**具体讲 `queryKey` 的作用**：

```tsx
queryKey: ["questions", { page: 1, sort: "latest" }]
queryKey: ["questions", { page: 2, sort: "latest" }]     // 不同的 key → 不同的缓存条目
queryKey: ["questions", { page: 1, sort: "views" }]      // 不同的 key
```

> React Query 做的事：
>
> | 场景 | 它的行为 |
> |---|---|
> | 两个组件用同一个 key | **只发一次请求**，两个组件共享结果 |
> | 参数变了（key 变了） | 自动发新请求，**旧的自动作废**（竞态自动解决） |
> | 返回上一页（key 命中缓存） | **立刻显示缓存**，同时后台悄悄刷新 |
> | 请求失败 | 按策略自动重试 |
> | 窗口重新获得焦点 | 自动刷新（可配置） |

**关键一句**：

> **注意第二行：竞态问题在这里自动消失了。**
>
> 因为 React Query 知道"当前应该显示的是哪个 key 的数据"，**过期的响应回来时，它对应的 key 已经不是当前 key 了，直接丢弃。**
>
> 这就是单元 5 那个 `stale` 标记做的事——**只是它替你做了，而且做得更彻底**（它还会缓存那份数据，万一你切回去就能立刻显示）。
>
> 这是评价"要不要上库"时最重要的一条：**它是不是替你解决了一类你解决不干净的问题。**

### 8.4 写操作与失效

```tsx
const qc = useQueryClient();

const { mutate, isPending } = useMutation({
  mutationFn: (body: QuestionCreate) => client.POST("/questions", { body }),
  onSuccess: () => {
    qc.invalidateQueries({ queryKey: ["questions"] });    // ← 让列表失效
  },
});
```

> `invalidateQueries({ queryKey: ["questions"] })` 的意思是：**所有以 `"questions"` 开头的缓存条目全部标记为过期，正在显示的那些立刻重新拉取。**
>
> 对比之前的做法：POST 成功后手动调一次 `loadList()`——**而且你得记得每个改动了问题的地方都调一次。**
>
> **判据：这又是"把依赖人记得的规则换成机制"的一个实例。** 失效规则写在 mutation 定义里，而不是散落在每个调用点。

**顺手回收第 3 次课**：

> 注意 mutation 里没有做任何"防重复提交"的事。
>
> **回收第 11 次课单元 7.4：`disabled` 是体验，后端的唯一约束才是保证。**
>
> React Query 的 `isPending` 能让你禁用按钮，**但它同样防不住刷新后重复提交。** 那件事必须在后端（第 6 次课的唯一约束已经做了）。

### 8.5 什么时候该上库（**必须给判据，否则学生会到处装库**）

**封面级素材**：

> **判据：当你第三次实现同一个机制时，考虑上库。**

| 你的情况 | 建议 |
|---|---|
| 一两个页面，各拉一次数据，不需要共享 | **手写就好**，单元 5.5 那 30 行够用 |
| 多个组件用同一份数据 / 需要缓存 / 写完要刷新列表 | **上库** |
| 团队里没人了解这个库 | 先评估学习成本 |
| 只是"别人都在用" | ❌ **不是理由** |

**然后给一个诚实的代价清单**：

| 代价 | 说明 |
|---|---|
| 包体积 | gzip 十几 kB（**回收第 10 次课：装之前先量**） |
| 心智负担 | 要理解 `staleTime` / `gcTime` / 失效策略 |
| 调试变难 | 多一层抽象，出问题要先判断是你的问题还是库的问题 |
| **你必须能说清它替你做了什么** | 见下 |

**最后一条要强调**：

> **判据：引入一个库之前，你必须能说出"如果不用它，我要自己写哪些东西"。**
>
> 如果你说不出来，说明你还没遇到它解决的问题——**那就是过度工程。**
>
> 这也是本课程一贯的做法：**先手写，感受痛，再引库。** 单元 5.5 那 30 行不是白写的，它是你评估这个库的基准线。

### 8.6 一个仍然属于你的决定

```tsx
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 30_000,          // 30 秒内认为数据是新鲜的，不重新拉
      retry: 1,
      refetchOnWindowFocus: false,
    },
  },
});
```

> `staleTime` 设多少？**库不会替你决定，因为这是业务问题。**
>
> | 数据 | 合理的 staleTime |
> |---|---|
> | 用户自己的资料 | 长（几分钟） |
> | 问题列表 | 短（几十秒） |
> | 实时统计 / 库存 | **接近 0，或者根本不该缓存** |
>
> **回收第 2 次课那条判据：** 当时讲 HTTP 缓存，结论是"'缓存多久'这个问题问错了，正确的问题是'这个 URL 会不会指向不同的内容'"。
>
> 第 10 次课用 hash 指纹消掉了那个两难（内容变 → URL 变 → 可以缓存一年）。
>
> **但服务端数据做不到这一点**——`/questions?page=1` 这个 URL 的内容**随时会变**，而你没办法在文件名里放 hash。
>
> **所以这里只能是一个业务判断：这份数据陈旧多久是可以接受的。** 没有技术方案能替你回答。

### 材料

- **封面级素材**：8.1 的五个问题表。
- **封面级素材**：8.2 的"客户端状态 vs 服务端状态"六行表。
- **封面级素材**：8.3 的"key 的三次出现"表（**三行三色，对应三次课**）。
- **封面级素材**：8.5 的"第三次实现同一个机制时上库" + 代价清单。
- 高光图：8.3 的 React Query 五种行为表。
- 高光图：8.6 的 staleTime 业务判断表。
- 截图：两个组件用同一 queryKey，Network 里只有一条请求。
- 截图：单元 5 那个竞态操作，在 React Query 下**不再出错**（**很有说服力**）。
- 截图：对比——手写版 30 行 vs `useQuery` 版 5 行（**并排，同样的功能**）。
- tag `v12-query`。

---

## 九、C 档结论卡

**约 3 分钟。时间不够整体跳过。**

### 9.1 本次课没讲的

| 主题 | 一句话 | 何时学 |
|---|---|---|
| `useRef` | 存"跨渲染保持、改了不触发渲染"的值。**常用于存最新的回调，绕开依赖数组** | 自读 |
| `useLayoutEffect` | 在浏览器绘制**之前**同步执行。**只在需要测量 DOM 并立刻调整时用** | 自读 |
| `useSyncExternalStore` | 订阅外部数据源的官方方式，**状态管理库的底层** | 自读 |
| 乐观更新 | 先改 UI，失败再回滚。**体验好，但要处理回滚** | 自读 |
| 无限滚动 / 分页游标 | `useInfiniteQuery`；配合第 7 次课的 keyset 分页 | 自读 |
| Suspense for Data | React 的数据获取新模型。**还在演进，不急** | — |
| SSR / RSC | 改变"在哪渲染"，本次课的心智仍适用 | — |
| WebSocket / SSE | 服务端推送。**它让"数据会过期"这个问题变简单了** | 自读 |

### 9.2 一句话结论卡

| 问题 | 结论 |
|---|---|
| React Query / SWR / RTK Query 选哪个 | 功能重叠度很高。**选团队熟的那个**；新项目 React Query 生态最全 |
| 还需要 Redux 吗 | 如果服务端状态交给 Query，剩下的客户端状态通常少到用 `useState` + context 就够 |
| `fetch` vs `axios` | `fetch` 是标准、零依赖；`axios` 的拦截器和错误处理更顺手。**我们用生成的 `openapi-fetch`，两者都不用直接写** |
| 请求要不要统一封装 | 要。**至少统一：base URL、错误结构解析、request id 提取**。第 8 次课的 `client.ts` 就是 |
| 全局 loading 指示器 | React Query 的 `useIsFetching()` 一行搞定 |
| 错误边界（Error Boundary） | 它抓的是**渲染期抛出的错误**，抓不到异步回调里的。**两者要分别处理** |
| 轮询 vs WebSocket | 轮询简单但浪费；**先用轮询，量上来了再换** |
| 离线与重试 | React Query 默认在断网恢复后重试。**但写操作的重试要小心幂等性**（第 3 次课） |
| CORS 调试技巧 | **先看后端日志有没有收到请求**。有 → CORS 配置问题；没有 → 网络/URL 问题 |
| 为什么 CORS 报错信息这么难懂 | 浏览器出于安全不会把细节暴露给 JS。**详细原因只在 Console，不在 `catch` 里** |

### 9.3 跨端对照

| 能力 | Web | iOS/Android 原生 |
|---|---|---|
| 同源策略 | ✅ 有 | ❌ **没有**（所以原生 App 不需要 CORS） |
| 请求取消 | `AbortController` | `URLSessionTask.cancel()` / OkHttp `cancel()` |
| 服务端状态缓存 | React Query | Room + Repository / SwiftData |
| 竞态 | 同样存在 | **同样存在** |

> 两点值得注意：
>
> **一、CORS 是浏览器特有的。** 原生 App 调你的 API 不受任何限制——**这也说明 CORS 不是"保护 API"的机制**，它保护的是浏览器里的用户凭证。
>
> **二、竞态是跨平台的。** 任何"发出去的请求可能乱序回来"的环境都有这个问题。今天学的心智，换个平台照样用。

---

## 十、作业与欠账

**约 5 分钟。**

### 10.1 作业一：数据获取改造（主线，必交）

在 `v12-broken` 基础上，把所有数据获取改造正确。

| # | 要求 | 自检 |
|---|---|---|
| 1 | **StrictMode 开启**，且所有 effect 在双执行下行为正确 | 每个拉数据的页面，Network 里应恰好两条（StrictMode 的正常表现），且无重复副作用 |
| 2 | 所有 effect 该有清理的都有 | 切页面后无残留定时器/请求 |
| 3 | `eslint --max-warnings 0` 通过；**任何 `eslint-disable` 必须附理由注释** | CI |
| 4 | 依赖数组**只含原始值**（有例外须说明） | grep |
| 5 | 所有数据获取用**四态可辨识联合**，错误态展示 `X-Request-Id` | 截图 |
| 6 | **竞态已消除**，且 `AbortError` 被正确过滤 | 见第 7 条 |
| 7 | 交一段录屏：快速切换详情页 10 次，**内容始终与 URL 一致，且不闪错误提示** | 录屏 |
| 8 | 派生数据一律在渲染时计算，**不用 effect + state** | grep `setTotal` 之类 |
| 9 | 分页/排序/筛选全部迁到 `useSearchParams`，**从 URL 读出的值做白名单校验** | 见第 10 条 |
| 10 | 交一段录屏：改筛选 → 复制 URL → 新标签打开 → 同样的页面 → 后退正确 | 录屏 |

**`decisions.md` 新增两条**：
- 你的 `AbortController` 用在哪些请求上？**有没有哪个请求你决定不取消？为什么？**
- 有哪些状态你**决定不放进 URL**？依据是什么？

### 10.2 作业二：三种网络拓扑对照实验（必交）

**这是本次课最能建立直觉的作业，必须实际跑三遍。**

搭三套环境，各测一次，填表：

| 拓扑 | 怎么搭 |
|---|---|
| **A. dev proxy** | 当前的 `vite.config.ts` proxy |
| **B. 跨域 + CORS** | 删掉 proxy，前端直连 `http://localhost:8000`，后端配 CORSMiddleware |
| **C. 同源部署** | `docker compose`：nginx 伺服 `dist/` + 反代 `/api` 到后端 |

**测量表（每一格都要有证据截图）**：

| 测量项 | A | B | C |
|---|---|---|---|
| GET 列表：Network 里几条请求 | | | |
| POST 创建：Network 里几条请求 | | | |
| 有没有 `OPTIONS` 预检 | | | |
| 前端能读到 `X-Request-Id` 吗 | | | |
| POST 的总耗时（Network 面板） | | | |
| 直接访问 `/questions/5` 并刷新 | | | |

**必答四问**：

1. B 和 C 的 POST 耗时差多少？**这个差值是什么造成的？**
2. 在 B 下，**去掉 `expose_headers` 配置**，`X-Request-Id` 会怎样？截图证明。**这个失败是响亮的还是静默的？**
3. C 拓扑下你做了什么配置才让"刷新 `/questions/5` 不 404"？**没做这件事的话会发生什么？**（→ 记下来，第 16 次课要用）
4. 单元 6.5 说"开发环境的网络拓扑应该和生产一致"。**你的项目准备用哪个拓扑上生产？那你的 dev 应该用哪个？** 如果两者不一致，你打算怎么弥补？

### 10.3 作业三：AI 异步代码审查（**课程主题作业**）

**第一部分：拿到样本**

向 AI 提一个需求（不给任何额外约束）：

> 用 React + TypeScript 写一个带搜索框的问题列表：输入关键词实时搜索（防抖 300ms），点击某条进入详情页，详情页显示完整内容。要有加载状态。

**原样保存输出。**

**第二部分：逐条审查**

| # | 检查项 | 它的写法 | 有问题吗 | 后果 |
|---|---|---|---|---|
| 1 | 依赖数组写了吗，里面有对象/函数吗 | | | |
| 2 | 有清理函数吗 | | | |
| 3 | **有竞态保护吗**（stale flag / abort） | | | |
| 4 | 防抖的定时器清理了吗 | | | |
| 5 | 有错误态吗，还是只有二态 | | | |
| 6 | 有没有用 effect 做派生状态 | | | |
| 7 | 有没有 `setState` 之后立刻读那个 state | | | |
| 8 | 搜索关键词放了 URL 还是 `useState` | | | |

**第三部分：量化护栏的覆盖率（本作业核心）**

| 步骤 | 做什么 | 记录 |
|---|---|---|
| ① | 跑 `tsc --noEmit` | 抓到 ___ 条 |
| ② | 跑 `eslint --max-warnings 0` | 抓到 ___ 条 |
| ③ | **开启 StrictMode**，手工操作一遍 | 暴露 ___ 条 |
| ④ | **挂上课堂用的延迟中间件**，快速切换 10 次 | 暴露 ___ 条 |
| ⑤ | 统计：第二部分找出 ___ 条，工具+实验共抓住 ___ 条 | **抓住率 ___%** |

**第四部分：必答五问（评分重点）**

| # | 问题 |
|---|---|
| 1 | 第 ③ 步和第 ④ 步各暴露了几条？**这两步的成本分别是多少？** 用第 10 次课"护栏成本/收益"的框架评价它们 |
| 2 | 有哪些问题是**①②③④ 全都没抓到**的？你打算靠什么发现它们？ |
| 3 | **竞态这类 bug，和前面几次课见过的 AI 错误，最大的区别是什么？** |
| 4 | 第 11 次课把 AI 错误分成了两类：**"缺少项目信息"** 和 **"训练数据里错误写法是多数"**。**竞态属于哪一类？还是第三类？** |
| 5 | 基于第 4 问，给出一条"让 AI 写异步代码"的操作规则，**并说明为什么"把文档贴给它"不足以解决问题** |

> **第 3、4 问是本次作业的核心。**
>
> 提示一个方向——前面见过的错误，无论哪一类，都有一个共同点：**它们是确定性的**。
>
> | 错误 | 表现 |
> |---|---|
> | 猜错字段名 | **每次**都报同样的类型错误 |
> | `key={index}` | **每次**按同样步骤都能复现 |
> | 编造包名 | **每次** `npm install` 都 404 |
> | **竞态** | **这次对，下次错** |
>
> **竞态是第三类：不是"AI 不知道"，也不是"AI 在模仿多数"，而是"这个错误在 AI 的输出里和在人的输出里都不可见"。**
>
> 它在编写时不可见、在类型检查时不可见、在本地测试时不可见——**它只在真实网络条件下、在特定时序下可见。**

**封面级素材（讲作业时打出）**：

| AI 错误的三类来源 | 例子 | 对策 |
|---|---|---|
| **① 缺少项目特定信息** | 猜字段名、漏业务约束、编造包名 | **补充信息**：契约、schema、约束文档 |
| **② 训练数据里错误写法是多数** | `key={index}`、`push` 后 setState | **施加约束**：`readonly`、lint 规则、禁止清单 |
| **③ 错误本身在编写期不可见** | **竞态、漏清理、缓存失效** | **改变结构**：让错误不可能发生（abort / 库 / StrictMode） |

> 三类的应对方式完全不同：
>
> - ① 给信息 → **它就不用猜了**
> - ② 给约束 → **它猜错了会被当场拦住**
> - ③ **给再多信息和约束都没用** → 只能改变代码结构，让这类错误在结构上不可能出现
>
> **判据：面对第三类错误，"检查"这条路是走不通的，只能走"消除"。**
>
> 这就是为什么单元 8 那个库有价值——**它不是"帮你少写代码"，是"让一整类 bug 不可能发生"。**

### 10.4 本次课新增的欠账登记

| 欠账 | 何时还 |
|---|---|
| SPA 路由刷新 404（需要 `try_files`） | **第 16 次课** |
| 认证 token 怎么存、怎么带、`SameSite` | **第 14 次课** |
| 认证态在组件树里怎么传（context 的正当用法） | **第 14 次课** |
| CSRF（"请求还是发出去了"的后果） | **第 15 次课** |
| 生产环境的 `cors_origins` 怎么配、怎么随环境变 | **第 16 次课** |
| WebSocket / SSE | 课后自读 |
| 乐观更新与回滚 | 课后自读 |
| `useRef` / `useLayoutEffect` / 错误边界 | 课后自读 |
| 无限滚动（配合 keyset 分页） | 课后自读 |

---

## 十一、素材清单与制作说明

### 必需素材

| 素材 | 说明 |
|---|---|
| tag `v12-broken` | 起始版：五个问题齐备。**ESLint 必须真的报出那条 `params` 警告**，它是"警告被忽略"这个论点的证据 |
| tag `v12-deps-fixed` | 单元 4 结束 |
| tag `v12-race-fixed` | 单元 5 结束 |
| tag `v12-cors` | 单元 6 结束：CORS 配置 + nginx/compose 就绪 |
| tag `v12-router` | 单元 7 结束 |
| tag `v12-query` | 单元 8 结束 |
| tag `v12-final` | 作业参考交付 |
| `app/middleware/dev_delay.py` | **仅 dev 生效**，奇偶 id 不同延迟。课堂与作业都要用 |
| `nginx.conf` + `docker-compose.yml` | 作业二拓扑 C |
| `tests/race.test.tsx` | 含红/绿两态 |
| **封面级 A** | 单元 1.1 的快照图（**第 11 次课原图重放**）+ "发起时是快照，回来时世界已变" |
| **封面级 B** | 单元 2 的五个演示归类表 |
| **封面级 C** | 单元 3.1 的"同步不是监听" |
| **封面级 D** | 单元 3.2 的"什么该放 effect"九行表 |
| **封面级 E** | 单元 3.4 的清理函数时间线（"重新执行之前"高亮） |
| **封面级 F** | 单元 3.5 的"StrictMode 是 React 自己做的那件事" |
| **封面级 G** | 护栏累加表（新增第十、十一行，**"开发期"用新颜色**） |
| **封面级 H** | 单元 4.1 的"引用判等三次出现"表 |
| **封面级 I** | 单元 4.4 的"问题在依赖为什么不稳定" |
| **封面级 J** | 单元 5.3 的两个 effect 闭包示意图 |
| **封面级 K** | 单元 5.3 的"请求是有顺序的，响应没有" |
| **封面级 L** | 单元 5.4 的过期标记时间线 |
| **封面级 M** | 单元 5.6 的"竞态打破了同样输入同样输出"五行表 |
| **封面级 N** | 单元 5.6 的三条对策 |
| **封面级 O** | 单元 6.2 的"同源策略是浏览器的规则" |
| **封面级 P** | 单元 6.3 的简单请求条件（`application/json` 那行标红） |
| **封面级 Q** | 单元 6.5 的三种拓扑表 |
| **封面级 R** | 单元 6.5 的"dev proxy 就是在模拟同源部署" + 两个推论 |
| **封面级 S** | 单元 7.1 的"能放 URL 就放 URL" |
| **封面级 T** | 单元 8.2 的"客户端状态 vs 服务端状态"六行表 |
| **封面级 U** | 单元 8.3 的"key 的三次出现"表（**三行三色**） |
| **封面级 V** | 单元 8.5 的"第三次实现同一个机制时上库" |
| **封面级 W** | 单元 10.3 的"AI 错误三类来源"表（**第三类新增**） |
| 高光图 X | 单元 3.4 的"建立了什么需要拆掉吗" |
| 高光图 Y | 单元 4.2 / 4.3 的依赖数组三种写法、三种改法 |
| 高光图 Z | 单元 5.4 的两种修法对照 |
| 高光图 AA | 单元 6.4 的两个坑 |
| 高光图 AB | 单元 8.6 的 staleTime 业务判断 |
| 高光图 AC | 单元 9.3 的跨端对照（CORS 是浏览器特有的） |
| **录屏 1（最关键）** | 竞态复现：点 1 → 立刻点 2 → **t=150ms 暂停 3 秒** → 继续 → 跳回问题 1 |
| **截图（杀手级）** | 竞态最终态：**URL `/questions/2` + 左侧"问题 2"高亮 + 右侧"问题 1"内容** 同屏 |
| **截图（杀手级）** | **浏览器 CORS 红色报错 + 后端终端 `200 OK` 日志** 并排 |
| 录屏 2 | 无 cleanup 时计数一秒跳 2 → 加 cleanup 后正常 |
| 录屏 3 | URL 状态：改排序 → URL 变 → 复制到新标签 → 同页 → 后退 |
| 截图 | 演示一：Network 面板请求数飞涨 |
| 截图 | 演示一对应的 ESLint 警告全文 |
| 截图 | StrictMode 下两条相同请求 |
| 截图 | `curl` 成功 vs 浏览器失败（两终端并排） |
| 截图 | Network 里 `OPTIONS` + `POST` 两条 |
| 截图 | `allow_origins=["*"]` + credentials 的报错 |
| 截图 | 未配 `expose_headers` 时 `X-Request-Id` 为 `null` |
| 截图 | 忘记过滤 `AbortError` → 切换时闪"加载失败" |
| 截图 | 竞态测试红/绿两态 |
| 截图 | 手写 30 行 vs `useQuery` 5 行并排 |
| 截图 | React Query 下竞态操作不再出错 |
| 截图 | `vite preview` 下直接访问 `/questions/5` 报 404 |

### 可后补

- C 档结论卡（纯文字）。
- 单元 8.4 mutation 相关截图（若压缩则不需要）。

### 备用材料

| 风险 | 备用方案 |
|---|---|
| **竞态演示在快机器上点不够快**（最高风险） | 延迟中间件把慢的一侧调到 **2 秒**；备一个"程序化触发"的按钮（点一下自动连发两个请求）；**务必备录屏** |
| StrictMode 双执行被 React 版本改变行为 | 锁定 React 版本；底稿标注版本号；备录屏 |
| 学生环境里 CORS 报错文案与课件不一致（浏览器差异） | 统一用 Chrome 演示；截图标注浏览器与版本 |
| Docker 在教室不可用（作业二拓扑 C） | 备一个纯 nginx 本地安装方案；或提供云端演示环境 |
| React Query 大版本 API 变化（`isPending` vs `isLoading` 等） | 锁版本；代码片段标注版本 |
| 后端延迟中间件被误带上生产 | **中间件必须有 `settings.env == "dev"` 守卫**，并在 `test_conventions.py` 里加一条检查 |
| AI 现场调用失败（作业三演示） | 预录一份输出。**必须真实缺少竞态保护和清理函数**，不要人工编造 |
| 时间超支 | 按单元〇压缩顺序；单元 7、8 有自读材料 `docs/routing.md`、`docs/server-state.md` |

### 环境与运行条件

延用第 11 次课环境。**新增**：`react-router-dom`、`@tanstack/react-query`（可选）、nginx（Docker）。后端新增 `CORSMiddleware` 与 dev 延迟中间件。

**演示开始时的初始状态**：`web/` 在 tag `v12-broken`，`npm run dev` 已启动，**StrictMode 处于关闭状态**（单元 3.5 现场打开）；后端已启动且 **dev 延迟中间件已挂载**；三个终端（前端 dev、后端、命令行）；浏览器两个标签（应用 + DevTools 的 Network 面板已打开并勾选"保留日志"）。

**复位方式**：`git checkout v12-broken -- web/src app/main.py`。

---

## 十二、与前后课的衔接

**本次课回收的前序埋点**：

| 来源 | 埋点 | 回收位置 |
|---|---|---|
| 第 2 次课 | HTTP 缓存与"缓存多久"的两难 | **单元 8.2、8.6**（服务端状态是同一个问题换了一层） |
| 第 3 次课 | 入口闸门：不可信输入在最外层收窄 | 单元 7.2（`useParams` 是字符串） |
| 第 3 次课 | POST 不幂等 | 单元 8.4 |
| 第 4 次课 | `X-Request-Id` 贯穿排障 | **单元 6.4**（跨域下默认读不到！） |
| 第 5 次课 | 静默失败比响亮失败更危险 | 单元 6.4（`expose_headers` 的症状是"没有症状"） |
| 第 6 次课 | 每张表必须有主键 | **单元 8.3**（key 的第一次出现） |
| 第 6 次课 | 唯一约束防重复 | 单元 8.4 |
| 第 6 次课 | 不存冗余字段，能算就算 | 单元 2 演示五（第三次出现） |
| 第 7 次课 | 排序 `Literal` 白名单 | 单元 7.3（前移到 URL 解析处） |
| 第 7 次课 | 分页参数 | 单元 7.3（迁到 `useSearchParams`） |
| 第 8 次课 | Vite proxy "只在开发期有效" | **单元 6.1、6.5**（如约完整清账） |
| 第 8 次课 | `State<T>` 四态，二态是陷阱 | **单元 2 演示二、5.5** |
| 第 8 次课 | 契约只有一个真相来源 | 单元 2 演示五（第三次出现） |
| 第 9 次课 | 红-绿两步方法论 | 单元 5.6、6.4 各执行一次 |
| 第 9 次课 | 断言性质不断言数值 | **单元 5.6**（第三次使用） |
| 第 9 次课 | 一个可以忽略的检查等于没有检查 | **单元 4.4**（`--max-warnings 0`） |
| 第 9 次课 | 固定动作：新增纪律当场补进检查 | 单元 4.4、6.4 各兑现一次 |
| 第 10 次课 | proxy 是 dev server 的功能 | **单元 6.1**（删掉它，现场看后果） |
| 第 10 次课 | `vite preview` 跑的是真产物 | 单元 6.5（网络拓扑版的同构判据） |
| 第 10 次课 | 前端密钥必然泄漏 → 后端代理 | 单元 6.5 方案③ BFF |
| 第 10 次课 | 动态 `import()` 拆包 | 单元 7.4（按路由拆分） |
| 第 10 次课 | 装库之前先量体积 | 单元 8.5 代价清单 |
| 第 10 次课 | 护栏成本/收益框架 | 作业三第 1 问 |
| 第 10 次课 | AI 错误两类来源 | **单元 10.3 新增第三类** |
| 第 11 次课 | **快照心智** | **贯穿单元 1、3、5** |
| 第 11 次课 | 引用判等（`Object.is`） | **单元 4.1**（第三次出现） |
| 第 11 次课 | React key | **单元 8.3**（key 的第二次出现） |
| 第 11 次课 | `setState` 后不要读 state | 作业三检查项 7 |
| 第 11 次课 | 前端校验是体验，后端是安全 | 单元 7.2、8.4 |
| 第 11 次课 | StrictMode 开发期双渲染（C 档卡提及） | **单元 3.5 正式展开** |
| 第 11 次课 | `readonly` 类型护栏 | 护栏表补登第十行 |

**本次课埋下、后面必须回引的五处**（请在课件中明显标记）：

- **单元 6.2 的"请求还是发出去了"** → 第 15 次课 CSRF 的全部前提就在这一句；
- **单元 6.6 的 `allow_credentials`** → 第 14 次课讲 cookie 认证时直接接上；
- **单元 7.4 的 SPA 刷新 404** → 第 16 次课配 nginx `try_files` 时回引，作业二第 3 问已经让学生踩过一次；
- **单元 6.5 的三种拓扑表** → 第 16 次课选部署方案时直接用这张表；
- **单元 10.3 的"AI 错误三类来源"** → 第 15 次课的安全问题会同时落在第二类（不安全写法是多数）和第三类（攻击在编写期不可见），要回引对照。

**本次课不承担、请勿提前引入**：认证与 token 存储（第 14 次课）、XSS/CSRF 的攻防（第 15 次课）、部署与环境配置（第 16 次课）、WebSocket、乐观更新（C 档卡）。

**给第 13 次课的提示**：

到今天为止，**前端的完整链路已经打通**：工程化（第 10 次课）→ 渲染机制（第 11 次课）→ 数据获取与网络（第 12 次课）。学生手上有一个真正能跑、能部署的前后端应用。

同时，本次课交付了三样**后续可以直接复用的资产**：

| 资产 | 后续怎么用 |
|---|---|
| `Async<T>` 四态 + `client` 封装 | 任何新接口零成本接入 |
| **dev 延迟中间件** | **任何怀疑有时序问题的地方，挂上它跑一遍** |
| 三种网络拓扑的实测数据 | 第 16 次课选部署方案时的直接依据 |

**另外，本次课在方法论上推进了一步，值得在后续课程中持续检验**：

单元 5.6 指出：**前面所有的检查手段都建立在"同样的输入产生同样的输出"这个前提上，而竞态打破了它。**

这个判断在后面会反复出现，而且会越来越重要：

| 后续会遇到的"不确定性" | 哪次课 |
|---|---|
| 并发写入导致的数据竞争（丢失更新） | 若有数据库并发专题 |
| 攻击只在特定输入下触发 | **第 15 次课** |
| 部署时的环境差异 | **第 16 次课** |
| 负载下才出现的性能退化 | **第 16 次课** |

**建议在遇到每一个时，都回引单元 5.6 那张表，并追问同一个问题：**

**"这一类问题，是该靠'检查'发现，还是只能靠'结构'消除？"**

这个问题的答案，往往比具体的技术方案更值得学生带走。