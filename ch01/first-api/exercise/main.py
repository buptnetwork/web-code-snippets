"""第 1 课练习：补全详情；收尾时增加存活探针。本骨架尚不满足 M0。"""

from fastapi import FastAPI

app = FastAPI()

QUESTIONS = [
    {"id": 3, "title": "React 的 props 是什么？", "body": "想知道组件怎样接收数据。"},
    {"id": 2, "title": "FastAPI 如何接收路径参数？", "body": "希望从地址取出问题编号。"},
    {"id": 1, "title": "浏览器怎样显示列表？", "body": "先确认接口能返回正确的数据。"},
]


@app.get("/questions")
def list_questions():
    return {"items": QUESTIONS}


# region task
@app.get("/questions/{qid}")
def get_question(qid: int):
    # 在 QUESTIONS 中按编号查找。
    # 补全找到与未找到的分支。
    pass
# endregion task
