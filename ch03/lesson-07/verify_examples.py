"""教师自检：验证第 7 课最终 ORM 源文件，不解析底稿、不触碰 M1 表。

Python 3.12+，SQLAlchemy 2.0.54、psycopg[binary] 3.3.6、Alembic 1.20.0、
FastAPI 0.162.0、httpx 0.28.1；PostgreSQL 16+。
先配置指向隔离教学数据库的 PGHOST / PGPORT / PGDATABASE / PGUSER 等标准变量。
运行（课件仓库根目录）：
  uv run --no-project --with sqlalchemy==2.0.54 --with 'psycopg[binary]==3.3.6' \
    --with alembic==1.20.0 --with fastapi==0.162.0 --with httpx==0.28.1 \
    python snippets/ch03/lesson-07/verify_examples.py

第 7 课示例会真实提交，因此每个阶段新建随机 schema（lesson07_verify_*）；
五表与固定数据取自第 6 课 schema.sql / seed.sql。结束时只删除本脚本创建的 schema。
这验证了对象读写、查询、加载、服务与迁移基线，不是 M1 迁移或完整 HTTP／HTML 验收。
"""

import asyncio
import contextlib
import importlib.util
import io
import shutil
import sys
import tempfile
from pathlib import Path
from uuid import uuid4

import fastapi
import httpx
import psycopg
import pydantic
import sqlalchemy as sa
from alembic import command
from alembic.config import Config
from psycopg import sql
from psycopg.rows import dict_row
from sqlalchemy import event

ROOT = Path(__file__).resolve().parent
LESSON06 = ROOT.parent / "lesson-06"
SCHEMAS_SOURCE = ROOT.parents[1] / "ch02/lesson-05/question-api/models.py"

# 第 5 课输入输出模型与业务异常以 schemas 名称提供给示例模块。
spec = importlib.util.spec_from_file_location("schemas", SCHEMAS_SOURCE)
schemas = importlib.util.module_from_spec(spec)
sys.modules["schemas"] = schemas
spec.loader.exec_module(schemas)
sys.path.insert(0, str(ROOT))

import api  # noqa: E402
import object_demos as demos  # noqa: E402
import orm_queries as queries  # noqa: E402
import question_service as service  # noqa: E402
from orm_models import Base, Question  # noqa: E402
from resources import make_session_factory  # noqa: E402

CREATED = []
ENGINES = []
PASSED = []


def check(ok, label):
    if not ok:
        raise AssertionError(label)
    PASSED.append(label)


def options(schema):
    return f"-c search_path={schema} -c timezone=UTC -c statement_timeout=10000"


def connect(schema):
    return psycopg.connect("", options=options(schema), row_factory=dict_row, connect_timeout=5)


def fixture(mode="ddl", seed=True):
    schema = f"lesson07_verify_{uuid4().hex}"
    with psycopg.connect("", autocommit=True, connect_timeout=5) as admin:
        admin.execute(sql.SQL("CREATE SCHEMA {}").format(sql.Identifier(schema)))
    CREATED.append(schema)
    url = sa.URL.create("postgresql+psycopg", query={"options": options(schema)})
    engine, sessions = make_session_factory(url)
    ENGINES.append(engine)
    if mode == "ddl":
        with connect(schema) as conn:
            conn.execute((LESSON06 / "schema.sql").read_text(encoding="utf-8"))
    elif mode == "models":
        Base.metadata.create_all(engine)
    elif mode == "migration":
        migrate(engine)
    if seed:
        with connect(schema) as conn:
            conn.execute((LESSON06 / "seed.sql").read_text(encoding="utf-8"))
    return schema, engine, sessions


def migrate(engine):
    # 临时最小 Alembic 装配，只运行本目录的固定基线；正式配置由教师工程提供。
    with tempfile.TemporaryDirectory() as directory:
        target = Path(directory)
        (target / "versions").mkdir()
        shutil.copy(ROOT / "migrations/versions/001_baseline.py", target / "versions")
        (target / "env.py").write_text(
            "from alembic import context\n"
            "config = context.config\n"
            "context.configure(connection=config.attributes['connection'], "
            "target_metadata=config.attributes['metadata'])\n"
            "with context.begin_transaction():\n"
            "    context.run_migrations()\n"
        )
        config = Config(stdout=io.StringIO())
        config.set_main_option("script_location", directory)
        config.attributes["metadata"] = Base.metadata
        with engine.begin() as conn:
            config.attributes["connection"] = conn
            check(not sa.inspect(conn).has_table("questions"), "迁移前目标为空")
            command.upgrade(config, "head")
            command.upgrade(config, "head")
            check(conn.scalar(sa.text("SELECT version_num FROM alembic_version")) == "001_baseline", "空库升级与重复升级到 001_baseline")
            check(conn.scalar(sa.text("SELECT count(*) FROM questions")) == 0, "迁移只建结构不播种")


def signature(schema):
    with connect(schema) as conn:
        columns = conn.execute("""
            SELECT c.relname, a.attname, format_type(a.atttypid, a.atttypmod) AS type,
                   a.attnotnull, pg_get_expr(d.adbin, d.adrelid) AS default, co.collname
            FROM pg_class c JOIN pg_namespace n ON n.oid = c.relnamespace
            JOIN pg_attribute a ON a.attrelid = c.oid
            LEFT JOIN pg_attrdef d ON d.adrelid = c.oid AND d.adnum = a.attnum
            LEFT JOIN pg_collation co ON co.oid = a.attcollation
            WHERE n.nspname = current_schema() AND c.relkind = 'r'
              AND c.relname <> 'alembic_version' AND a.attnum > 0 AND NOT a.attisdropped
            ORDER BY c.relname, a.attnum
        """).fetchall()
        constraints = conn.execute("""
            SELECT conname, contype, pg_get_constraintdef(oid) AS definition, condeferrable, confdeltype
            FROM pg_constraint WHERE connamespace = current_schema()::regnamespace
              AND conrelid <> COALESCE(to_regclass('alembic_version'), 0)
            ORDER BY conname
        """).fetchall()
    # 序列名包含 schema，比较时去掉具体 schema 名称。
    for row in columns:
        if row["default"]:
            row["default"] = row["default"].replace(f"{schema}.", "")
    return columns, constraints


def snapshot(schema):
    with connect(schema) as conn:
        return {table: conn.execute(sql.SQL("SELECT * FROM {} ORDER BY 1, 2").format(sql.Identifier(table))).fetchall()
                for table in ("users", "questions", "answers", "tags", "question_tags")}


@contextlib.contextmanager
def sql_events(engine):
    statements = []
    def record(conn, cursor, statement, parameters, context, executemany):
        statements.append(statement.lstrip())
    event.listen(engine, "before_cursor_execute", record)
    try:
        yield statements
    finally:
        event.remove(engine, "before_cursor_execute", record)


def payload(title, tags=None):
    return schemas.QuestionCreate(title=title, body="这是符合当前输入规则的教学问题正文。", tags=tags or [])


def structure_queries_loading():
    schema, engine, sessions = fixture()
    orm_schema, _, _ = fixture("models")
    migrated, _, migrated_sessions = fixture("migration")
    check(signature(schema) == signature(orm_schema) == signature(migrated), "第 6 课 DDL、ORM metadata、迁移基线结构一致")
    check(demos.read_one_demo(sessions) == (101, "Python 如何读取问题列表？"), "get 按主键读取 101")
    for author_id, expected in ((1, [101]), (2, [102]), (9, [])):
        with sessions() as session:
            check([q.id for q in queries.questions_by_author(session, author_id)] == expected, f"Q1 对象 author={author_id}")
            rows = queries.question_columns_by_author(session, author_id)
            check([r.id for r in rows] == expected, f"Q1 列投影 author={author_id}")
    with sessions() as session:
        rows = queries.question_columns_by_author(session, 1)
        check([tuple(r) for r in rows] == [(101, "Python 如何读取问题列表？")], "Q1 两列结果行")
    with sessions() as session:
        pairs = queries.question_answer_pairs(session)
        check([(r.question_id, r.answer_id) for r in pairs] == [(101, 201), (101, 202), (101, 203)], "Q2 三行配对")
        counts = queries.question_answer_counts(session)
        check([(r.id, r.answer_count) for r in counts] == [(101, 3), (102, 0)], "Q3 101→3、102→0")
        for page, expected in ((1, [102]), (2, [101]), (3, [])):
            check(queries.question_page_demo(session, page) == (expected, 2), f"Q4 page={page}")
    outputs = []
    for eager, expected in ((False, 3), (True, 2)):
        with sessions() as session, sql_events(engine) as statements:
            result = queries.read_answer_bodies(session, eager=eager)
        check(len(statements) == expected and all(s.upper().startswith("SELECT") for s in statements), f"完整回答读取 eager={eager}：{expected} 条 SELECT")
        check([a["id"] for a in result[0]["answers"]] == [201, 202, 203] and result[1]["answers"] == [], "回答顺序与零回答空集合")
        outputs.append(result)
    check(outputs[0] == outputs[1], "lazy 与 selectinload 输出相同")
    for source, factory in (("DDL", sessions), ("迁移", migrated_sessions)):
        for keyword, expected in (("", [102, 101]), ("  PYTHON  ", [101]), ("%", []), ("_", [])):
            with factory() as session:
                result = service.list_questions_orm(session, keyword=keyword)
            check([q.id for q in result.items] == expected and result.total == len(expected), f"{source} 字面搜索 {keyword!r}")
        with factory() as session:
            for page, expected in ((1, [102]), (2, [101]), (3, [])):
                result = service.list_questions_orm(session, page=page, page_size=1)
                check([q.id for q in result.items] == expected and result.total == 2 and result.page == page, f"{source} 列表 page={page}")
            dto = service.get_question_service(session, 101)
            check(dto.tags == ["python", "sql"] and set(dto.model_dump()) == {"id", "title", "body", "tags", "created_at"}, f"{source} 详情五字段与标签顺序")
            for qid in (0, -1, 999):
                try:
                    service.get_question_service(session, qid)
                except schemas.QuestionNotFound:
                    check(True, f"{source} 缺失 {qid} 为业务异常")
                else:
                    raise AssertionError("缺失详情必须抛业务异常")
    with migrated_sessions() as session:
        created = service.create_question_service(session, payload("迁移后正常创建的教学问题", ["python", "sql"]), author_id=1)
    with migrated_sessions() as session:
        check(service.get_question_service(session, created.id) == created, "迁移后创建并在新 Session 回读")
    for page, expected in ((1, 3), (3, 2)):
        with sessions() as session, sql_events(engine) as statements:
            service.list_questions_orm(session, page=page, page_size=1)
        check(len(statements) == expected, f"公开列表 page={page}：{expected} 条 SELECT")


def lifecycle():
    schema, engine, sessions = fixture()
    output = io.StringIO()
    with sql_events(engine) as statements, contextlib.redirect_stdout(output):
        qid = demos.create_one_demo(sessions)
    lines = output.getvalue().splitlines()
    check(qid == 103 and lines[0] == "构造后 None" and lines[1] == "add 后 None" and lines[2].startswith("flush 后 103 "), "构造／add／flush 时 id 的变化")
    check(len(statements) == 1 and statements[0].startswith("INSERT") and "RETURNING" in statements[0], "一次 INSERT … RETURNING 取得生成值")
    with connect(schema) as conn:
        check(conn.execute("SELECT title FROM questions WHERE id = %s", (qid,)).fetchone()["title"] == "ORM 如何保存一条问题？", "提交后独立连接回读")
    with sql_events(engine) as statements:
        result = demos.update_one_demo(sessions, qid)
    check([s.split()[0] for s in statements] == ["SELECT", "UPDATE"], "新 Session：SELECT 后 UPDATE")
    with connect(schema) as conn:
        check(conn.execute("SELECT body FROM questions WHERE id = %s", (qid,)).fetchone()["body"] == result[1], "修改提交后独立回读")
    before = snapshot(schema)
    with sql_events(engine) as statements:
        try:
            demos.rollback_demo(sessions)
        except RuntimeError as exc:
            check(str(exc) == "提交前教学异常", "提交前教学异常")
        else:
            raise AssertionError("应出现教学异常")
    check(any(s.startswith("INSERT") for s in statements) and snapshot(schema) == before, "INSERT 已执行，rollback 后无残留")
    with sessions() as session, sql_events(engine) as statements:
        check(session.get(Question, 101) is session.get(Question, 101) and len(statements) == 1, "同 Session 主键身份复用")
    with sessions() as a, connect(schema) as b:
        p = payload("自动刷新与独立连接可见性")
        question = Question(title=p.title, body=p.body, author_id=1)
        a.add(question)
        check(b.execute("SELECT id FROM questions WHERE title = %s", (p.title,)).fetchone() is None, "只有 add：独立连接无新行")
        a.expunge(question)
        with sql_events(engine) as statements:
            question, found = demos.add_and_query_probe(a, p, author_id=1)
        check(question is found and [s.split()[0] for s in statements] == ["INSERT", "SELECT"], "autoflush：查询前先 INSERT")
        check(b.execute("SELECT id FROM questions WHERE title = %s", (p.title,)).fetchone() is None, "独立连接看不到未提交行")
        a.commit()
        check(b.execute("SELECT id FROM questions WHERE title = %s", (p.title,)).fetchone()["id"] == question.id, "commit 后独立连接下一条查询可见")
    with sessions() as session:
        session.add(Question(title="关闭前未提交的教学问题", body=p.body, author_id=1))
        session.flush()
    with connect(schema) as conn:
        check(conn.execute("SELECT id FROM questions WHERE title = %s", ("关闭前未提交的教学问题",)).fetchone() is None, "关闭 Session 不自动提交")
    for loaded in (False, True):
        before = snapshot(schema)
        with sessions() as session:
            question = session.get(Question, 101)
            if loaded:
                list(question.answers), list(question.tag_links)
            session.delete(question)
            try:
                session.flush()
            except sa.exc.IntegrityError as exc:
                check(exc.orig.sqlstate == "23503", f"删除仍被引用的问题由外键拒绝 loaded={loaded}")
                session.rollback()
            else:
                raise AssertionError("父记录不应被 ORM 级联处理")
        check(snapshot(schema) == before, "删除失败后数据不变")


def services():
    schema, _, sessions = fixture()
    with sessions() as session:
        result = service.create_question_service(session, payload("完整服务新问题的标题", ["python", "新标签"]), author_id=1)
    with sessions() as session:
        check(service.get_question_service(session, result.id) == result and result.tags == ["python", "新标签"], "创建提交问题与有序标签")
    before = snapshot(schema)
    with sessions() as session:
        try:
            service.create_question_service(session, payload(result.title), author_id=1)
        except schemas.DuplicateTitle:
            check(True, "已知标题冲突翻译为 DuplicateTitle")
        else:
            raise AssertionError("应拒绝重复标题")
    check(snapshot(schema) == before, "标题冲突回滚无残留")
    with sessions() as session:
        try:
            service.create_question_service(session, payload("不存在作者的教学问题"), author_id=999)
        except sa.exc.IntegrityError as exc:
            check(exc.orig.sqlstate == "23503", "外键错误不误报为标题冲突")
        else:
            raise AssertionError("应拒绝不存在的作者")
    before = snapshot(schema)
    original = service.question_to_dto
    service.question_to_dto = lambda q: schemas.QuestionOut(id="不是整数", title=q.title, body=q.body, tags=[], created_at=q.created_at)
    try:
        with sessions() as session:
            try:
                service.create_question_service(session, payload("输出校验失败的教学问题", ["应当回滚的新标签"]), author_id=1)
            except pydantic.ValidationError:
                check(True, "DTO 校验失败发生在提交之前")
            else:
                raise AssertionError("应出现输出校验失败")
    finally:
        service.question_to_dto = original
    check(snapshot(schema) == before, "DTO 失败回滚问题、新标签与关联")
    # 只登记候选差异，不当作现行 M1 契约通过。
    with sessions() as session:
        result = service.create_question_service(session, payload("重复标签迁移候选行为", ["a", "a", "", " b"]), author_id=1)
    check(result.tags == ["a", "", " b"], "候选写入确有标签去重差异")


async def api_wiring():
    _, _, sessions = fixture()
    api.SessionLocal = sessions
    app = fastapi.FastAPI()
    app.include_router(api.router)

    @app.exception_handler(schemas.AppError)
    async def business_error(request, exc):
        status, code, message = schemas.BUSINESS_HTTP[type(exc)]
        return fastapi.responses.JSONResponse(status_code=status, content={"code": code, "message": message})

    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/questions", params={"page_size": 1})
        check(response.status_code == 200 and response.json()["items"][0]["id"] == 102 and response.json()["total"] == 2, "临时 ASGI 列表")
        check((await client.get("/questions/101")).json()["tags"] == ["python", "sql"], "临时 ASGI 详情")
        for url in ("/questions/0", "/questions/-1", "/questions/999"):
            check((await client.get(url)).status_code == 404, f"临时 ASGI {url} 404")
        for url in ("/questions/not-an-int", "/questions?page=0", "/questions?page_size=51"):
            check((await client.get(url)).status_code == 422, f"临时 ASGI {url} 422")
        body = payload("ASGI 创建并回读的教学问题", ["python", "sql"]).model_dump()
        response = await client.post("/questions", json=body)
        check(response.status_code == 201, "临时 ASGI 创建 201")
        readback = await client.get(response.headers["Location"])
        check(readback.status_code == 200 and readback.json() == response.json(), "Location 回读一致")
        check((await client.post("/questions", json=body)).status_code == 409, "临时 ASGI 标题冲突 409")
        check((await client.post("/questions", json={**body, "title": "带作者字段的教学问题", "author_id": 1})).status_code == 422, "不接受客户端作者字段")


def main():
    # 使用 libpq 标准连接环境变量；连接参数和认证信息不打印、不写入源码。
    with psycopg.connect("", connect_timeout=5) as conn:
        assert conn.info.server_version >= 160000, "需要 PostgreSQL 16+"
        assert conn.execute("SHOW server_encoding").fetchone()[0] == "UTF8"
    try:
        structure_queries_loading()
        lifecycle()
        services()
        asyncio.run(api_wiring())
    finally:
        for engine in ENGINES:
            engine.dispose()
        with psycopg.connect("", autocommit=True, connect_timeout=5) as admin:
            for schema in CREATED:
                admin.execute(sql.SQL("DROP SCHEMA {} CASCADE").format(sql.Identifier(schema)))
    print(f"完成：{len(PASSED)} 项检查通过；本脚本创建的 {len(CREATED)} 个 schema 已删除")


if __name__ == "__main__":
    main()
