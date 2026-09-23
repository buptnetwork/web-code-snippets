"""初始化固定的 30 个问题、15 个回答、5 个标签；只操作隔离教学库。"""
import argparse
import os
from pathlib import Path

from sqlalchemy import create_engine, text
from sqlalchemy.engine import make_url


def seed_database(database_url: str, reset: bool = False):
    url = make_url(database_url)
    if url.get_backend_name() == "sqlite":
        if Path(url.database or "").name != "demo.db":
            raise ValueError("安全限制：SQLite 教学库文件名必须是 demo.db")
    elif url.get_backend_name() == "postgresql":
        if url.host not in {"localhost", "127.0.0.1", "::1"} or not (url.database or "").startswith("m0_"):
            raise ValueError("安全限制：只允许本机且库名以 m0_ 开头的 PostgreSQL 教学库")
    else:
        raise ValueError("只支持 SQLite 与 PostgreSQL")
    engine = create_engine(database_url)
    try:
        with engine.begin() as conn:
            for statement in Path(__file__).with_name("seed.sql").read_text().split(";"):
                if statement.strip():
                    conn.execute(text(statement))
            count = conn.execute(text("SELECT COUNT(*) FROM questions")).scalar_one()
            if count and not reset:
                raise ValueError("已有数据。确认是隔离教学库后使用 --reset 重置")
            if reset:
                for table in ("answers", "questions", "tags"):
                    conn.execute(text(f"DELETE FROM {table}"))
            topics = ["react", "python", "http", "sql", "debug"]
            conn.execute(text(
                "INSERT INTO questions (id,title,body,created_at) VALUES (:id,:title,:body,:created_at)"
            ), [{"id": i, "title": f"{topics[(i - 1) % 5]} 练习问题 {i:02d}",
                 "body": f"这是虚构教学数据，第 {i} 个问题，不对应真实用户。",
                 "created_at": "2026-09-01T08:00:00Z"} for i in range(1, 31)])
            conn.execute(text("INSERT INTO answers (id,question_id,body) VALUES (:id,:qid,:body)"),
                         [{"id": i, "qid": i, "body": f"虚构回答 {i}"} for i in range(1, 16)])
            conn.execute(text("INSERT INTO tags (id,name) VALUES (:id,:name)"),
                         [{"id": i, "name": topic} for i, topic in enumerate(topics, 1)])
    finally:
        engine.dispose()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--reset", action="store_true", help="清空隔离教学库的三张表并重新填充")
    args = parser.parse_args()
    seed_database(os.getenv("DATABASE_URL", "sqlite:///./demo.db"), args.reset)
    print("初始化完成：questions=30, answers=15, tags=5；全部为虚构数据")
