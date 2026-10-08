"""教师设施：真实回环 HTTP 验证第 3 课起点包；不要求学生解释或编写本文件。

覆盖：完整参考应用的列表／详情／创建契约、三组边界、SQL 字面匹配与注入样本、
四种输出对照模式、种子幂等与升级、起点留白与参考源码结构、调试配置。
默认验证 reference.server:app（完整答案）；学生 server.py 的创建接口在补齐前不通过自检属正常。
运行（包根，已激活本包环境）：
    python verify_examples.py
"""

import importlib
import importlib.metadata
import json
import os
from contextlib import contextmanager
from pathlib import Path
import socket
import subprocess
import sys
import tempfile
import time
import unittest
from urllib.error import HTTPError
from urllib.parse import quote
from urllib.request import ProxyHandler, Request, build_opener

from check_api import (
    ALL_RECORDS,
    RECORD_3,
    NoRedirect,
    check,
    parse_instant,
    record_fields_ok,
    request,
    same_public,
)

ROOT = Path(__file__).resolve().parent


def code_only(text):
    """丢弃整行 # 注释与提示，只对实际代码做断言（注释里允许出现答案措辞）。"""
    return "\n".join(line for line in text.splitlines() if not line.lstrip().startswith("#"))


def _opener():
    return build_opener(ProxyHandler({}), NoRedirect())


@contextmanager
def server(target="reference.server:app", **extra_env):
    """在包根启动 uvicorn 子进程；用临时 DB，探测 /healthz 或 /probe 就绪后交回 base。"""
    with socket.socket() as reservation:
        reservation.bind(("127.0.0.1", 0))
        port = reservation.getsockname()[1]
    base = f"http://127.0.0.1:{port}"
    probe_ready = "/probe" if target.startswith("experiments") else "/healthz"
    with tempfile.TemporaryDirectory(prefix="question-api-") as temporary:
        db_path = Path(temporary) / "questions.db"
        log_path = Path(temporary) / "server.log"
        env = {**os.environ, "PYTHONUNBUFFERED": "1", "DB_PATH": str(db_path), **extra_env}
        with log_path.open("w", encoding="utf-8") as output:
            process = subprocess.Popen(
                [sys.executable, "-m", "uvicorn", target, "--host", "127.0.0.1", "--port", str(port)],
                cwd=ROOT,
                env=env,
                stdout=output,
                stderr=subprocess.STDOUT,
            )
            try:
                for _ in range(200):
                    if process.poll() is not None:
                        raise RuntimeError(log_path.read_text(encoding="utf-8"))
                    try:
                        if request(base, probe_ready, timeout=0.3)[0] in (200, 500):
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


class SelfCheckTests(unittest.TestCase):
    def test_self_check_all_pass_on_reference(self):
        with server() as (base, _):
            self.assertEqual(check(base, emit=lambda _: None), 0)
            result = subprocess.run(
                [sys.executable, str(ROOT / "check_api.py"), "--base-url", base],
                capture_output=True, text=True, timeout=60,
            )
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertIn(f"{23}/{23}", result.stdout)


class ReadContractTests(unittest.TestCase):
    def test_list_shapes(self):
        with server() as (base, _):
            _, _, body, _ = request(base, "/questions?keyword=&page=1&page_size=20")
            self.assertEqual(len(body["items"]), 3)
            self.assertTrue(all(same_public(r, e) for r, e in zip(body["items"], ALL_RECORDS)))
            self.assertTrue(all(record_fields_ok(r) for r in body["items"]))
            self.assertEqual((body["total"], body["page"]), (3, 1))
            _, _, react, _ = request(base, "/questions?keyword=react")
            self.assertEqual([r["id"] for r in react["items"]], [3])
            self.assertEqual(react["total"], 1)
            _, _, empty, _ = request(base, "/questions?keyword=zzzz-no-match")
            self.assertEqual((empty["items"], empty["total"]), ([], 0))
            _, _, page2, _ = request(base, "/questions?page=2&page_size=2")
            self.assertEqual([r["id"] for r in page2["items"]], [1])
            self.assertEqual(page2["total"], 3)

    def test_detail_health_and_422(self):
        with server() as (base, _):
            status, _, body, _ = request(base, "/questions/3")
            self.assertEqual(status, 200)
            self.assertTrue(same_public(body, RECORD_3))
            self.assertTrue(record_fields_ok(body))
            for qid in (999, 0, -1):
                self.assertEqual(request(base, f"/questions/{qid}")[0], 404)
                self.assertEqual(request(base, f"/questions/{qid}")[2], {"detail": "问题不存在"})
            self.assertEqual(request(base, "/questions/abc")[0], 422)
            self.assertEqual(request(base, "/questions?page=0")[0], 422)
            self.assertEqual(request(base, "/questions?page_size=100")[0], 422)
            self.assertEqual(request(base, "/healthz")[2], {"status": "ok"})

    def test_same_origin_page(self):
        with server() as (base, _):
            req = Request(base + "/", headers={"Accept": "*/*"}, method="GET")
            with _opener().open(req, timeout=3) as response:
                text = response.read().decode("utf-8")
                self.assertEqual(response.headers.get_content_type(), "text/html")
            self.assertIn('id="search-form"', text)
            self.assertIn("/static/app.js", text)
            js_status, js_media, _, _ = request(base, "/static/app.js")
            self.assertEqual(js_status, 200)
            self.assertIn("javascript", js_media)


class CreateContractTests(unittest.TestCase):
    def test_create_and_readback(self):
        with server() as (base, _):
            payload = {"title": "回环验证创建的问题", "body": "这是用于回环验证的正文内容。", "tags": ["fastapi"]}
            status, _, body, headers = request(base, "/questions", "POST", payload)
            self.assertEqual(status, 201)
            location = headers.get("Location")
            self.assertTrue(location)
            self.assertTrue(record_fields_ok(body))
            self.assertEqual(body["title"], payload["title"])
            self.assertEqual(body["tags"], ["fastapi"])
            r_status, _, r_body, _ = request(base, location)
            self.assertEqual(r_status, 200)
            self.assertEqual(r_body["id"], body["id"])
            self.assertEqual(r_body["title"], payload["title"])

    def test_strip_and_default_tags(self):
        with server() as (base, _):
            status, _, body, _ = request(base, "/questions", "POST",
                                         {"title": "  两端空白的标题  ", "body": "  0123456789  "})
            self.assertEqual(status, 201)
            self.assertEqual(body["title"], "两端空白的标题")
            self.assertEqual(body["body"], "0123456789")
            status2, _, body2, _ = request(base, "/questions", "POST",
                                           {"title": "省略标签的另一个问题", "body": "0123456789"})
            self.assertEqual(status2, 201)
            self.assertEqual(body2["tags"], [])

    def test_boundaries_422_loc(self):
        with server() as (base, _):
            for payload, loc_tail in (
                ({"title": "abcd", "body": "0123456789"}, "title"),
                ({"title": "合法标题足够长", "body": "012345678"}, "body"),
                ({"title": "合法标题足够长", "body": "0123456789", "tags": ["a", "b", "c", "d", "e", "f"]}, "tags"),
                ({"title": "含额外字段", "body": "0123456789", "id": 999}, None),
                ({"title": "缺少正文"}, None),
                ({"title": "    x", "body": "0123456789"}, None),
            ):
                status, _, body, _ = request(base, "/questions", "POST", payload)
                self.assertEqual(status, 422, payload)
                if loc_tail is not None:
                    detail = body["detail"]
                    self.assertTrue(any(err["loc"][-1] == loc_tail for err in detail), detail)

    def test_duplicate_title_409(self):
        with server() as (base, _):
            payload = {"title": "回环重复标题样本", "body": "0123456789"}
            self.assertEqual(request(base, "/questions", "POST", payload)[0], 201)
            status, _, body, _ = request(base, "/questions", "POST", payload)
            self.assertEqual(status, 409)
            self.assertEqual(body, {"detail": "标题已存在"})
            _, _, listing, _ = request(base, "/questions?keyword=" + quote("回环重复标题样本"))
            self.assertEqual(listing["total"], 1)  # 冲突不新增第二条

    def test_sql_literal_and_injection(self):
        with server() as (base, _):
            # % 与 _ 不作通配符
            self.assertEqual(request(base, "/questions?keyword=%25")[2]["total"], 0)
            self.assertEqual(request(base, "/questions?keyword=_")[2]["total"], 0)
            # 注入样本被当作字面值绑定，不破坏表；随后固定三条仍在
            injection = "'; DROP TABLE questions;--"
            self.assertEqual(request(base, "/questions?keyword=" + quote(injection))[2]["total"], 0)
            _, _, listing, _ = request(base, "/questions?keyword=")
            self.assertEqual(listing["total"], 3)


class OutputProbeTests(unittest.TestCase):
    def test_probe_modes(self):
        expectations = {
            "normal": (200, False),
            "extra": (200, False),
            "direct": (200, True),
            "missing": (500, None),
        }
        for mode, (want_status, note_visible) in expectations.items():
            with self.subTest(mode=mode), server("experiments.output_probe:app", PROBE_MODE=mode) as (base, _):
                status, _, body, _ = request(base, "/probe")
                self.assertEqual(status, want_status)
                if want_status == 200:
                    self.assertEqual("internal_note" in (body or {}), note_visible)
                    if mode != "direct":
                        self.assertTrue(record_fields_ok(body))


class StoreTests(unittest.TestCase):
    def test_seed_idempotent_and_upgrade(self):
        with tempfile.TemporaryDirectory() as temporary:
            os.environ["DB_PATH"] = str(Path(temporary) / "q.db")
            db = importlib.reload(importlib.import_module("question_db"))
            try:
                db.init_db()
                db.init_db()  # 幂等：不应重复插入
                from contextlib import closing
                with closing(db.open_connection()) as conn:
                    result = db.search_questions(conn, "", 1, 20)
                    self.assertEqual(result["total"], 3)
                    self.assertEqual([r["id"] for r in result["items"]], [3, 2, 1])
                    self.assertTrue(all(r["tags"] == [] for r in result["items"]))
                    self.assertTrue(all(parse_instant(r["created_at"]) is not None for r in result["items"]))
                    # 字面子串匹配，不区分英文大小写
                    self.assertEqual(db.search_questions(conn, "REACT", 1, 20)["total"], 1)
                    self.assertEqual(db.search_questions(conn, "%", 1, 20)["total"], 0)
                    detail = db.find_question(conn, 3)
                    self.assertTrue(same_public(detail, RECORD_3))
                    self.assertIsNone(db.find_question(conn, 999))
            finally:
                os.environ.pop("DB_PATH", None)
                importlib.reload(importlib.import_module("question_db"))

    def test_upgrade_from_two_field_db(self):
        import sqlite3
        with tempfile.TemporaryDirectory() as temporary:
            db_file = Path(temporary) / "old.db"
            # 模拟第 2 课三字段库
            legacy = sqlite3.connect(db_file)
            legacy.execute("CREATE TABLE questions (id INTEGER PRIMARY KEY, title TEXT NOT NULL, body TEXT NOT NULL)")
            legacy.execute("INSERT INTO questions (id, title, body) VALUES (1, '旧库标题足够长', '旧库正文内容也足够长')")
            legacy.commit()
            legacy.close()
            os.environ["DB_PATH"] = str(db_file)
            db = importlib.reload(importlib.import_module("question_db"))
            try:
                db.init_db()  # 触发升级补列
                from contextlib import closing
                with closing(db.open_connection()) as conn:
                    row = db.find_question(conn, 1)
                    self.assertEqual(row["tags"], [])
                    self.assertTrue(parse_instant(row["created_at"]) is not None)
            finally:
                os.environ.pop("DB_PATH", None)
                importlib.reload(importlib.import_module("question_db"))


class SourceStructureTests(unittest.TestCase):
    def test_student_start_has_blank_task(self):
        student = code_only((ROOT / "server.py").read_text(encoding="utf-8"))
        self.assertIn("region task", (ROOT / "server.py").read_text(encoding="utf-8"))
        # 起点不预置创建答案（只看代码，注释里允许提示）
        self.assertNotIn("min_length", student)
        self.assertNotIn("create_question_service(conn", student)
        self.assertNotIn('extra="forbid"', student)

    def test_reference_has_complete_answer(self):
        ref = code_only((ROOT / "reference" / "server.py").read_text(encoding="utf-8"))
        self.assertIn("min_length", ref)
        self.assertIn('extra="forbid"', ref)
        self.assertIn("create_question_service(conn, payload)", ref)
        self.assertIn("field_validator", ref)

    def test_shared_modules_have_regions(self):
        db_text = (ROOT / "question_db.py").read_text(encoding="utf-8")
        for region in ("region row-mapping", "region search", "region insert-find"):
            self.assertIn(region, db_text)
        self.assertIn("region service", (ROOT / "service.py").read_text(encoding="utf-8"))
        self.assertIn("region out-models", (ROOT / "models.py").read_text(encoding="utf-8"))
        self.assertIn("region probe", (ROOT / "experiments" / "output_probe.py").read_text(encoding="utf-8"))


class ConfigTests(unittest.TestCase):
    def test_launch_config(self):
        config = json.loads((ROOT / ".vscode" / "launch.json").read_text(encoding="utf-8"))
        for item in config["configurations"]:
            self.assertEqual(item["module"], "uvicorn")
            self.assertNotIn("--reload", item["args"])
            self.assertNotIn("python", item)
            cwd = ROOT / item["cwd"].replace("${workspaceFolder}", "").strip("/")
            self.assertTrue((cwd / "server.py").is_file() or (cwd / "reference" / "server.py").is_file())


if __name__ == "__main__":
    print("Python", sys.version.split()[0], flush=True)
    for package in ("fastapi", "starlette", "uvicorn", "pydantic", "debugpy"):
        print(package, importlib.metadata.version(package), flush=True)
    unittest.main(verbosity=2)
