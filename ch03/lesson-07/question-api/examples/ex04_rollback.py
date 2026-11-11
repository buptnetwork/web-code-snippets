"""INSERT 已发送、提交前出错：rollback 后数据库中没有这条问题。

运行：uv run --env-file .env python -m examples.ex04_rollback
"""

from sqlalchemy import func, select

from app.database import SessionLocal
from app.models import Question


# region rollback-one
def rollback_demo(session_factory):
    with session_factory() as session:
        try:
            question = Question(
                title="提交前失败的教学问题",
                body="这条记录用于解释已发送但尚未提交的写入。",
                author_id=1,
            )
            session.add(question)
            session.flush()
            raise RuntimeError("提交前教学异常")
        except Exception:
            session.rollback()
            raise
# endregion rollback-one


if __name__ == "__main__":
    try:
        rollback_demo(SessionLocal)
    except RuntimeError as exc:
        print("捕获：", exc)
    with SessionLocal() as session:
        count = session.scalar(select(func.count()).where(Question.title == "提交前失败的教学问题"))
    print("数据库中这条标题的记录数：", count)
