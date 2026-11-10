"""Engine 与 Session 工厂；数据库 URL 由教师配置取得，不写入源码或日志。"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


# region session-factory
def make_session_factory(database_url, *, echo=False):
    engine = create_engine(
        database_url, echo=echo, pool_pre_ping=True,
        isolation_level="READ COMMITTED",
    )
    return engine, sessionmaker(bind=engine, expire_on_commit=False)
# endregion session-factory
