"""采集可复演证据：真实 HTTP、并发日志、debugpy 停点栈与 SQL。

只启动本脚本的回环服务，使用专属 .capture/demo.db；不连接既有数据库。
调试素材来自 DAP 的 stackTrace/variables，不是 VS Code 界面截图或录像。
"""
import asyncio
from concurrent.futures import ThreadPoolExecutor
from contextlib import contextmanager
from datetime import datetime, timezone
import importlib.metadata
import json
import os
from pathlib import Path
import socket
import subprocess
import sys
import time

import httpx
from seed import seed_database

HERE = Path(__file__).resolve().parent
WORK = HERE / ".capture"
OUTPUT = HERE.parents[2] / "public" / "images" / "ch01" / "evidence.json"


def free_port():
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        return sock.getsockname()[1]


def wait_http(port, process):
    with httpx.Client(trust_env=False, timeout=1) as client:
        for _ in range(150):
            if process.poll() is not None:
                raise RuntimeError("演示进程提前退出，请查看 .capture 中的输出")
            try:
                if client.get(f"http://127.0.0.1:{port}/openapi.json").status_code == 200:
                    return
            except httpx.HTTPError:
                pass
            time.sleep(.1)
    raise TimeoutError("演示服务未就绪")


@contextmanager
def server(mode, debug=False):
    port, debug_port = free_port(), free_port()
    logfile = WORK / f"{mode}.log"
    env = {**os.environ, "DATABASE_URL": f"sqlite:///{WORK / 'demo.db'}",
           "LOG_FILE": str(logfile), "TRACE_MODE": "plain" if mode == "plain" else "trace",
           "DEMO_DELAY_MS": "0" if debug else "80", "SQL_ECHO": "1" if debug else "0"}
    command = [sys.executable]
    if debug:
        command += ["-m", "debugpy", "--listen", f"127.0.0.1:{debug_port}", "--wait-for-client"]
    command += ["-m", "uvicorn", "v2_traceable:app", "--host", "127.0.0.1", "--port", str(port)]
    with (WORK / f"{mode}-process.log").open("w") as output:
        process = subprocess.Popen(command, cwd=HERE, env=env, stdout=output, stderr=subprocess.STDOUT)
        try:
            if not debug:
                wait_http(port, process)
            yield port, debug_port, process, logfile
        finally:
            process.terminate()
            try:
                process.wait(timeout=8)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait(timeout=3)


async def concurrent_requests(port):
    async with httpx.AsyncClient(base_url=f"http://127.0.0.1:{port}", trust_env=False, timeout=4) as client:
        async def send(rid):
            result = await client.post("/getQuestions", params={"keyword": "react"}, headers={"X-Request-ID": rid})
            result.raise_for_status()
            assert len(result.json()["data"]) == 6
        start = time.perf_counter()
        await asyncio.gather(*(send(f"noise-{i:02d}") for i in range(10)), send("stu-demo-01"))
        return round(time.perf_counter() - start, 3)


class DebugClient:
    def __init__(self, port):
        for _ in range(100):
            try:
                self.sock = socket.create_connection(("127.0.0.1", port), timeout=5)
                break
            except OSError:
                time.sleep(.1)
        else:
            raise TimeoutError("debugpy 未启动")
        self.stream = self.sock.makefile("rb")
        self.seq = 0
        self.pending = []

    def send(self, command, arguments):
        self.seq += 1
        body = json.dumps({"seq": self.seq, "type": "request", "command": command, "arguments": arguments}).encode()
        self.sock.sendall(f"Content-Length: {len(body)}\r\n\r\n".encode() + body)
        return self.seq

    def wait(self, predicate):
        for index, item in enumerate(self.pending):
            if predicate(item):
                return self.pending.pop(index)
        while True:
            length = 0
            while True:
                line = self.stream.readline()
                if not line:
                    raise ConnectionError("调试连接断开")
                if line == b"\r\n":
                    break
                if line.lower().startswith(b"content-length:"):
                    length = int(line.split(b":", 1)[1])
            message = json.loads(self.stream.read(length))
            if predicate(message):
                return message
            self.pending.append(message)

    def request(self, command, arguments):
        seq = self.send(command, arguments)
        response = self.wait(lambda item: item.get("request_seq") == seq)
        if not response.get("success"):
            raise RuntimeError(response)
        return response.get("body", {})

    def close(self):
        self.stream.close()
        self.sock.close()


def collect():
    WORK.mkdir(exist_ok=True)
    seed_database(f"sqlite:///{WORK / 'demo.db'}", reset=True)
    evidence = {"captured_at": datetime.now(timezone.utc).isoformat(),
                "python": sys.version.split()[0], "database": "SQLite，固定 50 行虚构数据",
                "versions": {name: importlib.metadata.version(name) for name in ("fastapi", "starlette", "sqlalchemy", "uvicorn", "debugpy")},
                "limits": ["调试栈来自 debugpy DAP，不是 IDE 截图", "并发实验含人为 80ms 延迟，不是性能基准", "四处合流另采单次请求，暂停并发", "PostgreSQL、IDE 录像与教室投影未验证"]}
    for mode in ("plain", "trace"):
        with server(mode) as (port, _, _, logfile):
            elapsed = asyncio.run(concurrent_requests(port))
            evidence[mode] = {"seconds": elapsed, "requests": 11, "log": logfile.read_text()}
    trace = evidence["trace"]["log"].splitlines()
    evidence["filtered"] = "\n".join(line for line in trace if "[stu-demo-01]" in line)
    assert len(evidence["filtered"].splitlines()) == 6

    with server("joined", debug=True) as (port, debug_port, process, logfile):
        debugger = DebugClient(debug_port)
        try:
            debugger.request("initialize", {"adapterID": "python", "clientID": "m0-evidence", "linesStartAt1": True, "columnsStartAt1": True, "pathFormat": "path"})
            attach_seq = debugger.send("attach", {"justMyCode": False})
            debugger.wait(lambda item: item.get("event") == "initialized")
            source = HERE / "v2_traceable.py"
            line = next(index for index, value in enumerate(source.read_text().splitlines(), 1) if "rows = conn.execute" in value)
            debugger.request("setBreakpoints", {"source": {"path": str(source)}, "breakpoints": [{"line": line}]})
            debugger.request("configurationDone", {})
            debugger.wait(lambda item: item.get("request_seq") == attach_seq)
            wait_http(port, process)
            with ThreadPoolExecutor(max_workers=1) as pool:
                future = pool.submit(httpx.post, f"http://127.0.0.1:{port}/getQuestions?keyword=react",
                                     headers={"X-Request-ID": "stu-demo-01"}, timeout=30, trust_env=False)
                stopped = debugger.wait(lambda item: item.get("event") == "stopped")
                tid = stopped["body"]["threadId"]
                frames = debugger.request("stackTrace", {"threadId": tid})["stackFrames"]
                scopes = debugger.request("scopes", {"frameId": frames[0]["id"]})["scopes"]
                locals_scope = next(scope for scope in scopes if scope.get("presentationHint") == "locals" or scope["name"] == "Locals")
                variables = debugger.request("variables", {"variablesReference": locals_scope["variablesReference"]})["variables"]
                selected = {item["name"]: item["value"] for item in variables if item["name"] in {"rid", "keyword", "page"}}
                assert "stu-demo-01" in selected["rid"]
                clean_frames = [{"name": frame["name"], "file": Path(frame.get("source", {}).get("path", "unknown")).name, "line": frame["line"]} for frame in frames]
                # 多行表达式可能再次命中同一源码行，取证后先移除断点。
                debugger.request("setBreakpoints", {"source": {"path": str(source)}, "breakpoints": []})
                debugger.request("continue", {"threadId": tid})
                response = future.result(timeout=10)
                assert response.status_code == 200 and response.headers["x-request-id"] == "stu-demo-01"
            evidence["joined"] = {"request": "POST /getQuestions?keyword=react", "rid": "stu-demo-01",
                                  "status": response.status_code, "http_version": response.http_version,
                                  "headers": dict(response.headers), "body": response.json(),
                                  "stack": clean_frames, "variables": selected,
                                  "log": logfile.read_text(), "stack_source": "debugpy DAP stackTrace + variables，实际断点采集"}
        finally:
            debugger.close()
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(evidence, ensure_ascii=False, indent=2) + "\n")
    print(f"已采集：{OUTPUT}")
    print(f"并发 10+1：plain={evidence['plain']['seconds']}s，trace={evidence['trace']['seconds']}s")
    print("实际栈帧：", [frame["name"] for frame in evidence["joined"]["stack"]])


if __name__ == "__main__":
    collect()
