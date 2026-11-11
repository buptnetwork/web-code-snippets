"""多个测试文件共用的小工具。"""

from pathlib import Path

from alembic import command
from alembic.config import Config
from sqlalchemy import text

from app.schemas import QuestionCreate

PROJECT = Path(__file__).resolve().parents[1]
TABLES = ("users", "questions", "answers", "tags", "question_tags")


def upgrade_head(connection):
    """在传入的连接上执行 alembic upgrade head（见 migrations/env.py 的第一个分支）。"""
    config = Config(PROJECT / "alembic.ini")
    config.attributes["connection"] = connection
    command.upgrade(config, "head")


def make_payload(title, tags=None):
    return QuestionCreate(title=title, body="这是符合当前输入规则的教学问题正文。", tags=tags or [])


def snapshot(engine):
    """读出五张表的全部记录，用于比较操作前后数据是否变化。"""
    with engine.connect() as conn:
        return {table: conn.execute(text(f"SELECT * FROM {table} ORDER BY 1, 2")).all() for table in TABLES}
