"""数据形状。对应第 1 次课的 app/schemas/post.py。"""
from dataclasses import dataclass


# #region todo
@dataclass
class Todo:
    id: int
    title: str
    done: bool
    created_at: str
    created_by: str = "local"   # 内部字段，展示时不输出
# #endregion todo
