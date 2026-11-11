# 第 7 课 · question-api

用 SQLAlchemy 2.0 ORM 读写第 6 课的五表数据，并接入 FastAPI。可独立安装、迁移、运行与测试，不引用其他课次的文件。

配套课件：`pages/ch03/07.md`（正文）与 `pages/ch03/07-reference.md`（完整映射、写入帮助函数、迁移主体、M2 契约）。

## 前置条件

- Python 3.12+ 与 [uv](https://docs.astral.sh/uv/)
- PostgreSQL 16+，数据库编码 UTF8
- 一个**可丢弃的教学数据库**（下面用 `lesson07`）。`reset_data.py` 会清空五张表，不要用 M1 应用库或任何有真实数据的库

先建库（用你自己的超级用户执行一次）：

```bash
createdb lesson07
```

## 快速开始

在本目录（`snippets/ch03/lesson-07/question-api/`）执行，**顺序不能颠倒**：

```bash
uv sync                                          # 1. 按 uv.lock 装依赖，生成 .venv
cp .env.example .env                             # 2. 生成连接配置（.env 不提交）
#                                                # 3. 编辑 .env，填写 DATABASE_URL
uv run --env-file .env alembic upgrade head      # 4. 建表 → 001_baseline
uv run --env-file .env pytest                    # 5. 自检，应 51 passed
uv run --env-file .env python -m examples.reset_data      # 6. 导入固定数据
uv run --env-file .env python -m examples.ex01_read_one   # 7. 跑第一个示例
uv run --env-file .env uvicorn app.main:app --reload      # 8. 起 HTTP 服务
```

**第 4、6 步是必须的。** 本工程的示例直接读写教学库的 `public` schema，表不会自动出现；跳过迁移就会报 `relation "questions" does not exist`。

`.env` 只有一个变量：

```dotenv
DATABASE_URL=postgresql+psycopg://user@localhost:5432/lesson07
```

需要密码时写在 URL 的用户信息里：`postgresql+psycopg://user:密码@localhost:5432/lesson07`。密码中的 `@ : / % #` 要转义（`@` 写作 `%40`）；也可改用 `PGPASSWORD` 或 `~/.pgpass` 提供，URL 中就不写密码。本机 socket 或 trust 认证的教学库可以没有密码。

> `uv run --env-file .env` 只把变量注入它启动的那个进程，不会写回你的 shell。手敲 `psql` 时要么自己 export，要么同样带上 `--env-file`。

## 目录结构

| 路径 | 用途 |
|---|---|
| `app/models.py` | 五表 ORM 映射（SQLAlchemy 2.0 声明式） |
| `app/schemas.py` | 沿用第 5 课的 Pydantic 输入／输出模型与业务异常 |
| `app/database.py` | Engine、Session 工厂与每个请求的 Session 依赖 |
| `app/services.py` | DTO、字面搜索、列表、详情、写入帮助函数与创建服务 |
| `app/routes.py` · `main.py` | 三个 JSON 路由 · 应用入口与业务错误响应 |
| `alembic.ini` · `migrations/` | Alembic 配置、`env.py` 与 `001_baseline` 固定基线 |
| `sql/seed.sql` | 固定数据，供 `reset_data.py` 使用 |
| `examples/` | ex01–ex07 按课件顺序编号，另有 `reset_data.py` |
| `tests/` | pytest，51 项 |

`models.py` 是 ORM 模型，`schemas.py` 是 Pydantic 模型，两者同名易混，注意区分。

Python 文件里的 `# region 名` 标记就是课件 `<<<` 引用的区段，改动区段内容会让课件高亮错位。

## 示例清单

| 命令（省略 `uv run --env-file .env` 前缀） | 看什么 | 是否改数据 |
|---|---|---|
| `python -m examples.reset_data` | 清空五表并重新导入固定数据 | **清空重灌** |
| `python -m examples.ex01_read_one` | 按主键读取：有行得实例，无行得 None | 只读 |
| `python -m examples.ex02_create_one` | 构造、add、flush、commit 各阶段 id 的变化 | **真实提交** |
| `python -m examples.ex03_update_one [qid]` | 新 Session 中修改已提交的问题，flush 时 UPDATE | **真实提交** |
| `python -m examples.ex04_rollback` | INSERT 已发送、提交前出错，rollback 后库里没有这条 | 回滚 |
| `python -m examples.ex05_autoflush` | 查询前先 flush，查得到但仍未提交 | 关闭不提交 |
| `python -m examples.ex06_queries` | 第 6 课 Q1–Q4 的 ORM 写法 | 只读 |
| `python -m examples.ex07_loading` | 默认 lazy 与 selectinload 的 SELECT 条数对比 | 只读 |

**跑过 ex02／ex03 之后，重跑或换顺序前先执行一次 `reset_data`**，否则后面的示例会看到被改过的数据。ex06／ex07 依赖固定的两问题、三回答。

## 隔离机制：示例与测试不一样

- **示例**直接读写教学库的 `public`，改动会持久留下（这正是第 7 课要观察的提交与可见性）。
- **测试**每个用例新建 `lesson07_test_<uuid>` schema，在其中迁移并导入固定数据，结束时删除，互不干扰，也不碰 `public`。

所以 `pytest` 可以随时重复跑，不会污染示例数据；而示例跑完库里的数据是真的变了。

> 这一点与第 6 课 `sql-labs` 相反：那边每次示例运行都自建临时 schema 并在退出时删除，跑完 `public` 是空的，要用 `--keep` 才留得下来。

## HTTP 接口

起服务后默认在 <http://127.0.0.1:8000>：

| 方法与路径 | 说明 |
|---|---|
| `GET /questions` | 列表，参数 `keyword`／`page`（≥1，默认 1）／`page_size`（1–50，默认 20）；返回 `items`／`total`／`page`，按 id DESC，`total` 是筛选后分页前总数 |
| `GET /questions/{qid}` | 详情，输出 id／title／body／tags／created_at 五字段 |
| `POST /questions` | 创建，成功 201 + `Location` 头 |

输入规则（`QuestionCreate`）：`title` 5–200 字符、`body` 10–20000 字符、`tags` 最多五项，两者先 strip，且**拒绝额外字段**（`extra="forbid"`）。

错误响应分两种：

- 业务异常由 `main.py` 的处理器翻译成 `{"code", "message"}` 两字段：404 `question_not_found`、409 `duplicate_title`
- 输入校验失败是 FastAPI 默认的 422，响应体为 `{"detail": [...]}`，不走业务处理器

搜索沿用字面子串约定，`%` 与 `_` 不会偷偷变成 LIKE 通配符。本工程没有 request-id 中间件与探针端点（那些属于第 4／5 课的 M1 应用）。

```bash
curl -s http://127.0.0.1:8000/questions/101
curl -s -o /dev/null -w "%{http_code}\n" http://127.0.0.1:8000/questions/999   # 404
```

## 常见问题

**`relation "questions" does not exist`**
没跑 `alembic upgrade head`，或 `DATABASE_URL` 指向了另一个空库。先确认：

```bash
uv run --env-file .env alembic current          # 应显示 001_baseline (head)
```

**`请先设置环境变量 DATABASE_URL`**
忘了带 `--env-file .env`，或 `.env` 不在当前目录。

**示例结果和课件对不上**
多半是 ex02／ex03 改过数据。跑 `python -m examples.reset_data` 复位。

**POST 返回 422**
不一定是 bug：`body` 最少 10 字符、`title` 最少 5 字符，且不允许多传字段。看 `detail` 里的 `loc` 与 `msg` 定位是哪一项，换一段足够长的正文再试。

**`reset_data` 会不会删掉我的数据**
会。它 `TRUNCATE` 五张表并 `RESTART IDENTITY`，只对可丢弃的教学库运行。

## 边界

- 迁移基线 `001_baseline` 的列定义写在迁移文件里，不 import 会继续变化的 `app.models`；第 6 课 DDL、此 metadata 与迁移产物三方结构一致
- 没有 delete／delete-orphan cascade，删除仍被引用的问题由**数据库外键拒绝**，ORM 不先删或置空子记录
- 服务层显式提交，连接依赖只提供与关闭
- M1 当前仍是 SQLite，本工程不替换它，也不做真实数据迁移；重复标签在五表结构下的契约差异仍待确认，见课件参考页
- 依赖精确版本以 `uv.lock` 为准；本课在 PostgreSQL 18.6 实测 51 项测试通过，ex01–ex07 与三个接口均已运行
