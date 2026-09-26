"""第 1 课起始版：固定数据与列表接口；在本目录启动 main:app。"""

# region application
from fastapi import FastAPI

app = FastAPI()
# endregion application

# region data
QUESTIONS = [
    {
        "id": 3,
        "title": "React 的 props 是什么？",
        "body": "想知道组件怎样接收数据。",
    },
    {
        "id": 2,
        "title": "FastAPI 如何接收路径参数？",
        "body": "希望从地址取出问题编号。",
    },
    {
        "id": 1,
        "title": "浏览器怎样显示列表？",
        "body": "先确认接口能返回正确的数据。",
    },
]
# endregion data


# region list
@app.get("/questions")
def list_questions():
    return {"items": QUESTIONS}
# endregion list
