"""第 4 课服务层：把连接当协作对象，显式管理事务，只抛业务异常、不碰 HTTP。

理解边界（对应底稿〇「教师提供与学生负责」）：
- 从参数接收连接，自己不 connect／不 close（连接由 server 的 get_conn 依赖负责）；
- 写路径显式 commit／rollback，提交只出现在服务写函数内，不挪到端点返回之后或依赖退出里；
- 未找到抛 QuestionNotFound、标题冲突抛 DuplicateTitle（都是 models.AppError 子类），
  服务不 import HTTPException——R 阶段端点就地翻译成第 3 课的 {"detail": ...}，
  E 阶段由统一处理器按 BUSINESS_HTTP 翻译成四字段 ErrorOut。

`create_question_service` 沿用第 3 课写法，不是新增另一套提交方案；`get_question_service`
是 E 阶段详情服务，把「找不到」表达为业务异常，端点不再就地翻译。
数据层沿用第 3 课 question_db（search_questions／insert_question／find_question），不改 SQL。
"""

import sqlite3

from models import DuplicateTitle, QuestionNotFound, QuestionOut
from question_db import find_question, insert_question


# region create-service
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
# endregion create-service


# region get-service
def get_question_service(conn, qid):
    result = find_question(conn, qid)
    if result is None:
        raise QuestionNotFound()
    return QuestionOut.model_validate(result)
# endregion get-service
