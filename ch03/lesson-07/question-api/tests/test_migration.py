"""迁移：空库升级到 head、重复升级不重复建表、只建结构不导入数据；结果与 ORM 模型一致。"""

from sqlalchemy import inspect, text

from app.models import Base
from tests.helpers import upgrade_head

COLUMNS = """
    SELECT c.relname, a.attname, format_type(a.atttypid, a.atttypmod) AS type,
           a.attnotnull, pg_get_expr(d.adbin, d.adrelid) AS default, co.collname
    FROM pg_class c JOIN pg_namespace n ON n.oid = c.relnamespace
    JOIN pg_attribute a ON a.attrelid = c.oid
    LEFT JOIN pg_attrdef d ON d.adrelid = c.oid AND d.adnum = a.attnum
    LEFT JOIN pg_collation co ON co.oid = a.attcollation
    WHERE n.nspname = current_schema() AND c.relkind = 'r'
      AND c.relname <> 'alembic_version' AND a.attnum > 0 AND NOT a.attisdropped
    ORDER BY c.relname, a.attnum
"""
CONSTRAINTS = """
    SELECT conname, contype, pg_get_constraintdef(oid) AS definition, condeferrable, confdeltype
    FROM pg_constraint WHERE connamespace = current_schema()::regnamespace
      AND conrelid <> COALESCE(to_regclass('alembic_version'), 0)
    ORDER BY conname
"""


def signature(engine):
    """当前 schema 的列（类型、可空、默认值、排序规则）与约束定义。"""
    with engine.connect() as conn:
        schema = conn.scalar(text("SELECT current_schema()"))
        columns = [dict(row) for row in conn.execute(text(COLUMNS)).mappings()]
        constraints = [dict(row) for row in conn.execute(text(CONSTRAINTS)).mappings()]
    # 序列名包含 schema 名，比较时去掉。
    for row in columns:
        if row["default"]:
            row["default"] = row["default"].replace(f"{schema}.", "")
    return columns, constraints


def test_upgrade_empty_database_twice(new_schema):
    engine, _ = new_schema()
    with engine.begin() as conn:
        assert not inspect(conn).has_table("questions")
        upgrade_head(conn)
        upgrade_head(conn)
        assert conn.scalar(text("SELECT version_num FROM alembic_version")) == "001_baseline"
        assert conn.scalar(text("SELECT count(*) FROM questions")) == 0


def test_migration_matches_orm_metadata(new_schema):
    migrated, _ = new_schema()
    with migrated.begin() as conn:
        upgrade_head(conn)
    from_models, _ = new_schema()
    Base.metadata.create_all(from_models)
    assert signature(migrated) == signature(from_models)
