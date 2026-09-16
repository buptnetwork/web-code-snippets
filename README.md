# 现代Web开发技术课程课件

基于 [Slidev](https://sli.dev/) 制作的《现代Web开发技术》教学课件。全课程共用一个 Slidev 项目，每章一个入口 md 文件。

## 使用

```bash
pnpm install
pnpm dev                    # 打开 ch00（默认入口）
pnpm dev:ch ch01.md --open  # 打开指定章节
pnpm build                  # 整站构建到 dist/（部署前缀见 scripts/build-site.mjs）
pnpm export                 # 导出 PDF（需先装 playwright-chromium）
```

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
│   ├── ch00/          # 课程导论
│   │   └── 01-introduction.md        # 导论全文（45 页 / 70 分钟）
│   └── ch01/          # 章内分节，一次课一个文件，用 src: 引入
│       ├── 01-basic-concepts.md      # 第 1 次课：基本概念
│       └── 02-algorithm-analysis.md  # 第 2 次课：算法分析
├── components/        # 全课程共享 Vue 组件（结构可视化等）
│   └── UnitNav.vue    # 导论专用：五条理由的全场导航条
├── snippets/          # 可用 <<< 引入的示例代码
├── public/            # 静态资源，用 / 开头的绝对路径引用
│   ├── images/        # 位图：common/ 为全课通用，chXX/ 为各章专属
│   ├── diagrams/      # SVG 图示，同上分章
│   ├── videos/
│   └── fonts/
├── scripts/           # 构建辅助脚本
│   └── build-site.mjs      # 整站构建：章节扫描、--base 部署前缀、站点根文件生成
└── docs/              # 流程规范、讲稿/教案初稿，不参与构建
    ├── authoring-workflow.md          # 课件制作流程规范
    ├── lesson-draft-guide.md          # 教师编写教学底稿的指南
    ├── draft/ch00/ch00.md             # 导论教案（已归档，以 md 课件为准）
    └── slidev-starter-*.md.bak        # Slidev 官方模板 demo 留档
```

## 约定

- 内容编写与生成流程见 [docs/authoring-workflow.md](docs/authoring-workflow.md)，其中的五条硬规则对所有章节生效。
- 内容作者（教师）编写各次课教学底稿，见 [docs/lesson-draft-guide.md](docs/lesson-draft-guide.md)。
- 新增一章：在根目录建 `chXX.md` 作为入口，章内按"次课"拆到 `pages/chXX/*.md`，入口用 `src: ./pages/chXX/01-xxx.md` 引入。
- 章封面沿用统一规范（共用背景图 + 组合标志反白），新增章节时照抄 `ch00.md` 首屏，见 [docs/authoring-workflow.md](docs/authoring-workflow.md) §9「已登记版式」。
- `pnpm build` 会自动扫描构建根目录全部 `chXX.md`（无需修改脚本或命令）；新增章节后只需给 `netlify.toml` / `vercel.json` 各补一条该章路由规则（nginx 兜底与 `dist/_redirects` 均自动覆盖新章）。
- 资源统一放 `public/`，引用写绝对路径，如 `![单链表](/diagrams/ch01/linked-list.svg)`。
  frontmatter 里的 `background:` / `image:` 不经 Vite 转换，必须用这种绝对路径。
- 图示优先用 SVG 或 `mermaid` 代码块，导出 PDF 时不会发虚。
- 讲述性内容放 slide 末尾的 `<!-- -->` 注释块，作为演讲者备注。

### 内联 SVG 的两个坑（UnoCSS attributify 导致）

项目开了 attributify 模式，SVG 的部分呈现属性会被当成工具类改写，写内联 SVG 时必须避开：

- **不要用 `font-size="12"`**，会被解析成 `font-size-12` → `3rem`（约 4 倍），文字撑爆后被 `overflow:hidden` 裁掉。改写内联样式：`style="font-size:12px"`。
- **`<text>` 不要用 `fill="currentColor"` 或依赖默认填充，也不要加 `opacity=` 属性**，否则整段文字不渲染。一律写死颜色：`fill="rgb(71,85,105)"`。
- 结构性图示（分层框、流程块）优先用 HTML + UnoCSS 拼，比 SVG 可控；SVG 只用来画曲线、多边形这类几何图形。
