"""第 2 课起点包服务：同源静态页 + 搜索分页接口 + 教师故障切换设施。

理解边界：
- 页面挂载、启动配置、给定样式与故障设施对学生为「要求会用／黑盒」，不考内部实现。
- 搜索固定取第一页由页面负责；后端具备分页能力不等于本课要开发分页交互。
- 故障切换用独立的教师端点，不污染业务 URL（不假设 /questions 支持某个故障参数）。

启动（包根，已激活本包环境）：
    python -m uvicorn server:app --host 127.0.0.1 --port 8000
"""

# region imports
import asyncio
import os
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Literal

from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

import question_store

ROOT = Path(__file__).resolve().parent
STATIC_DIR = ROOT / "static"
PREDICT_DIR = ROOT / "experiments" / "predict"

FaultMode = Literal[
    "normal", "delay", "http500_json", "http500_html", "json200_html", "struct200"
]
ALLOWED_FAULTS = ("normal", "delay", "http500_json", "http500_html", "json200_html", "struct200")
# 教学用有界延迟；有明确上限，不是性能测量结论。
DELAY_SECONDS = float(os.environ.get("DELAY_SECONDS", "1.0"))
# endregion imports


# region fault-state
def _initial_fault() -> str:
    mode = os.environ.get("FAULT_MODE", "normal")
    if mode not in ALLOWED_FAULTS:
        raise ValueError(f"FAULT_MODE 只允许 {ALLOWED_FAULTS}，收到 {mode!r}")
    return mode


# 单进程教学服务，用一个模块级状态表示当前故障模式；默认正常。
_FAULT = _initial_fault()


class FaultRequest(BaseModel):
    mode: FaultMode
# endregion fault-state


# region app
@asynccontextmanager
async def lifespan(_: FastAPI):
    # 启动即确保数据库已建表并播种（幂等）。
    question_store.init_db()
    yield


app = FastAPI(lifespan=lifespan)
# endregion app


# region teacher-fault
@app.get("/__teacher/fault")
def read_fault():
    """教师端点：读取当前故障模式。黑盒，学生不实现、不修改。"""
    return {"mode": _FAULT, "allowed": list(ALLOWED_FAULTS)}


@app.post("/__teacher/fault")
def set_fault(request: FaultRequest):
    """教师端点：切换故障模式；mode=normal 复位。非法模式由框架返回 422。"""
    global _FAULT
    _FAULT = request.mode
    return {"mode": _FAULT}
# endregion teacher-fault


# region search-endpoint
@app.get("/questions")
async def search_questions(
    keyword: str = "",
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=50),
):
    """搜索接口：GET /questions?keyword=...&page=1&page_size=20。

    正常返回 {"items":[...], "total":匹配总数, "page":当前页}；记录含 id/title/body。
    非法分页参数由框架返回 422。故障模式改变本次响应，用于课堂受控对照。
    """
    mode = _FAULT
    if mode == "http500_json":
        raise HTTPException(status_code=500, detail="服务器内部错误（教学故障 http500_json）")
    if mode == "http500_html":
        return HTMLResponse("<h1>500 内部错误（教学故障 http500_html）</h1>", status_code=500)
    if mode == "json200_html":
        # 200 + HTML 正文：HTTP 检查通过，但 .json() 解析失败。
        return HTMLResponse("<h1>这不是 JSON（教学故障 json200_html）</h1>", status_code=200)
    if mode == "struct200":
        # 200 + 合法 JSON 但结构不符：items 不是数组，触发页面结构检查失败。
        return JSONResponse({"items": None})
    if mode == "delay":
        await asyncio.sleep(DELAY_SECONDS)
    items, total = question_store.search(keyword, page, page_size)
    return {"items": items, "total": total, "page": page}
# endregion search-endpoint


# region detail
@app.get("/questions/{qid}")
def get_question(qid: int):
    """详情：保持第 1 课记录结构，缺失为 404。本课不开发详情页面。"""
    record = question_store.get_by_id(qid)
    if record is None:
        raise HTTPException(status_code=404, detail="问题不存在")
    return record
# endregion detail


# region health
@app.get("/healthz")
def healthz():
    """纯存活探针：200 + {"status":"ok"}，不检查数据库。"""
    return {"status": "ok"}
# endregion health


# region page
@app.get("/")
def index():
    """同源页面入口：返回静态 index.html。"""
    return FileResponse(STATIC_DIR / "index.html")
# endregion page


# region mounts
# 脚本与样式在 /static/*；预测实验页在 /experiments/predict/。
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
app.mount("/experiments/predict", StaticFiles(directory=PREDICT_DIR, html=True), name="predict")
# endregion mounts
