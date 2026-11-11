"""在新 Session 中修改一条已提交的问题：先 SELECT，flush 时 UPDATE。

运行：uv run --env-file .env python -m examples.ex03_update_one [qid]
qid 默认 103，即 ex02 在刚恢复的固定数据上创建的问题。
"""

import sys

from app.database import SessionLocal
from app.models import Question
from app.schemas import QuestionNotFound


# region update-one
def update_one_demo(session_factory, qid):
    with session_factory() as session:
        try:
            question = session.get(Question, qid)
            if question is None:
                raise QuestionNotFound()
            question.body = "修改属性后，由 Session 生成对应的更新语句。"
            session.flush()
            result = question.id, question.body
            session.commit()
            return result
        except Exception:
            session.rollback()
            raise
# endregion update-one


if __name__ == "__main__":
    qid = int(sys.argv[1]) if len(sys.argv) > 1 else 103
    print(update_one_demo(SessionLocal, qid))
