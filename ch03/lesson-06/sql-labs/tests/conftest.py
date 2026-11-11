"""测试共用夹具：每个测试在新建的临时 schema 中运行，结束后删除。

需要 PG* 环境变量指向可丢弃的教学数据库（PostgreSQL 16+、UTF8）。
运行：uv run --env-file .env pytest
"""

import pytest

from examples.ex01_two_tables import create_two_tables
from examples.ex03_five_tables import create_five_tables
from labs.connection import connect, isolated_schema


@pytest.fixture
def conn():
    """一个 autocommit 连接，独占一个临时 schema；用完删除 schema 并关闭连接。"""
    try:
        connection = connect()
    except RuntimeError as exc:
        pytest.exit(str(exc), returncode=2)
    with connection:
        if connection.info.server_version < 160000:
            pytest.exit("需要 PostgreSQL 16+", returncode=2)
        if connection.execute("SHOW server_encoding").fetchone()["server_encoding"] != "UTF8":
            pytest.exit("教学数据库需要 UTF8 编码", returncode=2)
        connection.execute("SET statement_timeout = '10s'")
        with isolated_schema(connection):
            yield connection


@pytest.fixture
def two_tables(conn):
    """两表阶段的固定数据：问题 101、102，回答 201–203。"""
    create_two_tables(conn)
    return conn


@pytest.fixture
def five_tables(conn):
    """五表阶段的固定数据：另加两位用户、两个标签与三条关联。"""
    create_five_tables(conn)
    return conn
