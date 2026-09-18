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
│   │   └── 00-lecture-two.md        # 导论第2讲
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
