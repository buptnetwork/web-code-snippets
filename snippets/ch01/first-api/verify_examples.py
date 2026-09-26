"""教师设施：真实回环 HTTP 验证；不要求学生解释或编写本文件。"""

import argparse
from contextlib import contextmanager
import importlib.metadata
import json
import os
from pathlib import Path
import socket
import subprocess
import sys
import tempfile
import time
import unittest

from check_m0 import EXPECTED, check, fetch, local_base_url, positive_timeout, same_json

ROOT = Path(__file__).resolve().parent


@contextmanager
def server(directory, **extra_env):
    with socket.socket() as reservation:
        reservation.bind(("127.0.0.1", 0))
        port = reservation.getsockname()[1]
    base = f"http://127.0.0.1:{port}"
    with tempfile.TemporaryDirectory(prefix="first-api-log-") as temporary:
        log_path = Path(temporary) / "server.log"
        with log_path.open("w", encoding="utf-8") as output:
            process = subprocess.Popen(
                [sys.executable, "-m", "uvicorn", "main:app", "--host", "127.0.0.1", "--port", str(port)],
                cwd=directory,
                env={**os.environ, "PYTHONUNBUFFERED": "1", **extra_env},
                stdout=output,
                stderr=subprocess.STDOUT,
            )
            try:
                for _ in range(100):
                    if process.poll() is not None:
                        raise RuntimeError(log_path.read_text(encoding="utf-8"))
                    try:
                        if fetch(base, "/openapi.json", 0.2)[0] == 200:
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


class ExampleTests(unittest.TestCase):
    def test_reference_and_cli(self):
        with server(ROOT / "reference") as (base, _):
            self.assertEqual(check(base), 0)
            result = subprocess.run(
                [sys.executable, str(ROOT / "check_m0.py"), "--base-url", base],
                capture_output=True, text=True, timeout=40,
            )
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertIn("10/10", result.stdout)

    def test_starter(self):
        with server(ROOT / "starter") as (base, _):
            self.assertEqual(fetch(base, "/questions"), (200, "application/json", {"items": EXPECTED}))
            self.assertEqual(fetch(base, "/questions/3")[0], 404)

    def test_skeleton_fails(self):
        with server(ROOT / "exercise") as (base, _):
            self.assertEqual(fetch(base, "/questions/3"), (200, "application/json", None))
            self.assertGreater(check(base, emit=lambda _: None), 0)
            result = subprocess.run(
                [sys.executable, str(ROOT / "check_m0.py"), "--base-url", base],
                capture_output=True, text=True, timeout=40,
            )
            self.assertEqual(result.returncode, 1)

    def test_untyped_string_at_entry(self):
        with server(ROOT / "experiments/untyped") as (base, log):
            self.assertEqual(fetch(base, "/questions/3")[0], 404)
            self.assertIn("qid = 3 类型 = str", log.read_text(encoding="utf-8"))

    def test_typed_entry_and_pre_endpoint_failures(self):
        with server(ROOT / "reference") as (base, log):
            self.assertEqual(fetch(base, "/questions/3")[2], EXPECTED[0])
            self.assertEqual(fetch(base, "/questions/999")[0], 404)
            self.assertEqual(fetch(base, "/questions/abc")[0], 422)
            self.assertEqual(fetch(base, "/not-a-route")[0], 404)
            lines = [line for line in log.read_text(encoding="utf-8").splitlines() if "收到详情请求" in line]
            self.assertEqual(lines, [
                "收到详情请求，qid = 3 类型 = int",
                "收到详情请求，qid = 999 类型 = int",
            ])

    def test_missing_null_and_empty_are_200_but_fail_m0(self):
        for mode, expected in (("null", None), ("empty", {})):
            with self.subTest(mode=mode), server(ROOT / "experiments/missing", MISSING_RETURN=mode) as (base, _):
                self.assertEqual(fetch(base, "/questions/999"), (200, "application/json", expected))
                self.assertEqual(fetch(base, "/questions/1")[2], EXPECTED[2])
                self.assertEqual(check(base, emit=lambda _: None), 3)

    def test_hardcoded_detail_is_detected(self):
        source = (ROOT / "reference/main.py").read_text(encoding="utf-8")
        # 教师在隔离副本里构造缺陷，不修改参考答案或学生文件。
        source = source.replace('if question["id"] == qid:', 'if question["id"] == 3:')
        with tempfile.TemporaryDirectory(prefix="first-api-hardcoded-") as temporary:
            (Path(temporary) / "main.py").write_text(source, encoding="utf-8")
            with server(temporary) as (base, _):
                self.assertEqual(fetch(base, "/questions/3")[2], EXPECTED[0])
                self.assertGreater(check(base, emit=lambda _: None), 0)

    def test_edit_restart_restore(self):
        source = (ROOT / "starter/main.py").read_text(encoding="utf-8")
        with tempfile.TemporaryDirectory(prefix="first-api-restart-") as temporary:
            path = Path(temporary) / "main.py"
            path.write_text(source, encoding="utf-8")
            with server(temporary) as (base, _):
                self.assertEqual(fetch(base, "/questions")[2]["items"][0]["title"], EXPECTED[0]["title"])
                path.write_text(source.replace("React 的 props 是什么？", "React 的 props 如何传递？"), encoding="utf-8")
                self.assertEqual(fetch(base, "/questions")[2]["items"][0]["title"], EXPECTED[0]["title"])
            with server(temporary) as (base, _):
                self.assertEqual(fetch(base, "/questions")[2]["items"][0]["title"], "React 的 props 如何传递？")
            path.write_text(source, encoding="utf-8")
            with server(temporary) as (base, _):
                self.assertEqual(fetch(base, "/questions")[2]["items"], EXPECTED)

    def test_checker_boundaries(self):
        self.assertTrue(same_json({"a": 1, "b": 2}, {"b": 2, "a": 1}))
        self.assertFalse(same_json({"id": True}, {"id": 1}))
        self.assertFalse(same_json({"id": 1.0}, {"id": 1}))
        self.assertEqual(local_base_url("http://127.0.0.1:8000/"), "http://127.0.0.1:8000")
        for value in ("https://example.com", "http://127.0.0.1:8000/a", "http://user@localhost:8000", "http://localhost:0"):
            with self.assertRaises(argparse.ArgumentTypeError):
                local_base_url(value)
        for value in ("nan", "inf", "0", "31"):
            with self.assertRaises(argparse.ArgumentTypeError):
                positive_timeout(value)

    def test_launch_config(self):
        config = json.loads((ROOT / ".vscode/launch.json").read_text(encoding="utf-8"))
        for item in config["configurations"]:
            self.assertEqual(item["module"], "uvicorn")
            self.assertNotIn("--reload", item["args"])
            self.assertNotIn("python", item)
            cwd = ROOT / item["cwd"].removeprefix("${workspaceFolder}/")
            self.assertTrue((cwd / "main.py").is_file())


if __name__ == "__main__":
    print("Python", sys.version.split()[0], flush=True)
    for package in ("fastapi", "starlette", "uvicorn", "debugpy"):
        print(package, importlib.metadata.version(package), flush=True)
    unittest.main(verbosity=2)
