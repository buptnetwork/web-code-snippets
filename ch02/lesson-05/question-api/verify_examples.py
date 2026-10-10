"""教师设施：真实回环 HTTP 验证第 5 课起点包；不要求学生解释或编写本文件。

覆盖（对应底稿 6.2 M1 验收与 §九制作状态）：
- reference.ssr:app 通过 check_ssr 全部 16 项（三页导航、三字段回填、303/PRG、409、JSON 回归、探针）；
- api:app 的 JSON 基线：四字段 404、201 + Location、healthz 未退化；
- 源码 region 结构与模板标记，逐字复制的模型／服务／数据层与第 4 课一致，api.py 的 ROOT 为单层 parent；
- 调试配置：三条 uvicorn、无 --reload、wait_lab 单 worker；
- 可选 --wait：启动 wait_lab 子进程，用 concurrency 核对 awaiting/threaded 并发 10 重叠、blocking 不重叠。
运行（包根，已激活本包环境）：
    python verify_examples.py
    python verify_examples.py --wait
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

import concurrency
from check_ssr import NoRedirect, check, count_via_json, get, post_form, post_json

ROOT = Path(__file__).resolve().parent
SSR_TARGET = "ssr:app"
REFERENCE_TARGET = "reference.ssr:app"
API_TARGET = "api:app"
WAIT_TARGET = "wait_lab:app"
RUN_WAIT = "--wait" in sys.argv


def _opener():
    return build_opener(ProxyHandler({}), NoRedirect())


def _probe(base, target, timeout):
    """就绪探针：wait_lab 的 /lab/* 都会 sleep 1s，改探根路径（拿到任意响应含 404 即已就绪）；其余用 /healthz（200 或 503）。"""
    if target.startswith("wait_lab"):
        get(base, "/", timeout)   # 连接被拒会抛 OSError，交由上层重试；能返回即说明 uvicorn 已在服务
        return True
    return get(base, "/healthz", timeout)[0] in (200, 503)


@contextmanager
def server(target=REFERENCE_TARGET, **extra_env):
    """在包根启动 uvicorn 子进程；用临时 DB，探测就绪后交回 (base, log_path)。"""
    with socket.socket() as reservation:
        reservation.bind(("127.0.0.1", 0))
        port = reservation.getsockname()[1]
    base = f"http://127.0.0.1:{port}"
    extra_args = ["--workers", "1"] if target.startswith("wait_lab") else []
    with tempfile.TemporaryDirectory(prefix="question-api-l05-") as temporary:
        db_path = Path(temporary) / "questions.db"
        log_path = Path(temporary) / "server.log"
        env = {**os.environ, "PYTHONUNBUFFERED": "1", "DB_PATH": str(db_path), **extra_env}
        with log_path.open("w", encoding="utf-8") as output:
            process = subprocess.Popen(
                [sys.executable, "-m", "uvicorn", target, "--host", "127.0.0.1", "--port", str(port), *extra_args],
                cwd=ROOT, env=env, stdout=output, stderr=subprocess.STDOUT,
            )
            try:
                for _ in range(200):
                    if process.poll() is not None:
                        raise RuntimeError(log_path.read_text(encoding="utf-8"))
                    try:
                        if _probe(base, target, 0.3):
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


class SSRContractTests(unittest.TestCase):
    """reference.ssr:app 应通过学生自检的全部 M1 用例。"""

    def test_check_ssr_all_pass_on_reference(self):
        with server(REFERENCE_TARGET) as (base, _):
            self.assertEqual(check(base, emit=lambda _: None), 0)
            result = subprocess.run(
                [sys.executable, str(ROOT / "check_ssr.py"), "--base-url", base],
                capture_output=True, text=True, timeout=120,
            )
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertIn("16/16", result.stdout)

    def test_student_stub_is_incomplete(self):
        # 学生工作文件在补齐前：三字段非法提交因 render_validation_failure 未实现而落到安全 500，
        # 但列表/详情骨架仍能 200 渲染（不是崩溃），确认任务壳可运行、待补齐。
        with server(SSR_TARGET) as (base, _):
            status, media, _, _ = post_form(
                base, "/ui/questions",
                {"title": "  x  ", "body": "  short  ", "tags": "a,b,c,d,e,f"})
            self.assertEqual(status, 500)
            self.assertTrue((media or "").startswith("text/html"))
            self.assertEqual(get(base, "/ui/questions")[0], 200)


class JSONBaselineTests(unittest.TestCase):
    """api:app 的 JSON 基线（不挂 HTML 路由）契约未退化。"""

    def test_four_field_404(self):
        with server(API_TARGET) as (base, _):
            status, media, text, headers = get(base, "/questions/999")
            self.assertEqual(status, 404)
            self.assertEqual(media, "application/json")
            body = json.loads(text)
            self.assertEqual(set(body), {"code", "message", "detail", "request_id"})
            self.assertEqual(body["code"], "question_not_found")
            self.assertEqual(headers.get("x-request-id"), body["request_id"])

    def test_create_201_and_healthz(self):
        with server(API_TARGET) as (base, _):
            payload = {"title": "JSON 基线合法标题", "body": "0123456789"}
            status, _, body, headers = post_json(base, "/questions", payload)
            self.assertEqual(status, 201)
            self.assertTrue((headers.get("Location") or "").startswith("/questions/"))
            self.assertEqual(count_via_json(base, "JSON 基线合法标题"), 1)
            self.assertEqual(json.loads(get(base, "/healthz")[2]), {"status": "ok"})


@unittest.skipUnless(RUN_WAIT, "并发机制核对较慢，仅在 --wait 时运行")
class WaitLabTests(unittest.TestCase):
    """单 worker 真实 HTTP：awaiting/threaded 并发 10 重叠、blocking 不重叠。"""

    def test_overlap_pattern(self):
        with server(WAIT_TARGET) as (base, _):
            awaiting_serial = concurrency.run_group(base, "awaiting", 1, 10, 30)
            awaiting_concurrent = concurrency.run_group(base, "awaiting", 10, 10, 30)
            blocking_concurrent = concurrency.run_group(base, "blocking", 10, 10, 30)
            threaded_concurrent = concurrency.run_group(base, "threaded", 10, 10, 30)
            for row in (awaiting_serial, awaiting_concurrent, blocking_concurrent, threaded_concurrent):
                self.assertEqual(row["success"], 10, row)
            self.assertGreater(awaiting_serial["duration_s"], 8)      # 顺序约 10 秒
            self.assertLess(awaiting_concurrent["duration_s"], 3)     # 可挂起重叠约 1 秒
            self.assertGreater(blocking_concurrent["duration_s"], 8)  # 阻塞事件循环不重叠
            self.assertLess(threaded_concurrent["duration_s"], 3)     # 线程池重叠约 1 秒


class SourceStructureTests(unittest.TestCase):
    def test_python_regions_present(self):
        cases = {
            "ssr.py": ["region templates-entry", "region read-form", "region submit-endpoint",
                       "region task", "region read-routes", "region html-error", "region make-ssr"],
            "reference/ssr.py": ["region templates-entry", "region validation-failure",
                                 "region read-routes", "region html-error", "region make-ssr"],
            "api.py": ["region register-handlers", "region register-trace", "region make-application"],
            "wait_lab.py": ["region make-wait-lab"],
            "models.py": ["region out-models", "region create-model", "region error-models", "region response-models"],
            "service.py": ["region create-service", "region get-service"],
            "service_fault.py": ["region fault"],
        }
        for rel, regions in cases.items():
            text = (ROOT / rel).read_text(encoding="utf-8")
            for region in regions:
                self.assertIn(region, text, f"{rel} 缺 {region}")

    def test_template_markers_present(self):
        cases = {
            "templates/base.html": "#region base",
            "templates/question_form.html": "#region form",
            "reference/templates/base.html": "#region base",
            "reference/templates/question_form.html": "#region form",
            "reference/templates/question_list.html": "#region list",
            "reference/templates/question_detail.html": "#region detail",
        }
        for rel, marker in cases.items():
            self.assertIn(marker, (ROOT / rel).read_text(encoding="utf-8"), f"{rel} 缺 {marker}")

    def test_student_task_is_stub_reference_is_complete(self):
        student = (ROOT / "ssr.py").read_text(encoding="utf-8")
        reference = (ROOT / "reference" / "ssr.py").read_text(encoding="utf-8")
        self.assertIn("NotImplementedError", student)
        self.assertNotIn("NotImplementedError", reference)
        self.assertIn('errors.setdefault(field, FIELD_MESSAGES[field])', reference)

    def test_verbatim_copies_match_lesson04(self):
        l04 = ROOT.parent.parent / "lesson-04" / "question-api"
        for name in ("models.py", "question_db.py", "service.py", "service_fault.py"):
            self.assertEqual((l04 / name).read_text(encoding="utf-8"),
                             (ROOT / name).read_text(encoding="utf-8"), f"{name} 应与第 4 课逐字一致")

    def test_api_root_is_single_parent(self):
        text = (ROOT / "api.py").read_text(encoding="utf-8")
        self.assertIn("ROOT = Path(__file__).resolve().parent\n", text)
        self.assertNotIn("ROOT = Path(__file__).resolve().parent.parent", text)


class ConfigTests(unittest.TestCase):
    def test_launch_config(self):
        config = json.loads((ROOT / ".vscode" / "launch.json").read_text(encoding="utf-8"))
        configs = config["configurations"]
        self.assertTrue(all(item["module"] == "uvicorn" for item in configs))
        for item in configs:
            self.assertNotIn("--reload", item["args"])
        targets = {item["args"][0] for item in configs}
        self.assertEqual(targets, {"ssr:app", "reference.ssr:app", "wait_lab:app"})
        wait = next(item for item in configs if item["args"][0] == "wait_lab:app")
        self.assertIn("--workers", wait["args"])
        self.assertEqual(wait["args"][wait["args"].index("--workers") + 1], "1")


if __name__ == "__main__":
    # --wait 是本文件自定义开关（RUN_WAIT 已在导入时读取），须在 unittest 解析参数前移除。
    if "--wait" in sys.argv:
        sys.argv.remove("--wait")
    print("Python", sys.version.split()[0], flush=True)
    for package in ("fastapi", "starlette", "uvicorn", "pydantic", "jinja2", "python-multipart", "markupsafe", "debugpy"):
        try:
            print(package, importlib.metadata.version(package), flush=True)
        except importlib.metadata.PackageNotFoundError:
            print(package, "MISSING", flush=True)
    unittest.main(verbosity=2)
