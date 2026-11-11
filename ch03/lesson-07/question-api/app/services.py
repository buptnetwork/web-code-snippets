"""问题列表、详情与创建的数据服务；服务层显式提交，帮助函数只读写。"""

from sqlalchemy import func, literal, or_, select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import selectinload

from app.models import Question, QuestionTag, Tag
from app.schemas import DuplicateTitle, QuestionListOut, QuestionNotFound, QuestionOut


# region dto-helpers
def tag_load_option():
    return selectinload(Question.tag_links).joinedload(QuestionTag.tag)


def question_to_dto(question):
    return QuestionOut(
        id=question.id, title=question.title, body=question.body,
        tags=[link.tag.name for link in question.tag_links],
        created_at=question.created_at,
    )
# endregion dto-helpers


# region search-condition
def search_condition(keyword):
    needle = func.lower(literal(keyword.strip()).collate("C"))
    return or_(
        func.strpos(func.lower(Question.title.collate("C")), needle) > 0,
        func.strpos(func.lower(Question.body.collate("C")), needle) > 0,
    )
# endregion search-condition


# region list-questions
def list_questions_orm(session, *, keyword="", page=1, page_size=20):
    condition = search_condition(keyword)
    total = session.scalar(select(func.count()).select_from(Question).where(condition))
    statement = (
        select(Question).where(condition).options(tag_load_option())
        .order_by(Question.id.desc())
        .offset((page - 1) * page_size).limit(page_size)
    )
    items = [question_to_dto(q) for q in session.scalars(statement).all()]
    return QuestionListOut(items=items, total=total, page=page)
# endregion list-questions


# region detail
def read_question_dto(session, qid):
    statement = select(Question).where(Question.id == qid).options(tag_load_option())
    question = session.scalar(statement)
    return None if question is None else question_to_dto(question)


def get_question_service(session, qid):
    result = read_question_dto(session, qid)
    if result is None:
        raise QuestionNotFound()
    return result
# endregion detail


# region write-helpers
def get_or_create_tag_id(session, name):
    statement = (
        insert(Tag).values(name=name)
        .on_conflict_do_nothing(constraint="tags_name_key")
        .returning(Tag.id)
    )
    tag_id = session.scalar(statement)
    if tag_id is None:
        tag_id = session.scalar(select(Tag.id).where(Tag.name == name))
    if tag_id is None:
        raise RuntimeError("标签状态已变化")
    return tag_id


def write_question(session, payload, *, author_id):
    question = Question(title=payload.title, body=payload.body, author_id=author_id)
    session.add(question)
    session.flush()
    for position, name in enumerate(dict.fromkeys(payload.tags), start=1):
        tag_id = get_or_create_tag_id(session, name)
        session.add(QuestionTag(question_id=question.id, tag_id=tag_id, position=position))
    return question
# endregion write-helpers


# region create-service
def create_question_service(session, payload, *, author_id):
    try:
        question = write_question(session, payload, author_id=author_id)
        session.flush()
        result = read_question_dto(session, question.id)
        if result is None:
            raise RuntimeError("创建后的回读缺失")
        session.commit()
        return result
    except IntegrityError as exc:
        session.rollback()
        original = exc.orig
        constraint = getattr(getattr(original, "diag", None), "constraint_name", None)
        if getattr(original, "sqlstate", None) == "23505" and constraint == "questions_title_key":
            raise DuplicateTitle() from exc
        raise
    except Exception:
        session.rollback()
        raise
# endregion create-service
