# 第 8 次课教学底稿
## 前后端分离与 API 契约

---

## 〇、给 PPT 制作团队的全局说明

本次课 100 分钟，留 5 分钟缓冲。**本次课是全课程"契约"主线的收口。** 第 3 次课提出"契约先行是约束 AI 最有效的抓手"，当时它还只是一句判断；今天要把它变成一条**机器可检查**的链路：Pydantic schema → `/openapi.json` → TypeScript 类型 → 编译期报错。

**本次课的核心思想，请务必让它贯穿始终**：

> **单体应用里，前后端之间的接口是函数调用——改了签名，编译器立刻告诉你所有调用处。**
> **分离之后，接口变成了网络上的 JSON——没有编译器，没有类型，改了字段名，没有任何东西会告诉你。**
>
> **前后端分离最大的代价，是把编译期错误变成了运行期错误。类型生成就是把它变回去。**

这段话要做成一页单独的封面级素材，并在单元 4、6 各回引一次。

**本次课有三个高光，按重要性排序**：

1. **契约变更演练（单元 6，14 分钟）**。改一个字段名，统计"没有类型生成"和"有类型生成"两种情况下各能自动发现几处。**必须做成对照表**：前者 0 处、靠人肉找，后者 tsc 一次列出全部。这是本次课的课程主题落点。
2. **从 OpenAPI 生成类型（单元 4，16 分钟）**。三步：生成类型 → 用上类型 → 连 URL 和参数也被约束。要现场看到红波浪线。
3. **前端 N+1 与 request_id 闭环（单元 5、7）**。request_id 的闭环特别值得做：第 4 次课设计它、第 5 次课修好它、今天终于有了消费者——前端把它显示给用户，老师当场 grep 到那条日志。**这是"一个三次课之前的小设计今天才显出价值"的最好例证。**

**关于前端技术栈的选择，请在课件里明确说明理由**：本次课用 **Vite + 原生 TypeScript，不用任何前端框架**。理由有三条，要讲给学生听：今天的主题是契约不是框架；框架会把契约问题藏进它自己的数据层里；三个页面用不着框架。真实项目会用 React/Vue，C 档卡给落点。

**一个必须守住的边界**：第 5 次课的 C 档卡已经承诺"CORS 的坑第 12 次课现场踩"。所以本次课会**遇到一次** CORS 报错，**当场用 Vite proxy 绕过**，只给一句话解释，明确记欠账。**不要在本次课展开 CORS 配置**，那会抢掉第 12 次课的主线。

**若时间不够的压缩顺序**：先压单元 9 的 C 档卡（整体移课后）→ 再压单元 8 的版本化（只留判据表）→ 再压单元 5 的样式与页面细节（前端代码给成品，课上只讲三态）。**单元 4、6 不能压缩。**

---

## 一、开场：M2 之上，还缺什么

**约 4 分钟。**

### 1.1 盘点现状

M2 交付后，项目里有**两套客户端**，共享同一套业务层：

```
                    ┌─────────────┐
   浏览器直接访问 →  │  HTML 页面   │ ─┐
   （第 5 次课）     └─────────────┘  │
                                      ├→ services/ → repositories/ → DB
   curl / Postman →  ┌─────────────┐  │
   （第 3 次课）      │  JSON API   │ ─┘
                     └─────────────┘
```

提问：**既然 HTML 页面已经能用了，为什么还要再做一套前端？**

让学生答，通常会说"更好看""体验好"。指出这些都不是架构理由，然后给出真正的四条：

| 真正的理由 | 说明 |
|---|---|
| **多端复用** | iOS、Android、小程序、第三方集成——它们都用不了你的 HTML |
| **独立部署节奏** | 前端改个按钮颜色不需要重启后端；后端加个索引不需要前端发版 |
| **团队并行** | 两个人可以同时开工，只要契约先定下来 |
| **前端资源可上 CDN** | 静态文件就近分发，后端只管数据 |

> 注意这四条里**没有一条是"更好看"**。SSR 页面一样可以很好看。
>
> 而且我要先把话说在前面：**这四条好处，全部建立在"契约不漂移"这个前提上。** 契约一漂移，四条全变成负担——这正是今天要处理的。

### 1.2 本次课要回答的问题

本次课结束时你应当能回答：

- "前后端分离"具体改变了哪几行代码？**能数清楚吗？**
- 后端把 `body` 改名成 `content`，前端会发生什么？**为什么没有任何东西报错？**
- 怎么让"字段名写错"在**编译期**就被发现？
- 前端要不要再写一遍校验规则？**规则的唯一来源在哪？**
- 第 4 次课设计的 `request_id`，前端该拿它做什么？
- 什么时候**不该**分离？
- 什么样的 API 变更是破坏性的？破坏性变更怎么发布？

---

## 二、解剖台：AI 写的那个前端

**约 12 分钟。四个演示都要做。**

### 情境设定

> 你把后端的 `/docs` 截图发给 AI，说"给我写一个前端，展示问题列表，能点进详情，能发新问题"。
>
> 它给了你一个 `index.html` 和一个 `app.js`。打开，能用。你很满意。

### 代码（tag: `v8-broken`）

```javascript
// static/app.js —— AI 原样产出
async function loadQuestions() {
  const res = await fetch('http://localhost:8000/questions?page=1&size=20');
  const data = await res.json();
  const list = document.getElementById('list');
  list.innerHTML = data.items.map(q => `
    <li>
      <a href="/detail.html?id=${q.id}">${q.title}</a>
      <span class="meta">${q.author.display_name} · ${q.answer_count} 回答</span>
    </li>
  `).join('');
}

async function loadDetail(id) {
  const res = await fetch('http://localhost:8000/questions/' + id);
  const q = await res.json();
  document.getElementById('title').textContent = q.title;
  document.getElementById('body').innerHTML = q.body;          // ← 记住这里
}

async function submitQuestion() {
  const title = document.getElementById('title-input').value;
  const body  = document.getElementById('body-input').value;
  if (title.length < 5) { alert('标题太短'); return; }          // ← 和后端各写一遍
  if (body.length < 10) { alert('正文太短'); return; }

  const res = await fetch('http://localhost:8000/questions', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({title: title, body: body})
  });
  if (!res.ok) {
    console.log('失败', res.status);                            // ← 只打控制台
    return;
  }
  location.href = '/';
}

loadQuestions();
```

先让学生看 30 秒，提问：**你觉得这段代码有问题吗？**

多数人会说"没什么问题"或者只挑出 `innerHTML`。**这正是本次课要处理的：它的问题都不在"这一行写错了"的层面。**

### 演示一：后端改个字段名，前端静默变空白

**这个演示要接第 7 次课**：

> 上节课我们做了一次迁移，把 `questions.body` 改名成 `content`。当时我们修了模型、修了 schema、修了迁移脚本。
>
> **现在把那次改动真正应用上去，看前端会怎样。**

```python
# app/schemas/question.py
class QuestionDetail(BaseModel):
    id: int
    title: str
-   body: str
+   content: str
```

刷新详情页：

```
标题：如何理解 SQL 的三值逻辑
正文：（空白）
```

打开控制台：**什么都没有。没有报错，没有警告，没有红色。**

> `q.body` 在 JavaScript 里是 `undefined`。`textContent = undefined` 就是清空。
>
> **JavaScript 不认为这是错误。** 访问一个不存在的属性返回 `undefined`，这是语言规范里的正常行为。
>
> 对比一下：如果这是一次函数调用，`get_question().body` 在 Python 里会抛 `AttributeError`，在 TypeScript 里编译就过不去。**分离之后，这个保护消失了。**

提问：**这个 bug 什么时候会被发现？**

> 答案：**用户打开详情页，看到一片空白，然后不说话，然后走了。**
>
> 或者：三天后有人在群里说"详情页是不是坏了"。

### 演示二：后端 500 了，前端白屏

停掉数据库，刷新列表页：

```
（整个页面空白）
```

控制台：`Uncaught TypeError: Cannot read properties of undefined (reading 'map')`

> 后端返回的是第 4 次课设计的统一错误体：
>
> ```json
> {"code": "internal_error", "message": "服务器内部错误",
>  "detail": null, "request_id": "a3f91c22e0d7"}
> ```
>
> 这个响应体里**没有 `items`**，所以 `data.items.map` 炸了。
>
> 我们花了一整次课设计错误契约，**前端一个字段都没用。** `request_id` 就在那里，它是我们专门为了"用户报障时能定位"设计的，现在它进了 `data` 变量然后被丢掉了。

再演示第三种情况——数据库正常但没有数据：

```bash
curl -s "localhost:8000/questions?page=999" | jq '.items | length'
# 0
```

页面：**也是空白。**

> **三种完全不同的情况，用户看到的是同一个东西：**
>
> | 实际发生了什么 | 用户看到 | 用户该怎么办 |
> |---|---|---|
> | 正在加载 | 空白 | 等一下 |
> | 后端挂了 | 空白 | 报障 / 稍后再试 |
> | 确实没有数据 | 空白 | 去发一条 |
>
> **三种情况需要三种不同的用户行为，但界面给了同一个信号。** 这不是"不好看"的问题，是**信息丢失**。

### 演示三：前端校验和后端校验对不上

前端写的是 `title.length < 5`，后端 schema 写的是 `min_length=5`。看起来一样。

现场输入一个标题：`  测试  `（前后各两个空格，共 8 个字符）

- 前端：`length = 8`，通过 ✅
- 后端：`title.strip()` 之后是 2 个字符，校验失败 → **422**
- 前端：`res.ok` 为 false → `console.log('失败', 422)` → **用户什么都没看到，表单还在那，按钮好像没反应**

> 两套规则，写在两个地方，用两种语言。**它们今天一致，下周就不一致了。**
>
> 而且注意失败的方式：**不是"报错"，是"没反应"。** 用户会再点一次，还是没反应，然后关掉页面。

### 演示四：多一次网络往返

列表页要显示作者名，于是 `QuestionOut` 里嵌套了 `author`。但如果后端只返回了 `author_id`，AI 很自然会这么写：

```javascript
// 一个常见的"补救"写法
for (const q of data.items) {
  const u = await fetch(`http://localhost:8000/users/${q.author_id}`);
  q.author = await u.json();
}
```

打开浏览器 Network 面板，刷新列表页：

```
请求数：21
总耗时：1.9 s
```

> **第 7 次课的 N+1，在前端又来了一次。**
>
> 而且前端版本更贵：后端的 N+1 是 41 次数据库往返（每次零点几毫秒），前端的 N+1 是 21 次**完整的 HTTP 往返**——每次都包含 DNS、TCP、TLS、认证、中间件、序列化。
>
> 单元 7 会量化这个差别。

### 四个问题的性质对照（**做成一页**）

| 问题 | 症状 | 谁会发现 | 什么时候发现 |
|---|---|---|---|
| ① 字段改名 | 页面局部空白 | 用户 | 上线后 |
| ② 三态不分 | 页面全空白 | 用户 | 出故障时 |
| ③ 校验双写 | 按钮"没反应" | 用户 | 边界输入时 |
| ④ 前端 N+1 | 慢 | 用户（或没人） | 数据量上来时 |
| —— | | | |
| 共同点 | **控制台里一个红字都没有** | **全都是用户** | **全都是上线后** |

> 第七次课我们说过"在你能做的所有常规检查里，它们都是好的"。
>
> **今天这四个更进一步：连运行时都不报错。** 它们静默地降级，把问题转嫁给用户。
>
> 所以今天的目标不是"把这四个修好"——修好很容易。**目标是让这四类问题以后都无法静默发生。**

### 欠账清单

| 问题 | 本次课处理 | 何时还 |
|---|---|---|
| 字段名靠手写字符串 | **单元 4**（类型生成） | — |
| URL 硬编码 | **单元 4.4**（类型化客户端） | — |
| 三态缺失 | **单元 5.2** | — |
| 错误契约无人消费、`request_id` 被丢弃 | **单元 5.3** | — |
| 校验规则双写 | **单元 5.4** | — |
| 前端 N+1 | **单元 7** | — |
| `innerHTML` 渲染用户内容 | 单元 5.5 指出 | **第 15 次课**（XSS） |
| 跨端口请求被浏览器拦 | 单元 3.3 用 proxy 绕过 | **第 12 次课**（CORS 完整解法） |
| 前端怎么带身份 | 记一笔 | **第 14 次课** |
| 前端构建产物怎么部署 | 记一笔 | **第 16 次课** |
| 类型生成怎么进 CI | 记一笔 | **第 9 次课** |

---

## 三、分离到底改了哪几行

**约 10 分钟。**

### 3.1 把第 5 次课那张表拿出来

**这是第 5 次课单元 8.6 的原表，请直接复用同一张图，加一列**：

| | JSON API | HTML 表单（第 5 次课） | **SPA 前端（今天）** |
|---|---|---|---|
| Content-Type | `application/json` | `x-www-form-urlencoded` | `application/json` |
| 接参 | Pydantic 模型 | `Form(...)` | Pydantic 模型 |
| 校验失败 | 422 JSON | 服务端重渲染 + 回填 | **422 JSON，前端回填** |
| 成功 | 201 + 资源体 | 303 重定向 | **201 + 资源体，前端跳转** |
| 谁处理"刷新重提交" | 前端（不会重放） | 服务端（PRG） | **前端（不会重放）** |
| 一次性提示 | 前端状态管理 | flash（服务端会话） | **前端状态管理** |
| 谁渲染 HTML | —— | **服务端** | **浏览器** |
| 共用的部分 | **`services/` 和 `repositories/` 完全一样** | | ← 三套都一样 |

**关键提问**：

> 看最后一行。第 5 次课加 HTML 时，业务层零改动。第 7 次课换掉整个数据访问技术栈，业务层零改动。
>
> **今天加一个 SPA 前端，后端要改几行？**

### 3.2 现场数一遍

**答案：后端改动接近于零。** 现场用 `git diff --stat` 证明：

```
app/main.py            |  6 ++++++      ← 挂载静态文件 / 开发期 CORS（见 3.3）
app/schemas/common.py  |  4 ++++        ← 分页响应加 total、has_next（见 3.4）
2 files changed, 10 insertions(+)
```

> **10 行。**
>
> 而前端新增了 300 行。这个比例本身就说明了分离的性质：
>
> **"前后端分离"这个词容易让人以为是一次后端重构。它不是。后端早在第 3 次课定下 JSON 契约的时候就已经"分离"了。**
>
> **今天做的事情是：给那个契约加一个新的消费者。**
>
> 判据：**如果你的项目"改成前后端分离"需要大改后端，那说明你的后端之前就没有清晰的契约边界**——业务逻辑写在模板里、状态存在服务端会话里、页面跳转由后端决定。

### 3.3 那 10 行里的第一处：跨端口被拦住了

启动前端开发服务器（`localhost:5173`），打开页面：

```
Access to fetch at 'http://localhost:8000/questions' from origin
'http://localhost:5173' has been blocked by CORS policy: No
'Access-Control-Allow-Origin' header is present on the requested resource.
```

> 浏览器拦住了。**注意是浏览器拦的，不是后端拒绝的**——后端根本没看到这个请求被拒，或者看到了正常响应但浏览器不给 JS。
>
> 今天我们**不解决它**，用一个开发期的办法绕过去：

```typescript
// web/vite.config.ts
export default defineConfig({
  server: {
    proxy: {
      "/api": {
        target: "http://localhost:8000",
        changeOrigin: true,
        rewrite: (p) => p.replace(/^\/api/, ""),
      },
    },
  },
});
```

```typescript
// 前端里所有请求改成同源路径
fetch("/api/questions")       // 浏览器认为这是同源请求
```

> **为什么这样就行了？** 因为请求发给了 `localhost:5173`（同源，浏览器不管），由 Vite 的开发服务器在**服务端**转发到 8000。**服务器之间的请求没有同源策略。**
>
> 但我要明确说清两件事：
>
> 1. **这只在开发期有效。** 生产环境没有 Vite dev server。
> 2. **它掩盖了一个真实存在的问题。** 这是本课程第三次看到"开发环境掩盖生产问题"了——第 5 次课多 worker 掩盖串行化、第 7 次课空库掩盖迁移的数据丢失，今天是 proxy 掩盖跨域。
>
> **判据：凡是"开发时正常、生产时才出现"的问题，都要在开发期就人为制造一次。** 第 12 次课我们会把 proxy 关掉，正面处理它——包括"为什么 CORS 中间件必须在最外层"（第 5 次课 C 档卡埋的点）。
>
> 记欠账。

### 3.4 那 10 行里的第二处：分页响应要变

SSR 时代分页很简单——服务端知道当前是第几页，直接渲染页码。SPA 不知道，它只有一个 JSON。

```python
# app/schemas/common.py
class Page(BaseModel, Generic[T]):
    items: list[T]
    total: int          # ← 新增
    page: int
    size: int
    has_next: bool      # ← 新增
```

> 这是一个很小的改动，但它说明了一件事：
>
> **分离会让"状态放在哪"这个问题浮出水面。** SSR 时代，"当前第几页"这个状态在服务端的请求处理过程里；分离之后，它必须被显式地传输。
>
> 类似的状态还有一堆：当前用户是谁、有没有未读消息、刚才那个操作成功了没有（第 5 次课的 flash）。**每一个都要变成契约的一部分。**
>
> 顺便：`total` 这个字段看起来无害，但它意味着**每次列表查询都要多一条 `SELECT count(*)`**。十万行表上这条 count 不便宜。**这是"前端要什么后端就给什么"的第一个代价样本**，单元 7 会系统地讲。
>
> 〔`total` 的替代方案：只给 `has_next`（多查一条看有没有），前端做"加载更多"而不是页码。**→ 第 11 次课 keyset 分页会重新讨论。**〕

### 3.5 前端工程的最小形态

```
web/
├── index.html          # 列表页
├── detail.html         # 详情页
├── new.html            # 发帖页
├── src/
│   ├── api.d.ts        # ← 生成的，不手写（单元 4）
│   ├── client.ts       # 请求封装
│   ├── render.ts       # 三态渲染（单元 5）
│   ├── list.ts
│   ├── detail.ts
│   └── new.ts
├── vite.config.ts
├── tsconfig.json
└── package.json
```

**为什么不用框架（要讲给学生听）**：

> 1. **今天的主题是契约，不是框架。** React 的状态管理、Vue 的响应式，都是另一门课的内容。
> 2. **框架会把契约问题藏起来。** 你用 React Query，它会帮你处理 loading/error 三态——**你就学不到为什么需要三态了**。
> 3. **三个页面用不着框架。** 用得着的时候你自然会知道。
>
> 真实项目当然用框架。**但框架解决的是"UI 状态怎么组织"，不解决"契约怎么不漂移"。** 后者是今天的题目，而且换了框架照样存在。

### 材料

- tag `v8-broken`（起始）、`v8-proxy`（本单元结束）。
- **高光图**：第 5 次课那张对照表加第三列（请与第 5 次课同风格，可叠加）。
- 截图：CORS 报错的浏览器控制台原文。
- 截图：`git diff --stat` 显示后端只改了 10 行。

---

## 四、契约：从 OpenAPI 到编译期检查

**约 16 分钟。本次课第二高光。**

### 4.1 先确认契约已经在那里了

```bash
curl -s localhost:8000/openapi.json | jq '.components.schemas | keys'
```

```json
["AnswerBrief", "ErrorBody", "Page_QuestionOut_", "QuestionCreate",
 "QuestionDetail", "QuestionOut", "UserBrief", "ValidationError"]
```

```bash
curl -s localhost:8000/openapi.json | jq '.components.schemas.QuestionOut'
```

```json
{
  "type": "object",
  "required": ["id", "title", "author", "answer_count", "created_at"],
  "properties": {
    "id": {"type": "integer"},
    "title": {"type": "string", "minLength": 5, "maxLength": 200},
    "author": {"$ref": "#/components/schemas/UserBrief"},
    "answer_count": {"type": "integer"},
    "created_at": {"type": "string", "format": "date-time"}
  }
}
```

**醒目页**：

> **这个文件不是文档。它是一份机器可读的契约。**
>
> 它是从你的 Pydantic schema **自动生成**的——你第 3 次课写 `response_model` 的时候，就已经在写这份契约了，只是当时你以为你在写文档。
>
> 三条信息全在里面：
> - **有哪些字段**（前端不用猜字段名）
> - **哪些是必填**（前端知道什么时候要处理 `null`）
> - **约束是什么**（`minLength: 5` ——这就是那条前端重写了一遍的规则）
>
> 判据：**如果一份契约是手工维护的 Markdown 文档，它一定会过时。如果它是从代码生成的，它不会。**

### 4.2 第一步：生成 TypeScript 类型

```bash
cd web
npm i -D openapi-typescript
npx openapi-typescript http://localhost:8000/openapi.json -o src/api.d.ts
```

打开生成的文件看一眼（**不要逐行念，只看关键部分**）：

```typescript
// src/api.d.ts —— 生成的，不要手改
export interface components {
  schemas: {
    QuestionOut: {
      id: number;
      title: string;
      author: components["schemas"]["UserBrief"];
      answer_count: number;
      created_at: string;
    };
    ErrorBody: {
      code: string;
      message: string;
      detail?: Record<string, unknown> | null;
      request_id: string;
    };
    // ...
  };
}

export interface paths {
  "/questions": {
    get: {
      parameters: { query?: { page?: number; size?: number; sort?: "latest" | "oldest" | "views" } };
      responses: { 200: { content: { "application/json": components["schemas"]["Page_QuestionOut_"] } } };
    };
    post: { /* ... */ };
  };
  "/questions/{qid}": { /* ... */ };
}
```

**停下来指出两处**：

> **一、`sort` 的类型是 `"latest" | "oldest" | "views"`。**
>
> 这是第 7 次课单元 8.4 那个 `Literal` 白名单。**你在后端为了防注入写的一个类型，今天变成了前端的自动补全。**
>
> 同一个约束，服务了三件事：挡住非法输入（第 7 次课）、自我描述的 API 文档、前端的类型提示。**这就是"契约先行"的复利。**
>
> **二、`ErrorBody` 也在里面。**
>
> 第 4 次课设计的统一错误体，因为它是一个 Pydantic 模型，所以它也进了契约。**前端现在可以按类型处理错误了。**

### 4.3 第二步：把类型用起来，看它红给你看

```typescript
// src/list.ts
import type { components } from "./api";

type QuestionOut = components["schemas"]["QuestionOut"];

function renderItem(q: QuestionOut): string {
  return `<li>
    <a href="/detail.html?id=${q.id}">${q.title}</a>
    <span>${q.author.display_name} · ${q.answer_count} 回答</span>
  </li>`;
}
```

**现场演示：故意写错一个字段名。**

```typescript
  return `<li>... ${q.auther.display_name} ...</li>`;
//              ~~~~~~
```

编辑器立刻画红波浪线：

```
Property 'auther' does not exist on type 'QuestionOut'. Did you mean 'author'?
```

```bash
npx tsc --noEmit
# src/list.ts:8:22 - error TS2551: Property 'auther' does not exist...
# Found 1 error.
```

**回到本次课的核心句（醒目页，第二次出现）**：

> **分离把编译期错误变成了运行期错误。类型生成把它变回去了。**
>
> 而且注意：**这个类型不是我写的，是从后端的 Pydantic schema 生成的。**
>
> 所以这条链是：
>
> ```
> Pydantic schema  →  /openapi.json  →  api.d.ts  →  tsc 报错
>    （后端真相）      （机器可读契约）    （前端类型）   （编译期拦截）
> ```
>
> **后端改了 schema，这条链会一路传导到前端的编译错误。** 单元 6 会现场走一遍。

### 4.4 第三步：连 URL 和参数也别手写

字段名解决了，但 URL 还是字符串：

```typescript
fetch("/api/questions?page=1&size=20")      // 拼错了也没人管
fetch("/api/question/" + id)                // 少个 s，运行时 404
```

用 `openapi-fetch`：

```bash
npm i openapi-fetch
```

```typescript
// src/client.ts
import createClient from "openapi-fetch";
import type { paths } from "./api";

export const api = createClient<paths>({ baseUrl: "/api" });
```

```typescript
// src/list.ts
const { data, error } = await api.GET("/questions", {
  params: { query: { page: 1, size: 20, sort: "latest" } },
});
```

**现场演示三次报错**：

```typescript
await api.GET("/question", ...);
//            ~~~~~~~~~~~  路径不在契约里

await api.GET("/questions", { params: { query: { sort: "newest" } } });
//                                            ~~~~~~~~  不是那三个值之一

await api.GET("/questions", { params: { query: { page: "1" } } });
//                                            ~~~~  应该是 number
```

> 现在**路径、查询参数、请求体、响应体，四样东西全部被契约约束了**。
>
> `data` 的类型自动就是 `Page_QuestionOut_`，`error` 的类型自动就是 `ErrorBody`。**一行类型标注都不用写。**

### 4.5 第六道结构性护栏

**醒目页，累加表**：

| 次课 | 护栏 | 把什么变成了什么 | 在哪一层拦住 |
|---|---|---|---|
| 第 3 次课 | `response_model` | 字段泄漏 → 出不去 | 运行时（后端） |
| 第 4 次课 | 全局异常处理器 | 内部信息泄漏 → 统一错误体 | 运行时（后端） |
| 第 5 次课 | Jinja2 自动转义 | 用户输入变 HTML → 纯文本 | 运行时（后端） |
| 第 6 次课 | 数据库约束 | 脏数据 → 写入失败 | 运行时（数据库） |
| 第 7 次课 | `lazy="raise"` | 静默 N+1 → 响亮报错 | 运行时（后端） |
| **第 8 次课** | **生成的类型** | **字段名写错 → 编译失败** | **编译期（前端）** |

> 第六道和前五道有一个本质区别，请特别注意：
>
> **前五道都在运行时拦截——错误已经发生了，只是被拦住了。**
> **第六道在编译期拦截——错误根本没机会发生。**
>
> 这是护栏能达到的最好位置。**判据：能在编译期拦的，不要留到运行时。**
>
> 但它有一个前提：**契约必须是生成的，不是手写的。** 手写的 `.d.ts` 只会给你虚假的安全感——它和后端不一致的时候，编译器会自信地告诉你"没问题"。

### 4.6 一条纪律和一个欠账

**纪律（写进 README）**：

```json
// package.json
{
  "scripts": {
    "gen": "openapi-typescript http://localhost:8000/openapi.json -o src/api.d.ts",
    "check": "tsc --noEmit"
  }
}
```

> 1. **`src/api.d.ts` 是生成物。它要提交到仓库**（这样别人不用起后端就能编译），**但永远不要手改它。**
> 2. 文件头加一行 `// GENERATED —— do not edit. Run: npm run gen`。
> 3. **后端改了 schema，第一件事是 `npm run gen`。**

**欠账**：

> 第 3 条靠人记得，就和前七次课骂过无数遍的做法一样。
>
> 正确的做法是 CI 里做：重新生成一次，**如果生成的结果和仓库里的不一致，构建失败**。这就把"记得重新生成"变成了结构性的。
>
> ```bash
> npm run gen && git diff --exit-code src/api.d.ts
> ```
>
> **→ 第 9 次课写进 CI。** 今天先记账。

### 材料

- **封面级素材**："编译期 vs 运行期"那句核心话，单独一页。
- **封面级素材**：`Pydantic schema → openapi.json → api.d.ts → tsc 报错` 的四段链路图。
- **封面级素材**：六道护栏累加表，第六行的"编译期"用不同颜色。
- 截图：`openapi.json` 里 `QuestionOut` 的定义（含 `minLength`）。
- 截图：编辑器里 `q.auther` 的红波浪线 + "Did you mean 'author'?"。
- 截图：`api.GET("/questions", { query: { sort: "newest" }})` 的类型报错。
- tag `v8-typed`（本单元结束状态）。

---

## 五、前端最小闭环：三态与错误契约

**约 12 分钟。**

### 5.1 三态是什么

**醒目页**：

> **任何一次异步数据获取，都有且只有四种状态：**
>
> | 状态 | 界面应该显示 | 用户该做什么 |
> |---|---|---|
> | **loading** | 骨架屏 / 转圈 | 等 |
> | **error** | 错误信息 + 重试按钮 + **错误编号** | 重试 或 报障 |
> | **empty** | "还没有内容" + 引导动作 | 去创建 |
> | **success** | 数据 | 用 |
>
> **判据：写任何一个数据展示组件，先问"这四种状态我都画了吗"。**
>
> 缺一种，就会有一类用户在某个时刻看到一片空白然后离开。

### 5.2 实现

```typescript
// src/render.ts
type State<T> =
  | { kind: "loading" }
  | { kind: "error"; message: string; requestId?: string }
  | { kind: "empty" }
  | { kind: "success"; data: T };

export function render<T>(
  el: HTMLElement,
  state: State<T>,
  ok: (data: T) => string,
) {
  switch (state.kind) {
    case "loading":
      el.innerHTML = `<div class="skeleton">加载中…</div>`;
      break;
    case "error":
      el.innerHTML = `
        <div class="error">
          <p>${escapeHtml(state.message)}</p>
          ${state.requestId
            ? `<p class="rid">错误编号：<code>${state.requestId}</code></p>`
            : ""}
          <button onclick="location.reload()">重试</button>
        </div>`;
      break;
    case "empty":
      el.innerHTML = `
        <div class="empty">还没有问题<a href="/new.html">发第一条</a></div>`;
      break;
    case "success":
      el.innerHTML = ok(state.data);
      break;
  }
}
```

> 注意 `State<T>` 这个**可辨识联合类型**：TypeScript 会强制你在 `switch` 里处理所有分支，**漏一个就编译不过**。
>
> **这是又一个"把纪律变成结构"的例子。** "记得处理三态"是纪律，靠人记得；用联合类型表达状态，编译器帮你检查。

### 5.3 对接统一错误契约 —— request_id 的闭环（**本单元高光，必须现场做**）

```typescript
// src/client.ts
import type { components } from "./api";
type ErrorBody = components["schemas"]["ErrorBody"];

export async function call<T>(fn: () => Promise<{data?: T; error?: ErrorBody}>):
    Promise<State<T>> {
  try {
    const { data, error } = await fn();
    if (error) {
      return { kind: "error", message: error.message, requestId: error.request_id };
    }
    return { kind: "success", data: data! };
  } catch {
    return { kind: "error", message: "网络连接失败，请检查网络后重试" };
  }
}
```

**现场演示（三步，必须连着做完）**：

**第一步**：停掉数据库，刷新页面。

```
┌──────────────────────────────┐
│  服务器内部错误                │
│  错误编号：a3f91c22e0d7        │
│  [ 重试 ]                     │
└──────────────────────────────┘
```

**第二步**：在服务端终端里：

```bash
grep a3f91c22e0d7 server.log
```

```
2025-03-25 14:22:31 ERROR unhandled rid=a3f91c22e0d7
Traceback (most recent call last):
  File "app/repositories/question.py", line 34, in list_questions
    ...
sqlalchemy.exc.OperationalError: connection to server ... failed
```

**第三步**，停下来说：

> **这是一个跨越四次课的闭环。**
>
> | 什么时候 | 做了什么 |
> |---|---|
> | 第 4 次课 | 设计统一错误体，加了一个 `request_id` 字段。当时有同学问"这玩意有什么用" |
> | 第 4 次课 | 中间件生成 request_id 并放进响应头 |
> | 第 5 次课 | 发现异常路径下它失效了，在异常处理器里补了一次 |
> | **今天** | **前端把它显示给用户** |
>
> 现在这条链是通的：
>
> **用户截图 → 上面有编号 → 你 grep 一下 → 直接看到那次请求的完整堆栈。**
>
> 不用问"你什么时候操作的""你点了什么""能复现吗"。
>
> 判据：**可观测性不是上线前加的，是设计时就留好的。** 第 4 次课那个字段当时看起来是多余的，今天它省掉的是每一次线上排障的半小时。

### 5.4 校验规则的唯一来源（**回收第 5 次课欠账**）

先重申问题：前端 `title.length < 5`，后端 `min_length=5`，**两个地方，会漂移**。

**关键判断（醒目页）**：

> **前端校验和后端校验的目的不同，所以不能互相替代，但规则必须同源。**
>
> | | 前端校验 | 后端校验 |
> |---|---|---|
> | 目的 | **即时反馈**（不等往返就知道错了） | **权威保证**（谁都绕不过） |
> | 能不能省 | 能，只是体验差 | **绝对不能**（用 curl 直接打就绕过前端了） |
> | 规则来源 | **来自后端契约** | 后端自己定义 |
>
> **判据：前端校验是体验优化，不是安全措施。** 永远假设前端不存在。

**规则同源的三种做法，按代价排序**：

| 做法 | 怎么做 | 代价 |
|---|---|---|
| **A. 只在提交时用后端结果**（本课程起点） | 不写前端规则，收到 422 后把 `detail` 映射到字段 | 要等一次往返 |
| **B. 从 OpenAPI 读约束** | `openapi.json` 里有 `minLength`，生成一份规则表 | 需要一点脚手架 |
| **C. 共享 schema 定义** | 用 JSON Schema 或 Zod，前后端同一份 | 侵入性最大 |

**本课程做 A + 一点 B**。先看 A：

后端 422 的响应体（第 3 次课学过它的结构）：

```json
{
  "code": "validation_error",
  "message": "请求数据校验失败",
  "detail": {
    "fields": [
      {"field": "title", "type": "string_too_short", "msg": "标题至少 5 个字"}
    ]
  },
  "request_id": "..."
}
```

```typescript
// src/new.ts
const { error } = await api.POST("/questions", { body: { title, body } });
if (error?.code === "validation_error") {
  const fields = (error.detail as any)?.fields ?? [];
  for (const f of fields) {
    showFieldError(f.field, f.msg);       // ← 就地显示在对应输入框下
  }
  return;
}
```

> **注意 `error.code === "validation_error"` 这个判断。**
>
> 回收第 3 次课的判据：**依赖稳定标识，不依赖人类可读的文案。** 这是这条判据在本课程的**第四次**出现（422 的 `type`、数据库约束名、错误 `code`）。
>
> 如果这里写 `error.message === "请求数据校验失败"`，那后端改一个字的文案，前端就坏了。

**再看那"一点 B"**：

```typescript
// src/constraints.ts —— 由脚本从 openapi.json 提取，不手写
export const CONSTRAINTS = {
  QuestionCreate: {
    title: { minLength: 5, maxLength: 200 },
    body:  { minLength: 10 },
  },
} as const;
```

```html
<input name="title" minlength="5" maxlength="200" required>
```

> 把约束提取出来，用在 HTML 的原生属性上，浏览器就能做即时提示。**规则仍然只在后端定义一次。**
>
> 判据：**"同一条规则出现在两个地方"不可怕，可怕的是"两个地方各自定义"。** 生成 ≠ 复制。

**至此第 5 次课那笔欠账还清了**：

> 第 5 次课我说 HTML 表单路径不得不手写 `if len(title) < 5`，因为 Pydantic 的 422 是 JSON 而表单要的是回填页面。当时说"这是 B 档选做"。
>
> **分离之后这个矛盾消失了**——因为前端本来就在消费 JSON。422 的 `detail.fields` 直接映射到输入框，**规则从头到尾只有后端 schema 一份**。
>
> 这是分离的一个真实好处，而且不在开场那四条里：**它消除了"同一套规则服务两种客户端"的那次妥协。**

### 5.5 顺手指出 XSS 口子

```javascript
document.getElementById('body').innerHTML = q.body;     // 解剖台里的那一行
```

> 第 5 次课讲过：Jinja2 **默认**转义，`| safe` 是手动关掉它。
>
> **前端这边默认值是反的：`innerHTML` 默认不转义，`textContent` 才转义。**
>
> | | 默认行为 | 危险的那个 |
> |---|---|---|
> | Jinja2 | 转义 | `\| safe` |
> | `innerHTML` | **不转义** | 默认就是它 |
> | `textContent` | 转义 | —— |
> | React `{}` | 转义 | `dangerouslySetInnerHTML`（名字起得好） |
>
> 判据：**换栈时必须查一遍"这个模板/渲染机制的默认值是安全的还是危险的"。** 不要把上一个栈的安全感带过来。
>
> 今天先把 `innerHTML` 换成 `textContent`。**完整的 XSS 演示和富文本的正确处理方式 → 第 15 次课。**

### 材料

- **封面级素材**：request_id 闭环四步图（第 4 次课设计 → 第 5 次课修好 → 今天显示 → grep 到日志），配现场截图。
- 截图：错误态界面（含错误编号）+ 服务端 `grep` 结果，**同屏并排**。
- 截图：四种状态的界面各一张（loading / error / empty / success）。
- 高光图：5.4 的前端/后端校验对照表。
- 高光图：5.5 的"默认值是否安全"四行表。
- tag `v8-states`（本单元结束状态）。

---

## 六、现场必做：契约变更演练

**约 14 分钟。本次课最高光，绝对不能压缩。**

### 6.1 设计：同一次变更，两种世界

> 需求：产品说"问题列表里要显示标签，另外 `answer_count` 改名叫 `reply_count`，和界面文案对齐"。
>
> 我们分两次做这个变更：**第一次在"没有类型生成"的世界，第二次在"有类型生成"的世界。**

### 6.2 第一轮：没有类型生成（切到 tag `v8-broken`）

后端改：

```python
class QuestionOut(BaseModel):
    id: int
    title: str
    author: UserBrief
-   answer_count: int
+   reply_count: int
+   tags: list[TagBrief]
```

**不碰前端**，刷新页面。

```
如何理解 SQL 的三值逻辑
张三 · undefined 回答
```

现场提问，逐个确认：

| 检查手段 | 发现了吗 |
|---|---|
| 浏览器控制台 | ❌ 一个字都没有 |
| 后端日志 | ❌ 请求 200 |
| 后端测试 | ❌ 全绿（后端确实是对的） |
| 前端有测试的话 | ❓ 取决于测试写没写这个字段 |
| `git grep answer_count` | ✅ **只能这样了** |

```bash
cd web && grep -rn "answer_count" src/
# src/list.ts:12
# src/detail.ts:31
```

> **人肉 grep 是唯一的手段。** 而且它只能找到字符串完全匹配的地方——如果前端写的是 `q["answer_" + "count"]`，或者字段名被拼进了模板字符串的变量里，grep 就找不到。
>
> 更麻烦的是**新增字段 `tags`**：grep 找不到"应该用但没用"的地方。**前端要靠人去读 API 文档才知道多了个字段。**

### 6.3 第二轮：有类型生成（切到 tag `v8-typed`）

同样的后端改动，然后：

```bash
cd web
npm run gen                 # 重新生成 api.d.ts
npm run check               # tsc --noEmit
```

```
src/list.ts:12:38 - error TS2339: Property 'answer_count' does not exist on
  type 'QuestionOut'. Did you mean 'reply_count'?

12     <span>${q.author.display_name} · ${q.answer_count} 回答</span>
                                            ~~~~~~~~~~~~

src/detail.ts:31:20 - error TS2339: Property 'answer_count' does not exist on
  type 'QuestionDetail'. Did you mean 'reply_count'?

Found 2 errors in 2 files.
```

> **两处，全部列出，带行号，带修改建议。**
>
> 而且注意 `git diff api.d.ts`：

```diff
   QuestionOut: {
     id: number;
     title: string;
     author: components["schemas"]["UserBrief"];
-    answer_count: number;
+    reply_count: number;
+    tags: components["schemas"]["TagBrief"][];
   };
```

> **这份 diff 就是"契约变更清单"。** 它是自动生成的，不会漏，不会过时，而且可以放进 PR 里让人审。
>
> 新增的 `tags` 字段虽然不会导致编译错误（加字段不是破坏性变更），**但它出现在 diff 里了**——前端一眼就知道"后端给了新东西"。

### 6.4 对照表（**封面级素材**）

| | 没有类型生成 | 有类型生成 |
|---|---|---|
| 发现改名的手段 | 人肉 grep | **`tsc --noEmit`** |
| 能发现几处 | 取决于 grep 写得准不准 | **全部，2/2** |
| 发现"新增了字段" | ❌ 要读文档 | ✅ `git diff api.d.ts` |
| 发现"字段变可空了" | ❌ 完全发现不了 | ✅ 编译错误（`string` → `string \| null`） |
| 发现"类型变了" | ❌ 运行时才炸 | ✅ 编译错误 |
| 什么时候发现 | **上线后，用户发现** | **改完 3 秒内** |
| 能进 CI 吗 | 不能 | **能** |

**第四行要专门讲**：

> `string` 变成 `string | null` 是最阴险的一种变更。
>
> 后端觉得"我只是让这个字段变得更宽松了，不是破坏性变更"。**但前端 `q.author.display_name.slice(0, 10)` 会在 `null` 上炸。**
>
> 没有类型的时候，这种变更**完全无法被发现**，只能等某一条数据恰好是 null 的时候线上报错。
>
> 有类型的时候，tsc 会直接说 "Object is possibly 'null'"。
>
> **判据：可空性的变化是破坏性变更，尽管它看起来是"放宽"。**

### 6.5 契约漂移：给它一个名字

**醒目页**：

> **契约漂移（contract drift）：后端改了契约而前端不知道，或者前端假设了后端从未承诺的东西。**
>
> 它的性质：
> - **单向静默**——后端毫无感觉，前端毫无报错
> - **延迟暴露**——从改动到出问题可能隔几周
> - **责任模糊**——出了问题两边都觉得不是自己的锅
>
> **契约漂移是前后端分离的头号成本。** 开场说的那四条好处，每一条都以"契约不漂移"为前提。
>
> 治理它只有三条路，按有效性排序：
>
> | | 做法 | 有效性 |
> |---|---|---|
> | 1 | **生成类型 + CI 校验** | 高，且零维护成本 |
> | 2 | 契约测试（后端提供的响应必须符合 schema） | 高，但要写 → **第 9 次课** |
> | 3 | 人工同步（改了在群里说一声） | **接近于零** |
>
> 第 3 条不是玩笑——**这是绝大多数团队实际在做的事**，而且他们真心相信它有效。

### 6.6 课程主题落点：契约是给 AI 的规格说明书

**这一小节是本次课与课程主题的正式接点，请完整制作。**

**现场做一个 A/B 实验（两个提示词并排，两份输出并排）**：

**A 组提示词**：

> 给我写一个 TypeScript 函数，从 `/api/questions` 拉取问题列表并渲染成 HTML 列表，每项显示标题、作者名和回答数。

**B 组提示词**：

> 这是后端的 API 类型定义（附 `api.d.ts` 的相关片段）。请用 `openapi-fetch` 的 `api.GET` 写一个函数拉取问题列表并渲染，每项显示标题、作者名和回答数。必须通过 `tsc --noEmit`。

**对比输出**：

| | A 组（只有自然语言） | B 组（给了契约） |
|---|---|---|
| 字段名 | `q.author_name` / `q.authorName` / `q.author.name`——**猜的** | `q.author.display_name` ✅ |
| 响应结构 | 直接 `data.map`，**假设返回的是数组** | `data.items.map` ✅ |
| 回答数字段 | `q.answers_count` / `q.answerCount`——**猜的** | `q.reply_count` ✅ |
| 错误处理 | `catch(e => console.log(e))` | 用 `error` 分支 + `ErrorBody` 类型 |
| 能不能编译过 | ❌ | ✅ |

**然后给出判断（醒目页）**：

> **AI 写前端代码时，字段名是猜的。**
>
> 这不是它的缺陷，是**信息缺失**——它没有你的后端 schema，只能从对话上下文和训练数据里的常见命名习惯去推断。`author_name`、`authorName`、`author.name` 都是完全合理的猜测。
>
> 这和第 6 次课那个判断是同一句话：**AI 在"需要你的特定知识"的地方一定会犯错，而它不会告诉你它缺少这个知识。**
>
> 区别在于今天这个错误的性质：
>
> | | 第 6 次课：漏约束 | 今天：猜字段名 |
> |---|---|---|
> | 能不能靠更好的提示词解决 | 部分能（说明业务规则） | **完全能** |
> | 怎么解决 | 把业务规则写进提示词 | **把契约文件给它** |
>
> **判据：能用文件给的信息，不要用自然语言描述。**
>
> 自然语言描述会丢失精度（"回答数"到底叫什么）、会遗漏（可空性、格式约束）、会过时（你上次描述的是三周前的版本）。**`api.d.ts` 不会。**
>
> 这就是第 3 次课那句"契约先行是约束 AI 最有效的抓手"的完整含义：
>
> **契约不只是让 AI 写得更对，它让"写得对不对"这件事可以被机器判定。** A 组的输出要靠你读一遍才知道对不对；B 组的输出跑一次 `tsc` 就知道。
>
> **判据升级版：给 AI 的约束里，最有价值的是那些"能被自动检查"的约束。**

三层护栏（**第五次使用同一套方法**）：

| 层 | 做法 |
|---|---|
| **约定** | 让 AI 写前端代码时，必须把相关的 `api.d.ts` 片段贴给它 |
| **机械检查** | CI：① `npm run gen` 后 `git diff --exit-code`；② `tsc --noEmit` → **第 9 次课** |
| **定量兜底** | 契约测试：用 schemathesis 按 openapi.json 打一遍后端，验证响应真的符合契约 → **第 9 次课** |

### 材料

- **封面级素材**：6.4 的七行对照表，"上线后用户发现" vs "改完 3 秒内"两格分别标红/标绿。
- **封面级素材**：6.6 的 A/B 实验输出并排，猜错的字段名逐个标红。
- 截图：`undefined 回答` 的页面 + 空白的控制台（**两者同屏**，证明"没有任何报错"）。
- 截图：`tsc --noEmit` 精确列出两处错误的终端输出。
- 截图：`git diff src/api.d.ts` 的三行变更。
- 备用：A/B 实验的预录产物（AI 现场可能不稳定）。

---

## 七、前端 N+1 与"契约决定成本"

**约 10 分钟。**

### 7.1 量一次前端 N+1

打开 Network 面板，对比两种实现：

| 实现 | 请求数 | 总耗时（本机） | 总耗时（RTT=50ms，模拟真实网络） |
|---|---|---|---|
| 列表 + 每个问题单独查作者 | **21** | 320 ms | **1 300 ms** |
| 列表（`author` 已嵌套） | **1** | 45 ms | **95 ms** |

〔制作团队：用 Chrome DevTools 的网络限速（Slow 3G 或自定义 50ms 延迟）做第二列，**必须录屏**。〕

**和第 7 次课并排讲（做成一页）**：

| | 第 7 次课：后端 N+1 | 今天：前端 N+1 |
|---|---|---|
| 一次额外调用的成本 | 数据库往返，**0.3 ms** | HTTP 往返，**5–100 ms** |
| 21 次的总代价 | ~6 ms | **100–2000 ms** |
| 能不能靠索引解决 | ❌ | ❌ |
| 怎么发现 | SQL 计数器 | **Network 面板数请求数** |
| 怎么修 | `selectinload` | **让后端一次给全** |

> **同一个反模式，在越外层的调用上越贵。** 数据库往返是微秒到毫秒级，HTTP 往返是毫秒到百毫秒级。
>
> 判据：**"请求数"是前端最重要的性能指标，就像"SQL 条数"是后端最重要的一样。** 两者都不看耗时，先看次数。
>
> 而且第 7 次课那个思路可以直接搬过来：**把它变成一条会失败的检查。** Playwright 可以断言"打开列表页发出的请求数 ≤ 2"。**→ 第 9 次课。**

### 7.2 契约决定实现成本（**本单元核心**）

> 现在有个产品需求："列表页每条问题下面，显示最近 3 条回答的作者头像。"
>
> 前端会说：**"那你在 `QuestionOut` 里加个 `recent_answers` 就行了，很简单。"**

**把第 7 次课的数字搬出来算一下**：

| 契约长什么样 | 后端要做什么 | 代价 |
|---|---|---|
| 只有 `id, title` | 一条 SQL | 3 条 SQL，~100 行 |
| 加 `author` | `selectinload(author)` | +1 条 SQL |
| 加 `reply_count` | 聚合子查询 | +0 条（进主查询） |
| 加 `tags` | `selectinload(tags)` | +1 条 SQL |
| **加 `recent_answers`（每题前 3 条）** | **需要窗口函数或 LATERAL JOIN** | **查询复杂度跳一个台阶** |

> 最后一行值得展开：**"每个问题的前 N 条回答"在 SQL 里不是一个简单查询。**
>
> 用 `selectinload(Question.answers)` 会把**所有**回答拉回来（第 7 次课单元 5.6 那个 1847 行的教训），然后在 Python 里切前 3 条。
>
> 正确做法是 `ROW_NUMBER() OVER (PARTITION BY question_id ORDER BY created_at DESC)` 或者 PostgreSQL 的 `LATERAL JOIN`——**这是第 7 次课单元 8.3 判据表里"该放弃 ORM 写 SQL"的典型情形。**
>
> **前端的一句"加个字段就行"，对应后端一条难写、难测、难优化的查询。**

**关键判断（醒目页）**：

> **契约是前后端共同拥有的，不是前端点菜、后端做饭。**
>
> 谈契约的时候，两个问题必须同时问：
>
> 1. **这个字段前端真的需要吗？** 还是"顺便要了以后可能用得上"？
> 2. **这个字段的代价是多少？** 后端要把这个数字说出来，不要闷头实现。
>
> 判据：**一个契约变更，如果后端说不出它的查询代价，那它还没设计完。**

**三种折中方案（给判据，不展开）**：

| 方案 | 做法 | 什么时候用 |
|---|---|---|
| **字段裁剪** | `?fields=id,title` 或者分 `QuestionBrief`/`QuestionDetail` 两个 schema | 同一资源在不同页面需要的详略差别大 |
| **拆端点** | `/questions/{id}/recent-answers` 单独一个端点 | 这块数据不是每次都要，且可以异步加载 |
| **BFF** | 为这个前端专门做一层聚合 API | 多端且各端需求差异大。**小团队不要上** |

> 本课程的建议：**优先"分两个 schema"**（`QuestionBrief` 列表用、`QuestionDetail` 详情用）。这是第 3 次课 In/Out schema 分离的自然延伸，**零额外架构成本**。
>
> 什么时候上 BFF：**当你有三个以上的客户端，且它们要的数据形状明显不同的时候。** 不是"因为大厂都有"。

### 7.3 顺手回收 openapi 的另一个用处

```bash
curl -s localhost:8000/openapi.json | \
  jq '.paths | to_entries[] | {path: .key, methods: (.value | keys)}'
```

> 契约文件还能回答一个常被忽略的问题：**"我们一共有多少个端点？哪些没人用？"**
>
> 把 openapi.json 里的端点列表和前端 `api.GET/POST` 的调用点对比，**没被调用的端点就是候选的删除对象**。
>
> 判据：**API 只增不减会变成一片沼泽。** 定期对账一次。〔C 档卡。〕

### 材料

- **封面级素材**：7.1 的前后端 N+1 对照表（五行）。
- 录屏：Network 面板里 21 个请求瀑布图 vs 1 个请求（限速 50ms 下）。
- 高光图：7.2 的"契约字段 → 后端代价"五行表，最后一行标红。
- 高光图：三种折中方案判据表。

---

## 八、什么时候不该分离；破坏性变更怎么发布

**约 6 分钟。**

### 8.1 不该分离的四种情况

**醒目页**：

| 情况 | 为什么不该分离 |
|---|---|
| **内部工具 / 管理后台** | 用户是同事，不需要极致体验；SSR 一个人两天能做完，分离要两套工程化 |
| **内容型站点（博客、文档、商品页）** | SEO 和首屏时间是核心指标，**CSR 在这两点上先天劣势** |
| **团队只有一两个人** | "团队并行"这条好处不存在，只剩下成本 |
| **表单密集的业务系统** | 第 5 次课那套 PRG + 服务端回填，代码量是 SPA 的三分之一 |

> **判据：分离的四条好处（多端、独立部署、团队并行、CDN），你占几条？**
>
> 一条都不占就别分离。占两条以上，分离是划算的。
>
> 还有一条经验：**真实项目常常是混合的。** 用户端 SPA + 管理后台 SSR，是非常常见也非常合理的组合。**不要为了架构的"统一"去做不划算的事。**
>
> 我们的项目现在就是混合的——第 5 次课那套 HTML 页面**保留**着。它们共享同一套业务层，各自服务不同场景。**这不是技术债，这是一个决定。** 写进 `decisions.md`。

### 8.2 什么是破坏性变更（判据表）

| 变更 | 破坏性？ | 为什么 |
|---|---|---|
| 新增一个可选字段 | ❌ 不是 | 老客户端忽略它 |
| 新增一个端点 | ❌ 不是 | —— |
| 放宽校验（`min_length` 5→3） | ❌ 不是 | 原来能过的还能过 |
| **删字段 / 改字段名** | ✅ **是** | 老客户端拿到 `undefined` |
| **字段变可空** | ✅ **是** | 老客户端可能在 null 上崩 |
| **改字段类型**（`int` → `string`） | ✅ **是** | —— |
| **收紧校验**（`min_length` 3→5） | ✅ **是** | 原来能过的现在 422 |
| **改错误 `code` 的含义** | ✅ **是** | 前端按 code 分支处理 |
| 新增必填请求字段 | ✅ **是** | 老客户端的请求全部 422 |
| 改 HTTP 状态码（200→204） | ✅ **是** | —— |

> 请注意第 2、5 行的位置：**"加个可选字段"是安全的，"让一个字段可空"是危险的。** 这两个听起来很像，性质完全相反。

### 8.3 破坏性变更怎么发布 —— 又是扩展-收缩

**醒目页，这是本次课最漂亮的一个呼应**：

> 第 7 次课讲数据库迁移时，我们学了**扩展-收缩**：
>
> ```
> 加新列 → 双写 → 切读到新列 → 观察 → 删旧列
> ```
>
> **API 的破坏性变更，用的是同一个模式：**
>
> ```
> 加新字段 → 两个字段都返回 → 前端切到新字段 → 观察 → 删旧字段
> ```

具体到 `answer_count` → `reply_count`：

| 步骤 | 后端 | 前端 | 能回滚吗 |
|---|---|---|---|
| 1 | 加 `reply_count`，**同时保留 `answer_count`** | 不动 | ✅ |
| 2 | 不动 | 切到 `reply_count` 并发版 | ✅ |
| 3 | 观察一两周，确认没有客户端在读 `answer_count` | —— | ✅ |
| 4 | 删 `answer_count` | —— | ❌ 但风险已验证 |

> **同一个模式，在数据库层和 API 层各出现一次。** 这不是巧合——
>
> **判据：任何"有独立生命周期的消费者"的地方，破坏性变更都要用扩展-收缩。**
>
> 数据库的消费者是"运行中的旧版应用"，API 的消费者是"用户浏览器里缓存的旧版前端"。**两者都不在你的控制之下，都不能假设它们会同时更新。**
>
> 尤其是移动端 App：**用户可能三个月不更新。** 这时候扩展期不是两周，是两年。

**API 版本化的三种做法（给结论，不展开）**：

| 做法 | 例子 | 评价 |
|---|---|---|
| URL 路径 | `/v1/questions` | 最直观，最常见。**代价：v1/v2 两套代码并存** |
| 请求头 | `Accept: application/vnd.api.v2+json` | 更"规范"，但调试麻烦，缓存麻烦 |
| **不版本化，只做兼容** | 永远扩展-收缩，永不破坏 | **小团队首选** |

> **本课程的判据：先努力做到"永不破坏"。** 版本化的成本（两套代码、两套测试、两套文档）通常高于"多留一个废弃字段半年"的成本。
>
> 真的要版本化时，用 URL 路径，并且**给旧版本一个明确的下线日期**。没有下线日期的 v1 会永远活着。

### 材料

- 高光图：8.1 的四种不该分离的情况。
- **高光图**：8.2 破坏性变更判据表（十行），破坏性的那些用红色。
- **封面级素材**：8.3 的"扩展-收缩在两层的同构图"——上半是第 7 次课的数据库版本，下半是今天的 API 版本，中间用箭头标"同一个模式"。

---

## 九、C 档结论卡

**约 4 分钟。时间不够整体跳过。**

### 9.1 渲染策略对照

| 策略 | 谁渲染 HTML | 首屏 | SEO | 交互后 | 适合 |
|---|---|---|---|---|---|
| **SSR**（第 5 次课） | 服务器，每次请求 | 快 | 好 | 整页刷新 | 表单系统、管理后台 |
| **CSR / SPA**（今天） | 浏览器 | 慢（要等 JS + 数据） | 差 | 局部更新 | 应用型产品、多端 |
| **SSG** | 构建时预生成 | 最快 | 好 | 局部更新 | 文档、博客、营销页 |
| **SSR + Hydration**（Next/Nuxt） | 服务器首屏 + 浏览器接管 | 快 | 好 | 局部更新 | 两者都要，**代价是复杂度** |

> **判据：先问"首屏和 SEO 重要吗"。** 不重要就 CSR，最简单。重要且内容不常变就 SSG。都重要且内容动态，才考虑第四种——**它的复杂度是前三种的好几倍，不要因为"看起来先进"选它。**

### 9.2 契约技术跨栈对照

| 能力 | REST + OpenAPI（本课程） | GraphQL | tRPC | gRPC |
|---|---|---|---|---|
| 契约来源 | 后端代码生成 | Schema 优先 | **后端 TS 类型直接复用** | `.proto` 文件 |
| 前端类型 | 生成 | 生成 | **不用生成，直接 import** | 生成 |
| 字段裁剪 | 后端定 schema | **前端按需查询** | 后端定 | 后端定 |
| 前端 N+1 | 要靠后端设计好 | **一次查询解决** | 同 REST | 同 REST |
| 后端 N+1 | 可控 | **更容易踩**（resolver 层层展开） | 可控 | 可控 |
| 跨语言 | ✅ | ✅ | ❌ 仅 TS | ✅ |
| 浏览器直连 | ✅ | ✅ | ✅ | 需要 grpc-web |
| 复杂度 | 低 | **高** | 低（但锁 TS） | 中 |

> 三句话：
>
> - **tRPC 是"不分离的分离"**——前后端都是 TypeScript，类型直接共享，连生成这一步都省了。**代价是锁死技术栈。**
> - **GraphQL 把"契约决定成本"的问题转移了**——前端能按需取，但后端的 resolver 更容易产生 N+1（第 7 次课那个问题在这里被放大）。
> - **本课程选 REST + OpenAPI 的理由**：跨语言、工具成熟、契约是生成的、**而且 FastAPI 白送**。

### 9.3 一句话结论卡

| 问题 | 结论 | 展开处 |
|---|---|---|
| `api.d.ts` 要不要进仓库 | **要**，且加 `// GENERATED` 头，CI 校验一致性 | 单元 4.6 |
| 前端怎么带身份 | Cookie（`HttpOnly`）还是 Bearer token，各有取舍 | **第 14 次课** |
| 分离架构下的 CSRF | Cookie 方案需要防；Bearer 方案基本不需要 | **第 15 次课** |
| 前端构建产物部署 | 静态文件走 CDN / nginx；API 走反向代理同源 → **可顺便消除 CORS** | **第 12、16 次课** |
| 契约测试工具 | schemathesis 按 openapi.json 自动生成用例打后端 | **第 9 次课** |
| 前端请求数怎么进 CI | Playwright 断言页面加载的请求数 | **第 9 次课** |
| 未使用端点的清理 | openapi.json 端点列表 vs 前端调用点对账 | 单元 7.3 |
| Mock：前端不等后端 | 用 openapi.json 起一个 mock server（prism），**契约先行的完整形态** | 自读 |
| 分页从 offset 换 keyset | 是破坏性变更（响应结构变），要走扩展-收缩 | **第 11 次课** |

---

## 十、作业与欠账

**约 6 分钟。**

### 10.1 作业一：给 M2 加一个类型安全的前端（主线）

**功能要求**（三个页面，不要更多）：

| # | 页面 | 要求 |
|---|---|---|
| 1 | 列表页 | 分页、排序（用 `Literal` 那三个值）、**四态齐全** |
| 2 | 详情页 | 问题 + 回答列表；**404 要有专门的界面**，不能显示"错误" |
| 3 | 发帖页 | 提交、422 字段级错误回填、成功后跳转详情页 |

**结构要求（硬性）**：

| # | 要求 | 自检 |
|---|---|---|
| 4 | `src/api.d.ts` 由 `npm run gen` 生成，**文件头有 GENERATED 标记，无手改痕迹** | `npm run gen && git diff --exit-code src/api.d.ts` |
| 5 | `npm run check`（`tsc --noEmit`）**零错误，零 `any`** | grep `any` |
| 6 | 所有请求经 `openapi-fetch`，**前端代码里零处硬编码 URL 字符串** | grep `fetch(` 和 `"/questions` |
| 7 | 所有错误显示都带 `request_id` | 截图 |
| 8 | 前端**不重复定义**任何校验规则（可以从契约提取） | 代码审阅 |
| 9 | 渲染用户内容一律 `textContent`，**零处 `innerHTML` 接用户数据** | grep |
| 10 | 列表页加载的 HTTP 请求数 ≤ 2 | Network 面板截图 |

**交付物**：

- `web/` 目录（含 `package.json`、`tsconfig.json`、`vite.config.ts`）；
- `README.md` 增加前端启动步骤；
- `docs/decisions.md` **新增至少三条**，必须包含：
  - 为什么保留第 5 次课的 SSR 页面（或者为什么删掉）
  - 前端校验规则的来源与同步机制
  - 列表页需要哪些字段，以及每个字段的后端代价

### 10.2 作业二：契约变更影响面报告（B 档，必交）

选一次**破坏性变更**（建议：把 `QuestionDetail.body` 改名为 `content`，并把 `author` 变为可空），完整走一遍，提交：

**第一部分：两种世界的对照表**

| 检查手段 | 无类型生成时发现了吗 | 有类型生成时发现了吗 | 耗时 |
|---|---|---|---|
| 浏览器控制台 | | | |
| 后端测试 | | | |
| `grep` | | | |
| `tsc --noEmit` | | | |

**第二部分：必答四问**

1. `author` 变可空这一项，**无类型生成时能被发现吗？** 你是怎么验证这个结论的？
2. `git diff src/api.d.ts` 一共列出了几处变化？其中几处会导致编译错误，几处不会？**不会的那些危险吗？**
3. 按单元 8.3 的扩展-收缩，这次变更应该分几步发布？**每一步的回滚方案是什么？**
4. 如果你的客户端里有一个三个月不更新的 App，扩展期应该多长？这会改变你的决定吗？

### 10.3 作业三：AI 前端对照实验（**本次课的课程主题作业**）

**第一部分：A/B 实验（必做）**

1. 用两组提示词各请 AI 写一个"详情页数据加载与渲染"的函数：

   **A 组**（只给自然语言）：

   > 写一个 TypeScript 函数，根据 URL 里的 id 参数从后端拉取问题详情并渲染。要显示标题、正文、作者名、回答列表（每条显示作者名和内容）。

   **B 组**（给契约）：

   > 附件是后端的 `api.d.ts`。用 `openapi-fetch` 的 `api.GET` 写一个函数，根据 URL 里的 id 拉取问题详情并渲染，显示标题、正文、作者名、回答列表。必须通过 `tsc --noEmit`，不许用 `any`。

2. **原样保存两份输出。**

3. 填表：

   | 对照项 | A 组 | B 组 |
   |---|---|---|
   | 字段名猜对了几个 / 共几个 | | |
   | 响应结构假设对了吗 | | |
   | 可空字段处理了吗 | | |
   | 错误处理用了 `ErrorBody` 吗 | | |
   | `tsc --noEmit` 通过吗 | | |
   | 你要改几行才能用 | | |

**第二部分：必答四问（评分重点）**

| 问题 | 你的回答 |
|---|---|
| A 组猜错的字段名，**如果你没发现直接上线，用户会看到什么？** | |
| A 组的错误"能被什么检查发现"？B 组呢？ | |
| 为什么说"给文件比给描述好"？**用你这次实验的具体数据支撑。** | |
| 单元 6.6 说"最有价值的约束是能被自动检查的约束"。在你的项目里，**还有哪些约束目前只存在于文档/口头，能不能变成可自动检查的？** 列举至少两条并说明怎么做 | |

> **最后一问是本次作业的核心。** 它要你把本次课的方法迁移到别的地方去——比如"错误码必须在枚举里"、"每个端点必须有 tags"、"迁移脚本必须有 downgrade"。这些现在都是口头约定，**它们都可以变成检查**。第 9 次课你会真的写出来。

### 10.4 本次课新增的欠账登记

| 欠账 | 何时还 |
|---|---|
| CORS 的生产解法与中间件位置 | **第 12 次课** |
| `npm run gen` 一致性校验进 CI | **第 9 次课** |
| `tsc --noEmit` 进 CI | **第 9 次课** |
| 契约测试（schemathesis） | **第 9 次课** |
| 前端请求数断言（Playwright） | **第 9 次课** |
| 前端怎么携带身份（cookie vs token） | **第 14 次课** |
| 分离架构下的 CSRF | **第 15 次课** |
| `innerHTML` / XSS 完整处理 | **第 15 次课** |
| 前端构建产物的部署与同源反代 | **第 12、16 次课** |
| `total` 那条 `count(*)` 的代价 | **第 11 次课** |
| keyset 分页对契约的破坏性 | **第 11 次课** |
| `recent_answers` 类需求的窗口函数写法 | 第 11 次课 |
| Mock server 让前端不等后端 | 课后自读 |
| 未使用端点的对账 | 课后自读 |

---

## 十一、素材清单与制作说明

### 必需素材

| 素材 | 说明 |
|---|---|
| tag `v8-broken` | 起始版：AI 产出的前端，含四个问题。**四个演示必须稳定复现** |
| tag `v8-proxy` | 单元 3 结束：Vite proxy 配好，能跑通 |
| tag `v8-typed` | 单元 4 结束：类型生成 + openapi-fetch |
| tag `v8-states` | 单元 5 结束：四态 + 错误契约对接 |
| tag `v8-final` | 作业参考交付状态 |
| `web/` 脚手架 | Vite + vanilla-ts 最小模板，**`npm i && npm run dev` 一条命令起得来**；三个 OS 各验证一次 |
| `scripts/gen-constraints.mjs` | 从 openapi.json 提取校验约束生成 `constraints.ts`（单元 5.4） |
| **封面级 A** | "编译期 vs 运行期"核心句，单独一页 |
| **封面级 B** | `Pydantic → openapi.json → api.d.ts → tsc` 四段链路图 |
| **封面级 C** | 六道护栏累加表，第六行"编译期"异色 |
| **封面级 D** | 单元 6.4 契约变更七行对照表 |
| **封面级 E** | 单元 6.6 A/B 实验输出并排，猜错字段名标红 |
| **封面级 F** | request_id 四次课闭环图 + 现场截图 |
| **封面级 G** | 单元 7.1 前后端 N+1 五行对照表 |
| **封面级 H** | 单元 8.3 扩展-收缩在数据库层与 API 层的同构图 |
| 高光图 I | 第 5 次课对照表加第三列（同风格可叠加） |
| 高光图 J | 四态定义表 |
| 高光图 K | 前端校验 vs 后端校验对照表 |
| 高光图 L | "默认值是否安全"四行表（Jinja2 / innerHTML / textContent / React） |
| 高光图 M | 破坏性变更判据表（十行） |
| 高光图 N | 契约字段 → 后端代价 五行表 |
| 截图 | CORS 报错原文 |
| 截图 | `git diff --stat` 后端只改 10 行 |
| 截图 | `undefined 回答` 的页面 **+ 空白控制台同屏** |
| 截图 | 编辑器里 `q.auther` 红波浪线 |
| 截图 | `tsc --noEmit` 精确列出两处错误 |
| 截图 | `git diff src/api.d.ts` |
| 截图 | 四种状态界面各一张 |
| 截图 | 错误态界面（含编号）**+ 服务端 grep 结果同屏** |
| 录屏 | Network 面板 21 请求 vs 1 请求（限速 50ms） |

### 可后补

- 跨栈对照表、渲染策略表、一句话结论卡（纯文字）。
- 前端样式（给一份极简 CSS 即可，**不要在课上讲样式**）。

### 备用材料

| 风险 | 备用方案 |
|---|---|
| **`npm i` 在教室网络下很慢**（最高风险） | 课前发放含 `node_modules` 的压缩包；或提供离线 npm 缓存；**或全程用预装好的容器镜像** |
| AI 现场调用失败（单元 6.6 A/B 实验） | 准备预先生成并验证的两份输出，标注"预录产物"。**A 组那份要真实体现"猜字段名"**，不要人工编造 |
| 学生 Node 版本不一致导致 Vite 起不来 | 在 `package.json` 里锁 `engines`；提供 `.nvmrc`；备一份 CDN 版（`<script type="module">` + importmap）的降级方案 |
| `openapi-typescript` 版本差异导致生成格式不同 | 锁定版本号；**底稿里的 `api.d.ts` 示例要标注生成版本** |
| 后端 openapi.json 与底稿示例不一致 | 提供 `v8-*` tag 对应的 openapi.json 快照文件，可离线生成类型 |
| 时间超支 | 按单元〇的压缩顺序；单元 5 的页面实现有成品代码 `web/src/*.ts`，课上只讲三态与错误对接 |

### 环境与运行条件

延用前序环境。**新增**：Node.js 20+、npm。

**演示开始时的初始状态**：后端在 tag `v8-broken` 且已启动（`localhost:8000`，数据已 seed）；`web/` 目录已 `npm i` 完成；浏览器开两个标签（前端 `localhost:5173`、后端 `/docs`）；一个终端跑 `npm run dev`，一个终端准备 grep 日志，一个终端在后端项目里。

**复位方式**：`git checkout v8-broken -- web/ app/ && make reset-db`。

---

## 十二、与前后课的衔接

**本次课回收的前序埋点**：

| 来源 | 埋点 | 回收位置 |
|---|---|---|
| 第 3 次课 | 契约先行是约束 AI 最有效的抓手 | **单元 4、6.6**（升级为"能被机器检查的约束"） |
| 第 3 次课 | `response_model` / In-Out schema 分离 | 单元 4.1（它就是契约本身）、单元 7.2（Brief/Detail 分离） |
| 第 3 次课 | 依赖稳定标识不依赖文案 | 单元 5.4（`error.code` 判断，**第四次出现**） |
| 第 3 次课 | 读懂 422 结构 | 单元 5.4（前端消费 `detail.fields`） |
| 第 4 次课 | 统一错误体 `code/message/detail/request_id` | **单元 5.3**（终于有了消费者） |
| 第 4 次课 | request_id 设计 | **单元 5.3 完整闭环** |
| 第 5 次课 | JSON API vs HTML 表单对照表 | **单元 3.1**（加第三列） |
| 第 5 次课 | HTML 表单被迫手写校验的妥协 | **单元 5.4 还清** |
| 第 5 次课 | Jinja2 自动转义 / `\| safe` | 单元 5.5（前端默认值是反的） |
| 第 5 次课 | 开发环境掩盖生产问题（多 worker） | 单元 3.3（proxy 掩盖 CORS，**第三次出现**） |
| 第 5 次课 | CORS 必须最外层 | 单元 3.3 轻触，**留给第 12 次课** |
| 第 6 次课 | AI 在"需要你的特定知识"处一定犯错 | **单元 6.6**（同一句话，今天是字段名） |
| 第 7 次课 | N+1 是"次数"问题不是"慢查询"问题 | **单元 7.1**（前端版本，成本高 100 倍） |
| 第 7 次课 | `Literal` 排序白名单 | 单元 4.2（变成前端自动补全） |
| 第 7 次课 | Out schema 决定加载策略 | **单元 7.2**（契约决定后端成本，带数字） |
| 第 7 次课 | 扩展-收缩发布模式 | **单元 8.3**（同一模式用在 API 层） |
| 第 7 次课 | 分层的回报在被修改时 | 单元 3.2（第三次兑现：加客户端，后端改 10 行） |
| 第 5–7 次课 | 五道结构性护栏 | 单元 4.5（第六道，**第一道在编译期**） |
| 第 5–7 次课 | "约定 + 机械检查 + 定量兜底" | 单元 6.6（**第五次使用同一套方法**） |

**本次课埋下、后面必须回引的五处**（请在课件中明显标记）：

- **单元 4.6 的 `npm run gen` + `git diff --exit-code`** → 第 9 次课写进 CI，是"契约不漂移"的机械保证；
- **单元 6.6 作业三第四问"还有哪些约定能变成检查"** → 第 9 次课直接拿学生的答案来实现；
- **单元 3.3 的 proxy 障眼法** → 第 12 次课关掉它，正面处理 CORS 与中间件顺序；
- **单元 7.2 的"契约决定成本"** → 第 11 次课优化那条 `count(*)` 和 `recent_answers` 时回到这一页；
- **单元 8.3 的扩展-收缩** → 第 16 次课零停机发布时第三次出现（数据库 → API → 部署）。

**本次课不承担、请勿提前引入**：测试与 CI（第 9 次课）、缓存/keyset/全文检索（第 11 次课）、CORS 完整解法（第 12 次课）、认证与 token 存储（第 14 次课）、XSS/CSRF（第 15 次课）、部署与 CDN（第 16 次课）、前端框架与状态管理（不讲）、SSR 框架（C 档卡）。

**给第 9 次课的提示**：

本次课结束时，项目已经积累了**一批"应该检查但目前靠人记得"的约定**，它们分布在前八次课：

| 来源 | 约定 | 检查方式（第 9 次课实现） |
|---|---|---|
| 第 3 次课 | 端点必须有 `response_model` | AST 扫描或 openapi.json 校验 |
| 第 4 次课 | `services/` 不许 `import fastapi` | grep |
| 第 5 次课 | `async def` 里不许有阻塞调用 | AST 扫描 |
| 第 5 次课 | 模板里不许 `\| safe` | grep |
| 第 6 次课 | 所有表有主键、所有外键有索引 | 查 `pg_catalog` |
| 第 7 次课 | `.commit()` 只在 `deps.py` | grep |
| 第 7 次课 | 迁移能 upgrade/downgrade（**在带数据快照上**） | CI step |
| 第 7 次课 | 列表端点 SQL 条数 ≤ 3 | 用 `sqlcount.py` 写成断言 |
| **第 8 次课** | **`api.d.ts` 与后端一致** | `gen` + `git diff --exit-code` |
| **第 8 次课** | **`tsc --noEmit` 零错误** | CI step |
| **第 8 次课** | **列表页请求数 ≤ 2** | Playwright 断言 |

**建议第 9 次课的开场就用这张表**：八次课积累了十一条纪律，**每一条今天都还靠"我记得"**。第 9 次课的任务就是把它们一条条变成会失败的东西——这正是本课程"把纪律变成结构"这条主线的总收口。

第 7 次课的 `sqlcount.py` 和本次课的 `npm run gen` 是两个最现成的抓手，**它们已经是可执行的代码，只差一个 `assert` 和一个 CI 文件。**