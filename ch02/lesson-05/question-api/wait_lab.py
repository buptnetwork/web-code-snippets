"""第 5 课教师实验：三种等待端点，对照 def / async def / 阻塞调用的执行位置。

对应底稿 5.2：三个端点都没有数据库、模板或真实外部服务，仅等待 1 秒并返回相同数据，
只用来观察「等待能否在同一进程里重叠」，不证明真实数据库／CPU／网络具有相同成本。
- /lab/blocking：async def 里直接 time.sleep，占住事件循环（隔离反例，不是把合格 M1 改坏）；
- /lab/awaiting：async def + await asyncio.sleep，可挂起，让其他任务前进；
- /lab/threaded：普通 def，框架放入线程池，释放事件循环但仍占一个线程。

只注册在本实验应用，不挂到 M1 公开工程；单 worker 启动，端口与 M1 区分：
    python -m uvicorn wait_lab:app --host 127.0.0.1 --port 8001 --workers 1
不启用 reload；先用 concurrency.py 核对请求确实发给本实验服务。
"""

# region make-wait-lab
import asyncio
import time
from fastapi import FastAPI


def make_wait_lab():
    lab = FastAPI(debug=False)

    @lab.get("/lab/blocking")
    async def blocking_wait():
        time.sleep(1)          # async 里直接阻塞：占住事件循环
        return {"ok": True}

    @lab.get("/lab/awaiting")
    async def awaiting_wait():
        await asyncio.sleep(1) # 可挂起：让其他任务前进
        return {"ok": True}

    @lab.get("/lab/threaded")
    def threaded_wait():
        time.sleep(1)          # 普通 def：框架放线程池，占一个线程
        return {"ok": True}

    return lab
# endregion make-wait-lab


app = make_wait_lab()
