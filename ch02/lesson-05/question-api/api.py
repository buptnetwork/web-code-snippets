"""第 5 课 JSON 基线：第 4 课 E 阶段完整应用工厂（提供 make_application 与 ConnDep）。

第 5 课的 SSR 表现层（ssr.py）在此之上装配 HTML 路由与错误适配，不复制这里的 JSON 契约：
- register_handlers 四类处理器统一出口，错误正文为四字段 ErrorOut；
- register_trace 中间件生成／透传 request-id，并记录 request_start／request_end 结构化日志；
- healthz 真实探针：数据库可用 ok、不可用 degraded + 503；
- make_application 装配：处理器 → trace → 路由 → 静态挂载。

本文件保留 `app = make_application()`，可单独启动做 JSON 回归（不挂 HTML 路由）：
    python -m uvicorn api:app --host 127.0.0.1 --port 8000
SSR 主入口是 ssr.py（学生工作文件）或 reference/ssr.py（完整参考）。
"""

# region imports
import json
import logging
import re
import sqlite3
import time
import uuid
from contextlib import closing
from pathlib import Path
from typing import Annotated, Iterator, Literal

from fastapi import Depends, FastAPI, Query, Request, Response
from fastapi.exceptions import RequestValidationError
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from starlette.exceptions import HTTPException as StarletteHTTPException

from models import (
    BUSINESS_HTTP,
    AppError,
    ErrorOut,
    QuestionCreate,
    QuestionListOut,
    QuestionOut,
)
from question_db import DB_PATH, init_db, open_connection, reset_db, search_questions
from service import create_question_service, get_question_service
from service_fault import create_with_fault

logger = logging.getLogger("question_api")

# OpenAPI 文档声明：所有响应都带 X-Request-ID 头，普通 JSON 错误统一为四字段 ErrorOut。
REQUEST_ID_HEADER = {"schema": {"type": "string"}, "description": "关联本次请求的 id，可由客户端提供或框架生成"}
API_ERROR_RESPONSES = {status: {"model": ErrorOut} for status in (404, 405, 409, 422, 500)}

ROOT = Path(__file__).resolve().parent
STATIC_DIR = ROOT / "static"
# endregion imports


# region logging
def configure_logging() -> None:
    # 课堂观察：把结构化日志原样打到 stderr（format 只保留消息本身），便于核对 start/end 配对。
    if logger.handlers:
        return
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter("%(message)s"))
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)
    logger.propagate = False
# endregion logging


# region get-conn
def get_conn() -> Iterator[sqlite3.Connection]:
    # 与 R 阶段同一连接工厂：镜像 open_connection 的三项设置，另加 check_same_thread=False。
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.isolation_level = "DEFERRED"
    try:
        yield conn
    finally:
        conn.close()


ConnDep = Annotated[sqlite3.Connection, Depends(get_conn)]
# endregion get-conn


# region error-response
def error_response(request, status, code, message, detail=None, headers=None):
    rid = getattr(request.state, "request_id", "-")
    body = ErrorOut(code=code, message=message, detail=detail, request_id=rid)
    response = JSONResponse(status_code=status, content=body.model_dump(mode="json"),
                            headers=headers)
    response.headers["X-Request-ID"] = rid
    return response
# endregion error-response


# region register-handlers
def register_handlers(app):
    @app.exception_handler(Exception)
    async def unexpected(request: Request, exc: Exception):
        # 只记录异常类型，不把可能含请求正文的异常字符串投影给客户端。
        logger.error(json.dumps({"event": "unhandled_error", "type": type(exc).__name__,
                                 "request_id": getattr(request.state, "request_id", "-")},
                                ensure_ascii=False))
        return error_response(request, 500, "internal_error", "服务暂时不可用")

    @app.exception_handler(AppError)
    async def business(request: Request, exc: AppError):
        mapping = BUSINESS_HTTP.get(type(exc))
        if mapping is None:
            return await unexpected(request, exc)
        status, code, message = mapping
        return error_response(request, status, code, message)

    @app.exception_handler(RequestValidationError)
    async def validation(request: Request, exc: RequestValidationError):
        details = [{"loc": list(error["loc"]), "type": error["type"],
                    "msg": "该字段不符合接口约束"} for error in exc.errors()]
        return error_response(request, 422, "validation_error", "请求参数不合法", details)

    @app.exception_handler(StarletteHTTPException)
    async def framework_http(request: Request, exc: StarletteHTTPException):
        # 覆盖框架未知路径 404 与方法不符 405；保留 Allow 等必要响应头。
        return error_response(request, exc.status_code, f"http_{exc.status_code}",
                              str(exc.detail), headers=getattr(exc, "headers", None))
# endregion register-handlers


# region register-trace
def register_trace(app):
    @app.middleware("http")
    async def trace(request: Request, call_next):
        supplied = request.headers.get("X-Request-ID", "")
        rid = supplied if re.fullmatch(r"[A-Za-z0-9._-]{1,64}", supplied) else uuid.uuid4().hex
        request.state.request_id = rid
        started = time.perf_counter()
        outcome = "error"
        logger.info(json.dumps({"event": "request_start", "request_id": rid,
                                "method": request.method}, ensure_ascii=False))
        try:
            response = await call_next(request)
            outcome = response.status_code
            response.headers["X-Request-ID"] = rid
            return response
        finally:
            logger.info(json.dumps({
                "event": "request_end", "request_id": rid, "outcome": outcome,
                "duration_ms": round((time.perf_counter() - started) * 1000, 1),
            }, ensure_ascii=False))
# endregion register-trace


# region endpoints
def list_questions(
    conn: ConnDep,
    keyword: str = Query(""),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=50),
):
    return search_questions(conn, keyword, page, page_size)
# endregion endpoints


# region e-write-endpoints
def create_question(payload: QuestionCreate, response: Response, conn: ConnDep):
    result = create_question_service(conn, payload)
    response.headers["Location"] = f"/questions/{result.id}"
    return result


def get_question(qid: int, conn: ConnDep):
    return get_question_service(conn, qid)
# endregion e-write-endpoints


# region fault-endpoint
def fault_create(payload: QuestionCreate, conn: ConnDep, fault: str = Query("normal")):
    return create_with_fault(conn, payload, fault)
# endregion fault-endpoint


# region healthz
class HealthOut(BaseModel):
    status: Literal["ok", "degraded"]


def healthz():
    try:
        with closing(open_connection()) as conn:
            conn.execute("SELECT 1").fetchone()
    except sqlite3.Error:
        body = HealthOut(status="degraded")
        return JSONResponse(status_code=503, content=body.model_dump())
    return HealthOut(status="ok")
# endregion healthz


# region teacher
def reset():
    reset_db()
    return {"status": "reset", "count": 3}


def index():
    return FileResponse(STATIC_DIR / "index.html")
# endregion teacher


# region make-application
def make_application() -> FastAPI:
    configure_logging()
    init_db()
    application = FastAPI(debug=False)
    register_handlers(application)
    register_trace(application)
    ok = {200: {"headers": {"X-Request-ID": REQUEST_ID_HEADER}}}
    application.add_api_route(
        "/questions", list_questions, methods=["GET"],
        response_model=QuestionListOut, responses={**ok, **API_ERROR_RESPONSES})
    application.add_api_route(
        "/questions/{qid}", get_question, methods=["GET"],
        response_model=QuestionOut, responses={**ok, **API_ERROR_RESPONSES})
    application.add_api_route(
        "/questions", create_question, methods=["POST"], status_code=201,
        response_model=QuestionOut,
        responses={201: {"headers": {"X-Request-ID": REQUEST_ID_HEADER, "Location": {"schema": {"type": "string"}}}},
                   **API_ERROR_RESPONSES})
    application.add_api_route(
        "/healthz", healthz, methods=["GET"], response_model=HealthOut,
        responses={503: {"description": "数据库不可用", "model": HealthOut}})
    application.add_api_route("/__teacher/reset", reset, methods=["POST"])
    application.add_api_route("/__teacher/fault-create", fault_create, methods=["POST"],
                              status_code=201, response_model=QuestionOut)
    application.add_api_route("/", index, methods=["GET"])
    application.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
    return application
# endregion make-application


app = make_application()
