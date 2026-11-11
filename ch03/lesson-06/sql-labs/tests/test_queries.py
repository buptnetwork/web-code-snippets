"""Q1–Q4 与辅助查询：结果与课件里的结果表逐行一致。"""

import pytest

from examples.ex07_order_paging import page
from tests.helpers import query, values


def test_q1_filters_by_author(five_tables):
    assert values(query(five_tables, "q1"), "id", "title") == [(101, "Python 如何读取问题列表？")]


def test_q2_pairs_question_with_answers(five_tables):
    rows = query(five_tables, "q2")
    assert values(rows, "question_id", "answer_id") == [(101, 201), (101, 202), (101, 203)]
    assert all(row["title"] == "Python 如何读取问题列表？" for row in rows)


def test_q3_counts_keep_question_without_answers(five_tables):
    assert values(query(five_tables, "q3"), "id", "answer_count") == [(101, 3), (102, 0)]


@pytest.mark.parametrize("offset, expected", [(0, [102]), (1, [101]), (2, [])])
def test_q4_pages(five_tables, offset, expected):
    assert values(page(five_tables, offset), "id") == [(qid,) for qid in expected]


def test_total_and_filtered_total(five_tables):
    assert query(five_tables, "total") == [{"total": 2}]
    assert query(five_tables, "filtered-total") == [{"total": 1}]


def test_time_order_breaks_tie_by_id(five_tables):
    assert values(query(five_tables, "time-order"), "id") == [(102,), (101,)]


def test_tag_read_restores_position_order(five_tables):
    assert values(query(five_tables, "tag-read"), "name") == [("python",), ("sql",)]


def test_left_join_keeps_four_rows(five_tables):
    # 两个 NULL 来源不同：202 的作者未知，102 根本没有回答
    assert values(query(five_tables, "left-rows"), "question_id", "answer_id", "author_id") == [
        (101, 201, 2), (101, 202, None), (101, 203, 2), (102, None, None),
    ]


def test_three_counts_differ(five_tables):
    assert values(query(five_tables, "count-compare"), "id", "joined_rows", "answers", "known_authors") == [
        (101, 3, 3, 2), (102, 1, 0, 0),
    ]
