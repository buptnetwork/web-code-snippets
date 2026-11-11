"""按主键读取一条问题：有行得到实例，无行得到 None。

运行：uv run --env-file .env python -m examples.ex01_read_one
"""

from app.database import SessionLocal
from app.models import Question


# region read-one
def read_one_demo(session_factory):
    with session_factory() as session:
        question = session.get(Question, 101)
        if question is None:
            return None
        return question.id, question.title
# endregion read-one


if __name__ == "__main__":
    print(read_one_demo(SessionLocal))
