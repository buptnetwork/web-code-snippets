"""外部输入的翻译层。对应第 1 次课的 app/routers/posts.py + app/errors.py 的处理器。

它只做四件事：解析输入 → 调用服务 → 把结果翻译成人话 → 把错误翻译成退出码。
业务判断零行。

关键：整个程序只有一处在做"领域异常 → 外界错误编号"的翻译，就是下面那个 except AppError。
第 1 次课把它换成 @app.exception_handler(AppError)，做的是同一件事。
"""
import argparse
import logging
import sys

from mini.errors import AppError
from mini.repo import JsonTodoRepo
from mini.service import TodoService


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="mini", description="课前课用的待办清单")
    sub = parser.add_subparsers(dest="command", required=True)

    p_add = sub.add_parser("add", help="添加一条待办")
    p_add.add_argument("title")

    sub.add_parser("list", help="列出全部待办")

    p_done = sub.add_parser("done", help="标记完成")
    p_done.add_argument("todo_id", type=int)

    p_del = sub.add_parser("delete", help="删除一条待办")
    p_del.add_argument("todo_id", type=int)

    return parser


# #region render
def render(todo) -> str:
    mark = "x" if todo.done else " "
    # 注意：created_by 是内部字段，这里不输出。
    # 对应第 1 次课的 response_model —— 出站白名单。
    return f"[{mark}] #{todo.id} {todo.title}"
# #endregion render


# #region main
def main(argv: list[str] | None = None) -> int:
    logging.basicConfig(
        level=logging.INFO, format="%(levelname)-5s %(name)-12s %(message)s"
    )
    args = build_parser().parse_args(argv)
    svc = TodoService(repo=JsonTodoRepo())      # 组装依赖：对应第 1 次课的 deps.py

    try:
        if args.command == "add":
            print("已添加：" + render(svc.add_todo(args.title)))
        elif args.command == "list":
            rows = svc.list_todos()
            if not rows:
                print("（空）")
            for row in rows:
                print(render(row))
        elif args.command == "done":
            print("已完成：" + render(svc.finish_todo(args.todo_id)))
        elif args.command == "delete":
            svc.remove_todo(args.todo_id)
            print(f"已删除 #{args.todo_id}")
    except AppError as exc:
        # ← 全程序唯一的错误翻译点
        print(f"错误[{exc.code}]：{exc.detail}", file=sys.stderr)
        return exc.exit_code
    return 0
# #endregion main


if __name__ == "__main__":
    sys.exit(main())
