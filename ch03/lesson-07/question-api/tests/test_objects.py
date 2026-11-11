"""对象读写与事务：id 何时出现、SQL 何时发出、提交与回滚之后数据库里有什么。"""

import pytest
from sqlalchemy import exc, text

from app.models import Question
from examples.ex01_read_one import read_one_demo
from examples.ex02_create_one import create_one_demo
from examples.ex03_update_one import update_one_demo
from examples.ex04_rollback import rollback_demo
from examples.ex05_autoflush import add_and_query_probe
from tests.helpers import make_payload, snapshot

FIND_BY_TITLE = text("SELECT id FROM questions WHERE title = :title")


def test_get_by_primary_key(sessions):
    assert read_one_demo(sessions) == (101, "Python 如何读取问题列表？")


def test_create_id_appears_after_flush(engine, sessions, sql_log, capsys):
    sql_log.clear()
    qid = create_one_demo(sessions)
    lines = capsys.readouterr().out.splitlines()
    assert qid == 103
    assert lines[0] == "构造后 None"
    assert lines[1] == "add 后 None"
    assert lines[2].startswith("flush 后 103 ")
    # 一条 INSERT … RETURNING 同时取回生成的 id 与 created_at
    assert len(sql_log) == 1
    assert sql_log[0].startswith("INSERT") and "RETURNING" in sql_log[0]
    # 另开连接回读：已经提交
    with engine.connect() as other:
        assert other.scalar(FIND_BY_TITLE, {"title": "ORM 如何保存一条问题？"}) == qid


def test_update_in_new_session(engine, sessions, sql_log):
    qid = create_one_demo(sessions)
    sql_log.clear()
    _, body = update_one_demo(sessions, qid)
    assert [s.split()[0] for s in sql_log] == ["SELECT", "UPDATE"]
    with engine.connect() as other:
        assert other.scalar(text("SELECT body FROM questions WHERE id = :id"), {"id": qid}) == body


def test_rollback_leaves_no_row(engine, sessions, sql_log):
    before = snapshot(engine)
    sql_log.clear()
    with pytest.raises(RuntimeError, match="提交前教学异常"):
        rollback_demo(sessions)
    assert any(s.startswith("INSERT") for s in sql_log)  # INSERT 确实发出过
    assert snapshot(engine) == before


def test_same_session_reuses_object(sessions, sql_log):
    with sessions() as session:
        sql_log.clear()
        assert session.get(Question, 101) is session.get(Question, 101)
        assert len(sql_log) == 1


def test_autoflush_and_visibility(engine, sessions, sql_log):
    payload = make_payload("自动刷新与独立连接可见性")
    with sessions() as session, engine.connect() as other:
        question = Question(title=payload.title, body=payload.body, author_id=1)
        session.add(question)
        assert other.scalar(FIND_BY_TITLE, {"title": payload.title}) is None  # 只有 add：还没有 INSERT
        session.expunge(question)

        sql_log.clear()
        question, found = add_and_query_probe(session, payload, author_id=1)
        assert question is found
        assert [s.split()[0] for s in sql_log] == ["INSERT", "SELECT"]  # 查询前先 flush
        assert other.scalar(FIND_BY_TITLE, {"title": payload.title}) is None  # 未提交，别的连接看不到

        session.commit()
        assert other.scalar(FIND_BY_TITLE, {"title": payload.title}) == question.id


def test_closing_session_does_not_commit(engine, sessions):
    payload = make_payload("关闭前未提交的教学问题")
    with sessions() as session:
        session.add(Question(title=payload.title, body=payload.body, author_id=1))
        session.flush()
    with engine.connect() as other:
        assert other.scalar(FIND_BY_TITLE, {"title": payload.title}) is None


@pytest.mark.parametrize("loaded", [False, True])
def test_delete_referenced_question_rejected_by_foreign_key(engine, sessions, loaded):
    before = snapshot(engine)
    with sessions() as session:
        question = session.get(Question, 101)
        if loaded:
            list(question.answers), list(question.tag_links)
        session.delete(question)
        with pytest.raises(exc.IntegrityError) as caught:
            session.flush()
        assert caught.value.orig.sqlstate == "23503"
        session.rollback()
    assert snapshot(engine) == before
