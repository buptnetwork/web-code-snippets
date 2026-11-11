"""请求与响应的 Pydantic 模型，以及服务层抛出的业务异常。

内容沿用第 5 课 question-api/models.py；本工程中 models.py 存放 ORM 模型，
所以这些类改放在 schemas.py。
"""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator


class QuestionOut(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: int
    title: str
    body: str
    tags: list[str]
    created_at: datetime


class QuestionListOut(BaseModel):
    items: list[QuestionOut]
    total: int = Field(ge=0)
    page: int = Field(ge=1)


class QuestionCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")
    title: str = Field(min_length=5, max_length=200)
    body: str = Field(min_length=10, max_length=20000)
    tags: list[str] = Field(default_factory=list, max_length=5)

    @field_validator("title", "body", mode="before")
    @classmethod
    def strip_text(cls, value):
        return value.strip() if isinstance(value, str) else value


# 业务异常只表达原因，不带状态码；状态码与 code／message 由 main.py 的处理器按下表翻译。
class AppError(Exception):
    pass


class QuestionNotFound(AppError):
    pass


class DuplicateTitle(AppError):
    pass


BUSINESS_HTTP = {
    QuestionNotFound: (404, "question_not_found", "问题不存在"),
    DuplicateTitle: (409, "duplicate_title", "标题已存在"),
}
