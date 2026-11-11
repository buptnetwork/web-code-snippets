"""Q1 与参数绑定：同一筛选条件，一次写死在 SQL 里，一次由 Python 传值。

运行：uv run --env-file .env python -m examples.ex05_q1_binding
"""

import sys

from examples.ex03_five_tables import create_five_tables
from labs.binding import find_questions_by_author
from labs.connection import connect, isolated_schema
from labs.sqlfile import region, run


def q1(conn):
    """课件 Q1：SQL 文本里写死 author_id = 1。"""
    return run(conn, region("04-queries.sql", "q1"))[0]


def main():
    with connect() as conn, isolated_schema(conn, keep="--keep" in sys.argv):
        create_five_tables(conn)
        print("Q1（写死作者 1）：", q1(conn))
        for author_id in (1, 2, 9):
            print(f"绑定 author_id={author_id}：", find_questions_by_author(conn, author_id))


if __name__ == "__main__":
    main()
