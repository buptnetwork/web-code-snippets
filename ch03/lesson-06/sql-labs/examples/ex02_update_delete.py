"""两表阶段：UPDATE 与 DELETE 各自在事务里演示，然后回滚复位。

运行：uv run --env-file .env python -m examples.ex02_update_delete
"""

import sys

from examples.ex01_two_tables import create_two_tables
from labs.connection import connect, isolated_schema
from labs.sqlfile import region, run

QUESTION_102 = "SELECT id, body FROM questions WHERE id = 102"
ANSWERS_OF_101 = "SELECT id FROM answers WHERE question_id = 101 ORDER BY id"


def update_then_rollback(conn):
    """执行 update 区段：SQL 自带 BEGIN…ROLLBACK，返回事务内那条 SELECT 的行。"""
    return run(conn, region("05-transactions.sql", "update"))[0]


def delete_then_rollback(conn):
    """执行 delete 区段：删掉回答 203 后读一次，再回滚。"""
    return run(conn, region("05-transactions.sql", "delete"))[0]


def main():
    with connect() as conn, isolated_schema(conn, keep="--keep" in sys.argv):
        create_two_tables(conn)
        print("修改后（事务内）：", update_then_rollback(conn))
        print("回滚后读回：", conn.execute(QUESTION_102).fetchall())
        print("删除后（事务内）：", delete_then_rollback(conn))
        print("回滚后读回：", conn.execute(ANSWERS_OF_101).fetchall())


if __name__ == "__main__":
    main()
