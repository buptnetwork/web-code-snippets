"""参数绑定：作者编号由 Python 传入，SQL 文本不变。"""

import psycopg
import pytest

from labs.binding import find_questions_by_author
from tests.helpers import values


@pytest.mark.parametrize("author_id, expected", [(1, [101]), (2, [102]), (9, [])])
def test_author_is_bound_as_value(five_tables, author_id, expected):
    assert values(find_questions_by_author(five_tables, author_id), "id") == [(qid,) for qid in expected]


def test_rows_are_dicts_with_two_columns(five_tables):
    rows = find_questions_by_author(five_tables, 1)
    assert set(rows[0]) == {"id", "title"}


def test_sql_looking_input_is_not_executed(five_tables):
    # 值只会被当作 bigint 字面量，不会变成筛选条件；这里因类型不合法而报错，不是返回全表
    with pytest.raises(psycopg.errors.DataError):
        find_questions_by_author(five_tables, "1 OR 1=1")
