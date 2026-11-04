"""教师自检：验证最终 SQL 源文件，不解析底稿、不触碰 M1 表。

Python 3.12+，psycopg[binary]==3.3.6，PostgreSQL 16+。
先配置指向隔离教学数据库的 PGHOST / PGPORT / PGDATABASE / PGUSER 等标准变量。
运行：uv run --no-project --with 'psycopg[binary]==3.3.6' python verify_examples.py

每阶段在外层事务中新建随机 schema，退出时整体回滚，不保留教学对象。
修改示例使用同一 DML/SELECT，在嵌套保存点中回滚，以保留外层初始化。
这验证了结果与复位，不是 M1 迁移或 HTTP 联调验证器。
"""

from pathlib import Path
from uuid import uuid4

import psycopg
from psycopg import sql
from psycopg.rows import dict_row

from binding import find_questions_by_author

ROOT = Path(__file__).resolve().parent


def source(filename):
    return (ROOT / filename).read_text(encoding="utf-8")


def region(filename, name):
    text = source(filename)
    start = f"-- #region {name}\n"
    end = f"-- #endregion {name}"
    if text.count(start) != 1 or text.count(end) != 1:
        raise ValueError(f"无唯一代码区段：{filename}#{name}")
    return text.split(start, 1)[1].split(end, 1)[0].strip()


def query(conn, name):
    return conn.execute(region("queries.sql", name)).fetchall()


def values(rows, *keys):
    return [tuple(row[key] for key in keys) for row in rows]


def check_transactions(conn):
    original = conn.execute("SELECT id, body FROM questions ORDER BY id").fetchall()
    for name in ("update", "delete"):
        statements = [part.strip() for part in region("transactions.sql", name).split(";") if part.strip()]
        assert statements[0] == "BEGIN" and statements[-1] == "ROLLBACK"
        with conn.transaction(force_rollback=True):
            conn.execute(statements[1])
            result = conn.execute(statements[2]).fetchall()
            if name == "update":
                assert result == [{"id": 102, "body": "更新后的说明仍然围绕表和记录展开。"}]
            else:
                assert values(result, "id") == [(201,), (202,)]
        assert conn.execute("SELECT id, body FROM questions ORDER BY id").fetchall() == original
        assert values(conn.execute("SELECT id FROM answers ORDER BY id").fetchall(), "id") == [(201,), (202,), (203,)]


def reject(conn, statement, error_type, constraint):
    try:
        with conn.transaction():
            conn.execute(statement)
    except error_type as exc:
        assert exc.diag.constraint_name == constraint
    else:
        raise AssertionError(f"预期由 {constraint} 拒绝，但写入成功")


def check_full(conn, schema):
    q1 = query(conn, "q1")
    assert q1 == [{"id": 101, "title": "Python 如何读取问题列表？"}]
    for author, expected in ((1, [(101,)]), (2, [(102,)]), (9, [])):
        assert values(find_questions_by_author(conn, author), "id") == expected
    pairs = query(conn, "q2")
    assert values(pairs, "question_id", "answer_id") == [(101, 201), (101, 202), (101, 203)]
    assert all(row["title"] == q1[0]["title"] for row in pairs)
    assert values(query(conn, "unknown-author"), "id", "question_id") == [(202, 101)]
    assert values(query(conn, "tag-read"), "name") == [("python",), ("sql",)]
    assert values(query(conn, "left-rows"), "question_id", "answer_id", "author_id") == [
        (101, 201, 2), (101, 202, None), (101, 203, 2), (102, None, None),
    ]
    assert values(query(conn, "q3"), "id", "answer_count") == [(101, 3), (102, 0)]
    assert values(query(conn, "count-compare"), "id", "joined_rows", "answers", "known_authors") == [
        (101, 3, 3, 2), (102, 1, 0, 0),
    ]
    for offset, expected in ((0, [(102,)]), (1, [(101,)]), (2, [])):
        statement = region("queries.sql", "q4").replace("OFFSET 0", f"OFFSET {offset}")
        assert values(conn.execute(statement).fetchall(), "id") == expected
        assert query(conn, "total") == [{"total": 2}]
    assert query(conn, "filtered-total") == [{"total": 1}]
    assert values(query(conn, "time-order"), "id") == [(102,), (101,)]

    reject(conn, region("transactions.sql", "duplicate"), psycopg.errors.UniqueViolation, "question_tags_pkey")
    reject(conn, "UPDATE answers SET question_id = 999 WHERE id = 201", psycopg.errors.ForeignKeyViolation, "answers_question_id_fkey")
    reject(conn, "DELETE FROM questions WHERE id = 101", psycopg.errors.ForeignKeyViolation, "answers_question_id_fkey")
    reject(conn, "DELETE FROM users WHERE id = 1", psycopg.errors.ForeignKeyViolation, "questions_author_id_fkey")
    assert values(conn.execute("SELECT question_id, tag_id, position FROM question_tags ORDER BY question_id, position").fetchall(), "question_id", "tag_id", "position") == [(101, 1, 1), (101, 2, 2), (102, 1, 1)]
    check_transactions(conn)

    fkeys = conn.execute(
        "SELECT confdeltype, condeferrable FROM pg_constraint WHERE connamespace = %s::regnamespace AND contype = 'f'",
        (schema,),
    ).fetchall()
    assert len(fkeys) == 5
    assert all(row == {"confdeltype": "a", "condeferrable": False} for row in fkeys)
    for table, count in (("users", 2), ("questions", 2), ("answers", 3), ("tags", 2), ("question_tags", 3)):
        actual = conn.execute(sql.SQL("SELECT count(*) AS n FROM {}").format(sql.Identifier(table))).fetchone()
        assert actual["n"] == count
    for table, expected in (("users", 3), ("questions", 103), ("answers", 204), ("tags", 3)):
        actual = conn.execute("SELECT nextval(pg_get_serial_sequence(%s, 'id')) AS n", (table,)).fetchone()
        assert actual["n"] == expected
    print("五表：种子、Q1–Q4、绑定、标签、NULL、关联计数、分页、约束与回滚通过")


def main():
    # 使用 libpq 标准连接环境变量；连接参数和认证信息不打印、不写入源码。
    with psycopg.connect("", autocommit=True, row_factory=dict_row, connect_timeout=5) as conn:
        assert conn.info.server_version >= 160000, "需要 PostgreSQL 16+"
        print(conn.execute("SELECT version() AS version").fetchone()["version"])
        assert conn.execute("SHOW server_encoding").fetchone()["server_encoding"] == "UTF8"
        for stage in ("two", "full"):
            schema = f"lesson06_verify_{stage}_{uuid4().hex}"
            with conn.transaction(force_rollback=True):
                conn.execute(sql.SQL("CREATE SCHEMA {}").format(sql.Identifier(schema)))
                conn.execute(sql.SQL("SET LOCAL search_path TO {}, pg_catalog").format(sql.Identifier(schema)))
                conn.execute("SET LOCAL TIME ZONE 'UTC'")
                conn.execute("SET LOCAL statement_timeout = '10s'")
                if stage == "two":
                    conn.execute(source("two-tables.sql"))
                    assert values(conn.execute("SELECT id FROM questions ORDER BY id").fetchall(), "id") == [(101,), (102,)]
                    assert values(conn.execute("SELECT id, question_id FROM answers ORDER BY id").fetchall(), "id", "question_id") == [(201, 101), (202, 101), (203, 101)]
                    check_transactions(conn)
                    print("两表：建表、种子、读取、修改／删除与回滚通过")
                else:
                    conn.execute(source("schema.sql"))
                    conn.execute(source("seed.sql"))
                    check_full(conn, schema)
            assert conn.execute("SELECT to_regnamespace(%s) AS schema", (schema,)).fetchone()["schema"] is None
        print("完成：两个随机 schema 均已整体回滚，未保留教学对象")


if __name__ == "__main__":
    main()
