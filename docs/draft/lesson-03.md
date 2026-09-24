# 第 3 次课教学底稿（第四版）
## FastAPI 正式入门：参数、模型与返回值

> **备课基线**：[第四版大纲](../syllabus-v4.md)第 3 课与[新版第 2 课交接](lesson-02.md)。本稿重新组织正文、接口规格、验收与第 4 课交接，尚未移交归档；配套工程和课件需随后重构，不从旧工程反推本课要求。

## 〇、这次课要建立什么

**讲给学生的目标句**：你能用 Pydantic 正常实现列表查询和创建接口，并说出非法输入被挡在了哪里。

第 1 课写过路径参数，第 2 课调用了教师提供的搜索接口。本课不再把后端看成黑盒：先声明从哪里接收参数、允许哪些值，再将已校验的数据接入教师提供的查询／插入骨架。

核心解释是：**走 FastAPI 的自动请求校验路径时，不满足声明的输入会在调用端点函数前被拒绝。** 与它配对的出口约束是：普通返回值按输出模型处理；多余字段与缺失必填字段的结果不同。

课堂路线：**正常列表 → 参数与模型 → 学生创建一条问题 → 三组边界输入 → 入口断点与出口对照 → OpenAPI 核对**。不以路由冲突、多表联查或一组混杂故障作为开场。

### 95 分钟教学 + 5 分钟缓冲

| 分钟 | 教学单元 | 当场产出 |
|---|---|---|
| 5 | 回顾与目标 | 第 2 课页面及读取接口仍正常 |
| 15 | 三类参数与 In/Out 模型 | 字段放在哪里、由谁填写 |
| 20 | 教师构建列表与讲解参数化查询 | Query 声明、占位符绑定和输出映射 |
| 25 | 学生实现创建接口 | 模型、插入字段映射、201 与三组边界输入 |
| 12 | 入口与出口机制 | 非法输入未进端点；缺字段与多字段的区别 |
| 10 | OpenAPI 对照实际请求 | 声明与运行结果逐项对应 |
| 8 | 边界一句话、作业与交接 | 验收范围和第 4 课起点 |
| **95** | **合计** | **另留 5 分钟缓冲，无课内小测** |

前置只需类型注解、类属性、列表／字典和 JSON 结构。数据访问不从零搭建；首次试讲记录 25 分钟任务的完成情况，超时先压缩工具面板与参考层解释，不削减正常示例和学生实践。

### 教师提供与学生负责

| 提供物 | 标注 | 学生要求 |
|---|---|---|
| 参数化查询／插入骨架、显式字段映射、`lastrowid` | 要求解释 | 说清占位符与值的对应关系，按模型字段改写并接入端点 |
| 连接获取与关闭、SQLite 建库与数据升级 | 要求会用 | 按约定获取和关闭，不实现数据库设施；第 4 课才收进依赖 |
| 服务层提交、回滚与已知标题冲突模板 | 本课要求会用，第 4 课升级为要求解释 | 知道调用成功意味着提交已返回，不移动提交位置，不从零设计事务模板 |
| Query、输入／输出模型、端点接线 | 要求解释 | 能修改声明、构造边界输入并说明状态码与字段 |
| 故障对照开关、回归脚本 | 黑盒 | 使用并核对结果，不编写实验工具 |

本课继续使用 SQLite，不引入 PostgreSQL、SQLAlchemy、ORM、用户表、作者关联、回答接口或 PATCH。标题、正文与标签是本课最小创建输入；标签暂由教师模板存为 JSON 文本，第 6 课再建立规范化关联表，不提前要求学生实现多表写入。

## 一、开场：读取页不变，新增一次正常创建

**课堂 5 分钟。先回归 `react` 得一条、无匹配词得空列表。**

教师说明：
> 上节课，你会判断接口返回了什么。这节课，我们声明接口允许收到什么，再让它保存一条新问题。

### 1.1 保持的公开契约

- `GET /questions` 继续接收 keyword/page/page_size，默认值分别为空字符串、1、20；page 为整数且至少为 1，page_size 为整数且在 1–50 范围内。
- 搜索先去掉关键词首尾空白，在标题或正文中做字面子串匹配；样本英文字母不区分大小写，`%`、`_` 不作通配符。按 id 降序后分页，total 是分页前的匹配总数。
- 列表外壳继续是 `items/total/page`，不是本课才迁移到这个容器。
- 详情仍为 `GET /questions/{qid}`。保留 `qid: int`，本课不新增正数限制：不存在的整数 id，包括 0 和负数，返回业务 404；不能解析成整数的路径参数返回框架 422。
- `/healthz` 仍为 200、`{"status":"ok"}`，不访问数据库。统一错误体、request-id 与数据库可用性检查均在第 4 课引入。

### 1.2 本课明确新增的字段与操作

所有问题记录保留 id/title/body，**增加 tags 与 created_at**。列表、详情和创建成功都使用同一记录形状；本课不删除列表正文，不增加作者展示。第 2 课页面只消费既有字段，因此读取与渲染代码可以继续工作；若主动展示新字段，仍使用安全文本输出。

教师在独立教学库中为原有三条记录补 `tags=[]` 与固定、带时区的 created_at，保留原 id/title/body。学生不重建或覆盖自己的数据来完成接口任务。

新增 `POST /questions`：按输入模型创建，成功返回 201、记录正文以及指向详情的 Location。先用正常输入完成一次创建，再测非法输入。

## 二、必要铺垫：参数从哪里来，模型约束谁

**课堂 15 分钟。把输入声明画在“路由匹配之后、端点调用之前”，输出模型画在“端点返回之后、响应发送之前”。**

### 2.1 三类参数位置

| 来源 | 声明形状 | 例子与意义 |
|---|---|---|
| 路径 | `qid: int` 与 `/questions/{qid}` 对应 | 选择某一条问题；非法整数在函数调用前拒绝 |
| 查询串 | `page: int = Query(1, ge=1)` | 读取方式及条件；默认值和范围写进声明 |
| JSON 正文 | `payload: QuestionCreate` | 一组创建字段，由 Pydantic 模型描述 |

本课使用上述明确写法，不讲完整参数推断算法。不要把所有外部输入都说成字符串：查询串经解析得到参数，而 JSON 本身就有字符串、数字、数组和 null 等类型。

类型注解在普通 Python 调用中不自动拦截值；这里是 FastAPI 读取声明并执行校验。直接在 Python 里调用函数，不等同经过一次 HTTP 请求。

### 2.2 给定字段契约：先判断，再写模型

以下是本课固定验收规格，学生不自行改变范围。它也作为随后教师《契约与迁移交接表》的录入依据，不要求本轮另建一份文档。

| 字段 | 创建输入 | 成功输出 | 规则 |
|---|---|---|---|
| title | 必填 | 必有 | 字符串，先去首尾空白，最终长度 5–200 |
| body | 必填 | 必有 | 字符串，先去首尾空白，最终长度 10–20000 |
| tags | 可省，默认空列表 | 必有 | 最多 5 个字符串；本课不额外约束单项长度、排序或去重，原样保存 |
| id | 不允许客户端填写 | 必有 | 数据库生成的整数 |
| created_at | 不允许客户端填写 | 必有 | 服务端生成的 UTC 时间，JSON 中为带时区的时间字符串 |

- 长度按清洗后的字符串字符数计，不是 UTF-8 字节数。title/body 的 null、缺失及错误类型不会被强行转成字符串。
- 创建拒绝其他字段，包括客户端提交的 id、created_at、author_id。拒绝额外字段是输入契约，不是认证或权限检查。
- 教师库对清洗后的 title 有唯一约束；当前按 SQLite 的精确文本比较，大小写不同不自动视为同一标题。已知重复标题返回 409，不把所有数据库异常都叫重复。
- 本课输出字段是 id/title/body/tags/created_at，没有 author、version 或内部维护字段。结构正确仍可能取错记录，需要核对业务结果。

保留 tags 是为了后续表单有标题、正文、标签三类输入；当前只解释字符串列表与数量限制，不把标签关系建模塞进本课。

### 2.3 输入与输出的职责

`QuestionCreate` 回答“调用者可提交什么”，`QuestionOut` 回答“服务承诺返回什么”。它们不是把同一个模型换两个名字：客户端不生成 id 和时间，而服务端必须给出它们。

教师先让学生按字段表分类，再看参考。第三单元的正常列表演示使用教师预置读模型；第四单元由学生完成创建模型和输出字段核对，最终列表／详情／创建共用同一个 `QuestionOut`，不要求维护多份相同输出模型。

## 三、教师构建列表：声明、绑定、返回三件事

**课堂 20 分钟。约 5 分钟看 Query 与输出模型，8 分钟逐行说明查询绑定，4 分钟接入端点，3 分钟核对返回数据。**

### 3.1 输出模型与通用导入

下列代码分段构成最终参考；app、同源静态页和 `open_connection()` 来自教师起点包。改造时替换旧列表／详情声明，不把相同方法和路径的第二个端点追加在旧路由后，也不重新创建 app 丢掉页面挂载。

```python
import json
import sqlite3
from contextlib import closing
from datetime import datetime, timezone

from fastapi import HTTPException, Query, Response
from pydantic import BaseModel, ConfigDict, Field, field_validator


class QuestionOut(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: int
    title: str
    body: str
    tags: list[str]
    created_at: datetime


class QuestionListOut(BaseModel):
    items: list[QuestionOut]
    total: int = Field(ge=0)
    page: int = Field(ge=1)
```

输出明确忽略模型未声明的额外字段，声明的必填字段则必须存在。时间由框架序列化为字符串，验收比较时间含义，不把 `Z` 与 `+00:00` 的等价表示当作业务差异。

### 3.2 数据模块展开成可读骨架

第 2 课的模块自己处理连接；教师在本课提供显式接收 conn 的查询与插入骨架，便于学生看清绑定关系。这是内部调用接口的展开，不改变公开搜索行为。

教师包约定：

- 使用 Python 标准库 sqlite3；`open_connection()` 每次返回连接，设置 `row_factory=sqlite3.Row`，启用非自动提交的写入事务模式。
- questions 表包含 `id INTEGER PRIMARY KEY`、唯一且非空的 title、非空 body、tags_json 和 created_at；tags_json 由 Python JSON 编解码，不依赖学生编写 SQLite JSON 扩展查询。
- 保留旧记录，填入合法 JSON 数组和带时区时间。建库、升级和 seed 为教师提供项。
- 端点用 `closing(...)` 关闭连接。sqlite3 连接自己的 `with` 管理事务，不等于自动关闭连接；这里由教师封装和演示，不展开底层实现。

先看显式行映射：

```python
def row_to_question(row):
    return {
        "id": row["id"],
        "title": row["title"],
        "body": row["body"],
        "tags": json.loads(row["tags_json"]),
        "created_at": row["created_at"],
    }
```

列名、输出字段名与转换关系写明，不把数据库行对象直接当作最终 JSON。tags_json 是存储字段，不出现在 API 输出中。

```python
def search_questions(conn, keyword, page, page_size):
    params = {
        "keyword": keyword.strip(),
        "limit": page_size,
        "offset": (page - 1) * page_size,
    }
    rows = conn.execute("""
        SELECT id, title, body, tags_json, created_at
        FROM questions
        WHERE instr(lower(title), lower(:keyword)) > 0
           OR instr(lower(body), lower(:keyword)) > 0
        ORDER BY id DESC
        LIMIT :limit OFFSET :offset
    """, params).fetchall()
    total = conn.execute("""
        SELECT count(*) FROM questions
        WHERE instr(lower(title), lower(:keyword)) > 0
           OR instr(lower(body), lower(:keyword)) > 0
    """, {"keyword": params["keyword"]}).fetchone()[0]
    return {
        "items": [row_to_question(row) for row in rows],
        "total": total,
        "page": page,
    }
```

课堂逐行说清：

1. `:keyword` 对应参数字典的 keyword；值没有拼进 SQL 结构。关键词里有引号，也仍然是一个待查询的值。
2. limit 是当前页条数上限，offset 按给定页码计算；count 使用相同筛选条件，但不带分页。
3. `instr` 做字面子串查找，`%`、`_` 没有通配符含义；SQLite 内置 lower 对本课英文字母样本适用，不承诺完成任意 Unicode 语言的大小写折叠。
4. 当前按固定数据和 id 降序验收；不把两次查询说成自动共享并发一致快照。并发分页与其他搜索能力不在本课扩展。

SQL 深层执行原理第 6 课讲，本课必须能解释占位符绑定和返回字段，不能仅说“这是老师给的黑盒”。

### 3.3 把声明接到查询

```python
@app.get("/questions", response_model=QuestionListOut)
def list_questions(
    keyword: str = Query(""),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=50),
):
    print("进入列表端点", page, page_size)
    with closing(open_connection()) as conn:
        return search_questions(conn, keyword, page, page_size)
```

正常请求先验证：空关键词为三条；`react` 为 id 3；无匹配为 200 空列表；`page=2&page_size=2` 为 id 1，total=3。新增记录之后数量会变化，所以固定样本检查在创建前或独立复位库中运行。

此时先问学生 `page=0` 会在哪里停，不立即改代码。第五单元再用断点验证预测。

## 四、学生任务：正常创建，再构造边界输入

**课堂 25 分钟。建议 7 分钟完成模型与字段分类，8 分钟接入插入骨架和端点，6 分钟构造三组边界，4 分钟互相核对。**

### 4.1 学生真正决定什么

学生依据固定字段表完成 `QuestionCreate`、核对 `QuestionOut`，将 title/body/tags 显式映射到插入参数，构造三组触及边界的输入。可以选择代码组织与测试值，但不能自改长度、让调用者传 id 或把标签静默丢弃。

先创建一条普通问题，从返回的 Location 回读，确认 id、标题、正文与标签属于同一条记录。只有看到 201 而没有持久化证据，不算完成闭环。

### 4.2 输入模型参考：先清洗，再限制长度

以下完整实现用于教师核对和学生完成后的比较；起点包提供字段表、模型类壳及校验器提示，不把完整创建答案作为待填骨架。

```python
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

`"    x"` 清洗后只有一个字符，应该被拒绝。这里先运行 before 校验器，再按字符串类型和长度检查；不先按原长度放行再返回短字符串，也不用 `str(value)` 把错误类型悄悄变成输入。

`default_factory=list` 给省略的 tags 创建空列表；tags 的 max_length 限制列表元素个数，不是每个标签的字符数。输入中额外的字段由 forbid 拒绝；这不代表使用者已经被授权。

### 4.3 插入骨架与回读

教师给出 SQL 结构、JSON 编码及时间生成方式，学生补齐字段映射。接线后的参考如下：

```python
def insert_question(conn, payload):
    cursor = conn.execute("""
        INSERT INTO questions (title, body, tags_json, created_at)
        VALUES (:title, :body, :tags_json, :created_at)
    """, {
        "title": payload.title,
        "body": payload.body,
        "tags_json": json.dumps(payload.tags, ensure_ascii=False),
        "created_at": datetime.now(timezone.utc).isoformat(),
    })
    return cursor.lastrowid


def find_question(conn, qid):
    row = conn.execute("""
        SELECT id, title, body, tags_json, created_at
        FROM questions WHERE id = :qid
    """, {"qid": qid}).fetchone()
    return None if row is None else row_to_question(row)
```

`lastrowid` 来自这次 INSERT 使用的游标，不用 `SELECT max(id)` 猜新记录编号。这里是 sqlite3 的写法，迁到 PostgreSQL 时教师会换成相应的 RETURNING，不让学生机械照搬驱动 API。

### 4.4 教师服务模板：先完成提交，再返回成功

本段是预置模板，本课会用，第 4 课再逐行解释事务与异常职责。学生不把 commit 移到数据访问函数、端点返回之后或未来依赖的退出代码里。

```python
class DuplicateTitle(Exception):
    pass


def create_question_service(conn, payload):
    try:
        qid = insert_question(conn, payload)
        result = QuestionOut.model_validate(find_question(conn, qid))
        conn.commit()
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

限定条件：教师单表基线**唯一的 UNIQUE 约束是 questions.title**，并核验当前驱动的扩展错误码；只有该已知冲突映射为 DuplicateTitle。添加其他唯一约束后必须同步分类，不能继续把任意唯一冲突都解释为标题重复。其他数据库错误仍按服务器失败处理。

服务层先验证可返回的记录，再显式提交。这个模板不等于“所有 500 都没有写入”；提交确认后仍可能在后续处理失败，第 4 课会用固定故障开关说明。当前不让学生设计重试或模拟提交期间断网。

### 4.5 创建与详情的 HTTP 接线

```python
@app.post("/questions", status_code=201, response_model=QuestionOut,
          responses={409: {"description": "标题已存在"}})
def create_question(payload: QuestionCreate, response: Response):
    print("进入创建端点")
    try:
        with closing(open_connection()) as conn:
            result = create_question_service(conn, payload)
    except DuplicateTitle as exc:
        raise HTTPException(status_code=409, detail="标题已存在") from exc
    response.headers["Location"] = f"/questions/{result.id}"
    return result


@app.get("/questions/{qid}", response_model=QuestionOut,
         responses={404: {"description": "问题不存在"}})
def get_question(qid: int):
    with closing(open_connection()) as conn:
        result = find_question(conn, qid)
    if result is None:
        raise HTTPException(status_code=404, detail="问题不存在")
    return result
```

端点做 HTTP 翻译，服务层提交，数据访问函数只读写。详情接线作为教师参考与课后回归，不增加第二个独立现场大任务。

`response.headers` 是在注入的 Response 上补头，最终仍返回模型／普通数据；这不同于直接返回一个 JSONResponse，后者会绕过常规输出模型处理。

### 4.6 三组边界：输入、预期、依据一起写

下面是教师验收口径。学生可以换成相同边界的自选值；涉及合法创建时用不同标题或独立复位库，避免把重复标题 409 当成长度校验失败。

| 组 | 输入构造 | 预期与解释 |
|---|---|---|
| 刚好合法 | title 长 5、body 长 10、tags 恰 5 项；另核对 title=200、body=20000 的上界 | 201，输出与清洗后输入一致；省略 tags 则输出空列表 |
| 刚好越界 | 分别只改一个字段：title 为 4／201，body 为 9／20001，tags 为 6 项 | 422，loc 指向相应 body 字段，端点未进入，不新增记录 |
| 空白与首尾空格 | 合法 title/body 外包空白；纯空白 title 或 body；`"    x"` | 外包空白后仍合法则 201 并保存清洗后的值；清洗后不足下限则 422 |

25 分钟内每组先完成一个代表请求，余下组合由教师回归器帮助课后核对。仍需理解三组为何不同，不以堆截图数量计分。

## 五、机制回收：拒绝输入与校验输出不是同一件事

**课堂 12 分钟。先回收 `page=0` 的预测，再做固定输出模型的两组对照。**

### 5.1 输入为什么没进入端点

IDE 在列表或创建函数第一行停点，关闭 reload，按一次请求观察。先发合法请求证明断点有效，再发 `page=0`：响应为 422，列表第一行不执行。

在响应 detail 中找：

- `loc`：位置与字段路径，例如 `["query", "page"]` 或 `["body", "title"]`。
- `type`：错误分类；`msg`：说明文案，不用整句英文相等来写测试。
- 可能存在 `input` 等信息：教学只用虚构数据，不在请求里放真实秘密。第 4 课再做安全的错误正文投影。

创建的非法输入同理。坏 JSON 语法在当前 FastAPI 自动请求解析路径下也是 422，不先承诺必然为 400。手工调用模型的 `model_validate` 抛的是 Pydantic ValidationError，不会脱离 HTTP 上下文自动变成 422。

“端点未进入”不等于整个应用没有执行代码：中间件与部分依赖可能已运行。当前端点内才获取连接，因此这些输入校验失败不会执行本端点的插入路径；这不是对所有应用副作用的通用保证。

### 5.2 输出模型保持不变，只改变返回数据

教师提供隔离只读实验，沿用本课 `QuestionOut`。不删除共享数据库字段，不对创建接口注入故障来混淆提交结果；实验路径不是新的必交业务接口。

```python
from fastapi import FastAPI
from fastapi.responses import JSONResponse


def make_output_probe(mode):
    lab = FastAPI(debug=False)

    @lab.get("/probe", response_model=QuestionOut)
    def probe():
        result = {
            "id": 3, "title": "React 的 props 是什么？",
            "body": "想知道组件怎样接收数据。", "tags": [],
            "created_at": "2026-09-01T08:00:00+00:00",
        }
        if mode == "missing":
            result.pop("created_at")
        if mode in ("extra", "direct"):
            result["internal_note"] = "仅供教师隔离对照"
        if mode == "direct":
            return JSONResponse(content=result)
        return result

    return lab
```

先预测，再观察：

| 模式 | 固定模型下的结果 | 为什么 |
|---|---|---|
| normal | 200，包含五个公开字段 | 正常数据满足输出模型 |
| missing | 输出校验失败，HTTP 500 | 服务端缺少承诺的必填 created_at，不是客户端输入错误 |
| extra | 200，不出现 internal_note | 普通返回值按显式 extra=ignore 的输出模型处理 |
| direct | 200，internal_note 出现 | 直接 Response 绕过常规输出模型处理；仅作为边界对照 |

学生重点解释 missing 与 extra；direct 为教师短演示，不要求实现另一套业务返回路径。TestClient 默认可能把服务端异常抛给测试程序；要观察 500 响应使用 `raise_server_exceptions=False`，不是通过改业务代码吞掉异常来让测试继续。

## 六、OpenAPI：声明怎样变成可查的接口

**课堂 10 分钟。打开 `/openapi.json` 与 `/docs`，把声明、文档、实际请求逐项对照。**

### 6.1 本课核对清单

- 搜索参数名、默认值与 page/page_size 的范围。
- POST 的 Request Body 是否引用 QuestionCreate；title/body 必填、tags 可省且最多 5 项、额外字段策略是否与模型一致。`default_factory=list` 在当前版本不生成静态 `default: []` Schema；省略 tags 得空列表须另用真实请求核对，不把 UI 未显示默认值判为接口错误。
- 成功响应是否引用 QuestionOut／QuestionListOut，created_at 是否作为必填时间字段出现。
- 创建成功状态是否为 201；实际响应含 Location，沿它 GET 能回读同一记录。
- 默认输入校验的 422，以及我们显式登记的详情 404、标题重复 409。

文档 UI 根据 OpenAPI 渲染，不是另一套接口实现。函数里 raise 的所有错误、动态写入的响应头和业务副作用不会自动被完整推导；这里的 responses 只补充状态描述，**不等于已经登记了完整错误 Schema 或 Location 响应头 Schema**。实际行为仍须用请求核验，后续统一错误体时同步完整文档。

`/docs` 的外部资源如果在教室不可用，用本地 `/openapi.json` 与现有请求工具继续核对；不把 JSON 可读取说成文档 UI 已离线可用。教师包若提供离线 UI，须另行实际验收。

### 6.2 AI 解释核对

让 AI 解释一份真实 422 的 detail 层次，再用三组边界中的输入核对其说法。AI 正确时记录接受理由与验证证据，不要求一定找出错误；不增加“重新让 AI 生成全部工程”的任务。

OpenAPI 快照用于记录本次公开契约，不是代码一改就自动保护所有调用方。自动类型消费者与 CI 是后续课次，本课只运行教师提供的行为回归。

## 七、回收、验收与一个作业包

**课堂 8 分钟。先用一句话收束，再说明课后范围。**

> 输入模型约束调用者能交什么，输出模型约束普通返回值该长什么样；它们不替你选对记录、实现业务规则或完成授权。

### 常用写法卡 #3

| 写法 | 当前作用 | 边界 |
|---|---|---|
| `Query` 的默认值与范围 | 把读取参数约束交给框架 | 非法输入未进入该端点，不等于应用从未运行 |
| `QuestionCreate` + before 校验器 | 先清洗 title/body，再校验类型与长度 | 不能把错误类型强转为字符串来放行 |
| `response_model=QuestionOut` | 处理普通返回数据，过滤额外字段 | 缺必填字段会失败；直接 Response 可绕过 |
| SQL 占位符 + 参数字典 | 将输入作为值绑定 | 不用用户值拼 SQL，结构正确也可能映射错字段 |
| `lastrowid` | 取回本次插入编号 | 不用 max(id) 猜，不跨驱动照搬 |
| 调用创建服务后返回 201 + Location | 保存完成后给出结果与回读位置 | commit 由服务层显式执行，不放进清理阶段 |

### 7.1 功能与回归规格

| 验收项 | 预期 |
|---|---|
| 列表／搜索／分页 | 保持参数、筛选与排序规则；固定三条样本及第二页正确，空结果仍为 200 |
| 详情 | 五个公开字段；不存在整数 id 为 404、非整数路径为 422；未知路径仍为框架 404 |
| 创建 | title/body/tags 按契约接收；201 + Location；独立连接可回读同一 id、正文和标签 |
| 三组边界 | 刚好合法、刚好越界、空白与首尾空格；非法输入不新增记录 |
| 其他输入拒绝 | 缺必填字段、错误类型、tags 超量、客户端填写 id／created_at／author_id 均为 422 |
| 已知标题冲突 | 精确重复标题为 409、`{"detail":"标题已存在"}`，不增加第二条记录 |
| 输出机制 | 缺 created_at 为 500，多 internal_note 被过滤，理解直接 Response 的例外 |
| 探针与页面 | `/healthz` 仍为纯存活响应；第 2 课四态、正文显示、安全文本与恢复不退化 |

### 7.2 一次提交，不重复写报告

交一个作业包：

1. 列表／详情／创建三端点、模型与字段映射代码，保留 `/healthz` 和同源页面。
2. 三组边界输入、实际状态／字段定位、输入输出机制说明。正常创建的 Location 回读、标签与持久化核对可以复用同一组证据。
3. 本阶段 OpenAPI 契约快照与简短迁移说明：增加 tags/created_at 和 POST，读取参数、列表容器及原字段不变。
4. 一次 AI 解释核对记录及教师回归器结果；将模型、绑定与断点的理解写在上述材料旁，不另交多份独立报告。

不要求学生实现数据库升级器、故障工具或自动测试框架。更多边界组合可由教师脚本执行；模型声明、字段映射和结果解释仍需学生自己理解。

选做只在隔离副本中改变一项契约，例如标题上限或错误格式，比较取舍；主线仍按给定规则验收。不提前布置 PATCH、作者权限、路由内部属性或跨框架移植。

## 八、第 4 课交接：抽取资源与统一错误，提交位置不变

第 4 课起点是有真实持久化的 SQLite 三端点，不是只有内存实验，也不是已经迁到 ORM 的项目。

| 已有基础 | 第 4 课要做什么 | 不能悄悄改变什么 |
|---|---|---|
| 三处 `closing(open_connection())` | 收进 `yield` 依赖并传递同一连接 | 连接使用期间有效，最终正确关闭 |
| `create_question_service` 显式 commit | 讲清事务边界、失败回滚与调用顺序 | commit 仍在服务层，依赖只提供资源与清理 |
| HTTPException 404／409 与框架 422 | 业务异常经统一处理器翻译，迁移四字段错误体 | 已批准状态码与成功数据契约继续保留 |
| 端点内最小观察日志 | 引入 request-id 与结构化日志模板 | 不能声称第 3 课已完成中间件或全链路取证 |
| 纯存活 `/healthz` | 增加数据库可用性检查，故障返回 503 | 沿用 status 字段的正文结构，不回退到旧多字段探针 |
| 第 2 课四态页面 | 回归 HTTP 失败与恢复，按需适配新的错误提示 | 保留文本渲染、列表容器及既有字段 |

教师提供两种事务故障开关：SQL 已执行但 commit 调用前失败，以及 commit 已确认返回后失败；都在 HTTP 响应启动前触发。两者都可能返回 500，但持久化结果不同，必须用独立连接回读。该设施在第 4 课引入，不要求本课学生先实现，也不把它当作提交期间断网的模拟。

第 5 课继续复用 title/body/tags 的输入规则，完成 SSR 表单解析与失败回填。第 6 课迁往 PostgreSQL 并建立标签关联时，由教师提供从 tags_json 到关联表的明确迁移与去重规则，不能把存储变化伪装成“数据自动就有了”。

## 九、制作与验证状态

本稿参考代码依赖教师提供的 app、同源静态挂载、SQLite 建库／升级与 `open_connection()`；这些并未因重写底稿而自动成为仓库里的新工程。

- **本轮机制验证已完成**：复用 Python 3.12.12、FastAPI 0.141.1、Starlette 1.6.0、Pydantic 2.13.5、httpx 0.28.1，通过临时脚本提取本稿代码，组合隔离 SQLite 与 TestClient。239 项行为／Schema 断言通过：列表搜索与分页、路径及输入拒绝、6 组合法创建、清洗和标签、201 与 Location 独立连接回读、重复标题 409、特殊字符字面匹配及 SQL 注入样本、4 种输出模式、OpenAPI、连接失败 500、输出校验失败回滚与直接服务调用的 NOT NULL 分类；另 1 项课时断言确认 95 分钟教学、25 分钟学生任务及另留 5 分钟缓冲。
- **核验限制**：本轮 SQLite 使用隔离共享内存库和独立连接，证明事务提交可见性，不证明文件落盘、进程重启或数据升级。未启动真实服务器；TestClient 的 httpx 适配仍提示弃用，本轮未安装或升级依赖。临时核验脚本不是独立练习包或已交付的课程自检器。
- **试讲前必须补齐**：第 3 课独立起点包、固定种子与升级脚本、模型／插入任务骨架、服务模板、输出对照开关、锁定环境及回归器。
- **需要实际验收**：真实 HTTP、课堂 IDE 的合法／非法请求停点、页面新增字段后的回归、OpenAPI UI 与投影可读性；进程内测试不等于这些条件已完成。
- **首轮试讲重点**：字段划分与 before 校验是否理解、参数字典能否自己补齐、25 分钟创建任务是否需要额外提示。超时先减少参考层讲述，不把数据库设施开发转嫁给学生。
