"""第 5 课黑盒自检：只发本地 HTTP，验证 SSR 表单闭环（M1 验收，底稿 6.2）。

不检查 ssr.py 的写法、类名或代码组织，只看真实响应：三页可导航、三字段同时非法带原值回填、
成功 303 → GET 详情、重复标题 409 回填、JSON 四字段与探针未退化、响应带 X-Request-ID。
运行前会调用教师复位端点把库还原为固定三条，可重复运行。

保持 SSR 服务运行，另开一个终端、激活同一环境、在 question-api 目录下：
    python check_ssr.py
    python check_ssr.py --base-url http://127.0.0.1:8001 --timeout 3

学生工作文件（ssr:app）在补齐 render_validation_failure 与两个模板前，相关用例会失败；
教师完整参考（reference.ssr:app）应全部通过。全部通过退出码 0，否则 1。
"""

import argparse
import json
import math
from html.parser import HTMLParser
from urllib.error import HTTPError
from urllib.parse import quote, urlencode, urlsplit
from urllib.request import HTTPRedirectHandler, ProxyHandler, Request, build_opener

SEED_CREATED_AT = "2026-09-01T08:00:00+00:00"
RECORD_3 = {"id": 3, "title": "React 的 props 是什么？", "body": "想知道组件怎样接收数据。"}
FIELD_MESSAGES = {
    "title": "标题去除首尾空白后须为 5–200 个字符。",
    "body": "正文去除首尾空白后须为 10–20000 个字符。",
    "tags": "标签须为字符串列表，最多 5 项。",
}
MAX_BYTES = 1_048_576


class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


class Page(HTMLParser):
    """把 SSR 页面解析成 fields/text/links/elements；按已核对的 HTML 换行规则处理 textarea 首换行。"""

    def __init__(self, source):
        super().__init__(convert_charrefs=True)
        self.fields = {}
        self.text = []
        self.links = []
        self.elements = []
        self.area = None
        self.ignore_first_lf = False
        self.feed(source.replace("\r\n", "\n").replace("\r", "\n"))

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        self.elements.append((tag, attrs))
        if tag == "input" and "name" in attrs:
            self.fields[attrs["name"]] = attrs.get("value", "")
        if tag == "textarea":
            self.area = attrs.get("name")
            self.fields[self.area] = ""
            self.ignore_first_lf = True
        if tag == "a":
            self.links.append(attrs.get("href", ""))

    def handle_endtag(self, tag):
        if tag == "textarea":
            self.area = None

    def handle_data(self, data):
        if self.area is not None:
            if self.ignore_first_lf:
                data = data.removeprefix("\n")
                self.ignore_first_lf = False
            self.fields[self.area] += data
        self.text.append(data)

    @property
    def joined(self):
        return "".join(self.text)

    def detail_links(self):
        return [href for href in self.links if href.startswith("/ui/questions/")]


def local_base_url(value):
    try:
        parts = urlsplit(value)
        if (
            parts.scheme != "http"
            or parts.hostname not in {"127.0.0.1", "localhost", "::1"}
            or parts.username is not None
            or parts.password is not None
            or parts.path not in {"", "/"}
            or parts.query
            or parts.fragment
            or parts.port == 0
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
    # 不使用系统代理、不跟随跳转，以便核对 303 与 Location。
    return build_opener(ProxyHandler({}), NoRedirect())


def _read(response):
    raw = response.read(MAX_BYTES + 1)
    if len(raw) > MAX_BYTES:
        raise ValueError("响应超过本课自检的 1 MiB 限制")
    return raw


def get(base, path, timeout=3, accept="*/*"):
    """返回 (status, content_type, text, headers)。"""
    req = Request(base + path, headers={"Accept": accept}, method="GET")
    try:
        response = _opener().open(req, timeout=timeout)
    except HTTPError as exc:
        response = exc
    with response:
        raw = _read(response)
        return response.status, response.headers.get_content_type(), raw.decode("utf-8", "replace"), response.headers


def post_form(base, path, fields, timeout=3):
    """以 application/x-www-form-urlencoded 提交；fields 可为 dict 或 (键, 值) 列表（保留重复键）。"""
    pairs = list(fields.items()) if isinstance(fields, dict) else list(fields)
    data = urlencode(pairs).encode("utf-8")
    req = Request(base + path, data=data,
                  headers={"Accept": "text/html", "Content-Type": "application/x-www-form-urlencoded"},
                  method="POST")
    try:
        response = _opener().open(req, timeout=timeout)
    except HTTPError as exc:
        response = exc
    with response:
        raw = _read(response)
        return response.status, response.headers.get_content_type(), raw.decode("utf-8", "replace"), response.headers


def post_json(base, path, payload, timeout=3):
    data = json.dumps(payload).encode("utf-8")
    req = Request(base + path, data=data,
                  headers={"Accept": "*/*", "Content-Type": "application/json"}, method="POST")
    try:
        response = _opener().open(req, timeout=timeout)
    except HTTPError as exc:
        response = exc
    with response:
        raw = _read(response)
        body = None
        if response.headers.get_content_type() == "application/json":
            try:
                body = json.loads(raw)
            except json.JSONDecodeError:
                body = None
        return response.status, response.headers.get_content_type(), body, response.headers


def reset_db(base, timeout=3):
    req = Request(base + "/__teacher/reset", data=b"", headers={"Accept": "*/*"}, method="POST")
    try:
        with _opener().open(req, timeout=timeout) as response:
            return response.status
    except HTTPError as exc:
        return exc.code
    except OSError:
        return None


def count_via_json(base, title, timeout=3):
    """用 JSON 列表接口按关键词计数，作为独立连接的写入核对。"""
    status, media, text, _ = get(base, "/questions?keyword=" + quote(title), timeout)
    if status != 200 or media != "application/json":
        return None
    try:
        return json.loads(text).get("total")
    except json.JSONDecodeError:
        return None


def check(base, timeout=3, emit=print):
    reset = reset_db(base, timeout)
    if reset not in (200, 201, 204):
        emit(f"提示：复位端点返回 {reset}（可能未提供教师复位）；固定样本检查可能受既有数据影响。")

    cases = []

    def case(name, path, run):
        cases.append((name, path, run))

    def is_html(media):
        return (media or "").startswith("text/html")

    # —— 三页导航（读取，先跑）——
    def form_page():
        status, media, text, headers = get(base, "/ui/questions/new", timeout)
        reasons = []
        if status != 200 or not is_html(media):
            return [f"创建表单页应 200 text/html，实得 {status}/{media}"]
        page = Page(text)
        if page.fields.get("title") != "" or page.fields.get("body") != "" or page.fields.get("tags") != "":
            reasons.append(f"新建表单三字段应为空，实得 {page.fields}")
        if not any(t == "form" and a.get("action") == "/ui/questions" and a.get("method") == "post"
                   and "novalidate" in a for t, a in page.elements):
            reasons.append("缺少 method=post、action=/ui/questions、novalidate 的表单")
        if "/ui/questions" not in page.links or "/ui/questions/new" not in page.links:
            reasons.append("未继承 base 的导航链接")
        if not headers.get("X-Request-ID"):
            reasons.append("响应缺少 X-Request-ID 头")
        return reasons

    def list_page():
        status, media, text, _ = get(base, "/ui/questions", timeout)
        if status != 200 or not is_html(media):
            return [f"列表页应 200 text/html，实得 {status}/{media}"]
        page = Page(text)
        ids = [int(href.rsplit("/", 1)[1]) for href in page.detail_links() if href.rsplit("/", 1)[1].isdigit()]
        reasons = []
        if ids[:3] != [3, 2, 1]:
            reasons.append(f"列表应按 id 降序含 3/2/1，实得链接 {ids}")
        if RECORD_3["title"] not in page.joined:
            reasons.append("列表未显示种子标题")
        if "3" not in page.joined:
            reasons.append("列表未显示总数")
        return reasons

    def list_search():
        status, _, text, _ = get(base, "/ui/questions?keyword=react", timeout)
        page = Page(text)
        ids = [int(href.rsplit("/", 1)[1]) for href in page.detail_links() if href.rsplit("/", 1)[1].isdigit()]
        return [] if status == 200 and ids == [3] else [f"keyword=react 应只含 id 3，实得 {status} {ids}"]

    def list_empty():
        status, _, text, _ = get(base, "/ui/questions?keyword=zzzz-no-match", timeout)
        if status == 200 and "没有找到相关问题" in text:
            return []
        return [f"无匹配应 200 且提示“没有找到相关问题”，实得 {status}"]

    def list_page2():
        status, _, text, _ = get(base, "/ui/questions?page=2&page_size=2", timeout)
        page = Page(text)
        ids = [int(href.rsplit("/", 1)[1]) for href in page.detail_links() if href.rsplit("/", 1)[1].isdigit()]
        return [] if status == 200 and ids == [1] else [f"page=2&page_size=2 应含 id 1，实得 {status} {ids}"]

    def list_bad_param():
        status, media, text, _ = get(base, "/ui/questions?page=0", timeout)
        if status == 422 and is_html(media) and "请求参数不合法" in text:
            return []
        return [f"page=0 应 422 HTML 安全页，实得 {status}/{media}"]

    def detail_page():
        status, media, text, _ = get(base, "/ui/questions/3", timeout)
        if status != 200 or not is_html(media):
            return [f"详情应 200 text/html，实得 {status}/{media}"]
        reasons = []
        if RECORD_3["title"] not in text or RECORD_3["body"] not in text:
            reasons.append("详情未显示种子标题或正文（不能写死单条）")
        if "暂无标签" not in text:
            reasons.append("空标签未显示“暂无标签”")
        if SEED_CREATED_AT not in text:
            reasons.append(f"详情未显示带时区创建时间 {SEED_CREATED_AT}")
        return reasons

    def detail_missing():
        reasons = []
        for qid in (999, 0, -1):
            status, media, text, _ = get(base, f"/ui/questions/{qid}", timeout)
            if not (status == 404 and is_html(media) and "问题不存在" in text):
                reasons.append(f"/ui/questions/{qid} 应 404 HTML“问题不存在”，实得 {status}/{media}")
        return reasons

    def detail_non_int():
        status, media, text, _ = get(base, "/ui/questions/abc", timeout)
        if status == 422 and is_html(media):
            return []
        return [f"/ui/questions/abc 应 422 HTML，实得 {status}/{media}"]

    # —— 表单闭环（会写库，放在读取之后）——
    def three_field_invalid():
        invalid = [("title", "  x  "), ("body", "  short  "), ("tags", "a,b,c,d,e,f")]
        before = count_via_json(base, "", timeout)
        status, media, text, headers = post_form(base, "/ui/questions", invalid, timeout)
        reasons = []
        if status != 422 or not is_html(media):
            return [f"三字段同时非法应 422 HTML，实得 {status}/{media}"]
        page = Page(text)
        if page.fields.get("title") != "  x  " or page.fields.get("body") != "  short  " or page.fields.get("tags") != "a,b,c,d,e,f":
            reasons.append(f"三字段原值应完整回填，实得 {page.fields}")
        for field, message in FIELD_MESSAGES.items():
            if message not in text:
                reasons.append(f"缺少 {field} 的固定提示文案")
        if "Location" in headers:
            reasons.append("422 不应带 Location")
        if before is not None and count_via_json(base, "", timeout) != before:
            reasons.append("422 不应写入新记录")
        return reasons

    def create_prg():
        values = {"title": "第一个 SSR 合法问题", "body": "这是用于验证表单闭环的合法正文。", "tags": "python,FastAPI"}
        status, media, text, headers = post_form(base, "/ui/questions", values, timeout)
        reasons = []
        if status != 303:
            return [f"合法创建应 303，实得 {status}/{media} {text[:120]}"]
        location = headers.get("Location", "")
        if not location.startswith("/ui/questions/"):
            reasons.append(f"303 的 Location 应指向 /ui/questions/<id>，实得 {location!r}")
        if count_via_json(base, values["title"], timeout) != 1:
            reasons.append("独立连接应看到刚提交的一条记录")
        if location:
            d_status, d_media, d_text, _ = get(base, location, timeout)
            if d_status != 200 or not is_html(d_media):
                reasons.append(f"沿 Location GET 详情应 200 HTML，实得 {d_status}/{d_media}")
            else:
                if values["title"] not in d_text or values["body"] not in d_text:
                    reasons.append("详情页未显示刚提交的标题或正文")
                if "python" not in d_text or "FastAPI" not in d_text:
                    reasons.append("详情页未显示按逗号切分的两个标签")
            again_status, _, _, _ = get(base, location, timeout)
            if again_status != 200 or count_via_json(base, values["title"], timeout) != 1:
                reasons.append("再次 GET 详情不应写入第二条")
        return reasons

    def duplicate_409():
        values = {"title": "  重复标题冲突样本  ", "body": "第一次创建这段合法正文用于冲突核对。", "tags": "a"}
        first = post_form(base, "/ui/questions", values, timeout)[0]
        status, media, text, _ = post_form(base, "/ui/questions", values, timeout)
        reasons = []
        if first != 303:
            reasons.append(f"首次创建应 303，实得 {first}")
        if status != 409 or not is_html(media):
            return reasons + [f"重复标题应 409 HTML，实得 {status}/{media}"]
        page = Page(text)
        if page.fields.get("title") != values["title"] or page.fields.get("body") != values["body"]:
            reasons.append(f"409 应回填原始三项，实得 {page.fields}")
        if "标题已存在" not in text:
            reasons.append("409 未提示“标题已存在”")
        if count_via_json(base, "重复标题冲突样本", timeout) != 1:
            reasons.append("冲突后独立连接应只有一条")
        return reasons

    def extra_form_key():
        values = {"title": "含额外键的合法标题", "body": "这段正文合法但表单多了一个键。", "tags": "", "id": "999"}
        status, media, text, _ = post_form(base, "/ui/questions", values, timeout)
        if status == 422 and is_html(media) and "表单只接受标题、正文和标签字段。" in text:
            return []
        return [f"额外表单键应 422 HTML 并提示只接受三字段，实得 {status}/{media}"]

    # —— JSON 与探针回归 ——
    def json_not_html_by_accept():
        status, media, text, _ = get(base, "/questions/999", timeout, accept="text/html")
        reasons = []
        if status != 404 or media != "application/json":
            return [f"JSON 路径带 Accept:text/html 仍应 404 JSON，实得 {status}/{media}"]
        try:
            body = json.loads(text)
        except json.JSONDecodeError:
            return ["404 正文不是 JSON"]
        if set(body) != {"code", "message", "detail", "request_id"} or body.get("code") != "question_not_found":
            reasons.append(f"四字段错误未保持，实得 {body}")
        return reasons

    def json_create_201():
        payload = {"title": "JSON 入口仍然可用", "body": "证明 SSR 未破坏 JSON 创建契约。", "tags": ["one,two"]}
        status, media, body, headers = post_json(base, "/questions", payload, timeout)
        reasons = []
        if status != 201 or not isinstance(body, dict):
            return [f"JSON 合法创建应 201，实得 {status}/{media}"]
        if body.get("tags") != ["one,two"]:
            reasons.append(f"JSON 标签应原样保留（不受表单 CSV 规则影响），实得 {body.get('tags')}")
        if not (headers.get("Location") or "").startswith("/questions/"):
            reasons.append("JSON 201 应带 /questions/<id> 的 Location")
        return reasons

    def healthz():
        status, media, text, _ = get(base, "/healthz", timeout)
        try:
            body = json.loads(text)
        except json.JSONDecodeError:
            body = None
        if status == 200 and body == {"status": "ok"}:
            return []
        return [f"/healthz 应 200 {{\"status\":\"ok\"}}，实得 {status} {body}"]

    case("创建表单页空值", "/ui/questions/new", form_page)
    case("列表三条降序", "/ui/questions", list_page)
    case("列表搜索 react", "/ui/questions?keyword=react", list_search)
    case("列表空结果 200", "/ui/questions?keyword=zzzz-no-match", list_empty)
    case("列表分页第二页", "/ui/questions?page=2&page_size=2", list_page2)
    case("列表非法参数 422", "/ui/questions?page=0", list_bad_param)
    case("详情命中", "/ui/questions/3", detail_page)
    case("详情不存在 404", "/ui/questions/999|0|-1", detail_missing)
    case("详情非整数 422", "/ui/questions/abc", detail_non_int)
    case("三字段同时非法回填", "POST /ui/questions", three_field_invalid)
    case("合法创建 303 与 PRG", "POST /ui/questions", create_prg)
    case("重复标题 409 回填", "POST /ui/questions", duplicate_409)
    case("额外表单键拒绝", "POST /ui/questions", extra_form_key)
    case("JSON 不因 Accept 变 HTML", "/questions/999", json_not_html_by_accept)
    case("JSON 创建 201", "POST /questions", json_create_201)
    case("存活探针", "/healthz", healthz)

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
    emit("自检只看 HTTP 表现；模板结构、字段映射与执行方式判据请用课堂观察和 reference/ssr.py 对照。")
    return failures


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base-url", type=local_base_url, default="http://127.0.0.1:8000")
    parser.add_argument("--timeout", type=positive_timeout, default=3)
    args = parser.parse_args()
    return 1 if check(args.base_url, args.timeout) else 0


if __name__ == "__main__":
    raise SystemExit(main())
