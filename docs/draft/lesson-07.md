# 第 7 次课教学底稿（修订版）
## 可观察的 ORM、事务与迁移 ｜ 交付 M2

## 〇、备课定位与内容取舍

本课不把 SQLAlchemy 当作另一套 API 背诵。主线是：**换掉持久层实现，保持业务和 HTTP 契约；把隐式查询、提交和结构变更变成可核对的行为。** 第六课 SQL 是正确性基线，不是引入 ORM 后就要丢掉的旧写法。

原稿把三个反例、五条 ORM 翻译、三阶段性能实验、事务与复杂迁移都要求现场完成，含缓冲超过 100 分钟；反例还混入输出缺字段、失效请求和固定 SQL 条数。修订后只保留一个学生现场主任务：在**同一输出契约**下定位并修复 N+1。事务与迁移由教师展示完整闭环，代码和安全条件留在课件中供课后完成。

### 课堂路线：95 分钟教学 + 5 分钟缓冲

| 单元 | 分钟 | 课堂处理 |
|---|---:|---|
| 一、SQL 基线与替换边界 | 4 | 明确什么不能跟着 ORM 改 |
| 二、三个反例分开观察 | 7 | N+1 主演示；提交与排序先定位 |
| 三、对象、Session 与 Unit of Work | 10 | 看一条 UPDATE 何时出现 |
| 四、模型与 Session 依赖 | 13 | 主讲一个模型，完整五表课后读 |
| 五、同契约 N+1 实验 | 20 | 学生现场必做；10 分钟时核对计数边界 |
| 六、事务成功与失败 | 12 | 教师演示回滚、409 和提交失败 |
| 七、五条 SQL 翻译与加载选择 | 10 | 列表/计数主讲，其他导读 |
| 八、Alembic 最小安全闭环 | 14 | 空库基线与副本改名演示；复杂迁移自学 |
| 九、M2 验收与收尾 | 5 | 基础交付、扩展与验证边界 |
| 合计 | 95 | 另留 5 分钟缓冲 |

A 档包括课堂任务、教师演示后的复做与课后基础阅读；B 档包括全项目扫描、加载策略扩展、slug 上线等。超时将第四单元模型细节和第七单元翻译变体转课后，保留 N+1 同契约证据、失败不留半截数据以及一次保数据迁移。

### 输入基线与版本

- Python 3.12、SQLAlchemy 2.0、PostgreSQL 16+、psycopg；FastAPI 教学锁定版本须支持 `Depends(scope="function")`。不把其他版本的依赖退出时序套过来。
- 第六课五表 DDL、约束名称、已采用索引、小数据预期结果；若仍用 SQLite，先完成教师提供的 PostgreSQL 环境接入。
- 第五课三个核心 JSON 端点、HTML 页面与 `/healthz` 保留。列表参数 `keyword/page/page_size`，默认 20、上限 50；响应容器仍为 `items/total/page`。
- 不因为 ORM 方便就改为裸数组、改变字段名称、遗漏搜索条件或取消错误契约。实验额外字段放在独立 `/lab/orm/questions`，不得暗改生产接口。
- 第四课曾简化为“Connection 换 Session 只改依赖”，本课明确纠正：调用方法、返回类型、事务时机、错误翻译都可能要调整；分层的收益是限制影响范围，不是承诺只改一行。

文中模型与函数是完整机制参考或注明上下文的片段，独立演示工程、seed、迁移文件与 HTTP 验收仍需在制作阶段提供，不假定已有 `v7-*` tag。

## 一、为什么已经会 SQL，还要学 ORM

**课堂 4 分钟。**

第六课已经能描述合法结构并手算查询。ORM 提供对象—行映射、关系导航、状态跟踪和 SQL 构造；这些便利也会隐藏额外查询和写入。

讲：不是“原生 SQL 低级，ORM 高级”，而是选择可维护且可观察的表达方式。同一个项目可以组合 ORM、SQLAlchemy Core 和参数化 SQL。今天用第六课的结果与第五课的请求契约证明替换没有改变行为。

学生结束时应能回答：

1. 没写 UPDATE，为什么数据库还是更新了？
2. 属性访问或序列化能否发 SQL，计数应放在哪里？
3. `flush` 成功是否等于写入已经提交？
4. 提交失败时客户端会得到什么，数据库会留下什么？
5. autogenerate 比较谁与谁，为什么不能代替迁移审读？

## 二、解剖台：三个缺陷，三个隔离阶段

**课堂 7 分钟。** 不声称正常测试绝不可能发现问题，也不把“缺陷可能导致数据不一致”夸大成永远无法恢复。

### 2.1 N+1：先保证响应可构造

错误查询形态示意：先查一页 id，再循环 `session.get(Question, id)`，最后访问 author/answers。它可能造成额外查询；但要先确保输出字段都有来源。

```python
# 预期缺陷片段；只在独立实验函数使用。
ids = session.scalars(select(Question.id).limit(page_size)).all()
questions = [session.get(Question, qid) for qid in ids]
```

这不是主实验的起始版，因为同时混入了逐主键查询。第五单元使用一次主查询开始，单独观察关系加载。

`QuestionOut` 写一个 `answer_count: int` 并不会自动计算 `len(q.answers)`；模型没有该属性时，响应先校验失败，不能用它演示“页面正常但 N+1”。本课明确构造 DTO，标出每次关系访问。

多对一作者关系可能命中 Session 的 identity map。N 个问题并不一定发 N 条作者查询；取决于不同作者数及已加载对象。条数需要测量，不预定为 41。

### 2.2 半截提交：使用合法输入触发指定失败点

在隔离错误版中，先插入问题并 commit，再处理标签时人为抛异常。请求必须通过入口校验，不能用过短标题或缺正文让它先返回 422。

```bash
curl -i -X POST http://127.0.0.1:8000/questions \
  -H 'Content-Type: application/json' \
  -d '{"title":"事务回滚验证标题","body":"这是一段满足最小长度要求的正文。","tags":["python","sql"]}'
```

故障点由测试替身控制在“问题已经写入、第二个标签关联之前”，不是声称不存在的标签会触发未定义 CHECK。错误版观察到问题残留；修复版同一失败点后问题、标签关系和本次新建标签均不留下。

### 2.3 动态排序不是值参数

```python
# 不安全示意：用户输入成为 SQL 语法。
stmt = text(f"SELECT id FROM questions ORDER BY {sort} DESC")
```

参数绑定适合值，不适合把列名直接绑定成排序表达式。第七单元用白名单映射列对象修复；注入完整实验只在第十五课本地靶场进行。

课堂此处只指出三种验证手段：SQL 计数、失败后查库、排序白名单边界。它们都可以进入第九课测试，不必等上线才发现。

## 三、对象、Session、Unit of Work

**课堂 10 分钟。**

### 3.1 不写 UPDATE 也发生 UPDATE

```python
with SessionLocal.begin() as session:
    question = session.get(Question, 101)
    question.view_count += 1
    session.flush()
    # 观察这里出现 UPDATE；with 正常退出才提交。
```

Session 跟踪持久对象的变化，将需要写入的变更组织成一组数据库操作，这就是 Unit of Work 的核心。修改属性不是立即自动提交；flush 将变更发到当前事务，commit 才结束事务并尝试提交。

| 操作 | 作用 | 重要边界 |
|---|---|---|
| add | 把对象纳入 Session 管理 | 不一定立即 INSERT |
| flush | 发出待执行写入，获取生成的键等 | 可失败；成功也未提交 |
| commit | 必要时 flush，再提交事务 | 可在此阶段失败 |
| rollback | 回滚未提交事务 | 不能撤销之前已提交事务 |
| close | 释放 Session 资源 | 不替你提交未完成工作 |

ORM 查询等操作可能触发 autoflush；不要把它说成“任何查询之前必然 flush”。调试时从日志看实际时机。

### 3.2 identity map 不是全局查询缓存

一个 Session 内，同一数据库标识通常对应同一个对象：

```python
with SessionLocal() as session:
    first = session.get(Question, 101)
    second = session.get(Question, 101)
    assert first is second
```

第二次 get 在对象未过期且仍在映射中时可能不发 SQL；任意 SELECT 并不会因此自动免查询。新的 Session、对象过期或条件查询都会改变行为。

Session 是有状态的工作单元，不是并发安全的全局对象。同一请求中的并行任务也不能共享同一个 Session 同时操作；同步栈沿第五课用 `def`，不在异步端点中直接执行同步 ORM。

### 3.3 批量 UPDATE 与内存状态

`session.execute(update(...))` 的 ORM 同步策略可能更新或过期内存对象；不是永远不管 identity map。使用 Core、原生 SQL 或关闭同步时，应明确何时 refresh/expire，并核对对象与数据库状态。

完整状态机 transient/pending/persistent/detached/expired 为课后阅读，课堂只要求区分“对象在内存中”“SQL 已发出”“事务已提交”。

## 四、模型与依赖：保留第六课的规则

**课堂 13 分钟。** 主讲 Question 与 Answer，其他模型为完整参考。

### 4.1 引擎与连接预算

```python
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

engine = create_engine(
    settings.database_url,
    pool_size=5,
    max_overflow=10,
    pool_pre_ping=True,
    echo=settings.sql_echo,
)
SessionLocal = sessionmaker(bind=engine, expire_on_commit=False)
```

这是 PostgreSQL 教学配置起点，不是通用性能调优答案。pool_size 是池保留容量，不是启动时一定预开五条连接；pre_ping 可检查取出的陈旧连接，不保证事务执行中永不掉线。

多个实例/worker 的连接上限需要合并预算，并为迁移、后台任务与管理连接留余量。pool_recycle 是否需要取决于基础设施超时，不机械写一个固定秒数。进程退出时释放 engine，生命周期钩子中的同步清理也应避免阻塞事件循环。

`expire_on_commit=False` 是本参考实现的便利选择，不是所有 FastAPI 响应都必须设置；它不让未加载的关系自动可用。主线仍在 Session 可用时构造明确 DTO。

### 4.2 完整五表模型基线

下列模型对应第六课**最终 DDL**。先保留数据库列 `body`；第八单元改名时再同步映射。为避免误解 naming_convention 对显式 name 的处理，本参考直接使用稳定的完整约束名。

```python
from datetime import datetime
from sqlalchemy import (
    BigInteger, Boolean, CheckConstraint, Column, DateTime, ForeignKey,
    Integer, Table, Text, UniqueConstraint, func,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

class Base(DeclarativeBase):
    pass

question_tags = Table(
    "question_tags", Base.metadata,
    Column("question_id", BigInteger,
           ForeignKey("questions.id", ondelete="CASCADE",
                      name="question_tags_question_id_fkey"), primary_key=True),
    Column("tag_id", BigInteger,
           ForeignKey("tags.id", ondelete="CASCADE",
                      name="question_tags_tag_id_fkey"), primary_key=True),
)

class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    email: Mapped[str] = mapped_column(Text)
    display_name: Mapped[str] = mapped_column(Text)
    password_hash: Mapped[str] = mapped_column(Text)
    role: Mapped[str] = mapped_column(Text, server_default="member")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now())
    questions: Mapped[list["Question"]] = relationship(
        back_populates="author", passive_deletes="all")
    answers: Mapped[list["Answer"]] = relationship(
        back_populates="author", passive_deletes="all")
    __table_args__ = (
        UniqueConstraint("email", name="users_email_key"),
        CheckConstraint("role IN ('member','moderator','admin')", name="users_role_check"),
        CheckConstraint("char_length(display_name) BETWEEN 2 AND 40", name="users_name_len"),
    )

class Question(Base):
    __tablename__ = "questions"
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    title: Mapped[str] = mapped_column(Text)
    body: Mapped[str] = mapped_column(Text)
    author_id: Mapped[int] = mapped_column(BigInteger, ForeignKey(
        "users.id", ondelete="RESTRICT", name="questions_author_id_fkey"))
    status: Mapped[str] = mapped_column(Text, server_default="open")
    view_count: Mapped[int] = mapped_column(Integer, server_default="0")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now())
    author: Mapped["User"] = relationship(back_populates="questions")
    answers: Mapped[list["Answer"]] = relationship(
        back_populates="question", cascade="all, delete-orphan", passive_deletes=True)
    tags: Mapped[list["Tag"]] = relationship(
        secondary=question_tags, back_populates="questions", passive_deletes=True)
    __table_args__ = (
        UniqueConstraint("title", name="questions_title_key"),
        CheckConstraint("status IN ('open','closed','deleted')", name="questions_status_check"),
        CheckConstraint("char_length(title) BETWEEN 5 AND 200", name="questions_title_len"),
        CheckConstraint("char_length(body) BETWEEN 10 AND 20000", name="questions_body_len"),
        CheckConstraint("view_count >= 0", name="questions_views_nonneg"),
    )

class Answer(Base):
    __tablename__ = "answers"
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    question_id: Mapped[int] = mapped_column(BigInteger, ForeignKey(
        "questions.id", ondelete="CASCADE", name="answers_question_id_fkey"))
    author_id: Mapped[int | None] = mapped_column(BigInteger, ForeignKey(
        "users.id", ondelete="SET NULL", name="answers_author_id_fkey"))
    body: Mapped[str] = mapped_column(Text)
    is_accepted: Mapped[bool] = mapped_column(Boolean, server_default="false")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now())
    question: Mapped["Question"] = relationship(back_populates="answers")
    author: Mapped["User | None"] = relationship(back_populates="answers")
    __table_args__ = (
        CheckConstraint("char_length(body) BETWEEN 10 AND 10000", name="answers_body_len"),
    )

class Tag(Base):
    __tablename__ = "tags"
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    name: Mapped[str] = mapped_column(Text)
    questions: Mapped[list["Question"]] = relationship(
        secondary=question_tags, back_populates="tags", passive_deletes=True)
    __table_args__ = (UniqueConstraint("name", name="tags_name_key"),)
```

PostgreSQL 会为未显式命名的主键使用默认名称；需在基线审读时核对与第六课一致。索引只加入已经采用的方案，例如 `Index("idx_answers_question", Answer.question_id)`，不把第六课候选集未经评估全部塞入。已采用索引必须同时出现在 metadata 与迁移基线。

### 4.3 三个容易混淆的地方

- `Mapped[str]` 在没有显式覆盖 nullable 等设置时通常推导为非空；`Mapped[int | None]` 表达可空。显式列配置仍可改变推导结果。
- Python `default` 由 SQLAlchemy 在写入时提供；`server_default` 写进 DDL，其他写入路径也可使用。本课状态与时间默认值保留数据库端定义。
- 模型描述目标结构，迁移描述如何到达；autogenerate 不能覆盖触发器、所有约束或数据演进。模型不是所有数据库对象唯一且完整的真相来源。

采用 naming_convention 的项目要理解 token：`UniqueConstraint("title", name="title")` 不会在常见 uq 模板下自动变成 `uq_questions_title`。本课保留 `questions_title_key`，否则第六课结构化错误翻译也要同步调整。不要为了命名好看制造无意义 drop/create。

### 4.4 ORM cascade 与 ON DELETE

数据库 ON DELETE 约束直接 SQL 和其他客户端的删除；ORM cascade 决定 Session 对关联对象的操作。`passive_deletes` 可让未加载集合的删除更多交给数据库，不意味着所有状态下一定只发一条 SQL。

Question.answers 的 delete-orphan 表示从父集合移除回答会安排删除；需先确认业务允许。User 侧 `passive_deletes="all"` 让数据库执行 RESTRICT/SET NULL，不先由 ORM 把不可空作者设成 NULL。数据库级联后的已加载对象可能需要过期/刷新，不能假设内存总是自动同步。

### 4.5 请求依赖：在回应成功前结束事务

```python
from typing import Annotated, Iterator
from fastapi import Depends
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

def get_session() -> Iterator[Session]:
    try:
        with SessionLocal() as session:
            with session.begin():
                yield session
    except IntegrityError as exc:
        # 包含 flush 与 commit 失败；到这里已退出事务并回滚。
        constraint = getattr(getattr(exc.orig, "diag", None), "constraint_name", None)
        if constraint == "questions_title_key":
            raise DuplicateTitle() from exc
        raise

SessionDep = Annotated[Session, Depends(get_session, scope="function")]
```

所有实际使用这条事务边界的端点都用 SessionDep；不是只新增别名、旧 `Depends(get_session)` 原封不动。同步短请求是本课选择；流式响应、后台任务、长操作等需要自己的资源和事务边界。

## 五、现场必做：同契约 N+1 实验

**课堂 20 分钟。** 核心不是“SQL 条数越少越好”，而是定位不必要的往返，并确认优化没有改结果。

### 5.1 固定实验契约，不给生产端点偷偷加字段

独立路径 `/lab/orm/questions` 返回问题摘要、作者、回答数和标签；所有阶段字段相同。它不代替原有 `/questions`，M2 回归仍以原有契约为准。

```python
from pydantic import BaseModel

class LabAuthorOut(BaseModel):
    id: int
    display_name: str

class LabQuestionOut(BaseModel):
    id: int
    title: str
    created_at: datetime
    author: LabAuthorOut
    answer_count: int
    tags: list[str]

class LabListOut(BaseModel):
    items: list[LabQuestionOut]
    total: int
    page: int

def to_lab_dto(question, answer_count=None):
    return LabQuestionOut(
        id=question.id, title=question.title, created_at=question.created_at,
        author=LabAuthorOut(id=question.author.id,
                            display_name=question.author.display_name),
        answer_count=(len(question.answers) if answer_count is None else answer_count),
        tags=sorted(tag.name for tag in question.tags),
    )
```

这里明确标出 author、answers、tags 三处属性读取。`from_attributes=True` 也可能在读取关系时触发加载，但不会替你凭空计算 answer_count。不要用 `**q.__dict__` 映射 DTO，那里可能含 ORM 内部状态、过期或缺失字段。

### 5.2 三个策略，共用查询与 DTO

```python
from sqlalchemy import select
from sqlalchemy.orm import selectinload

def read_lab_page(session, page, page_size, strategy):
    base = (
        select(Question)
        .where(Question.status == "open")
        .order_by(Question.created_at.desc(), Question.id.desc())
        .offset((page - 1) * page_size).limit(page_size)
    )
    total = session.scalar(
        select(func.count()).select_from(Question).where(Question.status == "open")
    )
    if strategy == "lazy":
        questions = session.scalars(base).all()
        items = [to_lab_dto(q) for q in questions]
    elif strategy == "selectin":
        stmt = base.options(
            selectinload(Question.author), selectinload(Question.answers),
            selectinload(Question.tags),
        )
        items = [to_lab_dto(q) for q in session.scalars(stmt).all()]
    elif strategy == "aggregate":
        count_expr = (
            select(func.count(Answer.id)).where(Answer.question_id == Question.id)
            .correlate(Question).scalar_subquery().label("answer_count")
        )
        stmt = base.add_columns(count_expr).options(
            selectinload(Question.author), selectinload(Question.tags),
        )
        items = [to_lab_dto(q, n) for q, n in session.execute(stmt).all()]
    else:
        raise ValueError("未知实验策略")
    return LabListOut(items=items, total=total, page=page)
```

使用同一受控数据、不并发写入，三种策略的响应应相同。第三阶段只需回答数，不再加载完整回答正文；它是这个输出需求下的候选优化，不是所有 selectinload 都只是“止血”。如果页面确实需要回答集合，聚合不能替代它。

```python
from typing import Literal
from fastapi import Query

@router.get("/lab/orm/questions", response_model=LabListOut)
def lab_questions(
    session: SessionDep,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=50),
    strategy: Literal["lazy", "selectin", "aggregate"] = "lazy",
):
    return read_lab_page(session, page, page_size, strategy)
```

实验路径仅在本地注册。基础任务测 lazy 与 selectin；aggregate 教师导读或课后复做。

### 5.3 数的是执行次数，不是日志行数

```python
from contextlib import contextmanager
from sqlalchemy import event

@contextmanager
def count_sql(engine):
    stats = {"executions": 0, "statements": []}
    def before(conn, cursor, statement, parameters, context, executemany):
        stats["executions"] += 1
        stats["statements"].append(statement)
    event.listen(engine, "before_cursor_execute", before)
    try:
        yield stats
    finally:
        event.remove(engine, "before_cursor_execute", before)
```

计数必须和被测 engine 在**同一进程**。外部 curl/httpx 脚本不能靠监听本进程 engine 数到另一个服务进程的 SQL。参考使用进程内 TestClient：

```python
from fastapi.testclient import TestClient
from time import perf_counter

with TestClient(app) as client:
    with count_sql(engine) as stats:
        started = perf_counter()
        response = client.get(
            "/lab/orm/questions", params={"page_size": 20, "strategy": "lazy"})
        elapsed_ms = (perf_counter() - started) * 1000
    assert response.status_code == 200
    result = response.json()
```

监听范围覆盖请求、DTO 构造、FastAPI 序列化及函数依赖退出；不只包住 repository 查询。测试应用使用专用 engine，禁用后台并发访问；初始化、seed、DDL 和预热放在计数外。

`before_cursor_execute` 统计执行事件，不直接统计返回行数、网络字节或一次 executemany 的写入行数。事务命令/驱动探针是否经过该事件也要按实际记录说明。SQL echo 适合解释语句，不用 grep 日志总行数代替精确计数。

### 5.4 条数推导有前提

每轮新 Session；无已有关系缓存；当前页有 N>0 个问题，引用 U 位不同作者；每次 selectin 在一批内：

| 策略 | 示例推导（包含 total） | 读取的内容 |
|---|---|---|
| lazy | `2 + U + N + N` | 总数、问题、作者、各问题回答与标签 |
| selectin | 通常 `2 + 3` | 总数、问题、三类批量关系 |
| aggregate | 通常 `2 + 2` | 总数、带回答数的问题、作者与标签 |

这些不是硬编码验收值。空页、selectin 分批、不同加载状态或额外序列化读取都会改变条数；先分类语句再解释。共同作者会减少 lazy 的作者查询，不能固定写 N 条。

基础先使用第六课小数据，然后由独立 seed 扩展到足够的 20/50 条，重复作者、零回答和多标签都要保留。页大小不超过约定的 50，不要求用被校验器拒绝的 100。

| 数据/页大小 | 策略 | 响应是否相同 | SQL 执行次数及分类 | 多轮耗时 |
|---|---|---|---|---|
| 待记录 | lazy/selectin/aggregate | 待断言 | 待测 | 待测 |

耗时测试与大量 echo 输出分开：日志 I/O 本身会影响结果。若模拟每次执行额外等待 1ms，预期增加约“执行次数 × 1ms”，不能把 41 条额外 41ms 说成凭空增加几百毫秒；模拟不等于真实远程数据库基准。

## 六、事务：成功可确认，失败不留半截

**课堂 12 分钟。**

### 6.1 一个短写请求的边界

```text
进入函数作用域依赖 → Session/事务
  → schema 与业务处理 → flush/查询 → 构造 DTO 或 303
  → 依赖退出：提交成功 → 发送成功响应
               提交失败 → 回滚/释放 → 异常处理 → 错误响应
```

端点返回 Response 对象不等于响应已经发出。默认 request scope 的 yield 退出可能在发送后，不能用它承担“提交成功才宣告成功”的承诺。本稿统一使用第四单元的函数作用域依赖。

一请求一事务是本课程短业务操作的选择，不是所有系统的普遍真理。事务不要包住长时间外部 HTTP 等待；流式输出、后台任务和跨资源一致性需另行设计。

### 6.2 创建与标签：不在中途 commit

```python
# service 参考：payload 为第五课共享的 QuestionCreate。
def create_question(session, payload, author_id):
    question = Question(title=payload.title, body=payload.body, author_id=author_id)
    session.add(question)
    for name in dict.fromkeys(payload.tags):
        question.tags.append(get_or_create_tag(session, name))
    session.flush()
    return question
```

flush 获取 id 或提早暴露约束错误；它不是提交。这里不吞 IntegrityError，让它穿过第四单元的事务依赖，完成回滚后按 `questions_title_key` 翻译 DuplicateTitle。

JSON 端点在 Session 内构造现有 QuestionOut，成功 201；HTML 端点保存 `request.state.form_values`，成功准备 303。DuplicateTitle 的表现层沿用第五课：JSON 409 或 HTML 409 回填。不要在 HTML 路由捕获数据库失败后正常 return，让已失败的 Session 再走成功提交路径。

### 6.3 标签创建的并发边界（课后基础参考）

“查不到就插入”也可能竞争。PostgreSQL 参考实现使用命名唯一约束配合 ON CONFLICT：

```python
from sqlalchemy.dialects.postgresql import insert

def get_or_create_tag(session, name):
    statement = (
        insert(Tag).values(name=name)
        .on_conflict_do_nothing(constraint="tags_name_key")
        .returning(Tag.id)
    )
    tag_id = session.scalar(statement)
    if tag_id is None:
        tag_id = session.scalar(select(Tag.id).where(Tag.name == name))
    if tag_id is None:
        raise RuntimeError("标签并发状态已变化，请重试整个操作")
    return session.get(Tag, tag_id)
```

此参考依赖 PostgreSQL READ COMMITTED 的后续语句可见性，且本课没有并发删除标签的功能。更复杂隔离级别、删除竞争和失败重试要另作设计；不能把它当所有场景的通用 get_or_create。新标签与问题仍在同一事务中。

### 6.4 必须验证的四类失败

| 场景 | 客户端期望 | 数据库期望 |
|---|---|---|
| 输入不合法 | JSON/HTML 422 | 无业务新增 |
| 重复标题 | JSON/HTML 409，HTML 保留输入 | 仍只有原问题，无新关联 |
| 问题 flush 后标签处理抛异常 | 500，不暴露内部细节 | 本次问题、关联及新标签全部回滚 |
| commit 故障 | 不得出现 201/303 | 测试中的未提交事务回滚 |

最后一项在隔离测试中替换 Session 的提交行为，或用 PostgreSQL 延迟约束场景；不要为课堂随机断生产网络。先验证正常提交，再验证 flush 与 commit 两种失败位置，HTTP 和数据两头都断言。

实际网络在提交时断开可能导致“提交结果未知”，不能一概声称所有提交错误都证明数据库没提交；这类场景需要幂等键/查询确认等设计，第八课继续讨论。

### 6.5 DetachedInstanceError 的准确演示（自学）

```python
ExpiringSession = sessionmaker(bind=engine, expire_on_commit=True)
session = ExpiringSession()
question = session.get(Question, 101)
session.commit()
session.close()
print(question.title)  # 已过期且脱离 Session，触发 DetachedInstanceError。
```

演示必须有 commit 导致过期、close 导致脱离，再访问属性；不编造错误的 FastAPI 序列化顺序。主线用显式 DTO，减少响应生成对 Session 生命周期的依赖。即使 expire_on_commit=False，未加载关系在关闭后仍可能访问失败。

## 七、SQL 对照与加载策略：按需求选择

**课堂 10 分钟；五条完整对照为课后基础阅读。** 下列编号与第六课对应，不要求所有 SQL 都改成 ORM。

### 7.1 Q1：稳定分页

```python
stmt = (
    select(Question).options(selectinload(Question.author))
    .where(Question.status == "open")
    .order_by(Question.created_at.desc(), Question.id.desc())
    .offset((page - 1) * page_size).limit(page_size)
)
questions = session.scalars(stmt).all()
```

total 另用相同过滤条件计数；keyword 非空时两条查询都应用同样的搜索条件。输出仍适配既有 `items/total/page`，不返回裸 ORM 对象列表代替契约。

### 7.2 Q3：回复数，不是全部回复

第五单元 aggregate 展示相关子查询，这里给出预聚合 JOIN 版本作为对照：

```python
counts = (
    select(Answer.question_id, func.count(Answer.id).label("n"))
    .group_by(Answer.question_id).subquery()
)
stmt = (
    select(Question, func.coalesce(counts.c.n, 0).label("answer_count"))
    .outerjoin(counts, counts.c.question_id == Question.id)
    .where(Question.status == "open")
    .order_by(Question.created_at.desc(), Question.id.desc())
    .offset((page - 1) * page_size).limit(page_size)
)
rows = session.execute(stmt).all()
```

返回 `(Question, count)` 行，不是纯 Question。DTO 构造时显式拆开；如还需作者、标签，要显式添加相应加载选项。相关子查询、预聚合和原 Q3 的 GROUP BY 都可正确，性能由数据与计划判断。

### 7.3 Q4：标签 AND

```python
names = list(dict.fromkeys(tag_names))
stmt = select(Question).where(Question.status == "open")
if names:
    matching = (
        select(question_tags.c.question_id)
        .join(Tag, Tag.id == question_tags.c.tag_id)
        .where(Tag.name.in_(names))
        .group_by(question_tags.c.question_id)
        .having(func.count(func.distinct(Tag.id)) == len(names))
    )
    stmt = stmt.where(Question.id.in_(matching))
stmt = stmt.order_by(Question.created_at.desc(), Question.id.desc())
```

空列表不筛选；不同标签去重后再比较数量。对照第六课两标签数据，预期 id=101。关系 `.any()` 也是可选表达，但不能不比较结果就替换。

### 7.4 Q5：贡献排行

```python
answer_count = func.count(Answer.id).label("answer_count")
accepted_count = func.count(Answer.id).filter(Answer.is_accepted).label("accepted_count")
stmt = (
    select(User.id, User.display_name, answer_count, accepted_count)
    .outerjoin(Answer, Answer.author_id == User.id)
    .group_by(User.id, User.display_name)
    .order_by(accepted_count.desc(), answer_count.desc(), User.id)
    .limit(page_size)
)
```

输出是投影行，用显式 schema/字典转换，不强行映射为 User。已采纳优先、回答数其次、id 决胜，必须与原 SQL 口径一致。

### 7.5 Q6：字面搜索与排序白名单

```python
from sqlalchemy import or_

pattern = literal_pattern(keyword)  # 第六课的 ! / % / _ 转义函数。
stmt = select(Question).where(Question.status == "open")
if keyword:
    stmt = stmt.where(or_(
        Question.title.ilike(pattern, escape="!"),
        Question.body.ilike(pattern, escape="!"),
    ))
stmt = stmt.order_by(Question.created_at.desc(), Question.id.desc())
stmt = stmt.offset((page - 1) * page_size).limit(page_size)
```

表达式 API 为值生成绑定参数；仍需转义 LIKE 通配符才能保留字面搜索语义。动态排序则映射受控表达式：

```python
SORTS = {"created_at": Question.created_at, "title": Question.title,
         "view_count": Question.view_count}
# 对外参数用 Literal/枚举约束；无效输入返回既有 422 契约。
stmt = stmt.order_by(None).order_by(SORTS[sort].desc(), Question.id.desc())
```

本片段只有在 sort 已验证时使用，不能任意 getattr；不把用户字符串交给 text。第八课再将允许的排序字段固化进正式 API 契约。

### 7.6 lazy / selectin / joined 的边界

| 策略 | 可考虑的场景 | 需要验证 |
|---|---|---|
| lazy | 单对象偶尔访问关系 | 循环、DTO/序列化是否触发额外查询 |
| selectinload | 批量父对象的集合关系 | 分批次数、IN 参数规模与子对象总量 |
| joinedload | 多对一或规模受控的关系 | 列重复、集合行数膨胀与去重 |
| 聚合/投影 | 只需计数、摘要或少量列 | 语义、输出字段、查询计划 |

```python
from sqlalchemy.orm import joinedload

stmt = select(Question).options(joinedload(Question.answers)).limit(20)
questions = session.execute(stmt).unique().scalars().all()
```

SQLAlchemy 2.x 对 joinedload 集合要求 `.unique()`；缺失时通常抛错，不是必然把 20 个问题返回成上千个对象。带 LIMIT 的主查询可由 ORM 包装子查询后再 JOIN，不应简单说 joinedload 必然分页错误。数据库传输行数仍可能膨胀，需要独立测量。

`raiseload("*")` 可在测试里帮助发现未声明的关系访问，但不是所有 N+1 的禁令：它不禁止显式循环查询，flush 内部也可能需要加载。详情页“需要回答”仍应考虑分页或数量上限。

### 7.7 什么时候用 Core 或 text

窗口函数、复杂报表、数据库专用语法或更清晰的固定 SQL 都可能适合 Core/text。受信 SQL 模板加绑定值并不因为用了 text 就不安全；真正危险的是把不可信输入拼成语法。

作业只需说明一次选择及其依据，不强制找一个“必须放弃 ORM”的例子。两种实现的结果与成本可比较，但不是所有学生都要写双份代码。

## 八、Alembic：先有正确基线，再谈演进

**课堂 14 分钟；完整说明留课后。** 本单元所有操作只在可丢弃数据库或已备份副本，不对学生唯一一份数据演示 downgrade。

### 8.1 autogenerate 比较的是现库与 metadata

```text
当前连接数据库的结构  ← 比较 →  已导入的 Base.metadata
                       ↓
                  候选迁移脚本
```

如果现库已经有五张表，再生成 init，可能得到空迁移；这不能让新环境从空库重建。反过来，漏导入模型或连接错库也可能生成大量危险差异。

本课选择：**001_baseline 就是第六课最终结构；002_body_content 只做问题正文数据库列改名。** 不再在该链后面重复添加已经存在的 status 约束。之前做过的清洗保存历史记录，不伪造为“迁移又重新记录了当时执行”。

### 8.2 环境接线与检查

独立工程初始化 Alembic 后，在 env.py 导入全部模型再设置 `target_metadata = Base.metadata`。在线迁移可直接从专用配置创建 engine，避免把包含 `%` 的 URL 未转义写入 ini 插值：

```python
from alembic import context
from sqlalchemy import create_engine, pool
from app.config import settings
from app.models import Base

target_metadata = Base.metadata

def run_migrations_online():
    connectable = create_engine(settings.database_url, poolclass=pool.NullPool)
    try:
        with connectable.connect() as connection:
            context.configure(connection=connection, target_metadata=target_metadata,
                              compare_type=True, compare_server_default=True)
            with context.begin_transaction():
                context.run_migrations()
    finally:
        connectable.dispose()
```

这是对生成模板在线函数的替换参考；保留模板对在线/离线模式的调用分支。离线 SQL 生成不作为本课基础要求。记录数据库名、schema、版本，但不打印带密码的 URL。

### 8.3 空库建基线

确认当前模型仍为数据库列 body，且连接的是**专用空库**，再执行：

```bash
alembic init migrations
alembic revision --autogenerate --rev-id 001_baseline -m "baseline schema"
alembic upgrade head
```

init 仅在尚未初始化的工程运行。生成后先审读再 upgrade，至少检查五张表、外键删除策略、长度/状态约束、默认值、已采用索引和约束名称。若 autogenerate 遗漏对象，人工补全脚本；不可因为命令成功就当基线完整。

另建一份空库执行 `upgrade head`，确认不依赖 `create_all()` 或人工先建表；随后按第六课 seed 校验正常查询和新增写入。

### 8.4 列改名：审读而不是盲跑

目标是数据库 `questions.body → content`，Python/API 的字段仍叫 body。先调整目标模型：

```python
body: Mapped[str] = mapped_column("content", Text)
# 同步修改该模型 __table_args__ 中的表达式，约束名称保持不变：
CheckConstraint("char_length(content) BETWEEN 10 AND 20000", name="questions_body_len")
```

在具有 001_baseline 结构的教学库上生成：

```bash
alembic revision --autogenerate --rev-id 002_body_content -m "rename question body"
```

工具可能将改名当作删除/新增：

```python
# 危险候选，仅用于审读，不执行。
op.add_column("questions", sa.Column("content", sa.Text(), nullable=False))
op.drop_column("questions", "body")
```

有数据且无默认时，第一步添加 NOT NULL 列可能就失败；在空表或其他生成顺序下行为不同。准确结论是“无法表达保数据改名，并有失败/丢数据风险”，不能宣称该脚本在有数据表上一定完整执行后静默清空。

手工改成明确改名，保留生成文件的 revision/down_revision 元数据：

```python
from alembic import op

def upgrade():
    op.alter_column("questions", "body", new_column_name="content")

def downgrade():
    op.alter_column("questions", "content", new_column_name="body")
```

PostgreSQL 改名会保留列内容及引用该列的约束关联；metadata 中的 CHECK 文本仍要同步改为 content。不要顺手改掉 answers.body 或外部 JSON 字段。

### 8.5 一次保数据的迁移往返

在副本上记录问题 id、正文内容和行数，包含中文、换行和边界长度；然后执行：

```bash
alembic upgrade head
alembic current
alembic downgrade 001_baseline
alembic upgrade head
alembic check
```

每一步核对：revision、列名、约束、记录数和逐 id 正文。中间回到 001 时应用也须使用对应版本，或暂停应用只做 SQL 检查；当前映射 content 的应用不能假装兼容 body 结构。最终升回 head，再回归 JSON/HTML 创建、详情与搜索。

不要盲用 `downgrade -1`：若当前只有 init，可能直接删表。`alembic check` 只说明 autogenerate 没检测到待生成变化，不验证所有数据库对象，更不验证数据语义。

### 8.6 已有库接入：核对后 stamp，不是跳过迁移

另一路径面对第六课已经存在的数据库：

1. 在副本中将实际结构与 **001_baseline 的标准空库产物**逐项比较，包含类型、可空性、默认值、外键、约束和已采用索引。
2. 核实清洗已完成、数据满足约束；修复差异，不靠 stamp 掩盖不一致。
3. 确认匹配 body 基线后，才可 `alembic stamp 001_baseline`。
4. 再执行 `alembic upgrade head` 做 body→content 改名并验证内容与应用。

stamp 只写版本标记，不建表、不清洗、不替你证明迁移已执行。不能在只有 body 的旧库 stamp 最新 head，跳过真正需要的改名。

### 8.7 B 档：slug 的分阶段上线

slug 不列入 M2 基础验收；保留它作为“结构变化还影响未来写入”的阅读案例。

- 先增加可空 slug，应用暂时兼容旧行。
- 发布能在**第一次 INSERT 前**生成 slug 的新应用，例如受约束的 UUID 标识；不能等插入后拿到 id 才填，否则最终 NOT NULL 下插入先失败。
- 回填旧行，核查 NULL/重复，再加 UNIQUE 与 NOT NULL；多版本部署时等旧写入端退出后才收紧。
- 说明 slug 是否成为公开 URL、是否允许更改及冲突处理。降级应用若不写 slug，需兼容策略，不能只回退代码。

删除 slug 列会丢失映射，不因脚本有 downgrade 就称数据可逆。历史数据清洗和破坏性操作需备份、审计或前向修复方案。

### 8.8 迁移审读清单

- 目标库/版本正确吗？旧库是不是还在依赖人工 DDL？
- 是否把改名当成删加？新增 NOT NULL 有没有历史数据与未来写入方案？
- 约束命名、ON DELETE、默认值、索引与第六课一致吗？autogenerate 的检测范围是否覆盖该对象？
- upgrade/downgrade 各在什么应用版本、数据状态下可用？是否真的保留内容？
- 脚本是否错误 import 当前业务模型？历史迁移应使用固定版本 SQL/Core 表达式或局部 Table，避免模型变化使旧迁移失效。
- 是否把多 head 当成需要分析的分支问题，而非随意删除历史？是否用重复清洗覆盖旧证据？

## 九、M2 交付与作业

**课堂 5 分钟。** 基础工作预估 3—4 小时；课堂计数和教师提供的验收骨架可以复用。

### 9.1 A 档基础交付

| 交付 | 验收 |
|---|---|
| 当前核心功能持久化 | 三个 JSON 端点、HTML 页面与健康检查不回归；不是要求本课补齐所有未来业务 |
| 五表模型与约束 | 与第六课基线一致；保留约束错误到 409 的翻译 |
| 一个代表性列表 N+1 对照 | 固定契约/数据/页大小，新 Session，覆盖 DTO/序列化；响应相同 |
| 事务边界 | 成功提交；标签中途失败无半截数据；提交失败不提前 201/303 |
| 五条 SQL 对照阅读 | 重点复做列表和回答数，其余按第六课小数据核对，不再额外创造五个接口 |
| 迁移链 | 空库到 head；副本完成 001→002→001→002，正文与约束核对 |
| 一次选型说明 | ORM/Core/text 任一选择及理由，允许继续保留合理 SQL |

不以“全仓 commit 恰好一次”评分；脚本、测试和后台任务可有独立事务。基础请求路径不能出现破坏业务原子性的中途提交。也不以“所有列表 SQL ≤3”评分，而是说明每一类查询有何必要、会如何随数据增长。

AI 协作记录选本次真实的一段模型、查询或迁移建议：提示词、输出、判断、证据，有问题才附修复 diff。原方案合理可以保留，不强制找到一个必须改 text 的例子，不要求新增固定数量 ADR。

### 9.2 B 档选做

全项目 N+1 扫描、selectin/joined/聚合的传输与计划对照、raiseload 测试、slug 扩展迁移、复杂报表 Core/text 对照。任选一项，建议不超过一小时；完整资料保留供自学，不变成隐性必交。

## 十、素材与验证边界

制作独立演示工程前需要补齐：

- Python/FastAPI/Starlette/SQLAlchemy/PostgreSQL/Alembic 的锁定版本，以及函数作用域依赖行为测试。
- 正常基线、纯 lazy 反例、中途 commit 反例、排序反例分开的源码与数据状态；不在同一请求里叠加所有故障。
- 第六课 seed、扩展 20/50 条分页数据、同进程计数测试和响应等价断言；大数据与网络 RTT 模拟单独标识。
- 001_baseline 与 002_body_content 两个实际迁移文件、空库创建和副本恢复流程、正文内容核对与应用回归。
- 缺数据库/现场超时时使用注明版本环境的预录证据，不用示意耗时表冒充实测。

本轮使用现有 SQLAlchemy 2.0.54 环境做了精简模型的内存 SQLite 验证：三个问题共用一位作者，含零回答与标签；lazy/selectin/aggregate 得到相同输出，执行次数分别为 9/5/4，符合本节在该数据下的推导。另验证了事务异常回滚、joinedload 集合需要 unique，以及带 LIMIT 的 PostgreSQL 方言编译会包装主查询。这些是机制验证，不是完整五表模型、HTTP 序列化链或真实性能报告。

PostgreSQL 压测、完整 Alembic 往返和浏览器验收尚未执行；现有第一课 Python 环境未安装 Alembic，本轮未安装新依赖。SQLite 的最小机制验证不能证明 PostgreSQL 约束和迁移全部通过。复位只操作明确标记的可丢弃副本，不覆盖学生未提交代码或唯一数据。

## 十一、收束与前后衔接

第五课确定请求执行方式和成功响应时机；第六课定义合法状态和 SQL 结果；第七课让 ORM 的隐式工作可见，并为结构演进留证据。

第八课承接 API 契约、并发写入与重试正确性；第九课把 SQL 计数、失败回滚与契约核对纳入测试；第十六课再讨论迁移与部署顺序。深分页、全文检索等放在本课/第六课自学拓展，不错误指向讲 React 的第十一课。

讲：能解释“这条 SQL 是谁触发的”“这次成功何时才被确认”“新环境怎样得到同样的数据库”，比记住更多 ORM 方法重要。

参考：SQLAlchemy 2.0 的 Session Basics、Relationship Loading Techniques、Constraint Naming；FastAPI Advanced Dependencies；Alembic Autogenerate/Cookbook；PostgreSQL ALTER TABLE。结论需结合教学锁定版本和真实验证证据。
