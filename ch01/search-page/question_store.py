"""第 2 课数据模块：SQLite 存储、搜索分页与详情查询。

理解边界：本模块对学生为「要求会用」——按接口发请求即可，
不要求实现或解释 SQL、连接管理与分页内部。全部数据均为教学虚构。
"""

# region config
import os
import sqlite3
from pathlib import Path

# 默认落在包目录下，可用 DB_PATH 环境变量覆盖（教师验证时用临时库）。
DB_PATH = Path(os.environ.get("DB_PATH", Path(__file__).resolve().parent / "questions.db"))

# 与第 1 课相同的三条虚构问题；只有 id 3 的标题包含 React。
SEEDS = [
    (3, "React 的 props 是什么？", "想知道组件怎样接收数据。"),
    (2, "FastAPI 如何接收路径参数？", "希望从地址取出问题编号。"),
    (1, "浏览器怎样显示列表？", "先确认接口能返回正确的数据。"),
]
# endregion config


# region connect
def _connect() -> sqlite3.Connection:
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    return connection
# endregion connect


# region init
def init_db() -> None:
    """建表并播种；幂等，重复调用不会重复插入或清空既有数据。"""
    with _connect() as connection:
        connection.execute(
            "CREATE TABLE IF NOT EXISTS questions ("
            "id INTEGER PRIMARY KEY, title TEXT NOT NULL, body TEXT NOT NULL)"
        )
        count = connection.execute("SELECT COUNT(*) AS n FROM questions").fetchone()["n"]
        if count == 0:
            connection.executemany(
                "INSERT INTO questions (id, title, body) VALUES (?, ?, ?)", SEEDS
            )
# endregion init


# region like
def _like_pattern(keyword: str) -> str:
    """把关键词转成字面子串匹配模式；% 与 _ 不作通配符，反斜杠为转义符。

    SQLite 的 LIKE 对 ASCII 默认不区分大小写，正对应「英文字母不区分大小写」；
    中文按字节精确匹配子串。
    """
    escaped = (
        keyword.replace("\\", "\\\\")
        .replace("%", "\\%")
        .replace("_", "\\_")
    )
    return f"%{escaped}%"
# endregion like


# region search
def search(keyword: str, page: int, page_size: int) -> tuple[list[dict], int]:
    """返回 (本页记录, 匹配总数)。记录按 id 降序后分页；total 为分页前匹配总数。"""
    keyword = keyword.strip()
    limit = page_size
    offset = (page - 1) * page_size
    with _connect() as connection:
        if keyword:
            pattern = _like_pattern(keyword)
            where = "WHERE title LIKE :p ESCAPE '\\' OR body LIKE :p ESCAPE '\\'"
            params = {"p": pattern, "limit": limit, "offset": offset}
        else:
            where = ""
            params = {"limit": limit, "offset": offset}
        total = connection.execute(
            f"SELECT COUNT(*) AS n FROM questions {where}",
            {k: v for k, v in params.items() if k == "p"},
        ).fetchone()["n"]
        rows = connection.execute(
            f"SELECT id, title, body FROM questions {where} "
            "ORDER BY id DESC LIMIT :limit OFFSET :offset",
            params,
        ).fetchall()
    items = [{"id": r["id"], "title": r["title"], "body": r["body"]} for r in rows]
    return items, total
# endregion search


# region detail
def get_by_id(qid: int) -> dict | None:
    """按编号取单条记录；不存在返回 None。保持第 1 课记录结构。"""
    with _connect() as connection:
        row = connection.execute(
            "SELECT id, title, body FROM questions WHERE id = ?", (qid,)
        ).fetchone()
    if row is None:
        return None
    return {"id": row["id"], "title": row["title"], "body": row["body"]}
# endregion detail
