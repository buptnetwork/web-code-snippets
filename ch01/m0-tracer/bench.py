"""有限并发噪音：10 个请求，同时在浏览器点一次；不是压测工具。"""
import argparse
import asyncio
import time

import httpx


async def run(base_url: str):
    async with httpx.AsyncClient(base_url=base_url, timeout=3, trust_env=False) as client:
        async def send(i):
            response = await client.post("/getQuestions", params={"keyword": "react", "page": 1},
                                         headers={"X-Request-ID": f"noise-{i:02d}"})
            response.raise_for_status()
            return response.status_code
        start = time.perf_counter()
        results = await asyncio.wait_for(asyncio.gather(*(send(i) for i in range(10))), timeout=4.5)
        print(f"完成 {len(results)} 个请求，耗时 {time.perf_counter() - start:.3f}s")
        print("这是本机本次观测，不保证所有学生机器都在同一时间完成。")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base-url", default="http://127.0.0.1:8000")
    args = parser.parse_args()
    asyncio.run(run(args.base_url))
