"""课堂目标：单文件 + 四处观察。TRACE_MODE=plain 只显示朴素日志。

仅本地实验；故意保留 SQL 拼接及 /boom 的异常路径缺陷。
DEMO_DELAY_MS 是人为教学延迟，不是数据库性能。
"""
import logging
import os
import re
import time
import uuid
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import FileResponse
from sqlalchemy import create_engine, text

# region logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
    handlers=[logging.StreamHandler(), logging.FileHandler(
        os.getenv("LOG_FILE", "server.log"), mode="w", encoding="utf-8")],
    force=True,
)
logger = logging.getLogger("app")
# endregion logging

app = FastAPI(title="M0 · v2 四处观察")
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./demo.db")
TRACE_MODE = os.getenv("TRACE_MODE", "trace")
DEMO_DELAY_MS = min(200, max(0, int(os.getenv("DEMO_DELAY_MS", "0"))))
# region engine
engine = create_engine(DATABASE_URL, echo=os.getenv("SQL_ECHO", "0") == "1")
# endregion engine

# region middleware
# region identity
@app.middleware("http")
async def trace_middleware(request: Request, call_next):
    supplied = request.headers.get("X-Request-ID", "")
    # 受控实验也限制长度与字符，避免换行等输入污染日志。
    rid = (supplied if re.fullmatch(r"[A-Za-z0-9._-]{1,64}", supplied)
           else uuid.uuid4().hex)
    request.state.request_id = rid
    start = time.perf_counter()
    if TRACE_MODE == "trace":
        logger.info("[%s] --> %s %s", rid, request.method, request.url.path)
# endregion identity
# region return_path
    response = await call_next(request)
    cost = (time.perf_counter() - start) * 1000
    if TRACE_MODE == "trace":
        logger.info("[%s] <-- %s %.1fms", rid, response.status_code, cost)
        response.headers["X-Request-ID"] = rid
    return response
# endregion return_path
# endregion middleware


def record(rid: str, message: str, *args):
    if TRACE_MODE == "trace":
        logger.info("[%s] " + message, rid, *args)
    else:
        logger.info(message, *args)


# region search
@app.post("/getQuestions")
def get_questions(request: Request, keyword: str = "", page: int = 1):
    rid = request.state.request_id
    record(rid, "query keyword=%s page=%s", keyword, page)
    if DEMO_DELAY_MS:
        time.sleep(DEMO_DELAY_MS / 1000)  # 人为延迟，仅用于交织演示
    with engine.connect() as conn:
        record(rid, "sql:begin search")
        rows = conn.execute(text(
            f"SELECT * FROM questions WHERE title LIKE '%{keyword}%' "
            f"LIMIT 20 OFFSET {(page - 1) * 20}"
        )).fetchall()  # 在 conn.execute 这一行设置断点
        record(rid, "sql:done rows=%d", len(rows))
    record(rid, "assemble rows=%d", len(rows))
    return {"success": True, "data": [dict(r._mapping) for r in rows]}
# endregion search


@app.post("/getQuestionDetail")
def get_question_detail(request: Request, qid: int):
    rid = request.state.request_id
    record(rid, "sql:begin detail")
    with engine.connect() as conn:
        row = conn.execute(text(f"SELECT * FROM questions WHERE id = {qid}")).fetchone()
    record(rid, "sql:done found=%s", row is not None)
    if row is None:
        return {"success": False, "message": "not found"}
    return {"success": True, "data": dict(row._mapping)}


# region boom
@app.get("/boom")
def boom():
    raise RuntimeError("故意触发：观察中间件没有执行后半段")
# endregion boom


@app.get("/", include_in_schema=False)
def index():
    return FileResponse(Path(__file__).parent / "static" / "index.html")
