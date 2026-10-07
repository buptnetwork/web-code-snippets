"""第 2 课黑盒自检：只读本地 HTTP，验证搜索契约与同源页面是否可访问。

不检查学生 app.js 的写法、函数名或 DOM 组织；四态行为与安全渲染由课堂观察
与 reference/app.js 对照，不在此自动判定。运行前会把教师故障模式复位为 normal。
"""

import argparse
import json
import math
from urllib.error import HTTPError
from urllib.parse import urlsplit
from urllib.request import HTTPRedirectHandler, ProxyHandler, Request, build_opener

# 预期来自本课契约，不从被测实现导入。
RECORD_3 = {"id": 3, "title": "React 的 props 是什么？", "body": "想知道组件怎样接收数据。"}
RECORD_2 = {"id": 2, "title": "FastAPI 如何接收路径参数？", "body": "希望从地址取出问题编号。"}
RECORD_1 = {"id": 1, "title": "浏览器怎样显示列表？", "body": "先确认接口能返回正确的数据。"}
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


def fetch(base, path, timeout=3):
    """返回 (status, content_type, body_bytes)。"""
    request = Request(base + path, headers={"Accept": "*/*"}, method="GET")
    try:
        response = _opener().open(request, timeout=timeout)
    except HTTPError as exc:
        response = exc
    with response:
        raw = response.read(MAX_BYTES + 1)
        if len(raw) > MAX_BYTES:
            raise ValueError("响应超过本课自检的 1 MiB 限制")
        return response.status, response.headers.get_content_type(), raw


def fetch_json(base, path, timeout=3):
    status, media_type, raw = fetch(base, path, timeout)
    return status, media_type, json.loads(raw)


def reset_fault(base, timeout=3):
    """把教师故障模式复位为 normal；失败不阻断自检，仅提示。"""
    data = json.dumps({"mode": "normal"}).encode("utf-8")
    request = Request(
        base + "/__teacher/fault",
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with _opener().open(request, timeout=timeout) as response:
            return response.status
    except HTTPError as exc:
        return exc.code
    except OSError:
        return None


def same_json(actual, expected):
    return json.dumps(actual, sort_keys=True, ensure_ascii=False) == json.dumps(
        expected, sort_keys=True, ensure_ascii=False
    )


# 每项检查返回失败原因列表；空列表表示通过。
def check(base, timeout=3, emit=print):
    reset = reset_fault(base, timeout)
    if reset not in (200, 201, 204):
        emit(f"提示：故障模式复位返回 {reset}（可能未提供教师端点）；按当前模式继续自检。")

    cases = []

    def case(name, path, run):
        cases.append((name, path, run))

    def search_empty():
        status, media, body = fetch_json(base, "/questions?keyword=&page=1&page_size=20", timeout)
        reasons = []
        if status != 200:
            reasons.append(f"状态 {status}，预期 200")
        if media != "application/json":
            reasons.append(f"媒体类型 {media}，预期 application/json")
        if not isinstance(body, dict) or not same_json(body.get("items"), ALL_RECORDS):
            reasons.append("items 不是三条固定样本（顺序 3／2／1）")
        if body.get("total") != 3 or body.get("page") != 1:
            reasons.append(f"total/page 应为 3/1，实得 {body.get('total')}/{body.get('page')}")
        return reasons

    def search_react():
        status, media, body = fetch_json(base, "/questions?keyword=react&page=1&page_size=20", timeout)
        reasons = []
        if status != 200 or media != "application/json":
            reasons.append(f"状态/媒体 {status}/{media}，预期 200/application/json")
        if not isinstance(body, dict) or not same_json(body.get("items"), [RECORD_3]):
            reasons.append("keyword=react 应只返回 id 3")
        if body.get("total") != 1:
            reasons.append(f"total 应为 1，实得 {body.get('total')}")
        return reasons

    def search_nomatch():
        status, _, body = fetch_json(base, "/questions?keyword=zzzz-no-match&page=1&page_size=20", timeout)
        reasons = []
        if status != 200:
            reasons.append(f"无匹配应为 200 空结果，实得状态 {status}")
        if not isinstance(body, dict) or body.get("items") != [] or body.get("total") != 0:
            reasons.append("无匹配应为 items=[]、total=0，不是 404")
        return reasons

    def detail_ok():
        status, _, body = fetch_json(base, "/questions/3", timeout)
        return [] if status == 200 and same_json(body, RECORD_3) else [f"详情 /questions/3 状态 {status} 或内容不符"]

    def detail_missing():
        status, _, body = fetch_json(base, "/questions/999", timeout)
        return [] if status == 404 and same_json(body, {"detail": "问题不存在"}) else [f"缺失详情应 404，实得 {status}"]

    def detail_abc():
        status, _, _ = fetch_json(base, "/questions/abc", timeout)
        return [] if status == 422 else [f"/questions/abc 应 422，实得 {status}"]

    def bad_page():
        status, _, _ = fetch_json(base, "/questions?page=0", timeout)
        return [] if status == 422 else [f"page=0 应 422，实得 {status}"]

    def bad_page_size():
        status, _, _ = fetch_json(base, "/questions?page_size=100", timeout)
        return [] if status == 422 else [f"page_size=100 应 422，实得 {status}"]

    def health():
        status, _, body = fetch_json(base, "/healthz", timeout)
        return [] if status == 200 and same_json(body, {"status": "ok"}) else [f"/healthz 状态 {status} 或内容不符"]

    def page_html():
        status, media, raw = fetch(base, "/", timeout)
        text = raw.decode("utf-8", "replace")
        reasons = []
        if status != 200 or media != "text/html":
            reasons.append(f"页面入口应 200/text/html，实得 {status}/{media}")
        if "search-form" not in text or "/static/app.js" not in text:
            reasons.append("页面缺少 #search-form 或 /static/app.js 引用")
        return reasons

    def app_js():
        status, media, raw = fetch(base, "/static/app.js", timeout)
        text = raw.decode("utf-8", "replace")
        reasons = []
        if status != 200 or "javascript" not in media:
            reasons.append(f"脚本应 200/javascript，实得 {status}/{media}")
        if "readQuestions" not in text:
            reasons.append("脚本缺少 readQuestions（起点包应已提供）")
        return reasons

    case("空关键词三条", "/questions?keyword=", search_empty)
    case("react 一条", "/questions?keyword=react", search_react)
    case("无匹配空结果", "/questions?keyword=zzzz-no-match", search_nomatch)
    case("详情命中", "/questions/3", detail_ok)
    case("详情缺失", "/questions/999", detail_missing)
    case("详情非整数", "/questions/abc", detail_abc)
    case("非法 page", "/questions?page=0", bad_page)
    case("非法 page_size", "/questions?page_size=100", bad_page_size)
    case("存活探针", "/healthz", health)
    case("页面入口", "/", page_html)
    case("静态脚本", "/static/app.js", app_js)

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
    emit("自检只看后端契约与静态可访问性；四态行为、恢复与安全渲染请用课堂观察和 reference/app.js 对照。")
    return failures


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base-url", type=local_base_url, default="http://127.0.0.1:8000")
    parser.add_argument("--timeout", type=positive_timeout, default=3)
    args = parser.parse_args()
    return 1 if check(args.base_url, args.timeout) else 0


if __name__ == "__main__":
    raise SystemExit(main())
