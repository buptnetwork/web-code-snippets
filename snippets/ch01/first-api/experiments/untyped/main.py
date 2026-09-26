"""教师类型对照：只观察入口，预期 qid 为 str；本例不满足 M0。"""

from fastapi import FastAPI, HTTPException

app = FastAPI()
QUESTIONS = [
    {"id": 3, "title": "React 的 props 是什么？", "body": "想知道组件怎样接收数据。"},
    {"id": 2, "title": "FastAPI 如何接收路径参数？", "body": "希望从地址取出问题编号。"},
    {"id": 1, "title": "浏览器怎样显示列表？", "body": "先确认接口能返回正确的数据。"},
]


# region untyped
@app.get("/questions/{qid}")
def get_question(qid):
    print("收到详情请求，qid =", qid, "类型 =", type(qid).__name__)
    for question in QUESTIONS:
        if question["id"] == qid:
            return question
    raise HTTPException(status_code=404, detail="问题不存在")
# endregion untyped
