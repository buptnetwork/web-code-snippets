# 第 11 课 · web

用 React 19 + TypeScript 重写第 10 课的问答页面：组件与 props、`useState`、事件与快照、受控输入、父子通信、列表 key，以及只在本地记录结果的创建表单。可独立安装、运行、构建与自检，不导入第 10 课源码，**不依赖后端**。

配套课件：`pages/ch05/11.md`（正文）与 `pages/ch05/11-reference.md`（阶段入口、机制源码、完整表单与 App）。

## 前置条件

- Node 22.13+（低于 23，本课实测 22.14.0）与 npm 10.9.2，见 `package.json` 的 `engines`
- 只有浏览器自检需要：本机安装的 **Google Chrome**。`playwright-core` 不会自动下载浏览器
- 不需要数据库、后端、`.env` 或代理

## 快速开始

在本目录（`snippets/ch05/lesson-11/web/`）执行，不在 Slidev 根工程：

```bash
npm ci          # 1. 按 package-lock.json 重建 node_modules
npm run dev     # 2. http://127.0.0.1:5181 ，Ctrl+C 停止
```

端口是 5181／4181，与第 10 课的 5173／4173 错开，两课可以同时运行。

## 阶段入口

同一个页面用查询参数切换阶段，每次只挂载一个阶段，彼此不共享状态：

| 地址（相对 5181） | 组件 | 看什么 |
|---|---|---|
| `/?stage=static` | `StaticCard` | 写死的一张卡片，没有 props 与状态 |
| `/?stage=props` | `PropsCard` | 文字 props，两张卡片显示不同数据 |
| `/?stage=object` | `ObjectCard` | 整个问题对象作 props，仍无 Hook |
| `/?stage=click` | `ClickCard` | 每张卡片独立的 `expanded`；`setExpanded(!expanded)` 在单次点击下正确 |
| `/?stage=snapshot` | `SnapshotDemo` | 打开 Console：第一次点击打印 `调用前 false`／`调用后 false`，界面变为"已展开" |
| `/?stage=update` | `UpdateDemo` | 同一事件内两次传下一值得 1，两次传更新函数得 2；每组先归零 |
| `/?stage=search` | `SearchDemo` | 单组件内的受控搜索 |
| `/?stage=communication` | `SearchApp` | 状态提升到父组件，`SearchBox` 只收值与回调 |
| `/?stage=index` | `IndexDemo` | **故意用 index 作 key** 的对照：展开 101 后反转，展开状态跟着位置跑到 102 |
| `/` | `App` | 最终版：集合操作、搜索、完整本地表单 |

未知的 `stage` 值会回到完整 `App`。阶段选择只服务演示，不是 Router 教学。

**复位要完整刷新页面**（Cmd/Ctrl+R）：恢复 102、101 两条数据、空关键词、全部收起、空草稿与空结果。改源码触发的热更新可能保留 state，不能当作复位。

## 目录结构

| 路径 | 用途 |
|---|---|
| `index.html` → `src/main.tsx` | `#root` 容器、`createRoot`、`StrictMode`、按 `stage` 选择内容 |
| `src/Stage.tsx` | 阶段分发，另含 `IndexDemo`、`PropsDemo` 两个对照；不保存业务状态 |
| `src/contracts.ts` · `data.ts` · `rules.ts` | 类型、固定两条问题（第 7 课种子副本）、纯筛选 |
| `src/StaticCard` · `PropsCard` · `ObjectCard` · `ClickCard.tsx` | 从静态到带状态的卡片演进 |
| `src/SnapshotDemo` · `UpdateDemo.tsx` | 状态快照日志、两种更新写法对照 |
| `src/QuestionCard` · `QuestionList.tsx` | 最终版卡片（函数式更新）、列表 key 与空结果 |
| `src/SearchDemo` · `SearchBox` · `SearchApp.tsx` | 单组件搜索 → 受控子组件 → 父组件接线 |
| `src/form-model.ts` · `CreateForm.tsx` | 草稿类型、长度校验、提交与清空 |
| `src/App.tsx` | 合并集合、搜索与表单的最终版 |
| `src/immutable.ts` | `rename102`／`addTag102` 两个不可变更新纯函数，只供推演与测试 |
| `tests/examples.test.mjs` | Node 自检，23 项 |
| `tests/browser.mjs` | 真实 Chrome 行为验证，88 项 |
| `.artifacts/` | 浏览器自检的报告与截图（不纳入 Git） |

`SearchApp.tsx` 导出的组件也叫 `App`，`Stage.tsx` 把它别名导入为 `SearchApp`，与最终 `App` 不会同时挂载，注意区分。

`// #region 名` 标记就是课件 `<<<` 引用的区段，改动区段内容会让课件高亮错位。

## 命令清单

| 命令 | 做什么 | 是否持续运行 |
|---|---|---|
| `npm run dev` | 开发服务器 <http://127.0.0.1:5181> | 是 |
| `npm run check` | `tsc --noEmit`，检查 `src` 全部 TS／TSX | 否 |
| `npm run lint` | ESLint 两条 Hook 规则：`rules-of-hooks`、`exhaustive-deps`，0 警告 | 否 |
| `npm run build` | 构建到 `dist/`，所有阶段组件都进入产物 | 否 |
| `npm run verify` | check → lint → build，前一步失败就停 | 否 |
| `npm run preview` | 预览已构建的 `dist/`，<http://127.0.0.1:4181> | 是 |
| `npm test` | 纯函数、类型与 lint 自检，应 23 项全部通过 | 否 |
| `npm run test:browser` | 另开终端、保持 dev 运行时执行，应 88 项全部通过 | 否 |

`preview` 只读已有的 `dist/`，不会自动重建：改了源码要先 `npm run build`。`base: './'` 让产物使用相对资源路径，`?stage=` 在 preview 中同样可用。

## 两类自检

两类证据互不替代：Node 自检不打开浏览器，浏览器自检不检查类型与构建。

**`npm test`（Node，23 项）**

- 固定数据、六个关键词的筛选结果，且不修改冻结的输入
- `rename102`／`addTag102` 只复制被改的数组与对象，未改部分复用原引用
- 标题 5–200、正文 10–20000 的长度边界；按 Unicode 码点计数，`trim` 只用于判断、不写回
- **预期失败**：用内联字符串构造三段错误代码（条件调用 Hook、缺失依赖、对象 props 传字符串），确认本包的 ESLint 与 `tsconfig` 真的会拒绝。这些虚拟文件名不在磁盘上，不污染正确源码

**`npm run test:browser`（Chrome，88 项）**

逐个阶段点击、输入、刷新，检查展开状态独立、快照日志、两种更新结果、稳定 key 与 index key 的差异、表单校验与本地结果；同时要求无运行异常、无 React 警告、**无任何业务请求或写请求**。报告写到 `.artifacts/browser.json`，截图为 `form-result.png`（整页）与 `result-region.png`（结果区域）。

对构建产物再跑一遍：先 `npm run build && npm run preview`，另开终端：

```bash
L11_BASE_URL=http://127.0.0.1:4181 npm run test:browser   # 报告写到 .artifacts/preview.json
```

`L11_BASE_URL` 只接受本机 HTTP 地址（`localhost`／`127.0.0.1`／`[::1]`）。没有 Chrome 时先跑其余检查，**不要把浏览器项算作通过**。

## 本地表单的边界

`App` 底部的创建表单**不发送任何请求**：

- 提交只把这次输入记录到"上次本地提交结果"，不会新增问题卡片，不是服务端成功响应
- `tags` 固定为空数组，界面显示"标签项数：0"
- 校验失败时保留已输入内容，也不覆盖上一次的合法结果；"清空草稿"是普通按钮，不提交
- 文本用 JSX 插值显示，输入 `<strong>` 只会显示成尖括号文本，不会生成 HTML 元素
- 真实网络请求、等待状态、422／409 错误与回读在第 12 课

## 常见问题

**`Port 5181 is already in use`**
`strictPort: true` 不会自动换端口。先查占用者再决定，不要结束不认识的进程：

```bash
lsof -nP -iTCP:5181 -sTCP:LISTEN
```

**`test:browser` 报连接失败**
dev 没有运行，或用 `L11_BASE_URL` 指向了没启动的 preview。

**`test:browser` 报找不到 Chrome**
脚本用 `channel: 'chrome'` 启动本机 Google Chrome，不会自动下载。安装 Chrome 后重试。

**快照阶段 Console 里日志条数与课件不同**
从完整刷新开始并先清空 Console。`StrictMode` 在开发时可能多调用一次组件函数，但事件处理函数每次点击只运行一次，只看 `调用前`／`调用后` 两条。

**改了代码后状态没复位**
热更新可能保留 state，完整刷新页面。

**改了源码，preview 没变化**
preview 读的是旧 `dist/`，先 `npm run build`。

## 边界

- 所有数据都在页面内存中，刷新即恢复；不读写数据库，不调用后端
- `src/data.ts` 与第 10 课的固定数据内容相同，但两课源码互不导入
- `interface` 只在编译期检查，不是运行时校验
- 浏览器自检观察的是普通 DOM 与 Console，不等于 React DevTools 的组件树观察
- 依赖精确版本以 `package-lock.json` 为准（当前 React 19.3.1、Vite 8.3.8、TypeScript 5.9.3、ESLint 10.15.0）；本课在 Node 22.14.0 + Chrome 157 实测 `verify` 通过，Node 自检 23 项、dev 与 preview 浏览器自检各 88 项通过
