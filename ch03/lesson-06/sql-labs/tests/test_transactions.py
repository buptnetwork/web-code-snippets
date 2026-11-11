"""修改与回滚：整段执行自带 BEGIN…ROLLBACK 的区段，数据回到原样。"""

from psycopg.pq import TransactionStatus

from examples.ex02_update_delete import delete_then_rollback, update_then_rollback
from tests.helpers import values

QUESTIONS = "SELECT id, body FROM questions ORDER BY id"
ANSWERS = "SELECT id FROM answers ORDER BY id"


def test_update_region_shows_new_body_then_restores(two_tables):
    before = two_tables.execute(QUESTIONS).fetchall()
    assert update_then_rollback(two_tables) == [{"id": 102, "body": "更新后的说明仍然围绕表和记录展开。"}]
    assert two_tables.execute(QUESTIONS).fetchall() == before


def test_delete_region_shows_two_answers_then_restores(two_tables):
    assert values(delete_then_rollback(two_tables), "id") == [(201,), (202,)]
    assert values(two_tables.execute(ANSWERS).fetchall(), "id") == [(201,), (202,), (203,)]


def test_regions_also_work_on_five_tables(five_tables):
    update_then_rollback(five_tables)
    delete_then_rollback(five_tables)
    assert values(five_tables.execute(ANSWERS).fetchall(), "id") == [(201,), (202,), (203,)]


def test_rollback_in_sql_really_took_effect(two_tables):
    update_then_rollback(two_tables)
    # 区段末尾的 ROLLBACK 已执行，连接不在事务中，可以继续正常查询
    assert two_tables.info.transaction_status == TransactionStatus.IDLE
    assert two_tables.execute("SELECT count(*) AS n FROM questions").fetchone()["n"] == 2
