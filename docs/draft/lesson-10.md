# 第 10 次课教学底稿（第四版）
## 前端工程链路：模块、构建与公开配置

> **备课基线**：[第四版大纲](../syllabus-v4.md)第 10 课与[第 9 课交接](lesson-09.md#八拓展与第-10-课交接)。本稿未归档，定义教学内容与配套工程要求，不代表独立课程包、锁文件、真实 M3 联调、远端 CI 或最终 Slidev 已交付。下文 `web/` 指学生问答工程的新前端目录，不是本 Slidev 仓库的根目录；不得用本课配置覆盖课件工程。

## 〇、这次课学会什么

**讲给学生的目标句**：你能改一个模块、跑起来、构建出产物，并在产物里找到你刚写的那行字。

核心解释目标只有一个：**你写的源码怎么变成浏览器真正执行的文件。** 模块、类型与公开配置都用同一条链路解释。先运行正确模块，再完成两次小实验；不从多组缺陷、依赖否决或安全扫描器开场。

**前置卡**：JS 模块 import／export、对象与解构、npm 脚本。课前用短例确认能读懂命名导入和对象字段；不把 TypeScript 或 React hooks 当作已学前提。

### 95 分钟教学 + 5 分钟缓冲

| 分钟 | 教学单元 | 当场产出 |
|---|---|---|
| 5 | 交接与目标 | 指认源码、工具和浏览器的分工 |
| 12 | 模块、依赖图与构建理由 | 从 HTML 入口连到自己能改的模块 |
| 13 | dev／build 两条链路与一次代理 GET | 同源判定、报文与转发路径 |
| 20 | 学生任务 A：改模块并找到产物 | 源码改动→dev 页面→构建文件证据 |
| 15 | TypeScript 最小集与转译对照 | 类型正确正例、已知类型缺陷的不同退出结果 |
| 18 | 学生任务 B：公开配置两组对照 | 被使用／未引用的虚构占位值与解释 |
| 12 | 接入统一门禁、写法卡与交付 | 前端 check／lint／build 接线与一个作业包 |
| **95** | **教学合计** | **另留 5 分钟缓冲，共 100 分钟** |

本课**不安排计分小测**。前端进入新领域，AI 回到**阶段一：解释器**；唯一的方案评审是做完配置实验后判断“客户端如何保密”。source map 反查、体积分析、供应链专题与检查器编写移参考。课堂不等待安装依赖；超时不挤掉 20／18 分钟学生操作。

### 教师模板与学生责任

| 内容 | 标注 | 边界 |
|---|---|---|
| `labels.ts`／`format.ts`、依赖图、构建输出 | 要求解释 | 学生选择改哪个模块、如何寻找证据，不改 API 契约 |
| 脚本、锁文件、Vite／tsconfig／ESLint 接线 | 要求会用 | 教师提供可运行版本；不要求背完整配置 |
| 列表类型、可选字段、联合与收窄 | 要求解释 | 只解释已经教过的类型，不考生成器内部 |
| React 入口、App 的状态与事件接线 | **黑盒** | 本课只当已工作的展示外壳；第 11 课从正例教组件，不提前考 hooks |
| GET 适配器与运行时形状检查 | 要求会用；内部黑盒 | 本课会追踪请求 URL／状态／外壳；第 12 课再学习请求生命周期 |
| 后端、虚构 seed、复位、测试与 CI 基线 | 教师提供，要求会用 | 不让学生现场造数据库／部署／扫描平台 |
| 两个实验记录、链路图与一次 AI 核对 | 学生完成 | 合并到一个作业包，不另交长报告 |

## 一、交接：已有 API，不等于已有完整 React 前端

**课堂 5 分钟。** 第 8 课增加条件投票与 PATCH，第 9 课把契约、真实提交与故障证据组织成回归。类型门禁当时使用教师最小消费者；本课才把它扩展到真实前端源码。

本课只联调一次原列表 GET，不新增业务端点或变更公开字段：

- `GET /questions?keyword=&page=1&page_size=20`；keyword 字面子串，id DESC；外壳 `items/total/page`。
- 列表每项 `id/title/body/tags/created_at` 五字段。不要从详情的七字段推导列表也有 vote_count/version，更不添加 author、answer_count、sort/status。
- 详情／创建／PATCH 与投票、四字段业务错误、HTML 三页、healthz 和服务事务约定均不变。前端相对路径不要求后端新增 `/api` 前缀。
- 迁移仍是 001→002；本课不改数据库、认证和 SSR 行为。React 起点不是“SSR 页面已经被删除”。

```text
index.html → main.tsx → App.tsx → labels.ts／format.ts／public-config.ts
                                  ↓ 点击一次
                              api.ts → dev server 转发 → M3 GET /questions
```

学生先指出：哪些文件是自己写的源码，哪些进程在开发机运行，最后浏览器拿到什么。React 外壳帮助观察模块结果，不把组件状态变成本课第二条主线。

## 二、正确模块：从一行文字读懂依赖图

**课堂 12 分钟。3 分钟入口，4 分钟模块，3 分钟构建理由，2 分钟脚本与锁文件。**

### 2.1 先看能工作的最小模块

`web/src/labels.ts`：

<!-- lesson10: labels -->
```ts
export const pageTitle = "问答社区 · 模块实验";
```

`web/src/format.ts`：

<!-- lesson10: format -->
```ts
export function formatCount(count: number): string {
  return `共 ${count} 条问题`;
}
```

外壳已经使用这两个模块：

```tsx
import { pageTitle } from "./labels";
import { formatCount } from "./format";
// 展示接线节选，不是独立 App 文件。
<h1>{pageTitle}</h1>
<p>{formatCount(3)}</p>
```

`export` 提供模块接口，命名 `import` 取同名绑定；默认导出另用不带花括号的导入。本课主线统一用命名导出，不花时间维护桶文件或比较模块系统。

普通静态 import 位于模块顶层，路径是字符串字面量；`import()` 是返回 Promise 的动态表达式，进入 B 档。依赖图由入口可达关系决定，**不是把 src 中每个文件无条件拼到一起**。

### 2.2 为什么本项目选择构建工具

浏览器本来支持 ESM，不是所有网页都必须打包。这个工程需要处理 TypeScript／JSX、npm 依赖和 CSS，并生成适合部署的一组资源，所以使用 Vite。

| 输入 | 本工程中工具做什么 | 不要误解成 |
|---|---|---|
| `.ts`／`.tsx` | 转换类型语法／JSX 等，产出 JavaScript | 浏览器直接执行类型标注 |
| `react` 等裸说明符 | 按依赖解析规则找到包并转换引用 | 浏览器自行遍历 node_modules |
| 模块与 CSS | 按可达依赖处理、打包和优化 | 所有已安装依赖都进入首屏 |
| 未使用代码 | 在可安全证明时移除 | ESM 必然全部能摇掉，CommonJS 绝对不能优化 |

没有 import map 等映射时，浏览器通常不能直接解析 `import ... from "react"`；import map 可映射裸说明符，包括依赖使用的说明符，但不负责转译 TS／JSX。本课不通过一个裸说明符错误证明“浏览器必须有打包器”。

工具内部随版本变化：本轮参考 Vite 8，使用 Oxc／Rolldown 链路；不要照搬旧版“永远由 esbuild／Rollup 完成”的结论。学生必须解释的是输入、转换和产物，而非内部工具名称。

### 2.3 脚本是明确命令，锁文件是安装依据

教师包固定 `package.json` 与 `package-lock.json`，课堂前完成 `npm ci`。在 `web/` 中运行：

```bash
npm ci
npm run dev
```

- `npm run dev` 执行 scripts.dev，不是 npm 自己懂 Vite。
- package.json 描述直接依赖及允许范围；lockfile 记录实际解析结果、传递依赖与完整性信息，二者一起版本管理。
- `npm ci` 要求清单与锁文件相容，按锁文件安装，不自动更新它；会重建该包 node_modules，不能在用户其他工程里随便运行。
- 锁文件不保证所有操作系统产物字节相同，不证明依赖无漏洞，也不自动锁住 Node／npm 与所有生命周期脚本行为。教师还提供 Node／npm 版本与平台自检。

本课不要求删满两个依赖或否决某个真实包；依赖变更须有需求依据和重新验证。

## 三、两条链路：一次列表 GET 发生在哪里

**课堂 13 分钟。4 分钟两链路，3 分钟同源，4 分钟 GET，2 分钟确认边界。**

### 3.1 dev、build、preview 分别是什么

| 命令 | 做什么 | 本课观察 |
|---|---|---|
| `npm run dev` | 启动开发服务器，按需转换模块，处理开发期更新 | 浏览器请求源码路径时拿到转换后的内容；更新也可能整页重载 |
| `npm run build` | 构建可达入口，生成 dist | 命令结束后得到 HTML／JS／CSS 等文件；**不会部署或启动服务器** |
| `npm run preview` | 启动本地服务器预览已构建的 dist | 看的是旧／新哪次构建，而不是自动读取最新源码 |

dev 不等于完全不处理依赖，build 也不保证只发“几个”请求；不拿请求数乘 RTT 估算首屏时间。构建工具不是后端服务，打包不把 Python 和数据库搬进浏览器。preview 用于本地核验，不是生产服务器方案。

### 3.2 同源看协议、主机和端口

固定开发环境：前端 `http://127.0.0.1:5173`，后端 `http://127.0.0.1:8000`，无浏览器扩展改写请求。

| 页面中的请求目标 | 与页面同源吗 | 原因 |
|---|---|---|
| `/questions?page=1&page_size=20` | 是 | 解析到当前页面的协议／主机／端口 |
| `http://127.0.0.1:8000/questions` | 否 | 端口不同 |
| `http://localhost:5173/questions` | 否 | 主机不同，不能用“都在本机”代替同源判定 |
| `https://127.0.0.1:5173/questions` | 否 | 协议不同 |

CORS 是浏览器对跨源访问的机制，不等于“跨源请求一定发不出去”，也不是认证或权限控制。完整配置与部署留第 16 课；本课只辨认源、看一次 dev proxy 转发。

### 3.3 开发期代理保留原 API 路径

教师的 `web/vite.config.ts`：

<!-- lesson10: vite_config -->
```ts
import { defineConfig } from "vite";

export default defineConfig({
  server: {
    host: "127.0.0.1",
    port: 5173,
    strictPort: true,
    proxy: {
      "^/questions(?:/|\\?|$)": {
        target: "http://127.0.0.1:8000",
        changeOrigin: true,
      },
    },
  },
  preview: { host: "127.0.0.1", port: 4173, strictPort: true, proxy: {} },
  build: { sourcemap: false },
});
```

```text
浏览器 GET http://127.0.0.1:5173/questions?...
   → Vite 根据路径转发
   → 后端收到 GET /questions?...（路径／查询不重写）
   → 原响应经过 Vite 返回浏览器
```

浏览器 Network 中的 Request URL 仍是 5173；不是浏览器偷偷变成跨源访问 8000。changeOrigin 主要改变代理上游 Host 等行为，不是“关闭浏览器 CORS”。严格端口在占用时失败，避免截图取错服务；不为启动课程程序停止不明来源进程。

教师已启动完成迁移、seed 的 M3 正确版，数据没有并发写者。点击一次“读取列表”，保存：请求 URL／GET、200、`items/total/page`、列表五字段及响应 `X-Request-ID`；对应后端 request-id 日志。不要只看按钮文字判定联调成功，也不要把静态 mock 说成真实 M3。

**生产边界**：proxy 配置属于运行中的开发服务器，不写进 dist。Vite preview 默认继承 server.proxy，因此本例显式 `preview.proxy: {}`，只验产物。按本轮 Vite 8.2.2 配置，预览页按钮发送 `Accept: application/json`，没有 API 路由时返回 **404**，页面显示“HTTP 404；request-id 未提供”；这不是后端的四字段业务 404。若请求接受 `text/html`，同一路径可回退到 200 HTML，适配器仍应以 content-type 拒绝。不能忽略 Accept、只看 URL 或 200 就判断联调成功。生产必须另配同源反代或明确跨源方案，不能把 preview 通过当生产已配好。

## 四、学生任务 A：改一个模块，在产物中认出它

**课堂 20 分钟。3 分钟选模块，5 分钟修改与 dev 核对，7 分钟构建／查找，5 分钟记录与解释。**

### 4.1 完整前提与学生的小决定

从教师正确版开始，真实源码路径固定，App 正在调用 labels／format；没有 API 写操作。选择以下一处：

- 改 pageTitle，保留页面用途，在末尾加唯一 ASCII 标记 `L10_MODULE_A`。
- 改 formatCount 的展示文案，在返回字符串中加 `L10_MODULE_A`；入参和返回值类型、API 字段不变。

可以用 IDE 的目录搜索、终端精确搜索或浏览器 Sources 定位，学生自己决定并说明为什么。标记不是函数名，不能只改一个会被压缩的局部变量名然后要求产物逐字保留它。

### 4.2 同一改动，四个观察点

1. 保存源码，在 **5173 dev 页面**确认标记可见。必要时刷新；不承诺无插件时保留所有 React 状态。
2. 在 web 目录执行 `npm run build`，记录真实退出码和输出目录。
3. 先打开 `dist/index.html`，沿其中真实 script／stylesheet 引用找资源；不要照抄示意 hash。
4. 在这次 dist 的 JS 中搜索 `L10_MODULE_A`，再用 **4173 preview** 打开这次产物，确认同一标记可见。API GET 只验 dev，本任务 preview 只验文字与静态资源。

终端查找示例（macOS／Linux；没有 rg 时用编辑器等价操作）：

```bash
rg --files dist
rg -l -F 'L10_MODULE_A' dist
npm run preview
```

`rg` 的无匹配退出 1 是查找结果，不是构建失败。输出文件应记录为本次实际路径；构建失败时可能还留着上一次 dist，不能对旧目录截图宣称新构建成功。

### 4.3 认识产物，不背固定文件数

```text
dist/
  index.html
  course-mark.txt          ← 本例 public 中的虚构静态文件
  assets/
    index-<实际hash>.js
    index-<实际hash>.css   ← 本例导入的 CSS；具体命名以实测为准
```

- index.html 是这次单页构建的入口索引，引用转换后的资源；它可能包含静态文字，不说“HTML 一定没有内容”。
- chunk 的合并、压缩、死代码删除可改变源码外观；源文件不必与产物一一对应。压缩不是加密。
- 文件名 hash 用于区分资源版本，支持部署缓存策略；hash 不是秘密，也不是“所有改动恰好只影响一个 chunk”的保证。源码变化若被优化消除，输出可以不变。
- public 默认原样复制到产物，放进去即应视为可公开资源。不要放 env、凭据或内部备份。
- 本例 sourcemap=false，不应凭空出现 map 文件。source map 反查移参考，不作为当堂额外任务。

记录一条链：**我的源模块→谁 import 它→入口→实际资源 URL→浏览器显示**。若 API 正常而文字没变，先排查当前端口／构建目录／缓存，不先修改后端。

## 五、TypeScript：从正确类型到一次受控对照

**课堂 15 分钟。7 分钟最小类型，5 分钟转译对照，3 分钟边界。**

### 5.1 读懂已有响应类型

教师在 `web/src/contracts.ts` 对齐第 9 课批准的契约；本轮是人工维护的最小消费者，不伪称第 8 课已交付自动生成链。

<!-- lesson10: contracts -->
```ts
export interface QuestionItem {
  id: number;
  title: string;
  body: string;
  tags: string[];
  created_at: string;
}

export interface QuestionListOut {
  items: QuestionItem[];
  total: number;
  page: number;
}

export type LoadNote =
  | { kind: "ok"; page: QuestionListOut }
  | { kind: "error"; message: string; requestId?: string };

export function describeLoad(note: LoadNote): string {
  if (note.kind === "ok") {
    return `第 ${note.page.page} 页，共 ${note.page.total} 条`;
  }
  return `${note.message}；追踪 ${note.requestId ?? "未提供"}`;
}
```

- 对象类型说明可用字段；`QuestionItem[]` 是数组，接口外壳不是数组本身。
- `requestId?` 表示本地错误展示信息可以省略，不是把后端错误的必填 request_id 改为可选。
- `kind` 是判别字段；检查后 TS 收窄到对应分支，ok 分支才有 page。普通 switch 不自动保证穷尽所有情况，不能随手加一个联合成员就声称必报错。
- `created_at` 在 JSON 中是字符串，不是已经可调用 Date 方法的对象。例中数值 id 位于 JavaScript 安全整数范围；没有借此修改后端 bigint 的范围承诺。
- `import type` 只引入类型用途，运行时不会生成一个校验器。

### 5.2 先正确，再只引入一个类型缺陷

`web/src/type-probe.ts` 被 App 导入并展示：

<!-- lesson10: type_probe -->
```ts
export const demoCount: number = 3;
```

正确版先跑 check／build。然后在**教师实验副本**只将右边改为字符串 `"3"`，App 用 `String(demoCount)` 展示；不同时制造未定义变量、错误 import 或语法错误。package.json 的 `build` 在本例明确只有 `vite build`，没有前置 tsc 或额外类型检查插件。

```bash
npm run build
npm run check
```

| 执行 | 本例预期 | 能说明什么 |
|---|---|---|
| Vite build | 成功，产物能显示 3 | 已完成转译／打包；不是类型正确 |
| tsc --noEmit | 非零，赋值处 TS2322 | string 不能赋给声明的 number |
| 恢复数字 3 后重跑 | 两者成功 | 已恢复本例正确起点 |

类型错误版不是正式交付版本，不修改 expected、不加 any／忽略注释来“修绿”。可以分别保留原始退出结果；最终统一门禁会先检查类型，再执行构建。

### 5.3 类型不是运行时闸门

TypeScript 类型通常被擦除；`as QuestionListOut` 不会检查收到的 JSON。`Response.json()` 的结果不能因为加了注解就变可信。教师适配器先用 unknown 接收并检查本课需要的形状，再交给页面。

这也不构成完整 OpenAPI 校验：长度、业务语义、权限和所有未来响应仍有各自边界。第 9 课契约测试只证明被测样本／版本，不能担保每次网络响应。前端校验不替代后端校验。ESLint 只执行配置的规则，既不是 TS 的替代，也不自动验证 React 生命周期。

## 六、学生任务 B：公开配置，两组独立对照

**课堂 18 分钟。3 分钟写预测，6 分钟被使用组，4 分钟未引用组，3 分钟解释与 AI 方案判断，2 分钟恢复。** 两组都从同一正确基线的独立副本开始，不把上一组的 dist 当下一组证据。

### 6.1 必须写全的实验条件

- 只用明确虚构值 `COURSE_ONLY_TOKEN_10_A`，没有权限、不对应任何第三方账户；不输入、展示或提交真实秘密。
- 值只写入实验副本 `web/.env`，键为 `VITE_DEMO_TOKEN`。没有 shell 同名覆盖，没有 .env.local／.env.production 等覆盖文件，工作目录为该 web，使用默认 production build。
- `.env` 被 Git 忽略；没有把它放入 public，没有 HTML `%VITE_DEMO_TOKEN%` 引用，没有 `import.meta.env` 整对象枚举、spread、JSON.stringify，没有插件另行注入环境。
- 每组独立输出，只有本组最新构建；sourcemap=false。只改变 public-config.ts，不夹入 API 或类型缺陷。

实验 `.env`：

<!-- lesson10: env -->
```dotenv
VITE_DEMO_TOKEN=COURSE_ONLY_TOKEN_10_A
```

正确起点 `web/src/public-config.ts`：

<!-- lesson10: public_config -->
```ts
export const demoToken = "未启用配置实验";
```

App 已把 demoToken 显示到 `<output>`；React 按普通文本呈现，不作为 HTML 执行。

### 6.2 组 A：引用后确实用于页面

先问：在上述条件下，值会在哪里出现？`.gitignore` 是否改变构建结果？然后把 public-config.ts 改为：

<!-- lesson10: used_config -->
```ts
export const demoToken = import.meta.env.VITE_DEMO_TOKEN ?? "未配置";
```

执行 build，在新 dist 中查 `COURSE_ONLY_TOKEN_10_A`，保存实际命中文件；打开对应 preview，查看页面与该 JS 资源。预计命中可达 JS，浏览器也能读到。本例 ASCII 字符串便于精确查找；其他值可能被转义、折叠、拆分或移除，不能把原样命中当作普遍格式保证。

```bash
npm run build
rg -l -F 'COURSE_ONLY_TOKEN_10_A' dist
npm run preview
```

Vite 在构建阶段静态替换可识别的 env 访问，后续工具仍会优化它；不是对所有文本做不加区分的搜索替换。普通自定义 VITE_ 值按字符串提供，`"false"` 不是布尔 false。

### 6.3 组 B：有同名配置，但客户端没有引用

重新取干净副本，保留同一 `.env`，使用起点 public-config.ts 的固定文字；确认客户端其他模块、HTML、插件都没有读取该键或整个 env。再 build 与查找，记录无命中，preview 只显示“未启用配置实验”。

**本例预期不含该值**，原因是配置没有进入这次可达输出。它不证明这个值“适合保存在前端”，也不证明构建系统的任何配置都不会泄漏。仅仅 import 一个模块还不够：若读取结果没有可观察用途，优化也可能移除它；组 A 特意显示到页面，排除了这个歧义。

### 6.4 由两个实验得到的安全边界

> **凡是交付给浏览器的值，都不能对接收它的人保密。** `.gitignore`、压缩、混淆、Base64、source map 开关都不能改变这个边界；运行时接口把原秘密下发给浏览器，也一样公开。

反过来，产物搜索无命中只是这次检测没有找到，不是保密证明。dist 在本地存在不等于已经对所有人发布；但一旦发布为可访问资源，应按可被访问者获取处理，不能靠“页面没有显示”保密。

普通默认 Vite 前缀规则不暴露非 VITE_ 变量，但自定义 envPrefix、define、插件和复制资源可能改变边界。env 的 TypeScript 声明也不保证实际配置存在。本课要求配置变更后重启 dev、重新 build，避免旧值与进程环境优先级干扰。

适合公开的有页面标题、公开 API 地址、演示开关；服务端私密凭据只由受控后端使用，不通过本课 GET 返回给前端。公开客户端标识须依照供应商文档核对权限、来源限制和服务端规则，不能仅凭名字有 public 就判断安全。

若真实凭据已发布，停止传播并由有权限的人撤销／轮换、核查使用记录和影响，再移除不当暴露、重新构建部署；删除源码不能收回已经复制的值。课堂只讨论流程，不操作真实账户，也不新建第三方代理端点。

### 6.5 AI 只评审自己已经验证过的问题

在任务 A 可让 AI 解释某条 import／构建链路，用实际资源核对。这里唯一的方案评审题是：

> 前端需要调用一个持有服务端私密凭据的第三方服务。请解释凭据放在何处，什么会发给浏览器，并说明 `.gitignore`、构建期与运行时下发各能保证什么。

学生引用组 A／B 的结果判断；合理方案直接接受并说明依据，有问题才改。不要求至少否决一个依赖、不要求找满三处错；预制反例须标明教师构造，不冒充真实 AI 输出。服务端代理仍需要授权、限流和上游故障处理，本课不把一句“放后端”当完整安全设计。

## 七、统一门禁与一个作业包

**课堂 12 分钟。6 分钟接线，3 分钟运行结果／卡片，3 分钟交付与下一课。**

### 7.1 保留第 9 课四类门禁，扩展实际前端覆盖

| 类别 | 本课增量 | 保持的边界 |
|---|---|---|
| lint | 原 Ruff 后增加 `npm --prefix web run lint` | ESLint 只检查已配置规则，不保证业务正确 |
| type | 保留 contract-client，增加 web check，成功后 web build | 构建是这一组的额外步骤，不把原始 build 等同质量验收 |
| test | 原单元／HTTP／真实提交回归 | 不删除旧测试来换前端绿灯 |
| contract | 原快照 check 与代表响应校验 | 不强制本课开发自动类型生成链 |

在第 9 课 `scripts/check.py` 的 GROUPS 定义之后、main 之前插入；ROOT／NPM 与 subprocess 的 check=True、首错停止规则沿用：

<!-- lesson10: gate_extension -->
```python
GROUPS["lint"].append([NPM, "--prefix", "web", "run", "lint"])
GROUPS["type"].extend([
    [NPM, "--prefix", "web", "run", "check"],
    [NPM, "--prefix", "web", "run", "build"],
])
```

本地／CI 仍调用同一个 `uv run --no-sync python -m scripts.check all`。在原 quality job 的 Node 安装步骤之后、统一入口之前，保留 contract-client 的安装，再加：

```yaml
- run: npm --prefix web ci
- run: uv run --no-sync python -m scripts.check all
```

这是现有工作流的接线片段，不是可单独运行的完整 YAML。job 名不另换，原 required check／适用分支／绕过名单继续核对；**CI 执行和分支保护强制合入条件仍是两件事**。本课不要求再搭一个独立前端流水线，也不实际替用户修改远端保护。

教师分别展示：正确 web 三命令成功；仅类型错误时 check 失败；仅 ESLint 规则违反时 lint 失败；入口引用不存在时 build 失败。它们是机制对照，不要求学生新增三份审计报告。前端快速核对可运行 `npm --prefix web run verify`；它不替代含后端的 all。

### 常用写法卡 #10

| 常用写法 | 工具替你做什么 | 必须知道的边界 |
|---|---|---|
| ESM import／export | 连接模块与依赖图 | 不保证每个源文件都变成独立 chunk |
| scripts＋lockfile／npm ci | 固定入口与依赖解析依据 | 锁文件不是所有环境完全一致或依赖安全证明 |
| dev／build／preview | 开发转换、构建资源、本地预览 | build 不部署；preview 不自动重建 |
| dist 入口与 hash | 让资源可寻址、可区分版本 | hash 不加密，缓存策略还需部署端配置 |
| 对象／可选字段／联合收窄 | 检查源码使用方式 | TS 不自动校验运行时 JSON |
| VITE_ 配置 | 暴露允许的构建输入到客户端链路 | 被下发就不保密，无命中不证明安全 |
| 相对 URL＋dev proxy | 让开发服务器转发到后端 | dist 不自带代理；同源由协议／主机／端口判断 |
| check／lint／build 接统一门禁 | 重复执行不同层检查 | 实际运行记录与合入保护不可由脚本名字替代 |

### A 档：只交一个前端起点包

1. 可复现源码、package.json／锁文件、版本说明与不含真实秘密的配置样例；正常 check／lint／build 可运行。
2. 一次**真实 M3 GET** 联调记录：浏览器 URL／状态／五字段、request-id 与后端日志；若只是 mock，明确标注未完成真实联调。
3. 任务 A 的局部改动、构建链路图、真实资源路径与 dev／preview 证据。
4. 任务 B 的被使用／未引用两组独立记录，解释“未命中不是安全证明”，附一次 AI 解释核对及基于实验的方案判断。
5. 前端三命令与统一门禁记录，注明对应版本、退出结果及远端尚未执行项。

上述内容复用课堂记录，卡片补例并入同一包。阶段一概念三问也写在这份记录中：谁转换源码？类型检查和构建各拦什么？浏览器能拿到的配置为何不能保密？不再增加三份作业、固定删依赖数量、必做拆包、扫描器或“能上生产”的验收承诺。

## 八、课后参考与第 11 课交接

### 8.1 B 档只选一次体积与动态 import 对照

选择教师的**纯文本帮助模块**，比较静态导入与按钮点击后 `import()` 的资源、字节与请求时机；前后使用同一功能、工具版本、构建模式和相同压缩口径。允许体积没降，说明拆分开销、共享依赖或预加载影响。

不先引入 Markdown 渲染、dangerouslySetInnerHTML、React.lazy／Effect 竞态或新第三方服务。动态 import 可形成异步 chunk，但不能凭语法保证“列表用户永不下载”，仍需看产物和 Network。

### 8.2 只作参考的工程边界

- **source map**：帮助把生成位置映射回源码，内容是否嵌入取决于配置；hidden 只是不加自动发现注释，不是访问控制。不公开 map 也不会使 JS 中的秘密安全。本课不要求现场反查或接监控平台。
- **缓存**：带版本资源可配置长缓存，HTML 需合适的重验证策略；前提是版本 URL 不被覆盖、发布与旧资源保留正确。no-cache 允许存储但要求使用前验证，不等于不缓存。具体部署在第 16 课。
- **模式**：dev 默认 development，build 默认 production；mode 与 NODE_ENV 不等价。shell 已有变量优先，模式文件可覆盖通用 env。切环境不一定必须重复构建：公开运行时配置也可行，但下发值仍公开。
- **依赖与扫描**：版本范围不证明兼容，包存在不证明可信；使用来源审核、锁文件和适当的扫描。任何正则或专业扫描器都不完备，不要求写“搜不到即安全”的门禁。
- **编译目标**：语法降级不自动补齐所有运行时 API；教师包需明确支持浏览器。不能用“Node 20+”覆盖工具实际最低版本要求。

### 8.3 下一课明确接收什么

第 11 课接收可运行的 Vite＋React＋TS 外壳、模块类型、统一门禁，以及教师新发的**固定 JSON 列表与表单 UI 模板**。先写死卡片→props→局部 state／事件→受控输入→map／稳定 key；模板中的作者字段属于第 11 课给定练习数据，**不倒逼本课公开列表 API 增加作者**。

第 10 课未教授 React 状态机制，不把黑盒外壳当成学生已会 hooks；第 11 课从正例开始讲。完整更新队列、批处理、memo 性能主题进参考；最小函数式更新到第 16 课首次需要时讲，不承诺第 12 课“还完整队列债”。第 11 课课后表单只接模拟状态，真实请求适配与提交反馈在第 12 课接入。

第 11 课底稿已按 v4 重写，落实卡片→props→局部 state→受控输入→交互列表，以及三种草稿存法对照、15 分钟小测和仅模拟状态的课后表单。隔离源码 check／lint／build 与 78 项浏览器自动机制检查通过；人工可视操作、截图、React DevTools 和正式课程包仍待验收，详见该课制作状态。完整 CORS、部署与公开运行时配置交给第 16 课，不沿用旧稿的“第 12 课专讲生产 CORS”。

## 九、教师附录：最小工程参考

附录不要求课堂逐行抄。以下围栏可组成 web 起点，**仍需教师提供真实生成并核验的 package-lock.json、环境说明、M3 后端与统一门禁接线**；配置写在底稿不等于课程包已交付。React 与适配器内部为本课黑盒。

### 9.1 文件与脚本

```text
web/
  package.json / package-lock.json / tsconfig.json
  vite.config.ts / eslint.config.mjs / index.html
  .gitignore / .env.example
  public/course-mark.txt
  src/
    main.tsx / App.tsx / style.css
    labels.ts / format.ts / type-probe.ts / public-config.ts
    contracts.ts / api.ts / vite-env.d.ts
```

参考版本显式固定，正式课程包须在目标平台重新安装验证，不从任意版本的在线脚手架临场生成：

<!-- lesson10: package -->
```json
{
  "name": "qanda-web-lesson10",
  "version": "0.0.0",
  "private": true,
  "type": "module",
  "engines": { "node": ">=22.12.0 <23" },
  "scripts": {
    "dev": "vite",
    "build": "vite build",
    "preview": "vite preview",
    "check": "tsc --noEmit",
    "lint": "eslint src --max-warnings 0",
    "verify": "npm run check && npm run lint && npm run build"
  },
  "dependencies": {
    "react": "19.2.0",
    "react-dom": "19.2.0"
  },
  "devDependencies": {
    "@eslint/js": "9.39.1",
    "@types/react": "19.2.2",
    "@types/react-dom": "19.2.2",
    "eslint": "9.39.1",
    "globals": "16.4.0",
    "typescript": "5.9.3",
    "typescript-eslint": "8.46.2",
    "vite": "8.2.2"
  }
}
```

这是最小 React 展示外壳，使用 Vite 内置 TSX 转换与 automatic JSX runtime；不含 Fast Refresh 插件，不承诺热更新保留组件状态。下一课若加 React 插件／hooks lint，由教师验证版本后更新锁文件。Node engines 默认不等于强制版本闸门，教师启动自检和 CI 还须固定实际版本。

<!-- lesson10: tsconfig -->
```json
{
  "compilerOptions": {
    "target": "ES2022",
    "lib": ["ES2022", "DOM", "DOM.Iterable"],
    "module": "ESNext",
    "moduleResolution": "Bundler",
    "jsx": "react-jsx",
    "strict": true,
    "isolatedModules": true,
    "verbatimModuleSyntax": true,
    "skipLibCheck": true,
    "noEmit": true,
    "types": ["vite/client"]
  },
  "include": ["src"]
}
```

此 check 覆盖 src，不宣称检查所有构建配置或依赖声明文件；Vite 配置加载由 build 实测。`skipLibCheck` 不关闭自己源码的类型检查。

<!-- lesson10: eslint -->
```js
import js from "@eslint/js";
import globals from "globals";
import tseslint from "typescript-eslint";

export default tseslint.config(
  { ignores: ["dist/**", "node_modules/**"] },
  {
    files: ["src/**/*.{ts,tsx}"],
    extends: [js.configs.recommended, ...tseslint.configs.recommended],
    languageOptions: { globals: globals.browser },
    rules: { "@typescript-eslint/no-explicit-any": "error" },
  },
);
```

不在这份非 type-aware 配置里声称启用了 no-floating-promises；也不凭 ESLint 绿灯断言请求都处理好了。自动修复不在门禁里运行。

<!-- lesson10: gitignore -->
```gitignore
node_modules/
dist/
.env
.env.*
!.env.example
```

`.env.example` 只给键名、公开说明与虚构值；真实 lockfile 由 npm 生成并提交。检查 Git 跟踪状态不能仅用“文件存在”代替；教师可用 `git ls-files --error-unmatch web/package-lock.json` 核对，不能用删除锁文件解决差异。

### 9.2 完整外壳

<!-- lesson10: html -->
```html
<!doctype html>
<html lang="zh-CN">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>第 10 课模块实验</title>
  </head>
  <body>
    <div id="root"></div>
    <script type="module" src="/src/main.tsx"></script>
  </body>
</html>
```

<!-- lesson10: main -->
```tsx
import { createRoot } from "react-dom/client";
import { App } from "./App";
import "./style.css";

const root = document.getElementById("root");
if (!root) throw new Error("缺少 root 容器");
createRoot(root).render(<App />);
```

<!-- lesson10: app -->
```tsx
import { useState } from "react";
import { listQuestions } from "./api";
import { pageTitle } from "./labels";
import { formatCount } from "./format";
import { demoCount } from "./type-probe";
import { demoToken } from "./public-config";

export function App() {
  const [result, setResult] = useState("尚未读取 API");
  const [busy, setBusy] = useState(false);

  async function load() {
    setBusy(true);
    try {
      const { page, requestId } = await listQuestions();
      setResult(`${formatCount(page.total)}；第 ${page.page} 页；id ${page.items.map((q) => q.id).join(",")}；request-id ${requestId ?? "未提供"}`);
    } catch (error: unknown) {
      setResult(error instanceof Error ? error.message : "读取失败");
    } finally {
      setBusy(false);
    }
  }

  return (
    <main>
      <h1>{pageTitle}</h1>
      <p>{formatCount(3)}</p>
      <p>类型对照值：<output id="type-probe">{String(demoCount)}</output></p>
      <p>虚构配置：<output id="config-probe">{demoToken}</output></p>
      <button disabled={busy} onClick={() => { void load(); }}>读取列表</button>
      <p role="status">{result}</p>
    </main>
  );
}
```

这个外壳只供单次按钮 GET 演示，不是完整搜索／分页 UI，不处理多条件竞态或 M4 写操作。上方 `formatCount(3)` 是固定模块示例，真实 API 的 total 显示在下方 status 区域，二者不要求相等。第 12 课再扩展请求生命周期；不把 catch 存在当成覆盖了所有异步风险。

<!-- lesson10: style -->
```css
body { margin: 0; font-family: system-ui, sans-serif; color: #172554; background: #f8fafc; }
main { max-width: 52rem; margin: 3rem auto; padding: 2rem; }
button { padding: 0.6rem 1rem; }
output { overflow-wrap: anywhere; }
```

<!-- lesson10: vite_env -->
```ts
interface ImportMetaEnv {
  readonly VITE_DEMO_TOKEN?: string;
}
```

### 9.3 教师 GET 适配器

`web/src/api.ts`。用固定合法参数，保留 response.ok／content-type 检查与 unknown；不把 JSON 错误体当成功列表，也不把 preview 的 HTML 回退当 API 成功。

<!-- lesson10: api -->
```ts
import type { QuestionItem, QuestionListOut } from "./contracts";

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === "object" && value !== null && !Array.isArray(value);
}

function isQuestion(value: unknown): value is QuestionItem {
  return isRecord(value)
    && typeof value.id === "number" && Number.isSafeInteger(value.id)
    && typeof value.title === "string"
    && typeof value.body === "string"
    && Array.isArray(value.tags) && value.tags.every((tag: unknown) => typeof tag === "string")
    && typeof value.created_at === "string";
}

export function readQuestionList(value: unknown): QuestionListOut {
  if (!isRecord(value) || !Array.isArray(value.items) || !value.items.every(isQuestion)
    || typeof value.total !== "number" || !Number.isSafeInteger(value.total) || value.total < 0
    || typeof value.page !== "number" || !Number.isSafeInteger(value.page) || value.page < 1) {
    throw new Error("列表响应形状不符合本课约定");
  }
  return { items: value.items, total: value.total, page: value.page };
}

export async function listQuestions(): Promise<{ page: QuestionListOut; requestId: string | null }> {
  const query = new URLSearchParams({ keyword: "", page: "1", page_size: "20" });
  const response = await fetch(`/questions?${query}`, { headers: { Accept: "application/json" } });
  const requestId = response.headers.get("X-Request-ID");
  if (!response.ok) {
    throw new Error(`HTTP ${response.status}；request-id ${requestId ?? "未提供"}`);
  }
  if (response.headers.get("content-type")?.split(";", 1)[0] !== "application/json") {
    throw new Error("预期 API JSON，实际不是 JSON；检查端口与代理");
  }
  const raw: unknown = await response.json();
  return { page: readQuestionList(raw), requestId };
}
```

此检查不禁止额外字段、不验证 created_at 日期格式或全部业务约束；它只保护本课展示所需形状。五字段精确契约仍由后端与回归核对，不能拿一个类型谓词取代第 9 课 contract 门禁。

### 9.4 制作与复位要求

- 教师交付正确版、类型单缺陷副本、配置 A／B 独立副本及明确版本，不依赖不存在的 Git tag；不使用强制 checkout 覆盖学生改动。
- 每份实验只有自己的输出目录，禁止清理工作区根 dist 或他人进程；Vite 默认清空所配置 outDir，因此只准指向本实验可丢弃目录。
- 课前确认 5173／4173／8000 的所有者、Node／npm／平台、锁文件安装、浏览器与后端 seed；三端口注明角色。不将其他课程的成功页面拼进本次截图。
- 本地 API 示例无真实凭据、不开放公网；代理 target 固定本地，不接收用户输入 URL。前端只执行 GET。
- 教室网络不可用时使用预先核验的同平台依赖缓存／镜像和注明版本的录屏；不要任意复制不同平台 node_modules。AI 不可用时用注明来源的材料，允许正确输出。
- 真实联调、浏览器页面证据、类型退出、产物查找分别验收；仅 build 成功不代表四项全过，更不代表最终课件视觉合格。

## 十、制作与验证状态

- **本轮隔离实测**：从围栏提取 8 个独立源码／输出副本，在临时父目录共享 npm 依赖；`npm install --no-audit --no-fund` 生成锁文件，再 `npm ci --no-audit --no-fund` 成功。未跳过生命周期脚本，未改课件根依赖；这是本机临时安装验证，不是正式 web 包或跨平台安装验收，也未进行依赖安全审计。
- **工具版本**：darwin-x64，Node 22.14.0、npm 10.9.2、Vite 8.2.2、TypeScript 5.9.3、React／React DOM 19.2.0、ESLint 9.39.1、typescript-eslint 8.46.2。npm 已提示该 ESLint 版本不再受支持；本轮保留实测基线，不以检查通过代替支持状态判断，正式发包前须选择受支持组合、重生成锁文件并重验。
- **77 项机制检查通过**：12 项命令退出、4 项诊断、26 项产物、21 项适配器及其边界、4 项真实 HTTP 代理、4 项 preview 边界、1 项 dev 转译、1 项前端入口、1 项统一入口分发、1 项隔离与 2 项课时。它们是临时验证器的断言计数，不是 77 条完整业务回归。
- **正反例结果**：正确版 check／lint／build 均退出 0；模块改动、配置使用／未引用三组 verify 均退出 0。单类型缺陷的原始 build 退出 0，check 以 TS2322 退出 2；前端 verify 在类型失败处停止，未构建。单 any 规则违反时类型通过、lint 退出 1；缺失模块的 build 以 UNRESOLVED_IMPORT 退出 1。这些非零均为受控反例的预期结果。
- **产物证据**：模块标记命中 `module/dist/assets/index-CNGvhtzn.js`；被使用的虚构配置命中 `used/dist/assets/index-CEeb10a3.js`，未引用组无命中。四组均核对真实 HTML 资源引用、public 原样复制与无 map；上述 hash 只记录本轮结果，不作为学生固定答案。
- **浏览器已核验**：Qoder 内嵌 Chromium 148 中，dev 与 module preview 显示同一模块标记，used／unused 显示对应配置结果，类型错误版产物仍显示 3。dev 按钮 GET 返回固定两条数据，Network 为 5173／GET／200，页面 request-id 与本地固定响应服务记录相符。浏览器工具无法直接展开原按钮响应体／头，五字段与追踪头另用一次只读 GET 核对，未冒充同一次请求。4173 按钮实际 404；独立 HTTP 对照确认 Accept 为 JSON 时 404、接受 HTML 时 200 HTML，两种请求均未转发后端。
- **证据位置与范围**：`.build-check/l10-532a9b28-e430-4939-a8f7-a460259b6fb8/` 中保留 `result.json`、`commands.json`、`preview-accept-results.json`、HTTP 记录与 6 张 `browser-*.png`。8000 是 Node HTTP 固定响应，不是 FastAPI／真实 M3；第 9 课扩展只核对四类、九命令及首错停止的分发，未运行完整后端 all、远端 CI 或生产部署。额外预览端口仅供本轮副本对照，不改课堂三端口配置。
- **正式课程包待制作**：受支持依赖组合与正式锁文件、目标平台自检、完整 M3 后端联调、正确版／独立实验副本、统一门禁与原回归、正式浏览器记录及应急材料。临时工具与截图不冒充完整课程交付。
- **外部环境待验收**：真实 GitHub Actions／分支保护、生产代理／CORS／缓存／部署；本课不执行真实密钥操作。
- **试讲待验收**：20 分钟模块实验、18 分钟配置双对照，以及 15 分钟最小类型是否可完成；不把参考专题挤进必修时间。

参考：[Vite 功能与 TypeScript](https://vite.dev/guide/features)、[环境变量与模式](https://vite.dev/guide/env-and-mode)、[preview 配置](https://vite.dev/config/preview-options)、TypeScript Handbook、npm ci、typescript-eslint Flat Config。最终 Slidev 中教师时间、制作待办、应急切换放备注；学生理解所需条件、操作与证据边界留正文。本轮不制作最终 Slidev 或 PDF。
