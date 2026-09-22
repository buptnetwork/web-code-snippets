# 第 5 次课教学底稿
## 中间件、并发模型、模板与表单闭环 ｜ 交付 M1

---

## 〇、给 PPT 制作团队的全局说明

本次课 100 分钟，留 5 分钟缓冲。**本次课是四个主题并列，内容量是全课程最大的一次，必须严格控时。** 请在制作时就按下面的分钟数排版，不要让任何一个单元的页数溢出。

**本次课有两个不可压缩的高光**：

1. **并发崩塌定量实验（单元 5，18 分钟）**。这是整门课里"数据说话"最有力的一次。核心不是"异步比同步快"，而是**一个 `async def` 加一句同步阻塞，代码看不出任何问题、单请求测试完全正常、并发一上来吞吐差 50 倍**。请务必把 before/after 数据表做成封面级素材。
2. **表单闭环与 PRG（单元 8，15 分钟）**。必须现场按 F5 制造出重复发帖，让数据库里真的多出一条。这个"手一抖就多一条"的现场感是说服力的全部。

**本次课的课程主题落点**：`async def` + 同步阻塞是 **AI 生成 FastAPI 代码的头号高频错误**，而且它的性质极端恶劣——不报错、不失败、code review 看不出来、单元测试测不出来，只在生产环境的并发峰值下暴露。请在单元 6.4 集中讲这一点，它是本次课与第 0 次课"哪些错误 AI 特别容易犯"的正式接点。

**若时间不够的压缩顺序**：先压单元 9 的 C 档卡（整体移课后）→ 再压单元 7 的 Jinja2（多数学生有前端基础，可只留自动转义那一页，其余给自读材料）→ 再压单元 3 的中间件顺序演示（第 4 次课已铺好洋葱图，可只讲结论表 + 一次打印验证）。**单元 5、8 不能压缩。**

**一个需要教师裁决的地方**：单元 3 要把第 4 次课留的"中间件失灵"欠账**完整修好**，而正确的修法需要在两个层次各做一件事（中间件改 `try/finally` + 在 `Exception` handler 里补响应头）。这一段技术链条较深但价值很高。如果你希望简化为只修日志、响应头留到课后，请告知，可省 4 分钟。

---

## 一、开场：把第 4 次课那张洋葱图接回来

**约 4 分钟。**

内容：

**直接把第 4 次课单元 5.5 的洋葱层次图放上来**，不要重画，就用同一张图——这次它是主角。

第 4 次课我们发现：`AppError` 的处理器让中间件恢复正常了，但真正未预期的异常（`RuntimeError`）会穿透中间件，让日志和响应头都失效。当时的结论是一句判断：

> **当你发现"某段代码在某些情况下不执行"，先问它在哪一层，而不是先改它的逻辑。**

今天把这句话做实。然后在同一张图上再加一层理解：**这些层不只有前后顺序，它们还跑在同一个事件循环里——所以其中任何一层阻塞了，整条链上所有请求一起卡住。**

本次课结束时你应当能回答：

- 两个中间件，谁先执行？依据是什么？（现场打印出来看）
- 为什么第 4 次课那个中间件在异常时失灵，**为什么单改中间件修不好**？
- `async def` 里写 `time.sleep(1)` 会发生什么？**能定量说出来吗？**
- 一个新端点，你怎么决定写 `def` 还是 `async def`？
- HTML 表单提交后按 F5，为什么会多发一条？303 凭什么能解决它？
- 校验失败时为什么**不能**重定向？

讲：

> 今天这节课有一个特点：**前四次课讲的都是"正确性"，今天有一半在讲"能不能扛住"。**
>
> 这两件事的失败方式完全不同。正确性错了，你会看到报错、看到 422、看到错误的数据。**扛不住这件事不报错——它在你的开发机上完全正常，在演示时完全正常，在只有你一个人用的时候完全正常。**
>
> 所以今天我要教你的不是"怎么写异步"，是**怎么把这类看不见的问题变成一张有数字的表**。

---

## 二、解剖台：两个不报错的 bug

**约 10 分钟。**

### 情境设定

> 这是你第 4 次课重构后的项目，加上了两个新东西：一个"发帖"的 HTML 页面，一个"抓取外部链接标题"的辅助端点。AI 帮你写的，你测了，都对。
>
> 然后：
> 第一，你把项目发给三个同学一起试用。**三个人同时点一下，页面转圈 3 秒才出来。** 你自己一个人测的时候是 0.1 秒。
> 第二，有个同学发了一条问题，网络卡了一下，他按了 F5。**数据库里现在有三条一模一样的问题。**

### 代码（tag: `v5-broken`，可运行，两个问题均可稳定复现）

```python
# app/routers/questions.py —— AI 补出来的两个端点
import time, requests
from fastapi import APIRouter, Depends, Form, Request
from fastapi.templating import Jinja2Templates

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


@router.get("/questions/{qid}/link-title")
async def fetch_link_title(qid: int, conn=Depends(get_conn)):
    q = svc.get(conn, qid)
    resp = requests.get(q.link_url, timeout=5)      # ← 同步 HTTP 调用
    return {"title": parse_title(resp.text)}


@router.get("/ui/questions/new")
async def new_question_page(request: Request):
    return templates.TemplateResponse(
        "question_form.html", {"request": request, "errors": {}, "values": {}})


@router.post("/ui/questions")
async def submit_question(
    request: Request,
    title: str = Form(...),
    body: str = Form(...),
    conn=Depends(get_conn),
):
    q = svc.create(conn, title, body, author_id=1)
    # 直接把详情页渲染出来返回
    return templates.TemplateResponse(
        "question_detail.html", {"request": request, "q": q})
```

```html
<!-- app/templates/question_detail.html —— 节选 -->
<h1>{{ q.title }}</h1>
<div class="body">{{ q.body | safe }}</div>     <!-- ← 记住这里 -->
```

### 现场演示顺序

**第一个：三个人一起点，就慢了**

先单请求：

```bash
time curl -s localhost:8000/questions/1/link-title > /dev/null
# real 0m0.52s   ← 正常
```

再三个并发：

```bash
for i in 1 2 3; do curl -s localhost:8000/questions/1/link-title & done; wait
# 最后一个：1.6s
```

提问：**这个端点的代码里，哪一行导致了这个现象？**

学生通常答不出来，或者猜"是 requests 慢"。指出：

> `requests.get` 本身的耗时没变，还是 0.5 秒。变的是**第二个和第三个请求要排队等第一个**。
>
> 而且注意：这个函数写的是 `async def`——它看起来是异步的，是"高并发"的写法。**它恰恰是最糟的组合。** 单元 5 会用数字把这件事说清楚。

再追加一个更隐蔽的观察：

> 更糟的是：现在卡住的**不只是这个端点**。三个人在抓链接标题的时候，你去访问 `/healthz`——它也卡住了。
>
> **一个端点的阻塞，会让整个服务的所有端点一起变慢。** 这一条要记住，单元 4 会解释为什么。

**第二个：F5 就多一条**

在浏览器里打开发帖页，填好，提交。页面显示详情。

**然后按 F5。**

浏览器弹出"确认重新提交表单？"，点确定。**数据库里多了一条。** 再按一次，第三条。

```sql
SELECT id, title, created_at FROM questions ORDER BY id DESC LIMIT 3;
--  9 | 怎么学 React | 2025-03-20 10:22:31.442
--  8 | 怎么学 React | 2025-03-20 10:22:28.105
--  7 | 怎么学 React | 2025-03-20 10:22:24.887
```

> 注意这个 bug 的性质：**代码没有任何错误。** POST 处理正确、校验正确、入库正确、返回的 HTML 正确。
>
> 错的是**它对浏览器行为的假设**。浏览器认为"当前页面是一次 POST 的结果"，所以刷新就是重发那次 POST。这是浏览器的正确行为，是我们没有告诉它该怎么办。

**第三个（不在情境里，顺手指出）**

把详情页模板里的 `{{ q.body | safe }}` 高亮：

> 记住这个 `| safe`。今天单元 7 会讲它关掉了什么，**第 15 次课会用它演示一次完整的 XSS**。今天先把它当成一笔欠账记下。

### 顺手回收第 4 次课的成果（**这一段请务必保留，它是对上次课的正向反馈**）

> 在进入正题之前，我要你们注意一件事。
>
> 刚才那个 `submit_question`，它处理的是 **HTML 表单**，不是 JSON。它的 Content-Type 是 `application/x-www-form-urlencoded`，参数用 `Form(...)` 接，返回的是 HTML 不是 JSON。**这是一个和之前六个端点完全不同的客户端。**
>
> 但你看这一行：
>
> ```python
> q = svc.create(conn, title, body, author_id=1)
> ```
>
> **和 JSON 端点调的是同一个 service 函数。** 业务规则（标题不能重复）、数据访问、事务边界，一行都没有重写。
>
> 这就是第 4 次课分层的回报。当时我说"分层的回报全在被修改这件事上"——今天是第一次兑现：**加一个全新的客户端类型，`services/` 和 `repositories/` 零改动。**

### 欠账清单

| 发现的问题 | 本次课处理 | 何时还 |
|---|---|---|
| `async def` 里调同步阻塞 | **单元 5、6 回收** | — |
| 一个端点阻塞拖垮全服务 | **单元 4 解释** | — |
| POST 后直接返回 HTML → 刷新重复提交 | **单元 8 回收** | — |
| 第 4 次课：中间件在未预期异常下失灵 | **单元 3 回收** | — |
| `\| safe` 关掉了自动转义 | 单元 7 指出机制 | **第 15 次课**（XSS 完整演示） |
| `author_id=1` 硬编码 | 记一笔 | 第 14 次课 |
| 表单提交没有防重放/防 CSRF | 记一笔 | 第 15 次课 |
| 外部 HTTP 调用没有重试与熔断 | 记一笔 | 第 16 次课 |

---

## 三、现场必做 A：中间件的顺序，以及把欠账彻底修好

**约 12 分钟。**

### 3.1 先做一个预测题

现场加两个中间件，**注意书写顺序**：

```python
# app/main.py
@app.middleware("http")
async def mw_a(request: Request, call_next):
    print("A enter")
    resp = await call_next(request)
    print("A exit")
    return resp

@app.middleware("http")
async def mw_b(request: Request, call_next):
    print("B enter")
    resp = await call_next(request)
    print("B exit")
    return resp
```

提问（让学生举手表决）：**打印顺序是什么？**

多数人会猜 `A enter → B enter → B exit → A exit`（按书写顺序）。

实际输出：

```
B enter
A enter
A exit
B exit
```

### 3.2 打印出来看（延续第 3、4 次课的同一个动作）

```python
for i, mw in enumerate(app.user_middleware):
    print(i, mw.cls.__name__, mw.kwargs.get("dispatch", None))
```

输出：

```
0 BaseHTTPMiddleware  <function mw_b at 0x...>     ← 后写的在索引 0
1 BaseHTTPMiddleware  <function mw_a at 0x...>
```

**结论（醒目页）**：

> **`add_middleware`（以及 `@app.middleware`）是往列表头部插入的。所以：**
>
> **最后注册的中间件在最外层，请求最先经过它，响应最后经过它。**
>
> 这和你的直觉相反，也和路由的规则相反（第 3 次课：路由是**先注册先匹配**）。**同一个框架里两套顺序语义，必须分别记。**

把第 4 次课的洋葱图补全成本次课的版本：

```
   ┌────────────────────────────────────────────────┐
   │ ServerErrorMiddleware        （框架，最外）      │  ← Exception handler 在这层
   │ ┌────────────────────────────────────────────┐ │
   │ │ mw_b        （最后注册）                    │ │
   │ │ ┌────────────────────────────────────────┐ │ │
   │ │ │ mw_a      （先注册）                    │ │ │
   │ │ │ ┌────────────────────────────────────┐ │ │ │
   │ │ │ │ ExceptionMiddleware （框架）         │ │ │ │  ← AppError / 422 handler 在这层
   │ │ │ │ ┌────────────────────────────────┐ │ │ │ │
   │ │ │ │ │ 路由 → 依赖 → 端点              │ │ │ │ │
   │ │ │ │ └────────────────────────────────┘ │ │ │ │
   │ │ │ └────────────────────────────────────┘ │ │ │
   │ │ └────────────────────────────────────────┘ │ │
   │ └────────────────────────────────────────────┘ │
   └────────────────────────────────────────────────┘
```

### 3.3 顺序判据

| 中间件 | 应该在 | 理由 |
|---|---|---|
| CORS | **最外层**（最后注册） | 预检请求 OPTIONS 要在任何其他逻辑之前被应答；出错的响应也必须带 CORS 头，否则浏览器连错误信息都读不到 → **第 12 次课会现场踩这个坑** |
| request-id / 日志 | 靠外（早注册？不，靠外 = 晚注册） | 要覆盖尽可能多的请求，包括 404 |
| GZip | 靠内于 CORS | 要压缩最终响应体 |
| 认证 | **不要写成中间件** | 回收第 4 次课单元 8 的判据 |

> 判据：**"要对所有请求生效、要改响应"的往外放；"只关心业务"的往内放或者别写成中间件。**

### 3.4 修好第 4 次课的欠账（**本单元的核心**）

回顾病情：`RuntimeError` 时，中间件的日志不打印、`X-Request-Id` 响应头没有。

**先试最直觉的修法：try/finally。**

```python
@app.middleware("http")
async def timing(request: Request, call_next):
    rid = uuid.uuid4().hex[:12]
    request.state.request_id = rid
    t0 = time.perf_counter()
    try:
        response = await call_next(request)
        response.headers["X-Request-Id"] = rid
        return response
    finally:
        cost = (time.perf_counter() - t0) * 1000
        logger.info("rid=%s %s %s %.1fms", rid, request.method,
                    request.url.path, cost)
```

重新触发 `RuntimeError`，观察：

- 日志 ✅ **打印了**
- 响应头 ❌ **还是没有**

**停下来提问：为什么响应头还是没有？**

引导回那张洋葱图：

> 异常从端点抛出，穿过 `ExceptionMiddleware`（没有匹配的 handler），穿过我们的中间件（`finally` 执行了日志），到达 `ServerErrorMiddleware`。
>
> **500 响应是 `ServerErrorMiddleware` 生成并发出的——它在我们外层。** 那个响应对象从来没有经过我们的中间件，我们根本碰不到它。
>
> 所以：**这个问题的两半发生在两个不同的层次，只在一个层次修是不够的。**

**正确的修法：在异常处理器里补。**

```python
# app/exception_handlers.py —— 改第 4 次课写的兜底处理器
@app.exception_handler(Exception)
async def handle_unexpected(request: Request, exc: Exception):
    rid = getattr(request.state, "request_id", "-")
    logger.exception("unhandled rid=%s", rid)
    return JSONResponse(
        status_code=500,
        content=_body("internal_error", "服务器内部错误", None, rid),
        headers={"X-Request-Id": rid},          # ← 补这一行
    )
```

再测一次：日志 ✅、响应头 ✅、响应体里有 request_id ✅。

**三行结论（醒目页）**：

> 1. **中间件能保证"我的代码一定执行"（`try/finally`），但不能保证"我能拿到响应"。**
> 2. 未预期异常的响应由外层框架生成，**要改它只能在异常处理器里改**。
> 3. 所以一条横切逻辑，有时候**必须在中间件和异常处理器两处各写一半**。

〔C 档一句话：如果不想在两处重复写，可以用 `contextvars` 存 request_id，日志和处理器都从 contextvar 里读，不依赖 `request.state` 传递。这在有后台任务、有多层调用时更干净。课后自读。〕

### 3.5 顺手提一个坑

> `@app.middleware("http")` 用的是 `BaseHTTPMiddleware`，它有若干已知的边角问题（读取请求体后端点读不到、和流式响应交互异常、有额外的任务开销）。
>
> 本课程规模下它够用。但你如果看到有人写"纯 ASGI 中间件"（直接 `async def __call__(self, scope, receive, send)`），**那不是在炫技，是在避开这些坑**。第 3 次课那 8 行裸 ASGI 应用就是它的骨架。

### 材料

- tag `v5-broken`（起始）、`v5-middleware`（本单元结束）。
- 截图：`app.user_middleware` 的打印输出；两个中间件的 enter/exit 打印顺序。
- **高光图**：补全版洋葱图（六层），需与第 4 次课那张同风格、可叠加对照。
- 截图：try/finally 修法下"日志有、响应头无"的对照（curl -i 输出 + 终端日志同屏）。

---

## 四、三种并发模型：一句话结论

**约 10 分钟。这一单元是单元 5 实验的理论准备，请控制在 10 分钟，不要展开。**

### 4.1 WSGI 与 ASGI 的一句话差别

把第 3 次课那 8 行裸 ASGI 应用调出来，旁边放 WSGI 版本：

```python
# WSGI：一次函数调用完成一个请求
def app(environ, start_response):
    start_response("200 OK", [("Content-Type", "text/plain")])
    return [b"hello"]

# ASGI：一个协程，可以在 await 处让出控制权
async def app(scope, receive, send):
    await send({"type": "http.response.start", "status": 200, "headers": [...]})
    await send({"type": "http.response.body", "body": b"hello"})
```

**一句话结论（醒目页）**：

> **WSGI 的函数一旦开始执行就必须跑完，期间它占着一个线程。**
>
> **ASGI 的协程可以在 `await` 处暂停、把线程让给别的请求、等结果回来再继续。**
>
> 所以 ASGI 能用一个线程处理成百上千个"正在等 IO"的请求——**前提是它们真的在 `await`，而不是在阻塞。**

最后半句要重读，它是今天所有问题的根源。

### 4.2 三种模型的结论表（**本单元核心，做成一页**）

| 模型 | 一个"执行单元"处理 | 切换由谁决定 | 并发上限受限于 | 适合 |
|---|---|---|---|---|
| **多进程** | 1 个请求 | 操作系统 | 内存（每进程几十 MB） | CPU 密集；隔离性要求高 |
| **线程池** | 1 个请求 | 操作系统（可抢占） | 线程数（默认几十） | **阻塞的 IO 调用**（同步库） |
| **事件循环** | 成百上千个请求 | **代码自己**（`await` 处让出） | 单核 CPU | **await 的 IO 调用**（异步库） |

**三个必须点出来的推论**：

1. **事件循环是协作式的。** 它靠你在 `await` 处主动让出。**你不 await，它就没有任何办法把线程拿回来**——没有超时、没有抢占、没有报错。这是单元 5 崩塌的机制。
2. **CPU 密集在三种模型里都只能靠多进程。** 线程池救不了（Python 的 GIL），事件循环更救不了。判据：**如果一段代码在算而不是在等，那只有进程数能提升它的吞吐。**
3. **uvicorn 单 worker 就是一个事件循环 + 一个线程池。** 这解释了解剖台第一个现象的后半段——为什么 `/healthz` 也卡住了：**它们共享同一个事件循环，循环被占死，谁都别想走。**

### 4.3 FastAPI 的调度规则（**这是本课最关键的一条机制**）

做成醒目页，字要大：

> **你写 `async def`，框架把你的函数放进事件循环里执行。**
> **你写 `def`，框架把你的函数扔进线程池里执行。**
>
> 依赖函数也一样，各自独立判断。

四种组合的后果：

| 你写的 | 你调用的 | 结果 |
|---|---|---|
| `def` | 同步阻塞 | ✅ 正确：阻塞发生在线程池，事件循环不受影响 |
| `async def` | `await` 异步库 | ✅ 正确：在 await 处让出，并发能力最强 |
| `async def` | **同步阻塞** | ❌ **灾难：阻塞发生在事件循环里，整个服务串行化** |
| `def` | `await`（`asyncio.run`） | ❌ 报错或行为异常，不要这么写 |

> 第三行就是解剖台那个 bug，也是单元 5 要量化的对象。
>
> 请注意它为什么危险：**它不报错。** 其他三种组合里，错的那种会直接报错让你发现。**只有这一种，Python 没有任何办法知道你调用的函数是不是阻塞的。**

---

## 五、现场必做 B：并发崩塌定量

**约 18 分钟。本次课最高光，绝对不能压缩。**

### 5.1 实验设计（先讲清设计，再跑）

三个端点，**业务逻辑完全等价**：都"等 0.5 秒然后返回"。

```python
# app/routers/lab.py —— 实验端点
import time, asyncio

@router.get("/lab/a")                      # 组合三：灾难
async def a():
    time.sleep(0.5)
    return {"mode": "async def + time.sleep"}

@router.get("/lab/b")                      # 组合二：正确
async def b():
    await asyncio.sleep(0.5)
    return {"mode": "async def + await"}

@router.get("/lab/c")                      # 组合一：正确
def c():
    time.sleep(0.5)
    return {"mode": "def + time.sleep"}

@router.get("/lab/d")                      # CPU 密集对照
def d():
    t0 = time.perf_counter()
    while time.perf_counter() - t0 < 0.5:  # 忙等，模拟计算
        pass
    return {"mode": "def + CPU bound"}
```

**服务启动参数（必须固定，否则数据不可比）**：

```bash
uvicorn app.main:app --workers 1 --log-level warning
```

> **`--workers 1` 是这个实验的前提。** 多 worker 会把崩塌掩盖掉一部分，让你以为问题没那么严重——**而这正是很多团队在生产环境里"感觉还行"的原因：他们用多 worker 掩盖了单 worker 的串行化。**

压测脚本（课程提供，避免装工具）：

```bash
python scripts/bench.py --url http://localhost:8000/lab/a --concurrency 1  --total 8
python scripts/bench.py --url http://localhost:8000/lab/a --concurrency 10 --total 40
python scripts/bench.py --url http://localhost:8000/lab/a --concurrency 50 --total 200
# 对 b / c / d 重复
```

脚本输出：总耗时、吞吐（req/s）、p50、p95。

### 5.2 先跑并发 1（**这一步是整个实验的关键，不要跳**）

```
/lab/a  concurrency=1  →  2.0 req/s   p50 502ms   p95 508ms
/lab/b  concurrency=1  →  2.0 req/s   p50 501ms   p95 505ms
/lab/c  concurrency=1  →  2.0 req/s   p50 503ms   p95 511ms
```

**停在这里，把三行数据留在屏幕上，然后说**：

> 三个端点，**在并发 1 下的表现完全一样**。
>
> 这意味着：
> - 你在开发机上点一下，测不出来；
> - 你写一个单元测试断言"响应时间小于 1 秒"，测不出来；
> - 你做 code review，看到 `async def` 觉得挺现代的，看不出来；
> - **你把这段代码给 AI 看，问它"有没有性能问题"，它也未必看得出来——因为它不知道 `parse_title` 里那个 `requests.get` 是同步的。**
>
> **这类 bug 的定义就是：在你能做的所有常规检查里，它都是好的。**

### 5.3 提升并发，看崩塌

**填这张表（这是本次课的封面级素材）**：

| 端点 | 组合 | 并发 1 | 并发 10 | 并发 50 | 并发 50 的 p95 |
|---|---|---|---|---|---|
| `/lab/a` | `async def` + `time.sleep` | 2.0 req/s | **2.0** | **2.0** | **≈ 25 s** |
| `/lab/b` | `async def` + `await` | 2.0 | 19.6 | **95** | **≈ 0.52 s** |
| `/lab/c` | `def` + `time.sleep` | 2.0 | 19.6 | **76** | **≈ 0.65 s** |
| `/lab/d` | `def` + CPU 忙等 | 2.0 | **2.0** | **2.0** | ≈ 25 s |

〔制作团队请在演示机上实测填入真实数据，上表为理论预期值，用于校验实验是否正确搭建。允许 ±20% 偏差；若 `/lab/a` 在并发 50 下吞吐明显高于 2.0，说明 worker 数没设成 1。〕

**四条观察，逐条讲**：

**观察一：`/lab/a` 的吞吐完全不随并发增长，恒定在 2.0。**

> 2.0 req/s = 1 / 0.5s。**这就是完全串行。** 50 个并发请求，它一个一个做，最后一个等了 25 秒。
>
> 事件循环被 `time.sleep` 占死了，期间它不能接受新连接、不能处理别的请求、不能响应健康检查。**服务在这 25 秒里对外表现为"挂了"。**

**观察二：`/lab/a` 和 `/lab/b` 的代码差别有多小。**

把两段代码并排放大：

```python
async def a():
    time.sleep(0.5)            # 差别就在这一行

async def b():
    await asyncio.sleep(0.5)
```

> **一个 `await`，五个字符，吞吐差 47 倍，p95 差 48 倍。**
>
> 这是我今年最想让你们记住的一张对照图。

**观察三：`/lab/c` 也很好，但有上限（76 而不是 95）。**

> `def` 端点跑在线程池里，线程池默认大小约 40（AnyIO 默认值）。所以上限约 40 / 0.5s = 80 req/s。
>
> 并发 50 时有一小部分请求要排队等线程，所以 p95 略高于 0.5 秒。
>
> **结论：`def` + 同步阻塞是"正确且够用"，不是"最优"。** 它的天花板是线程池大小；异步的天花板是单核 CPU。对本课程规模，两者都远远够。

**观察四：`/lab/d` 写的是 `def`，为什么也崩了？**

> 因为它**不在等，它在算**。线程池有 40 个线程，但 Python 的 GIL 让它们没法真正并行执行 Python 字节码。
>
> **判据：`def` 能救"阻塞的等待"，救不了"CPU 密集的计算"。** 后者只有两条路：换进程（`ProcessPoolExecutor` 或多 worker）、或者把这件事移出请求路径（放进任务队列 → 第 16 次课）。

### 5.4 修复解剖台的那个端点

```python
# 修法一：改成 def，让框架放线程池（最小改动，本课程首选）
@router.get("/questions/{qid}/link-title")
def fetch_link_title(qid: int, conn=Depends(get_conn)):
    q = svc.get(conn, qid)
    resp = requests.get(q.link_url, timeout=5)
    return {"title": parse_title(resp.text)}
```

```python
# 修法二：全程异步（要换库：requests → httpx.AsyncClient）
@router.get("/questions/{qid}/link-title")
async def fetch_link_title(qid: int, conn=Depends(get_conn)):
    q = svc.get(conn, qid)
    async with httpx.AsyncClient(timeout=5) as client:
        resp = await client.get(q.link_url)
    return {"title": parse_title(resp.text)}
```

**必须点出修法二的隐藏代价**（这是一次取舍训练）：

> 修法二看起来更"正确"，但注意它要求什么：
>
> - `requests` 换成 `httpx`——一个新依赖；
> - 这个端点还依赖 `get_conn`，而我们的数据库连接是**同步的 SQLAlchemy**。也就是说这个 `async def` 端点里还藏着一个同步阻塞（那次数据库查询）；
> - 要彻底异步，数据库也得换成 `asyncpg` + SQLAlchemy 的异步引擎，那意味着 `deps.py`、`repositories/` 全部要改。
>
> **判据：异步是全链路的。链上有一环是同步的，整条链的收益就打折甚至归零。**
>
> 所以本课程的选择是**修法一**：项目是同步栈，端点就写 `def`。这不是将就，这是一致性。
>
> 〔什么时候值得上全异步栈：单机需要扛数千并发长连接、或大量外部 HTTP 调用。不是"因为异步更现代"。〕

### 5.5 B 档作业的起点

> 作业里你要重跑这个实验，并且加一组：**把 `--workers 1` 改成 `--workers 4`，重测 `/lab/a`。**
>
> 先预测：吞吐会变成多少？为什么？**这个预测是作业的一部分。**

### 材料

- `scripts/bench.py`：httpx + asyncio 压测脚本，参数 `--url --concurrency --total`，输出吞吐/p50/p95，**必须在三种操作系统上验证可跑**。
- tag `v5-lab`：含四个实验端点。
- **封面级素材**：5.3 那张四行五列的数据表，`/lab/a` 那一行的三个 2.0 用红色高亮。
- **封面级素材**：`a()` 与 `b()` 两段代码并排图，差异行高亮，下方标注"47×"。
- 截图：并发 1 下三个端点数据完全相同的终端输出（**这张图的说服力可能比崩塌图更大**）。
- 备用：预录 90 秒实验录像（压测在教室网络下可能不稳）。

---

## 六、def 还是 async def：判据

**约 10 分钟。含本次课的课程主题落点。**

### 6.1 决策规则（醒目页，字要大）

> **看你的函数体里有没有"会等待但不 await"的调用。**
>
> **有 → 写 `def`。没有 → 随便，但写 `async def` 能拿到更高上限。**

展开成一张可执行的清单：

| 函数体里出现了 | 写什么 |
|---|---|
| 同步 ORM / `conn.execute()` | `def` |
| `requests.*` / `urllib` | `def` |
| `open().read()` / 文件操作 | `def` |
| `time.sleep()` | `def`（但先想想为什么要 sleep） |
| 同步的 redis / 第三方 SDK | `def` |
| 大量计算、图片处理、加解密 | `def`，**而且要考虑移出请求路径** |
| 只有 `await` 的异步库调用 | `async def` |
| 什么 IO 都没有（纯内存计算，很快） | 都行 |

### 6.2 三个容易忽略的地方

**一、依赖函数各自独立判断。**

```python
def get_conn():                    # 同步依赖 → 框架放线程池 ✅
    with engine.begin() as conn:
        yield conn

async def get_current_user(...):   # 如果里面有同步查库 → ❌ 错了
    user = repo.find_user(conn, uid)   # 同步阻塞在事件循环里
```

> 第 4 次课我们写的依赖全是 `def`，**那是有意的**。今天你知道原因了。

**二、`async def` 里想调同步代码，有正规办法。**

```python
from fastapi.concurrency import run_in_threadpool

@router.get("/x")
async def x():
    data = await run_in_threadpool(blocking_call, arg)   # 显式扔线程池
```

> 但请注意：如果你整个函数只是为了包一个同步调用，**那直接写 `def` 更简单**。`run_in_threadpool` 的用途是"这个函数大部分是异步的，只有一处必须同步"。

**三、`async def` 里绝对不要做的两件事**：不要 `time.sleep`（用 `asyncio.sleep`）、不要跑长时间计算（挪到线程池或进程池）。

### 6.3 worker 数量：经验结论与它的前提

| 场景 | 起点 | 前提 |
|---|---|---|
| CPU 密集为主 | `workers = CPU 核数` | 再多只会增加切换开销 |
| IO 密集 + 同步代码（`def` 端点） | `workers = 2 × 核数 + 1` | gunicorn 文档的经验值；**前提是每个 worker 内存占用可控** |
| IO 密集 + 全异步 | `workers = 核数` 就够 | 并发靠事件循环，不靠 worker 数 |
| 容器环境 | **先查容器的 CPU limit，不是宿主机核数** | 这一条最容易错 |

**必须补的一段**（这是取舍训练，不是记公式）：

> 这些数字是**起点，不是答案**。
>
> 每个 worker 都是一个独立进程：独立的内存、**独立的数据库连接池**。4 个 worker × 每池 10 连接 = 40 个数据库连接。**你的 PostgreSQL 默认最大连接数是 100。** 加到 16 个 worker，数据库先挂。
>
> 判据：**worker 数量不是一个可以单独决定的参数，它和连接池大小、数据库上限、容器内存限制是一组约束。**
>
> 〔第 16 次课部署时会把这组约束一起算一遍。今天只要知道它们互相牵制。〕

### 6.4 课程主题落点：为什么这是 AI 的头号错误

**这一小节是本次课与课程主题的正式接点，请完整制作。**

先给出现象：

> 你让 AI "给我写一个 FastAPI 端点，查数据库返回问题列表"。
>
> 它有**很高的概率**给你 `async def`，然后在里面用同步的 SQLAlchemy。

三个原因，值得讲清楚：

| 原因 | 说明 |
|---|---|
| **训练数据的偏向** | FastAPI 的宣传语就是"高性能异步框架"，教程和博客里 `async def` 占压倒多数。**AI 学到的是"FastAPI 端点长什么样"，不是"这个端点该不该是异步的"** |
| **它看不到你的调用栈** | 它不知道 `svc.create()` 里面最终调的是同步的 `conn.execute()`。**判断阻塞需要跟进好几层，而它通常只看到你给它的那个文件** |
| **没有任何反馈信号** | 代码能跑、测试能过、类型检查能过、linter 不报警。**AI 没有任何机会知道自己错了** |

然后是关键的一段：

> 我要你们注意这个错误的**性质**，因为它和前几次课见过的都不一样：
>
> | | 怎么被发现 |
> |---|---|
> | 第 3 次课：返回了密码哈希 | 肉眼看响应体能发现（虽然容易漏） |
> | 第 4 次课：错误格式不统一 | 前端接的时候一定会发现 |
> | **今天：`async def` + 阻塞** | **在开发和测试阶段，没有任何一种常规检查能发现** |
>
> 所以它需要的护栏也不一样。前两种可以靠 schema、靠统一处理器——**结构上堵住**。这一种堵不住，因为"一个函数是不是阻塞的"在 Python 里没有类型可以表达。
>
> 那怎么办？三层：
>
> 1. **约定**：本项目所有端点和依赖一律写 `def`，除非你能说出全链路都是 await 的。**用一致性消除判断成本。**
> 2. **检查**（可机械化）：在 CI 里 grep——`async def` 的函数体里出现 `requests.`、`.execute(`、`time.sleep` 就失败。这是个粗糙的检查，但它能抓住 90% 的情况。**→ 第 9 次课会写它。**
> 3. **压测**（兜底）：把今天这个实验做成一条基线，发布前跑一次。**数据是唯一不会被糊弄的东西。**
>
> **判据：当一类错误无法在结构上堵住时，就用"约定 + 机械检查 + 定量兜底"三层来兜。** 这三层都不依赖某个人当天足够细心。

---

## 七、Jinja2 最小集与自动转义

**约 10 分钟。若时间紧，只保留 7.3 自动转义那一页，其余转自读材料。**

### 7.1 为什么本课程要教一点模板

> 你们多数人会用 React 或 Vue。那为什么还要学 Jinja2？
>
> 三个理由，都很实际：
> 1. **M1 需要一个能点的界面**，不引入前端构建链是最快的路；
> 2. **管理后台、邮件模板、导出报表**——真实项目里服务端渲染从来没消失；
> 3. **第 8 次课讲前后端分离时，你需要一个"不分离"的对照物**才能说清分离解决了什么、代价是什么。
>
> 所以今天只讲最小集：**够用，不深入。**

### 7.2 最小集（五个东西）

```html
<!-- app/templates/base.html -->
<!DOCTYPE html>
<html>
<head><title>{% block title %}问答{% endblock %}</title></head>
<body>
  <nav>...</nav>
  {% block content %}{% endblock %}
</body>
</html>
```

```html
<!-- app/templates/question_list.html -->
{% extends "base.html" %}
{% block title %}问题列表{% endblock %}
{% block content %}
  <ul>
  {% for q in questions %}
    <li><a href="/ui/questions/{{ q.id }}">{{ q.title }}</a>
        （{{ q.created_at.strftime('%m-%d') }}）</li>
  {% else %}
    <li>还没有问题</li>
  {% endfor %}
  </ul>
{% endblock %}
```

| 要素 | 作用 |
|---|---|
| `{{ 变量 }}` | 插值，**默认 HTML 转义** |
| `{% if %}` / `{% for %}...{% else %}` | 控制流；`for-else` 处理空列表很顺手 |
| `{% extends %}` + `{% block %}` | 布局继承——**一个 base 页，各页只填 block** |
| `{% include %}` | 片段复用 |
| 过滤器 `\| length` `\| default('-')` | 小的展示变换 |

**一条判据**：

> **模板里只做展示，不做判断。**
>
> 看到模板里出现"如果用户是作者且问题未关闭且当前时间小于截止时间就显示按钮"这种条件，就该把它算成一个布尔值（`can_edit`）在 service 里算好传进来。
>
> 理由和第 4 次课分层一样：模板里的逻辑**测不到、看不见、AI 改起来最容易出错**。

### 7.3 自动转义：第三道结构性护栏（**本单元核心**）

现场做一个实验。发一条问题，标题写：

```
<script>alert('xss')</script>
```

打开列表页。看到的是：

```
<script>alert('xss')</script>
```

**页面上原样显示这行文字，没有弹窗。** 查看网页源码：

```html
<li><a href="...">&lt;script&gt;alert(&#39;xss&#39;)&lt;/script&gt;</a></li>
```

> Jinja2 **默认**把 `<`、`>`、`&`、`"`、`'` 转成了 HTML 实体。恶意标签变成了普普通通的文字。
>
> **注意"默认"这个词。** 你什么都没做，这道防护就在那里。

把它归到本课程的主线上（醒目页）：

> **这是本课程第三道结构性护栏。**
>
> | 次课 | 护栏 | 它自动挡住了什么 |
> |---|---|---|
> | 第 3 次课 | `response_model` | 没声明的字段出不去 |
> | 第 4 次课 | 全局异常处理器 | 内部错误信息不会泄漏给客户端 |
> | **今天** | **Jinja2 自动转义** | **用户输入不会变成可执行的 HTML** |
>
> 三者的共同点：**默认安全，不依赖开发者记得做某件事。**

然后是 `| safe`：

```html
<div class="body">{{ q.body | safe }}</div>     <!-- 解剖台里的那一行 -->
```

改成 `| safe` 再试一次：**弹窗出现了。**

> `| safe` 的意思是"我保证这段内容是安全的，别转义"。
>
> **它是一个手动关闭护栏的开关。**
>
> 什么时候真的需要它？当你要渲染用户写的 Markdown 转成的 HTML 时。那时候正确的做法是：**Markdown 转 HTML 之后先过一遍白名单清洗（sanitize），清洗后的结果才配用 `| safe`。**
>
> 判据：**`| safe` 后面跟的内容，必须来自一个你能指出名字的清洗函数。** 直接跟用户输入就是漏洞。
>
> 〔**第 15 次课**会完整做一遍：从这一行开始，演示 XSS 能偷到什么，然后做清洗。今天你只要知道这个开关在哪、它关掉了什么。〕

### 7.4 C 档卡（一句话各一条）

- 宏 `{% macro %}`：复用带参数的片段，比 `include` 更适合表单控件、分页条。
- 自定义过滤器：`templates.env.filters["ago"] = humanize_ago`——把时间格式化逻辑从模板里拿出来。
- `TemplateResponse` 必须传 `{"request": request}`，因为 `url_for` 需要它。
- 模板目录组织：`templates/base.html` + `templates/questions/*.html` + `templates/_partials/*.html`。

---

## 八、现场必做 C：表单闭环与 PRG

**约 15 分钟。本次课第二高光，不能压缩。**

### 8.1 先把 F5 的机制讲清楚

回到解剖台的重复发帖，画一张时序图：

```
用户填表 → POST /ui/questions → 服务端插入 → 返回 200 + HTML
                                                    │
                    浏览器地址栏：/ui/questions       │  ← 注意这里
                    浏览器记住的："这页是 POST 来的"   │
                                                    ▼
用户按 F5 → 浏览器："我要重放刚才那次 POST" → 又插入一条
```

> **问题的根源是：浏览器认为"当前页面 = 一次 POST 的结果"，所以刷新就是重放那次 POST。**
>
> 这不是浏览器的 bug，是 HTTP 的语义：POST 不是幂等的，浏览器不敢自己决定要不要重发，所以它问你，而用户永远会点"确定"。
>
> 顺带回收第 2 次课：**GET 幂等、POST 不幂等**，当时这是一句抽象的话。现在它变成了数据库里多出来的两条记录。

### 8.2 PRG：Post / Redirect / Get

```
用户填表 → POST /ui/questions → 插入 → 303 See Other, Location: /ui/questions/9
                                            │
                          浏览器自动发起 →  GET /ui/questions/9 → 200 + HTML
                                            │
                    浏览器地址栏：/ui/questions/9
                    浏览器记住的："这页是 GET 来的"
                                            ▼
                      用户按 F5 → 重放 GET → 只是再查一次 ✅
```

```python
from fastapi import status
from fastapi.responses import RedirectResponse

@router.post("/ui/questions")
def submit_question(
    title: str = Form(...),
    body: str = Form(...),
    conn=Depends(get_conn),
):
    q = svc.create(conn, title, body, author_id=1)
    return RedirectResponse(
        url=f"/ui/questions/{q.id}",
        status_code=status.HTTP_303_SEE_OTHER,
    )
```

**现场验证**：提交 → 看地址栏变了 → **按 F5 三次** → 数据库里还是一条。

### 8.3 为什么是 303，不是 302

这个问题值得单独一页，因为它是"读规范"的一次小训练：

| 状态码 | 规范说什么 | 实际后果 |
|---|---|---|
| **301 / 302** | 原本未明确规定重定向后用什么方法 | 历史上浏览器实现不一致；部分客户端会**保留 POST 方法**去请求新地址 |
| **303 See Other** | **明确要求：改用 GET 请求新地址** | 这正是 PRG 需要的语义 |
| **307 / 308** | **明确要求：保持原方法和请求体** | POST 后用它 = 重放 POST，**恰好是我们要避免的** |

> **判据：表单提交成功后重定向，用 303。**
>
> 顺便警惕 307/308：它们的存在是为了让重定向**不改变**方法。用在 PRG 上等于什么都没做——而且 AI 有时会给你 307，因为 FastAPI 的 `RedirectResponse` 默认值是 307。
>
> **`RedirectResponse` 的默认状态码是 307，你必须显式写 303。** 这是一个"默认值不是你想要的"的实例，值得记住。

### 8.4 校验失败的那条路：**不能重定向**

先提问：

> 用户标题只写了两个字，校验失败。按刚才的思路，是不是也重定向回表单页？

让学生想 20 秒，然后指出问题：

> 如果重定向回 `/ui/questions/new`，浏览器发一个全新的 GET 请求——**用户刚才辛辛苦苦填的那 500 字正文，全没了。**
>
> 这是真实产品里最招人骂的体验之一。

**正确的分叉（本单元核心，做成一页）**：

```
POST /ui/questions
   │
   ├── 校验失败 → 200（或 422）+ 重新渲染表单页
   │              带上：错误信息 + 用户原来填的值
   │              ⚠ 不重定向，因为要保住用户的输入
   │
   └── 成功    → 303 重定向到详情页
                  ⚠ 必须重定向，因为要防止刷新重提交
```

```python
@router.post("/ui/questions")
def submit_question(
    request: Request,
    title: str = Form(""),
    body: str = Form(""),
    conn=Depends(get_conn),
):
    # HTML 表单路径要自己收窄，因为不能让 422 直接抛给用户看
    errors = {}
    if len(title.strip()) < 5:
        errors["title"] = "标题至少 5 个字"
    if len(body.strip()) < 10:
        errors["body"] = "正文至少 10 个字"

    if errors:
        return templates.TemplateResponse(
            "question_form.html",
            {"request": request, "errors": errors,
             "values": {"title": title, "body": body}},   # ← 回填
            status_code=422,
        )

    try:
        q = svc.create(conn, title.strip(), body.strip(), author_id=1)
    except DuplicateTitle as e:                            # ← 业务错误也要回填
        return templates.TemplateResponse(
            "question_form.html",
            {"request": request, "errors": {"title": e.message},
             "values": {"title": title, "body": body}},
            status_code=409,
        )

    return RedirectResponse(f"/ui/questions/{q.id}", status_code=303)
```

```html
<!-- question_form.html 节选 -->
<form method="post" action="/ui/questions">
  <label>标题
    <input name="title" value="{{ values.title | default('') }}">
    {% if errors.title %}<span class="err">{{ errors.title }}</span>{% endif %}
  </label>
  <label>正文
    <textarea name="body">{{ values.body | default('') }}</textarea>
    {% if errors.body %}<span class="err">{{ errors.body }}</span>{% endif %}
  </label>
  <button type="submit">发布</button>
</form>
```

**现场演示**：故意填错 → 看到错误提示**且正文还在** → 改对 → 提交成功 → F5 不重复。

**一个必须承认的欠账**（不要掩饰）：

> 你们会发现一个问题：**上面那些 `if len(title) < 5` 是手写的校验，第 3 次课刚说过"能表达为约束的不要写成 if"。**
>
> 我知道。这里的困难是真实的：Pydantic 校验失败会抛 `RequestValidationError`，我们的处理器会返回 **JSON 422**——可是 HTML 表单的用户要的是**一个带回填的页面**，不是一段 JSON。
>
> 正确的解法是：**让 schema 仍然是唯一的规则来源，但在 HTML 路由上换一种处理方式**——比如手工调用 `QuestionCreate.model_validate()` 并捕获 `ValidationError`，把 `e.errors()` 映射成表单错误字典。这样规则只在 schema 里定义一次。
>
> **这是 B 档作业的选做项。** 今天课上用手写版本，是为了先把 PRG 这条主线讲透，不被校验的细节打断。**但我不希望你们以为手写校验是对的。**

〔挂欠账 → B 档作业；第 8 次课讲前后端分离时会重新讨论"同一套规则服务两种客户端"〕

### 8.5 flash message：重定向之后怎么说"成功了"

问题：重定向到详情页之后，怎么告诉用户"发布成功"？变量传不过去——那是一次全新的 GET 请求。

> 这是一个状态需要跨越两次请求的场景。办法：**把消息存在服务端会话里，下一次渲染时取出来并删掉。**

```python
# 极简实现：依赖 SessionMiddleware
@router.post("/ui/questions")
def submit_question(request: Request, ...):
    ...
    request.session["flash"] = {"level": "success", "text": "发布成功"}
    return RedirectResponse(f"/ui/questions/{q.id}", status_code=303)
```

```python
# app/deps.py —— 取一次就删
def pop_flash(request: Request) -> dict | None:
    return request.session.pop("flash", None)
```

```html
{% if flash %}<div class="flash {{ flash.level }}">{{ flash.text }}</div>{% endif %}
```

**三个要说的点**：

1. **"取一次就删"是 flash 的定义。** 用 `pop` 不用 `get`，否则用户每次刷新都看到"发布成功"。
2. **这是本课程第一次出现服务端会话。** `SessionMiddleware` 用签名 cookie 存数据——它能防篡改，但**不加密**，所以里面不能放敏感信息。
3 **欠账**：`SessionMiddleware` 的 `secret_key` 从哪来？→ 第 4 次课的 `settings.secret_key`。会话与登录的完整机制、cookie 的 `HttpOnly`/`Secure`/`SameSite` → **第 14 次课**。

### 8.6 小结：HTML 表单与 JSON API 的差异表

**这张表是第 8 次课（前后端分离）的直接铺垫，请保留。**

| | JSON API | HTML 表单 |
|---|---|---|
| Content-Type | `application/json` | `application/x-www-form-urlencoded` |
| 接参 | Pydantic 模型 | `Form(...)` |
| 校验失败 | 返回 422 JSON，前端自己回填 | **服务端重渲染 + 回填** |
| 成功 | 返回 201 + 资源体 | **303 重定向** |
| 谁处理"刷新重提交" | 前端（不会重放） | **服务端（靠 PRG）** |
| 一次性提示 | 前端状态管理 | **flash（服务端会话）** |
| 共用的部分 | **`services/` 和 `repositories/` 完全一样** | ← 这就是分层的回报 |

> 最后一行请重读一遍。**今天我们加了一整套 HTML 界面，业务层一行没改。**

### 材料

- tag `v5-prg`（本单元结束状态）。
- **封面级素材**：两张时序图上下对照——上"POST → 200 HTML → F5 重放 POST → 多一条"，下"POST → 303 → GET → F5 重放 GET → 安全"。
- **封面级素材**：校验失败/成功的两条路径分叉图。
- 截图：F5 三次后数据库里三条重复记录的 SQL 查询结果（**修复前**）；以及修复后 F5 三次仍只有一条。
- 截图：填错后的表单页，错误提示 + 正文仍在。
- 截图：XSS 实验的两种结果（转义后原样显示 / `| safe` 后弹窗）。

---

## 九、C 档结论卡

**约 4 分钟。时间不够整体跳过，转为课后自读。**

### 9.1 CORS 中间件为什么必须最外层

> 浏览器的跨域预检（`OPTIONS`）请求，**在任何业务逻辑之前就要被正确应答**。如果 CORS 中间件在内层，预检请求可能先被路由匹配、被认证中间件拦下，然后浏览器直接判定跨域失败。
>
> 更隐蔽的一条：**错误响应也必须带 CORS 头。** 如果你的 500 响应没有 `Access-Control-Allow-Origin`，浏览器会拒绝把响应交给 JS——前端只能看到一个"Network Error"，**连你精心设计的统一错误体都读不到**。
>
> 而 500 响应是 `ServerErrorMiddleware` 生成的（单元 3 讲过它在最外层），所以 CORS 必须更外或紧邻其外。
>
> → **第 12 次课会现场踩这个坑**，那时回到这一页。

### 9.2 一句话结论卡

| 问题 | 结论 | 展开处 |
|---|---|---|
| `BaseHTTPMiddleware` 的坑 | 读过 body 后端点读不到；与流式响应交互异常；有额外开销。规模上来后改纯 ASGI 中间件 | 自读 Starlette 源码 |
| `contextvars` 传 request_id | 比 `request.state` 更通用，后台任务里也能拿到 | 自读 |
| `run_in_threadpool` 与线程池大小 | AnyIO 默认约 40，可通过 `anyio.to_thread.current_default_thread_limiter()` 调整 | 第 16 次课 |
| CPU 密集怎么办 | 进程池，或移出请求路径进任务队列 | 第 16 次课 |
| `| safe` 与 Markdown | 先 sanitize 白名单清洗，再 safe | **第 15 次课** |
| Jinja2 宏与过滤器组织 | 见单元 7.4 | 自读 |

### 9.3 跨栈落点对照

| 能力 | FastAPI | Flask | Django | Express | Spring |
|---|---|---|---|---|---|
| 中间件 | `add_middleware` / ASGI | `before_request` / WSGI middleware | `MIDDLEWARE` 列表 | `app.use()` | `Filter` / `Interceptor` |
| 顺序语义 | **后注册在外** | 列表顺序 | 列表顺序（**先声明在外**） | **先注册先执行** | `@Order` |
| 模板自动转义 | Jinja2 默认开 | Jinja2 默认开 | DTL 默认开 | **EJS 默认不转义**（`<%= %>` 转义，`<%- %>` 不转义） | Thymeleaf 默认开 |
| PRG 支持 | 手写 303 | 手写 303 | `redirect()` + messages 框架 | `res.redirect(303)` | `redirect:` 前缀 |
| flash | 需 SessionMiddleware | `flash()` 内建 | `messages` 内建 | `connect-flash` | `RedirectAttributes` |

> 注意第二行：**各框架的中间件顺序语义不一致，Express 和 FastAPI 正好相反。** 换栈时这是必查项，不要靠记忆。
>
> 注意第三行：**不是所有模板引擎都默认转义。** 用 EJS 的项目 XSS 风险显著更高——这不是语言问题，是默认值问题。

---

## 十、M1 交付与作业

**约 6 分钟。本次课是里程碑交付，请给足时间讲清验收标准。**

### 10.1 M1 交付清单

> M1 的目标：**一个能点、能用、结构清楚的最小问答应用。**
>
> 它不需要好看，不需要功能多。它需要**每一处都说得出为什么这么写**。

**功能要求**：

| # | 内容 | 验收方式 |
|---|---|---|
| 1 | 六个 JSON 端点（第 3 次课清单） | `/docs` 全部可试通 |
| 2 | 三个 HTML 页面：列表、详情、发帖表单 | 浏览器完整走一遍 |
| 3 | 发帖表单闭环：校验失败回填、成功 303、flash 提示 | **现场按 F5 三次，数据不重复** |
| 4 | `/healthz` 返回依赖状态 | 停掉数据库后返回 503 |

**结构要求（沿用并累加前几次课的硬性标准）**：

| # | 要求 | 自检 |
|---|---|---|
| 5 | 分层目录，`services/` 无 `import fastapi` | `scripts/check_layering.sh` |
| 6 | 每个路由函数 ≤ 10 行 | 同上 |
| 7 | 所有端点有 `response_model`（HTML 端点除外） | 同上 |
| 8 | 错误响应统一为 `code/message/detail/request_id` | 同上 |
| 9 | 配置走 pydantic-settings，`.env` 不入仓，`.env.example` 已提交 | 同上 |
| 10 | 所有端点与依赖的 `def`/`async def` 选择正确 | **作业三逐个说明** |
| 11 | 日志含 request_id，**异常路径也有** | 触发 500 后查日志 |
| 12 | 模板中 `\| safe` 出现处 **≤ 0 处**（M1 阶段一律不许用） | grep |

**交付物**：

- Git 仓库（含完整提交历史，**不要 squash**——历史是过程的证据）；
- `README.md`：启动步骤、`.env` 说明、已知欠账清单；
- `docs/decisions.md`：**至少三条设计决定及理由**（格式见下）。

`docs/decisions.md` 的格式（每条不超过 5 行）：

```
## D-003 外链抓取端点使用 def 而非 async def
- 决定：写成 def，由框架放入线程池
- 理由：函数体内 requests.get 与 conn.execute 均为同步阻塞
- 备选方案：改 httpx.AsyncClient + 异步驱动
- 未采用的原因：数据库层仍为同步 SQLAlchemy，全链路改造成本不划算
- 何时应重新考虑：该端点 QPS 超过线程池上限时
```

> 最后一行"何时应重新考虑"是我特别要求的。**一个决定如果没有失效条件，它就不是决定，是信仰。**

### 10.2 作业一：阻塞实验数据表（B 档，必交）

重跑单元 5 的实验，提交完整数据表，**至少包含**：

| 端点 | worker 数 | 并发 | 吞吐 req/s | p50 | p95 |
|---|---|---|---|---|---|

行数要求：`/lab/a` `/lab/b` `/lab/c` `/lab/d` × 并发 {1, 10, 50} = 12 行，**外加** `/lab/a` 在 `--workers 4` 下的 3 行。

**必答三问**（这才是作业的重点）：

1. 你在跑 `--workers 4` 之前**预测**吞吐是多少？实测是多少？差异说明了什么？
2. `/lab/c` 在并发 50 时为什么达不到 100 req/s？上限由什么决定？
3. `/lab/d` 写的是 `def`，为什么也串行了？**如果要提高它的吞吐，你有哪两条路，各自的代价是什么？**

### 10.3 作业二：PRG 与表单闭环（随 M1 交付）

- 提交发帖表单的完整流程截图三张：校验失败（含回填）、成功后地址栏、F5 三次后的数据库查询结果；
- 说明为什么用 303 而不是 302 或 307；
- **B 档选做**：把手写的 `if len(title) < 5` 改成复用 `QuestionCreate` schema，捕获 `ValidationError` 后映射成表单错误字典。**做了这一项的，单元 8.4 那笔欠账就算你自己还了。**

### 10.4 作业三：`def`/`async def` 判据说明（**本次课的课程主题作业**）

**第一部分：全项目盘点。** 列出项目中所有端点和依赖，填表：

| 函数 | 位置 | `def` / `async def` | 函数体内的阻塞调用 | 是否正确 | 理由 |
|---|---|---|---|---|---|

**第二部分：AI 对照实验（必做）。**

1. 用这个提示词请 AI 写一个新端点（原样使用，抄进作业）：

   > 给我的 FastAPI 项目加一个端点 `GET /questions/{qid}/summary`，它从数据库读取问题正文，调用外部 HTTP 接口（`https://api.example.com/summarize`）做摘要，返回摘要文本。

2. **原样保存** AI 的输出。

3. 回答：

   | 问题 | 你的回答 |
   |---|---|
   | AI 写的是 `def` 还是 `async def`？ | |
   | 它用了什么库做 HTTP 调用？那个库是同步还是异步？ | |
   | 按单元 6.1 的判据，它对吗？**引用判据表里的具体一行** | |
   | 如果直接上线，在并发 50 时会发生什么？**估算吞吐** | |
   | 这个错误能被 code review 发现吗？能被单元测试发现吗？为什么？ | |
   | 你打算用单元 6.4 的哪一层护栏来防住它？具体怎么做？ | |

**评分重点是最后两问。** 前面几问答对不难，能说清"为什么常规检查抓不住它"才说明你真的理解了这类错误的性质。

### 本次课新增的欠账登记

| 欠账 | 何时还 |
|---|---|
| CORS 中间件位置与错误响应的 CORS 头 | **第 12 次课** |
| `\| safe` 与 XSS 完整演示、sanitize | **第 15 次课** |
| 会话、cookie 属性、登录 | **第 14 次课** |
| `author_id=1` 硬编码 | 第 14 次课 |
| 表单缺少 CSRF 防护 | **第 15 次课** |
| HTML 表单复用 schema 校验（若未做 B 档选做） | 第 8 次课 |
| `async def` 检查进 CI | **第 9 次课** |
| 压测基线固化 | 第 9、16 次课 |
| CPU 密集移出请求路径 | **第 16 次课** |
| 外部 HTTP 调用的超时、重试、熔断 | 第 16 次课 |
| worker 数 × 连接池 × 数据库上限的联合计算 | 第 16 次课 |
| 纯 ASGI 中间件改写 | 课后自读 |

---

## 十一、素材清单与制作说明

### 必需素材

| 素材 | 说明 |
|---|---|
| tag `v5-broken` | 起始版：含 `async def` + `requests`、POST 直接返回 HTML、模板里的 `\| safe`。**三个问题必须稳定复现** |
| tag `v5-middleware` | 单元 3 结束状态 |
| tag `v5-lab` | 含 `/lab/a~d` 四个实验端点 |
| tag `v5-prg` | 单元 8 结束状态 |
| tag `v5-m1` | M1 参考交付状态 |
| `scripts/bench.py` | 压测脚本。**必须在 macOS / Windows / Linux 各验证一次**；输出格式固定以便学生填表 |
| `scripts/check_layering.sh` | 扩展第 4 次课版本，新增 M1 的 7、10、12 三条检查 |
| **封面级素材 A** | 单元 5.3 的四行数据表，`/lab/a` 行三个 `2.0` 红框高亮 |
| **封面级素材 B** | `a()` / `b()` 两段代码并排，差异行高亮，底部"47×" |
| **封面级素材 C** | 单元 5.2 并发 1 下三端点数据完全相同的截图，配字"所有常规检查都通不过这道题" |
| **封面级素材 D** | PRG 前后两张时序图上下对照 |
| 高光图 E | 补全版六层洋葱图（**与第 4 次课同风格，需可叠加**） |
| 高光图 F | 校验失败 / 成功 两条路径分叉图 |
| 表 G | 三种并发模型结论表 |
| 表 H | `def`/`async def` 决策清单 |
| 表 I | JSON API vs HTML 表单差异表（**第 8 次课要复用**） |
| 表 J | 三道结构性护栏累计表（第 3、4、5 次课各一道） |
| 截图 | `app.user_middleware` 打印；中间件 enter/exit 顺序 |
| 截图 | try/finally 修法下"日志有、头无"的同屏对照 |
| 截图 | F5 三次 → 三条重复记录的 SQL 结果（修复前 / 修复后各一张） |
| 截图 | XSS 实验：转义后原样显示 / `\| safe` 后弹窗 |
| 截图 | 表单校验失败页（错误提示 + 正文保留） |

### 可后补

- 跨栈落点对照表、C 档一句话卡（纯文字）。
- Jinja2 语法示例（代码已在文中）。

### 备用材料

| 风险 | 备用方案 |
|---|---|
| **教室网络导致压测数据抖动**（最高风险） | 实验端点全部用 `sleep` 而非真实网络调用，**不依赖外网**；另备预录 90 秒实验录像 |
| `/lab/a` 在演示机上没有完全串行 | 检查 `--workers 1`、检查是否有 `--reload`（reload 模式会影响行为）；底稿给出了理论值用于自检 |
| AI 现场调用失败（作业三演示） | 准备一份预先生成并验证的"`async def` + `requests`"输出作为讲评素材，标注"预录产物" |
| 浏览器不弹"确认重新提交"（部分浏览器已改行为） | 备用：用 curl 手工重放 POST 演示同一后果；或用旧版行为的录屏 |
| SessionMiddleware 未装 / secret_key 未配 | `v5-prg` tag 已配好；flash 部分可降级为"用 query 参数 `?flash=created` 传递"，**并说明它的缺点（可被伪造、会留在地址栏）** |
| 时间超支 | 按单元 0 的压缩顺序执行；Jinja2 单元有独立自读材料 `docs/jinja2_minimal.md` |

### 环境与运行条件

延用前序环境。**新增依赖**：`jinja2`、`itsdangerous`（SessionMiddleware 需要）、`httpx`（压测脚本）、`requests`（作为反例保留）。

**演示开始时的初始状态**：工作区在 tag `v5-broken`；数据库已 seed；服务以 `--workers 1` 且**不带 `--reload`** 启动（reload 会影响并发实验）；浏览器打开发帖表单页；另开一个终端准备跑压测。

**复位方式**：`git checkout v5-broken -- app/ && make reset-db`。

---

## 十二、与前后课的衔接

**本次课回收的前序埋点**：

| 来源 | 埋点 | 回收位置 |
|---|---|---|
| 第 1 次课 | 中间件在异常路径失灵（第 4 次课修一半） | **单元 3.4 彻底修好** |
| 第 2 次课 | GET 幂等 / POST 不幂等 | 单元 8.1（变成数据库里多出的两条记录） |
| 第 2 次课 | 四种请求编码中的 `x-www-form-urlencoded` | 单元 8（`Form(...)`，还清欠账） |
| 第 3 次课 | 8 行裸 ASGI 应用 | 单元 4.1（对照 WSGI）、单元 3.5 |
| 第 3 次课 | "结构性护栏" | 单元 7.3（自动转义是第三道） |
| 第 3 次课 | "能表达为约束的不要写成 if" | 单元 8.4（如实承认 HTML 路径的困难） |
| 第 4 次课 | 洋葱层次图 | **单元 1、3.2 直接复用并补全** |
| 第 4 次课 | 中间件顺序 | 单元 3.1–3.3 |
| 第 4 次课 | 所有依赖都写 `def`"这是有意的" | **单元 6.2 揭晓原因** |
| 第 4 次课 | 分层的回报在"被修改"时 | **单元 2 结尾 + 单元 8.6 兑现：加整套 HTML，业务层零改动** |
| 第 4 次课 | `settings.secret_key` | 单元 8.5（SessionMiddleware 用它） |
| 第 4 次课 | 认证不该写成中间件 | 单元 3.3 顺序表 |

**本次课埋下、后面必须回引的五处**（请在课件中明显标记）：

- **单元 7.3 的 `| safe`** → 第 15 次课从这一行开始做 XSS 完整演示；
- **单元 9.1 CORS 必须最外层** → 第 12 次课会先踩坑再回到这一页；
- **单元 8.6 那张 JSON vs HTML 对照表** → 第 8 次课讲前后端分离时直接复用，回答"分离解决了什么、代价是什么"；
- **单元 6.4 三层护栏中的"CI 机械检查"** → 第 9 次课实现；
- **单元 6.3 worker × 连接池 × 数据库上限** → 第 16 次课联合计算。

**本次课不承担、请勿提前引入**：ORM 与 Session（第 7 次课）、测试（第 9 次课）、前后端分离与 CORS 实操（第 12 次课）、认证与会话完整机制（第 14 次课）、XSS / CSRF 防护（第 15 次课）、任务队列与部署（第 16 次课）。

**给第 6 次课的提示**：本次课交付的 M1 里，`GET /questions` 用的是 `LIMIT/OFFSET` 分页且数据量很小（seed 只有几十条）。**第 6 次课请在 M1 的基础上把数据灌到十万级**，让 OFFSET 分页和缺索引的问题自己浮出来——这是"痛感在前"的下一次应用。