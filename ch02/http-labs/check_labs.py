"""隔离实验黑盒自检：只发本地 HTTP，验证 app.py 四组实验的对外契约。

不看写法、类名或代码组织，只看真实响应。用于修改建议 5.4 批次 1「先验证教师答案」。
保持教师应用运行，另开一个终端、激活同一环境、在本目录：

    python -m uvicorn app:app --host 127.0.0.1 --port 8123   # 终端 A
    python check_labs.py --base-url http://127.0.0.1:8123     # 终端 B

全部通过退出码 0，否则 1。学生留白（student/*.py）在补齐前对应用例会失败，属预期。
"""

import argparse
import json
import uuid
from urllib.error import HTTPError
from urllib.parse import urlencode
from urllib.request import HTTPRedirectHandler, ProxyHandler, Request, build_opener

MAX_BYTES = 1_048_576
COOKIE = "course_lab_theme"

BASE = "http://127.0.0.1:8123"
TIMEOUT = 5.0
_results = []


class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


_opener = build_opener(NoRedirect, ProxyHandler({}))


def request(method, path, headers=None, data=None):
    req = Request(BASE + path, data=data, method=method)
    for key, value in (headers or {}).items():
        req.add_header(key, value)
    try:
        resp = _opener.open(req, timeout=TIMEOUT)
        return resp.status, resp.headers, resp.read().decode("utf-8", "replace")
    except HTTPError as exc:
        return exc.code, exc.headers, exc.read().decode("utf-8", "replace")


def encode_multipart(fields, files):
    boundary = ("----labcheck" + uuid.uuid4().hex).encode()
    body = b""
    for name, value in fields.items():
        body += b"--" + boundary + b"\r\n"
        body += f'Content-Disposition: form-data; name="{name}"\r\n\r\n'.encode()
        body += value.encode() + b"\r\n"
    for name, (filename, content, content_type) in files.items():
        body += b"--" + boundary + b"\r\n"
        body += f'Content-Disposition: form-data; name="{name}"; filename="{filename}"\r\n'.encode()
        body += f"Content-Type: {content_type}\r\n\r\n".encode()
        body += content + b"\r\n"
    body += b"--" + boundary + b"--\r\n"
    return body, f"multipart/form-data; boundary={boundary.decode()}"


def check(name, condition, detail=""):
    _results.append((name, bool(condition), detail))
    flag = "PASS" if condition else "FAIL"
    print(f"[{flag}] {name}" + (f" — {detail}" if detail and not condition else ""))


def set_cookie_headers(headers):
    # Set-Cookie 可能出现多次，且服务端用小写头名；用 get_all 大小写不敏感地全部取出。
    return "; ".join(headers.get_all("Set-Cookie") or [])


# ───────────────────────── 组 1 · 参数来源与普通依赖 ─────────────────────────


def group_params():
    status, _, body = request("GET", "/lab/items/latest")
    check("latest 固定路径 200", status == 200 and json.loads(body)["item"]["id"] == 3, f"status={status}")

    status, _, body = request("GET", "/lab/items/2")
    check("动态路径命中 id=2", status == 200 and json.loads(body)["item"]["id"] == 2, f"status={status}")

    status, _, body = request("GET", "/lab/items/0")
    check("Path(gt=0) 使 item_id=0 → 422", status == 422, f"status={status}")

    status, _, _ = request("GET", "/lab/items/abc")
    check("非整数 item_id → 422", status == 422, f"status={status}")

    status, _, _ = request("GET", "/lab/items/99")
    check("范围内但不存在 → 404", status == 404, f"status={status}")

    status, _, body = request("GET", "/lab/items/1", headers={"X-Client-Name": "alice"})
    check("Header 显式 alias 进函数参数", status == 200 and json.loads(body)["served_to"] == "alice", f"status={status}")

    status, _, body = request("GET", "/lab/items?page=1&page_size=2")
    data = json.loads(body) if status == 200 else {}
    check("普通依赖分页 /lab/items", status == 200 and len(data.get("items", [])) == 2 and data.get("total") == 3, f"status={status}")

    status, _, body = request("GET", "/lab/books?page=2&page_size=2")
    data = json.loads(body) if status == 200 else {}
    check("同一依赖复用到 /lab/books", status == 200 and len(data.get("books", [])) == 2 and data.get("page") == 2, f"status={status}")

    status, _, _ = request("GET", "/lab/items?page=0")
    check("依赖参数非法 page=0 → 422（端点不执行）", status == 422, f"status={status}")


# ───────────────────────────── 组 2 · 嵌套输入 ─────────────────────────────


def group_nested():
    payload = {"name": "书单", "items": [{"title": "HTTP 权威指南"}, {"title": "流畅的 Python"}]}
    status, _, body = request("POST", "/lab/reading-lists/preview",
                              headers={"Content-Type": "application/json"}, data=json.dumps(payload).encode())
    data = json.loads(body) if status == 200 else {}
    check("嵌套正常输入 200 + count", status == 200 and data.get("count") == 2, f"status={status}")

    bad = {"name": "书单", "items": [{"title": "HTTP 权威指南"}, {}]}
    status, _, body = request("POST", "/lab/reading-lists/preview",
                              headers={"Content-Type": "application/json"}, data=json.dumps(bad).encode())
    loc_ok = False
    if status == 422:
        for err in json.loads(body).get("detail", []):
            if list(err.get("loc", [])) == ["body", "items", 1, "title"]:
                loc_ok = True
    check("第二项缺 title → 422 且 loc=body/items/1/title", status == 422 and loc_ok, f"status={status}")


# ───────────────────────────── 组 3 · 文件检查 ─────────────────────────────


def _upload(content, filename="probe.bin", with_file=True, description="hello"):
    fields = {"description": description}
    files = {"file": (filename, content, "application/octet-stream")} if with_file else {}
    body, ctype = encode_multipart(fields, files)
    return request("POST", "/lab/uploads/inspect", headers={"Content-Type": ctype}, data=body)


def group_uploads():
    status, _, body = _upload(b"small file")
    data = json.loads(body) if status == 200 else {}
    check("正常小文件 200 + 实际字节数", status == 200 and data.get("received_bytes") == 10 and data.get("stored") is False, f"status={status}")

    status, _, body = _upload(b"x" * MAX_BYTES, filename="exact.bin")
    data = json.loads(body) if status == 200 else {}
    check("恰好 1 MiB 接受 + at_limit", status == 200 and data.get("at_limit") is True, f"status={status}")

    status, _, _ = _upload(b"x" * (MAX_BYTES + 1), filename="over.bin")
    check("超过 1 MiB → 413", status == 413, f"status={status}")

    status, _, _ = _upload(b"", with_file=False)
    check("缺文件 → 422", status == 422, f"status={status}")


# ───────────────────────────── 组 4 · 偏好 Cookie ─────────────────────────────


def group_cookie():
    status, _, body = request("GET", "/lab/preferences")
    check("无 Cookie 读取回退 light", status == 200 and "当前主题：<b>light</b>" in body, f"status={status}")

    status, headers, _ = request("POST", "/lab/preferences",
                                 headers={"Content-Type": "application/x-www-form-urlencoded"},
                                 data=urlencode({"theme": "dark"}).encode())
    sc = set_cookie_headers(headers)
    check("设置成功显式 303", status == 303, f"status={status}")
    check("Set-Cookie 写在实际 RedirectResponse 上", COOKIE in sc and "dark" in sc, sc)
    lowered = sc.lower()
    check("Cookie 属性 Path=/lab; HttpOnly; SameSite=lax; Max-Age=3600",
          "path=/lab" in lowered and "httponly" in lowered and "samesite=lax" in lowered and "max-age=3600" in lowered, sc)

    status, _, body = request("GET", "/lab/preferences", headers={"Cookie": f"{COOKIE}=dark"})
    check("后续请求携带 → 渲染 dark", status == 200 and "当前主题：<b>dark</b>" in body, f"status={status}")

    status, _, body = request("GET", "/lab/preferences", headers={"Cookie": f"{COOKIE}=neon"})
    check("未知值回退 light（不被严格枚举拦截）", status == 200 and "当前主题：<b>light</b>" in body, f"status={status}")

    status, _, _ = request("POST", "/lab/preferences",
                           headers={"Content-Type": "application/x-www-form-urlencoded"},
                           data=urlencode({"theme": "neon"}).encode())
    check("非法设置 theme=neon → 422", status == 422, f"status={status}")

    status, headers, _ = request("POST", "/lab/preferences/reset")
    sc = set_cookie_headers(headers).lower()
    check("重置 303 且下发删除 Cookie", status == 303 and COOKIE in sc and ("max-age=0" in sc or "expires=" in sc), f"status={status} sc={sc}")


def main():
    global BASE, TIMEOUT
    parser = argparse.ArgumentParser(description="HTTP 隔离实验黑盒自检")
    parser.add_argument("--base-url", default=BASE)
    parser.add_argument("--timeout", type=float, default=TIMEOUT)
    args = parser.parse_args()
    BASE = args.base_url.rstrip("/")
    TIMEOUT = args.timeout

    group_params()
    group_nested()
    group_uploads()
    group_cookie()

    passed = sum(1 for _, ok, _ in _results if ok)
    total = len(_results)
    print(f"\n{passed}/{total} 通过")
    if passed != total:
        print("失败项：")
        for name, ok, detail in _results:
            if not ok:
                print(f"  - {name}（{detail}）")
    raise SystemExit(0 if passed == total else 1)


if __name__ == "__main__":
    main()
