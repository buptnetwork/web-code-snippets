"""预期拒绝：重复关联与三处外键边界；失败回滚后数据不变、连接可继续用。"""

import psycopg
import pytest

from examples.ex04_constraints import constraint_failures, rejected
from labs.sqlfile import region
from tests.helpers import values

LINKS = "SELECT question_id, tag_id, position FROM question_tags ORDER BY question_id, position"
ANSWERS = "SELECT id FROM answers ORDER BY id"


def test_four_expected_rejections(five_tables):
    assert constraint_failures(five_tables) == [
        ("重复关联同一标签", "23505", "question_tags_pkey"),
        ("回答改到不存在的问题", "23503", "answers_question_id_fkey"),
        ("删除仍被回答引用的问题", "23503", "answers_question_id_fkey"),
        ("删除仍被问题引用的用户", "23503", "questions_author_id_fkey"),
    ]


def test_nothing_changed_after_rejections(five_tables):
    before = five_tables.execute(LINKS).fetchall()
    constraint_failures(five_tables)
    assert five_tables.execute(LINKS).fetchall() == before
    assert values(five_tables.execute(ANSWERS).fetchall(), "id") == [(201,), (202,), (203,)]


def test_duplicate_is_unique_violation_not_foreign_key(five_tables):
    five_tables.execute("BEGIN")
    with pytest.raises(psycopg.errors.UniqueViolation) as caught:
        five_tables.execute(region("05-transactions.sql", "duplicate"))
    five_tables.execute("ROLLBACK")
    assert caught.value.diag.constraint_name == "question_tags_pkey"


def test_rejected_reports_when_write_succeeds(five_tables):
    # 回答 203 没有被引用，可以删除；这不是预期拒绝，函数必须报出来（删除本身已回滚）
    with pytest.raises(AssertionError):
        rejected(five_tables, "DELETE FROM answers WHERE id = 203")
    assert values(five_tables.execute(ANSWERS).fetchall(), "id") == [(201,), (202,), (203,)]
