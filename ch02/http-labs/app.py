"""第 3—5 课隔离教学实验（教师完整正例 · 权威源）。

四组实验共存在一个轻量 FastAPI 应用里，全部挂在 `/lab` 前缀下，彼此不共享状态：

- 组 1 · 参数来源与普通依赖（第 3、4 课）：固定/动态路径顺序、Path 约束、Header 显式 alias，
  以及两个内存列表接口共享同一个普通分页依赖（`return` 一个准备好的分页对象，不用 yield）。
- 组 2 · 嵌套输入（第 3 课）：`POST /lab/reading-lists/preview`，错误定位 `body → items → 1 → title`。
- 组 3 · 文件检查（第 5 课）：`POST /lab/uploads/inspect`，1 MiB 上限、限量读取、实际字节计数、最终关闭。
- 组 4 · 偏好 Cookie（第 5 课）：`GET/POST /lab/preferences` 与 `POST /lab/preferences/reset`。

边界（对应修改建议 5.3）：不导入主线数据库与 Question 服务，不自动注册到 M1 应用；隔离实验使用
默认 FastAPI 错误，不复制第 4 课的四字段错误/日志框架；课件用 region 引入本文件片段，本文件为权威。

启动（包根，已激活本包环境）：
    python -m uvicorn app:app --host 127.0.0.1 --port 8123
自检（另开一个终端、同一环境、在本目录）：
    python check_labs.py --base-url http://127.0.0.1:8123
"""

# region lab-setup
from dataclasses import dataclass
from pathlib import Path
from typing import Annotated, Literal

from fastapi import (
    Depends,
    FastAPI,
    File,
    Form,
    Header,
    HTTPException,
    Path as PathParam,
    Query,
    Request,
    UploadFile,
)
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, ConfigDict, Field

ROOT = Path(__file__).resolve().parent
app = FastAPI(title="HTTP 隔离实验", docs_url="/docs", openapi_url="/openapi.json")
templates = Jinja2Templates(directory=str(ROOT / "templates"))
# endregion lab-setup


# region lab-index
@app.get("/", response_class=HTMLResponse)
def index(request: Request):
    """实验导航页：四组实验都是隔离只读/临时写入，不接主线数据库。"""
    return templates.TemplateResponse(request=request, name="index.html", context={})
# endregion lab-index


# ───────────────────────── 组 1 · 参数来源与普通依赖 ─────────────────────────

# 内存数据：没有数据库、没有仓储层，只为演示参数来源与普通分页依赖。
ITEMS = [
    {"id": 1, "name": "笔记本", "qty": 3},
    {"id": 2, "name": "钢笔", "qty": 7},
    {"id": 3, "name": "书签", "qty": 12},
]
BOOKS = [
    {"id": 1, "title": "HTTP 权威指南"},
    {"id": 2, "title": "流畅的 Python"},
    {"id": 3, "title": "Web 全栈开发"},
    {"id": 4, "title": "数据库系统概念"},
]


# region items-fixed
@app.get("/lab/items/latest")
def latest_item():
    """固定路径必须先注册：它比 `/lab/items/{item_id}` 更具体，先声明才不会被动态路径截走。"""
    newest = max(ITEMS, key=lambda row: row["id"])
    return {"item": newest}
# endregion items-fixed


# 一个端点里同时出现 Path 与 Header：路径段进 item_id，请求头进 x_client_name。
# `Path(gt=0)` 只是本实验的约束，用来演示 422；它不会传播到主线 Question 的 qid，
# 主线不存在的整数 id 仍是 404。Header 用非敏感的 X-Client-Name 演示显式 alias。
# region items-by-id
@app.get("/lab/items/{item_id}")
def get_item(
    item_id: Annotated[int, PathParam(gt=0)],
    x_client_name: Annotated[str, Header(alias="X-Client-Name")] = "unknown",
):
    for row in ITEMS:
        if row["id"] == item_id:
            return {"item": row, "served_to": x_client_name}
    raise HTTPException(status_code=404, detail="条目不存在")
# endregion items-by-id


# region page-dep
@dataclass(frozen=True)
class Page:
    """普通依赖要交给端点的“准备好的值”：一个分页参数对象。"""

    page: int
    page_size: int

    @property
    def offset(self) -> int:
        return (self.page - 1) * self.page_size

    def slice(self, rows):
        return rows[self.offset : self.offset + self.page_size]


def get_page(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=50),
) -> Page:
    # 普通依赖：解析请求、return 一个对象即可；没有 yield、没有连接、没有 finally 清理。
    return Page(page=page, page_size=page_size)


PageDep = Annotated[Page, Depends(get_page)]
# endregion page-dep


# region items-list
@app.get("/lab/items")
def list_items(pager: PageDep):
    return {
        "items": pager.slice(ITEMS),
        "page": pager.page,
        "page_size": pager.page_size,
        "total": len(ITEMS),
    }
# endregion items-list


# region books-list
@app.get("/lab/books")
def list_books(pager: PageDep):
    # 第二个接口复用同一个 get_page：约束只写一处，两个端点行为一致。
    return {
        "books": pager.slice(BOOKS),
        "page": pager.page,
        "page_size": pager.page_size,
        "total": len(BOOKS),
    }
# endregion books-list


# ───────────────────────────── 组 2 · 嵌套输入 ─────────────────────────────


# region nested-models
class BookIn(BaseModel):
    model_config = ConfigDict(extra="forbid")
    title: str = Field(min_length=1)


class ReadingListPreview(BaseModel):
    model_config = ConfigDict(extra="forbid")
    name: str = Field(min_length=1, max_length=50)
    items: list[BookIn] = Field(min_length=1)


class ReadingListOut(BaseModel):
    name: str
    count: int
    titles: list[str]
# endregion nested-models


# region nested-endpoint
@app.post("/lab/reading-lists/preview", response_model=ReadingListOut)
def preview_reading_list(payload: ReadingListPreview):
    """外层模型组合书目模型：第二项缺 title 时，错误 loc 是 body → items → 1 → title（索引从 0）。"""
    return ReadingListOut(
        name=payload.name,
        count=len(payload.items),
        titles=[book.title for book in payload.items],
    )
# endregion nested-endpoint


# ───────────────────────────── 组 3 · 文件检查 ─────────────────────────────

MAX_BYTES = 1_048_576  # 1 MiB = 1,048,576 字节（不是 1000×1000）
CHUNK = 64 * 1024


# region upload-page
@app.get("/lab/uploads", response_class=HTMLResponse)
def upload_page(request: Request):
    """同源文件表单：enctype=multipart/form-data，与 JSON 正文不是同一种编码。"""
    return templates.TemplateResponse(request=request, name="upload_form.html", context={})
# endregion upload-page


# 限量读取：边读边计数，超过 1 MiB 立即 413，绝不先无上限读完再判断长度。
# `file` 缺失由 FastAPI 直接 422（必填）；filename/content_type 只是不可信元信息，
# 不据此拼路径、不执行内容、不长期保存、不开放下载。finally 保证临时文件最终关闭。
# region upload-inspect
@app.post("/lab/uploads/inspect")
async def inspect_upload(
    file: Annotated[UploadFile, File()],
    description: Annotated[str, Form()] = "",
):
    seen = 0
    try:
        while True:
            chunk = await file.read(CHUNK)
            if not chunk:
                break
            seen += len(chunk)
            if seen > MAX_BYTES:
                raise HTTPException(status_code=413, detail="文件超过 1 MiB 上限")
    finally:
        await file.close()
    return {
        "received_bytes": seen,
        "at_limit": seen == MAX_BYTES,
        "filename": file.filename,
        "content_type": file.content_type,
        "description": description,
        "stored": False,
    }
# endregion upload-inspect


# ───────────────────────────── 组 4 · 偏好 Cookie ─────────────────────────────


# region cookie-constants
COOKIE_NAME = "course_lab_theme"
COOKIE_PATH = "/lab"  # 携带范围限定在 /lab 下；不设 Domain
ALLOWED_THEMES = ("light", "dark")


class PreferenceForm(BaseModel):
    # 写入用严格枚举：非法 theme → 422；读取端不套这个模型，避免把未知值提前拦掉。
    theme: Literal["light", "dark"]
# endregion cookie-constants


# region cookie-read
@app.get("/lab/preferences", response_class=HTMLResponse)
def read_preferences(request: Request):
    """读取：直接拿原始字符串判断，缺失/未知一律回退 light，不用严格枚举提前拦截。"""
    raw = request.cookies.get(COOKIE_NAME)
    theme = raw if raw in ALLOWED_THEMES else "light"
    return templates.TemplateResponse(
        request=request, name="preferences.html", context={"theme": theme, "raw": raw}
    )
# endregion cookie-read


# region cookie-write
@app.post("/lab/preferences")
async def set_preferences(form: Annotated[PreferenceForm, Form()]):
    """写入：成功显式 303 回 GET；set_cookie 写在这次真正返回的 RedirectResponse 上。"""
    response = RedirectResponse(url="/lab/preferences", status_code=303)
    response.set_cookie(
        key=COOKIE_NAME,
        value=form.theme,
        max_age=3600,
        path=COOKIE_PATH,
        httponly=True,
        secure=False,  # 本地 HTTP；生产 HTTPS 用 secure=True
        samesite="lax",
    )
    return response
# endregion cookie-write


# region cookie-reset
@app.post("/lab/preferences/reset")
def reset_preferences():
    """删除：同名、同 Path、同属性范围；不只是把页面颜色改回去。"""
    response = RedirectResponse(url="/lab/preferences", status_code=303)
    response.delete_cookie(
        key=COOKIE_NAME,
        path=COOKIE_PATH,
        httponly=True,
        secure=False,
        samesite="lax",
    )
    return response
# endregion cookie-reset


# region lab-mounts
app.mount("/static", StaticFiles(directory=str(ROOT / "static")), name="static")
# endregion lab-mounts
