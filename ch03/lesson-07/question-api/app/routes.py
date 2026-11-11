"""问题列表、详情与创建的 JSON 路由；由 main.py 注册到应用。"""

from fastapi import APIRouter, Query, Response

from app.database import SessionDep
from app.schemas import QuestionCreate, QuestionListOut, QuestionOut
from app.services import create_question_service, get_question_service, list_questions_orm

router = APIRouter()


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
