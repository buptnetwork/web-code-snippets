"""读取 sql/ 下的文件与区段，并把区段当作一段 SQL 执行。

课件用 `<<< 文件#区段` 引用同一份 SQL，所以这里按 `-- #region 名字` 标记取片段，
保证课堂上看到的和学生运行的是同一段文本。
"""

from pathlib import Path

SQL_DIR = Path(__file__).resolve().parent.parent / "sql"


def read(name):
    """读取整个 SQL 文件，例如 read("01-two-tables.sql")。"""
    return (SQL_DIR / name).read_text(encoding="utf-8")


def region(name, tag):
    """取出 `-- #region tag` 与 `-- #endregion tag` 之间的 SQL。"""
    text = read(name)
    start, end = f"-- #region {tag}\n", f"-- #endregion {tag}"
    if text.count(start) != 1 or text.count(end) != 1:
        raise ValueError(f"{name} 中没有唯一的区段：{tag}")
    return text.split(start, 1)[1].split(end, 1)[0].strip()


def run(conn, statement):
    """执行一段可能含多条语句的 SQL，按顺序返回每条 SELECT 的行。

    多语句执行时，psycopg 把多个结果集放在同一个游标上，用 nextset() 逐个取出；
    BEGIN、UPDATE、ROLLBACK 这类没有结果集的语句会被跳过。
    需要传值时不要用本函数，改用 conn.execute(sql, params)，见 labs/binding.py。
    """
    cursor = conn.execute(statement)
    results = []
    while True:
        if cursor.description is not None:
            results.append(cursor.fetchall())
        if not cursor.nextset():
            return results
