"""数据服务：字面搜索、分页、详情、创建，以及失败时整体回滚。"""

import pydantic
import pytest
from sqlalchemy import exc

from app import services
from app.schemas import DuplicateTitle, QuestionNotFound, QuestionOut
from tests.helpers import make_payload, snapshot


@pytest.mark.parametrize("keyword, expected", [("", [102, 101]), ("  PYTHON  ", [101]), ("%", []), ("_", [])])
def test_literal_search(sessions, keyword, expected):
    with sessions() as session:
        result = services.list_questions_orm(session, keyword=keyword)
    assert [q.id for q in result.items] == expected
    assert result.total == len(expected)


@pytest.mark.parametrize("page, expected", [(1, [102]), (2, [101]), (3, [])])
def test_list_pages(sessions, page, expected):
    with sessions() as session:
        result = services.list_questions_orm(session, page=page, page_size=1)
    assert [q.id for q in result.items] == expected
    assert result.total == 2 and result.page == page


@pytest.mark.parametrize("page, selects", [(1, 3), (3, 2)])
def test_list_select_count(sessions, sql_log, page, selects):
    # 计数、问题、标签各一条；页中没有问题时不需要读标签
    sql_log.clear()
    with sessions() as session:
        services.list_questions_orm(session, page=page, page_size=1)
    assert len(sql_log) == selects


def test_detail_has_five_fields_and_ordered_tags(sessions):
    with sessions() as session:
        dto = services.get_question_service(session, 101)
    assert dto.tags == ["python", "sql"]
    assert set(dto.model_dump()) == {"id", "title", "body", "tags", "created_at"}


@pytest.mark.parametrize("qid", [0, -1, 999])
def test_missing_detail_raises_business_error(sessions, qid):
    with sessions() as session, pytest.raises(QuestionNotFound):
        services.get_question_service(session, qid)


def test_create_then_read_back_in_new_session(sessions):
    with sessions() as session:
        created = services.create_question_service(
            session, make_payload("完整服务新问题的标题", ["python", "新标签"]), author_id=1,
        )
    assert created.tags == ["python", "新标签"]
    with sessions() as session:
        assert services.get_question_service(session, created.id) == created


def test_duplicate_title_becomes_business_error_and_rolls_back(engine, sessions):
    before = snapshot(engine)
    with sessions() as session, pytest.raises(DuplicateTitle):
        services.create_question_service(session, make_payload("Python 如何读取问题列表？"), author_id=1)
    assert snapshot(engine) == before


def test_foreign_key_error_is_not_reported_as_duplicate_title(sessions):
    with sessions() as session, pytest.raises(exc.IntegrityError) as caught:
        services.create_question_service(session, make_payload("不存在作者的教学问题"), author_id=999)
    assert caught.value.orig.sqlstate == "23503"


def test_dto_failure_happens_before_commit(engine, sessions, monkeypatch):
    def broken_dto(question):
        return QuestionOut(id="不是整数", title=question.title, body=question.body, tags=[], created_at=question.created_at)

    monkeypatch.setattr(services, "question_to_dto", broken_dto)
    before = snapshot(engine)
    with sessions() as session, pytest.raises(pydantic.ValidationError):
        services.create_question_service(
            session, make_payload("输出校验失败的教学问题", ["应当回滚的新标签"]), author_id=1,
        )
    assert snapshot(engine) == before  # 问题、新标签与关联都没有留下


def test_duplicate_tags_are_removed(sessions):
    # 候选行为：五表结构下同一问题不能重复关联同一标签，因此写入时去重；接口契约仍待确认。
    with sessions() as session:
        result = services.create_question_service(
            session, make_payload("重复标签迁移候选行为", ["a", "a", "", " b"]), author_id=1,
        )
    assert result.tags == ["a", "", " b"]
