"""测试用的小工具：取行中的列、执行查询区段、读序列的下一个 id。"""

from labs.sqlfile import region, run


def values(rows, *keys):
    """把字典行压成元组，便于和课件里的结果表逐行比对。"""
    return [tuple(row[key] for key in keys) for row in rows]


def query(conn, tag):
    """执行 04-queries.sql 中的一个区段，返回它的行。"""
    return run(conn, region("04-queries.sql", tag))[0]


def next_id(conn, table):
    """序列校准后，下一条新增会拿到的 id。"""
    row = conn.execute("SELECT nextval(pg_get_serial_sequence(%s, 'id')) AS n", (table,)).fetchone()
    return row["n"]
