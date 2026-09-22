"""按教学底稿重建的反例，不是外部仓库的 Git tag。

只对本地虚构数据运行。故意保留拼接 SQL、读用 POST、业务失败仍 200。
框架仍可能返回 422/500；uvicorn 也有访问日志，缺的是应用级关联记录。
"""
# region setup
import os
from fastapi import FastAPI
from sqlalchemy import create_engine, text

app = FastAPI(title="M0 · v1 教学反例")
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./demo.db")
API_TOKEN = "DEMO_ONLY_NOT_A_REAL_TOKEN"  # 未使用；硬编码反例，非真实凭据
engine = create_engine(DATABASE_URL)
# endregion setup

# region search
@app.post("/getQuestions")
def get_questions(keyword: str = "", page: int = 1):
    with engine.connect() as conn:
        rows = conn.execute(text(
            f"SELECT * FROM questions "
            f"WHERE title LIKE '%{keyword}%' "
            f"LIMIT 20 OFFSET {(page - 1) * 20}"
        )).fetchall()
    return {"success": True, "data": [dict(r._mapping) for r in rows]}
# endregion search

# region detail
@app.post("/getQuestionDetail")
def get_question_detail(qid: int):
    with engine.connect() as conn:
        row = conn.execute(text(
            f"SELECT * FROM questions WHERE id = {qid}"
        )).fetchone()
    if row is None:
        return {"success": False, "message": "not found"}
    return {"success": True, "data": dict(row._mapping)}
# endregion detail
