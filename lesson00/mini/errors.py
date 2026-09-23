"""领域异常家族。
与第 1 次课的 app/errors.py 同构：那里的 status_code 是 HTTP 状态码，
这里的 exit_code 是命令行退出码——两者都是"给外界的错误编号"。
业务代码（service.py）只抛这个家族的异常，不关心外界怎么表达它们。
"""


# #region family
class AppError(Exception):
    code = "internal_error"
    exit_code = 1

    def __init__(self, detail: str = "") -> None:
        self.detail = detail
        super().__init__(detail)


class NotFoundError(AppError):
    code = "not_found"
    exit_code = 4


class ConflictError(AppError):
    code = "conflict"
    exit_code = 5


class RuleViolation(AppError):
    code = "rule_violation"
    exit_code = 6
# #endregion family
