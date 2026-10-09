"""第 4 课 R 阶段服务（你的工作文件）：连接收进 yield 依赖，服务负责事务，端点只表达 HTTP 契约。

理解边界（对应底稿〇「教师提供与学生负责」）：
- `get_conn` 依赖、服务层显式提交与异常传播为「教师提供 / 要求解释」；
- 三个端点的接线、故障实验、E 阶段错误与观测升级为「学生负责」。

R 阶段只重构资源与职责，保持第 3 课已验收契约不变：状态码、`QuestionOut`／`QuestionListOut`、
验证错误、404／409 的 `{"detail": ...}` 正文都不改。E 阶段（reference/server.py）才把错误
正文迁移为四字段 ErrorOut，并加 request-id 中间件与升级 healthz。

启动（包根，已激活本包环境）：
    python -m uvicorn server:app --host 127.0.0.1 --port 8000
改完代码先停止再重启（不要用 --reload）。
"""

# region imports
import sqlite3
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, HTTPException, Query, Response
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from models import (
    DuplicateTitle,
    QuestionCreate,
    QuestionListOut,
    QuestionOut,
)
from question_db import DB_PATH, find_question, init_db, reset_db, search_questions
from service import create_question_service
from service_fault import create_with_fault

ROOT = Path(__file__).resolve().parent
STATIC_DIR = ROOT / "static"
# endregion imports


# region app
@asynccontextmanager
async def lifespan(_: FastAPI):
    # 启动即确保数据库已建表、升级并播种（幂等）。
    init_db()
    yield


app = FastAPI(lifespan=lifespan)
# endregion app


# region get-conn
from typing import Annotated, Iterator

from fastapi import Depends


def get_conn() -> Iterator[sqlite3.Connection]:
    # 镜像 open_connection 的三项设置，另加 check_same_thread=False：连接在依赖里获取，
    # 却可能在另一个线程（线程池执行端点、依赖退出）被使用或关闭。
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.isolation_level = "DEFERRED"
    try:
        yield conn
    finally:
        conn.close()


ConnDep = Annotated[sqlite3.Connection, Depends(get_conn)]
# endregion get-conn


# region list-endpoint
@app.get("/questions", response_model=QuestionListOut)
def list_questions(
    conn: ConnDep,
    keyword: str = Query(""),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=50),
):
    return search_questions(conn, keyword, page, page_size)
# endregion list-endpoint


# region write-endpoints
@app.post("/questions", status_code=201, response_model=QuestionOut,
          responses={409: {"description": "标题已存在"}})
def create_question(payload: QuestionCreate, response: Response, conn: ConnDep):
    try:
        result = create_question_service(conn, payload)
    except DuplicateTitle as exc:
        raise HTTPException(status_code=409, detail="标题已存在") from exc
    response.headers["Location"] = f"/questions/{result.id}"
    return result


@app.get("/questions/{qid}", response_model=QuestionOut,
         responses={404: {"description": "问题不存在"}})
def get_question(qid: int, conn: ConnDep):
    result = find_question(conn, qid)
    if result is None:
        raise HTTPException(status_code=404, detail="问题不存在")
    return result
# endregion write-endpoints


# region fault-endpoint
@app.post("/__teacher/fault-create", status_code=201, response_model=QuestionOut)
def fault_create(payload: QuestionCreate, conn: ConnDep, fault: str = Query("normal")):
    """教师故障实验端点：用隔离副本注入 before_commit／after_commit，观察数据去留。黑盒，学生不实现。"""
    return create_with_fault(conn, payload, fault)
# endregion fault-endpoint


# region health
@app.get("/healthz")
def healthz():
    """R 阶段存活探针保持第 3 课形态：200 + {"status":"ok"}，不访问数据库。"""
    return {"status": "ok"}
# endregion health


# region teacher-reset
@app.post("/__teacher/reset")
def reset():
    """教师端点：把数据库复位为固定三条，供自检重复运行。黑盒，学生不实现、不修改。"""
    reset_db()
    return {"status": "reset", "count": 3}
# endregion teacher-reset


# region page
@app.get("/")
def index():
    """同源页面入口：返回静态 index.html（第 2 课四态搜索页，本课用于回归）。"""
    return FileResponse(STATIC_DIR / "index.html")
# endregion page


# region mounts
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
# endregion mounts
