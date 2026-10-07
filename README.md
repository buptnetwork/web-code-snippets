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
| `ch01/search-page/` | **当前第 2 课**：SQLite 搜索分页接口、同源四态搜索页起点、故障切换设施与黑盒自检 |

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

所有阶段均用 `main:app`，由工作目录区分。切换前停止旧服务；**不用 `--reload`，修改后停止、重启再访问**。不关闭未知端口进程。教师切入实验目录时也先激活本包环境。

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

第 2 课起点包已制作，见下方 `search-page` 一节，不算 M0 欠账。第 1 课源码与课件仍用同一份 region。

## search-page：当前第 2 课

进入 `ch01/search-page/`，要求 Python 3.12 与 [uv](https://docs.astral.sh/uv/)。`.python-version` 固定 3.12.12，`uv.lock` 锁定依赖；运行时只有 FastAPI／Uvicorn（SQLite 用标准库 `sqlite3`，同源静态挂载用 Starlette），debugpy 在开发依赖组。页面与 API 同源，无 Node 构建。

### 安装与启动

```bash
uv sync --frozen
source .venv/bin/activate    # macOS / Linux
python -m uvicorn server:app --host 127.0.0.1 --port 8000
```

Windows PowerShell 用 `.venv\Scripts\Activate.ps1` 激活。启动后浏览器打开 `http://127.0.0.1:8000/` 即同源搜索页；首次启动自动建库播种（`questions.db`，已被 `.gitignore` 排除）。**不用 `--reload`**，改代码后停止、重启再访问；不关闭未知端口进程。

| 目录／文件 | 使用阶段与理解边界 |
|---|---|
| `server.py` | 同源静态挂载＋搜索分页＋详情/healthz＋故障切换；页面挂载与故障设施要求会用／黑盒 |
| `question_store.py` | SQLite 数据模块：建库播种、搜索分页、详情；内部要求会用，不解释 SQL 与连接 |
| `static/index.html` | HTML 骨架（form/label/input/button/status/results），要求会用 |
| `static/app.js` | **学生工作文件**：已给元素引用、`readQuestions`、`renderQuestions` 与最小入口；在 `region task` 内补四态并替换最小入口 |
| `static/styles.css` | 给定样式，只保证可读与四态可辨，不考布局 |
| `reference/app.js` | 完整四态参考（`setState`/`loadQuestions`/`busy`/`finally`），独立尝试后对照，不冒充本人实作 |
| `experiments/predict/` | 第五单元预测实验页：故意不检查 `res.ok` 的隔离片段 |
| `check_page.py` | 学生会运行、会读结果；黑盒自检搜索契约与同源可访问性 |
| `verify_examples.py` | 教师真实回环 HTTP 验证器，不要求学生编写或解释 |

### 搜索契约与自检

- `GET /questions?keyword=...&page=1&page_size=20`：200，`{"items":[...],"total":N,"page":N}`；记录含 `id/title/body`，按 id 降序后分页。
- 关键词去首尾空白，在标题或正文做字面子串匹配；英文不区分大小写，`%`／`_` 不作通配符。
- 空关键词三条、`react` 一条（id 3）、无匹配为 200 空 `items`（不是 404）；`page<1` 或 `page_size` 超出 1–50 返回 422。
- `GET /questions/3` 返回记录，`/questions/999` 返回 404 `{"detail":"问题不存在"}`，`/healthz` 返回 `{"status":"ok"}`（不查库）。

第二终端激活同一环境、在包根运行：

```bash
python check_page.py
python check_page.py --base-url http://127.0.0.1:8001 --timeout 3
```

自检运行前把故障模式复位为 `normal`；只发本地 GET 与一次复位 POST，禁止重定向与环境代理，超时默认 3 秒。11 项覆盖搜索三态、详情/404/422、探针、页面入口与静态脚本；全部通过退出 0，失败退出 1。四态行为、恢复与安全渲染由课堂观察与 `reference/app.js` 对照，不在自检内自动判定。

### 故障切换设施（黑盒）

搜索页地址与 `/questions` 调用关系保持不变；用独立教师端点切换故障，不污染业务参数：

```bash
curl -X POST http://127.0.0.1:8000/__teacher/fault \
  -H 'Content-Type: application/json' -d '{"mode":"http500_json"}'
curl -X POST http://127.0.0.1:8000/__teacher/fault \
  -H 'Content-Type: application/json' -d '{"mode":"normal"}'
```

| mode | `/questions` 表现 | 对应课堂失败阶段 |
|---|---|---|
| `normal` | 正常搜索 | — |
| `delay` | 有界延迟（默认 1 秒）后正常，用于演示 loading | 加载态 |
| `http500_json` | 500 ＋ JSON 错误体 | `!response.ok` 主动抛错 |
| `http500_html` | 500 ＋ HTML | `!response.ok` 主动抛错 |
| `json200_html` | 200 ＋ HTML | `.json()` 解析失败 |
| `struct200` | 200 ＋ `{"items":null}` | 结构检查失败 |

也可用环境变量 `FAULT_MODE`（启动即生效）、`DELAY_SECONDS`、`DB_PATH` 覆盖。一次只启用一种，切换后由用户手工提交，结束后复位 `normal`。网络失败用浏览器 Offline 制造，不是服务端模式。

### 教师验证

```bash
uv run --frozen python verify_examples.py
```

13 个测试覆盖搜索契约、详情/404/422、同源静态、六种故障模式、有界延迟、启动即故障、种子幂等与搜索规则（大小写／通配符／分页）、参考页四态源码、学生起点最小化、预测片段与调试配置。验证器仅启停自己的回环子进程并用临时数据库，不修改学生文件；配置与源码静态检查不替代真实浏览器操作、Offline 与课堂试讲。

## 说明

- `.venv`、`__pycache__`、`.capture/`、`*.db`、`.env` 等运行产物与本地凭据已由 `.gitignore` 排除,不入库。
- 全部数据与示例均为教学虚构,不连接任何生产数据。
- 本仓库通常由课件仓库通过 subtree 单向发布;如需回改,请在课件仓库修改 `snippets/` 后 `git subtree push`,避免两端并发编辑。
