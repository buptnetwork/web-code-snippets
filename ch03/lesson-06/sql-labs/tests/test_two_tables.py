"""两表阶段：建表与固定数据、读取区段、序列校准，以及此阶段还没有作者列。"""

from examples.ex01_two_tables import create_two_tables, read_back
from tests.helpers import next_id, values

COLUMNS = """
    SELECT column_name FROM information_schema.columns
    WHERE table_schema = current_schema() AND table_name = 'questions'
"""


def test_init_gives_two_questions_and_three_answers(conn):
    create_two_tables(conn)
    questions = conn.execute("SELECT id FROM questions ORDER BY id").fetchall()
    answers = conn.execute("SELECT id, question_id FROM answers ORDER BY id").fetchall()
    assert values(questions, "id") == [(101,), (102,)]
    assert values(answers, "id", "question_id") == [(201, 101), (202, 101), (203, 101)]


def test_read_region_returns_two_result_sets(two_tables):
    questions, answers = read_back(two_tables)
    assert values(questions, "id", "title") == [
        (101, "Python 如何读取问题列表？"), (102, "SQL 查询从哪里开始？"),
    ]
    assert values(answers, "id") == [(201,), (202,), (203,)]


def test_questions_have_no_author_column_yet(two_tables):
    rows = two_tables.execute(COLUMNS).fetchall()
    assert {row["column_name"] for row in rows} == {"id", "title", "body", "created_at"}


def test_sequences_are_calibrated(two_tables):
    # 显式插入 id 不推进序列，校准后下一条新增才拿到 103 与 204
    assert next_id(two_tables, "questions") == 103
    assert next_id(two_tables, "answers") == 204
