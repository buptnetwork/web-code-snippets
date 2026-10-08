"""第 3 课完整参考（课后对照，不作为学生练习起点）。

与包根 server.py 的差异只在 `# region create-model` 与 `# region write-endpoints`：
QuestionCreate 已按字段契约补齐（先清洗再限长、forbid 额外字段），create_question 已接线
（closing 获取连接 → 服务层提交 → DuplicateTitle 翻译 409 → 补 Location → 返回结果）。
其余（app、列表、详情、存活探针、教师复位、同源页面挂载）与 server.py 完全相同。

运行对照（包根，已激活本包环境）：
    python -m uvicorn reference.server:app --host 127.0.0.1 --port 8000
"""

# region imports
from contextlib import asynccontextmanager, closing
from pathlib import Path

from fastapi import FastAPI, HTTPException, Query, Response
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, ConfigDict, Field, field_validator

from models import QuestionListOut, QuestionOut
from question_db import (
    find_question,
    init_db,
    open_connection,
    reset_db,
    search_questions,
)
from service import DuplicateTitle, create_question_service

ROOT = Path(__file__).resolve().parent.parent
STATIC_DIR = ROOT / "static"
# endregion imports


# region app
@asynccontextmanager
async def lifespan(_: FastAPI):
    init_db()
    yield


app = FastAPI(lifespan=lifespan)
# endregion app


# region create-model
class QuestionCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")
    title: str = Field(min_length=5, max_length=200)
    body: str = Field(min_length=10, max_length=20000)
    tags: list[str] = Field(default_factory=list, max_length=5)

    @field_validator("title", "body", mode="before")
    @classmethod
    def strip_text(cls, value):
        return value.strip() if isinstance(value, str) else value
# endregion create-model


# region list-endpoint
@app.get("/questions", response_model=QuestionListOut)
def list_questions(
    keyword: str = Query(""),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=50),
):
    print("进入列表端点", page, page_size)
    with closing(open_connection()) as conn:
        return search_questions(conn, keyword, page, page_size)
# endregion list-endpoint


# region write-endpoints
@app.post("/questions", status_code=201, response_model=QuestionOut,
          responses={409: {"description": "标题已存在"}})
def create_question(payload: QuestionCreate, response: Response):
    print("进入创建端点")
    try:
        with closing(open_connection()) as conn:
            result = create_question_service(conn, payload)
    except DuplicateTitle as exc:
        raise HTTPException(status_code=409, detail="标题已存在") from exc
    response.headers["Location"] = f"/questions/{result.id}"
    return result


@app.get("/questions/{qid}", response_model=QuestionOut,
         responses={404: {"description": "问题不存在"}})
def get_question(qid: int):
    with closing(open_connection()) as conn:
        result = find_question(conn, qid)
    if result is None:
        raise HTTPException(status_code=404, detail="问题不存在")
    return result
# endregion write-endpoints


# region health
@app.get("/healthz")
def healthz():
    return {"status": "ok"}
# endregion health


# region teacher-reset
@app.post("/__teacher/reset")
def reset():
    reset_db()
    return {"status": "reset", "count": 3}
# endregion teacher-reset


# region page
@app.get("/")
def index():
    return FileResponse(STATIC_DIR / "index.html")
# endregion page


# region mounts
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
# endregion mounts
