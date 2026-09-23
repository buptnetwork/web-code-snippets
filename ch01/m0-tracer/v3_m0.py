"""M0 作业参考答案，课后发布；不导入公共课件。

有意保留单文件与 SQL 拼接欠账。不是生产模板；只用于隔离虚构数据。
"""
import logging
import os
import re
import time
import uuid
from pathlib import Path as FilePath

from fastapi import FastAPI, Path, Request
from fastapi.responses import FileResponse, JSONResponse
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
    handlers=[logging.StreamHandler(), logging.FileHandler(
        os.getenv("LOG_FILE", "server.log"), mode="w", encoding="utf-8")],
    force=True,
)
logger = logging.getLogger("app")
app = FastAPI(title="M0 · v3 作业参考（课后）")
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./demo.db")
engine = create_engine(DATABASE_URL, echo=os.getenv("SQL_ECHO", "0") == "1")


@app.middleware("http")
async def trace_middleware(request: Request, call_next):
    supplied = request.headers.get("X-Request-ID", "")
    rid = supplied if re.fullmatch(r"[A-Za-z0-9._-]{1,64}", supplied) else uuid.uuid4().hex
    request.state.request_id = rid
    start = time.perf_counter()
    logger.info("[%s] --> %s %s", rid, request.method, request.url.path)
    response = await call_next(request)
    cost = (time.perf_counter() - start) * 1000
    logger.info("[%s] <-- %s %.1fms", rid, response.status_code, cost)
    response.headers["X-Request-ID"] = rid
    return response


@app.get("/questions")
def get_questions(request: Request, keyword: str = "", page: int = 1):
    rid = request.state.request_id
    logger.info("[%s] sql:begin search", rid)
    with engine.connect() as conn:
        rows = conn.execute(text(
            f"SELECT * FROM questions WHERE title LIKE '%{keyword}%' "
            f"LIMIT 20 OFFSET {(page - 1) * 20}"
        )).fetchall()
    logger.info("[%s] sql:done rows=%d", rid, len(rows))
    return {"success": True, "data": [dict(row._mapping) for row in rows]}


@app.get("/questions/{qid}")
def get_question(request: Request, qid: int = Path(ge=1)):
    rid = request.state.request_id
    logger.info("[%s] sql:begin detail", rid)
    with engine.connect() as conn:
        row = conn.execute(text(
            f"SELECT id, title, body, created_at FROM questions WHERE id = {qid}"
        )).fetchone()
    logger.info("[%s] sql:done found=%s", rid, row is not None)
    if row is None:
        return JSONResponse(status_code=404, content={
            "code": "question_not_found", "message": "问题不存在", "request_id": rid,
        })
    return dict(row._mapping)


@app.get("/healthz")
def healthz(request: Request):
    rid = request.state.request_id
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
    except SQLAlchemyError:
        logger.warning("[%s] health db=down", rid)
        return JSONResponse(status_code=503, content={"status": "degraded", "db": "down"})
    return {"status": "ok", "db": "ok"}


@app.get("/boom")
def boom():
    raise RuntimeError("已知缺陷：未捕获异常没有离开日志和 X-Request-ID")


@app.get("/", include_in_schema=False)
def index():
    return FileResponse(FilePath(__file__).parent / "static" / "index.html")
