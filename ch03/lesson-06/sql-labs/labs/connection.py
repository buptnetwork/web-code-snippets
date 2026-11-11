"""连接教学数据库，并为本次运行准备一个干净的 schema。

连接参数取自 libpq 标准环境变量（PGHOST、PGPORT、PGDATABASE、PGUSER、PGPASSWORD），
psql 与 Python 示例共用同一份 .env；凭据不写入源码，也不打印。
"""

from contextlib import contextmanager
from uuid import uuid4

import psycopg
from psycopg import sql
from psycopg.rows import dict_row


def connect():
    """打开一个 autocommit 连接：SQL 里写的 BEGIN／ROLLBACK 就是实际执行的语句。

    dict_row 让每行按列名返回字典，例如 {"id": 101, "title": "..."}。
    """
    try:
        return psycopg.connect("", autocommit=True, row_factory=dict_row, connect_timeout=5)
    except psycopg.OperationalError as exc:
        raise RuntimeError(
            "连不上教学数据库：请把 .env.example 复制为 .env 并填写 PG* 变量，"
            "再用 uv run --env-file .env ... 运行"
        ) from exc


@contextmanager
def isolated_schema(conn, *, keep=False):
    """新建只属于本次运行的 schema，退出时删除；keep=True 时保留供 psql 查看。

    两表阶段与五表阶段因此不会叠加，也不需要手工切换 schema。
    """
    schema = f"lesson06_{uuid4().hex[:12]}"
    conn.execute(sql.SQL("CREATE SCHEMA {}").format(sql.Identifier(schema)))
    conn.execute(sql.SQL("SET search_path TO {}, pg_catalog").format(sql.Identifier(schema)))
    conn.execute("SET TIME ZONE 'UTC'")
    try:
        yield schema
    finally:
        if keep:
            # 下面几行只是给人看的提示命令，schema 名由本脚本生成，不含用户输入。
            # 必须带 --env-file：PG* 变量只在 .env 里，直接敲 psql 会连到默认库。
            print(f"已保留 schema：{schema}")
            print("在 sql-labs 目录执行：")
            print(f'  uv run --env-file .env psql -c "SET search_path TO {schema}; '
                  f'SELECT id, title FROM questions ORDER BY id;"')
            print(f"  uv run --env-file .env psql -c 'DROP SCHEMA {schema} CASCADE'")
        else:
            conn.execute(sql.SQL("DROP SCHEMA {} CASCADE").format(sql.Identifier(schema)))
