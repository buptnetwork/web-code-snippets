"""业务规则层。对应第 1 次课的 app/services/post_service.py。

注意这个文件"没有什么"：
  - 没有 import argparse、没有 import sys
  - 没有一个 print
  - 没有一个退出码数字
它不知道自己是在为命令行服务。所以第 1 次课把 cli.py 换成 HTTP 路由时，
本文件一行都不用改。
"""
from mini.errors import ConflictError, NotFoundError, RuleViolation
from mini.models import Todo
from mini.repo import JsonTodoRepo

MIN_TITLE_LEN = 2
BANNED_WORDS = ("摸鱼", "算了")


class TodoService:
    # #region init
    def __init__(self, repo: JsonTodoRepo) -> None:
        # 仓储从外面传进来，不在这里创建 —— 这样才换得掉、测得了
        self.repo = repo
    # #endregion init

    def list_todos(self) -> list[Todo]:
        return self.repo.list()

    # #region get_todo
    def get_todo(self, todo_id: int) -> Todo:
        row = self.repo.get(todo_id)
        if row is None:
            raise NotFoundError(f"待办 {todo_id} 不存在")
        return row
    # #endregion get_todo

    # #region add_todo
    def add_todo(self, title: str) -> Todo:
        title = title.strip()
        # 只看这一次输入就能判断的 —— 格式规则
        if len(title) < MIN_TITLE_LEN:
            raise RuleViolation(f"标题至少 {MIN_TITLE_LEN} 个字，你给的是 {title!r}")
        hit = next((w for w in BANNED_WORDS if w in title), None)
        if hit:
            raise RuleViolation(f"标题包含违规词：{hit}")
        # 需要查系统里已有什么才能判断的 —— 业务规则
        if self.repo.title_exists(title):
            raise ConflictError(f"已存在同名待办：{title}")
        return self.repo.add(title=title, created_by="local")
    # #endregion add_todo

    def finish_todo(self, todo_id: int) -> Todo:
        self.get_todo(todo_id)               # 不存在则抛 NotFoundError
        row = self.repo.set_done(todo_id, True)
        assert row is not None
        return row

    def remove_todo(self, todo_id: int) -> None:
        self.get_todo(todo_id)               # 不存在则抛 NotFoundError
        self.repo.delete(todo_id)
