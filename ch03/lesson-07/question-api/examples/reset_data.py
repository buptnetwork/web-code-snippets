"""把教学库恢复为固定数据：清空五张表，再执行 sql/seed.sql。

只对可丢弃的教学数据库运行：五张表中的现有记录会全部删除。
前提：已执行 uv run --env-file .env alembic upgrade head。
运行：uv run --env-file .env python -m examples.reset_data
"""

from pathlib import Path

from app.database import engine

SEED = Path(__file__).resolve().parents[1] / "sql" / "seed.sql"


def reset_data():
    with engine.begin() as conn:
        conn.exec_driver_sql("TRUNCATE question_tags, answers, questions, tags, users RESTART IDENTITY")
        conn.exec_driver_sql(SEED.read_text(encoding="utf-8"))


if __name__ == "__main__":
    reset_data()
    print("已恢复固定数据：用户 1、2；问题 101、102；回答 201–203；标签 python、sql")
