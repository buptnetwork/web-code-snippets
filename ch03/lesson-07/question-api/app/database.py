"""Engine、Session 工厂与每个请求使用的 Session 依赖。

数据库 URL 从环境变量 DATABASE_URL 读取，不写入源码或日志。
"""

import os
from typing import Annotated, Iterator

from fastapi import Depends
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker


# region session-factory
def make_session_factory(database_url, *, echo=False):
    engine = create_engine(
        database_url, echo=echo, pool_pre_ping=True,
        isolation_level="READ COMMITTED",
    )
    return engine, sessionmaker(bind=engine, expire_on_commit=False)
# endregion session-factory


DATABASE_URL = os.environ.get("DATABASE_URL")
if not DATABASE_URL:
    raise RuntimeError("请先设置环境变量 DATABASE_URL，示例见 .env.example")

engine, SessionLocal = make_session_factory(DATABASE_URL)


# region session-dependency
def get_session() -> Iterator[Session]:
    with SessionLocal() as session:
        yield session


SessionDep = Annotated[Session, Depends(get_session)]
# endregion session-dependency
