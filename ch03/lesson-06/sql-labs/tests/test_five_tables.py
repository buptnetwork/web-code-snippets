"""五表阶段：固定数据、NULL 作者、关联位置、序列校准与外键删除策略。"""

import pytest

from examples.ex03_five_tables import row_counts, unknown_author
from tests.helpers import next_id, values

LINKS = "SELECT question_id, tag_id, position FROM question_tags ORDER BY question_id, position"
FOREIGN_KEYS = """
    SELECT confdeltype, condeferrable FROM pg_constraint
    WHERE connamespace = current_schema()::regnamespace AND contype = 'f'
"""


def test_row_counts(five_tables):
    assert row_counts(five_tables) == {
        "users": 2, "questions": 2, "answers": 3, "tags": 2, "question_tags": 3,
    }


def test_questions_keep_identity_and_gain_author(five_tables):
    rows = five_tables.execute("SELECT id, title, author_id FROM questions ORDER BY id").fetchall()
    assert values(rows, "id", "author_id") == [(101, 1), (102, 2)]
    assert rows[0]["title"] == "Python 如何读取问题列表？"


def test_answer_202_author_is_null(five_tables):
    assert values(unknown_author(five_tables), "id", "question_id") == [(202, 101)]


def test_tag_links_keep_position(five_tables):
    rows = five_tables.execute(LINKS).fetchall()
    assert values(rows, "question_id", "tag_id", "position") == [(101, 1, 1), (101, 2, 2), (102, 1, 1)]


@pytest.mark.parametrize("table, expected", [("users", 3), ("questions", 103), ("answers", 204), ("tags", 3)])
def test_sequences_are_calibrated(five_tables, table, expected):
    assert next_id(five_tables, table) == expected


def test_foreign_keys_are_no_action_and_not_deferrable(five_tables):
    rows = five_tables.execute(FOREIGN_KEYS).fetchall()
    assert len(rows) == 5
    # 'a' 就是 NO ACTION：不级联删除，也不自动置空
    assert all(row == {"confdeltype": "a", "condeferrable": False} for row in rows)


def test_session_runs_in_utc(five_tables):
    assert five_tables.execute("SELECT current_setting('TimeZone') AS tz").fetchone()["tz"] == "UTC"
