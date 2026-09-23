# 第 4 次课教学底稿（完整整改版）
## 可控重构：依赖、职责与错误边界

## 〇、备课定位与起点

本课不是“把全部重复清零”，而是**在回归保障下，把一项共享规则放到可指认的位置，并说明哪些行为没有改变**。课件可以保留完整代码、异常时序与配置参考，课堂只要求学生独立完成一个重构任务。

取消本课20分钟诊断小测。按95分钟教学＋5分钟缓冲安排，不在正文或作业中重新加回小测。

起点是第三课合格交付：
- `GET /questions`：keyword/page/page_size；page≥1，page_size默认20、范围1—50；`items/total/page`。
- `GET /questions/{qid}`、`POST /questions`：`QuestionOut`，创建201，作者由服务端固定夹具提供。
- Query/Path/Pydantic 已生效，title/body先strip再长度校验；不退回手工if和静默修正。
- `/healthz` 必保留200 ok/ok、数据库故障503 degraded/down。
- 同步SQLAlchemy Core、已有Engine连接池；创建模板先提交再返回成功；标题唯一约束和标签关联不能丢。
- request-id沿用M0合法格式 `[A-Za-z0-9._-]{1,64}` 与进入/离开日志；未知异常路径是明确的历史观测缺口。

### 95分钟课堂路线

| 单元 | 分钟 | 课堂处理 |
|---|---:|---|
| 一、回归基线与真实变更 | 5 | 主讲 |
| 二、正确但重复的代码 | 10 | 教师统计实际位置，不预填数字 |
| 三、连接依赖与事务时序 | 14 | 教师演示资源与失败边界 |
| 四、一次共享规则重构 | 22 | 唯一学生现场必做，中途运行回归 |
| 五、错误契约与表现层 | 14 | 教师演示，完整处理器课后读 |
| 六、抽取业务职责 | 12 | 主讲一条创建链，参考实现课后读 |
| 七、配置与横切逻辑 | 10 | 思路导读；认证细节后移 |
| 八、交接与作业 | 8 | 核对前后行为与取舍 |
| 合计 | 95 | 另留5分钟缓冲 |

A档：基础重构、资源和异常路径验证、错误契约、配置检查，允许课后补齐。B档：依赖工厂、完整依赖树、更多方案比较；认证实现第十四课，完整事务第七课，中间件调度与洋葱细节第五课。超时压缩API罗列和配置现场敲写，不压缩回归结果解释。

## 一、先保存事实：本课有两类不同改动

**课堂5分钟。**

| 阶段 | 允许改变 | 不允许改变 |
|---|---|---|
| R：纯重构 | 代码位置、资源获取入口、函数边界 | 方法、路径、状态、参数名、默认值、范围、业务规则、成功响应 |
| E：批准的错误契约迁移 | 普通业务JSON错误统一为code/message/detail/request_id；同步OpenAPI与前端 | 探针200/503形状、既有成功响应和状态语义 |

先跑教师提供的第三课行为检查，再进入R。E阶段独立记录预期差异，不能把“新增错误字段”冒充纯重构。旧快照留作历史，只有批准的变更才更新断言。下文代码按职责分段，不是按文章顺序拼接的单文件：组装时先定义模型/异常和基础设施，再定义依赖/service与router，最后注册处理器、中间件并include_router。迁移时替换旧业务路由声明，不将同方法同路径的新实现追加到旧路由后。

教师回归包应覆盖：正常/空列表、分页边界、详情存在/不存在/非法qid、合法/非法/重复创建、标签保存、输出字段、id与日志、探针失败与恢复。第九课再系统教测试设计和CI，但今天就运行这些检查。

## 二、起始案例：保留第三课的正确成果

**课堂10分钟。** 以下是第三课已有辅助函数和模型上的端点节选，不是新造一个有四个列表的学生项目。

```python
from fastapi import Query

@app.get("/questions", response_model=QuestionListOut)
def list_questions(
    keyword: str = Query(""), page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=50),
):
    with engine.connect() as conn:
        return read_page(conn, keyword, page, page_size)
```

创建端点使用第三课 `with engine.begin()`、命名唯一约束翻译、`QuestionOut.model_validate` 和Location；详情使用连接上下文与输出映射。它们可以是正确但资源管理写在各端点中的代码，不能重新引入第三课已修复的错误。

让学生统计实际情况：

| 问题 | 记录什么 | 不预设什么 |
|---|---|---|
| 业务端点如何获取和释放连接 | 函数/文件/位置 | 每次都是新的物理连接 |
| 分页规则有几处 | Query或等价权威定义 | 人人都有4个分页端点 |
| 错误正文有哪些 | 用真实请求收集 | 一定有5种格式或11处错误 |
| 创建的业务与SQL混在哪里 | 具体调用位置 | 每个端点都必须新增service |

本课的真实共享需求是：“三个核心业务端点采用统一的连接生命周期，创建失败先退出事务；错误编号和正文通过表现层集中生成。”只有一个分页端点时，抽分页依赖可以服务清晰边界，但不虚构大量减少修改位置的收益。

漏改一处是否被发现取决于检查覆盖。教师可在隔离副本故意漏接一个依赖或漏改422文档，让**已有回归检查报错**。不要称漏改“没有任何方式发现”，也不要要求学生故意把自己的合格代码改坏。

## 三、连接依赖：使用期间有资源，退出时有确定边界

**课堂14分钟，完整时序A档课后阅读。**

### 3.1 普通函数与依赖的差别

普通上下文管理器也能正确释放资源，测试也可通过传参或替换函数实现；不是“没有Depends就无法测试”。Depends的收益是把需求声明在签名、接入框架生命周期和替换挂点，代价是执行流程更隐式。

先提供业务异常，不含HTTP状态码：

```python
class AppError(Exception):
    """预期的业务失败；HTTP映射放在表现层。"""

class QuestionNotFound(AppError):
    pass

class DuplicateTitle(AppError):
    pass
```

资源依赖参考（engine来自统一数据库模块，不在依赖里反复create_engine）：

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

数据库错误翻译是基础设施边界，识别的是PostgreSQL/psycopg结构化诊断，不搜索异常字符串。捕获在事务上下文之外，覆盖语句或提交失败，并先回滚/释放再向表现层传播。别的完整性错误不能全报“重复标题”。

R阶段先用以下过渡适配器承接第三课的existing_error与ExistingErrorOut，404/409仍是原三字段；422和未知异常保持旧处理，不能提前迁移。它在事务退出后处理业务异常，不会把失败吞在事务里。E阶段再用第五单元register_handlers替换此适配器；两阶段分别新建应用并重启，不在服务已运行后修改处理器。

```python
from fastapi import Request


def register_r_handlers(app):
    @app.exception_handler(QuestionNotFound)
    async def not_found(request: Request, exc: QuestionNotFound):
        return existing_error(request, 404, "question_not_found", "问题不存在")

    @app.exception_handler(DuplicateTitle)
    async def duplicate(request: Request, exc: DuplicateTitle):
        return existing_error(request, 409, "duplicate_title", "标题已存在")
```

R阶段路由responses仍声明ExistingErrorOut。E阶段不再调用register_r_handlers，避免具体异常处理器优先于AppError处理器而保留旧正文。

### 3.2 成功响应必须晚于提交

```text
请求 → 依赖进入with，到yield交出Connection
     → 端点与普通响应数据处理
     → 函数作用域依赖退出：提交成功 / 异常回滚与释放
     → HTTP成功响应发送
```

这是 `scope="function"` 的必要前提，不是默认yield依赖的普遍时序。当前FastAPI默认request作用域在响应发送后退出；此时提交失败可能无法撤回已经发送的201。

- 所有取连接位置复用同一个ConnDep，子依赖也用它，不能混入无scope的另一份get_conn声明。
- 需要包裹ConnDep的yield子依赖也须匹配function生命周期；request作用域yield不能依赖生命周期更短的function资源。
- 正常退出提交；异常穿过上下文后回滚。不能在with内部吞业务错误然后返回一个“正常Response”，否则事务可能照常提交。
- `yield` 后的普通语句遇异常不保证执行；资源释放靠with或finally。进程被杀、严重运行时故障不是框架可以保证的清理场景。
- 这是普通短请求策略。流式响应、后台任务不能在依赖已关闭后继续用同一连接。
- 提交时网络断开可能导致结果未知；“没有返回201”不保证数据库绝未提交，安全重试留第八课。

教师做两个最小验证：事务中插入后抛异常，表内不留行；模拟依赖退出失败，比较request作用域与function作用域客户端状态。第二个是时序模拟，不冒称真实数据库commit失败覆盖。

### 3.3 Engine、Connection与将来的Session

Engine配置连接池与方言；Connection是借出的数据库连接使用接口；Session提供ORM工作单元等能力。现在已经有连接池策略，不能写“第七课才有池”。

本课把连接/事务入口集中。第七课换Session还涉及模型、repository、查询结果、加载策略和错误翻译，**不保证只改deps.py一个文件**。集中边界减少传播，不让真实差异消失。

## 四、唯一现场必做：一次可验证的共享资源重构

**课堂22分钟。**

任务分成一个连续过程：
1. 保存R阶段前的检查结果与实际位置数。
2. 接入ConnDep，先改列表与创建的资源入口；中间跑一次回归。
3. 详情改同一入口，探针保持独立失败边界。
4. 检查非法输入仍422、page_size名称没变、成功输出一致、失败没有半截业务数据。
5. 写一段“集中在哪、哪些没抽、为什么”的说明。

完整service与错误处理器由教师骨架提供，学生不在22分钟内从零敲完所有文件。跟不上时可以使用标明版本的阶段副本继续，缺少的独立改动课后补，不用固定tag名称假装已经有可切换仓库。

### 4.1 分页依赖：内部名称不改变公开参数

```python
from dataclasses import dataclass
from fastapi import Query

PAGE_SIZE_MAX = 50

@dataclass(frozen=True)
class Page:
    page: int
    size: int
    offset: int


def pagination(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=PAGE_SIZE_MAX),
) -> Page:
    return Page(page=page, size=page_size, offset=(page - 1) * page_size)


PageDep = Annotated[Page, Depends(pagination)]


@router.get("/questions", response_model=QuestionListOut)
def list_questions(conn: ConnDep, pg: PageDep, keyword: str = Query("")):
    return repo.read_page(conn, keyword, pg.page, pg.size)
```

这里router不额外配置`/questions`前缀；如果项目已有前缀，路径相应写空串，不能重复成`/questions/questions`。约束仍是第三课的1—50，输入不合法仍422，不静默改20。

`Page.size`是内部字段，HTTP必须叫page_size；也可以内部Query参数叫size并显式alias="page_size"，但本课参考直接沿用公开名字。OpenAPI必须只有page_size，不新增公开size。

只用一次也可能因资源生命周期或清晰边界值得抽依赖；复用次数不是唯一判据。若做“上限50→30”变更实验，只在隔离副本明确变更规格并跑边界，回归交接版本恢复50；不把这个实验混进主线纯重构。

### 4.2 子依赖和缓存（教师导读）

```python
from fastapi import Path


def get_question_resource(conn: ConnDep, qid: int = Path(ge=1)) -> QuestionOut:
    return svc.get(conn, qid)


QuestionDep = Annotated[QuestionOut, Depends(get_question_resource, scope="function")]


@router.get("/questions/{qid}", response_model=QuestionOut,
            responses={404: {"model": ErrorOut}})
def get_question(question: QuestionDep):
    return question
```

要观察缓存，用独立只读实验依赖同时直接与间接请求ConnDep，记录获取次数和对象标识。路径必须包含子依赖声明的qid，无需提前引入PATCH：

```python
@router.get("/lab/dependency-sharing/{qid}", include_in_schema=False)
def dependency_sharing(conn: ConnDep, question: QuestionDep):
    return {"id": question.id}
```

同一请求、相同依赖缓存键和一致scope下通常复用；不是全局缓存。改变依赖函数实例、scope、use_cache或安全上下文等会改变行为。打印依赖图有两个节点，不代表一定获取两次连接。

## 五、统一错误契约：明确覆盖与例外

**课堂14分钟，教师演示；完整参考A档课后阅读。**

### 5.1 批准的迁移

普通业务JSON错误统一为：

```json
{"code":"question_not_found","message":"问题不存在","detail":null,"request_id":"demo-01"}
```

code稳定供程序判断；message供人阅读，字段本身是契约的一部分，但客户端不应匹配具体文案。detail只放经过筛选的安全结构；request_id用于关联，不携带用户隐私。

**范围**：业务404/409、请求422、框架未匹配路径404/方法405、普通未知异常500。`GET /healthz` 的数据库503保持探针正文。第五课HTML错误返回页面，不能强制所有响应都是JSON。响应已经开始的流式错误、后台失败也不能重新改成此JSON。

### 5.2 业务异常在HTTP边界映射

```python
from typing import Any
from pydantic import BaseModel

class ErrorOut(BaseModel):
    code: str
    message: str
    detail: Any = None
    request_id: str


BUSINESS_HTTP = {
    QuestionNotFound: (404, "question_not_found", "问题不存在"),
    DuplicateTitle: (409, "duplicate_title", "标题已存在"),
}
```

AppError不放status_code。业务调用者得到“问题不存在/标题重复”；HTTP适配器决定404/409，CLI可决定退出码。HTTPException也是普通异常，在CLI里并非不能捕获；问题是复用者被迫理解HTTP术语，不是必然崩溃或必须重写全部service。

### 5.3 四类处理器（含框架HTTP错误）

```python
import logging
from http import HTTPStatus
from fastapi import Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

logger = logging.getLogger("app")


def error_response(request, status, code, message, detail=None, headers=None):
    rid = getattr(request.state, "request_id", "-")
    body = ErrorOut(code=code, message=message, detail=detail, request_id=rid)
    result = JSONResponse(status_code=status, content=body.model_dump(mode="json"),
                          headers=headers)
    result.headers["X-Request-ID"] = rid
    return result


def register_handlers(app):
    @app.exception_handler(Exception)
    async def unexpected(request: Request, exc: Exception):
        rid = getattr(request.state, "request_id", "-")
        logger.error("unhandled rid=%s", rid,
                     exc_info=(type(exc), exc, exc.__traceback__))
        return error_response(request, 500, "internal_error", "服务器内部错误")

    @app.exception_handler(AppError)
    async def business(request: Request, exc: AppError):
        mapping = BUSINESS_HTTP.get(type(exc))
        if mapping is None:
            return await unexpected(request, exc)
        status, code, message = mapping
        return error_response(request, status, code, message)

    @app.exception_handler(RequestValidationError)
    async def validation(request: Request, exc: RequestValidationError):
        details = [{"loc": list(error["loc"]), "type": error["type"],
                    "msg": "该字段不符合接口约束"} for error in exc.errors()]
        return error_response(request, 422, "validation_error", "请求参数不合法", details)

    @app.exception_handler(StarletteHTTPException)
    async def http_error(request: Request, exc: StarletteHTTPException):
        messages = {401: "需要有效认证凭据", 403: "请求被拒绝", 404: "路径不存在",
                    405: "该路径不支持此方法", 429: "请求过于频繁"}
        try:
            fallback = HTTPStatus(exc.status_code).phrase
        except ValueError:
            fallback = "HTTP请求失败"
        return error_response(request, exc.status_code, f"http_{exc.status_code}",
                              messages.get(exc.status_code, fallback), headers=exc.headers)
```

注册在应用开始处理请求之前；新增子类需加入映射，不让未识别错误意外披露内部信息。实际产品可为type映射更友好的字段提示，这里固定安全文案，保留loc/type，不回传input、ctx、SQL或任意exc.detail。

必须捕获Starlette基类，才能覆盖框架产生的404/405；只捕获FastAPI子类不够。保留 `exc.headers`，尤其405的Allow、401的WWW-Authenticate、429的Retry-After。若应用返回直接Response，不会自动经过这些异常处理器，要单独核对。

### 5.4 OpenAPI与客户端同步

E阶段先定义ErrorOut，再创建业务router，然后登记前述端点：

```python
from fastapi import APIRouter

API_ERROR_RESPONSES = {
    422: {"model": ErrorOut, "description": "请求校验失败"},
    500: {"model": ErrorOut, "description": "未预期错误"},
}
router = APIRouter(responses=API_ERROR_RESPONSES)
```

详情装饰器已声明404，创建装饰器另声明409（第六单元）；列表使用router共享的422/500。第四单元详情节选采用E阶段的ErrorOut，R阶段对应使用ExistingErrorOut。探针在app单独登记HealthOut，避免把业务错误清单误作探针503正文。最后在应用启动前执行 `register_handlers(app)` 和 `app.include_router(router)`，不能仅定义常量而没有接入路由。

按端点实际可能状态在路由声明或router级responses登记，特别覆盖原自动422模型。框架404/405也在契约说明里列出；未知路径本身不是一个可在OpenAPI中枚举的业务operation。添加responses只改变文档，不给处理器自动加运行校验，因此上面的error_response先构造ErrorOut。

客户端按 `code` 决策、用message显示、用detail回填；第二课的HTTP分流仍保留。错误页不是合法JSON时，保留状态级降级提示，不让错误解析再次覆盖最初问题。E阶段快照与运行结果一起核对。

### 5.5 探针例外（不是“零处连接”的扣分项）

```python
from typing import Literal
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

class HealthOut(BaseModel):
    status: Literal["ok", "degraded"]
    db: Literal["ok", "down"]


@app.get("/healthz", response_model=HealthOut,
         responses={503: {"model": HealthOut}})
def healthz():
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
    except SQLAlchemyError:
        return JSONResponse(status_code=503,
                            content={"status": "degraded", "db": "down"})
    return {"status": "ok", "db": "ok"}
```

不能先用普通ConnDep获取连接，再只在探针函数里捕获SELECT错误：连接获取失败发生在进入端点之前，会变成通用500。探针的整个获取与执行放在专用失败边界；可提取为probe函数，但不能丢捕获范围。预期数据库故障503，其他程序错误仍按真实类别处理。

### 5.6 中间件与兜底：分别补日志和响应头

先解释旧M0为什么“正常业务错误有离开日志、未知异常没有”。处理器层次：

```text
ServerErrorMiddleware：未知异常/500处理器
  → 用户中间件
    → ExceptionMiddleware：业务异常、HTTPException、请求校验错误
      → 路由、依赖、端点
```

内层业务错误转成响应，call_next正常返回；外层兜底在异常穿过用户中间件后才生成500。因此仅注册Exception处理器不能保证旧中间件后半段执行。函数作用域提交失败也遵循异常传播，不能把响应成功提前发走。

本课参考目标保留M0日志格式和合法id，并提供最小安全补齐；课堂只导读，**第五课详细复演顺序和实现边界**：

```python
import re
import time
import uuid

@app.middleware("http")
async def trace_middleware(request: Request, call_next):
    supplied = request.headers.get("X-Request-ID", "")
    rid = supplied if re.fullmatch(r"[A-Za-z0-9._-]{1,64}", supplied) else uuid.uuid4().hex
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
```

finally补日志；error_response给外层500补响应头。未知异常日志中的error不是观察到的实际HTTP状态，不伪造为500；计时到call_next返回或抛异常，不是流式传输完成。实际应用 `debug=False` 才采用该普通兜底正文，debug模式可能显示调试响应；不能说处理器让debug开关不再重要。

若学生已采用等价正确实现，不撤回它来制造缺口。当前目标修复/boom后，历史M0验证器对/boom缺日志/缺头的“预期失败”断言需要在新阶段明确更新，旧阶段测试保留不动。

## 六、职责抽取：只沿一条创建链讲清楚

**课堂12分钟，完整参考课后读。**

### 6.1 三类职责与一个独立schema

| 位置 | 关心什么 | 判断是否值得抽 |
|---|---|---|
| router / handlers | HTTP方法、参数、状态、表现形式 | 对外契约是否可见且一致 |
| schema / mapper | 输入约束、输出字段、数据映射 | 是否避免暴露数据库内部结构 |
| service | 标题唯一等业务规则、编排 | 是否有规则或多个数据访问动作 |
| repository | SQL、行映射和数据访问 | 是否可以更换实现而限定影响 |
| deps / config | 生命周期、共享准备、配置 | 是否有稳定权威入口 |

不按路由≤10行打分，不用“有循环就错”代替语义判断。简单读取可以router直接调repository；也可为了统一业务入口经service，但要说明成本。循环导入是否当场报错取决于导入时访问顺序，不是假定一条反向import必然报同一异常。

### 6.2 创建链参考

repository复用第三课已经正确的 `find_detail`、`read_page`、`insert_question_with_tags`；移动完整逻辑，不删除tags分支。可额外保留预查以改善提示：

```python
def find_by_title(conn, title):
    return conn.execute(text("SELECT id FROM questions WHERE title = :title"),
                        {"title": title}).scalar_one_or_none()
```

service不import FastAPI、不创建Response、不commit：

```python
def get(conn, qid):
    result = repo.find_detail(conn, qid)
    if result is None:
        raise QuestionNotFound()
    return QuestionOut.model_validate(result)


def create(conn, payload: QuestionCreate, author_id: int):
    if repo.find_by_title(conn, payload.title) is not None:
        raise DuplicateTitle()
    qid = repo.insert_question_with_tags(conn, payload, author_id)
    return get(conn, qid)
```

这里service返回DTO便于JSON/HTML复用；Pydantic依赖是课程取舍，不是纯领域层必需条件。预查不代替 `questions_title_key` 唯一约束，竞争失败仍由第三单元get_conn翻译。业务抛异常让事务边界回滚，表现层再决定HTTP输出。

```python
from fastapi import Response

@router.post("/questions", response_model=QuestionOut, status_code=201,
             responses={409: {"model": ErrorOut}, 422: {"model": ErrorOut},
                        500: {"model": ErrorOut}})
def create_question(payload: QuestionCreate, conn: ConnDep, response: Response):
    question = svc.create(conn, payload, author_id=1)
    response.headers["Location"] = f"/questions/{question.id}"
    return question
```

此时构造Location不等于已发送201；function scope成功退出后才发送。response_model缺字段、业务异常或数据库错误不得在端点中吞掉后回正常结果。普通成功DTO在资源有效期构造好，第五课HTML也复用 `svc.create(conn,payload,author_id)`。

目录可以是 `routers/schemas/services/repositories/deps/config`，也可按小项目模块组织；验收看依赖方向和行为，不强制文件名完全一致。不要求为简单读取添加空转的一层。

## 七、配置与横切逻辑：有据取舍，不制造假收益

**课堂10分钟；完整配置、依赖工厂为课后阅读。**

### 7.1 配置的真实收益

`create_engine(os.getenv("DATABASE_URL"))` 若参数是None，会立即抛配置错误，不是一定等第一次请求才失败。另一方面create_engine通常延迟建立物理连接，有效形状的URL仍可能连接失败；配置类型校验不能证明数据库可达。

```python
from typing import Literal
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")
    database_url: str = Field(min_length=1)
    debug: bool = False
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR"] = "INFO"

settings = Settings()
```

集中字段、类型转换、必填与范围校验、可见配置清单是收益。database_url只校验非空字符串，URL能否由SQLAlchemy解析、驱动是否存在和网络是否可达还要另检验。

分页上限当前只在PAGE_SIZE_MAX定义，不再顺手加一个未接入Query的第二配置源。若以后改为配置，应确保唯一读取点、重启时更新OpenAPI，并声明是否是对外契约变更。

本课尚未使用会话，不凭空要求未使用的SECRET_KEY。第五课B档启用签名Cookie时再增加必填、长度校验的密钥字段与生产配置检查。不能提供可用默认密钥。

`.env`不进Git，`.env.example`列键名和占位值。若真实密钥泄漏，应吊销/轮换并核查使用记录，清理历史不能替代轮换；不在课堂投影真实历史凭据。忽略文件并不能移除已经跟踪的内容。

当前M0环境缺pydantic-settings：独立第四课工程需显式声明并锁定依赖，不能说Week0已经保证安装。可先用Pydantic模型加显式os.environ演示同一原则，但不得标成已验证pydantic-settings集成。

### 7.2 横切逻辑归属

| 需求 | 本课推荐落点 | 边界 |
|---|---|---|
| 全应用request-id、常规响应头 | 中间件＋外层500兜底补头 | 未匹配路由也需覆盖；注册/包装位置重要 |
| 参数、资源对象、按端点的认证前置 | 依赖 | 不在未匹配路由执行；签名显式可见 |
| 发帖规则、状态检查、跨数据编排 | service | 可被HTTP之外调用 |
| IP/入口限流 | 入口设施或中间件 | 不依赖尚未执行的用户依赖 |
| 按用户限流 | 依赖用户识别的限流依赖 | **端点执行前**检查并拒绝 |

依赖可以通过Response或HTTPException.headers设置响应头；不是“只要需要Retry-After就必须中间件”。中间件也能按路径条件选择、读取部分请求信息，不是绝对做不到，只是上游执行时路由参数和已解析对象尚未可靠可用，绕开框架解析增加复杂度。

按用户限流的必要顺序：

```text
验证凭据 → 获取用户 → 检查/消耗调用额度 → 允许端点执行
                             └→ 超额则429，可携带Retry-After
```

不能让用户依赖先在call_next内部识别，再等call_next返回后由外层中间件决定拒绝：写操作此时可能已发生。完整限流和认证不在本课实现。认证中间件也有合理方案，不能因AI用了它就直接判错。

### 7.3 RFC9457的真实取舍

课程保留现有 `code/message/detail/request_id`，原因是保持教学客户端与后续课一致、降低本轮迁移范围，不是假称标准不支持需求。

| 标准字段 | 含义 |
|---|---|
| type | 问题类型URI引用；不要求每种错误都维护可访问文档站，缺省可用about:blank |
| title | 类型的简短摘要 |
| status | 对应HTTP状态 |
| detail | 本次具体说明 |
| instance | 本次问题标识URI引用 |
| 扩展字段 | 可以合法增加request_id、errors等 |

媒体类型是application/problem+json；fetch的response.json()不会因此自动换一种JSON解析。特定库的媒体类型策略另行验证。公共API可考虑标准格式，不声称自定义格式普遍更好。

## 八、作业、验收与第五课交接

**课堂8分钟。**

A档必交：
1. R阶段重构diff与回归：三个核心端点和探针不退化，未破坏分页名字/范围、输出、标签、标题唯一及清洗顺序。
2. E阶段错误契约迁移：业务404/409、422、框架404/405、普通500；检查Allow等必要头与id；探针数据库503正文不变；OpenAPI同步。
3. 资源失败证据：插入后异常不留半截；退出阶段模拟失败不得发201；连接资源能释放。测试模拟和真实数据库实验分开写。
4. 指定规则的权威位置与依赖方向；配置字段、`.env.example`及敏感信息处理。
5. 一张变更影响表，区分文件数与位置数；合理保留的重复要说明。

| 变更问题 | 重构前文件/位置 | 重构后文件/位置 | 说明 |
|---|---|---|---|
| 普通业务连接生命周期策略 | 按实际填 | 按实际填 | 探针专用失败边界为何保留 |
| JSON错误增加一个诊断字段 | 按实际填 | 按实际填 | 同时考虑schema、文档、客户端与测试，不只改一行 |
| 隔离副本中分页上限50→30 | 按实际填 | 按实际填 | 主线交付仍50；只有一个列表也可以如实填 |

不要求路由零个with、零个except、全仓恰好一个commit或完全一致目录；更不把/healthz必要捕获判为分层失败。不按“文件越少越好”评分，分层后文件可能增加。

B档：打印依赖树；比较认证中间件与依赖；画Connection→Session影响范围。允许AI方案原本正确，不要求必须找到“误写中间件”的案例，也不要求提前实现认证。

第五课交接清单：
- 同步端点/持久层与ConnDep function scope；同一QuestionCreate，svc.create返回可用id的DTO。
- 三JSON端点＋必保留探针；items/total/page、page_size默认20上限50；标题唯一与标签功能。
- JSON错误契约已经登记；第五课新增HTML表现，不把错误吞在事务内部。
- 本课已给出最小finally日志与500补头参考，第五课深化洋葱顺序、CORS、流式边界和调度；不为了课堂反例把正确实现撤回。
- “课后完成基础验收”不等于可选，不把未完成的第三课成果推给第五课补救。

## 九、课后依赖阅读与素材状态

依赖树可遍历APIRoute.dependant打印；这是框架内部观察接口，不作为稳定公共API依赖。名称应兼容可调用对象，不一律访问 `.__name__`。资源清理通常按建立的上下文逆序，不把图的打印顺序当作所有求值与副作用时序保证。

依赖工厂需要避免为同一语义反复创建不同函数导致缓存差异；认证安全方案第十四课再选。使用一次的资源依赖也有清理和替换价值，不能简单用复用次数否决。

本仓库尚无独立第四课工程、v4各阶段tag、分层检查脚本或配置截图。本文提供职责、代码和验收条件；制作阶段须提供可运行副本、第三课数据升级、完整导入与注册顺序、真实回归入口。不能指示学生checkout不存在的tag或将未完成素材标“已验证”。

本轮从本文代码提取依赖、分页、处理器、中间件与探针，使用FastAPI 0.141.1、Starlette 1.6.0、Pydantic 2.13.5、SQLAlchemy 2.0.54完成临时机制验证：
- 同请求直接/间接依赖只获取一次连接；page_size公开名、默认约束及422文档保持正确。
- SQLite插入后业务异常、模拟退出失败均回滚；模拟退出失败时request作用域返回201，function作用域返回500。后者不是实际PostgreSQL commit故障测试。
- R阶段保持三字段409；E阶段业务/校验/框架/未知错误为四字段，Allow、WWW-Authenticate、Retry-After与合法点号id保留；未知异常有配对日志和响应头。
- 模拟探针获取失败保持503 degraded/down，恢复200；详情404与探针503的OpenAPI模型分别正确。
- 同步核对第五课的配对日志、点号id和JSON/HTML500分流。结合前述各课检查，Python临时验证共95项断言通过，四课预算均95＋5；不等于已有完整课程回归包。

完整验收还需：PostgreSQL语句与真实提交错误、标签竞争、异常诊断、真实数据库断连与恢复、页面错误显示、完整OpenAPI快照及配置集成。最小FastAPI/SQLite机制验证不等于上述全部验收；每项记录版本、输入和实际结果。
