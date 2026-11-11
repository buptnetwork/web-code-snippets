"""新增一条问题，观察构造、add、flush、commit 各阶段 id 的变化。

运行：uv run --env-file .env python -m examples.ex02_create_one
标题有唯一约束，重复运行会失败；先运行 examples.reset_data 恢复固定数据。
"""

from app.database import SessionLocal
from app.models import Question


# region create-one
def create_one_demo(session_factory):
    question = Question(
        title="ORM 如何保存一条问题？",
        body="通过同一个对象观察新增记录和事务提交。",
        author_id=1,
    )
    print("构造后", question.id)
    with session_factory() as session:
        try:
            session.add(question)
            print("add 后", question.id)
            session.flush()
            print("flush 后", question.id, question.created_at)
            qid = question.id
            session.commit()
            return qid
        except Exception:
            session.rollback()
            raise
# endregion create-one


if __name__ == "__main__":
    print("qid =", create_one_demo(SessionLocal))
