"""第 4 课模型：第 3 课输入／输出契约 ＋ 本课新增的错误与探针模型。

理解边界（对应底稿〇「教师提供与学生负责」）：
- `QuestionOut`／`QuestionListOut`／`QuestionCreate` 沿用第 3 课，R 阶段不改字段与校验；
- `AppError` 家族只表达业务原因、不带状态码，也不 import 任何 Web 类型，服务只抛它、不碰 HTTP；
  状态码与 code／message 集中收进 `BUSINESS_HTTP`，由统一处理器翻译；
- `ErrorOut` 是统一错误出口的四字段安全投影（升级后的存活探针输出 HealthOut 见 reference/server.py）。
全部数据均为教学虚构。
"""

# region out-models
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


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
# endregion out-models


# region create-model
from pydantic import field_validator


class QuestionCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")
    title: str = Field(min_length=5, max_length=200)
    body: str = Field(min_length=10, max_length=20000)
    tags: list[str] = Field(default_factory=list, max_length=5)

    @field_validator("title", "body", mode="before")
    @classmethod
    def strip_text(cls, value):
        return value.strip() if isinstance(value, str) else value
# endregion create-model


# region error-models
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
# endregion error-models


# region response-models
from typing import Any


class ErrorOut(BaseModel):
    """统一错误出口的四字段安全投影：只暴露稳定 code、可读 message、可空 detail 与追踪 id。"""

    code: str
    message: str
    detail: Any = None
    request_id: str | None = None
# endregion response-models
