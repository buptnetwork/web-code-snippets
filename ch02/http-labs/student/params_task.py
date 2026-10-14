"""第 3 课独立参数实验（学生工作文件）：读懂规则，再改一处声明。

教师已给固定路径 `/lab/items/latest` 与动态路径 `/lab/items/{item_id}` 的可运行骨架，
以及一个非敏感 Header 的显式 alias。你的任务只有一处：

    给 item_id 补一个范围约束，使 item_id <= 0 时返回 422，而不是 404。

要求与边界：
- 只改这一处声明；不要改动 latest 的注册顺序，也不要动主线 Question 的 qid。
- 改完自行构造正常请求（如 /lab/items/3）与非法请求（如 /lab/items/0、/lab/items/abc），
  记录状态码与错误 loc，直接收入写法卡，不另交报告。
- 实验里的 `Path(gt=0)` 不会传播到主线；主线不存在的整数 id 仍然是 404。

启动（包根，已激活本包环境）：
    python -m uvicorn student.params_task:app --host 127.0.0.1 --port 8124
"""

from typing import Annotated

from fastapi import FastAPI, Header, HTTPException, Path

app = FastAPI(title="参数实验（学生工作文件）")

ITEMS = [
    {"id": 1, "name": "笔记本", "qty": 3},
    {"id": 2, "name": "钢笔", "qty": 7},
    {"id": 3, "name": "书签", "qty": 12},
]


@app.get("/lab/items/latest")
def latest_item():
    # 固定路径先注册：比 /lab/items/{item_id} 更具体，先声明才不会被动态路径截走。
    newest = max(ITEMS, key=lambda row: row["id"])
    return {"item": newest}


# region student-task
@app.get("/lab/items/{item_id}")
def get_item(
    item_id: Annotated[int, Path()],  # TODO(学生): 在这里补范围约束，使 item_id<=0 → 422
    x_client_name: Annotated[str, Header(alias="X-Client-Name")] = "unknown",
):
    for row in ITEMS:
        if row["id"] == item_id:
            return {"item": row, "served_to": x_client_name}
    raise HTTPException(status_code=404, detail="条目不存在")
# endregion student-task
