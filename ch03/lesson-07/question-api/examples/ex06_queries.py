"""第 6 课 Q1–Q4 的 ORM 写法；只读固定的两问题、三回答数据。

运行：uv run --env-file .env python -m examples.ex06_queries
"""

from sqlalchemy import func, select

from app.database import SessionLocal
from app.models import Answer, Question


# region q1-objects
def questions_by_author(session, author_id):
    statement = (
        select(Question)
        .where(Question.author_id == author_id)
        .order_by(Question.id)
    )
    return session.scalars(statement).all()
# endregion q1-objects


# region q1-columns
def question_columns_by_author(session, author_id):
    statement = (
        select(Question.id, Question.title)
        .where(Question.author_id == author_id)
        .order_by(Question.id)
    )
    return session.execute(statement).all()
# endregion q1-columns


# region q2-join
def question_answer_pairs(session):
    statement = (
        select(Question.id.label("question_id"), Question.title, Answer.id.label("answer_id"))
        .join(Answer, Answer.question_id == Question.id)
        .order_by(Question.id, Answer.id)
    )
    return session.execute(statement).all()
# endregion q2-join


# region q3-counts
def question_answer_counts(session):
    statement = (
        select(Question.id, Question.title, func.count(Answer.id).label("answer_count"))
        .outerjoin(Answer, Answer.question_id == Question.id)
        .group_by(Question.id, Question.title)
        .order_by(Question.id)
    )
    return session.execute(statement).all()
# endregion q3-counts


# region q4-page
def question_page_demo(session, page):
    statement = select(Question).order_by(Question.id.desc()).offset(page - 1).limit(1)
    questions = session.scalars(statement).all()
    total = session.scalar(select(func.count()).select_from(Question))
    return [q.id for q in questions], total
# endregion q4-page


if __name__ == "__main__":
    with SessionLocal() as session:
        print("Q1 对象：", [(q.id, q.title) for q in questions_by_author(session, 1)])
        print("Q1 两列：", [tuple(row) for row in question_columns_by_author(session, 1)])
        print("Q2 配对：", [tuple(row) for row in question_answer_pairs(session)])
        print("Q3 计数：", [tuple(row) for row in question_answer_counts(session)])
        for page in (1, 2, 3):
            print(f"Q4 第 {page} 页：", question_page_demo(session, page))
