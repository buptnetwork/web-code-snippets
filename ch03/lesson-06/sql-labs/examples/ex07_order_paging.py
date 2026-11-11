"""排序与分页：Q4 的三页、总数与过滤后总数、按时间排序。

运行：uv run --env-file .env python -m examples.ex07_order_paging
"""

import sys

from examples.ex03_five_tables import create_five_tables
from labs.connection import connect, isolated_schema
from labs.sqlfile import region, run


def page(conn, offset):
    """Q4 的一页：课件写死 OFFSET 0，这里只把偏移量换成占位符，由 Python 传值。"""
    statement = region("04-queries.sql", "q4").replace("OFFSET 0", "OFFSET %s")
    return conn.execute(statement, (offset,)).fetchall()


def totals(conn):
    """总数与过滤后总数：页数要按过滤后的条数算，不是按整表条数。"""
    return (
        run(conn, region("04-queries.sql", "total"))[0],
        run(conn, region("04-queries.sql", "filtered-total"))[0],
    )


def by_time(conn):
    """按创建时间倒序；两条问题时间相同，再用 id 倒序决定先后。"""
    return run(conn, region("04-queries.sql", "time-order"))[0]


def main():
    with connect() as conn, isolated_schema(conn, keep="--keep" in sys.argv):
        create_five_tables(conn)
        for offset in (0, 1, 2):
            print(f"OFFSET {offset}：", page(conn, offset))
        total, filtered = totals(conn)
        print("总数：", total, "作者 1 的总数：", filtered)
        print("按时间倒序：", by_time(conn))


if __name__ == "__main__":
    main()
