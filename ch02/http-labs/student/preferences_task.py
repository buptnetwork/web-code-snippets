"""第 5 课偏好 Cookie 实验（学生工作文件）：设置 / 读取 / 删除，二选一实现方向之一。

教师已给页面模板与常量；你补齐三个端点的接线，使一次完整往返成立：

    GET  /lab/preferences        读取 Cookie，缺失/未知回退 light，渲染页面
    POST /lab/preferences        校验 theme∈{light,dark}（非法 422），成功显式 303 并 set_cookie
    POST /lab/preferences/reset  删除同名同 Path 的 Cookie，成功显式 303

固定契约（不能改）：
- 名称 course_lab_theme，Path=/lab，不设 Domain；
- HttpOnly、SameSite=Lax、Max-Age=3600；本地 HTTP 用 secure=False；
- set_cookie / delete_cookie 必须写在这次真正返回的 RedirectResponse 上；
- 读取端直接判断原始字符串，缺失/未知回退 light，不套严格枚举提前拦截。

页面脚本读不到 HttpOnly Cookie 属于预期；服务端读取后渲染偏好即可。

启动（包根，已激活本包环境）：
    python -m uvicorn student.preferences_task:app --host 127.0.0.1 --port 8125
"""

# region student-preferences
from pathlib import Path
from typing import Annotated, Literal

from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel

ROOT = Path(__file__).resolve().parent.parent
app = FastAPI(title="偏好 Cookie 实验（学生工作文件）")
templates = Jinja2Templates(directory=str(ROOT / "templates"))

COOKIE_NAME = "course_lab_theme"
COOKIE_PATH = "/lab"
ALLOWED_THEMES = ("light", "dark")


class PreferenceForm(BaseModel):
    theme: Literal["light", "dark"]


@app.get("/lab/preferences", response_class=HTMLResponse)
def read_preferences(request: Request):
    raw = request.cookies.get(COOKIE_NAME)
    theme = raw if raw in ALLOWED_THEMES else "light"
    return templates.TemplateResponse(
        request=request, name="preferences.html", context={"theme": theme, "raw": raw}
    )


@app.post("/lab/preferences")
async def set_preferences(form: Annotated[PreferenceForm, Form()]):
    response = RedirectResponse(url="/lab/preferences", status_code=303)
    # TODO(学生): 在 response 上 set_cookie —— 名称/Path/HttpOnly/SameSite/Max-Age/secure 按契约填写
    return response


@app.post("/lab/preferences/reset")
def reset_preferences():
    response = RedirectResponse(url="/lab/preferences", status_code=303)
    # TODO(学生): 在 response 上 delete_cookie —— 同名、同 Path、同属性范围
    return response


app.mount("/static", StaticFiles(directory=str(ROOT / "static")), name="static")
# endregion student-preferences
