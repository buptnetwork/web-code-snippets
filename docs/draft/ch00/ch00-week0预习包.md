# 《Week 0 预习包》

## 第 1 章｜开发环境（本机安装）

### 1.1 装完以后应该是什么样

你需要在自己电脑上直接装五样东西：

```
你的电脑
├── Git                  版本控制，提交作业
├── Python 3.12+  + uv   后端运行环境与包管理
├── Node.js 20 LTS(或22) + npm   前端构建工具链
├── PostgreSQL 16/17    数据库（含命令行工具 psql）
└── AI Coding Agent (Qoder / Codex / Claude Code / OpenCode)     AI IDE
```

### 1.2 安装清单与验证方式

**安装方法请自行搜索官方文档或可靠教程**（这本身是本课要求的基本能力）。下面只给**目标版本、推荐路径、验证命令、以及最容易踩的坑**。

| # | 组件 | 版本要求 | 推荐安装路径 | 验证命令 |
|---|---|---|---|---|
| 1 | Git | 2.30+ | Windows: Git for Windows；macOS: `brew install git` 或 Xcode CLT；Linux: 包管理器 | `git --version` |
| 2 | Python | **3.12 或 3.13** | 官方安装包；或用 `uv python install 3.12` 直接由 uv 装 | `python --version` |
| 3 | uv | 最新 | 官方一键脚本（Astral 官网）；也可 `pipx install uv` | `uv --version` |
| 4 | Node.js | **20 LTS 或 22 LTS** | 强烈建议用版本管理器：Windows 用 `nvm-windows` 或 `fnm`，macOS/Linux 用 `nvm` 或 `fnm`；不建议直装 | `node -v` / `npm -v` |
| 5 | PostgreSQL | **16 或 17** | Windows: EDB 官方安装包（**记住勾选 Command Line Tools**）；macOS: Postgres.app 或 `brew install postgresql@17`；Linux: 官方 apt 仓库 | `psql --version` |
| 6 | AI Coding Agent (Qoder / Codex / Claude Code / OpenCode)  | 最新 | 官网 | 任选一种 |


### 2.8 Git 最小必需集

- `clone` / `status` / `add` / `commit` / `push` / `pull`
- 分支：`branch` / `switch` / `merge`；知道什么是 PR（本课程后期会做互审）
- `.gitignore` 的作用；**为什么 `.env` 与密钥绝不能提交**（第 4 次课会回收这一点）
- 写出有意义的 commit message（不要 `update`、`fix`、`111`）

---

## 第 3 章｜Python 必需集（约 3 小时）

**只学下面这些，够用即止。** 每项后面标注了它在本课程中的用途——这决定了你该学到什么深度。

| # | 主题 | 深度要求 | 在本课程中的用途 |
|---|---|---|---|
| 1 | 虚拟环境与包管理概念 | 知道"项目隔离"是什么意思，会用 `uv run` | 全程 |
| 2 | 基本语法、f-string、真值判断 | 熟练 | 全程 |
| 3 | list / dict / set 与推导式 | 熟练 | 数据整理 |
| 4 | 函数：默认参数、`*args/**kwargs`、关键字参数 | 读懂 | 框架回调与依赖签名 |
| 5 | **类型注解**：`int/str/list[str]/dict[str,int]/Optional/`\|`None` | **重点，能自己写** | Pydantic 模型、FastAPI 参数（第 3 次课） |
| 6 | 类：属性、方法、`__init__`、继承 | 会写简单类 | ORM 模型（第 7 次课） |
| 7 | `dataclass` | 读懂 | 理解 Pydantic 的思路 |
| 8 | 异常：`try/except/raise`、自定义异常类 | 能写 | 统一错误契约（第 4 次课） |
| 9 | **装饰器**：会用 `@xxx`，**能读懂**一个简单装饰器的实现 | **重点** | 路由注册的"魔法"（第 3 次课） |
| 10 | 上下文管理器：`with` 的作用 | 会用，知道它保证了什么 | Session 生命周期、`yield` 依赖（第 4、7 次课） |
| 11 | `async def` / `await` 的**语法形态** | 只要认得出、会照着写；**不要求理解事件循环** | 异步端点（第 5 次课会讲原理） |
| 12 | 模块与包：`import`、`from ... import`、`__init__.py` | 会组织多文件 | 分层目录（第 4 次课） |
| 13 | 生成器与 `yield` | 认得出 | `yield` 依赖 |

**明确不需要**：元类、描述符、多重继承与 MRO、`__slots__`、GIL 细节、协程内部实现、迭代器协议实现。

**自测**：`warmup/python_quiz.md`，15 题，目标 ≥80%。答案在 `warmup/python_quiz_answer.md`，**做完再看**。

**重点练习（必做，会在第 3 次课用到）**：读懂并解释下面这段代码——它是 FastAPI 路由装饰器的极简原型。

```python
ROUTES = {}

def route(path):
    def decorator(func):
        ROUTES[path] = func
        return func
    return decorator

@route("/hello")
def hello():
    return "hi"

print(ROUTES)          # 这里打印出什么？
print(hello())         # 这里还能正常调用吗？为什么？
```

要求写出三句话：① `ROUTES` 里存了什么 ② 装饰器在什么时机执行 ③ 如果 `decorator` 里不写 `return func` 会发生什么。

---

## 第 4 章｜JavaScript 必需集（约 2.5 小时）

| # | 主题 | 深度要求 | 用途 |
|---|---|---|---|
| 1 | `let/const`，不用 `var` | 熟练 | 全程 |
| 2 | 箭头函数 | 熟练 | React 事件与回调 |
| 3 | 模板字符串 | 熟练 | 拼接 |
| 4 | 解构（对象/数组）与默认值 | **熟练** | React props、hooks 返回值 |
| 5 | 展开运算符 `...` | **熟练** | **不可变更新**（第 11 次课重点） |
| 6 | 数组方法：`map / filter / find / reduce / sort / some / every` | **`map` 与 `filter` 必须熟练** | 列表渲染 |
| 7 | 对象与 JSON、`JSON.parse/stringify` | 熟练 | 接口数据 |
| 8 | 可选链 `?.` 与空值合并 `??` | 会用 | 处理可能缺失的数据 |
| 9 | 模块：`import/export`（含 default 与命名导出） | **熟练** | 第 10 次课重点 |
| 10 | Promise 与 `async/await`、`try/catch` | **熟练** | `fetch` 请求（第 12 次课） |
| 11 | `fetch` 基本用法 | 会照着写 | 第 2、12 次课 |
| 12 | 闭包：知道"函数记住了它定义时的变量" | 概念清楚即可 | 第 12 次课闭包陷阱 |
| 13 | 相等判断：为什么用 `===` | 知道 | 避免踩坑 |

**明确不需要**：`class` 与继承、`this` 的复杂绑定规则、原型链、`var` 提升、Generator、装饰器提案、jQuery。

**自测**：`warmup/js_quiz.md`，15 题，目标 ≥80%。

**重点练习（必做，第 11 次课会回收）**：不修改原数组/原对象，写出四个操作。

```js
const posts = [
  { id: 1, title: "A", votes: 3 },
  { id: 2, title: "B", votes: 7 },
];

// 1. 追加一条 { id: 3, title: "C", votes: 0 }，得到新数组
// 2. 把 id 为 2 的 votes 改成 8，得到新数组
// 3. 删除 id 为 1 的那条，得到新数组
// 4. 按 votes 降序排序，得到新数组（注意 sort 会原地修改！）
```

写完后回答一句话：**为什么 React 要求这样做，而不是直接改？**（不会答没关系，第 11 次课讲；带着问题来。）

---

## 第 5 章｜HTML / CSS（约 2 小时，B 档：不设门槛测试）

**本课程不考 CSS 布局与视觉设计能力**，并会提供统一样式基线。这里只要求"看得懂、改得动"。

**HTML 需要认识**：文档基本结构；`div/span/p/h1~h6/ul/li/a/img/table`；**语义标签** `header/nav/main/section/article/footer`；**表单全套** `form/input(各 type)/textarea/select/option/label/button`，以及 `name`、`value`、`action`、`method`、`required` 的作用。

**CSS 需要认识**：如何引入样式；选择器（标签/类/id/后代）；优先级的粗略概念；盒模型（`margin/border/padding/content`、`box-sizing`）；`display` 常用值；Flex 的五个属性（`display:flex`、`flex-direction`、`justify-content`、`align-items`、`gap`）；一个媒体查询的写法。

**任务**：临摹 `warmup/mockups/` 下的 3 个页面（列表页、详情页、表单页）。允许用 AI 生成，但**必须逐行注释你不理解的地方**，并把不理解的点列成清单提交——这份清单比页面本身重要。

---

## 第 6 章｜HTTP 初识与 DevTools（约 1.5 小时）

这一章是第 1、2 次课的直接基础，**投入产出比最高**。

**需要知道**：

1. **URL 的构成**：`https://host:port/path?query#fragment`，各段谁来解析、`#fragment` 会不会发到服务器。
2. **一次请求/响应各四部分**：请求行（方法/路径/版本）、请求头、空行、请求体；状态行、响应头、空行、响应体。
3. **常见方法**：`GET/POST/PUT/PATCH/DELETE` 分别用来做什么。
4. **状态码大类**：2xx/3xx/4xx/5xx 各代表什么；认识 `200/201/204/301/302/303/400/401/403/404/409/422/500`。
5. **常见头**：`Content-Type`、`Accept`、`Cookie`、`Set-Cookie`、`Authorization`、`Cache-Control`、`Location`。
6. **DevTools Network 面板会做五件事**：看某个请求的状态码、看请求头与响应头、看请求载荷与响应体、看耗时、勾选 Disable cache 并区分"从缓存来"和"从服务器来"。

**任务（必做）**：打开任意一个你常用的网站，在 Network 面板中完成——

1. 找出**第一个** HTML 文档请求，记录：方法、状态码、`Content-Type`。
2. 找出一个返回 JSON 的请求，把它的响应体前 5 行抄下来。
3. 找出一个从缓存加载的资源，记录它的 `Cache-Control` 与 Size 列显示的内容。
4. 找出一个设置了 Cookie 的响应，记录 `Set-Cookie` 里出现的属性名（不要抄值）。
5. 用一句话描述：这个页面加载共发出多少个请求，最慢的是哪一个。

提交这 5 条记录（截图 + 文字）。

**自测**：`warmup/http_quiz.md`，10 题。


---

## 附录 A｜参考资料（只列必要的，按顺序读）

| 主题 | 资料 | 范围 |
|---|---|---|
| Python 类型注解 | Python 官方文档 typing 入门章节 | 只看基础类型与 `Optional` |
| Python 装饰器 | 任一可靠教程 | 只需理解"函数作为参数返回函数" |
| JS 现代语法 | MDN JavaScript 指南 | 解构、展开、模块、Promise 四节 |
| HTTP | MDN《HTTP 概述》《HTTP 消息》《HTTP 状态码》 | 全读，共约 40 分钟 |
| DevTools | Chrome DevTools 官方文档 Network 面板章节 | 全读 |
| Git | 任一入门教程 | 只到分支与 PR |
