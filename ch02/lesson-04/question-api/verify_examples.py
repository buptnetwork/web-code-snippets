"""教师设施：真实回环 HTTP 验证第 4 课起点包；不要求学生解释或编写本文件。

覆盖（对应底稿 7.1 验证矩阵）：
- R 阶段 server.py 通过第 3 课 23 项 check_api（契约未变，404/409 仍是 {"detail": ...}）；
- E 阶段 reference/server.py 的四字段 ErrorOut（404/409/422/500 都含 code/message/detail/request_id）；
- request-id 透传与生成、start/end 结构化日志配对；
- healthz：可用 200 ok、数据库不可用 503 degraded；
- 故障：before_commit 500 且无数据、after_commit 500 但数据留存、normal 201；
- 依赖探针：open→use→close、请求内同一连接、yield 退出晚于响应、获取失败仍 close；
- 源码 region 结构与调试配置。
运行（包根，已激活本包环境）：
    python verify_examples.py
"""

import importlib
import importlib.metadata
import json
import os
import socket
import subprocess
import sys
import tempfile
import time
import unittest
from contextlib import contextmanager
from pathlib import Path
from urllib.parse import quote
from urllib.request import ProxyHandler, Request, build_opener

from check_api import (
    ALL_RECORDS,
    RECORD_3,
    NoRedirect,
    check,
    record_fields_ok,
    request,
    same_public,
)

ROOT = Path(__file__).resolve().parent
R_TARGET = "server:app"
E_TARGET = "reference.server:app"
PROBE_TARGET = "experiments.dependency_probe:app"


def _opener():
    return build_opener(ProxyHandler({}), NoRedirect())


@contextmanager
def server(target=E_TARGET, **extra_env):
    """在包根启动 uvicorn 子进程；用临时 DB，探测就绪后交回 (base, log_path)。"""
    with socket.socket() as reservation:
        reservation.bind(("127.0.0.1", 0))
        port = reservation.getsockname()[1]
    base = f"http://127.0.0.1:{port}"
    probe_ready = "/probe" if target.startswith("experiments") else "/healthz"
    with tempfile.TemporaryDirectory(prefix="question-api-l04-") as temporary:
        db_path = Path(temporary) / "questions.db"
        log_path = Path(temporary) / "server.log"
        env = {**os.environ, "PYTHONUNBUFFERED": "1", "DB_PATH": str(db_path), **extra_env}
        with log_path.open("w", encoding="utf-8") as output:
            process = subprocess.Popen(
                [sys.executable, "-m", "uvicorn", target, "--host", "127.0.0.1", "--port", str(port)],
                cwd=ROOT, env=env, stdout=output, stderr=subprocess.STDOUT,
            )
            try:
                for _ in range(200):
                    if process.poll() is not None:
                        raise RuntimeError(log_path.read_text(encoding="utf-8"))
                    try:
                        if request(base, probe_ready, timeout=0.3)[0] in (200, 503):
                            break
                    except (OSError, ValueError):
                        time.sleep(0.05)
                else:
                    raise RuntimeError("教师临时服务未就绪")
                yield base, log_path
            finally:
                process.terminate()
                try:
                    process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    process.kill()
                    process.wait()


def read_log(log_path, retries=20, delay=0.05):
    """日志落盘可能有微小延迟，轮询读取直到内容稳定。"""
    text = ""
    for _ in range(retries):
        text = log_path.read_text(encoding="utf-8")
        if "request_end" in text:
            break
        time.sleep(delay)
    return text


class RStageContractTests(unittest.TestCase):
    """R 阶段只重构资源与职责，第 3 课 23 项契约必须全过。"""

    def test_self_check_all_pass_on_r_stage(self):
        with server(R_TARGET) as (base, _):
            self.assertEqual(check(base, emit=lambda _: None), 0)
            result = subprocess.run(
                [sys.executable, str(ROOT / "check_api.py"), "--base-url", base],
                capture_output=True, text=True, timeout=60,
            )
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertIn("23/23", result.stdout)


class EStageErrorTests(unittest.TestCase):
    """E 阶段统一错误出口：四字段 ErrorOut + request-id。"""

    def _assert_four_field(self, body):
        self.assertIsInstance(body, dict)
        self.assertEqual(set(body), {"code", "message", "detail", "request_id"})

    def test_not_found_404_four_field(self):
        with server() as (base, _):
            status, _, body, headers = request(base, "/questions/999")
            self.assertEqual(status, 404)
            self._assert_four_field(body)
            self.assertEqual(body["code"], "question_not_found")
            self.assertEqual(body["message"], "问题不存在")
            self.assertTrue(body["request_id"])
            self.assertEqual(headers.get("x-request-id"), body["request_id"])

    def test_duplicate_409_four_field(self):
        with server() as (base, _):
            payload = {"title": "回环重复标题样本", "body": "0123456789"}
            self.assertEqual(request(base, "/questions", "POST", payload)[0], 201)
            status, _, body, _ = request(base, "/questions", "POST", payload)
            self.assertEqual(status, 409)
            self._assert_four_field(body)
            self.assertEqual(body["code"], "duplicate_title")
            _, _, listing, _ = request(base, "/questions?keyword=" + quote("回环重复标题样本"))
            self.assertEqual(listing["total"], 1)

    def test_validation_422_four_field(self):
        with server() as (base, _):
            status, _, body, _ = request(base, "/questions", "POST", {"title": "abcd", "body": "0123456789"})
            self.assertEqual(status, 422)
            self._assert_four_field(body)
            self.assertEqual(body["code"], "validation_error")
            self.assertIsInstance(body["detail"], list)
            self.assertTrue(any("title" in item["loc"] for item in body["detail"]))

    def test_unhandled_500_four_field_via_fault(self):
        with server() as (base, _):
            payload = {"title": "触发提交前故障的问题", "body": "0123456789"}
            status, _, body, _ = request(base, "/__teacher/fault-create?fault=before_commit", "POST", payload)
            self.assertEqual(status, 500)
            self._assert_four_field(body)
            self.assertEqual(body["code"], "internal_error")
            self.assertNotIn("RuntimeError", json.dumps(body, ensure_ascii=False))

    def test_request_id_passthrough_and_generation(self):
        with server() as (base, _):
            req = Request(base + "/questions/999", headers={"x-request-id": "verify-trace-1"}, method="GET")
            try:
                with _opener().open(req, timeout=3) as response:
                    echoed = response.headers.get("x-request-id")
                    body = json.loads(response.read())
            except Exception as exc:  # HTTPError 也要取头与正文
                echoed = exc.headers.get("x-request-id")
                body = json.loads(exc.read())
            self.assertEqual(echoed, "verify-trace-1")
            self.assertEqual(body["request_id"], "verify-trace-1")
            # 不带 header 时生成一个合法 id
            status, _, gen_body, gen_headers = request(base, "/questions/999")
            self.assertEqual(status, 404)
            self.assertTrue(gen_body["request_id"])
            self.assertEqual(gen_headers.get("x-request-id"), gen_body["request_id"])

    def test_start_end_logs_paired(self):
        with server() as (base, log_path):
            req = Request(base + "/questions/3", headers={"x-request-id": "verify-log-1"}, method="GET")
            with _opener().open(req, timeout=3) as response:
                response.read()
            text = read_log(log_path)
            self.assertIn('"event": "request_start"', text)
            self.assertIn('"event": "request_end"', text)
            self.assertIn('"request_id": "verify-log-1"', text)


class EStageHealthTests(unittest.TestCase):
    def test_healthz_ok(self):
        with server() as (base, _):
            status, _, body, _ = request(base, "/healthz")
            self.assertEqual(status, 200)
            self.assertEqual(body, {"status": "ok"})

    def test_healthz_degraded_503(self):
        # 单元级：让 open_connection 抛 sqlite3.Error，healthz 应返回 degraded + 503 的 JSONResponse。
        import sqlite3
        ref = importlib.import_module("reference.server")
        original = ref.open_connection
        ref.open_connection = lambda: (_ for _ in ()).throw(sqlite3.OperationalError("数据库不可用"))
        try:
            result = ref.healthz()
            self.assertEqual(result.status_code, 503)
            self.assertEqual(json.loads(result.body), {"status": "degraded"})
        finally:
            ref.open_connection = original


class FaultTests(unittest.TestCase):
    """commit 位置决定数据去留：before_commit 无数据、after_commit 数据留存。"""

    def test_before_commit_500_no_data(self):
        with server() as (base, _):
            payload = {"title": "提交前故障唯一标题", "body": "0123456789"}
            status, _, _, _ = request(base, "/__teacher/fault-create?fault=before_commit", "POST", payload)
            self.assertEqual(status, 500)
            _, _, listing, _ = request(base, "/questions?keyword=" + quote("提交前故障唯一标题"))
            self.assertEqual(listing["total"], 0)

    def test_after_commit_500_data_persists(self):
        with server() as (base, _):
            payload = {"title": "提交后故障唯一标题", "body": "0123456789"}
            status, _, _, _ = request(base, "/__teacher/fault-create?fault=after_commit", "POST", payload)
            self.assertEqual(status, 500)
            _, _, listing, _ = request(base, "/questions?keyword=" + quote("提交后故障唯一标题"))
            self.assertEqual(listing["total"], 1)

    def test_normal_fault_201(self):
        with server() as (base, _):
            payload = {"title": "无故障正常创建标题", "body": "0123456789"}
            status, _, body, _ = request(base, "/__teacher/fault-create?fault=normal", "POST", payload)
            self.assertEqual(status, 201)
            self.assertTrue(record_fields_ok(body))


class DependencyProbeTests(unittest.TestCase):
    def test_probe_lifecycle_and_reuse(self):
        with server(PROBE_TARGET) as (base, log_path):
            status, _, body, _ = request(base, "/probe")
            self.assertEqual(status, 200)
            self.assertTrue(body["same_conn"])  # 请求内依赖缓存：同一连接
            text = read_log(log_path)
            order = [line for line in text.splitlines() if "dependency_probe" in line]
            joined = "\n".join(order)
            self.assertLess(joined.index("open"), joined.index("use"))
            self.assertLess(joined.index("use"), joined.index("service-exit"))
            self.assertLess(joined.index("service-exit"), joined.index("close"))

    def test_probe_failure_still_closes(self):
        with server(PROBE_TARGET) as (base, log_path):
            status, _, _, _ = request(base, "/probe-fail")
            self.assertEqual(status, 500)
            text = read_log(log_path)
            self.assertIn("fail-open", text)
            self.assertIn("fail-close", text)


class SourceStructureTests(unittest.TestCase):
    def test_regions_present(self):
        cases = {
            "models.py": ["region out-models", "region create-model", "region error-models", "region response-models"],
            "service.py": ["region create-service", "region get-service"],
            "service_fault.py": ["region fault"],
            "server.py": ["region get-conn", "region list-endpoint", "region write-endpoints"],
            "reference/server.py": ["region error-response", "region register-handlers", "region register-trace",
                                     "region e-write-endpoints", "region healthz", "region make-application"],
            "experiments/dependency_probe.py": ["region probe"],
        }
        for rel, regions in cases.items():
            text = (ROOT / rel).read_text(encoding="utf-8")
            for region in regions:
                self.assertIn(region, text, f"{rel} 缺 {region}")

    def test_r_stage_preserves_detail_contract(self):
        # R 阶段端点仍就地翻译为 HTTPException({"detail": ...})，保持第 3 课契约。
        text = (ROOT / "server.py").read_text(encoding="utf-8")
        self.assertIn('detail="问题不存在"', text)
        self.assertIn('detail="标题已存在"', text)

    def test_e_stage_removes_inline_translation(self):
        # E 阶段端点不再就地翻译，改由统一处理器出口。
        text = (ROOT / "reference" / "server.py").read_text(encoding="utf-8")
        self.assertIn("register_handlers", text)
        self.assertIn("ErrorOut", text)
        self.assertNotIn('detail="问题不存在"', text)

    def test_question_db_unchanged(self):
        # 数据层与第 3 课逐字一致（不改已验收 SQL）。
        l03 = (ROOT.parent.parent / "question-api" / "question_db.py").read_text(encoding="utf-8")
        l04 = (ROOT / "question_db.py").read_text(encoding="utf-8")
        self.assertEqual(l03, l04)


class ConfigTests(unittest.TestCase):
    def test_launch_config(self):
        config = json.loads((ROOT / ".vscode" / "launch.json").read_text(encoding="utf-8"))
        names = [item["module"] for item in config["configurations"]]
        self.assertTrue(all(name == "uvicorn" for name in names))
        for item in config["configurations"]:
            self.assertNotIn("--reload", item["args"])


if __name__ == "__main__":
    print("Python", sys.version.split()[0], flush=True)
    for package in ("fastapi", "starlette", "uvicorn", "pydantic", "debugpy"):
        print(package, importlib.metadata.version(package), flush=True)
    unittest.main(verbosity=2)
