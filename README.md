# web-code-snippets

《现代Web开发技术》课程的示例代码，配合课堂使用。每个工程都用 [uv](https://docs.astral.sh/uv/) 锁定依赖，按下面的步骤就能在自己电脑上跑起来。

## 目录

| 路径 | 对应课 | 你会用到什么 |
|---|---|---|
| `lesson00/` | 课前课 | Python 注解／装饰器演示、调用栈与 traceback 样本、`mini/` 迷你分层示例、`demo_server.py` |
| `ch01/first-api/` | 第 1 课 | 从列表接口到补详情，含 M0 自检 |
| `ch01/search-page/` | 第 2 课 | 搜索分页接口 ＋ 同源四态搜索页，含黑盒自检 |
| `ch02/question-api/` | 第 3 课 | 用 Pydantic 声明输入／输出模型，补一个带校验的创建接口，含黑盒自检 |

## 环境准备（每个工程一次）

1. 安装 Python 3.12 与 [uv](https://docs.astral.sh/uv/)。
2. 进入工程目录，执行下面命令按 `uv.lock` 装好依赖，并生成 `.venv`：

   ```bash
   uv sync --frozen
   ```

3. 激活虚拟环境：

   ```bash
   source .venv/bin/activate        # macOS / Linux
   .venv\Scripts\Activate.ps1       # Windows PowerShell
   ```

   如果 Windows 执行策略阻止激活，可不激活，直接把后面命令里的 `python` 换成 `.venv\Scripts\python.exe`。

> 每个工程的 `.python-version` 已固定为 3.12.12。运行时只依赖 FastAPI／Uvicorn，不需要额外安装数据库服务，也不需要 Node 环境。

---

## 第 1 课 · first-api

进入 `ch01/first-api/`，完成上面的[环境准备](#环境准备每个工程一次)。

### 启动

```bash
cd exercise
python -m uvicorn main:app --host 127.0.0.1 --port 8000
```

浏览器打开 <http://127.0.0.1:8000/questions>。改完代码后**先停止再重启**（不要用 `--reload`）；切换目录前也要先停掉旧服务。

### 文件说明

| 目录／文件 | 怎么用 |
|---|---|
| `starter/main.py` | 课堂跟随的正常列表版；先读懂应用与路由 |
| `exercise/main.py` | **你的工作文件**：补详情的「找到／未找到」分支，再加最小日志与 `healthz`。同一路径不要注册两次 |
| `reference/main.py` | 完整答案，自己写完再对照 |
| `check_m0.py` | 自检脚本，你会运行并读它的结果 |

> 三个版本都用 `main:app` 启动，靠所在工作目录区分。

### 自检 M0

保持服务运行，**另开一个终端**，激活同一环境并进入 `exercise`：

```bash
python ../check_m0.py
# 若服务开在别的端口：
python ../check_m0.py --base-url http://127.0.0.1:8001 --timeout 3
```

自检只发本地 GET，全部通过退出码为 0，否则为 1。**`exercise` 还没补完时自检不通过是正常的。** 期望行为：

- `/questions`：200，外壳 `{"items":[...]}`，三条记录顺序 3／2／1。
- `/questions/3`、`/questions/2`、`/questions/1`：200，对应完整记录，只有 `id/title/body`。
- `/questions/999`、`/questions/0`、`/questions/-1`：404，`{"detail":"问题不存在"}`。
- `/questions/abc`：422（路径参数不是整数）。
- `/healthz`：200，`{"status":"ok"}`。

### 在 IDE 里调试

**VS Code**：打开 `first-api` 文件夹，安装 Python／Python Debugger 扩展，解释器选本工程的 `.venv`。运行配置「第 1 课：我的详情练习」，在 `exercise/main.py` 的 `print` 行下断点，访问 `/questions/3`，观察 `qid` 的值和类型。启动调试前先停掉占用同端口的终端服务。

**PyCharm**：新建运行配置，模块名 `uvicorn`，参数 `main:app --host 127.0.0.1 --port 8000`，工作目录指向 `exercise`，解释器选本工程 `.venv`，不要勾选 reload。

---

## 第 2 课 · search-page

进入 `ch01/search-page/`，完成上面的[环境准备](#环境准备每个工程一次)。

### 启动

```bash
python -m uvicorn server:app --host 127.0.0.1 --port 8000
```

浏览器打开 <http://127.0.0.1:8000/> 就是同源搜索页（页面和接口是同一个地址）。首次启动会自动建库并播种 `questions.db`（已被 `.gitignore` 忽略）。改完代码**先停止再重启**（不要用 `--reload`）。

### 文件说明

| 目录／文件 | 怎么用 |
|---|---|
| `static/app.js` | **你的工作文件**：已给好元素引用、`readQuestions`、`renderQuestions` 和一个最小入口；在 `region task` 内补齐 loading／success／empty／error 四态，并用它替换最小入口（最终只保留一个提交监听器） |
| `static/index.html` | 页面骨架，直接用 |
| `static/styles.css` | 给定样式，不用改布局 |
| `reference/app.js` | 完整四态参考，自己写完再对照 |
| `server.py`、`question_store.py` | 接口与数据层，课堂当黑盒使用，不用改 |
| `experiments/predict/` | 课堂预测实验页 |
| `check_page.py` | 自检脚本，你会运行并读它的结果 |

### 搜索接口

- `GET /questions?keyword=...&page=1&page_size=20` → `{"items":[...],"total":N,"page":N}`，记录含 `id/title/body`，按 id 降序分页。
- 关键词去首尾空白后，在标题或正文做子串匹配；英文不分大小写，`%`／`_` 不当通配符。
- 空关键词返回三条、`react` 返回一条（id 3）、无匹配是 200 空 `items`（**不是 404**）；`page<1` 或 `page_size` 超出 1–50 返回 422。
- `GET /questions/3` 返回记录，`/questions/999` 返回 404，`/healthz` 返回 `{"status":"ok"}`。

### 自检

保持服务运行，**另开一个终端**，激活同一环境、在 `search-page` 目录下：

```bash
python check_page.py
# 若服务开在别的端口：
python check_page.py --base-url http://127.0.0.1:8001 --timeout 3
```

自检会先把故障模式复位为 `normal`，共 11 项，全部通过退出码为 0，否则为 1。

### 课堂练习：切换故障模式

搜索页地址和 `/questions` 调用都不用改；用下面的端点切换故障，观察页面四态变化：

```bash
# 打开一种故障（例：500 + JSON 错误体）
curl -X POST http://127.0.0.1:8000/__teacher/fault \
  -H 'Content-Type: application/json' -d '{"mode":"http500_json"}'

# 练完复位
curl -X POST http://127.0.0.1:8000/__teacher/fault \
  -H 'Content-Type: application/json' -d '{"mode":"normal"}'
```

| mode | `/questions` 表现 | 页面应进入的状态 |
|---|---|---|
| `normal` | 正常搜索 | success / empty |
| `delay` | 延迟（默认 1 秒）后正常返回 | loading |
| `http500_json` | 500 ＋ JSON 错误体 | error |
| `http500_html` | 500 ＋ HTML | error |
| `json200_html` | 200 ＋ HTML（不是 JSON） | error |
| `struct200` | 200 ＋ `{"items":null}` | error |

一次只开一种，练完记得复位 `normal`。也可用环境变量覆盖：`FAULT_MODE`（启动即生效）、`DELAY_SECONDS`、`DB_PATH`。「网络失败」这一种用浏览器的 Offline 制造，不在上面的模式里。

---

## 第 3 课 · question-api

进入 `ch02/question-api/`，完成上面的[环境准备](#环境准备每个工程一次)。

### 启动

```bash
python -m uvicorn server:app --host 127.0.0.1 --port 8000
```

浏览器打开 <http://127.0.0.1:8000/> 是第 2 课的同源搜索页，本课用它回归读取接口没有退化。首次启动会自动建库、给旧库补 `tags`／`created_at` 两列并播种 `questions.db`（已被 `.gitignore` 忽略）。改完代码**先停止再重启**（不要用 `--reload`）。

### 文件说明

| 目录／文件 | 怎么用 |
|---|---|
| `server.py` | **你的工作文件**：列表／详情／存活探针／同源页面已给好；只在 `region task` 内按字段契约补齐 `QuestionCreate`，并把 `create_question` 接线到服务层 |
| `models.py` | 输出模型 `QuestionOut`／`QuestionListOut`，课堂要求解释，不用改 |
| `question_db.py` | 数据层（连接、建库升级、参数化查询与插入骨架），课堂当黑盒或按讲解阅读 |
| `service.py` | 创建服务模板 `create_question_service`（先验证再显式 commit，重复标题映射为 `DuplicateTitle`），本课要求会用，别把 commit 挪走 |
| `reference/server.py` | 完整答案（`QuestionCreate` 与创建接线都补齐），自己写完再对照 |
| `experiments/output_probe.py` | 课堂输出对照实验，用 `PROBE_MODE` 选 normal／missing／extra／direct 四模式 |
| `static/` | 同源页面骨架、样式与脚本，直接用 |
| `check_api.py` | 自检脚本，你会运行并读它的结果 |

### 接口

- `GET /questions?keyword=...&page=1&page_size=20` → `{"items":[...],"total":N,"page":N}`，记录在第 2 课基础上新增 `tags`（列表）与 `created_at`（带时区时间字符串）。
- `GET /questions/{qid}` → 命中 200、不存在 404、路径不是整数 422；`/healthz` → `{"status":"ok"}`。
- `POST /questions`（你要补的接口）→ 合法输入 201，返回记录并带指向详情的 `Location` 头；标题重复 409；字段越界或缺必填 422。

创建输入的字段契约：`title` 去首尾空白后长度 5–200、`body` 去首尾空白后长度 10–20000、`tags` 可省默认空列表且最多 5 个；`id`／`created_at` 由服务端生成，客户端填写会被拒绝。

### 自检

保持服务运行，**另开一个终端**，激活同一环境、在 `question-api` 目录下：

```bash
python check_api.py
# 若服务开在别的端口：
python check_api.py --base-url http://127.0.0.1:8001 --timeout 3
```

自检前会先调用教师复位端点把库还原成固定三条，可重复运行，共 23 项，全部通过退出码为 0，否则为 1。**`region task` 还没补齐时，创建类检查不通过是正常的。**

### 在 IDE 里调试

打开 `question-api` 文件夹，解释器选本工程的 `.venv`，`.vscode/launch.json` 已给好三条配置：起点包服务（`server:app`）、完整参考对照（`reference.server:app`）、输出对照实验（`experiments.output_probe:app`，默认 `PROBE_MODE=missing`）。在 `server.py` 的列表或创建函数第一行下断点，先发一次合法请求确认断点有效，再发 `page=0` 观察 422 时函数第一行不执行。启动调试前先停掉占用同端口的终端服务。

---

## 说明

- 所有数据与示例都是教学虚构，不连接任何生产数据。
- `.venv`、`__pycache__`、`*.db` 等运行产物已被 `.gitignore` 忽略，不用手动提交。
