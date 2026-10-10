"""第 5 课教师设施：真实 HTTP 并发对照三种等待端点（stdlib，不依赖第三方压测库）。

对应底稿 5.3：固定每组总请求数 10、并发上限分别为 1 与 10，共三端点 × 两并发 = 六组。
用 ThreadPoolExecutor 的 worker 数表达并发上限：10 个任务投给 10 个 worker 即同批并发，
投给 1 个 worker 即顺序处理相同的十个请求。每组先预热一次再测量；单请求服务延迟只计
urlopen 往返，等待并发名额的时间不计入单请求延迟，但计入整批总时长。

用法（先另开终端启动实验服务，单 worker，端口与本工具默认一致）：
    python -m uvicorn wait_lab:app --host 127.0.0.1 --port 8001 --workers 1
    python concurrency.py                 # 默认 http://127.0.0.1:8001，六组各 10 请求
    python concurrency.py --base-url http://127.0.0.1:8001 --total 10 --timeout 30

结论只验证「等待能否在同一进程里重叠」，不是生产吞吐或容量报告；少量样本不作性能阈值。
"""

import argparse
import json
import math
import time
from concurrent.futures import ThreadPoolExecutor
from urllib.error import HTTPError, URLError
from urllib.parse import urlsplit
from urllib.request import ProxyHandler, Request, build_opener

MODES = ("blocking", "awaiting", "threaded")
CONCURRENCIES = (1, 10)
MAX_BYTES = 1 << 16


def local_base_url(value):
    """只允许本地回环地址，不带路径，避免误打到教学服务之外。"""
    try:
        parts = urlsplit(value)
        if (
            parts.scheme != "http"
            or parts.hostname not in {"127.0.0.1", "localhost", "::1"}
            or parts.username is not None
            or parts.password is not None
            or parts.path not in {"", "/"}
            or parts.query
            or parts.fragment
            or parts.port == 0
        ):
            raise ValueError
    except ValueError as exc:
        raise argparse.ArgumentTypeError("只允许本地 http://127.0.0.1:端口 等回环地址，不带路径") from exc
    return value.rstrip("/")


def positive_timeout(value):
    number = float(value)
    if not math.isfinite(number) or not 0 < number <= 120:
        raise argparse.ArgumentTypeError("超时须在 0 到 120 秒之间（本工具默认 30，至少 30）")
    return number


def _opener():
    # 不使用系统代理；wait_lab 不重定向，无需自定义跳转处理。
    return build_opener(ProxyHandler({}))


def one_request(base, mode, timeout):
    """发一次 GET /lab/<mode>，返回 (kind, latency_s)。kind ∈ ok/http/timeout/other。"""
    req = Request(f"{base}/lab/{mode}", headers={"Accept": "application/json"}, method="GET")
    began = time.perf_counter()
    try:
        with _opener().open(req, timeout=timeout) as response:
            body = response.read(MAX_BYTES)
            status = response.status
        latency = time.perf_counter() - began
        if status == 200 and json.loads(body) == {"ok": True}:
            return "ok", latency
        return "http", latency
    except HTTPError:
        return "http", time.perf_counter() - began
    except TimeoutError:
        return "timeout", time.perf_counter() - began
    except URLError as exc:
        if isinstance(exc.reason, TimeoutError):
            return "timeout", time.perf_counter() - began
        return "other", time.perf_counter() - began
    except OSError:
        return "other", time.perf_counter() - began


def run_group(base, mode, concurrency, total, timeout):
    """把 total 个任务投给 concurrency 个 worker；总时长含等待名额，单请求延迟不含。"""
    started = time.perf_counter()
    with ThreadPoolExecutor(max_workers=concurrency) as pool:
        futures = [pool.submit(one_request, base, mode, timeout) for _ in range(total)]
        results = [future.result() for future in futures]
    duration = time.perf_counter() - started
    counts = {"ok": 0, "http": 0, "timeout": 0, "other": 0}
    latencies = []
    for kind, latency in results:
        counts[kind] += 1
        latencies.append(latency)
    return {
        "mode": mode, "concurrency": concurrency, "total": total,
        "success": counts["ok"], "http_fail": counts["http"],
        "timeout": counts["timeout"], "other_fail": counts["other"],
        "duration_s": round(duration, 3),
        "max_latency_s": round(max(latencies), 3),
        "avg_latency_s": round(sum(latencies) / len(latencies), 3),
    }


def main():
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--base-url", type=local_base_url, default="http://127.0.0.1:8001")
    parser.add_argument("--total", type=int, default=10, help="每组请求总数（固定口径为 10）")
    parser.add_argument("--timeout", type=positive_timeout, default=30)
    args = parser.parse_args()

    # 预热：每个端点先发一次，排除首次连接与导入开销，再进入测量。
    for mode in MODES:
        one_request(args.base_url, mode, args.timeout)

    print(f"目标 {args.base_url}；每组总数 {args.total}，超时 {args.timeout}s；先预热后测量。")
    print(f"{'mode':<10}{'conc':>5}{'total':>7}{'ok':>5}{'http':>6}{'timeout':>9}"
          f"{'other':>7}{'duration_s':>12}{'max_lat_s':>11}{'avg_lat_s':>11}")
    records = []
    for mode in MODES:
        for concurrency in CONCURRENCIES:
            row = run_group(args.base_url, mode, concurrency, args.total, args.timeout)
            records.append(row)
            print(f"{row['mode']:<10}{row['concurrency']:>5}{row['total']:>7}{row['success']:>5}"
                  f"{row['http_fail']:>6}{row['timeout']:>9}{row['other_fail']:>7}"
                  f"{row['duration_s']:>12}{row['max_latency_s']:>11}{row['avg_latency_s']:>11}")
    print(json.dumps(records, ensure_ascii=False))
    failed = sum(r["http_fail"] + r["timeout"] + r["other_fail"] for r in records)
    print(f"六组共 {sum(r['total'] for r in records)} 请求，失败/超时 {failed} 条。"
          f"数据只验证等待能否重叠，不作生产吞吐或容量结论。")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
