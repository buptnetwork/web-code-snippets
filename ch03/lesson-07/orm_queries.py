"""第 6 课 Q1–Q4 的 ORM 表达与关系加载；只读固定的两问题、三回答基线。"""

from sqlalchemy import func, select
from sqlalchemy.orm import selectinload

from orm_models import Answer, Question


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
