"""Alembic 运行环境：连接哪个数据库、以哪份 metadata 为目标。"""

import os
from logging.config import fileConfig

from alembic import context
from sqlalchemy import create_engine

from app.models import Base

config = context.config
target_metadata = Base.metadata


def run_migrations(connection):
    context.configure(connection=connection, target_metadata=target_metadata)
    with context.begin_transaction():
        context.run_migrations()


connection = config.attributes.get("connection")
if connection is not None:
    # 测试传入已打开的连接（指向临时 schema），直接在这个连接上迁移。
    run_migrations(connection)
else:
    # 命令行 alembic upgrade head：按 DATABASE_URL 新建连接，用完释放。
    fileConfig(config.config_file_name)
    engine = create_engine(os.environ["DATABASE_URL"])
    with engine.connect() as connection:
        run_migrations(connection)
    engine.dispose()
