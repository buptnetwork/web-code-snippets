# 现代Web开发技术课程课件

基于 [Slidev](https://sli.dev/) 制作的《现代Web开发技术》教学课件。全课程共用一个 Slidev 项目，每章一个入口 md 文件。

课件采用内容详实型设计，优先教学内容的价值与页面美观，兼顾课后查阅；不默认追求极简或增加师生互动。内容质量基线见通用流程，视觉制作与检查方法见 Slidev 实施指南。

## 使用

```bash
pnpm install
pnpm dev                    # 打开 ch00（默认入口）
pnpm dev:ch ch01.md --open  # 打开指定章节
pnpm build                  # 整站构建到 dist/（部署前缀见 scripts/build-site.mjs）
pnpm export                 # 导出 PDF（需先装 playwright-chromium）
```

## 第一次课：请求全链路

成稿入口为 `ch01.md`，正文与备注在 `pages/ch01/01.md`，包含教学正文、作业工具卡与准备附录。课前课聚焦“运行工具与代码阅读”，第一课保持“观察与取证”；分层和框架设计留后续课。节奏为 95 分钟＋5 分钟缓冲，作业工具卡供课后查阅，不挤占现场取证；底稿已归档，后续只修改最终工程。

```bash
pnpm exec slidev ch01.md --port 3031
pnpm exec slidev build ch01.md --base /web-2026b/ch01/ --out .build-check/ch01
```

### 单文件演示与阶段切换

示例是按底稿在本工程重建的，不是外部 `m0-tracer` 仓库的 Git tags。三个阶段各保留独立单文件；`v3_m0.py` 是课后参考，不被导入 slides 或复制到 public。发布学生材料时，只选取对应阶段，不能把整个目录当作课前包分发。

以下在 **`snippets/ch01/m0-tracer` 目录**执行，要求 Python 3.12 与 uv：

```bash
uv sync --frozen
uv run python seed.py
uv run uvicorn v1_ai_raw:app --host 127.0.0.1 --port 8000
```

- `v1_ai_raw:app`：能运行的反例，POST 查询、拼接 SQL、详情不存在仍返回 200。
- `v2_traceable:app`：课堂目标。先设 `TRACE_MODE=plain DEMO_DELAY_MS=80`，再切 `TRACE_MODE=trace DEMO_DELAY_MS=80`；第二终端执行 `uv run python bench.py`，同时手动发一次请求。
- 四处合流：停止并发，启动 `TRACE_MODE=trace SQL_ECHO=1 uv run uvicorn v2_traceable:app`。不再设置人为延迟，使用一次性的合法 id（1–64 个字母、数字、点、下划线或连字符）。
- 学生从同目录的 `v2_traceable.py` 复制为 `student_app.py` 读改：搜索迁移 `GET /questions`，详情改为 `GET /questions/{qid}`，增加 `GET /healthz`。保留日志、中间件与静态页面；允许查文档和 AI 辅助，但须解释改动并提交检查结果，不要求从零写框架。
- `v3_m0:app`：以上任务的课后参考；新 API 提示与完整验收约定已放入第一课作业页。
- 每次切换先停止上一个服务，避免端口冲突。每次启动重建 `server.log`，先保存必要证据；80ms 延迟仅用于日志交织，不是性能基准。
- 复制 `.env.example` 为 `.env` 后，使用 `uv run --env-file .env ...` 显式加载；仅创建文件不会自动加载。`.env` 已忽略，不能提交真实凭据。
- shell 内联环境变量是 macOS / Linux 写法；PowerShell 使用 `$env:TRACE_MODE='trace'` 等赋值。

默认 SQLite：`sqlite:///./demo.db`。结构在 `seed.sql`，`seed.py` 写入固定的 30 个问题、15 个回答、5 个标签；全部虚构。需要复位时先停服务，再执行 `uv run python seed.py --reset`。初始化工具只允许名为 `demo.db` 的 SQLite 文件，或本机库名以 `m0_` 开头的 PostgreSQL 教学库。

PostgreSQL 16 / 17 可通过 `DATABASE_URL` 配置：事先创建隔离教学库并给测试账号授权；不连接生产数据。本轮未获得可用 PostgreSQL 服务，**PostgreSQL 未验证**，默认 SQLite 为已验证备用路径。

### 调试、验收与证据

用 VS Code **直接打开 m0-tracer 目录**，安装 Python / Python Debugger 扩展；选附带 `.vscode/launch.json` 的配置，在 `v2_traceable.py` 的 `rows = conn.execute(...)` 处下断点。关闭 reload、`justMyCode=false`；Windows 将解释器路径改为 `.venv/Scripts/python.exe`。先截 Call Stack 与 Variables 中的 rid，继续后再截响应与日志。多行表达式可能再次命中，取证后可移除断点。

```bash
uv run python verify_m0.py --all       # 三个阶段的隔离 SQLite 验证
uv run python verify_m0.py --app student_app
make verify                          # 默认检查 v3_m0 参考答案
uv run python capture_evidence.py     # 重采 HTTP、并发日志、debugpy 停点与 SQL
```

验证器要求待测单文件暴露 `app`、`engine`，从 `DATABASE_URL` / `LOG_FILE` 环境变量读取测试配置；在临时 SQLite 中检查响应、数据、配对日志、SELECT 1、断连后的 503 和恢复。`/boom` 是特意保留的异常路径缺陷，由 v2/v3 阶段测试单独检查，不纳入学生模块的配对日志验收。凭据扫描只是有限 AST 规则，不等于安全审计。当前锁定的 Starlette 使用 HTTPX TestClient 时会发出弃用提示，测试仍通过。

证据采集只使用自身的 `.capture/demo.db` 与回环服务；停止自己启动的进程，不影响已有应用。原始记录与版本在 `public/images/ch01/evidence.json`；页面仅做时间前缀省略、节选和高亮。单次合流来自同一个 HTTP 请求和真实 debugpy 停点，**不是手写模拟数据，也不是 IDE / 终端界面截图**。用相同 id 重发四次不能冒充同一次执行。

已验证环境：Python 3.12.12、FastAPI 0.141.1、Starlette 1.6.0、SQLAlchemy 2.0.54、uvicorn 0.53.0、debugpy 1.8.22；准确锁定版本以 `uv.lock` 为准。SQL echo 本身无 request-id，四处合流在暂停并发后采集；计时含调试暂停，不用作性能证据。

**授课前缺项**：DevTools / 终端 / IDE 原始界面截图及 40 秒 IDE 备用录像待补；当前以真实协议与日志输出重排作有限备用。`/docs` 默认依赖 CDN 脚本，离线可用 curl。PDF 与教室投影未验证，网页可用不代表这些交付形式已验收。

## 课堂互动（课件端已集成）

支持教师面板、单选/多选/自由文本、二维码、公开统计、评论审核与展示端配对入口。默认关闭，公开浏览不请求互动 API、不建立 SSE；只有主动连接课堂后才实时同步。

```bash
VITE_CLASSROOM_ENABLED=true pnpm dev    # 打开底部导航“互动”
VITE_CLASSROOM_ENABLED=true pnpm build  # 构建包含互动入口的静态课件
pnpm test                              # 课堂模块单元测试
pnpm typecheck                         # 课堂集成代码类型检查
```

当前仅完成课件端，后端与学生手机页需要另建项目；未部署时教师操作会提示服务不可用，二维码不能完成真实投稿。登录权限必须由后端执行，Slidev 演讲者模式不是教师认证。

默认同源路径为 `/classroom-api/v1` 和 `/classroom`，不受章节部署前缀影响。章节身份来自 `ch00.md`、`ch01.md` 的 `classroom` headmatter。开发代理、生产接入和 API/SSE 字段契约见[设计文档第 15 节](docs/classroom-interaction-design.md#15-当前课件端落地与联调契约)。

`classroom-interaction` 开发团队请先阅读[交接说明](docs/classroom-interaction-handover.md)，再按[技术说明与接口契约](docs/classroom-interaction-technical-spec.md)实现后端与学生端；文档明确区分现有课件契约、学生接口建议和待完成验收。

## 部署

当前部署目标：**https://study.imedix.cn/web-2026b/**。部署前缀集中在 `scripts/build-site.mjs` 的 `DEPLOY_PREFIX`，更换路径只改这一处。

`pnpm build` 会扫描根目录 `ch*.md` 逐章构建，产物 `dist/web-2026b/` 即完整静态站点（站点根跳转页与 `_redirects` 自动生成）：

- **自建 nginx**：把 `dist/web-2026b/` 上传到 study.imedix.cn 站点根目录，并在其 `server` 块中加一条路由兜底（一条覆盖全部章节）：
  ```nginx
  location ~ ^/web-2026b/(ch\d+)/ { try_files $uri $uri/ /web-2026b/$1/index.html; }
  ```
- **Netlify / Vercel**：发布 `dist/`（配置已含 `/web-2026b/` 前缀规则），访问 `站点域名/web-2026b/`
- 翻页路由（`/web-2026b/ch00/45` 这类路径）依赖上述 fallback——**新增章节时只需同步 `netlify.toml` 与 `vercel.json`**（nginx 规则与构建脚本均自动覆盖）

## 目录结构

```
.
├── ch00.md            # 各章入口（必须放在仓库根，Slidev 的约定目录相对入口解析）
├── ch01.md            # 第 1 章 绪论
├── pages/
│   ├── ch00/          # 课程导论，章内分节，一次课一个文件，用 src: 引入
│   │   └── 00-lecture-zero.md        # 导论第0讲
│   │   └── 00-lecture-one.md        # 导论第1讲
│   │   └── 02-lecture-two.md        # 导论第2讲
│   └── ch01/          # 第1章
├── components/        # 全课程共享 Vue 组件（结构可视化等）
├── snippets/          # 可用 <<< 引入的示例代码
├── public/            # 静态资源，用 / 开头的绝对路径引用
│   ├── images/        # 位图：common/ 为全课通用，chXX/ 为各章专属
│   ├── diagrams/      # SVG 图示，同上分章
│   ├── videos/
│   └── fonts/
├── scripts/           # 构建辅助脚本
│   └── build-site.mjs      # 整站构建：章节扫描、--base 部署前缀、站点根文件生成
└── docs/              # 流程指南、教学底稿与历史记录，不参与构建
    ├── authoring-workflow.md          # 跨课程通用制作流程
    ├── lesson-draft-guide.md          # 教师编写教学底稿的指南
    ├── slidev-authoring-guide.md      # Slidev 语法、视觉制作与验证方法
    ├── course-conventions.md          # 当前课程的工程、视觉与教学检查约定
    ├── history/authoring-workflow-legacy.md  # 改造前流程与实测记录
    ├── draft/ch00/ch00.md             # 导论教案（已归档，以最终课件工程为准）
    └── slidev-starter-*.md.bak        # Slidev 官方模板 demo 留档
```

## 文档导航

| 需要做什么 | 阅读入口 |
|---|---|
| 教师准备一次课 | [教学底稿编写指南](docs/lesson-draft-guide.md) |
| 内容质量基线、制作职责与分层验收 | [通用制作流程](docs/authoring-workflow.md) |
| 信息层级、版式、截图、代码呈现与验证 | [Slidev 实施指南](docs/slidev-authoring-guide.md) |
| 本课程版式与代码资产、C/C++ 教学检查 | [当前课程约定](docs/course-conventions.md) |
| 查询旧设计、评审及实测证据 | [历史快照](docs/history/authoring-workflow-legacy.md)（非现行规范） |
| 启用课件互动、对接独立后端 | [课堂互动系统设计](docs/classroom-interaction-design.md)（课件端已实现，后端与学生端待开发） |
| 实现互动 API、SSE 与学生页面 | [classroom-interaction 技术说明](docs/classroom-interaction-technical-spec.md) |
| 开发团队接手、联调、部署与验收 | [classroom-interaction 交接说明](docs/classroom-interaction-handover.md) |

教师主要阅读底稿指南；AI 执行时同时读取通用流程、Slidev 实施指南和当前课程约定。通用流程可迁移到其他软件类课程，当前仓库仍专用于《现代Web开发技术》。

## 当前工程约定

- 新增一章：在根目录建 `chXX.md`，章内按次课拆到 `pages/chXX/*.md`，入口用 `src: ./pages/chXX/01-xxx.md` 引入；具体目录与代码资产约定见[课程约定](docs/course-conventions.md)。
- 章节封面、背景和徽标以[课程约定](docs/course-conventions.md)为准，不再分散维护。
- `pnpm build` 自动扫描根目录全部章节入口；新增章节后同步 `netlify.toml` / `vercel.json` 的路由，详见上方部署说明。
- 资源放 `public/`；绝对路径引用、备注、代码 region 及 UnoCSS/SVG 避坑统一见[Slidev 实施指南](docs/slidev-authoring-guide.md)。
- 迁移新课程时复用通用流程与适用的实施指南，重新确认课程约定；不默认继承数据结构的目录命名、技术栈或机构标识。
