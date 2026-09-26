# web-code-snippets

《现代Web开发技术》课程共享代码。本仓库由课件仓库
[`buptnetwork/web-development-slidev`](https://github.com/buptnetwork/web-development-slidev)
的 `snippets/` 目录通过 [git subtree](https://git-scm.com/book/en/v2/Git-Tools-Advanced-Merging#_subtree_merge)
拆分而来,单独发布给学生;课件仍按原路径 `<<< @/snippets/...` 引用这些示例。

## 目录

| 路径 | 内容 |
|---|---|
| `lesson00/` | 课前课 Python 素材:注解/装饰器演示、调用栈与 traceback、`mini/` 迷你分层示例、`demo_server.py` |
| `ch01/first-api/` | **当前第 1 课**：列表起始版、详情骨架、M0 参考、黑盒自检与教师对照 |
| `ch01/m0-tracer/` | 历史「请求全链路」示例与取证脚本；不作为新版 M0 |
| `external.ts` | Slidev 代码外置导入(`<<<`)的 TypeScript region 示例 |

## first-api：当前第 1 课

先进入 `ch01/first-api/`，要求 Python 3.12 与 [uv](https://docs.astral.sh/uv/)。`.python-version` 固定 3.12.12，`uv.lock` 锁定依赖；运行时只有 FastAPI／Uvicorn，debugpy 在开发依赖组。无需数据库、旧包或 Slidev 的 Node 环境。

### 安装与启动

```bash
uv sync --frozen
source .venv/bin/activate    # macOS / Linux
```

Windows PowerShell 用 `.venv\Scripts\Activate.ps1` 激活；若执行策略阻止激活，可在包根直接用 `.venv\Scripts\python.exe -m uvicorn main:app --app-dir exercise --host 127.0.0.1 --port 8000`，不必放宽全局执行策略。教师课前完成环境下载，课堂使用已准备环境。

激活后，进入当前阶段并启动：

```bash
cd exercise
python -m uvicorn main:app --host 127.0.0.1 --port 8000
```

| 目录／文件 | 使用阶段与理解边界 |
|---|---|
| `starter/main.py` | 教师示范正常列表；应用与路由要求解释，固定数据要求会用 |
| `exercise/main.py` | 学生补详情的找到／未找到分支，再加最小日志与 healthz；不要同时注册两份同路径端点 |
| `reference/main.py` | 独立尝试后对照的完整答案，不用它冒充本人实作 |
| `experiments/untyped/main.py` | 教师无注解对照：入口 qid 是 str，与整数 id 比较失败后 404 |
| `experiments/missing/main.py` | 教师缺失分支对照：`MISSING_RETURN=null`（默认）或 `empty`，分别为 null／{}＋200 |
| `check_m0.py` | 学生会运行、会读结果；内部为黑盒 |
| `verify_examples.py` | 教师真实回环 HTTP 验证器，不要求学生编写或解释 |

所有阶段均用 `main:app`，由工作目录区分。切换前停止旧服务；**不用 `--reload`，修改后停止、重启再访问**。不关闭未知端口进程。教师切入实验目录时也先激活本包环境，不从旧 m0-tracer 导入任何实现。

### M0 契约与自检

第二终端激活同一环境、进入 `exercise`，让第一终端的服务继续运行：

```bash
python ../check_m0.py
python ../check_m0.py --base-url http://127.0.0.1:8001 --timeout 3
```

默认回环地址 8000；另一个端口只有在你已明确把服务开在该处时才使用。只发 GET，禁止自动重定向与环境代理；每次超时默认 3 秒，范围大于 0 且不超过 30 秒。报告逐项通过／失败；全部通过退出 0，失败退出 1。

- `/questions`：200，外壳只有 `items`，三条记录顺序 3／2／1。
- `/questions/3`、`/questions/2`、`/questions/1`：200，对应完整记录，只有 `id/title/body`，不套列表外壳。
- `/questions/999`、`/questions/0`、`/questions/-1`：404，`{"detail":"问题不存在"}`。
- `/not-a-route`：404，`{"detail":"Not Found"}`。
- `/questions/abc`：422，JSON 响应，不逐字固定框架的版本相关文案。
- `/healthz`：200，`{"status":"ok"}`；仅存活，不检查数据库或所有业务。

自检前恢复起始版的三个虚构标题与正文；检查内容及顺序，不计 JSON 键顺序、空白或中文转义。不新增 author、tags、created_at、搜索分页、request-id。自检只看 HTTP 行为，不约束函数名或循环写法；“是否进入端点”要用实际入口日志／断点观察。未补全的 exercise 自检不通过是预期。

### 调试与教师验证

VS Code 直接打开 `first-api` 文件夹，安装 Python／Python Debugger 扩展，选择本包 `.venv` 解释器。停止相同端口的终端服务；运行“第 1 课：我的详情练习”，在已加入的 `print` 行下断点，访问 `/questions/3`，观察 `qid` 值和类型，截图后继续。附带起始版、练习、参考与无注解四种配置；均不写死解释器路径。

PyCharm 等价配置：Python 模块 `uvicorn`，参数 `main:app --host 127.0.0.1 --port 8000`，cwd 指向 `exercise`，解释器选本包 `.venv`，不加 reload。这里只提供操作指引，不宣称附带 PyCharm 项目文件或真实 IDE 停点已经验收。

教师在包根运行：

```bash
uv run --frozen python verify_examples.py
```

验证器仅启停自己的回环子进程，临时构造的缺陷不修改学生文件。10 个测试覆盖参考与 CLI、起始版、骨架失败、无注解、两种404与422入口、null／{}错误200、写死详情、改值重启恢复、自检边界与调试配置。配置静态检查不替代 IDE、浏览器视觉或课堂试讲。

第 2 课 SQLite／搜索分页／同源页面起点包**尚未制作**，不算 M0 欠账。当前源码与课件用同一份 region；本轮尚未同步到远端 snippets 仓库。

## 历史资产：m0-tracer

以下只用于重现旧课堂，不是新版第一课任务。旧数据库／SQL／request-id／四处取证与旧自检，不能叠加到 first-api 的 M0。

在 `ch01/m0-tracer/` 目录下执行,要求 Python 3.12 与 [uv](https://docs.astral.sh/uv/):

```bash
uv sync --frozen
uv run python seed.py                                   # 初始化演示用 SQLite
uv run uvicorn v1_ai_raw:app --host 127.0.0.1 --port 8000
```

- `v1_ai_raw:app`:能运行的反例(拼接 SQL、详情不存在仍返回 200)。
- `v2_traceable:app`:旧课堂目标,支持 `TRACE_MODE=plain|trace`、`SQL_ECHO=1` 等开关。
- `v3_m0:app`:旧 M0 参考实现。
- `verify_m0.py` / `bench.py` / `capture_evidence.py`:验收、并发与取证脚本;`make verify` 为默认检查。

复制 `.env.example` 为 `.env` 后,用 `uv run --env-file .env ...` 显式加载。默认数据库为
`sqlite:///./demo.db`,结构与固定虚构数据见 `seed.sql` / `seed.py`;复位执行
`uv run python seed.py --reset`。

## 说明

- `.venv`、`__pycache__`、`.capture/`、`*.db`、`.env` 等运行产物与本地凭据已由 `.gitignore` 排除,不入库。
- 全部数据与示例均为教学虚构,不连接任何生产数据。
- 本仓库通常由课件仓库通过 subtree 单向发布;如需回改,请在课件仓库修改 `snippets/` 后 `git subtree push`,避免两端并发编辑。
