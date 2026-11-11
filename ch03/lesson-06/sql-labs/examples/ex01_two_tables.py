"""两表阶段：建表、插入固定数据，再读回来。

运行：uv run --env-file .env python -m examples.ex01_two_tables
"""

import sys

from labs.connection import connect, isolated_schema
from labs.sqlfile import read, region, run


def create_two_tables(conn):
    """在空 schema 中执行两表初始化：建表、插入固定数据、校准序列。"""
    conn.execute(read("01-two-tables.sql"))


def read_back(conn):
    """执行 read 区段的两个 SELECT，返回 [问题行, 回答行]。"""
    return run(conn, region("01-two-tables.sql", "read"))


def main():
    with connect() as conn, isolated_schema(conn, keep="--keep" in sys.argv) as schema:
        create_two_tables(conn)
        questions, answers = read_back(conn)
        print(f"本次 schema：{schema}")
        print("问题：", questions)
        print("回答：", answers)


if __name__ == "__main__":
    main()
