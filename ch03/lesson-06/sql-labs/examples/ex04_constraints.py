"""约束：一处预期重复关联，三处外键拒绝；每次失败后回滚再继续。

运行：uv run --env-file .env python -m examples.ex04_constraints
"""

import sys

import psycopg

from examples.ex03_five_tables import create_five_tables
from labs.connection import connect, isolated_schema
from labs.sqlfile import region

# 课件“删除时的引用边界”页的三条写入：默认 NO ACTION，数据库拒绝破坏引用的操作。
FOREIGN_KEY_CASES = (
    ("回答改到不存在的问题", "UPDATE answers SET question_id = 999 WHERE id = 201"),
    ("删除仍被回答引用的问题", "DELETE FROM questions WHERE id = 101"),
    ("删除仍被问题引用的用户", "DELETE FROM users WHERE id = 1"),
)
LINKS = "SELECT question_id, tag_id, position FROM question_tags ORDER BY question_id, position"


def rejected(conn, statement):
    """执行一条预期失败的写入，返回 (SQLSTATE, 约束名)。

    显式事务出错后必须先 ROLLBACK，连接才能继续用于正常查询。
    """
    conn.execute("BEGIN")
    try:
        conn.execute(statement)
    except psycopg.errors.IntegrityError as exc:
        return exc.sqlstate, exc.diag.constraint_name
    finally:
        conn.execute("ROLLBACK")
    raise AssertionError("预期被约束拒绝，但写入成功了")


def constraint_failures(conn):
    """四处预期拒绝：重复关联在前，三条外键边界在后。"""
    cases = (("重复关联同一标签", region("05-transactions.sql", "duplicate")), *FOREIGN_KEY_CASES)
    return [(label, *rejected(conn, statement)) for label, statement in cases]


def main():
    with connect() as conn, isolated_schema(conn, keep="--keep" in sys.argv):
        create_five_tables(conn)
        for label, sqlstate, constraint in constraint_failures(conn):
            print(f"{label}：SQLSTATE {sqlstate}，约束 {constraint}")
        print("回滚后关联仍是：", conn.execute(LINKS).fetchall())


if __name__ == "__main__":
    main()
