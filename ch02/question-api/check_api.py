"""第 3 课黑盒自检：只发本地 HTTP，验证列表／详情契约与创建接口是否达标。

不检查学生 server.py 的写法、类名或代码组织；模型声明、字段映射与断点观察由课堂
与 reference/server.py 对照，不在此自动判定。运行前会调用教师复位端点，把库还原为固定三条，
因此可重复运行。**创建接口还没补齐时，创建类检查不通过是正常的。**
"""

import argparse
import json
import math
from datetime import datetime, timezone
from urllib.error import HTTPError
from urllib.parse import urlsplit
from urllib.request import HTTPRedirectHandler, ProxyHandler, Request, build_opener

SEED_CREATED_AT = datetime(2026, 9, 1, 8, 0, 0, tzinfo=timezone.utc)
RECORD_3 = {"id": 3, "title": "React 的 props 是什么？", "body": "想知道组件怎样接收数据。", "tags": []}
RECORD_2 = {"id": 2, "title": "FastAPI 如何接收路径参数？", "body": "希望从地址取出问题编号。", "tags": []}
RECORD_1 = {"id": 1, "title": "浏览器怎样显示列表？", "body": "先确认接口能返回正确的数据。", "tags": []}
ALL_RECORDS = [RECORD_3, RECORD_2, RECORD_1]

MAX_BYTES = 1_048_576


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


def _opener():
    # 不使用系统代理、不跟随跳转，以免访问到目标教学服务之外。
    return build_opener(ProxyHandler({}), NoRedirect())


def request(base, path, method="GET", payload=None, timeout=3):
    """返回 (status, content_type, body, headers)。payload 非空时以 JSON 正文发送。"""
    data = None
    headers = {"Accept": "*/*"}
    if payload is not None:
        data = json.dumps(payload).encode("utf-8")
        headers["Content-Type"] = "application/json"
    req = Request(base + path, data=data, headers=headers, method=method)
    try:
        response = _opener().open(req, timeout=timeout)
    except HTTPError as exc:
        response = exc
    with response:
        raw = response.read(MAX_BYTES + 1)
        if len(raw) > MAX_BYTES:
            raise ValueError("响应超过本课自检的 1 MiB 限制")
        body = None
        if response.headers.get_content_type() == "application/json":
            try:
                body = json.loads(raw)
            except json.JSONDecodeError:
                body = None
        return response.status, response.headers.get_content_type(), body, response.headers


def parse_instant(value):
    """把 created_at 解析成带时区的 datetime；Z 与 +00:00 视为等价。"""
    if not isinstance(value, str):
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None


def record_fields_ok(record):
    """成功输出应含五个公开字段，created_at 能解析成带时区时间。"""
    return (
        isinstance(record, dict)
        and set(record) == {"id", "title", "body", "tags", "created_at"}
        and parse_instant(record.get("created_at")) is not None
    )


def same_public(actual, expected):
    """比较 id/title/body/tags；created_at 只比较时间含义。"""
    if not isinstance(actual, dict):
        return False
    for key in ("id", "title", "body", "tags"):
        if actual.get(key) != expected[key]:
            return False
    return parse_instant(actual.get("created_at")) == SEED_CREATED_AT


def reset_db(base, timeout=3):
    req = Request(base + "/__teacher/reset", data=b"", headers={"Accept": "*/*"}, method="POST")
    try:
        with _opener().open(req, timeout=timeout) as response:
            return response.status
    except HTTPError as exc:
        return exc.code
    except OSError:
        return None


def check(base, timeout=3, emit=print):
    reset = reset_db(base, timeout)
    if reset not in (200, 201, 204):
        emit(f"提示：复位端点返回 {reset}（可能未提供教师复位）；固定样本检查可能受既有数据影响。")

    cases = []

    def case(name, path, run):
        cases.append((name, path, run))

    # —— 读取契约（固定三条，创建之前先跑）——
    def search_empty():
        status, media, body, _ = request(base, "/questions?keyword=&page=1&page_size=20", timeout=timeout)
        reasons = []
        if status != 200 or media != "application/json":
            reasons.append(f"状态/媒体 {status}/{media}，预期 200/application/json")
        if not isinstance(body, dict):
            return reasons + ["响应不是 JSON 对象"]
        items = body.get("items")
        if not isinstance(items, list) or len(items) != 3 or not all(same_public(r, e) for r, e in zip(items, ALL_RECORDS)):
            reasons.append("items 不是三条固定样本（顺序 3／2／1，含 tags=[]）")
        if not all(record_fields_ok(r) for r in (items or [])):
            reasons.append("记录缺五个公开字段或 created_at 不可解析")
        if body.get("total") != 3 or body.get("page") != 1:
            reasons.append(f"total/page 应为 3/1，实得 {body.get('total')}/{body.get('page')}")
        return reasons

    def search_react():
        status, _, body, _ = request(base, "/questions?keyword=react&page=1&page_size=20", timeout=timeout)
        reasons = []
        if status != 200 or not isinstance(body, dict):
            return [f"状态 {status} 或非 JSON 对象"]
        if not (isinstance(body.get("items"), list) and len(body["items"]) == 1 and same_public(body["items"][0], RECORD_3)):
            reasons.append("keyword=react 应只返回 id 3")
        if body.get("total") != 1:
            reasons.append(f"total 应为 1，实得 {body.get('total')}")
        return reasons

    def search_nomatch():
        status, _, body, _ = request(base, "/questions?keyword=zzzz-no-match&page=1&page_size=20", timeout=timeout)
        if status == 200 and isinstance(body, dict) and body.get("items") == [] and body.get("total") == 0:
            return []
        return [f"无匹配应为 200、items=[]、total=0（不是 404），实得 {status} {body}"]

    def search_page2():
        status, _, body, _ = request(base, "/questions?page=2&page_size=2", timeout=timeout)
        if status == 200 and isinstance(body, dict) and [r.get("id") for r in body.get("items", [])] == [1] and body.get("total") == 3:
            return []
        return [f"page=2&page_size=2 应为 id 1、total 3，实得 {status} {body}"]

    def bad_page():
        return [] if request(base, "/questions?page=0", timeout=timeout)[0] == 422 else ["page=0 应 422"]

    def bad_page_size():
        return [] if request(base, "/questions?page_size=100", timeout=timeout)[0] == 422 else ["page_size=100 应 422"]

    def detail_ok():
        status, _, body, _ = request(base, "/questions/3", timeout=timeout)
        if status == 200 and same_public(body, RECORD_3) and record_fields_ok(body):
            return []
        return [f"详情 /questions/3 状态 {status} 或字段不符"]

    def detail_missing():
        reasons = []
        for qid in (999, 0, -1):
            status, _, body, _ = request(base, f"/questions/{qid}", timeout=timeout)
            if not (status == 404 and body == {"detail": "问题不存在"}):
                reasons.append(f"/questions/{qid} 应 404 且 detail=问题不存在，实得 {status} {body}")
        return reasons

    def detail_abc():
        return [] if request(base, "/questions/abc", timeout=timeout)[0] == 422 else ["/questions/abc 应 422"]

    def health():
        status, _, body, _ = request(base, "/healthz", timeout=timeout)
        return [] if status == 200 and body == {"status": "ok"} else [f"/healthz 状态 {status} 或内容不符"]

    def page_html():
        req = Request(base + "/", headers={"Accept": "*/*"}, method="GET")
        with _opener().open(req, timeout=timeout) as response:
            text = response.read(MAX_BYTES).decode("utf-8", "replace")
            media = response.headers.get_content_type()
        reasons = []
        if media != "text/html":
            reasons.append(f"页面入口应 text/html，实得 {media}")
        if "search-form" not in text or "/static/app.js" not in text:
            reasons.append("页面缺少 #search-form 或 /static/app.js 引用")
        return reasons

    # —— 创建契约（会写库，放在读取检查之后）——
    def create_valid():
        payload = {"title": "第一个创建的问题", "body": "这是正文，用来跨过最小长度限制。", "tags": ["python"]}
        status, _, body, headers = request(base, "/questions", "POST", payload, timeout)
        reasons = []
        if status != 201:
            return [f"合法创建应 201，实得 {status} {body}"]
        location = headers.get("Location")
        if not location:
            reasons.append("201 响应缺少 Location 头")
        if not (record_fields_ok(body) and body.get("title") == payload["title"]
                and body.get("body") == payload["body"] and body.get("tags") == ["python"]):
            reasons.append(f"创建返回记录字段不符：{body}")
        if location:
            r_status, _, r_body, _ = request(base, location, timeout=timeout)
            if not (r_status == 200 and isinstance(r_body, dict) and r_body.get("id") == body.get("id")
                    and r_body.get("title") == payload["title"] and r_body.get("tags") == ["python"]):
                reasons.append(f"沿 Location 回读不到同一条记录：{r_status} {r_body}")
        return reasons

    def create_default_tags():
        payload = {"title": "省略标签的问题", "body": "同样需要跨过正文的最小长度。"}
        status, _, body, _ = request(base, "/questions", "POST", payload, timeout)
        if status == 201 and isinstance(body, dict) and body.get("tags") == []:
            return []
        return [f"省略 tags 应 201 且输出空列表，实得 {status} {body}"]

    def create_lower_bound():
        payload = {"title": "abcde", "body": "0123456789", "tags": ["a", "b", "c", "d", "e"]}
        status, _, body, _ = request(base, "/questions", "POST", payload, timeout)
        if status == 201 and isinstance(body, dict) and body.get("title") == "abcde":
            return []
        return [f"刚好合法（title 5、body 10、tags 5）应 201，实得 {status} {body}"]

    def _expect_422_loc(payload, loc_tail):
        status, _, body, _ = request(base, "/questions", "POST", payload, timeout)
        if status != 422:
            return [f"应 422，实得 {status} {body}"]
        detail = body.get("detail") if isinstance(body, dict) else None
        if not isinstance(detail, list) or not any(err.get("loc", [None])[-1:] == [loc_tail] for err in detail):
            return [f"422 的 loc 应指向 {loc_tail}，实得 {detail}"]
        return []

    def create_short_title():
        return _expect_422_loc({"title": "abcd", "body": "0123456789"}, "title")

    def create_short_body():
        return _expect_422_loc({"title": "合法标题足够长", "body": "012345678"}, "body")

    def create_too_many_tags():
        return _expect_422_loc({"title": "合法标题足够长", "body": "0123456789", "tags": ["a", "b", "c", "d", "e", "f"]}, "tags")

    def create_extra_field():
        status, _, body, _ = request(base, "/questions", "POST",
                                     {"title": "含额外字段的问题", "body": "0123456789", "id": 999}, timeout)
        return [] if status == 422 else [f"客户端填写 id 应 422（forbid 额外字段），实得 {status} {body}"]

    def create_missing_body():
        status, _, body, _ = request(base, "/questions", "POST", {"title": "缺少正文的问题"}, timeout)
        return [] if status == 422 else [f"缺 body 应 422，实得 {status} {body}"]

    def create_blank_title():
        status, _, body, _ = request(base, "/questions", "POST", {"title": "    x", "body": "0123456789"}, timeout)
        return [] if status == 422 else [f"清洗后不足下限应 422，实得 {status} {body}"]

    def create_strip_ok():
        payload = {"title": "  两端有空白的标题  ", "body": "  0123456789  "}
        status, _, body, _ = request(base, "/questions", "POST", payload, timeout)
        if status == 201 and isinstance(body, dict) and body.get("title") == "两端有空白的标题":
            return []
        return [f"外包空白清洗后应 201 且保存清洗值，实得 {status} {body}"]

    def create_duplicate_title():
        payload = {"title": "重复标题冲突样本", "body": "0123456789"}
        first = request(base, "/questions", "POST", payload, timeout)[0]
        status, _, body, _ = request(base, "/questions", "POST", payload, timeout)
        if first != 201:
            return [f"首次创建应 201，实得 {first}"]
        if status == 409 and body == {"detail": "标题已存在"}:
            return []
        return [f"重复标题应 409 且 detail=标题已存在，实得 {status} {body}"]

    def openapi_contract():
        status, _, body, _ = request(base, "/openapi.json", timeout=timeout)
        reasons = []
        if status != 200 or not isinstance(body, dict):
            return [f"/openapi.json 状态 {status}"]
        schemas = body.get("components", {}).get("schemas", {})
        if "QuestionCreate" not in schemas:
            reasons.append("OpenAPI 未登记 QuestionCreate")
        if "QuestionOut" not in schemas:
            reasons.append("OpenAPI 未登记 QuestionOut")
        post = body.get("paths", {}).get("/questions", {}).get("post", {})
        if "201" not in post.get("responses", {}):
            reasons.append("POST /questions 未登记 201")
        return reasons

    case("空关键词三条", "/questions?keyword=", search_empty)
    case("react 一条", "/questions?keyword=react", search_react)
    case("无匹配空结果", "/questions?keyword=zzzz-no-match", search_nomatch)
    case("第二页分页", "/questions?page=2&page_size=2", search_page2)
    case("非法 page", "/questions?page=0", bad_page)
    case("非法 page_size", "/questions?page_size=100", bad_page_size)
    case("详情命中", "/questions/3", detail_ok)
    case("详情不存在", "/questions/999|0|-1", detail_missing)
    case("详情非整数", "/questions/abc", detail_abc)
    case("存活探针", "/healthz", health)
    case("页面入口", "/", page_html)
    case("创建合法并回读", "POST /questions", create_valid)
    case("省略 tags 得空列表", "POST /questions", create_default_tags)
    case("刚好合法下界", "POST /questions", create_lower_bound)
    case("title 越界", "POST /questions", create_short_title)
    case("body 越界", "POST /questions", create_short_body)
    case("tags 超量", "POST /questions", create_too_many_tags)
    case("额外字段 id", "POST /questions", create_extra_field)
    case("缺 body", "POST /questions", create_missing_body)
    case("纯空白 title", "POST /questions", create_blank_title)
    case("首尾空白清洗后合法", "POST /questions", create_strip_ok)
    case("重复标题冲突", "POST /questions", create_duplicate_title)
    case("OpenAPI 契约", "/openapi.json", openapi_contract)

    failures = 0
    for name, path, run in cases:
        try:
            reasons = run()
        except (OSError, ValueError, json.JSONDecodeError) as exc:
            reasons = [f"读取失败：{exc}"]
        if reasons:
            failures += 1
            emit(f"未通过 [{name}] {path}：{'；'.join(reasons)}")
        else:
            emit(f"通过   [{name}] {path}")
    emit(f"合计：{len(cases) - failures}/{len(cases)} 条通过。")
    emit("自检只看 HTTP 契约；模型声明、字段映射与入口断点请用课堂观察和 reference/server.py 对照。")
    return failures


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base-url", type=local_base_url, default="http://127.0.0.1:8000")
    parser.add_argument("--timeout", type=positive_timeout, default=3)
    args = parser.parse_args()
    return 1 if check(args.base_url, args.timeout) else 0


if __name__ == "__main__":
    raise SystemExit(main())
