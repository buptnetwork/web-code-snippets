"""对象读写与事务观察示例；调用者传入已配置的 Session 工厂或 Session。

写入示例只在固定数据的独立副本运行，不与只读查询示例共用数据。
schemas 指第 5 课已有的输入输出模型与业务异常（question-api/models.py）。
"""

from sqlalchemy import select

from orm_models import Question
from schemas import QuestionNotFound


# region read-one
def read_one_demo(session_factory):
    with session_factory() as session:
        question = session.get(Question, 101)
        if question is None:
            return None
        return question.id, question.title
# endregion read-one


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


# region visibility-probe
def add_and_query_probe(session, payload, *, author_id):
    question = Question(title=payload.title, body=payload.body, author_id=author_id)
    session.add(question)
    found = session.scalar(select(Question).where(Question.title == payload.title))
    return question, found
# endregion visibility-probe
