"""第 4 课隔离故障副本（教师提供 · 要求观察）：在写路径注入提交前／后故障。

只修改本副本，不改动 service.py 的正常创建路径。三种模式（对应底稿 4.2）：
- normal：正常写入 → 201；
- before_commit：INSERT 与回读都成功、commit 尚未调用就抛错 → except 里 rollback 撤销插入 → 500，查询不到记录；
- after_commit：commit 已确认返回后才抛错 → except 里 rollback 对已提交事务无效 → 500，但查询能看到记录。

课堂结论：异常类型和 traceback 几乎相同，数据是否留下却由 commit 位置决定，
所以「捕获异常」不能替代「决定提交边界」。这是教师故障副本，不是学生主线要再加的第二个创建服务。
"""

import sqlite3

from models import DuplicateTitle, QuestionOut
from question_db import find_question, insert_question


# region fault
def create_with_fault(conn, payload, mode):
    if mode not in {"normal", "before_commit", "after_commit"}:
        raise ValueError("未知实验模式")
    try:
        qid = insert_question(conn, payload)
        result = QuestionOut.model_validate(find_question(conn, qid))
        if mode == "before_commit":
            raise RuntimeError("教师实验：提交前失败")
        conn.commit()
        if mode == "after_commit":
            raise RuntimeError("教师实验：提交确认后失败")
    except sqlite3.IntegrityError as exc:
        conn.rollback()
        if exc.sqlite_errorcode == sqlite3.SQLITE_CONSTRAINT_UNIQUE:
            raise DuplicateTitle() from exc
        raise
    except Exception:
        conn.rollback()
        raise
    return result
# endregion fault
