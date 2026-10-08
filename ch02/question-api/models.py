"""第 3 课输出模型（教师提供 · 要求解释）。

`QuestionOut` 回答「服务承诺返回什么」：列表／详情／创建共用同一个输出模型。
显式 extra="ignore"，未声明字段被忽略；声明的必填字段必须存在。
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
