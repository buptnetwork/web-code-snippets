"""autoflush：查询前 Session 先把待写入的对象 flush，查询能找到它，但仍未提交。

运行：uv run --env-file .env python -m examples.ex05_autoflush
脚本不 commit：Session 关闭后这条问题不会保存。
"""

from sqlalchemy import select

from app.database import SessionLocal
from app.models import Question
from app.schemas import QuestionCreate


# region visibility-probe
def add_and_query_probe(session, payload, *, author_id):
    question = Question(title=payload.title, body=payload.body, author_id=author_id)
    session.add(question)
    found = session.scalar(select(Question).where(Question.title == payload.title))
    return question, found
# endregion visibility-probe


if __name__ == "__main__":
    payload = QuestionCreate(title="自动刷新观察用的问题", body="查询之前先把待写入的对象发给数据库。")
    with SessionLocal() as session:
        question, found = add_and_query_probe(session, payload, author_id=1)
        print("found 是同一个对象：", found is question, "id =", question.id)
    with SessionLocal() as session:
        print("关闭后重新查询：", session.scalar(select(Question).where(Question.title == payload.title)))
