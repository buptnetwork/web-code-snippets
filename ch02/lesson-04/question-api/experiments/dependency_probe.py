"""第 4 课依赖生命周期探针（教师演示 · 黑盒）：用日志显示连接何时开／用／关、依赖何时退出。

观察点（对应底稿 2.3）：
- open → use → close 的顺序，close 由 finally 保证；
- 同一请求内多个参数声明同一依赖，拿到的是同一个实例（请求内缓存，不是连接池）；
- yield 依赖默认在响应发送之后才执行 finally（退出时机晚于 return）；
- 依赖获取阶段失败时 finally 仍执行（资源不漏），见 /probe-fail。
（after_commit 故障为什么留下已提交数据，用包根 server 的 /__teacher/fault-create 观察。）

运行（包根，已激活本包环境）：
    python -m uvicorn experiments.dependency_probe:app --port 8002
访问 /probe 与 /probe-fail，对照终端日志顺序。
"""

import sqlite3
from collections.abc import Generator
from typing import Annotated

from fastapi import Depends, FastAPI

app = FastAPI(title="Dependency Probe")


def log(event: str) -> None:
    print(f"[dependency_probe] {event}")


# region probe
def get_probe_conn() -> Generator[sqlite3.Connection, None, None]:
    log("open")
    conn = sqlite3.connect(":memory:")
    try:
        yield conn
    finally:
        log("close")
        conn.close()


ProbeConn = Annotated[sqlite3.Connection, Depends(get_probe_conn)]


def get_probe_service(conn: ProbeConn) -> Generator[str, None, None]:
    log("service-enter")
    yield "service"
    log("service-exit")


ProbeService = Annotated[str, Depends(get_probe_service)]


@app.get("/probe")
def probe(conn: ProbeConn, service: ProbeService, conn_again: ProbeConn):
    # conn 与 conn_again 是同一对象：证明请求内依赖缓存（不是每次新建、也不是连接池）。
    log(f"use same_conn={conn is conn_again} service={service}")
    return {"same_conn": conn is conn_again}


def get_failing_conn() -> Generator[sqlite3.Connection, None, None]:
    log("fail-open")
    conn = sqlite3.connect(":memory:")
    try:
        raise RuntimeError("依赖获取阶段失败")
        yield conn  # 永不执行
    finally:
        log("fail-close（获取失败仍关闭）")
        conn.close()


@app.get("/probe-fail")
def probe_fail(conn: Annotated[sqlite3.Connection, Depends(get_failing_conn)]):
    return {"unreachable": True}
# endregion probe
