"""教师构造的缺失分支对照：MISSING_RETURN=null 或 empty；两者均错误地返回 200。"""

import os

from fastapi import FastAPI

app = FastAPI()
MODE = os.environ.get("MISSING_RETURN", "null")
if MODE not in {"null", "empty"}:
    raise ValueError("MISSING_RETURN 只允许 null 或 empty")

QUESTIONS = [
    {"id": 3, "title": "React 的 props 是什么？", "body": "想知道组件怎样接收数据。"},
    {"id": 2, "title": "FastAPI 如何接收路径参数？", "body": "希望从地址取出问题编号。"},
    {"id": 1, "title": "浏览器怎样显示列表？", "body": "先确认接口能返回正确的数据。"},
]


@app.get("/questions")
def list_questions():
    return {"items": QUESTIONS}


# region missing
@app.get("/questions/{qid}")
def get_question(qid: int):
    for question in QUESTIONS:
        if question["id"] == qid:
            return question
    return None if MODE == "null" else {}
# endregion missing


@app.get("/healthz")
def healthz():
    return {"status": "ok"}
