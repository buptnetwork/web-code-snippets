"""本地自动验收：临时 SQLite 数据，不连接学生已有数据库。

默认验证 v3_m0；--app 指定学生的单文件模块；--all 同时检查课堂阶段。
接口测试使用真实 ASGI 应用与 SQLAlchemy，数据库断连用不可打开的 SQLite 路径注入。
这不是 PostgreSQL、浏览器或 IDE 断点的验收替代。
"""
import argparse
import ast
import importlib
import logging
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile

from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event
from seed import seed_database


def verify(module_name: str):
    with tempfile.TemporaryDirectory(prefix="m0-verify-", dir=Path(__file__).parent) as folder:
        root = Path(folder)
        database = f"sqlite:///{root / 'demo.db'}"
        logfile = root / "server.log"
        os.environ.update(DATABASE_URL=database, LOG_FILE=str(logfile), TRACE_MODE="trace", SQL_ECHO="0")
        seed_database(database)
        module = importlib.import_module(module_name)
        statements = []
        event.listen(module.engine, "before_cursor_execute", lambda conn, cursor, sql, params, ctx, many: statements.append(sql))
        paired_ids = []
        with TestClient(module.app, raise_server_exceptions=False) as client:
            def check(method, path, status, rid=None):
                response = client.request(method, path, headers={"X-Request-ID": rid} if rid else {})
                assert response.status_code == status, (path, response.status_code, response.text)
                if module_name != "v1_ai_raw":
                    actual = response.headers.get("X-Request-ID")
                    assert actual, (path, "缺响应 id")
                    if rid:
                        assert actual == rid, "传入的合法 id 被覆盖"
                    paired_ids.append(actual)
                return response

            if module_name == "v1_ai_raw":
                found = check("POST", "/getQuestions?keyword=react", 200)
                assert len(found.json()["data"]) == 6
                assert "X-Request-ID" not in found.headers
                missing = check("POST", "/getQuestionDetail?qid=999", 200)
                assert missing.json()["success"] is False
                check("POST", "/getQuestionDetail?qid=abc", 422)
                check("POST", "/getQuestions?keyword=%27", 500)
            elif module_name == "v2_traceable":
                found = check("POST", "/getQuestions?keyword=react", 200, "verify-search-01")
                assert len(found.json()["data"]) == 6
                check("POST", "/getQuestionDetail?qid=999", 200)
                check("POST", "/getQuestionDetail?qid=abc", 422)
                check("GET", "/docs", 200)
                check("GET", "/openapi.json", 200)
            else:
                search = check("GET", "/questions?keyword=react", 200, "verify-search-01").json()
                assert search["success"] is True and len(search["data"]) == 6
                detail = check("GET", "/questions/1", 200, "verify-detail-01").json()
                assert set(detail) == {"id", "title", "body", "created_at"}
                assert detail["id"] == 1 and detail["title"] == "react 练习问题 01"
                missing = check("GET", "/questions/999", 404, "verify-missing-01").json()
                assert missing["code"] == "question_not_found" and missing["request_id"] == "verify-missing-01"
                assert isinstance(missing["message"], str) and missing["message"]
                for value in ("abc", "0", "-1"):
                    check("GET", f"/questions/{value}", 422)
                check("POST", "/questions/1", 405)
                statements.clear()
                assert check("GET", "/healthz", 200).json() == {"status": "ok", "db": "ok"}
                assert [sql.strip().upper() for sql in statements] == ["SELECT 1"], statements
                original = module.engine
                broken = create_engine(f"sqlite:///{root / 'missing-directory' / 'demo.db'}")
                try:
                    module.engine = broken
                    assert check("GET", "/healthz", 503, "verify-db-down").json() == {"status": "degraded", "db": "down"}
                finally:
                    module.engine = original
                    broken.dispose()
                assert check("GET", "/healthz", 200).json()["db"] == "ok"
                for path in ("/docs", "/openapi.json", "/"):
                    check("GET", path, 200)
                check("GET", "/not-a-route", 404)
                check("POST", "/healthz", 405)
                response = client.get("/healthz", headers={"X-Request-ID": "bad id!"})
                assert re.fullmatch(r"[A-Za-z0-9._-]{1,64}", response.headers["X-Request-ID"])
                paired_ids.append(response.headers["X-Request-ID"])
                source = Path(module.__file__).read_text()
                tree = ast.parse(source)
                for node in ast.walk(tree):
                    if isinstance(node, ast.Constant) and isinstance(node.value, str):
                        assert not re.search(r"postgresql[^\s]*://[^\s:]+:[^@\s]+@|sk-[A-Za-z0-9]{10,}", node.value), "疑似硬编码凭据"
                    if isinstance(node, ast.Assign) and isinstance(node.value, ast.Constant) and node.value.value:
                        for target in node.targets:
                            if isinstance(target, ast.Name):
                                assert not re.search(r"password|secret|api_token|api_key", target.id, re.I), "敏感配置不应直接赋常量"
                assert "os.getenv" in source or "os.environ" in source, "缺少环境变量读取"
                assert Path(__file__).with_name(".env.example").exists()
                ignore = Path(__file__).resolve().parents[3] / ".gitignore"
                assert ".env" in ignore.read_text().splitlines(), ".env 未加入根 .gitignore"

            if module_name in {"v2_traceable", "v3_m0"}:
                response = client.get("/boom", headers={"X-Request-ID": "verify-boom"})
                assert response.status_code == 500
                assert "X-Request-ID" not in response.headers
        for handler in logging.getLogger().handlers:
            handler.flush()
        if module_name != "v1_ai_raw":
            logs = logfile.read_text()
            assert len(paired_ids) == len(set(paired_ids)), "未指定 id 时没有生成不同标识"
            for rid in paired_ids:
                assert logs.count(f"[{rid}] -->") == 1, (rid, "进入日志不配对")
                assert logs.count(f"[{rid}] <--") == 1, (rid, "离开日志不配对")
            if module_name in {"v2_traceable", "v3_m0"}:
                assert "[verify-boom] -->" in logs and "[verify-boom] <--" not in logs
        module.engine.dispose()
        logging.shutdown()
    print(f"PASS {module_name}：SQLite 接口、数据、日志及适用的预期失败检查通过")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--app", default="v3_m0", help="待验收的单文件模块名，不含 .py")
    parser.add_argument("--all", action="store_true")
    args = parser.parse_args()
    if args.all:
        for name in ("v1_ai_raw", "v2_traceable", "v3_m0"):
            subprocess.run([sys.executable, __file__, "--app", name], check=True, cwd=Path(__file__).parent)
    else:
        verify(args.app)
