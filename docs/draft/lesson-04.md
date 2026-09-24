# 第 4 次课教学底稿（第四版）
## 依赖注入与统一错误出口

> **备课基线**：[第四版大纲](../syllabus-v4.md)第 4 课与[新版第 3 课交接](lesson-03.md)。本稿重新编写，尚未移交归档；独立工程、故障设施与课件需随后制作。旧稿的数据库技术栈、事务方案和验证记录不作为本轮已完成项。

## 〇、这次课要建立什么

**讲给学生的目标句**：你能把重复的资源获取收敛进一个依赖，并让约定范围内的错误从统一出口返回。

核心解释目标是：**依赖什么时候求值、资源什么时候释放、提交与响应谁先发生。** 第 3 课已有正确的 SQLite 读写和服务层显式提交；今天改变资源传递方式，再明确迁移错误契约，不重新设计输入模型或数据库。

课堂路线：**回归三端点 → 正常连接依赖 → 教师接列表 → 学生接创建与详情 → 提交前后故障对照 → 统一错误 → request-id 与探针升级**。不把“先发成功再提交”的错误方案作为学生主线起点。

### 95 分钟教学 + 5 分钟缓冲

| 分钟 | 教学单元 | 当场产出 |
|---|---|---|
| 5 | 回顾三端点里的重复代码 | 标出真实连接入口及不变契约 |
| 15 | Depends 与资源生命周期 | 依赖求值、复用与清理的位置 |
| 18 | 教师抽取连接依赖并接列表 | 正常读取；断点核对服务层提交顺序 |
| 25 | 学生接入创建与详情 | 回归通过；两组故障的响应和数据对照 |
| 15 | 业务异常与统一错误出口 | 404／409／422／500 的职责与安全正文 |
| 10 | request-id 模板与探针升级 | 日志与响应关联；数据库失败 503 |
| 7 | 提交边界、作业与交接 | 一份重构差异及验收说明 |
| **95** | **合计** | **另留 5 分钟缓冲，无课内小测** |

前置是函数参数、异常与 `try/finally`、`yield` 的形状。先用资源“交出／归还”解释，不要求学生实现生成器调度。超时先压缩完整处理器逐行阅读与参考层，不压缩正常接线、学生任务和两次独立连接回读。

### 教师提供与学生负责

| 提供物 | 标注 | 学生要求 |
|---|---|---|
| 第 3 课模型、参数化 SQL、SQLite 种子与升级 | 要求会用，保留上课已要求解释的绑定关系 | 不改公开字段与搜索语义，不重建库覆盖已有数据 |
| `get_conn`、服务层显式提交与异常传播 | 要求解释 | 能接入剩余端点、指出提交和清理的位置 |
| 统一错误处理器、OpenAPI 注册骨架 | 要求解释 | 解释业务异常与 HTTP 翻译、核对状态和字段；不从零敲完全部处理器 |
| request-id 中间件与结构化日志模板 | 要求解释 | 解释进入、正常返回、异常离开及外层兜底分别负责什么 |
| 两个事务故障开关、依赖观察器、回归器 | 黑盒 | 选择固定模式并核对响应、日志与数据，不编写设施 |

继续使用标准库 sqlite3，不引入 PostgreSQL、SQLAlchemy、ORM、作者字段、用户表或标签关联表。tags 仍存为 JSON 文本；不实现认证、限流、配置框架或分页依赖工厂来挤占本课任务。

## 一、回顾：先分清纯重构与契约迁移

**课堂 5 分钟。先运行正常列表、详情和一次合法创建，再标出三处 `closing(open_connection())`。**

### 1.1 第 3 课带来的基线

- `GET /questions`：keyword/page/page_size，默认空字符串／1／20，page≥1、page_size 为 1–50；先清洗关键词，标题或正文做字面子串匹配，样本英文字母不区分大小写，`%`／`_` 不作通配符；id 降序后分页，total 为分页前总数。
- 列表外壳为 items/total/page；列表、详情与创建均含 id/title/body/tags/created_at。保留正文，无 author 或 version。
- `GET /questions/{qid}`：仍为 `qid: int`，无正数限制。不存在的整数（包括 0、负数）为业务 404；非整数为请求校验 422。
- `POST /questions`：title 清洗后长 5–200，body 清洗后长 10–20000；tags 默认空列表、最多 5 项、不额外去重；额外输入字段拒绝。成功 201 + Location，精确重复标题 409。
- 服务层已在提交前构造 `QuestionOut`，显式 commit 返回后才把结果交给端点；数据访问函数不提交。
- `/healthz` 此时仅为 200、`{"status":"ok"}`，不查数据库；request-id 与统一错误体尚未引入。

### 1.2 本课按阶段验收

| 阶段 | 允许改变 | 不允许悄悄改变 |
|---|---|---|
| R：资源重构 | 连接入口、传参和函数位置 | 方法、路径、参数、校验、成功字段、原错误正文和探针行为 |
| E：错误与观测升级 | 普通 JSON 错误迁为四字段；增加 request-id；探针增加数据库检查与 503 | 既有业务状态码、成功数据、提交位置；探针仍只含 status 字段 |

先保存 R 前结果，再在资源正常、单一边界输入等给定条件下核对 R 后等价；进入 E 时才更新批准的错误正文和探针断言。连接移到依赖后，多种失败同时发生时的优先级可能变化，见 3.1，不声称全部故障组合都等价。不能把新增错误字段称为“行为完全没变”。回归器由教师提供，第 9 课再系统学习测试设计。

本稿代码是分阶段参考：沿用第 3 课模型、行映射、查询／插入和创建服务。替换旧路由，不在同一 app 后面追加同方法同路径的第二份声明。E 阶段使用新的应用装配，明确替换 R 的注册结果；静态页挂载由教师保留。

## 二、依赖：声明需要什么，框架在调用前准备

**课堂 15 分钟。约 6 分钟解释签名与 yield，5 分钟观察复用，4 分钟观察清理。**

### 2.1 正常的资源提供者

`Depends(get_conn)` 传的是可调用对象，不写成 `Depends(get_conn())`。框架按请求解析依赖，把返回或 yield 的对象传给端点；不是 Python 类型注解自己打开数据库。

```python
from typing import Annotated, Iterator

from fastapi import Depends


def get_conn() -> Iterator[sqlite3.Connection]:
    conn = open_connection()
    try:
        yield conn
    finally:
        conn.close()


ConnDep = Annotated[sqlite3.Connection, Depends(get_conn)]
```

解释三处：获取成功后才 yield；端点使用同一连接；正常或异常退出都进入 finally 关闭。若获取阶段就失败，尚未交出连接，端点不会执行。部分初始化失败的清理由资源工厂自己负责。

教师的连接工厂仍设 `row_factory=sqlite3.Row`、非自动提交的写事务模式，例如显式 `isolation_level="DEFERRED"`。**本课同步 yield 依赖与同步端点不保证由同一工作线程执行**，工厂须设置 `check_same_thread=False`，并保持每请求独立连接、同一连接不并发使用。该参数取消线程亲和检查，不会自动提供并发安全；不把单个全局连接共享给所有请求。

`conn.close()` 不是成功提交；本例尚未提交的事务会被关闭回滚。正常写入必须由服务层 commit。显式服务层 rollback 负责失败分支，关闭资源是最终清理，不用“反正 close 会处理”代替业务事务边界。

### 2.2 同一请求中的复用：先预测

固定同一个函数对象、同一默认作用域、没有 `use_cache=False`。教师在隔离只读应用中同时直接和间接请求 ConnDep：

```python
def connection_identity(conn: ConnDep):
    return id(conn)


IdentityDep = Annotated[int, Depends(connection_identity)]


def dependency_probe(conn: ConnDep, identity: IdentityDep):
    return {"same_connection": id(conn) == identity}
```

教师把它临时注册到隔离实验路径，并在 `get_conn` 获取处计数。预测：是一个还是两个连接？核对结果：一次请求获取一次，两个位置用同一个对象；下一次请求重新获取，最终各自关闭。不能仅比较跨请求 id 数字，Python 可能复用已经释放对象的地址。

这是请求内依赖缓存，不是全局数据库池。换成不同函数对象、改变缓存配置或生命周期，会改变条件；完整依赖图与工厂是参考层。

### 2.3 默认退出时机与观察边界

当前锁定 FastAPI 的默认 request 作用域，普通响应发送后才退出 yield 依赖。因此：

```text
依赖获取连接 → yield → 端点调用服务 → 服务提交并返回
           → 端点返回普通数据 → 输出处理 → 发送响应 → 依赖 finally 关闭
```

这是普通成功路径，不是所有异常和流式响应的统一事件图。请求失败、输出处理失败时，依赖也会在退出路径清理；未知异常由外层处理。不能把 finally 的执行理解为事务已经成功。

教师在获取、yield 后退出、服务 commit 前后设观察点。IDE 断点证明运行到了哪行；**仅凭某一断点与浏览器的肉眼先后，不能精确证明响应启动时刻**，由教师 ASGI 事件观察器辅助核对。TestClient 返回时通常已执行清理，不能据此误判清理发生在响应前。

其他作用域可改变清理时机，本课不使用退出阶段提交方案。流式响应、后台任务与进程强制终止另有边界，不承诺关闭后的连接还能被继续使用。

## 三、教师构建：接通一个端点，提交位置不移动

**课堂 18 分钟。约 8 分钟接列表并回归，6 分钟沿创建服务追踪，4 分钟核对职责。**

### 3.1 教师接入列表（R 阶段）

以下片段替换第 3 课列表端点，查询函数保持不变：

```python
@app.get("/questions", response_model=QuestionListOut)
def list_questions(
    conn: ConnDep,
    keyword: str = Query(""),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=50),
):
    return search_questions(conn, keyword, page, page_size)
```

先核对空关键词三条、react 一条、空结果、第二页，再测 page=0。依赖进入和端点进入不是一件事：本课已经把获取连接移出端点，非法输入时部分依赖可能已运行；只承诺非法输入不进入该业务端点、不执行本次插入，不再声称“422 时一定没有连接”。

上述 422 回归以资源可正常获取为条件。若连接获取失败且 page=0 同时发生，当前实现可能先返回 500：第 3 课端点内才获取连接，非法参数会先被拒绝；重构后依赖求值可能先失败。这是需记录的失败优先级差异，不是输入规则被放宽，也不靠把连接错误伪装成 422 来保持表面一致。

### 3.2 逐行解释第 3 课已有的事务服务

继续使用第 3 课 `create_question_service(conn, payload)`，不是新增另一套提交方案：

```text
insert_question（只写入）
  → find_question（同一连接回读）
  → QuestionOut.model_validate（提交前检查可返回的字段）
  → conn.commit（确认本次事务提交）
  → 返回 DTO 给端点
```

- 服务层拥有这次创建的事务边界：发生异常先 rollback，再向外抛。内部辅助函数不各自提交，不对同一连接嵌套调用另一个自行提交的用例。
- 只有已知标题唯一冲突转为 DuplicateTitle。当前 SQLite 基线唯一的 UNIQUE 约束是 questions.title；判断 `SQLITE_CONSTRAINT_UNIQUE` 依赖此前提。NOT NULL 或其他数据库失败不冒充 409。
- 第 3 课已在提交前显式验证输出记录，因此这一步失败会回滚。但提交后仍可能发生程序错误，不能把“有输出模型”说成全部 500 都没有写入。
- 底层异常字符串、SQL 与用户输入不直接进入公开错误正文。

### 3.3 职责图只沿一条创建链

| 位置 | 负责什么 | 不负责什么 |
|---|---|---|
| 依赖 | 提供有效连接、最后关闭 | 不代替服务提交，不决定 HTTP 状态 |
| 端点与处理器 | 接收已校验输入、设置状态／头、翻译异常 | 不直接拼 SQL，不把业务层绑死在 HTTP |
| 服务 | 编排创建、显式提交、失败回滚 | 不创建 JSONResponse，不决定浏览器展示 |
| 数据访问与行映射 | 参数绑定、执行 SQL、转换存储字段 | 不私自 commit，不替接口更改契约 |

普通函数传参和上下文管理器也能正确管理资源。Depends 增加框架生命周期与可替换挂点，不是“没有它就无法测试”。不以端点行数、文件个数或“零个 with”评分，简单读取可以直接调用数据访问函数。

## 四、学生任务：剩余两端点与两组事务证据

**课堂 25 分钟。建议 10 分钟接创建／详情，5 分钟回归，7 分钟故障对照，3 分钟解释结果。**

### 4.1 独立完成的部分

学生组织连接传参和服务调用，保持输入模型、搜索语义、输出字段与提交位置；自己选一条合法创建数据并回读。教师给出函数签名提示和原服务，不预填完整端点答案。完成后用以下 R 阶段参考核对：

```python
@app.post("/questions", status_code=201, response_model=QuestionOut,
          responses={409: {"description": "标题已存在"}})
def create_question(payload: QuestionCreate, response: Response, conn: ConnDep):
    try:
        result = create_question_service(conn, payload)
    except DuplicateTitle as exc:
        raise HTTPException(status_code=409, detail="标题已存在") from exc
    response.headers["Location"] = f"/questions/{result.id}"
    return result


@app.get("/questions/{qid}", response_model=QuestionOut,
         responses={404: {"description": "问题不存在"}})
def get_question(qid: int, conn: ConnDep):
    result = find_question(conn, qid)
    if result is None:
        raise HTTPException(status_code=404, detail="问题不存在")
    return result
```

R 阶段仍为默认 detail 错误体，未知错误为默认 500；此时不提前要求四字段。探针暂时仍纯存活。教师保存前后行为对照，不要求学生实现检查框架。

### 4.2 故障开关的固定条件

教师提供独立事务实验副本，使用同样模型、非自动提交 SQLite、独立教学数据。一次只开一个模式，标题不能与已有记录重复；故障发生在 **HTTP 响应启动之前**。使用教师开关，不给公共业务接口增加可由任意客户端触发的故障参数。

| 模式 | 确切注入点 | HTTP | 另开连接查本次标题 |
|---|---|---|---|
| normal | 不注入 | 201 | 一条完整记录 |
| before_commit | INSERT 和回读成功后、commit 尚未调用 | 500 | 没有本次记录 |
| after_commit | commit 已确认成功返回后、服务返回前 | 500 | 本次记录仍在 |

前两步先预测再运行。不能用同一事务内能看见数据来证明提交；独立连接核对 title/body/tags。500 后手工重试可能遇到 409，并不表示前次必然没保存。

以下是教师故障副本的完整关键路径，**不是学生主线要再加的第二个创建服务**；隔离实验只替换创建服务调用，其余条件不变：

```python
def create_with_fault(conn, payload, mode):
    if mode not in {"normal", "before_commit", "after_commit"}:
        raise ValueError("未知实验模式")
    try:
        qid = insert_question(conn, payload)
        result = QuestionOut.model_validate(find_question(conn, qid))
        if mode == "before_commit":
            raise RuntimeError("教师实验：提交前失败")
        conn.commit()
        if mode == "after_commit":
            raise RuntimeError("教师实验：提交确认后失败")
    except sqlite3.IntegrityError as exc:
        conn.rollback()
        if exc.sqlite_errorcode == sqlite3.SQLITE_CONSTRAINT_UNIQUE:
            raise DuplicateTitle() from exc
        raise
    except Exception:
        conn.rollback()
        raise
    return result
```

after_commit 分支里再 rollback，不能撤销已提交事务。实验只证明这两个已知注入位置：**不是提交期间断网的模拟，也不覆盖提交结果未知**。实际提交故障必须按数据库证据分类；不看到 500 就自动重试，不把基础设施失败改成业务 409。

### 4.3 资源释放怎样核对

教师观察器记录每请求获取与关闭次数，覆盖正常、业务冲突、输出校验失败与两种故障。连接获取失败时没有交出资源，不要求出现虚构的“成功关闭”事件。只观察进程正常运行的请求生命周期，不宣称 finally 能抵抗强杀或机器断电。

## 五、统一错误：业务说原因，HTTP 边界决定怎样返回

**课堂 15 分钟。约 5 分钟业务异常与表现层，5 分钟四字段／安全投影，5 分钟未知异常与 OpenAPI 对照。完整处理器为课后可读参考。**

### 5.1 E 阶段公开契约

```json
{"code":"question_not_found","message":"问题不存在","detail":null,"request_id":"demo-01"}
```

- code 为稳定机器判据，message 给人读；不按具体消息文字分支。
- detail 只含经过筛选的结构或 null；不直接返回原始请求、异常文本、SQL、input、ctx。
- request_id 用于日志关联，不是用户身份、认证凭据或业务幂等键。

覆盖本课普通 JSON 请求：业务 404／409、请求 422（含坏 JSON）、框架未知路径 404／方法 405、响应启动前的未知异常 500（含输出校验失败）。**`/healthz` 的预期数据库 503 是例外，仍只含 status；第 5 课 HTML 页面错误另走 HTML 表现。** 直接返回 Response 不会自动走异常处理器；流式响应已启动或后台任务失败，不能重新改写成这份 JSON。

### 5.2 业务异常不携带 HTTP 状态码

E 阶段用以下定义**替换**原 DuplicateTitle，并新增缺失资源异常。服务里的名字引用同步指向新定义，不保留两个同名但不同对象的异常类：

```python
class AppError(Exception):
    pass


class QuestionNotFound(AppError):
    pass


class DuplicateTitle(AppError):
    pass


BUSINESS_HTTP = {
    QuestionNotFound: (404, "question_not_found", "问题不存在"),
    DuplicateTitle: (409, "duplicate_title", "标题已存在"),
}


def get_question_service(conn, qid):
    result = find_question(conn, qid)
    if result is None:
        raise QuestionNotFound()
    return QuestionOut.model_validate(result)
```

创建服务继续显式提交、抛 DuplicateTitle；端点不再就地翻译。同一个服务以后可以给 HTML 或 CLI 用，不必知道 HTTP 404 或页面模板。Pydantic DTO 是课程取舍，不宣称完全没有框架依赖。

### 5.3 四类处理器与安全投影

```python
import logging
from http import HTTPStatus
from typing import Any

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

logger = logging.getLogger("course.requests")


class ErrorOut(BaseModel):
    code: str
    message: str
    detail: Any
    request_id: str


def error_response(request, status, code, message, detail=None, headers=None):
    rid = getattr(request.state, "request_id", "-")
    body = ErrorOut(code=code, message=message, detail=detail, request_id=rid)
    response = JSONResponse(status_code=status, content=body.model_dump(mode="json"),
                            headers=headers)
    response.headers["X-Request-ID"] = rid
    return response


def register_handlers(app):
    @app.exception_handler(Exception)
    async def unexpected(request: Request, exc: Exception):
        logger.error(json.dumps({
            "event": "request_error",
            "request_id": getattr(request.state, "request_id", "-"),
            "error_type": type(exc).__name__,
        }, ensure_ascii=False))
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
            fallback = "HTTP 请求失败"
        return error_response(request, exc.status_code, f"http_{exc.status_code}",
                              messages.get(exc.status_code, fallback), headers=exc.headers)
```

- 捕获 Starlette 的 HTTPException 基类，才能覆盖框架 404／405；保留 Allow、WWW-Authenticate、Retry-After 等必要头。不以此要求学生现在实现认证或限流。
- RequestValidationError 只代表请求解析／校验失败。服务里直接调用 `model_validate` 失败不是请求 422，仍为服务端错误；不注册“所有 Pydantic 错误都返回 422”的处理器。
- detail 的 loc 可能包含字段路径与数组下标；模型拒绝额外字段时也可能包含客户端提供的键名。这里去掉原始值，**不把保留 loc 说成已彻底匿名化**；课堂只用虚构数据，错误文本在页面仍用安全文本渲染。
- 未知异常只公开固定正文；示例结构化日志只记异常类型，不记可能含请求正文的异常字符串。教师在隔离环境通过 IDE 看调用栈；生产诊断需额外受控、脱敏的日志策略，不投影真实秘密。

### 5.4 E 阶段端点与文档一起换

以下替换 R 阶段创建／详情函数，列表函数保持不变；函数由稍后的应用工厂注册，不再保留旧装饰器：

```python
def create_question(payload: QuestionCreate, response: Response, conn: ConnDep):
    result = create_question_service(conn, payload)
    response.headers["Location"] = f"/questions/{result.id}"
    return result


def get_question(qid: int, conn: ConnDep):
    return get_question_service(conn, qid)
```

所有错误都固定四个键，detail 没有内容时也发 null。ErrorOut 的 detail 必填但可为任意安全 JSON，包括 null；复杂字段错误 Schema 的精化留到契约化 API 阶段。

第 2 课页面检查 `!response.ok`，即使仍显示“服务返回 HTTP 500”也能继续正确分流。若增加 message/request_id 提示，错误正文只读取一次；解析失败保留原 HTTP 状态级提示，不让错误页的二次 JSON 解析覆盖最初失败。四态和 `textContent` 不变，不强迫本课重写页面。

## 六、关联日志与探针：补齐请求之外的共同工作

**课堂 10 分钟。约 6 分钟解释中间件正常／异常两条路径，4 分钟检查探针获取失败与恢复。代码模板随包提供，不现场全文抄写。**

### 6.1 request-id 模板必须能解释

```python
import re
import time
import uuid


def register_trace(app):
    @app.middleware("http")
    async def trace(request: Request, call_next):
        supplied = request.headers.get("X-Request-ID", "")
        rid = supplied if re.fullmatch(r"[A-Za-z0-9._-]{1,64}", supplied) else uuid.uuid4().hex
        request.state.request_id = rid
        started = time.perf_counter()
        outcome = "error"
        logger.info(json.dumps({"event": "request_start", "request_id": rid,
                                "method": request.method}, ensure_ascii=False))
        try:
            response = await call_next(request)
            outcome = response.status_code
            response.headers["X-Request-ID"] = rid
            return response
        finally:
            logger.info(json.dumps({
                "event": "request_end", "request_id": rid, "outcome": outcome,
                "duration_ms": round((time.perf_counter() - started) * 1000, 1),
            }, ensure_ascii=False))
```

本课首次引入合法格式 `[A-Za-z0-9._-]{1,64}`。缺失或非法时生成 uuid 十六进制 id；客户端提供合法值可以保留，不保证全局唯一或可信。不要放敏感信息，不把 id 当权限证据。模板记录 method，不记可能含用户输入的 query、body 或动态路径；独立教师启动配置启用该 logger 的 INFO 级别与消息输出，单有 `logger.info` 代码不等于已经配置日志出口。

一条请求对应同一 id 的 start/end；普通错误还有相同 id 的响应头及正文。教师启动器可配置 `logging.basicConfig(level=logging.INFO, format="%(message)s")`；这是独立进程的日志配置约定，不要求覆盖已有应用的日志系统。

先预测：端点抛未捕获 RuntimeError，call_next 会正常交回一个 500 Response 吗？固定 `debug=False`，本实现的层次是：

```text
ServerErrorMiddleware（未知异常兜底／Exception 处理器）
  → 用户 trace 中间件
    → ExceptionMiddleware（业务异常、HTTP 异常、请求校验异常处理器）
      → 路由、依赖、端点
```

普通业务异常在内层转为响应，call_next 正常返回；未捕获异常穿过用户中间件后，外层才生成 500。因此：**finally 负责异常时也有 end 日志，error_response 负责给外层 500 补响应头与正文中的 id**。仅在 try 正常返回后补头、记日志，覆盖不了这一分支。

outcome="error" 表示 call_next 抛出，不伪装成已经观察到 HTTP 500；计时到 call_next 返回／抛出，不是流式正文完全传输的耗时。异常发生在响应已启动之后时只能记录，不能再承诺客户端得到统一正文。debug 模式可能改用调试响应，正式验收固定关闭。

### 6.2 `/healthz`：只升级能力，不换正文结构

```python
from contextlib import closing
from typing import Literal


class HealthOut(BaseModel):
    status: Literal["ok", "degraded"]


def healthz():
    try:
        with closing(open_connection()) as conn:
            conn.execute("SELECT 1").fetchone()
    except sqlite3.Error:
        body = HealthOut(status="degraded")
        return JSONResponse(status_code=503, content=body.model_dump())
    return HealthOut(status="ok")
```

新增的是数据库连接与最小语句检查：正常仍为 200、`{"status":"ok"}`；预期数据库失败为 503、`{"status":"degraded"}`，**不增加 db 字段，不套普通四字段错误体**。两种响应均有中间件补的 X-Request-ID。

探针必须把获取连接和执行语句放在同一个捕获范围。若先由 ConnDep 获取连接，获取失败发生在端点前，端点里的 except 接不到，会变成通用 500。可以封装专用探针函数，不强求全项目零处 `open_connection()`。

SELECT 1 只验证当前连接和简单语句可用，不证明 questions 表、迁移、所有查询或写权限正确。SQLite 可能自动创建不存在的文件，教师连接工厂须固定预期教学库路径；不能将一次探针成功说成库文件和数据一定正确。程序错误不是预期数据库故障，不应无差别吞成 503。

### 6.3 最终应用装配（教师参考）

在模型、数据函数、依赖、最终端点、处理器与中间件均已定义后，组装 E 应用。**创建新实例替换 R 应用**，不向已经服务中的实例动态添加处理器或重复路由。同源页面与 `/static` 的挂载沿用教师包，以下只列本课 API 部分：

```python
API_ERROR_RESPONSES = {
    422: {"model": ErrorOut, "description": "请求校验失败"},
    500: {"model": ErrorOut, "description": "服务端处理失败"},
}
REQUEST_ID_HEADER = {
    "description": "本次请求的关联标识",
    "schema": {"type": "string"},
}


def make_application():
    application = FastAPI(debug=False)
    register_handlers(application)
    register_trace(application)
    application.add_api_route(
        "/questions", list_questions, methods=["GET"], response_model=QuestionListOut,
        responses={200: {"headers": {"X-Request-ID": REQUEST_ID_HEADER}},
                   **API_ERROR_RESPONSES})
    application.add_api_route(
        "/questions/{qid}", get_question, methods=["GET"], response_model=QuestionOut,
        responses={404: {"model": ErrorOut, "description": "问题不存在"},
                   **API_ERROR_RESPONSES})
    application.add_api_route(
        "/questions", create_question, methods=["POST"], status_code=201,
        response_model=QuestionOut,
        responses={201: {"headers": {
            "Location": {"description": "新问题详情路径", "schema": {"type": "string"}},
            "X-Request-ID": REQUEST_ID_HEADER,
        }}, 409: {"model": ErrorOut, "description": "标题已存在"},
            **API_ERROR_RESPONSES})
    application.add_api_route(
        "/healthz", healthz, methods=["GET"], response_model=HealthOut,
        responses={503: {"model": HealthOut, "description": "数据库检查失败"},
                   500: {"model": ErrorOut, "description": "非预期程序错误"}})
    return application
```

教师入口取得 `app = make_application()` 后补原有静态页挂载。responses 覆盖默认 422 模型，并登记详情 404、创建 409、探针 503 和创建 Location；框架未知路径无法作为一个不存在的 operation 枚举，404／405 及全部响应的 request-id 规则另在契约说明中列出。本节没有逐状态穷举所有响应头 Schema，不把该节选说成已经生成完整课程快照。

responses 主要是文档声明，不自动校验直接 Response 的正文，所以处理器和探针显式先构造模型；行为与 `/openapi.json` 都要核对。`/docs` 外部资源不可达时改用本地 JSON 和请求工具，不宣称文档 UI 已离线验收。

## 七、回收、验收与第 5 课交接

**课堂 7 分钟。用一条创建路径收束，再说明一次作业包。**

> 依赖负责连接何时可用和何时关闭；服务负责本次事务提交；处理器决定错误怎样对外表达。成功响应晚于提交完成，但失败响应不意味着没有写入。

### 常用写法卡 #4

| 写法 | 替我们完成什么 | 必须知道的边界 |
|---|---|---|
| `Depends(get_conn)` | 框架准备并注入资源 | 请求内复用不等于全局共享；非法参数时依赖也可能已运行 |
| yield + finally | 使用期间交出连接，最后清理 | 默认 request 退出在响应发送后，不在这里 commit |
| 服务层显式 commit／rollback | 控制一次业务操作的事务边界 | 提交确认后的错误不能用 rollback 撤销已提交事务 |
| AppError + exception_handler | 把业务原因集中翻译为 HTTP | 不是所有数据库错误都是冲突；不是所有校验错误都是请求 422 |
| ErrorOut | 约定 code/message/detail/request_id | 探针、HTML、已启动的流式响应有不同表现边界 |
| request-id 中间件 + 500 兜底 | 关联进入／离开／错误与响应 | id 不是身份；finally 日志不等于已经看到了最终状态 |

### 7.1 验收矩阵

| 范围 | 达标结果 |
|---|---|
| R 阶段 | 三端点读取／创建／校验／旧错误体不变；探针仍纯存活；服务提交未移位 |
| 成功契约 | 字面搜索、分页及五字段不变；201 + Location；独立连接回读标签和正文 |
| 事务对照 | 提交前失败 500 且无本次写入；确认提交后失败 500 且写入仍在；标注实际注入点 |
| E 业务错误 | 缺失整数 id 为 404/question_not_found；标题重复为 409/duplicate_title；均为四字段 |
| E 框架与未知错误 | 请求／坏 JSON 为 422/validation_error；未知路径 404/http_404；方法 405/http_405 且保留 Allow；未知及输出失败为 500/internal_error |
| 错误安全 | 不回显原始值、SQL 或异常文本；字段定位保留 loc/type；说明 loc 不等于彻底脱敏 |
| 日志 | 正常及响应前未知异常有同 id 的 start/end；500 正文、头与 error 记录关联；非法 id 被替换 |
| 资源 | 同请求相同依赖复用；各请求独立获取并关闭；获取失败不执行端点；其他失败仍清理 |
| 探针 | 正常 200/status=ok，预期数据库获取或查询失败 503/status=degraded，恢复后 200；不新增 db 字段 |
| 文档与页面 | OpenAPI 正确登记错误模型与 Location；第 2 课四态、正文显示、安全文本及恢复不退化 |

### 7.2 一个作业包

1. R 阶段重构 diff 与教师回归结果，指出三个端点的资源入口、服务提交位置和合理保留的探针例外。
2. E 阶段四字段错误迁移与契约快照；说明批准的变化，不重写全部历史快照来掩盖破坏性变更。
3. 两组事务故障的“注入点 → HTTP → 独立连接数据”对照；可复用其中一次未知异常记录作为 request-id 日志与响应证据，不再追加一套独立报告。
4. 一处“提交先于响应”的代码／事件说明；一次 AI 对依赖求值与清理的解释核对，正确时记录接受理由和证据。

不要求学生实现故障工具、数据库设施、配置框架或完整测试系统；完整处理器由教师提供并要求能解释。学生未完成的独立端点接线须课后补齐，不能把基础验收称为选做。选做依赖工厂，仅在隔离实验说明复用收益与函数对象身份，不提前布置认证。

### 7.3 第 5 课的明确起点

- 继续 SQLite 同步读写、同一 QuestionCreate/QuestionOut、同一服务层显式提交；HTML 与 JSON 调用同一业务服务，不在 HTML 端点或依赖退出时另立提交点。
- 保留三个 JSON 业务端点和探针；列表 items/total/page、page_size 默认 20 上限 50、原 id/title/body/tags/created_at 及标题唯一规则不变。
- 第 5 课新增 SSR 列表／详情／创建页，表单输入先转换再复用模型；失败回填、成功 303。JSON 四字段错误不强行套给 HTML 页面，表现层分别翻译相同业务原因。
- 本课首次建立 request-id 与结构化日志；下一课沿用异常路径覆盖，不撤回正确实现制造反例。第 5 课重点是 SSR 与同步／异步执行方式，不把本课遗漏的中间件讲解全部后移。
- 标签仍为 JSON 文本、没有作者关联；第 6 课教师迁移到 PostgreSQL、建关联表时提供明确的数据迁移和去重规则。第 7 课换 Session 仍遵循服务层事务边界，不保证只改一个依赖文件。

## 八、制作与验证状态

本稿给出 R/E 过程、最终 API 装配与隔离故障关键路径，仍依赖第 3 课的模型／数据函数、教师连接工厂、静态页、初始化与升级设施。不能指示学生切换不存在的 tag，也不从旧 ORM 工程推导本课要求。

- **本轮机制验证已完成**：复用 Python 3.12.12、FastAPI 0.141.1、Starlette 1.6.0、Pydantic 2.13.5、httpx 0.28.1，提取本稿代码并组合第 3 课模型／数据函数。389 项行为／Schema 断言通过：R 阶段回归、E 阶段错误及安全投影、必要 HTTP 头、request-id 配对日志、依赖复用与关闭、探针故障与恢复、输出校验回滚、NOT NULL 分类、两种事务故障及 OpenAPI；另 1 项课时断言核对大纲逐项为 5/15/18/25/15/10/7，共 95 分钟，加 5 分钟缓冲。
- **时序与限制**：隔离 SQLite 共享内存库使用独立连接回读；TestClient 外层 ASGI 观察器确认服务提交先于响应启动、默认依赖关闭晚于普通响应完成。连接获取／查询／提交方法的设施故障为模拟，提交前／确认后实验实际执行 SQLite 写入及 commit，但不证明文件落盘、进程重启、真实断连或提交结果未知。当前 httpx 适配有弃用提示，未安装或升级依赖；临时核验脚本不是已交付的教学工程。
- **跨课扫描**：已核对第 1–4 课的阶段性参数、字段、错误体、探针与事务交接，并通过 `git diff --check`。后续第 5 课已按第四版及本稿 7.3 重写，继续 SQLite、同一模型和服务层提交，新增 HTML 表现适配；其验证结果与独立工程待办见[第 5 课制作状态](lesson-05.md#九制作与验证状态)，不把底稿完成视为配套工程已完成。
- **试讲前必须补齐**：第 4 课独立阶段副本、显式连接选项、R/E 对照回归器、日志启动配置、两种固定故障开关、依赖和 ASGI 事件观察器、完整 OpenAPI 快照及页面回归。
- **仍需真实验收**：本地 HTTP、IDE 断点、文件库重启与数据保留、真实连接故障与恢复、页面显示及投影；进程内机制测试不等于这些条件已完成。
- **首轮试讲记录**：25 分钟内两端点接线与两组数据回读的完成情况、把 finally 当作 commit 的比例、把 500 当作无写入的比例。超时压缩参考代码阅读，不增加隐含学生设施任务。
