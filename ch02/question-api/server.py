"""第 3 课起点包服务（你的工作文件）：同源静态页 + 列表／详情 + 待补齐的创建接口。

理解边界（对应底稿〇「教师提供与学生负责」）：
- 页面挂载、启动配置、连接获取与关闭、建库与升级为「要求会用／黑盒」，不考内部实现。
- Query、输入／输出模型、端点接线为「要求解释」：能修改声明、构造边界输入并说明状态码与字段。
- 服务层提交／回滚与已知标题冲突模板为「本课要求会用」，不移动提交位置。

你的任务只在 `# region task` 内：按字段契约补齐 QuestionCreate，并接线 create_question。
列表、详情、存活探针与同源页面已给好，可直接运行、直接回归第 2 课四态页面。

启动（包根，已激活本包环境）：
    python -m uvicorn server:app --host 127.0.0.1 --port 8000
改完代码先停止再重启（不要用 --reload）。
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


# region task
class QuestionCreate(BaseModel):
    # 按字段契约补齐（底稿 2.2）：
    #   title 必填，去首尾空白后长度 5–200
    #   body  必填，去首尾空白后长度 10–20000
    #   tags  可省，默认空列表，最多 5 个字符串
    # 额外字段一律拒绝：extra="forbid"（客户端不得填写 id／created_at／author_id）。
    # 提示：加一个 mode="before" 的 field_validator，先对 title/body 去首尾空白，再校验长度。
    pass


@app.post("/questions", status_code=201, response_model=QuestionOut,
          responses={409: {"description": "标题已存在"}})
def create_question(payload: QuestionCreate, response: Response):
    # 接线（底稿 4.5）：
    #   with closing(open_connection()) as conn: result = create_question_service(conn, payload)
    #   捕获 DuplicateTitle 翻译成 409；在 response.headers 补 Location，再 return result。
    #   commit 由服务层执行，不要挪到这里或清理阶段。
    raise HTTPException(status_code=501, detail="创建接口待学生补齐")
# endregion task


# region detail-endpoint
@app.get("/questions/{qid}", response_model=QuestionOut,
         responses={404: {"description": "问题不存在"}})
def get_question(qid: int):
    with closing(open_connection()) as conn:
        result = find_question(conn, qid)
    if result is None:
        raise HTTPException(status_code=404, detail="问题不存在")
    return result
# endregion detail-endpoint


# region health
@app.get("/healthz")
def healthz():
    """纯存活探针：200 + {"status":"ok"}，不访问数据库。"""
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
