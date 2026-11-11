"""五表阶段：在另一个干净 schema 中建五表、导入固定数据，观察未知作者。

运行：uv run --env-file .env python -m examples.ex03_five_tables
"""

import sys

from psycopg import sql

from labs.connection import connect, isolated_schema
from labs.sqlfile import read, region, run

TABLES = ("users", "questions", "answers", "tags", "question_tags")


def create_five_tables(conn):
    """先建结构再导入数据：两个文件分开，正对应“建结构”和“导入数据”是两件事。"""
    conn.execute(read("02-five-tables.sql"))
    conn.execute(read("03-seed.sql"))


def row_counts(conn):
    """五张表各有多少行。表名是标识符，用 sql.Identifier 拼接，值才用 %s 绑定。"""
    counts = {}
    for table in TABLES:
        statement = sql.SQL("SELECT count(*) AS n FROM {}").format(sql.Identifier(table))
        counts[table] = conn.execute(statement).fetchone()["n"]
    return counts


def unknown_author(conn):
    """author_id IS NULL 的回答：存在这条回答，但这里没有已知的具体作者。"""
    return run(conn, region("04-queries.sql", "unknown-author"))[0]


def main():
    with connect() as conn, isolated_schema(conn, keep="--keep" in sys.argv) as schema:
        create_five_tables(conn)
        print(f"本次 schema：{schema}")
        print("行数：", row_counts(conn))
        print("作者未知的回答：", unknown_author(conn))


if __name__ == "__main__":
    main()
