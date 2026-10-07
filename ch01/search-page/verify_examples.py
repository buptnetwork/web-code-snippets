"""教师设施：真实回环 HTTP 验证第 2 课起点包；不要求学生解释或编写本文件。

覆盖：搜索契约（空/react/无匹配）、详情与 404、参数 422、静态同源页面、
六种故障模式、有界延迟、复位、种子幂等与搜索规则、参考页源码结构、调试配置。
运行（包根，已激活本包环境）：
    python verify_examples.py
"""

import importlib
import importlib.metadata
import json
from contextlib import contextmanager
import os
from pathlib import Path
import socket
import subprocess
import sys
import tempfile
import time
import unittest
from urllib.error import HTTPError
from urllib.request import ProxyHandler, Request, build_opener

from check_page import (
    ALL_RECORDS,
    RECORD_3,
    NoRedirect,
    check,
    fetch,
    fetch_json,
    same_json,
)

ROOT = Path(__file__).resolve().parent


def code_only(text):
    """丢弃整行 // 注释，只对实际代码做断言（注释里允许出现示例措辞）。"""
    return "\n".join(line for line in text.splitlines() if not line.lstrip().startswith("//"))


def _opener():
    return build_opener(ProxyHandler({}), NoRedirect())


def post_fault(base, mode, timeout=3):
    data = json.dumps({"mode": mode}).encode("utf-8")
    request = Request(
        base + "/__teacher/fault",
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with _opener().open(request, timeout=timeout) as response:
            return response.status, json.loads(response.read())
    except HTTPError as exc:
        return exc.code, None


@contextmanager
def server(**extra_env):
    """在包根启动 server:app 子进程；用临时 DB，探测 /healthz 就绪后交回 base。"""
    with socket.socket() as reservation:
        reservation.bind(("127.0.0.1", 0))
        port = reservation.getsockname()[1]
    base = f"http://127.0.0.1:{port}"
    with tempfile.TemporaryDirectory(prefix="search-page-") as temporary:
        db_path = Path(temporary) / "questions.db"
        log_path = Path(temporary) / "server.log"
        env = {**os.environ, "PYTHONUNBUFFERED": "1", "DB_PATH": str(db_path), **extra_env}
        with log_path.open("w", encoding="utf-8") as output:
            process = subprocess.Popen(
                [sys.executable, "-m", "uvicorn", "server:app", "--host", "127.0.0.1", "--port", str(port)],
                cwd=ROOT,
                env=env,
                stdout=output,
                stderr=subprocess.STDOUT,
            )
            try:
                for _ in range(150):
                    if process.poll() is not None:
                        raise RuntimeError(log_path.read_text(encoding="utf-8"))
                    try:
                        if fetch(base, "/healthz", 0.3)[0] == 200:
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


class SearchContractTests(unittest.TestCase):
    def test_self_check_all_pass(self):
        with server() as (base, _):
            self.assertEqual(check(base, emit=lambda _: None), 0)
            result = subprocess.run(
                [sys.executable, str(ROOT / "check_page.py"), "--base-url", base],
                capture_output=True, text=True, timeout=40,
            )
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertIn("11/11", result.stdout)

    def test_search_shapes(self):
        with server() as (base, _):
            self.assertEqual(fetch_json(base, "/questions?keyword=&page=1&page_size=20")[2]["items"], ALL_RECORDS)
            body = fetch_json(base, "/questions?keyword=react&page=1&page_size=20")[2]
            self.assertEqual(body, {"items": [RECORD_3], "total": 1, "page": 1})
            empty = fetch_json(base, "/questions?keyword=zzzz-no-match")[2]
            self.assertEqual(empty["items"], [])
            self.assertEqual(empty["total"], 0)

    def test_detail_health_and_422(self):
        with server() as (base, _):
            self.assertEqual(fetch_json(base, "/questions/3")[2], RECORD_3)
            self.assertEqual(fetch_json(base, "/questions/999"), (404, "application/json", {"detail": "问题不存在"}))
            self.assertEqual(fetch_json(base, "/questions/abc")[0], 422)
            self.assertEqual(fetch_json(base, "/questions?page=0")[0], 422)
            self.assertEqual(fetch_json(base, "/questions?page_size=100")[0], 422)
            self.assertEqual(fetch_json(base, "/healthz"), (200, "application/json", {"status": "ok"}))

    def test_same_origin_static(self):
        with server() as (base, _):
            status, media, raw = fetch(base, "/")
            text = raw.decode("utf-8")
            self.assertEqual((status, media), (200, "text/html"))
            self.assertIn('id="search-form"', text)
            self.assertIn("/static/app.js", text)
            js_status, js_media, js_raw = fetch(base, "/static/app.js")
            self.assertEqual(js_status, 200)
            self.assertIn("javascript", js_media)
            self.assertIn("readQuestions", js_raw.decode("utf-8"))
            # 预测实验页同源可访问
            p_status, p_media, p_raw = fetch(base, "/experiments/predict/")
            self.assertEqual((p_status, p_media), (200, "text/html"))
            self.assertIn("predict.js", p_raw.decode("utf-8"))


class FaultModeTests(unittest.TestCase):
    def test_fault_modes(self):
        with server() as (base, _):
            expectations = {
                "http500_json": (500, "application/json"),
                "http500_html": (500, "text/html"),
                "json200_html": (200, "text/html"),
                "struct200": (200, "application/json"),
            }
            for mode, (want_status, want_media) in expectations.items():
                with self.subTest(mode=mode):
                    self.assertEqual(post_fault(base, mode)[0], 200)
                    status, media, raw = fetch(base, "/questions?keyword=react")
                    self.assertEqual(status, want_status)
                    self.assertEqual(media, want_media)
                    if mode == "struct200":
                        self.assertEqual(json.loads(raw), {"items": None})
                    if mode == "http500_json":
                        self.assertIn("detail", json.loads(raw))
                    # 每种子测试后复位
                    self.assertEqual(post_fault(base, "normal")[0], 200)
                    self.assertEqual(fetch_json(base, "/questions?keyword=react")[2]["total"], 1)

    def test_invalid_fault_is_422(self):
        with server() as (base, _):
            self.assertEqual(post_fault(base, "not-a-mode")[0], 422)

    def test_delay_is_bounded_then_normal(self):
        with server(DELAY_SECONDS="0.4") as (base, _):
            self.assertEqual(post_fault(base, "delay")[0], 200)
            started = time.monotonic()
            status, media, raw = fetch(base, "/questions?keyword=react", timeout=5)
            elapsed = time.monotonic() - started
            self.assertEqual((status, media), (200, "application/json"))
            self.assertGreaterEqual(elapsed, 0.35)
            self.assertEqual(json.loads(raw)["total"], 1)
            post_fault(base, "normal")

    def test_env_fault_mode_at_startup(self):
        with server(FAULT_MODE="struct200") as (base, _):
            status, media, raw = fetch(base, "/questions?keyword=react")
            self.assertEqual((status, media), (200, "application/json"))
            self.assertEqual(json.loads(raw), {"items": None})


class StoreTests(unittest.TestCase):
    def test_seeding_idempotent_and_rules(self):
        with tempfile.TemporaryDirectory() as temporary:
            os.environ["DB_PATH"] = str(Path(temporary) / "q.db")
            store = importlib.reload(importlib.import_module("question_store"))
            try:
                store.init_db()
                store.init_db()  # 幂等：不应重复插入
                items, total = store.search("", 1, 20)
                self.assertEqual(total, 3)
                self.assertEqual([i["id"] for i in items], [3, 2, 1])
                # 英文不区分大小写
                self.assertEqual(store.search("REACT", 1, 20)[1], 1)
                # 正文子串匹配
                self.assertEqual(store.search("组件", 1, 20)[1], 1)
                # % 与 _ 不作通配符
                self.assertEqual(store.search("%", 1, 20)[1], 0)
                self.assertEqual(store.search("_", 1, 20)[1], 0)
                # 分页：total 为分页前总数，第二页取剩余
                page_items, page_total = store.search("", 2, 2)
                self.assertEqual(page_total, 3)
                self.assertEqual([i["id"] for i in page_items], [1])
                # 详情
                self.assertEqual(store.get_by_id(3), RECORD_3)
                self.assertIsNone(store.get_by_id(999))
            finally:
                os.environ.pop("DB_PATH", None)
                importlib.reload(importlib.import_module("question_store"))


class FrontendSourceTests(unittest.TestCase):
    def test_reference_has_four_state(self):
        ref = (ROOT / "reference" / "app.js").read_text(encoding="utf-8")
        for token in ("setState", "loadQuestions", "finally", "busy", "textContent"):
            self.assertIn(token, ref)
        # 最终只保留一个提交监听器
        self.assertEqual(ref.count("addEventListener('submit'"), 1)
        # 渲染用文本节点，不用 innerHTML
        self.assertNotIn("innerHTML", ref)

    def test_student_start_is_minimal(self):
        student = (ROOT / "static" / "app.js").read_text(encoding="utf-8")
        self.assertIn("region task", student)
        self.assertIn("readQuestions", student)
        self.assertIn("renderQuestions", student)
        # 起点包不预置四态答案（只看代码，注释里允许提示函数名）
        code = code_only(student)
        self.assertNotIn("loadQuestions", code)
        self.assertNotIn("setState", code)

    def test_predict_snippet_has_no_ok_check(self):
        predict = (ROOT / "experiments" / "predict" / "predict.js").read_text(encoding="utf-8")
        self.assertIn("已完成 JSON 解析", predict)
        self.assertIn("进入 catch", predict)
        self.assertNotIn(".ok", code_only(predict))  # 代码故意不检查 res.ok


class ConfigTests(unittest.TestCase):
    def test_launch_config(self):
        config = json.loads((ROOT / ".vscode" / "launch.json").read_text(encoding="utf-8"))
        for item in config["configurations"]:
            self.assertEqual(item["module"], "uvicorn")
            self.assertNotIn("--reload", item["args"])
            self.assertNotIn("python", item)
            cwd = ROOT / item["cwd"].replace("${workspaceFolder}", "").strip("/")
            self.assertTrue((cwd / "server.py").is_file())


if __name__ == "__main__":
    print("Python", sys.version.split()[0], flush=True)
    for package in ("fastapi", "starlette", "uvicorn", "pydantic", "debugpy"):
        print(package, importlib.metadata.version(package), flush=True)
    unittest.main(verbosity=2)
