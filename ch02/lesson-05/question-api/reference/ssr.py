"""第 5 课 SSR 完整参考（课后对照，不作为学生练习起点）。

在学生工作文件 ssr.py 之上给出 task 的完整答案：render_validation_failure 按 loc 第一项
放置固定安全文案、setdefault 不互相覆盖、返回 422 且原 values 不变。其余分段（模板入口、
Form 适配、创建端点、读取路由、HTML 错误适配、应用装配）与 ssr.py 逐字一致。

TEMPLATE_DIR 相对本文件定位到 reference/templates（含四个完整模板，列表／详情为参考答案）。

运行对照（包根，已激活本包环境）：
    python -m uvicorn reference.ssr:app --host 127.0.0.1 --port 8000
"""

# region baseline-imports
from api import ConnDep, make_application
from models import BUSINESS_HTTP, AppError, DuplicateTitle, QuestionCreate, QuestionListOut
from question_db import search_questions
from service import create_question_service, get_question_service
# endregion baseline-imports


# region templates-entry
from pathlib import Path

from fastapi import APIRouter, Depends, Form, Query, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from pydantic import ValidationError
from typing import Annotated

TEMPLATE_DIR = Path(__file__).resolve().parent / "templates"
templates = Jinja2Templates(directory=str(TEMPLATE_DIR))
ui = APIRouter(prefix="/ui", include_in_schema=False)


def render_form(request, values, errors, status_code=200):
    return templates.TemplateResponse(
        request=request, name="question_form.html",
        context={"values": values, "errors": errors}, status_code=status_code,
    )


@ui.get("/questions/new", response_class=HTMLResponse)
def new_question_page(request: Request):
    return render_form(request, {"title": "", "body": "", "tags": ""}, {})
# endregion templates-entry


# region read-form
async def read_question_form(
    request: Request,
    title: str = Form(""),
    body: str = Form(""),
    tags: str = Form(""),
):
    raw = await request.form()
    values = {"title": title, "body": body, "tags": tags}
    errors = {}
    if any(name not in values for name in raw):
        errors["form"] = "表单只接受标题、正文和标签字段。"
    elif any(len(raw.getlist(name)) > 1 for name in values):
        errors["form"] = "同一字段不能重复提交。"
    request.state.form_values = values
    return values, errors


FormDep = Annotated[tuple, Depends(read_question_form)]
# endregion read-form


# region submit-endpoint
@ui.post("/questions", response_class=HTMLResponse)
def submit_question_page(request: Request, form: FormDep, conn: ConnDep):
    values, errors = form
    if errors:
        return render_form(request, values, errors, 422)
    incoming = {
        "title": values["title"], "body": values["body"],
        "tags": values["tags"].split(",") if values["tags"] else [],
    }
    try:
        payload = QuestionCreate.model_validate(incoming)
    except ValidationError as exc:
        return render_validation_failure(request, values, exc)
    question = create_question_service(conn, payload)
    return RedirectResponse(f"/ui/questions/{question.id}", status_code=303)
# endregion submit-endpoint


# region validation-failure
FIELD_MESSAGES = {
    "title": "标题去除首尾空白后须为 5–200 个字符。",
    "body": "正文去除首尾空白后须为 10–20000 个字符。",
    "tags": "标签须为字符串列表，最多 5 项。",
}


def render_validation_failure(request, values, exc):
    errors = {}
    for error in exc.errors():
        field = error["loc"][0] if error["loc"] else "form"
        if field in FIELD_MESSAGES:
            errors.setdefault(field, FIELD_MESSAGES[field])
        else:
            errors.setdefault("form", "表单内容不符合接口约束。")
    return render_form(request, values, errors, 422)
# endregion validation-failure


# region read-routes
@ui.get("/questions", response_class=HTMLResponse)
def question_list_page(
    request: Request, conn: ConnDep,
    keyword: str = Query(""), page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=50),
):
    result = QuestionListOut.model_validate(
        search_questions(conn, keyword, page, page_size)
    )
    return templates.TemplateResponse(
        request=request, name="question_list.html",
        context={"result": result, "keyword": keyword, "page_size": page_size},
    )


@ui.get("/questions/{qid}", response_class=HTMLResponse)
def question_detail_page(request: Request, qid: int, conn: ConnDep):
    question = get_question_service(conn, qid)
    return templates.TemplateResponse(
        request=request, name="question_detail.html", context={"q": question},
    )
# endregion read-routes


# region html-error
from html import escape

from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException


def is_html_request(request):
    path = request.url.path
    return path == "/ui" or path.startswith("/ui/")


def html_error(request, status, message, headers=None):
    rid = getattr(request.state, "request_id", "-")
    response = HTMLResponse(
        "<!doctype html><html lang=\"zh-CN\"><meta charset=\"utf-8\">"
        f"<title>请求未完成</title><h1>{escape(message)}</h1>"
        f"<p>请求编号：{escape(rid)}</p>"
        '<a href="/ui/questions">返回问题列表</a></html>',
        status_code=status, headers=headers,
    )
    response.headers["X-Request-ID"] = rid
    return response


def register_html_handlers(application):
    json_business = application.exception_handlers[AppError]
    json_validation = application.exception_handlers[RequestValidationError]
    json_http = application.exception_handlers[StarletteHTTPException]
    json_unexpected = application.exception_handlers[Exception]

    @application.exception_handler(AppError)
    async def business(request: Request, exc: AppError):
        if not is_html_request(request):
            return await json_business(request, exc)
        mapping = BUSINESS_HTTP.get(type(exc))
        if mapping is None:
            return await unexpected(request, exc)
        status, code, message = mapping
        values = getattr(request.state, "form_values", None)
        if type(exc) is DuplicateTitle and request.method == "POST" and values is not None:
            return render_form(request, values, {"title": message}, 409)
        return html_error(request, status, message)

    @application.exception_handler(RequestValidationError)
    async def validation(request: Request, exc: RequestValidationError):
        if not is_html_request(request):
            return await json_validation(request, exc)
        return html_error(request, 422, "请求参数不合法")

    @application.exception_handler(StarletteHTTPException)
    async def http_error(request: Request, exc: StarletteHTTPException):
        if not is_html_request(request):
            return await json_http(request, exc)
        messages = {404: "路径不存在", 405: "该路径不支持此方法"}
        return html_error(request, exc.status_code,
                          messages.get(exc.status_code, "HTTP 请求失败"), headers=exc.headers)

    @application.exception_handler(Exception)
    async def unexpected(request: Request, exc: Exception):
        response = await json_unexpected(request, exc)
        if not is_html_request(request):
            return response
        return html_error(request, 500, "服务器内部错误")
# endregion html-error


# region make-ssr
def make_ssr_application():
    application = make_application()
    register_html_handlers(application)
    application.include_router(ui)
    return application
# endregion make-ssr


app = make_ssr_application()
