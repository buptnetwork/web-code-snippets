# 第 10 课 · web

从一页静态 HTML 出发，逐步接入 JavaScript、拆成模块、引入局部 TypeScript，并经 Vite 开发代理读取第 7 课的问题列表 API。可独立安装、运行、构建与自检，不引用其他课次的前端源码。

配套课件：`pages/ch05/10.md`（正文）与 `pages/ch05/10-reference.md`（入口、配置、适配器、后端边界）。

## 前置条件

- Node 22.13+（低于 23，本课实测 22.14.0）与 npm 10.9.2，见 `package.json` 的 `engines`
- 只读后端列表时才需要：第 7 课 `snippets/ch03/lesson-07/question-api/` 已按其 README 建库、迁移、导入种子，并在 8000 端口运行。纯前端部分（本地筛选、构建、自检）不需要后端

## 快速开始

在本目录（`snippets/ch05/lesson-10/web/`）执行，不在 Slidev 根工程：

```bash
npm ci                     # 1. 按 package-lock.json 重建 node_modules
cp .env.example .env       # 2. 生成公开配置（.env 不提交）
npm run dev                # 3. http://127.0.0.1:5173 ，Ctrl+C 停止
```

`.env` 只有一个虚构的公开值：

```dotenv
VITE_COURSE_NAME=问答课堂演示站
```

> `VITE_` 开头的变量会被 Vite 写进浏览器代码，**任何人打开页面都能看到**，只能放公开信息，不能放密码或密钥。`.gitignore` 忽略 `.env` 只影响 Git，不影响它进入构建产物。

## 四个入口

dev 运行后按地址打开，四个入口是独立的教学快照，彼此不同时载入：

| 地址（相对 5173） | 阶段 | 看什么 |
|---|---|---|
| `/stages/01-static/` | HTML／CSS 起点 | 只有一条写死的卡片；输入 SQL 回车，地址栏出现 `?keyword=SQL`（原生表单导航） |
| `/stages/02-single/` | 单文件 JS | 数据、三个纯函数与 DOM 接线全在一个 `main.js`，`preventDefault` 拦下导航 |
| `/stages/03-modules/` | JS 模块 | 拆成 `data.js`／`rules.js`／`main.js`，筛选结果与上一阶段相同 |
| `/` | 局部 TS 最终版 | `src` 中的 TS 数据与规则 + JS 接线、后端列表按钮、公开配置 |

所有阶段共用 `src/style.css`。`03-modules` 用 `type="module"`，直接双击 HTML（`file://`）打不开，统一用 dev 查看。

## 目录结构

| 路径 | 用途 |
|---|---|
| `index.html` · `src/style.css` | 最终版页面节点 · 各阶段共用样式 |
| `src/contracts.ts` | `QuestionItem`／`QuestionListOut` 类型，对应第 7 课列表响应 |
| `src/data.ts` · `rules.ts` | 固定两条问题（第 7 课种子的副本）· 筛选与计数文案 |
| `src/main.js` | 页面接线：本地筛选、后端按钮、公开配置 |
| `src/api.js` | GET 适配器：HTTP 状态、内容类型、JSON 形状分别检查 |
| `src/public-config.js` | 读取 `VITE_COURSE_NAME` |
| `stages/` | 01 静态、02 单文件、03 模块三个快照 |
| `examples/` | 独立语言片段与**故意写错**的故障片段 |
| `tests/examples.test.mjs` | `node:test` 自检，26 项 |
| `vite.config.js` | dev 端口与代理、preview 端口（不带代理） |
| `eslint.config.mjs` · `tsconfig.json` | lint 与类型检查范围 |

`// #region 名` 与 `<!-- #region 名 -->` 标记就是课件 `<<<` 引用的区段，改动区段内容会让课件高亮错位。`02-single`、`03-modules` 与 `src/main.js` 的 `select`／`node`／`render`／`event` 四个区段要求逐字一致，测试会检查。

## 命令清单

| 命令 | 做什么 | 是否持续运行 |
|---|---|---|
| `npm run dev` | 开发服务器 <http://127.0.0.1:5173>，带 `/questions` 代理 | 是 |
| `npm run check` | `tsc --noEmit`，只检查 `src/**/*.ts` | 否 |
| `npm run lint` | ESLint，只检查 `src/**/*.js` | 否 |
| `npm run build` | 只构建根 `index.html` 到 `dist/`，阶段快照不进入产物 | 否 |
| `npm run verify` | check → lint → build，前一步失败就停 | 否 |
| `npm run preview` | 预览已构建的 `dist/`，<http://127.0.0.1:4173> | 是 |
| `npm test` | 教师自检，应 26 项全部通过；不是课堂任务 | 否 |
| `node examples/language.mjs` | 运行语言片段，按课件顺序打印各块输出 | 否 |

`preview` 只读已有的 `dist/`，不会自动重建：改了源码要先 `npm run build`。

## 故意写错的故障片段

`examples/` 里有两个用来演示诊断的错误文件和一处显式调用才触发的故障，**不要修复它们**：

| 文件 | 故障 | 谁来检查 |
|---|---|---|
| `examples/type-error.ts` | 把字符串 `"2"` 赋给 `number`，TS2322 | 测试显式检查；`tsconfig.json` 只含 `src`，所以 `npm run check` 仍通过 |
| `examples/lint-error.js` | 把 `summary` 拼成 `summmary`，`no-undef` | 测试以 `src` 的规则检查；`npm run lint` 只扫 `src`，所以仍通过 |
| `examples/language.mjs` 的 `callbackError` | 把调用结果当函数传入，预期 `TypeError` | 只在显式调用时抛出，直接运行文件不会触发 |

测试同时验证"修正后错误消失"，说明故障确实来自那一处。

## 读取后端列表

```text
浏览器 → 127.0.0.1:5173/questions?…  ──Vite 代理──▶  127.0.0.1:8000/questions?…（第 7 课 FastAPI）
```

1. 按第 7 课 README 起服务：在 `snippets/ch03/lesson-07/question-api/` 执行 `uv run --env-file .env uvicorn app.main:app --reload`
2. 本目录 `npm run dev`，打开 <http://127.0.0.1:5173/>
3. 点"读取后端列表"，固定种子下应显示 `后端：第 1 页，共 2 条；本页 ID：102、101`

要点：

- 代理正则只匹配 `/questions`、其查询参数与子路径，不匹配 `/questions-extra`；后端收到的路径仍是 `/questions`，不加 `/api` 前缀
- DevTools Network 里的 Request URL 仍是 5173，浏览器看来是同源请求
- **preview 不带代理**（`preview.proxy` 显式为 `{}`），且 `main.js` 在非 DEV 模式下直接禁用按钮，显示"静态预览只核对页面；真实 API 演示使用 dev 服务"——这是设计，不是 CORS 故障
- 适配器只发一次 GET，没有重试、超时与取消；请求长时间无响应就停止演示

## 常见问题

**`Port 5173 is already in use`**
`strictPort: true` 不会自动换端口（避免证据里的地址对不上）。先查占用者再决定，不要结束不认识的进程：

```bash
lsof -nP -iTCP:5173 -sTCP:LISTEN
```

**点按钮显示 `后端读取未完成：HTTP 502`**
8000 端口没有服务，代理连不上。先起第 7 课后端，确认 `curl -s http://127.0.0.1:8000/questions` 能返回 JSON。

**显示 `预期 API JSON；请检查端口、路径与代理`**
响应不是 `application/json`，通常是请求落到了 Vite 的 HTML 页面而不是后端：核对代理配置与请求路径。

**显示 `列表响应形状不符合本课约定`**
后端返回了 JSON，但 `items`／`total`／`page` 或问题字段不符合 `src/api.js` 的检查，多半是 8000 上跑的不是第 7 课工程。

**页面显示"公开配置：未设置课程名称"**
没有 `.env`，或 `VITE_COURSE_NAME` 为空。改 `.env` 后要**重启 dev**；preview 还要先**重新 build**。

**改了源码，preview 没变化**
preview 读的是旧 `dist/`，先 `npm run build`。构建失败时留下的旧 `dist/` 不算本次成功。

**本地筛选结果乱了**
刷新页面即可复位，本地筛选不写任何数据。

## 边界

- 本地筛选只用 `src/data.ts` 的固定副本，运行时不读数据库；后端区域与本地列表从 DOM 到数据都相互独立
- `check` 只覆盖 `src` 中的 TS，不检查 `main.js` 与 `api.js` 的类型关系；没有启用 `allowJs`／`checkJs`
- 适配器只保护当前展示用到的字段形状，不禁止额外字段、不验证完整日期格式，也不替代后端校验
- 测试中的 DOM 与 `fetch` 都是最小替身，只验证局部逻辑；浏览器交互与真实 FastAPI 联调需另行验证，只有固定响应时不能记作联调
- 安装、构建与运行都不改数据库；Promise、`async`／`await`、`fetch` 在第 12 课正式讲授
- 依赖精确版本以 `package-lock.json` 为准；本课在 Node 22.14.0 实测 `verify` 通过、26 项测试通过
