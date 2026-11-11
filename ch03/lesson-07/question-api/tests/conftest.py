"""测试共用夹具：每个测试在新建的临时 schema 中迁移并导入固定数据，结束后删除该 schema。

需要 DATABASE_URL 指向可丢弃的教学数据库（PostgreSQL 16+）。
运行：uv run --env-file .env pytest
"""

import os
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import event, make_url

if not os.environ.get("DATABASE_URL"):
    pytest.exit("请先设置 DATABASE_URL（指向可丢弃的教学数据库），示例见 .env.example", returncode=2)

from app.database import engine as admin_engine  # noqa: E402
from app.database import get_session, make_session_factory  # noqa: E402
from app.main import app  # noqa: E402
from tests.helpers import PROJECT, upgrade_head  # noqa: E402

SEED = (PROJECT / "sql" / "seed.sql").read_text(encoding="utf-8")


@pytest.fixture
def new_schema():
    """返回一个函数：每调用一次，新建一个空 schema，并返回只连接它的 (engine, Session 工厂)。"""
    created = []

    def create():
        schema = f"lesson07_test_{uuid4().hex}"
        with admin_engine.begin() as conn:
            conn.exec_driver_sql(f'CREATE SCHEMA "{schema}"')
        options = f"-c search_path={schema} -c timezone=UTC -c statement_timeout=10000"
        url = make_url(os.environ["DATABASE_URL"]).update_query_dict({"options": options})
        engine, sessions = make_session_factory(url)
        created.append((schema, engine))
        return engine, sessions

    yield create
    for schema, engine in created:
        engine.dispose()
        with admin_engine.begin() as conn:
            conn.exec_driver_sql(f'DROP SCHEMA "{schema}" CASCADE')


@pytest.fixture
def db(new_schema):
    """升级到 head 并导入固定数据的临时数据库。"""
    engine, sessions = new_schema()
    with engine.begin() as conn:
        upgrade_head(conn)
        conn.exec_driver_sql(SEED)
    return engine, sessions


@pytest.fixture
def engine(db):
    return db[0]


@pytest.fixture
def sessions(db):
    return db[1]


@pytest.fixture
def sql_log(engine):
    """记录发给数据库的每条 SQL；测试在要观察的操作之前调用 sql_log.clear()。"""
    statements = []

    def record(conn, cursor, statement, parameters, context, executemany):
        statements.append(statement.lstrip())

    event.listen(engine, "before_cursor_execute", record)
    yield statements
    event.remove(engine, "before_cursor_execute", record)


@pytest.fixture
def client(sessions):
    """接口测试：把 get_session 换成连接临时数据库的版本。"""
    def override():
        with sessions() as session:
            yield session

    app.dependency_overrides[get_session] = override
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()
