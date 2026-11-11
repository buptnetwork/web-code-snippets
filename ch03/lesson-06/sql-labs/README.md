# 第 6 课 · sql-labs

在 PostgreSQL 上学表、约束、查询与事务。SQL 与 Python 示例都可直接运行，不引用其他课次的文件。

配套课件：`pages/ch03/06.md`（正文）与 `pages/ch03/06-reference.md`（完整五表、种子、序列校准）。

## 前置条件

- Python 3.12+ 与 [uv](https://docs.astral.sh/uv/)
- PostgreSQL 16+，数据库编码 UTF8
- 一个**可丢弃的教学数据库**（下面用 `lesson06`）。不要用 M1 应用库或任何有真实数据的库

先建库（用你自己的超级用户执行一次）：

```bash
createdb lesson06
```

## 快速开始

在本目录（`snippets/ch03/lesson-06/sql-labs/`）执行：

```bash
uv sync                              # 1. 按 uv.lock 装依赖，生成 .venv
cp .env.example .env                 # 2. 生成自己的连接配置（.env 不提交）
#                                    # 3. 编辑 .env，填写 PG* 变量
uv run --env-file .env pytest        # 4. 自检，应 38 passed
uv run --env-file .env python -m examples.ex01_two_tables   # 5. 跑第一个示例
```

`.env` 用 libpq 标准变量，**psql 与 Python 共用同一份**：

```dotenv
PGHOST=localhost
PGPORT=5432
PGDATABASE=lesson06
PGUSER=user
# 需要密码时再填 PGPASSWORD，或改用 ~/.pgpass（权限 0600）
# PGPASSWORD=
```

走本机 unix socket 时，把 socket 目录写进 `PGHOST`（例如 `PGHOST=/tmp`），此时通常不需要密码。

> `uv run --env-file .env` 只把变量注入它启动的那个进程，**不会写回你的 shell**。所以后面凡是手敲 `psql`，都要带上 `--env-file`，否则会连到默认库。

## 目录结构

| 路径 | 用途 |
|---|---|
| `sql/01-two-tables.sql` | 两表阶段初始化：建表、固定数据、读回、序列校准，可整文件执行 |
| `sql/02-five-tables.sql` | 五表结构（users、questions、answers、tags、question_tags） |
| `sql/03-seed.sql` | 五表固定数据与序列校准，在 02 之后执行 |
| `sql/04-queries.sql` | Q1–Q4 与辅助查询，只读 |
| `sql/05-transactions.sql` | update／delete 回滚演示，以及预期失败的 duplicate |
| `labs/connection.py` | `connect()` 与 `isolated_schema()` |
| `labs/sqlfile.py` | `read()` 读文件、`region()` 取区段、`run()` 执行多语句 |
| `labs/binding.py` | 参数绑定示例 `find_questions_by_author()` |
| `examples/` | ex01–ex07，按课件顺序编号 |
| `tests/` | pytest，38 项 |

SQL 文件里的 `-- #region 名` 标记就是课件 `<<<` 引用的区段，改动区段内容会让课件高亮错位。

## 示例清单

| 命令（省略 `uv run --env-file .env` 前缀） | 看什么 |
|---|---|
| `python -m examples.ex01_two_tables` | 两表阶段：建表、插入、读回两个结果集 |
| `python -m examples.ex02_update_delete` | UPDATE／DELETE 在事务内生效，ROLLBACK 后复位 |
| `python -m examples.ex03_five_tables` | 五表行数与「作者未知的回答 202」 |
| `python -m examples.ex04_constraints` | 四处预期拒绝：约束名与 SQLSTATE |
| `python -m examples.ex05_q1_binding` | Q1 写死作者 vs 由 Python 传值（1／2／9） |
| `python -m examples.ex06_joins` | Q2 配对、标签顺序、LEFT JOIN 四行、计数对比、Q3 |
| `python -m examples.ex07_order_paging` | Q4 三页、总数与过滤后总数、按时间排序 |

每个文件都是「函数接收 conn 并返回结果 + `__main__` 负责打印」，所以既能单独跑，也能被测试导入断言。

## 为什么跑完在数据库里看不到表

**这是设计行为。** `isolated_schema()` 每次运行会：

1. `CREATE SCHEMA lesson06_<随机12位>`
2. `SET search_path` 指向它，再建表、插数据、查询
3. 退出时 `DROP SCHEMA ... CASCADE`

所以进程一结束，表和 schema 一起消失，`public` 始终是空的。这样每次运行都自带干净环境，两表阶段与五表阶段不会叠加，也不需要手工切 schema 或复位数据。

想留下来看，加 `--keep`：

```bash
uv run --env-file .env python -m examples.ex03_five_tables --keep
```

脚本会打印 schema 名和**可直接照抄**的查看／删除命令：

```bash
uv run --env-file .env psql -c "SET search_path TO lesson06_xxx; SELECT id, title FROM questions ORDER BY id;"
uv run --env-file .env psql -c 'DROP SCHEMA lesson06_xxx CASCADE'
```

注意 `\dt` 默认只看 `search_path`，要列出临时 schema 的表得写 `\dt lesson06_xxx.*`。看完记得删，否则会在库里堆积。

## 手工用 psql 执行

课件参考页保留了这条路径。两表与五表**必须分处不同的空 schema**，不能叠加。用 `PGOPTIONS` 把 `search_path` 指过去：

```bash
# 两表阶段：建一个空 schema 并初始化
uv run --env-file .env psql -c "CREATE SCHEMA two_tables"
PGOPTIONS="-c search_path=two_tables" \
  uv run --env-file .env psql -v ON_ERROR_STOP=1 -1 -f sql/01-two-tables.sql

# 五表阶段：换另一个空 schema
uv run --env-file .env psql -c "CREATE SCHEMA five_tables"
PGOPTIONS="-c search_path=five_tables" \
  uv run --env-file .env psql -v ON_ERROR_STOP=1 -1 -f sql/02-five-tables.sql -f sql/03-seed.sql

# 查看与清理
uv run --env-file .env psql -c "SET search_path TO five_tables; SELECT id, title FROM questions ORDER BY id;"
uv run --env-file .env psql -c "DROP SCHEMA two_tables CASCADE; DROP SCHEMA five_tables CASCADE;"
```

`-1` 把初始化作为一个事务，`ON_ERROR_STOP` 遇错停止。这样建的表会**一直留在库里**，不像示例那样自动删除，看完请自己 DROP。

`sql/05-transactions.sql` 不要整文件盲跑：`update`／`delete` 区段自带 `BEGIN…ROLLBACK`，可整段执行；`duplicate` 是预期失败，必须单独 `BEGIN`、捕获错误后 `ROLLBACK`。

## 常见问题

**`连不上教学数据库：请把 .env.example 复制为 .env …`**
`.env` 没建、`PG*` 填错，或 PostgreSQL 没启动。先用 `uv run --env-file .env psql -Atc "SELECT current_database()"` 验证连接本身。

**跑完示例，库里一张表都没有**
见上一节，用 `--keep`。

**`relation "questions" does not exist`**
在 psql 里没设 `search_path`，或那个临时 schema 已被删除。

**序列下一个值是 103 而不是 3**
固定数据显式插入了 id 101／102，显式插入不推进序列；`setval` 校准后 `nextval` 就是 103。五表阶段校准结果是 users→3、questions→103、answers→204、tags→3。

**ex04 报错是不是坏了**
不是。那四处拒绝（`question_tags_pkey`、`answers_question_id_fkey` ×2、`questions_author_id_fkey`）就是教学目标，脚本捕获后打印约束名与 SQLSTATE，回滚再继续。

## 边界

- 连接是 `autocommit=True`，SQL 里写的 `BEGIN`／`ROLLBACK` 就是实际执行的语句
- 固定数据：2 用户／2 问题／3 回答／2 标签／3 关联，回答 202 的作者为 NULL
- 不替换 M1 的 SQLite 应用，不包含真实数据迁移
- 依赖精确版本以 `uv.lock` 为准；本课在 PostgreSQL 18.6 实测 38 项测试通过、ex01–ex07 与 `--keep` 均已运行
