"""关联与聚合：Q2 配对、标签顺序、LEFT JOIN 的四行、计数对比与 Q3。

运行：uv run --env-file .env python -m examples.ex06_joins
"""

import sys

from examples.ex03_five_tables import create_five_tables
from labs.connection import connect, isolated_schema
from labs.sqlfile import region, run

# 按课件顺序：JOIN 配对 → 读回标签 → LEFT JOIN 四行 → 三种计数 → GROUP BY 归组。
TAGS = ("q2", "tag-read", "left-rows", "count-compare", "q3")


def join_results(conn):
    """依次执行五个区段，返回 {区段名: 行}。"""
    return {tag: run(conn, region("04-queries.sql", tag))[0] for tag in TAGS}


def main():
    with connect() as conn, isolated_schema(conn, keep="--keep" in sys.argv):
        create_five_tables(conn)
        for tag, rows in join_results(conn).items():
            print(f"{tag}：")
            for row in rows:
                print("   ", row)


if __name__ == "__main__":
    main()
