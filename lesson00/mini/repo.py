"""数据访问层。对应第 1 次课的 app/repositories/post_repo.py。

它只管存取，不懂任何业务规则。第 1 次课的仓储会在第 6 次课被换成 SQLAlchemy 实现，
而上面两层一行不改；本文件同理——把 JSON 文件换成数据库，service.py 不用动。
"""
import json
import logging
from datetime import datetime, timezone
from pathlib import Path

from mini.models import Todo

log = logging.getLogger("mini.repo")
DATA_FILE = Path("todos.json")


class JsonTodoRepo:
    def __init__(self, path: Path = DATA_FILE) -> None:
        self.path = path

    # --- 内部工具 ---
    def _load(self) -> list[Todo]:
        if not self.path.exists():
            log.info("READ %s -> 0 rows (文件不存在)", self.path)
            return []
        raw = json.loads(self.path.read_text(encoding="utf-8"))
        rows = [Todo(**item) for item in raw]
        log.info("READ %s -> %d rows", self.path, len(rows))
        return rows

    def _save(self, rows: list[Todo]) -> None:
        data = [row.__dict__ for row in rows]
        self.path.write_text(
            json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8"
        )

    # --- 对外接口（第 1 次课的仓储也是这几个方法） ---
    def list(self) -> list[Todo]:
        return self._load()

    # #region get
    def get(self, todo_id: int) -> Todo | None:
        for row in self._load():
            if row.id == todo_id:
                return row
        return None
    # #endregion get

    def title_exists(self, title: str) -> bool:
        return any(row.title == title for row in self._load())

    # #region add
    def add(self, *, title: str, created_by: str) -> Todo:
        rows = self._load()
        next_id = max((r.id for r in rows), default=0) + 1
        row = Todo(
            id=next_id,
            title=title,
            done=False,
            created_at=datetime.now(timezone.utc).isoformat(timespec="seconds"),
            created_by=created_by,
        )
        rows.append(row)
        self._save(rows)
        log.info("INSERT -> id=%s", row.id)
        return row
    # #endregion add

    def set_done(self, todo_id: int, done: bool) -> Todo | None:
        rows = self._load()
        for row in rows:
            if row.id == todo_id:
                row.done = done
                self._save(rows)
                log.info("UPDATE id=%s done=%s", todo_id, done)
                return row
        return None

    def delete(self, todo_id: int) -> bool:
        rows = self._load()
        kept = [r for r in rows if r.id != todo_id]
        if len(kept) == len(rows):
            return False
        self._save(kept)
        log.info("DELETE id=%s", todo_id)
        return True
