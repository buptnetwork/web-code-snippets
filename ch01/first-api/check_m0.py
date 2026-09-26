"""M0 黑盒自检：只读本地 HTTP，不检查学生源码、函数名或循环写法。"""

import argparse
import json
import math
from urllib.error import HTTPError
from urllib.parse import urlsplit
from urllib.request import HTTPRedirectHandler, ProxyHandler, Request, build_opener

# 预期来自本课契约，不能从被测实现导入。
EXPECTED = [
    {"id": 3, "title": "React 的 props 是什么？", "body": "想知道组件怎样接收数据。"},
    {"id": 2, "title": "FastAPI 如何接收路径参数？", "body": "希望从地址取出问题编号。"},
    {"id": 1, "title": "浏览器怎样显示列表？", "body": "先确认接口能返回正确的数据。"},
]
STATUS_ONLY = object()
CASES = [
    ("/questions", 200, {"items": EXPECTED}),
    *[(f"/questions/{q['id']}", 200, q) for q in EXPECTED],
    *[(f"/questions/{qid}", 404, {"detail": "问题不存在"}) for qid in (999, 0, -1)],
    ("/not-a-route", 404, {"detail": "Not Found"}),
    ("/questions/abc", 422, STATUS_ONLY),
    ("/healthz", 200, {"status": "ok"}),
]


class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def local_base_url(value):
    try:
        parts = urlsplit(value)
        port = parts.port
        if (
            parts.scheme != "http"
            or parts.hostname not in {"127.0.0.1", "localhost", "::1"}
            or parts.username is not None
            or parts.password is not None
            or parts.path not in {"", "/"}
            or parts.query
            or parts.fragment
            or port == 0
        ):
            raise ValueError
    except ValueError as exc:
        raise argparse.ArgumentTypeError("只允许本地 http://127.0.0.1:端口 等回环地址，不带路径") from exc
    return value.rstrip("/")


def positive_timeout(value):
    number = float(value)
    if not math.isfinite(number) or not 0 < number <= 30:
        raise argparse.ArgumentTypeError("超时须在 0 到 30 秒之间")
    return number


def fetch(base, path, timeout=3):
    # 不使用系统代理、不跟随跳转，以免访问到目标教学服务之外。
    opener = build_opener(ProxyHandler({}), NoRedirect())
    request = Request(base + path, headers={"Accept": "application/json"}, method="GET")
    try:
        response = opener.open(request, timeout=timeout)
    except HTTPError as exc:
        response = exc
    with response:
        raw = response.read(1_048_577)
        if len(raw) > 1_048_576:
            raise ValueError("响应超过本课自检的 1 MiB 限制")
        return response.status, response.headers.get_content_type(), json.loads(raw)


def same_json(actual, expected):
    # 忽略键顺序和排版，但不把 JSON true、1、1.0 当成同一种字段值。
    return json.dumps(actual, sort_keys=True, ensure_ascii=False) == json.dumps(
        expected, sort_keys=True, ensure_ascii=False
    )


def check(base, timeout=3, emit=print):
    failures = 0
    for path, expected_status, expected_body in CASES:
        reasons = []
        try:
            status, media_type, body = fetch(base, path, timeout)
            if status != expected_status:
                reasons.append(f"状态 {status}，预期 {expected_status}")
            if media_type != "application/json":
                reasons.append(f"媒体类型 {media_type}，预期 application/json")
            if expected_body is not STATUS_ONLY and not same_json(body, expected_body):
                reasons.append("JSON 内容、字段类型或列表顺序不符合本课固定样本")
        except (OSError, ValueError) as exc:
            reasons.append(f"读取失败：{exc}")
        if reasons:
            failures += 1
            emit(f"未通过 GET {path}：{'；'.join(reasons)}")
        else:
            emit(f"通过   GET {path}")
    emit(f"合计：{len(CASES) - failures}/{len(CASES)} 条通过。")
    emit("端点是否执行请用日志和本人断点核对；自检不能替代 IDE 与链路图。")
    return failures


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base-url", type=local_base_url, default="http://127.0.0.1:8000")
    parser.add_argument("--timeout", type=positive_timeout, default=3)
    args = parser.parse_args()
    return 1 if check(args.base_url, args.timeout) else 0


if __name__ == "__main__":
    raise SystemExit(main())
