"""一个 40 行的最小服务端，只为课前课演示 HTTP 报文，不是本课程的技术栈。

它会把你发来的请求头原样回显，方便你看清 curl 和浏览器各自替你发了什么。

运行： uv run python snippets/lesson00/demo_server.py
"""
import json
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, HTTPServer


class DemoHandler(BaseHTTPRequestHandler):
    server_version = "demo/0.1"

    def _json(self, status: int, payload: dict) -> None:
        body = json.dumps(payload, ensure_ascii=False, indent=2).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("X-Demo-Server", "lesson00")
        self.end_headers()
        self.wfile.write(body)

    # #region do_get
    def do_GET(self):
        if self.path.startswith("/hello"):
            self._json(200, {
                "message": "hello",
                "method": self.command,
                "path": self.path,
                "your_headers": dict(self.headers),   # ← 把你发的请求头退回给你
                "server_time": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            })
        else:
            self._json(404, {"error": "not_found", "path": self.path})
    # #endregion do_get

    def do_POST(self):
        length = int(self.headers.get("Content-Length") or 0)
        raw = self.rfile.read(length).decode("utf-8")
        try:
            data = json.loads(raw) if raw else {}
        except json.JSONDecodeError:
            self._json(400, {"error": "bad_json", "你发的原始文本": raw})
            return
        self._json(201, {"received": data, "body_size": length})


if __name__ == "__main__":
    print("listening on http://127.0.0.1:8000   (Ctrl+C 退出)")
    print("试试： curl -i 'http://127.0.0.1:8000/hello?page=2'")
    HTTPServer(("127.0.0.1", 8000), DemoHandler).serve_forever()
