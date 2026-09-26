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

## 第一次课：第一个 Web 接口

新版按 [v4 大纲](docs/syllabus-v4.md) 组织为 **7 章／16 次课**，另保留 ch00 课前准备；完整映射见[课程约定](docs/course-conventions.md)。当前仅启用 ch01 中的第 1 次课，第 2 次课与 ch02–ch07 尚未制作，不提供空入口。

成稿入口 [ch01.md](ch01.md)，正文与备注 [pages/ch01/01.md](pages/ch01/01.md)，课后卡片 [01-reference.md](pages/ch01/01-reference.md)。当前 45 页：3 页章节定位＋35 页正文＋7 页参考。路线为正确列表 → 学生独立补详情 → 参数与失败位置 → 五框请求图 → M0；95 分钟教学＋5 分钟缓冲。底稿只保留归档快照，后续修改最终工程。

```bash
pnpm exec slidev ch01.md --port 3031
pnpm exec slidev build ch01.md --base /web-2026b/ch01/ --out .build-check/ch01
```

### 新版独立课堂包

以下在 **`snippets/ch01/first-api` 目录**执行，要求 Python 3.12 与 uv。使用本包独立环境，不启动旧 m0-tracer，不初始化数据库：

```bash
uv sync --frozen
source .venv/bin/activate     # macOS / Linux
cd exercise
python -m uvicorn main:app --host 127.0.0.1 --port 8000
```

PowerShell 激活命令为 `.venv\Scripts\Activate.ps1`；其余命令相同。教师课前完成安装，学生不在课堂首次下载。目录职责：
- `starter/main.py`：正确列表，供教师示范。
- `exercise/main.py`：学生补详情、最小日志与探针；未完成时自检失败正常。
- `reference/main.py`：完整 M0 参考，独立尝试后再看。
- `experiments/`、`verify_examples.py`：教师类型／缺失分支对照与验证设施，不是额外学生作业。

三个阶段都以 `main:app` 启动，靠工作目录区分；切换或修改后 **Ctrl+C 停止，再启动**，不用 `--reload`。不随意关闭未知端口进程。

### 调试、自检与边界

第二终端激活同一环境、进入 `exercise`，保持第一个终端的服务运行：

```bash
python ../check_m0.py
# 若自己改过端口，可显式指定：
python ../check_m0.py --base-url http://127.0.0.1:8001
```

自检是标准库黑盒 HTTP 客户端，只向本机发送 GET，默认每请求超时 3 秒。检查固定三条记录及顺序、列表／详情／两种 404／422／存活探针，共 10 条；失败退出非零，不限定函数名和查找写法，不据此证明断点已验。

VS Code **直接打开 first-api 文件夹**，安装 Python／Python Debugger 扩展并选中本包 `.venv` 解释器，运行附带配置“第 1 课：我的详情练习”。在自己加入的 `print` 行下断点，访问 `/questions/3`，观察 `qid` 值和类型，截图后继续。PyCharm 等价设置：模块 `uvicorn`、参数 `main:app --host 127.0.0.1 --port 8000`、cwd 为 exercise、本包解释器，无 reload。配置不写死机器路径；真实 IDE 停点仍需授课前补验。

教师在 first-api 包根复跑：

```bash
uv run --frozen python verify_examples.py
```

独立版本：Python 3.12.12、FastAPI 0.141.1、Starlette 1.6.0、Uvicorn 0.53.0、debugpy 1.8.22；精确依赖以本包 `uv.lock` 为准。具体验证、浏览器状态及缺口见[本轮移交记录](docs/lesson-draft-rewrite-handover.md#12-第-1-课-slidev-与最小配套移交)。代码完整说明见 [snippets/README.md](snippets/README.md)。

新版 M0 不含数据库、搜索分页、request-id 或前端。第 2 课 SQLite 与页面起点包尚未制作；网页与源码是本次交付，PDF 非必交，投影与 25 分钟学生任务试讲仍待教师实测。

### 历史材料

`snippets/ch01/m0-tracer/`、`public/images/ch01/evidence.json` 和旧取证图保持原样，仅供历史参考；它们的数据库、SQL、四处取证与旧 M0 自检不再是新版第一课要求。旧包运行见 [snippets 说明](snippets/README.md#历史资产m0-tracer)，历史验证见 [slides 修订交接](docs/slides-revision-handover.md)。ch00 仅同步版本提示和直接交接，其余旧路线仍待更新，不能将历史任务叠加给学生。

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
├── ch01.md            # 第 1 章 Web 入门：接口与页面（现含第1课）
├── pages/
│   ├── ch00/          # 课程导论，章内分节，一次课一个文件，用 src: 引入
│   │   └── 00-lecture-zero.md        # 导论第0讲
│   │   └── 00-lecture-one.md        # 导论第1讲
│   │   └── 02-lecture-two.md        # 导论第2讲
│   └── ch01/          # 第1章
├── components/        # 全课程共享 Vue 组件（结构可视化等）
├── snippets/          # 可用 <<< 引入的示例代码（独立仓库 subtree，见下）
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

## snippets 独立仓库（git subtree）

`snippets/` 已提取为独立仓库 [`buptnetwork/web-code-snippets`](https://github.com/buptnetwork/web-code-snippets)（分支 `main`），单独共享给学生；课件仍通过原路径 `<<< @/snippets/...` 引用，构建不受影响。本仓库以 git subtree 方式接回该目录，remote 名为 `snippets`。

同步命令（在本仓库根目录执行）：

```bash
# 拉取独立仓库的最新改动到 snippets/（--squash 保持本仓库历史整洁）
git subtree pull --prefix=snippets snippets main --squash

# 把本仓库对 snippets/ 的改动推送回独立仓库
git subtree push --prefix=snippets snippets main
```

- 首次 clone 本仓库后无需额外操作，`snippets/` 内容随仓库一起拉取。
- `.venv`、`__pycache__`、`.capture/`、`*.db` 等运行产物仍由根 `.gitignore` 排除，不进入任一仓库。
- 同一时间只在一端修改后再同步，避免双向并发编辑产生冲突。

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

- 新增一章：在根目录建 `chXX.md`，章内按次课拆到 `pages/chXX/*.md`，入口用 `src: ./pages/chXX/NN.md` 引入（NN 为全课程课次）；具体目录与代码资产约定见[课程约定](docs/course-conventions.md)。
- 章节封面、背景和徽标以[课程约定](docs/course-conventions.md)为准，不再分散维护。
- `pnpm build` 自动扫描根目录全部章节入口；新增章节后同步 `netlify.toml` / `vercel.json` 的路由，详见上方部署说明。
- 资源放 `public/`；绝对路径引用、备注、代码 region 及 UnoCSS/SVG 避坑统一见[Slidev 实施指南](docs/slidev-authoring-guide.md)。
- 迁移新课程时复用通用流程与适用的实施指南，重新确认课程约定；不默认继承数据结构的目录命名、技术栈或机构标识。
