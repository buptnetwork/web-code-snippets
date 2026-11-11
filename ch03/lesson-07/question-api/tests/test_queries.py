"""Q1–Q4 的 ORM 查询结果，以及 lazy 与 selectinload 两种加载方式发出的 SELECT 条数。"""

import pytest

from examples.ex06_queries import (
    question_answer_counts,
    question_answer_pairs,
    question_columns_by_author,
    question_page_demo,
    questions_by_author,
)
from examples.ex07_loading import read_answer_bodies


@pytest.mark.parametrize("author_id, expected", [(1, [101]), (2, [102]), (9, [])])
def test_q1_by_author(sessions, author_id, expected):
    with sessions() as session:
        assert [q.id for q in questions_by_author(session, author_id)] == expected
        assert [row.id for row in question_columns_by_author(session, author_id)] == expected


def test_q1_columns_are_two_value_rows(sessions):
    with sessions() as session:
        rows = question_columns_by_author(session, 1)
    assert [tuple(row) for row in rows] == [(101, "Python 如何读取问题列表？")]


def test_q2_join_gives_three_pairs(sessions):
    with sessions() as session:
        rows = question_answer_pairs(session)
    assert [(row.question_id, row.answer_id) for row in rows] == [(101, 201), (101, 202), (101, 203)]


def test_q3_counts_keep_question_without_answers(sessions):
    with sessions() as session:
        rows = question_answer_counts(session)
    assert [(row.id, row.answer_count) for row in rows] == [(101, 3), (102, 0)]


@pytest.mark.parametrize("page, expected", [(1, [102]), (2, [101]), (3, [])])
def test_q4_page(sessions, page, expected):
    with sessions() as session:
        assert question_page_demo(session, page) == (expected, 2)


@pytest.mark.parametrize("eager, selects", [(False, 3), (True, 2)])
def test_answer_loading_select_count(sessions, sql_log, eager, selects):
    sql_log.clear()
    with sessions() as session:
        result = read_answer_bodies(session, eager=eager)
    assert len(sql_log) == selects
    assert all(s.upper().startswith("SELECT") for s in sql_log)
    assert [a["id"] for a in result[0]["answers"]] == [201, 202, 203]
    assert result[1]["answers"] == []


def test_lazy_and_selectinload_give_same_result(sessions):
    with sessions() as session:
        lazy = read_answer_bodies(session, eager=False)
    with sessions() as session:
        eager = read_answer_bodies(session, eager=True)
    assert lazy == eager
