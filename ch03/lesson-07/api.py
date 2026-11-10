"""三处 JSON 接线主体；不是完整应用。

router 由现有应用工厂注册；统一错误出口、request-id、HTML 页面与探针由教师保留。
"""

from typing import Annotated, Iterator

from fastapi import APIRouter, Depends, Query, Response
from sqlalchemy.orm import Session

from question_service import create_question_service, get_question_service, list_questions_orm
from schemas import QuestionCreate, QuestionListOut, QuestionOut

# 启动阶段由教师装配：engine, SessionLocal = make_session_factory(database_url)
SessionLocal = None


# region session-dependency
def get_session() -> Iterator[Session]:
    with SessionLocal() as session:
        yield session


SessionDep = Annotated[Session, Depends(get_session)]
router = APIRouter()
# endregion session-dependency


# region read-routes
@router.get("/questions", response_model=QuestionListOut)
def list_questions(
    session: SessionDep,
    keyword: str = "",
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=50),
):
    return list_questions_orm(session, keyword=keyword, page=page, page_size=page_size)


@router.get("/questions/{qid}", response_model=QuestionOut)
def get_question(qid: int, session: SessionDep):
    return get_question_service(session, qid)
# endregion read-routes


# region create-route
@router.post("/questions", response_model=QuestionOut, status_code=201)
def create_question(payload: QuestionCreate, response: Response, session: SessionDep):
    result = create_question_service(session, payload, author_id=1)
    response.headers["Location"] = f"/questions/{result.id}"
    return result
# endregion create-route
