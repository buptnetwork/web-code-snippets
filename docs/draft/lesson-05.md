# 第 5 次课教学底稿（修订版）
## 请求执行方式与 SSR 表单闭环 ｜ 交付 M1

## 〇、备课定位与内容取舍

本课承接第四课的可控重构：同一套业务规则开始服务 JSON 与 HTML 两种客户端，同时检查请求究竟在哪里执行。主线是：**能返回正确结果，还要说明等待发生在哪里、失败如何结束、浏览器下一次会发什么请求。**

原稿把中间件、四组并发实验、模板、表单、flash 都列为不可压缩的现场任务；加上缓冲实际超过 100 分钟。本版保留完整的机制、分支与课后参考，取消“必须出现固定倍数”“刷新必须插入三条”“常规检查绝不可能发现”的叙事。

学生不需要先会 React/Vue。课堂使用给定样式和模板骨架，不考 CSS 布局。下面的代码按职责分段，是教学参考，不代表本仓库已经存在独立的第五课演示工程。

### 课堂路线：95 分钟教学 + 5 分钟缓冲

| 单元 | 分钟 | 课堂处理 |
|---|---:|---|
| 一、交付起点与两个现象 | 5 | 教师展示同一业务的两种入口 |
| 二、解剖台与实验控制 | 8 | 只定位阻塞、POST 结果页两个问题 |
| 三、中间件与异常路径 | 10 | 教师演示顺序和失败证据；完整代码课后读 |
| 四、并发模型与调度 | 10 | 主讲框架调度与普通调用的区别 |
| 五、受控并发实验 | 18 | 学生现场必做；中间停下来核对单请求基线 |
| 六、端点选择判据 | 8 | 沿一条调用链判断，不盘点全项目 |
| 七、模板与自动转义 | 10 | 主讲继承、插值、回填和转义 |
| 八、表单完整闭环 | 20 | 前 10 分钟校验与错误，后 10 分钟提交与 PRG |
| 九、M1 验收与收尾 | 6 | 展示基础清单，定位课后阅读 |
| 合计 | 95 | 另留 5 分钟缓冲 |

**A 档**是所有学生应完成的基础能力，可在课堂、教师演示或课后阅读中获得；**B 档**是选做拓展。flash、CPU、多 worker、纯 ASGI 中间件不占上述主线时间。超时先将中间件完整实现和并发模型跨栈讨论转为课后读，保留并发结果解释与表单两条路径。

### 跨课交接基线

- 保留 `GET /questions`、`GET /questions/{qid}`、`POST /questions` 三个核心 JSON 端点，不要求补回旧稿中的六端点清单。
- 第三课集合契约为 `QuestionListOut`：`items/total/page`；查询参数统一为 `keyword/page/page_size`，`page_size` 默认 20、上限 50。第四课依赖中的内部 `Page.size` 可以保留，但对外必须接 `page_size`，不能悄悄换成 `size`。
- 第三课详情/创建响应沿用 `id/title/body/created_at/author`，创建成功为 201。第一课的 `success/data` 是更早阶段，若项目尚未迁移，先记录契约变更并同步客户端，不在实验中混用两种格式。
- `/healthz` 继续保留：200 为 `{"status":"ok","db":"ok"}`；依赖不可用为 503 和 `{"status":"degraded","db":"down"}`。它不是可选功能，也不强行套业务错误体。
- JSON 业务错误沿用 `code/message/detail/request_id`；HTML 错误渲染页面，两种表现共用业务异常。未知错误不得暴露 SQL、栈、凭据或用户原始正文。
- 标题唯一是本课程已有业务约定。不得撤掉它，只为演示刷新造成重复数据。
- M1 仍使用给定同步持久层；需要查库的端点使用 `def`。复用第三课先 `strip`、后约束的校验器；第八单元展示同一模型如何接入表单，两种入口一起回归。

## 一、开场：增加界面，不复制业务

**课堂 5 分钟。**

让学生对照一次 JSON 创建和一次 HTML 表单提交：传输格式不同，但“标题长度”“正文长度”“标题冲突”等规则不应复制两份。

```text
JSON 请求 → JSON 入口 ─┐
                      ├→ 同一个 schema → service → repository → 数据库
HTML 表单 → 表单入口 ─┘
```

讲：第四课分层的收益不是保证以后“业务层一行不用改”，而是让变化有边界。新增 HTML 主要改变输入适配和输出表现；合格第四课的 service 已返回DTO，不含HTTP输出或隐藏提交，本课直接复用。若学生实现偏离该基线，先按交接检查修正，不把旧缺陷当作全班共同起点。

本课结束时应能回答：

1. 同步函数何时在线程池，何时仍在事件循环中？
2. 一次正常请求和一次未知异常，日志与响应头各在哪一层生成？
3. 表单校验失败怎样保留用户输入？
4. 成功创建何时才可以发送 303？
5. PRG 解决什么，不解决什么？

## 二、解剖台：一次只保留一个预期缺陷

**课堂 8 分钟。** 故障代码是人为控制的教学样例，不宣称来自某次真实 AI 输出。真实 AI 产物需另外保存来源和上下文。

### 2.1 阻塞反例

```python
import time
from fastapi import APIRouter

router = APIRouter()

@router.get("/lab/a")
async def blocking_wait():
    time.sleep(0.5)
    return {"ok": True}
```

单请求看似正常；多请求共享一个 worker 时，等待期间事件循环不能处理其他任务。延迟可能影响同 worker 的健康检查，但多 worker 或独立探针会改变现象，不能推广成“整个部署必然挂掉”。

本例不查询数据库、不抓真实网址，不需要不存在的 `link_url` 字段。`time.sleep` 只模拟同步等待；真实调用还要考虑超时、连接池、失败与限流。

### 2.2 POST 直接返回详情页

```python
# 预期缺陷片段：其余校验、事务和错误处理沿用修复版。
# 创建成功后仍返回 POST 的结果页，而不是重定向。
return templates.TemplateResponse(
    request=request,
    name="question_detail.html",
    context={"q": question},
)
```

在 Network 中保留日志，提交后刷新，观察浏览器是否确认重发 POST。浏览器行为可能不同，备用证据使用预录记录；手工重发请求只能证明重放后果，不能冒充浏览器 F5 证据。

**本项目的预期**：第一次创建成功，再次同标题 POST 应被业务规则或数据库唯一约束挡住，返回 409。问题仍是浏览器停留在 POST 结果页，重复发送写请求；不是要求数据库一定新增重复行。

讲：单次成功断言没有覆盖并发或重放场景，但代码审查、针对性的静态规则、并发测试和失败路径测试都可能发现这些问题。不把“现有检查未覆盖”说成“检查不可能发现”。

## 三、中间件：顺序与异常不是同一个问题

**课堂 10 分钟，完整实现为 A 档课后阅读。**

### 3.1 先打印顺序

```python
@app.middleware("http")
async def mw_a(request, call_next):
    print("A enter")
    response = await call_next(request)
    print("A exit")
    return response

@app.middleware("http")
async def mw_b(request, call_next):
    print("B enter")
    response = await call_next(request)
    print("B exit")
    return response
```

正常响应的顺序为 `B enter → A enter → A exit → B exit`。最后注册的是最外面的**用户中间件**，不是整个应用的最外层。

```text
ServerErrorMiddleware（未知异常的兜底响应）
  → 用户中间件 B
    → 用户中间件 A
      → ExceptionMiddleware（已注册业务异常、HTTP 错误）
        → 路由 / 依赖 / 端点
```

对于未知异常，`call_next` 可能抛出而不是返回响应。先定位边界，再决定改什么。认证授权依赖适合本课程的按端点需求，但并非所有系统都禁止认证中间件。

### 3.2 日志与响应头分别处理

以下适用于普通非流式响应，且 `debug=False`。第四课已给出最小finally日志和500补头，本课深化顺序并新增HTML错误表现；不要同时安装两份关联中间件或撤回学生已有正确实现。沿用第一课 request-id（含合法点号）：接受符合约束的标识，否则重新生成；不把不可信长字符串直接写日志。

```python
import logging
import re
import time
import uuid
from fastapi import Request
from fastapi.responses import HTMLResponse, JSONResponse

logger = logging.getLogger("app.requests")
RID = re.compile(r"[A-Za-z0-9._-]{1,64}\Z")

@app.middleware("http")
async def timing(request: Request, call_next):
    incoming = request.headers.get("X-Request-ID", "")
    rid = incoming if RID.fullmatch(incoming) else uuid.uuid4().hex
    request.state.request_id = rid
    started = time.perf_counter()
    outcome = "error"
    logger.info("[%s] --> %s %s", rid, request.method, request.url.path)
    try:
        response = await call_next(request)
        outcome = str(response.status_code)
        response.headers["X-Request-ID"] = rid
        return response
    finally:
        logger.info("[%s] <-- %s %.1fms", rid, outcome,
                    (time.perf_counter() - started) * 1000)

@app.exception_handler(Exception)
async def handle_unexpected(request: Request, exc: Exception):
    rid = getattr(request.state, "request_id", uuid.uuid4().hex)
    logger.error("unhandled rid=%s", rid,
                 exc_info=(type(exc), exc, exc.__traceback__))
    headers = {"X-Request-ID": rid}
    if request.url.path.startswith("/ui/"):
        return HTMLResponse("服务器内部错误，请稍后重试。", 500, headers=headers)
    return JSONResponse(
        status_code=500,
        content={"code": "internal_error", "message": "服务器内部错误",
                 "detail": None, "request_id": rid},
        headers=headers,
    )
```

教师在隔离副本分两步复演：只加 `finally` 时日志恢复，外层生成的 500 不一定带头；再由兜底处理器添加头。业务 409 则由内层处理器转响应，正常经过用户中间件。主线保留第四课已正确的配对日志与补头；日志中的error表示未拿到响应，不是假定实际HTTP状态。

边界必须留在学生可读正文中：

- 这里计时截至拿到响应或异常，不等于流式响应体完整发送时间。
- `finally` 覆盖正常 Python 控制流中的退出；进程强制终止等不能据此保证日志落盘。
- 响应已经开始发送后再发生错误，不能重新发送一份 JSON 500；后台任务失败也不能改写已发响应。
- 自定义纯 ASGI 外包装也可统一处理响应头，兜底处理器不是唯一方案。
- 日志中记录内部栈仍需权限、脱敏和保留策略，不因“不发给客户端”就可任意记录敏感信息。

### 3.3 CORS 与上下文：导读，不在本课搭跨域项目

`app.add_middleware(CORSMiddleware, ...)` 仍在 `ServerErrorMiddleware` 内部。若跨域客户端也必须读取外层产生的 500，可在全部路由注册后包装整个应用：

```python
from starlette.middleware.cors import CORSMiddleware

# api 是已经注册路由与异常处理器的 FastAPI 实例。
app = CORSMiddleware(
    app=api,
    allow_origins=["https://ui.example.com"],
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
    expose_headers=["X-Request-ID"],
)
```

只允许指定源，不为课堂方便开放带凭据的任意跨域。第十二课再做浏览器读取错误响应的完整实验。

`BaseHTTPMiddleware` 有任务与上下文传播边界，具体行为需按版本验证，不沿用“读一次 body 端点就必然读不到”的笼统结论。`contextvars` 也不是跨任务、跨进程、后台任务的万能传值机制。纯 ASGI 改写为 B 档阅读。

## 四、并发模型：先区分调度者

**课堂 10 分钟。**

| 模型 | 核心机制 | 主要限制 |
|---|---|---|
| 进程 | 独立内存与执行环境；每进程仍可有事件循环和线程池 | CPU 配额、内存、各进程数据库连接池总量 |
| 线程池 | 同步等待占住线程，但事件循环可以继续处理其他任务 | 容量令牌、线程资源、下游连接与并发限制 |
| 事件循环 | 协程在可挂起的等待点让出执行权 | 循环上的 CPU 工作、阻塞调用、连接数和下游能力 |

它们可以组合，不能把“一个进程”画成“只能处理一个请求”。WSGI 是同步调用接口，ASGI 是异步消息接口；协议本身不替应用决定 worker 数和数据库调用方式。

### 4.1 FastAPI 的规则及适用范围

- **由框架调用的**同步端点与同步依赖，通常在线程池中执行。
- 异步端点/异步依赖在事件循环中执行；可挂起的异步 I/O 才能让其他任务前进。不是每个 `await` 都一定发生切换。
- **你直接调用的普通函数**仍在当前执行位置运行。`async def` 里调用 `svc.get()`，不会因为 `get` 是 `def` 就自动进入线程池。

```python
# 错误示意：同步查询发生在事件循环线程。
async def bad_endpoint():
    return sync_repository_query()

# 同步栈的简洁选择：框架将端点放入线程池。
def sync_endpoint():
    return sync_repository_query()
```

### 4.2 CPU 与等待不能混为一谈

通常启用 GIL 的 CPython 中，多个线程不能同时执行大量 Python 字节码；线程池可隔离阻塞等待，却不保证纯 Python 计算吞吐增加。原生扩展可能释放 GIL，其他运行时也可能不同。

CPU 工作应先优化算法或用合适的原生实现，再考虑进程池、后台任务和资源预算。即使放到线程池，长计算仍可能通过 CPU 争抢影响服务；不能把它说成万能修复。

## 五、现场必做：三种等待，同一份测量

**课堂 18 分钟。** 先单请求，再提高并发；先保证响应正确，再解释数字。

### 5.1 对照代码

在第二单元 `/lab/a` 之外加两条，三条返回完全相同的响应：

```python
import asyncio

@router.get("/lab/b")
async def async_wait():
    await asyncio.sleep(0.5)
    return {"ok": True}

@router.get("/lab/c")
def thread_wait():
    time.sleep(0.5)
    return {"ok": True}
```

实验工程只在本地开启 `/lab/*`，不注册到最终交付或公开服务。参考启动命令供独立演示工程使用：

```bash
uvicorn app.main:app --workers 1 --log-level warning
```

不启用 reload；使用同一机器、相同 Python/依赖锁定版本、相同客户端连接池。脚本必须复用客户端，不把建连接时间差异混成服务端性能。

### 5.2 测量协议

课程制作阶段需提供并验证 `bench.py`，不能把下列文件名当成本仓库已有命令。参数协议：URL、并发、请求总数；输出总时长、成功/失败/超时数、吞吐、成功请求延迟 p50/p95。

```bash
python scripts/bench.py --url http://127.0.0.1:8000/lab/a --concurrency 1 --total 20
python scripts/bench.py --url http://127.0.0.1:8000/lab/a --concurrency 10 --total 20
```

对 b、c 重复，得到六组。每个请求从实际开始发送到响应体读完计时；并发控制器的等待不混入单请求延迟，总时长则包括整批排队。超时单独计数，不能删掉失败后声称 p95 很低。基础实验客户端超时建议 30 秒。

| 端点 | worker | 并发 | 总请求 | 成功/失败/超时 | 总时长 | 成功吞吐 | p50/p95 |
|---|---:|---:|---:|---|---|---|---|
| a / b / c | 1 | 1 / 10 | 20 | 实测 | 实测 | 实测 | 实测 |

这是一张**待填表**，不是已测数据。课堂单轮用于观察；要下性能结论，预热后多轮重复并记录波动。少量样本的 p95 只作说明，不当作生产容量报告。

### 5.3 如何解释，而不是背倍数

- 单并发时主要在等 0.5 秒，因此三个版本可能接近。
- 忽略开销的理想模型中，a 的吞吐约受 `1 / 0.5s` 限制；真实结果还受网络、队列和计时方式影响。
- b 可以同时等待；c 由线程池容纳多个同步等待。二者都受客户端和服务端容量约束，不能直接宣称异步总更快。
- AnyIO 默认通常有 40 个线程容量令牌，它不是本实验永久固定的线程数，且可能被其他同步工作共享。读取实际配置再解释瓶颈。
- 如果数据不符合预期，先核对进程数、实验代码、请求总数、超时和测量方法；不以偏离某个百分比直接判定实验错误。

讲：有说服力的是“受控变量 + 可重复证据 + 机制解释”，不是在对照图上预先写好 47 倍。

## 六、把实验结论带回项目

**课堂 8 分钟；CPU 与 worker 计算课后自学。**

### 6.1 选择判据

| 调用链 | 本课程选择 | 需要复查的条件 |
|---|---|---|
| 同步 SQLAlchemy、同步 SDK、阻塞文件 I/O | `def` 端点/依赖 | 线程与连接池是否饱和；是否有线程亲和要求 |
| 原生异步 I/O，正确使用异步驱动 | `async def` + `await` | 是否还藏着同步查询或长计算 |
| 很短的纯内存处理 | 均可，保持项目一致性 | 不为“更现代”改写 |
| 长时间 CPU 工作 | 单独评估算法、进程或任务系统 | 不靠改成 `async def` 解决 |

只把 `requests` 换为 `httpx.AsyncClient`，但保留同步 `conn.execute()`，不是“全程异步”。已有同步项目不必因此整栈迁移。

混合场景可显式卸载完整同步工作单元：

```python
from fastapi.concurrency import run_in_threadpool

# 连接在同一个同步工作单元内获取、使用并释放。
def load_summary(qid):
    with engine.connect() as conn:
        row = repo.find_detail(conn, qid)
        return {"id": row.id, "body": row.body}

async def mixed_endpoint(qid):
    data = await run_in_threadpool(load_summary, qid)
    return data
```

此片段只是卸载机制参考；本课没有必要为它新增业务端点。不把已经创建的 Session/Connection 放进多个并行任务共享；若驱动要求同线程，资源生命周期也要在同一个工作单元内。

### 6.2 B 档：固定工作量 CPU 实验

```python
def cpu_work(n: int) -> int:
    result = 0
    for i in range(n):
        result = (result + i * i) % 1_000_000_007
    return result
```

先校准 n，使单任务耗时便于观察，然后在各并发组**保持 n 不变**，核对返回值。不要用“忙等直到墙钟过了 0.5 秒”当固定计算量：并发争抢时每任务执行的循环次数不同，会产生虚假的吞吐提升。

### 6.3 B 档：worker 与连接池

没有通用于 FastAPI 的 `2 × 核数 + 1` 答案。从单 worker 基线开始，按 CPU 配额、内存、延迟目标增加并测量。

```text
部署实例数 × 每实例 worker 数 × (pool_size + max_overflow)
    + 迁移、后台任务、管理连接的预算
    ≤ 数据库可用连接额度
```

这是容量预算，不是活跃连接数的实时等式。多 worker 也会复制内存与连接池。第十六课再结合部署限制计算。

### 6.4 AI 协作的可执行约束

给 AI 的上下文应包括实际数据库驱动、同步/异步调用链、超时预算与验收方法。例如：“本项目使用同步 SQLAlchemy；请复用 service，说明端点为何用 `def`，并列出需要压测的等待点。”

审查调用链、针对性静态规则与并发测试互补。简单 grep 会漏掉包装函数，也会误判异步 `.execute()`，不宣称能覆盖某个固定比例。AI 输出正确时保留方案并给验证证据，不为了凑错而改坏代码。

## 七、Jinja2：最小模板足以完成 M1

**课堂 10 分钟。** 模板负责表现，业务规则仍由 schema/service 决定。

### 7.1 基础模板

```html
<!-- app/templates/base.html：独立演示工程中的建议位置 -->
<!doctype html>
<html lang="zh-CN">
<head><meta charset="utf-8"><title>{% block title %}问答{% endblock %}</title></head>
<body>
  <nav><a href="/ui/questions">问题列表</a> <a href="/ui/questions/new">提问</a></nav>
  {% block content %}{% endblock %}
</body>
</html>
```

```html
<!-- app/templates/question_list.html -->
{% extends "base.html" %}
{% block content %}
<ul>
  {% for q in questions %}
  <li><a href="/ui/questions/{{ q.id }}">{{ q.title }}</a></li>
  {% else %}<li>还没有问题</li>{% endfor %}
</ul>
{% endblock %}
```

```html
<!-- app/templates/question_detail.html -->
{% extends "base.html" %}
{% block title %}{{ q.title }}{% endblock %}
{% block content %}
<h1>{{ q.title }}</h1>
<p class="body">{{ q.body }}</p>
{% endblock %}
```

CSS 可用 `white-space: pre-wrap` 保留正文换行，不必为此插入 `|safe`。课堂主讲插值、循环空态、继承；include、宏、自定义过滤器留自读。

模板可以有简单展示条件，也可以测试。复杂授权/业务判断应在服务端集中执行；隐藏按钮从来不等于实施权限检查。

### 7.2 自动转义的边界

使用 `Jinja2Templates` 配置的 HTML 环境会自动转义；裸 `jinja2.Environment()` 或 `Template()` 不一定开启。不能把集成默认值当成所有 Jinja2 用法的保证。

只在本地隔离样例中，将以下内容放入 **body 字段**，并观察同一个 `q.body` 渲染位置：

```text
<script>alert('xss')</script>
```

先用 `{{ q.body }}`，查看响应源码里的实体；再在隔离反例改为 `{{ q.body | safe }}` 对照，最后恢复转义。若浏览器 CSP 阻止执行，也应记录条件，不把“没弹窗”当无漏洞证明。

自动 HTML 转义不等于任何上下文都安全：脚本、CSS、URL 协议等需要各自的处理。M1 不渲染用户富文本，不使用 `|safe`；第十五课再讲白名单清洗。

跨栈阅读只保留准确结论：EJS 的 `<%=` 会转义、`<%-` 不会；换模板引擎应检查实际语法与配置，不能据此推断某生态的事故率。

## 八、表单：同一套校验，两种响应

**课堂 20 分钟。** 先完成失败分支，再验证提交成功与 PRG。

### 8.1 共享 schema，不退回手写长度判断

下例复列第三课已经采用的共享模型，JSON 与表单使用同一份定义，不另复制一套规则。标题与正文上限沿用第三课；标签最多五个，标签格式和规范化若另有规则，也必须集中维护。

```python
from pydantic import BaseModel, ConfigDict, Field, field_validator

class QuestionCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")
    title: str = Field(min_length=5, max_length=200)
    body: str = Field(min_length=10, max_length=20000)
    tags: list[str] = Field(default_factory=list, max_length=5)

    @field_validator("title", "body", mode="before")
    @classmethod
    def strip_text(cls, value):
        return value.strip() if isinstance(value, str) else value
```

`"    字    "` 清洗后不满足长度，应失败。原始输入保留在表单 values 中，清洗后的 payload 才传给业务层。M1 表单只提供标题与正文，tags 使用默认空列表；已有 JSON 标签行为不得被新表单实现破坏。

### 8.2 表单和模板适配

环境必须包含 `python-multipart`，否则使用 `Form` 可能在注册路由时就报错。以下模板调用采用当前 Starlette 的 request-first/关键字形式，不使用旧的位置参数写法。

```python
from fastapi import Form, Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from pydantic import ValidationError

templates = Jinja2Templates(directory="app/templates")

def render_form(request, values, errors, status_code=200):
    return templates.TemplateResponse(
        request=request, name="question_form.html",
        context={"values": values, "errors": errors},
        status_code=status_code,
    )

# 静态 /new 在动态 /{qid} 之前注册。
@router.get("/ui/questions/new")
def new_question_page(request: Request):
    return render_form(request, {"title": "", "body": ""}, {})

@router.post("/ui/questions")
def submit_question(
    request: Request, conn: ConnDep,
    title: str = Form(""), body: str = Form(""),
):
    values = {"title": title, "body": body}
    request.state.form_values = values
    try:
        payload = QuestionCreate.model_validate(values)
    except ValidationError as exc:
        errors = {}
        for error in exc.errors():
            field = str(error["loc"][0]) if error["loc"] else "form"
            errors.setdefault(field, error["msg"])
        return render_form(request, values, errors, 422)

    # 业务/数据库错误向外抛，先让事务边界回滚，再转成 HTML。
    question = svc.create(conn, payload, author_id=1)
    return RedirectResponse(f"/ui/questions/{question.id}", status_code=303)
```

`ConnDep` 见下一节；`svc.create(conn, payload, author_id)` 是参考适配接口，内部可调用已有 repository，但不得自己提交。返回能在当前事务内取到 id 的对象或 DTO。若现有函数接收多个参数，集中适配，不要求为了照抄签名重写全部业务。

手工 `model_validate` 抛 `ValidationError`；FastAPI 对请求自动校验产生的是 `RequestValidationError`。两者不可混写。上述页面只映射已知字段的错误消息，不把完整异常输入回传；国际化错误文案可以后续集中处理。

```html
<!-- app/templates/question_form.html -->
{% extends "base.html" %}
{% block content %}
<form method="post" action="/ui/questions">
  <label>标题 <input name="title" value="{{ values.title }}"></label>
  {% if errors.title %}<p role="alert">{{ errors.title }}</p>{% endif %}
  <label>正文 <textarea name="body">{{ values.body }}</textarea></label>
  {% if errors.body %}<p role="alert">{{ errors.body }}</p>{% endif %}
  {% if errors.form %}<p role="alert">{{ errors.form }}</p>{% endif %}
  <button type="submit">发布</button>
</form>
{% endblock %}
```

浏览器字段校验可改善体验，不能替代服务端校验。空值、过长输入、纯空白、清洗后过短均需服务端测试。

### 8.3 提交先于成功响应

复用第四课的函数作用域ConnDep及完整错误翻译，不为HTML再定义一份默认作用域依赖。当前 FastAPI 默认 request scope 在响应发送后退出；仅仅在 `yield` 后写提交并不足够。下例复列已有实现，engine与DuplicateTitle沿用第四课模块。

```python
from typing import Annotated, Iterator
from fastapi import Depends
from sqlalchemy import Connection
from sqlalchemy.exc import IntegrityError

def get_conn() -> Iterator[Connection]:
    try:
        with engine.begin() as conn:
            yield conn
    except IntegrityError as exc:
        constraint = getattr(getattr(exc.orig, "diag", None), "constraint_name", None)
        if constraint == "questions_title_key":
            raise DuplicateTitle() from exc
        raise

ConnDep = Annotated[Connection, Depends(get_conn, scope="function")]
```

所有依赖这条事务边界的 JSON/HTML 端点应使用同一别名；嵌套 yield 依赖也需核对作用域兼容。上述 `engine.begin()` 正常退出提交、异常退出回滚，提交失败时不应发送已经准备好的 201/303。标题约束冲突仍在事务退出后翻译为DuplicateTitle；第六课解释约束依据，第七课替换为Session，不能因新增HTML丢失JSON原有409行为。

业务冲突不要在写入后由 HTML 路由吞掉异常返回正常响应。让它穿过事务边界，再在全局表现层处理：

```python
@app.exception_handler(DuplicateTitle)
async def duplicate_title_handler(request: Request, exc: DuplicateTitle):
    values = getattr(request.state, "form_values", None)
    if request.url.path == "/ui/questions" and values is not None:
        return render_form(request, values, {"title": "标题已存在"}, 409)
    return JSONResponse(
        status_code=409,
        content={"code": "duplicate_title", "message": "标题已存在",
                 "detail": None,
                 "request_id": getattr(request.state, "request_id", "-")},
    )
```

此函数登记在前述 `app` 上；不在 service 中判断 `/ui/`。若使用统一 `AppError` 处理器，将这个分支并入原处理器，不重复维护冲突规则。

### 8.4 PRG 与验收证据

```text
校验失败：POST → 422 HTML（错误 + 原值）；没有业务写入
业务冲突：POST → 异常 → 回滚 → 409 HTML（错误 + 原值）
创建成功：POST → 写入 → 提交成功 → 303 Location → GET 详情 → 200 HTML
刷新详情：GET → 200 HTML；不重发创建请求
```

- 本课程选择校验失败直接回填 422；其他产品可用服务器端状态配合重定向保留输入，但不是本课必要复杂度。
- POST 成功后用 303 明确转向读取；301/302 在现代 HTTP 语义中允许 POST 改为 GET，307/308 则保留方法和请求体。`RedirectResponse` 默认 307，必须显式设 303。
- PRG 减少成功结果页刷新重放 POST；双击、网络重试、并发请求仍可能重复写入，需要业务唯一约束或幂等机制。第八课继续讨论写操作正确性。
- `author_id=1` 只用于本地虚构用户；PRG 不提供登录、授权或 CSRF 防护。本阶段不得作为安全完备的公开站点上线。

教师验证时关闭自动跟随重定向，先看 303/Location，再看 GET；浏览器保留 Network 记录。不能只展示最后 200 就宣称 PRG 正确。提交失败用模拟故障验证没有 303，数据库没有新增记录。

### 8.5 B 档：flash 跨过两次请求

flash 不是 M1 必交。最小实现使用 `SessionMiddleware` 的**客户端签名 Cookie 会话**，并非服务器存储内容。签名防篡改、不加密，不能存凭据、敏感正文等。

```python
from starlette.middleware.sessions import SessionMiddleware

app.add_middleware(
    SessionMiddleware,
    secret_key=settings.secret_key,
    same_site="lax",
    https_only=settings.cookie_secure,
)
```

另需 `itsdangerous`。密钥来自外部配置；本地 HTTP 可设 `cookie_secure=False`，生产 HTTPS 必须开启。Cookie 的传输、容量与并发覆盖问题留第十四课。

在创建路由成功分支给 `request.state.flash_on_commit` 设为 True；由事务依赖在 `with engine.begin()` **成功退出之后**写入 `request.session["flash"] = "发布成功"`。不要在尚未提交时写成功消息，否则提交失败也可能发送带成功提示的 Cookie。此扩展会让依赖需要 `Request`，仅在选做实现中加入。

详情 GET 在查到资源后用 `request.session.pop("flash", None)` 取消息，并通过模板 context 的 `flash` 字段传入；模板增加 `{% if flash %}<p>{{ flash }}</p>{% endif %}`。下一次刷新不再出现消息。

## 九、M1 验收与作业

**课堂 6 分钟。** 预估基础任务 3 小时左右，拓展自选，不要求全部完成。

### 9.1 A 档基础交付

| 项目 | 验收证据 |
|---|---|
| 三个核心 JSON 端点、健康检查保持有效 | 契约快照与正常/异常响应；不改旧验收规则掩盖回归 |
| HTML 列表、详情、发帖页 | 列表空态、详情不存在与正常导航均可用 |
| JSON/表单复用 schema 与 service | 同一组长度、空白边界输入；两入口规则一致 |
| 失败回填 | 422 和标题冲突 409；正文保留且转义；失败没有业务新增 |
| 成功 PRG | POST 的 303/Location 与后续 GET；刷新不重发 POST |
| 提交与异常边界 | 提交失败没有 201/303；日志和普通 500 响应头可关联 |
| 同步/异步选择 | 一个代表性端点，沿 service/repository 指到实际阻塞调用 |
| 六组基础并发记录 | a/b/c × 并发 1/10；可使用课堂数据，注明来源和环境 |

原有配置外置、`.env` 不入仓、分层依赖方向继续保持；不设路由行数上限，不要求所有 HTML/健康响应套 JSON 业务模型。同步数据库测试应使用故障替身或隔离依赖，勿为演示停掉其他人的数据库。

### 9.2 AI 协作与判据说明

在本次实际工作中选一段模板、表单适配或调用链建议，保存提示词与输出，说明：符合哪些规则、怎样验证、是否修改以及原因。若建议正确，提交保留理由即可。

更新已有技术方案手册的一小节，不重复交多份相同截图。推荐记录一个决定：“本项目数据访问保持同步，因此端点使用 def；当等待量、资源预算与测量支持时再评估异步改造。”不要求每课凑满若干条 ADR。

### 9.3 B 档选做

任选一项，建议不超过一小时：flash；固定工作量 CPU 对照；并发 50 或多 worker 对照；纯 ASGI 中间件阅读与改写。交真实结果和局限，不以预测必须失败或吞吐必须提升评分。

## 十、素材、运行条件与验收状态

本底稿修订不等于独立演示工程、截图和压测脚本已经交付。制作前需要补齐：

- 独立的第五课工程及依赖锁：Python 3.12、支持函数作用域依赖的 FastAPI、匹配的 Starlette、Pydantic v2、同步 SQLAlchemy、Jinja2、python-multipart、httpx；flash 另需 itsdangerous。
- 正常 M1 起点与三个互不混杂的反例阶段：阻塞、POST 结果页、局部模板 `safe`；用明确版本或副本标识，不冒称已有 Git tag。
- `bench.py` 六组基础测量、预录备用证据、普通 500 的头与日志、422/409 回填截图和 PRG 的 Network 记录。
- 教师需验证依赖注册、模板调用、数据库提交故障与浏览器刷新行为。只构建课件不能替代这些验收。

本轮在 FastAPI 0.141.1 / Starlette 1.6.0 的进程内最小应用中验证：依赖退出抛异常时，默认 request scope 已返回 200，而 function scope 返回 500；另用 Pydantic 2.13.5 核对先 strip 再做标题长度约束。前者是提交失败时机的模拟，不是完整数据库提交测试。当前第一课 Python 环境未安装 Jinja2、python-multipart，本轮未安装新依赖；完整表单/模板、浏览器 PRG 和真实 HTTP 并发压测仍待验收。

所有实验用虚构数据和可丢弃副本；先确认库名、连接串与当前工作目录。复位只重建该演示副本，不覆盖学生未提交代码，不对真实项目批量灌脏数据。现场故障超过约半分钟，可切预录材料，注明机器、版本、日期和模拟条件。

## 十一、与后续课衔接

| 内容 | 后续位置 |
|---|---|
| 数据库约束与并发唯一性 | 第六课；不把已有合格 M1 改坏 |
| Session、提交失败、持久化实现替换 | 第七课 |
| PRG 之外的写入正确性与幂等 | 第八课 |
| 回归与故障验证固化 | 第九课 |
| 跨域读取、CORS 与客户端错误 | 第十二课 |
| 登录、身份与 Cookie | 第十四课 |
| XSS、CSRF 和公开站点安全 | 第十五课 |
| 外部服务等待、部署资源预算 | 第十六课；不承诺在本课实现任务队列 |

第六课先用小型可手算数据说明约束与 NULL，再在隔离性能库观察索引。完整模板参考、错误路径、容量判据保留在课件中，课堂不必逐条展开。

参考：FastAPI 的 Request Forms、Templates、Advanced Dependencies；Starlette Middleware；RFC 9110 的 303 See Other。制作演示工程时以锁定版本对应的官方文档和实测为准。
