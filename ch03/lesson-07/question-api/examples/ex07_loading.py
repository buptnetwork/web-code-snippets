"""读取问题及回答正文：对比默认 lazy 与 selectinload 发出的 SELECT 条数。

运行：uv run --env-file .env python -m examples.ex07_loading
本脚本打开 echo，终端会依次打印每条 SQL。
"""

from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.database import DATABASE_URL, make_session_factory
from app.models import Question


# region answer-bodies
def read_answer_bodies(session, *, eager=False):
    statement = select(Question).order_by(Question.id)
    if eager:
        statement = statement.options(selectinload(Question.answers))
    questions = session.scalars(statement).all()
    return [
        {"id": q.id, "answers": [{"id": a.id, "body": a.body} for a in q.answers]}
        for q in questions
    ]
# endregion answer-bodies


if __name__ == "__main__":
    engine, sessions = make_session_factory(DATABASE_URL, echo=True)
    for eager in (False, True):
        print(f"\n===== eager={eager} =====")
        with sessions() as session:
            result = read_answer_bodies(session, eager=eager)
        print([(item["id"], [a["id"] for a in item["answers"]]) for item in result])
    engine.dispose()
