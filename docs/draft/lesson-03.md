# 第 3 次课教学底稿（完整整改版）
## 路由选择与输入 / 输出契约

## 〇、备课定位与交接起点

主线：**输入按声明收窄，输出按承诺组织；知道这两道边界能保证什么。** 入口校验不等于授权，出口模型不等于业务正确，也不是不可绕过的安全屏障。

起点是第二课修好的 M0 页面与接口，不是旧稿里凭空出现的六端点项目。M0 已有部分路径类型约束、404 和探针；不能称学生“两道闸门一道都没有”。本课新增 JSON 创建，完善列表与详情契约，并**显式进行一次前后端同步迁移**。

### 95 分钟教学 + 5 分钟缓冲

| 单元 | 分钟 | 课堂处理 |
|---|---:|---|
| 一、起点与迁移范围 | 5 | 主讲 |
| 二、隔离反例与两道边界 | 8 | 教师对照，不修改合格库制造错误 |
| 三、路由表与选择 | 12 | 教师打印与方法 / 路径实验 |
| 四、参数来源与 schema | 12 | 主讲输入来源、清洗顺序 |
| 五、同一端点的入口 / 出口验证 | 22 | 唯一学生现场必做 |
| 六、业务端点与输出映射 | 14 | 教师演示迁移，完整 SQL 课后读 |
| 七、OpenAPI 与契约循环 | 12 | 主讲声明与运行的区别 |
| 八、作业与交接 | 10 | 5 分钟核对基线，5 分钟布置 |
| 合计 | 95 | 另留 5 分钟缓冲 |

A 档基础材料可课后读，不要求学生现场完成所有 SQL、三个端点与文档。B 档才是更多边界组合、路径转换器、跨栈和 ASGI 阅读。超时将路由对象属性、完整字段表转课后，保留第五单元的证据与解释。PATCH 不在本课实现或评分。

## 一、本课允许的契约迁移

**课堂 5 分钟。** 先展示旧 / 新响应及页面受影响位置，再修改代码。

| 内容 | 第二课交付 | 本课交付 |
|---|---|---|
| 列表路径 | GET /questions | 不变 |
| 查询参数 | keyword/page，固定页长 | keyword/page/page_size；page≥1；page_size 默认20、1—50 |
| 列表正文 | success/data，含正文 | items/total/page；每项 id/title/created_at/author，不含正文 |
| 详情正文 | id/title/body/created_at | 保留这些字段，新增 author={id,display_name} |
| 创建 | 尚非必做端点 | POST /questions，QuestionCreate → QuestionOut，201 + Location |
| /healthz | 200 ok/ok；503 degraded/down | 完全保留，必做而非拓展 |
| 错误正文 | M0 详情404与框架422不同 | 404保持 code/message/request_id，创建409同形；422先保留框架格式 |

第四课再迁移业务 JSON 错误为 `code/message/detail/request_id`，本课不暗中提前统一。列表不输出正文是明确的载荷选择，不能只改容器而忘记第二课 render 还读 q.body。

保留 request-id、日志与静态页。当前作者固定为教师夹具中的用户1，**不是已经完成登录或授权**。M0 数据中没有 users 和 question_tags：教师须提供隔离数据升级模板，保留既有问题 id/title/body/created_at，为旧问题回填存在的作者，并建立标签关联；不能运行原 seed 覆盖学生数据。

## 二、反例：一次只让一个问题起作用

**课堂 8 分钟。**

不再把手写 request.json、SQL 错误、作者外键不存在、路由冲突和出口泄漏混在一个所谓“已验证版本”中。

| 对照 | 固定条件 | 预期区别 |
|---|---|---|
| 路由选择 | 同 GET 方法，独立路由应用 | 参数路径先登记时 latest 进入参数校验而得422 |
| 入口校验 | 同一 POST，使用内存夹具，无数据库 | 非法输入不进入端点，合法输入进入 |
| 输出过滤 | 同一合法 POST、相同嵌套数据 | 无模型时多余字段暴露，有模型时过滤 |
| 输出边界 | 同一模型，换直接 Response / 缺字段 | 前者绕过，后者服务端校验失败 |

所有敏感字段用明显虚构占位，例如 `password_hash="not-a-real-hash"`。不使用真实用户数据，也不宣称“功能测试永远发现不了泄漏”：有字段白名单断言的测试就可以发现。

## 三、路由选择：打印内部结构，再解释结果

**课堂 12 分钟，教师演示。**

### 3.1 装饰器登记，不是收到请求才执行

课前的 route 装饰器把函数存入表；FastAPI 在执行路由声明时构造路由对象。不能说所有框架只能用 list 或全部按同一种算法匹配；这里只观察当前 FastAPI/Starlette 的实现。

```python
from fastapi import FastAPI
from fastapi.routing import APIRoute

route_app = FastAPI()

@route_app.get("/questions/{qid}")
def detail_demo(qid: int):
    return {"id": qid}

@route_app.get("/questions/latest")
def latest_demo():
    return {"id": 7}

for route in route_app.routes:
    print(type(route).__name__, getattr(route, "methods", None), route.path)

selected = next(route for route in route_app.routes
                if isinstance(route, APIRoute)
                and route.path == "/questions/{qid}" and "GET" in route.methods)
print(selected.path_regex, selected.endpoint, selected.response_model)
```

不要用 `app.routes[4]`。默认文档路由含 `/docs/oauth2-redirect`，自定义配置还可能改变数量。源码位置、方法和路径比固定下标稳定。

### 3.2 路径与方法共同决定匹配

相同方法下，默认参数路径匹配到字符串 `latest`，随后尝试转为 int，得422；`latest_demo` 没被调用。不是详情函数返回了422，而是框架在调用它之前拒绝了参数。

- 方法不匹配不等于立即使用这个路径候选；后面仍可能有完整匹配。
- 找不到完整匹配但有路径候选时可能得405；完全无路径则404。
- 重排为静态 `/questions/latest` 在参数路由前，即可避免本例遮蔽。
- `/questions/{qid:int}` 收窄路径转换器也是一种选择，但改变哪些请求得到404还是422；不是无需验收的替换。

演示重新构造应用并更换登记顺序，不把三个装饰器叠在同一个省略函数上冒充修复。`/questions/latest` 仅为实验或既有可选功能，不增加一个基础必交端点。

## 四、参数与输入模型：先清洗，再检验最终值

**课堂 12 分钟。**

| 来源 | 声明 | 本课例子 |
|---|---|---|
| 路径 | 与模板同名，Path 明确约束 | qid 整数≥1 |
| 查询串 | Query | keyword、page、page_size |
| JSON 正文 | Pydantic 模型参数 | QuestionCreate |
| 请求头 / Cookie | Header / Cookie 显式声明 | 后续认证与状态 |
| 表单 | Form | 第五课；不等同 JSON 模型参数 |

这是常用默认推断，不是完整算法；Body、Query 等显式元数据可以改变来源。查询串通常以文本到达，JSON 原本就有数字、布尔、数组与 null，不能把所有外部输入画成字符串。

### 4.1 本课与第五课共享的创建模型

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

为什么 before：`"    x"` 原长5，清洗后只有1。after 先按原值通过长度再返回 x，会破坏“最终对象满足长度约束”的承诺。before 先规范化，再进行内置类型与长度校验；非字符串交给类型校验，不用 str() 偷偷把任意对象变成合法输入。

`extra="forbid"` 拒绝多余 author_id/is_admin；默认 ignore 虽不把字段加入模型，但不会报告调用者多传。forbid 不是认证：作者仍须由可信服务端上下文决定，第十四课实现。

tags 是可省略列表，最多5个字符串；本课不新增标签字符集规则。教师持久化模板须保存所提交标签，不能接受后静默丢弃；重复标签按集合关联处理。更复杂的标签规范需另声明契约。

### 4.2 入口保证范围

“非法请求不进入端点”适用于框架自动校验这条路径。某些依赖和中间件可能已执行，所以不能说整个应用绝无动作。手工 `model_validate` 会抛 Pydantic `ValidationError`，不是 `RequestValidationError`；在其他入口直接调用业务函数也不会自动经过 HTTP 校验。

基础结构、长度和局部跨字段约束可放 schema；唯一性、资源状态等需要数据库与业务判断。不能因此宣称所有 if 都错误，或内部对象已被授权、永远不会被修改为非法状态。

## 五、唯一现场必做：在同一 POST 上证明两道边界

**课堂 22 分钟。** 使用独立内存实验，避免数据库约束先拦住输入而混淆观察。下面与第四单元模型、下述输出模型一起构成参考实验；不把实验 POST 当作真实持久化接口。

### 5.1 出口模型

```python
from datetime import datetime

class AuthorOut(BaseModel):
    id: int
    display_name: str

class QuestionBriefOut(BaseModel):
    id: int
    title: str
    created_at: datetime
    author: AuthorOut

class QuestionOut(QuestionBriefOut):
    body: str

class QuestionListOut(BaseModel):
    items: list[QuestionBriefOut]
    total: int = Field(ge=0)
    page: int = Field(ge=1)
```

输出默认忽略额外字段；若选择 extra=allow 或自定义序列化，行为会改变。入口用 forbid、出口白名单投影是本课明确选择，不泛化为 Pydantic 的所有用法。

### 5.2 可切换的实验应用

```python
from fastapi import FastAPI
from fastapi.responses import JSONResponse


def make_boundary_app(use_model=True, direct=False, missing=False):
    lab = FastAPI(debug=False)
    lab.state.entered = 0

    @lab.post("/lab/questions", status_code=201,
              response_model=QuestionOut if use_model else None)
    def boundary_demo(payload: QuestionCreate):
        lab.state.entered += 1
        result = {
            "id": 7, "title": payload.title, "body": payload.body,
            "created_at": "2026-09-01T08:00:00Z",
            "author": {"id": 1, "display_name": "课程用户",
                       "email": "demo@example.invalid",
                       "password_hash": "not-a-real-hash"},
            "internal_note": "仅用于隔离对照",
        }
        if missing:
            result.pop("body")
        if direct:
            return JSONResponse(status_code=201, content=result)
        return result

    return lab
```

实验顺序：
1. 先给 `/lab/questions` 发缺 body、空白短标题或多余 author_id，核对422、loc/type、entered 不增或端点断点未命中。
2. 发合法正文，核对清洗后的 title；无输出模型时观察多余字段。
3. 同数据启用模型，核对嵌套作者的敏感字段和 internal_note 消失。
4. 教师展示 direct=True：直接 JSONResponse 绕过模型过滤，额外字段又出现；这条路径不能当作合格业务输出。
5. 教师展示 missing=True：缺必填 body，输出校验失败得服务端500，而不是客户端422。用 TestClient 时设置 `raise_server_exceptions=False` 才看错误响应；默认模式可能把服务端异常抛给测试程序。

学生提交前3步的同一任务记录，并说明后2步的边界。不要求四次大型现场重写，也不强迫预测必须有一次错误。计数只用于单请求实验，不是并发安全统计。

### 5.3 读422

- loc 指明 body/query/path 等位置及嵌套字段路径。
- type 是机器分类，msg 是人读文案；依版本锁定核对，不以英文句子比较分支。
- detail 可以报告多项错误，但不保证对任意校验器一次穷尽所有错误。
- 默认响应可能包含 input，不能用真实秘密做教学输入；第四课会给安全的错误投影。
- 当前 FastAPI 对坏 JSON 也返回422；本课保留。422 已纳入现代 HTTP 语义规范，不说它只是非标准借用。

## 六、三个业务端点：迁移形状，不遗漏数据含义

**课堂 14 分钟；完整代码 A 档课后参考。** 本节使用同步 SQLAlchemy Core Connection 与 PostgreSQL 参数化 SQL，不是 ORM。教师提供持久化模板，学生重点修改和验证边界；本仓库尚未落地独立第三课工程。

### 6.1 联表显式投影，消除同名列

```python
from sqlalchemy import text

DETAIL_SQL = text("""
SELECT q.id AS question_id, q.title, q.body,
       q.created_at AS question_created_at,
       u.id AS author_id, u.display_name AS author_name
FROM questions q JOIN users u ON u.id = q.author_id
WHERE q.id = :qid
""")


def find_detail(conn, qid):
    row = conn.execute(DETAIL_SQL, {"qid": qid}).mappings().one_or_none()
    if row is None:
        return None
    return {
        "id": row["question_id"], "title": row["title"], "body": row["body"],
        "created_at": row["question_created_at"],
        "author": {"id": row["author_id"], "display_name": row["author_name"]},
    }
```

不再 `SELECT q.*, u.*`；同名 id、created_at 可能造成歧义或映射错误，类型正确的作者id也可能被误当问题id。出口模型验证形状，不验证字段属于正确实体。过滤实验用第五单元夹具，不在真实查询里多取敏感数据。

### 6.2 列表与稳定分页

```python
LIST_SQL = text("""
SELECT q.id AS question_id, q.title,
       q.created_at AS question_created_at,
       u.id AS author_id, u.display_name AS author_name
FROM questions q JOIN users u ON u.id = q.author_id
WHERE q.title ILIKE :pattern ESCAPE '!'
ORDER BY q.created_at DESC, q.id DESC
LIMIT :limit OFFSET :offset
""")
COUNT_SQL = text("""
SELECT count(*) FROM questions q
JOIN users u ON u.id = q.author_id
WHERE q.title ILIKE :pattern ESCAPE '!'
""")


def literal_pattern(keyword):
    value = keyword.replace("!", "!!").replace("%", "!%").replace("_", "!_")
    return f"%{value}%"


def read_page(conn, keyword, page, page_size):
    pattern = literal_pattern(keyword)
    rows = conn.execute(LIST_SQL, {
        "pattern": pattern, "limit": page_size, "offset": (page - 1) * page_size,
    }).mappings().all()
    total = conn.execute(COUNT_SQL, {"pattern": pattern}).scalar_one()
    items = [{"id": row["question_id"], "title": row["title"],
              "created_at": row["question_created_at"],
              "author": {"id": row["author_id"], "display_name": row["author_name"]}}
             for row in rows]
    return QuestionListOut(items=items, total=total, page=page)
```

本课迁移同时声明字面关键词匹配，`%/_` 不再被无声当成通配符；参数化防止值改变 SQL 结构，LIKE 转义处理的是另一件事。若原项目已经采用其他搜索口径，迁移记录必须标出，不能把语义变化伪装成纯重构。SQL 原理第六课展开，第三课模板提供。

排序用唯一id决胜；并发插删下 OFFSET 仍可能漂移，列表和 total 在默认隔离下也不保证同一快照。当前实验用固定数据，不提前承诺强一致分页。

### 6.3 端点边界与错误

下面的 app、engine、logger 和 request-id 中间件来自 M0；不是重新创建 app 后忘记原路由。迁移时替换旧列表与详情的路由声明，不把同方法同路径的新函数追加在旧路由后，否则请求仍可能命中旧实现。保留其余页面、探针和观察路由。辅助模型是本课暂存的错误契约：

```python
from fastapi import Path, Query, Request, Response
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError

class ExistingErrorOut(BaseModel):
    code: str
    message: str
    request_id: str


def existing_error(request, status, code, message):
    error = ExistingErrorOut(code=code, message=message,
                            request_id=request.state.request_id)
    return JSONResponse(status_code=status, content=error.model_dump())


@app.get("/questions", response_model=QuestionListOut, status_code=200,
         tags=["questions"], summary="问题列表")
def list_questions(
    keyword: str = Query(""), page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=50),
):
    with engine.connect() as conn:
        return read_page(conn, keyword, page, page_size)


@app.get("/questions/{qid}", response_model=QuestionOut, status_code=200,
         responses={404: {"model": ExistingErrorOut}},
         tags=["questions"], summary="问题详情")
def get_question(request: Request, qid: int = Path(ge=1)):
    with engine.connect() as conn:
        result = find_detail(conn, qid)
    if result is None:
        return existing_error(request, 404, "question_not_found", "问题不存在")
    return QuestionOut.model_validate(result)
```

这里错误 JSONResponse 是有意的表现层例外，用 ExistingErrorOut 先验证再输出，并显式声明 OpenAPI；不能以这个例外为理由把业务成功输出也无约束地直接返回。

### 6.4 创建参考与事务前置条件

同步创建用 engine.begin 管理连接与事务，先构造合法输出再退出提交，成功后才返回201。完整事务课程在第七课，但当前模板不能先发成功再提交。

教师提供的持久化模板接口：

```python
def insert_question_with_tags(conn, payload, author_id):
    qid = conn.execute(text("""
        INSERT INTO questions (title, body, author_id)
        VALUES (:title, :body, :author_id) RETURNING id
    """), {"title": payload.title, "body": payload.body,
           "author_id": author_id}).scalar_one()
    for name in dict.fromkeys(payload.tags):
        tag_id = conn.execute(text("""
            INSERT INTO tags (name) VALUES (:name)
            ON CONFLICT ON CONSTRAINT tags_name_key DO NOTHING RETURNING id
        """), {"name": name}).scalar_one_or_none()
        if tag_id is None:
            tag_id = conn.execute(text("SELECT id FROM tags WHERE name = :name"),
                                  {"name": name}).scalar_one()
        conn.execute(text("""
            INSERT INTO question_tags (question_id, tag_id) VALUES (:qid, :tid)
        """), {"qid": qid, "tid": tag_id})
    return qid


@app.post("/questions", response_model=QuestionOut, status_code=201,
          responses={409: {"model": ExistingErrorOut}},
          tags=["questions"], summary="创建问题")
def create_question(payload: QuestionCreate, request: Request, response: Response):
    try:
        with engine.begin() as conn:
            qid = insert_question_with_tags(conn, payload, author_id=1)
            result = QuestionOut.model_validate(find_detail(conn, qid))
    except IntegrityError as exc:
        constraint = getattr(getattr(exc.orig, "diag", None), "constraint_name", None)
        if constraint == "questions_title_key":
            return existing_error(request, 409, "duplicate_title", "标题已存在")
        raise
    response.headers["Location"] = f"/questions/{qid}"
    return result
```

前提：PostgreSQL + psycopg，命名唯一约束 `questions_title_key`、`tags_name_key`，question_tags 联合主键，已有用户1；标签回读使用 READ COMMITTED 且本课不并发删除标签。其他数据库不能照抄错误诊断或 ON CONFLICT 语法后声称兼容。第六、七课会系统解释；本课只用已准备模板。

标题唯一是课程业务约定，不是所有问答系统通则。先查后写不能保证并发唯一性；数据库约束才兜住竞争。不要撤掉已有正确约束制造故障。异常只在事务上下文退出后转换，不能吞掉失败再继续提交。没有匹配约束名的数据库异常仍按未知错误处理，不能全部误报409。

### 6.5 保留健康检查与页面同步

`/healthz` 继续独立捕获数据库连接获取与 SELECT 1 的失败，200 ok/ok、503 degraded/down。不使用 QuestionOut，不降级为选做，不变成业务500。

第二课前端迁移清单：
- URL 参数增加 page_size，名称不改为 size。
- `readSearch` 校验 `items/total/page`；每项改验 id/title/created_at/author.id/author.display_name。
- 返回前端适配器的 items=payload.items；删除旧 success/data 条件。
- render 不再读 q.body，改显示标题与作者（正文去详情获取）。文本仍用 textContent。
- loading、empty、HTTP/解析/结构错误、request-id 和 finally 恢复不退化。
- 固定数据下回归搜索与排序；同步验收脚本的**已批准变更项**，M0旧快照保留，不为了忽略失败删断言。

## 七、OpenAPI：声明不是全行为推断

**课堂 12 分钟。**

打开 `/openapi.json` 和 `/docs` 对照：文档 UI 渲染机器契约；路径参数、模型、成功状态与一些默认校验响应可自动生成，但函数里 raise404、直接 JSONResponse 或全局处理器**不会自动推导全部错误**。

上节用 responses={404/409: ...} 显式登记。本课默认422可用 FastAPI 生成模型，第四课改正文后必须覆盖文档中的422模型。给响应写文档也不自动验证 handler 实际返回，仍要跑请求。

契约先行小循环，不新增第四个现场任务：
1. 人确认 QuestionCreate / QuestionOut 和业务判据。
2. 让 AI 在现有模板中补创建实现，禁止擅改公开字段、忽略 tags、接受客户端作者或自行部署。
3. 检查输入拒绝、输出字段、201/404/409、健康检查和数据实际持久化。
4. 合理实现可以保留；发现问题附最小 diff，不要求凑错误数量。

schema 是需求的结构部分、实现约束和验收依据，但不能管住错误关联、授权、唯一性或所有副作用。schema 也能被改错、绕过；审查与测试共同保护它，不能说“AI 也绕不过去”“一次投入永久有效”。

类型生成必须重新生成并运行类型检查才可能发现客户端不兼容，不是后端一变前端自动即时失败。第九课系统学习测试设计与 CI；**现在就运行教师提供的回归检查**，不等第九课才有保障。

## 八、作业、验收与第四课交接

**课堂 10 分钟。**

A 档基础必交：
1. 三核心业务端点：列表、详情、创建；保留 `/healthz`。模型、公开参数与成功状态按第一单元。
2. 一组输入 / 输出对照证据，包含“普通返回会过滤、直接 Response 可绕过、缺字段可能500”的解释。
3. 基础边界表：合法带外侧空白、清洗后不足5、缺 body、正文超上限、多余 author_id、page_size=0/51、qid=abc/0、未知资源；写预测、实测、依据。可课后运行，不降为B档。
4. 新旧契约快照与迁移说明：列表容器、页长参数、作者输出、字面搜索口径、前端对应修改；未批准部分不改变。
5. 固定数据中创建后 GET 到同一 id 与正文，重复标题409；标签关联被保留；探针断连503和恢复200。

没有出现与预测不一致的情况也可满分；不能要求只有错了才记录。B 档是更多类型/边界组合、回答端点的模板迁移、路径转换器和跨框架阅读。**PATCH 延至第八课，不列可选作业诱导提前实现。**

第四课起点：正确的 Query/Path/Field 约束；items/total/page；page_size默认20上限50；QuestionOut；数据库标题唯一；普通同步连接上下文；统一错误体尚未完成。只有一个列表端点很正常，不能声称人人已有四处分页重复。

## 九、课后原理卡

- In 与 Out 回答不同问题：客户端可提交什么、系统承诺输出什么。Create 中 title/body必填但tags可省；不能说全部字段必填。Update 缺失与null单独在第八课建模，不用“全Optional”提前代替语义设计。
- 返回字典本身不是错误；**业务 JSON 成功响应必须经过明确出口契约约束**。查询也应最小化字段，不能只靠出口过滤补救不必要的数据读取。
- ASGI 传递 scope/receive/send；FastAPI在其上组织路由、依赖、校验与响应。同步端点线程栈并不含所有 ASGI 经过，沿用第一课边界。
- 路由和校验机制跨框架有对应物，但实现算法、默认强制校验和输出过滤不同，不泛化某生态“更容易泄漏”。
- Engine 已负责连接池策略；每次 with 获取 Connection 不等于每次新建物理连接。第四课集中生命周期，第七课改数据访问实现，不是从“完全没池”升级。

## 十、素材与验证边界

现有 M0 源码不包含本课用户关联、创建 SQL 和完整契约页面。独立第三课工程、升级 / seed 脚本、回归入口、契约快照和阶段录屏仍待制作，不能把本文代码块当作已经发布的 tags。

制作前按下列门槛验收：
- 路由实验与内存边界实验独立可运行，包含预期失败。
- PostgreSQL 表、完整命名约束与创建模板吻合；旧问题保持原数据，作者确实存在，手工seed id之后同步序列。
- API与页面一起切换；非法输入、额外输出、未知资源、标签、唯一性、探针都有结果证据。
- 断点无reload；Swagger CDN不可用时用curl，不宣称已有离线UI。

本轮从本文代码提取模型、内存实验、路由示例与详情映射进行临时验证。FastAPI 0.141.1、Starlette 1.6.0、Pydantic 2.13.5、SQLAlchemy 2.0.54下，先清洗后约束、非法输入未进端点、嵌套输出过滤、直接Response绕过、缺字段500、坏JSON422及路由顺序/方法对照均通过；SQLite两表夹具验证了问题id与作者id的别名映射。

这不等于完整PostgreSQL创建/标签/唯一约束诊断、数据升级、浏览器或教室验收。临时机制检查也不是已经发布的课堂回归包；只有验证了具体版本和行为才能给对应素材标“已验证”。
