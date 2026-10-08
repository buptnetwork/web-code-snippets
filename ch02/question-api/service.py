"""第 3 课服务模板（教师提供 · 本课要求会用，第 4 课升级为要求解释）。

服务层先验证可返回的记录，再显式提交；学生不把 commit 移到数据访问函数、
端点返回之后或未来依赖的退出代码里。教师单表基线唯一的 UNIQUE 约束是
questions.title，只有该已知冲突映射为 DuplicateTitle；其他数据库错误按服务器失败处理。
"""

import sqlite3

from models import QuestionOut
from question_db import find_question, insert_question


# region service
class DuplicateTitle(Exception):
    pass


def create_question_service(conn, payload):
    try:
        qid = insert_question(conn, payload)
        result = QuestionOut.model_validate(find_question(conn, qid))
        conn.commit()
    except sqlite3.IntegrityError as exc:
        conn.rollback()
        if exc.sqlite_errorcode == sqlite3.SQLITE_CONSTRAINT_UNIQUE:
            raise DuplicateTitle() from exc
        raise
    except Exception:
        conn.rollback()
        raise
    return result
# endregion service
