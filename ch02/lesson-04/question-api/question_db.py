"""第 3 课数据模块：SQLite 连接、建库／升级、参数化查询与插入骨架。

理解边界（对应底稿〇「教师提供与学生负责」）：
- `open_connection()`、建库与数据升级为「要求会用」：按约定获取和关闭连接，不实现数据库设施。
- `row_to_question`、`search_questions`、`insert_question`、`find_question` 为「要求解释」：
  说清占位符与值的对应关系，按模型字段改写并接入端点。
本模块只读写数据，不做 HTTP 翻译，也不提交事务（commit 由服务层显式执行）。全部数据均为教学虚构。
"""

# region config
import json
import os
import sqlite3
from contextlib import closing
from datetime import datetime, timezone
from pathlib import Path

# 默认落在包目录下，可用 DB_PATH 环境变量覆盖（教师验证时用临时库）。
DB_PATH = Path(os.environ.get("DB_PATH", Path(__file__).resolve().parent / "questions.db"))

# 固定、带时区的 created_at；保留原 id/title/body，补 tags=[]。
SEED_CREATED_AT = "2026-09-01T08:00:00+00:00"
SEEDS = [
    (3, "React 的 props 是什么？", "想知道组件怎样接收数据。", "[]", SEED_CREATED_AT),
    (2, "FastAPI 如何接收路径参数？", "希望从地址取出问题编号。", "[]", SEED_CREATED_AT),
    (1, "浏览器怎样显示列表？", "先确认接口能返回正确的数据。", "[]", SEED_CREATED_AT),
]

SCHEMA = (
    "CREATE TABLE IF NOT EXISTS questions ("
    "id INTEGER PRIMARY KEY, "
    "title TEXT NOT NULL UNIQUE, "
    "body TEXT NOT NULL, "
    "tags_json TEXT NOT NULL DEFAULT '[]', "
    "created_at TEXT NOT NULL)"
)
# endregion config


# region connect
def open_connection():
    """每次返回一个新连接：Row 工厂 + 非自动提交的写入事务模式。

    端点用 closing(...) 关闭连接；连接的 with 只管理事务，不等于自动关闭连接。
    """
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.isolation_level = "DEFERRED"
    return conn
# endregion connect


# region init
def _upgrade(conn):
    """为从第 2 课三字段库升级来的表补列；新建库已含全部列，此处幂等。"""
    columns = {row["name"] for row in conn.execute("PRAGMA table_info(questions)")}
    if "tags_json" not in columns:
        conn.execute("ALTER TABLE questions ADD COLUMN tags_json TEXT NOT NULL DEFAULT '[]'")
    if "created_at" not in columns:
        conn.execute("ALTER TABLE questions ADD COLUMN created_at TEXT NOT NULL DEFAULT ''")
        conn.execute("UPDATE questions SET created_at = ? WHERE created_at = ''", (SEED_CREATED_AT,))


def init_db():
    """建表、升级并播种；幂等，重复调用不会重复插入或清空既有数据。"""
    with closing(open_connection()) as conn:
        conn.execute(SCHEMA)
        _upgrade(conn)
        count = conn.execute("SELECT count(*) FROM questions").fetchone()[0]
        if count == 0:
            conn.executemany(
                "INSERT INTO questions (id, title, body, tags_json, created_at) "
                "VALUES (?, ?, ?, ?, ?)",
                SEEDS,
            )
        conn.commit()


def reset_db():
    """教师复位设施：清空并重新播种为固定三条，供自检重复运行。"""
    with closing(open_connection()) as conn:
        conn.execute("DELETE FROM questions")
        conn.executemany(
            "INSERT INTO questions (id, title, body, tags_json, created_at) "
            "VALUES (?, ?, ?, ?, ?)",
            SEEDS,
        )
        conn.commit()
# endregion init


# region row-mapping
def row_to_question(row):
    return {
        "id": row["id"],
        "title": row["title"],
        "body": row["body"],
        "tags": json.loads(row["tags_json"]),
        "created_at": row["created_at"],
    }
# endregion row-mapping


# region search
def search_questions(conn, keyword, page, page_size):
    params = {
        "keyword": keyword.strip(),
        "limit": page_size,
        "offset": (page - 1) * page_size,
    }
    rows = conn.execute("""
        SELECT id, title, body, tags_json, created_at
        FROM questions
        WHERE instr(lower(title), lower(:keyword)) > 0
           OR instr(lower(body), lower(:keyword)) > 0
        ORDER BY id DESC
        LIMIT :limit OFFSET :offset
    """, params).fetchall()
    total = conn.execute("""
        SELECT count(*) FROM questions
        WHERE instr(lower(title), lower(:keyword)) > 0
           OR instr(lower(body), lower(:keyword)) > 0
    """, {"keyword": params["keyword"]}).fetchone()[0]
    return {
        "items": [row_to_question(row) for row in rows],
        "total": total,
        "page": page,
    }
# endregion search


# region insert-find
def insert_question(conn, payload):
    cursor = conn.execute("""
        INSERT INTO questions (title, body, tags_json, created_at)
        VALUES (:title, :body, :tags_json, :created_at)
    """, {
        "title": payload.title,
        "body": payload.body,
        "tags_json": json.dumps(payload.tags, ensure_ascii=False),
        "created_at": datetime.now(timezone.utc).isoformat(),
    })
    return cursor.lastrowid


def find_question(conn, qid):
    row = conn.execute("""
        SELECT id, title, body, tags_json, created_at
        FROM questions WHERE id = :qid
    """, {"qid": qid}).fetchone()
    return None if row is None else row_to_question(row)
# endregion insert-find
