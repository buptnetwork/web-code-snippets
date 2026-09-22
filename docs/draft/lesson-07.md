# 第 7 次课教学底稿
## ORM 机制、关系加载与迁移 ｜ 交付 M2

---

## 〇、给 PPT 制作团队的全局说明

本次课 100 分钟，留 5 分钟缓冲。**本次课是全课程"隐式性"主题的最高峰**：ORM 的价值和它的危险来自同一件事——它替你做了很多你没写的事。今天的每一个单元都在回答同一个问题：**它替我做了什么，以及我怎么让它在做错的时候出声。**

**本次课有三个高光，按重要性排序**：

1. **N+1 定量与三阶段修复（单元 5，18 分钟）**。不要做成 before/after 两行，要做成**四行三列**的阶段表——因为 `selectinload` 只是止血，真正的修法是聚合子查询。这个"修了还不是最优"的层次是本单元的全部价值。同时必须演示"**N+1 藏在序列化阶段**"——端点代码里一行查询都看不到，SQL 却发了 41 条。
2. **事务边界与 Unit of Work（单元 7，11 分钟）**。必须现场制造出"半截数据"：问题入库了，标签没入库。然后用一句依赖改法把 commit 从 15 处收到 1 处。
3. **Alembic 的盲区（单元 9，14 分钟）**。重点**不是**教怎么跑 `alembic upgrade`，而是让学生亲眼看到 `autogenerate` 把一次列改名生成成 `drop_column` + `add_column`——**一次发布，整列数据消失，而且脚本语法完全正确、执行完全成功**。这是本次课的课程主题落点，也是全课程"不可逆错误"的顶点。

**本次课的教学法**：前六次课都是"先痛感后命名"。本次课要在此之上加一层——**"先看它替你做了什么，再看它替你做错了什么"**。所以单元 3 的 Unit of Work 演示（"我没写 UPDATE 它怎么就更新了"）必须在讲任何 API 之前做完，它是理解后面所有问题的钥匙。

**若时间不够的压缩顺序**：先压单元 10 的 C 档卡（整体移课后）→ 再压单元 8 的第 4、5 条 SQL 翻译（留作业）→ 再压单元 6 的 `joinedload` 行数放大演示（只留判据表）。**单元 5、7、9 不能压缩。**

**一个需要教师裁决的地方**：单元 7 会引入 `expire_on_commit=False` 并演示 `DetachedInstanceError`。这个错误是 FastAPI + SQLAlchemy 组合下最高频的踩坑，但解释它需要触及 Session 的对象状态机（transient / pending / persistent / detached / expired）。底稿采用的做法是**只讲现象和两条纪律，不画状态机**。如果你希望补上状态机，需要额外 4 分钟，建议从单元 8 借。

---

## 一、开场：从"手写 SQL 都对了"到"还差什么"

**约 4 分钟。**

内容：

第 6 次课结束时，项目的数据层达到了一个不错的状态：

| 已经对了 | 还没有 |
|---|---|
| 类型选择有依据 | 建表是**手工执行的 DDL**，没有版本管理 |
| 约束完整（NOT NULL / UNIQUE / FK / CHECK） | 数据清洗脚本**是一次性执行的**，没人知道它跑过没有 |
| 索引按三条规则建好 | 数据访问全是 `text()` 手写 SQL |
| 8 条业务 SQL 能跑 | 每条 SQL 的结果要**手工映射成对象** |

讲：

> 今天要解决的是右边那一列。但我要先把今天这节课的性质说清楚，因为它和前六次课不太一样。
>
> 前六次课我们做的事情，方向都是**"把隐式的变成显式的"**：
>
> - 第 3 次课：装饰器的"魔法"→ 打印 `app.routes` 看清它是个数据结构
> - 第 4 次课：重复的样板 → 抽成有名字的依赖
> - 第 5 次课：中间件的执行顺序 → 打印出来看
>
> **今天我们要引入一个工具，它的整个卖点就是"帮你隐式地做事"。**
>
> ORM 会替你生成 SQL、替你发 UPDATE、替你在你访问某个属性的时候悄悄查一次库、替你在提交时决定哪些对象需要写回。这些事做对了，你的代码会短一半；做错了，**你会看到一个完全正常的页面，背后发了 41 条 SQL**。
>
> 所以今天的主线只有一句话：
>
> **它替我做了什么？我怎么让它在做错的时候出声？**

本次课结束时你应当能回答：

- 我没写 `UPDATE`，它怎么就更新了？这个机制叫什么？
- 端点函数里明明只有一行查询，为什么日志里有 41 条 SQL？**这 40 条是从哪一行代码发出来的？**
- `selectinload` 和 `joinedload` 怎么选？为什么 `joinedload` 用在一对多上会出问题？
- `commit()` 应该写在哪？为什么"写在每个 service 里"是错的？
- `alembic revision --autogenerate` 生成的脚本，我为什么必须逐行读？**它最可能在哪里害我？**
- 什么时候应该放弃 ORM，直接写 SQL？

---

## 二、解剖台：三段"看不出问题"的 ORM 代码

**约 10 分钟。三个演示都要做。**

### 情境设定

> 你把第 6 次课的手写 SQL 交给 AI，说"帮我改成 SQLAlchemy ORM"。它很快给了你一份，能跑，页面正常，测试通过。
>
> 三个问题藏在里面。

### 代码（tag: `v7-broken`）

```python
# app/models.py —— AI 产出的模型（节选）
class Question(Base):
    __tablename__ = "questions"
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    title: Mapped[str] = mapped_column(Text)
    body: Mapped[str] = mapped_column(Text)
    author_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.id"))
    status: Mapped[str] = mapped_column(Text, default="open")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)

    author: Mapped["User"]        = relationship()
    answers: Mapped[list["Answer"]] = relationship()
    tags: Mapped[list["Tag"]]     = relationship(secondary="question_tags")
```

```python
# app/schemas/question.py
class QuestionOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    title: str
    author: UserBrief            # ← 嵌套
    answer_count: int
```

```python
# app/routers/questions.py
@router.get("/questions", response_model=list[QuestionOut])
def list_questions(sort: str = "created_at", session: Session = Depends(get_session)):
    stmt = text(f"SELECT * FROM questions ORDER BY {sort} DESC LIMIT 20")   # ③
    ids = [r.id for r in session.execute(stmt)]
    return [session.get(Question, i) for i in ids]                          # ①
```

```python
# app/services/question.py
def create(session, title, body, author_id, tag_names):
    q = Question(title=title, body=body, author_id=author_id)
    session.add(q)
    session.commit()                                    # ② commit 第 1 次

    for name in tag_names:
        tag = session.scalar(select(Tag).where(Tag.name == name))
        if tag is None:
            tag = Tag(name=name)
            session.add(tag)
            session.commit()                            # ② commit 第 2..k 次
        q.tags.append(tag)
    session.commit()                                    # ② commit 最后一次
    return q
```

### 演示一：一次请求，41 条 SQL

打开 `echo=True`，请求 `/questions?size=20`，然后数日志行数：

```bash
curl -s "localhost:8000/questions" > /dev/null
# 服务端日志：
grep -c "^SELECT\|^INFO sqlalchemy.engine.Engine SELECT" server.log
# 41
```

提问：**端点函数里有几行查询？**

学生会数出 2 行（`session.execute` 和列表推导里的 `session.get`）。

```
1 条：   那个 text() 的 SELECT
20 条：  20 次 session.get(Question, i)
20 条：  ???   ← 这 20 条在哪一行？
```

让学生找。**找不到**，因为它不在端点里。

> 那 20 条是 `q.author` 触发的——**而 `q.author` 出现在 `QuestionOut` 这个 schema 里，不在任何一行 Python 代码里。**
>
> 序列化的时候，Pydantic 去读 `q.author`，ORM 发现这个关系还没加载，**就悄悄发了一条 SELECT**。20 个问题，20 条。
>
> 这是今天第一件要记住的事：**N+1 最常见的藏身处不是循环，是序列化。** 你在端点里看不到它。
>
> 单元 5 会把这件事量化，并给出三层修法。

### 演示二：半截数据

在 `create` 里，第二个标签处理到一半时抛异常（现场用一个不存在的标签名触发 `CHECK` 约束，或者直接插一行 `raise`）：

```bash
curl -X POST localhost:8000/questions -d '{"title":"...","tag_names":["python","x"]}'
# 500
```

```sql
SELECT id, title FROM questions WHERE title = '...';
--  100042 | ...          ← 问题在！

SELECT * FROM question_tags WHERE question_id = 100042;
--  (0 rows)              ← 标签没有
```

> **请求失败了，返回了 500，但数据库里留下了一条没有标签的问题。**
>
> 这不是"部分成功"，这是**脏状态**。它比彻底失败更糟：用户以为失败了，会重试；重试时标题重复，被 `UNIQUE` 挡住（第 6 次课的护栏），于是他永远发不出这条问题，而且不知道为什么。
>
> 原因就在那三个 `commit()`。单元 7 解决它。

### 演示三：排序字段直接拼进 SQL

**这是第 6 次课欠下的账。**

```bash
curl -s "localhost:8000/questions?sort=title"     | jq -r '.[0].title'
# 能用 —— 说明这个字符串确实直接进了 SQL

curl -s "localhost:8000/questions?sort=view_count" | jq -r '.[0].title'
# 也能用

curl -s "localhost:8000/questions?sort=(SELECT count(*) FROM users)" | jq length
# 20 —— 一个子查询被当成排序表达式执行了
```

> 第三条请注意：**一个任意的 SQL 表达式被执行了。**
>
> 它现在看起来无害，只是排序结果变了。但"能执行任意表达式"就已经足够做**盲注**了——用 `CASE WHEN ... THEN 一列 ELSE 另一列 END` 配合观察返回顺序，可以一个字符一个字符地把 `password_hash` 猜出来。
>
> **完整的注入演示在第 15 次课。** 今天我们只把它修掉，并且顺便说清一件事：
>
> **ORM 不会自动帮你防注入。** 你在 `text()` 里拼字符串，ORM 一样把它原样发出去。ORM 的贡献是**让安全的写法变成最自然的写法**——单元 8 会看到，在 ORM 里你想拼字符串反而更费劲。

### 三个问题的性质对照（**做成一页**）

| 问题 | 症状 | 测试能发现吗 | 代价 |
|---|---|---|---|
| ① N+1 | 页面正常，**只是慢** | ❌ 断言"返回 20 条"会通过 | 性能；换成远程数据库后放大 6 倍 |
| ② 到处 commit | **500 + 脏数据** | 只有测"失败路径"才能发现 | **数据不一致，不可逆** |
| ③ 拼接排序字段 | 完全正常 | ❌ | 注入 |
| —— | | | |
| 共同点 | **正常路径上三个都表现完美** | | |

> 又一次：**在你能做的所有常规检查里，它们都是好的。** 这是本课程从第 5 次课以来反复出现的同一种错误性质。
>
> 今天要做的不只是修好这三个，是**为每一个装上一个会出声的装置**。

### 欠账清单

| 问题 | 本次课处理 | 何时还 |
|---|---|---|
| N+1（含序列化阶段的隐藏 N+1） | **单元 5、6** | — |
| 到处 commit → 半截数据 | **单元 7** | — |
| 排序字段拼接 | **单元 8.4**（白名单） | 注入演示 → 第 15 次课 |
| 建表无版本管理 | **单元 9**（Alembic） | — |
| 第 6 次课的数据清洗脚本没纳入管理 | **单元 9.5** | — |
| 手写 SQL 结果要手工映射 | 单元 4、8 | — |
| 连接池参数怎么定 | 单元 4.1 给结论 | **第 16 次课**（与 worker 数联合算） |
| 先读后写（`get_or_create_tag`）在并发下仍不可靠 | 单元 7.6 给结论 | **第 11 次课** |
| 异步 ORM 要不要上 | 单元 4.4 回收第 5 次课的判断 | 不做 |

---

## 三、ORM 到底做了什么：先看它替你做的那件事

**约 6 分钟。这一单元是理解后面所有内容的钥匙，不能跳。**

### 3.1 一句话定义

**醒目页**：

> **ORM 做两件事：**
>
> **一、把"行"变成"对象"，把"对象"变成"行"。**（映射）
> **二、记住你从库里拿出来的每个对象，在提交时把改动写回去。**（Unit of Work）
>
> 第一件事是大家都知道的。**第二件事是所有惊喜的来源。**

### 3.2 现场演示："我没写 UPDATE，它怎么就更新了"

```python
# 现场在一个临时端点里跑
@router.post("/lab/uow")
def lab_uow(session: Session = Depends(get_session)):
    q = session.get(Question, 5)        # ① SELECT
    q.title = "被改过的标题"              # ② 只是改了一个 Python 属性
    return {"ok": True}                  # ③ 没有 add，没有 commit，没有 UPDATE
```

日志：

```
SELECT questions.id, questions.title, ... FROM questions WHERE questions.id = 5
UPDATE questions SET title=%(title)s WHERE questions.id = %(id)s     ← 它自己发了
COMMIT
```

```sql
SELECT title FROM questions WHERE id = 5;
--  被改过的标题        ← 真的改了
```

**停下来，逐步解释（做成一页，分四步展开）**：

> **1. `session.get()` 之后，这个对象被 Session 记住了。**
> Session 里有一张表（identity map），记录着"id=5 的 Question 对象是这一个"。同时它还存了一份**从数据库读出来时的原始值**。
>
> **2. 你改了 `q.title`，Session 知道了。**
> ORM 给映射的属性装了拦截器。你一赋值，它就在这个对象上标记"title 脏了"。
>
> **3. 在需要的时候，Session 把所有脏对象的改动翻译成 SQL 发出去。这叫 flush。**
> 它会对比"现在的值"和"读出来时的值"，**只为变了的列生成 UPDATE**。
>
> **4. `commit()` 会先 flush，再提交事务。**
> 我们的 `get_session` 依赖在请求结束时 commit，所以 UPDATE 在那时发出。

### 3.3 三个直接后果

| 后果 | 好在哪 | 坏在哪 |
|---|---|---|
| 不用手写 UPDATE | 不会漏字段，不会拼错列名；改了什么就更新什么 | **你不小心改了什么，它也会写回去** |
| 对象身份唯一 | 同一个请求里两次 `get(Question, 5)` 是同一个对象，不会有两份不一致的副本 | 不同 Session 里是不同对象，跨 Session 传对象会出问题 |
| flush 的时机不由你写 | 少写很多代码 | **报错的位置和出错的原因不在同一行** |

第三条要现场演示一次，因为它最让人困惑：

```python
q = Question(title="一个已经存在的标题", body="...", author_id=1)
session.add(q)                                     # ← 这里不发 SQL
rows = session.scalars(select(Question).limit(1)).all()   # ← IntegrityError 在这一行抛出
```

```
sqlalchemy.exc.IntegrityError: duplicate key value violates unique constraint
"questions_title_key"
[SQL: INSERT INTO questions ...]
```

> 报错在 `select` 那一行，但错的是上面的 `add`。
>
> 原因：**autoflush**。Session 在执行任何查询之前，会先把待写入的东西 flush 出去——否则你可能查不到自己刚加的数据。
>
> 这是一个非常合理的设计，但它造成的现象是："**我一行查询，怎么报了个插入冲突？**"
>
> 判据：**看到 `IntegrityError` 报在一个 `select` 上，去找它上面最近的 `add`。**
>
> 〔`session.no_autoflush` 可以临时关掉它。极少需要。C 档卡。〕

### 3.4 本单元的判据

**醒目页**：

> **ORM 的隐式性有一个边界：它只对"Session 认识的对象"生效。**
>
> - 你从 Session 查出来的对象 → 它管
> - 你 `add` 进去的对象 → 它管
> - 你用 `session.execute(update(...))` 直接发的语句 → **它不管**（不会更新内存里的对象，可能导致内存和数据库不一致）
> - 别的进程改的数据 → 它不知道
>
> 这条边界会在单元 7 和第 11 次课各造成一次麻烦。今天先记住它存在。

---

## 四、模型定义与 Session 注入

**约 10 分钟。**

### 4.1 Engine 与连接池（一次说清，不展开）

```python
# app/db.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.config import settings

engine = create_engine(
    settings.database_url,
    pool_size=5,              # 常驻连接数
    max_overflow=10,          # 峰值可临时多开的数量
    pool_pre_ping=True,       # 取连接前 ping 一次，避免用到已断开的连接
    pool_recycle=1800,        # 30 分钟回收，避开中间件/数据库的空闲超时
    echo=settings.sql_echo,   # ← 今天的主角，见单元 5
)

SessionLocal = sessionmaker(engine, expire_on_commit=False)   # ← 这个参数见单元 7.5
```

**四个参数各一句话**：

| 参数 | 一句话 | 不设会怎样 |
|---|---|---|
| `pool_size` | 每个进程常驻几条连接 | 默认 5；够小项目用 |
| `max_overflow` | 峰值时最多再借几条 | 上限 = `pool_size + max_overflow` = 15 |
| `pool_pre_ping` | 防"连接已被对端关闭" | 偶发 `OperationalError: server closed the connection`，**且只在闲置一段时间后出现**，极难复现 |
| `pool_recycle` | 主动回收老连接 | 同上 |

**接上第 5 次课的欠账**：

> 第 5 次课讲 worker 数量时说过：**worker 数、连接池大小、数据库 `max_connections` 是一组互相牵制的约束。** 现在可以把式子写出来了：
>
> ```
> 进程数 × (pool_size + max_overflow) ≤ 数据库 max_connections − 预留
>    4    ×  (   5     +     10     ) = 60  ≤  100 − 10 ✅
>    8    ×  (   5     +     10     ) = 120 >  100 − 10 ❌ 数据库先挂
> ```
>
> 判据：**加 worker 之前先算这个式子。** 完整的部署计算在第 16 次课。

**还第 4 次课的另一笔账**：

```python
# app/main.py
@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    engine.dispose()          # 进程退出时释放连接池

app = FastAPI(lifespan=lifespan)
```

> 第 4 次课的 C 档卡里提过 `lifespan` "用来管进程级资源"。这就是最典型的一个用法：**连接池是进程级资源，不是请求级的。**

### 4.2 模型：类型标注直接决定 `NOT NULL`

```python
# app/models.py
from datetime import datetime
from sqlalchemy import (BigInteger, Text, Integer, Boolean, ForeignKey,
                        DateTime, CheckConstraint, UniqueConstraint, Index,
                        MetaData, func, text)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

NAMING = {                                 # ← 见 4.3
    "pk": "pk_%(table_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "ix": "ix_%(table_name)s_%(column_0_name)s",
}

class Base(DeclarativeBase):
    metadata = MetaData(naming_convention=NAMING)


class Question(Base):
    __tablename__ = "questions"

    id:         Mapped[int]      = mapped_column(BigInteger, primary_key=True)
    title:      Mapped[str]      = mapped_column(Text)               # → NOT NULL
    body:       Mapped[str]      = mapped_column(Text)               # → NOT NULL
    author_id:  Mapped[int]      = mapped_column(
        BigInteger, ForeignKey("users.id", ondelete="RESTRICT"), index=True)
    status:     Mapped[str]      = mapped_column(Text, server_default="open")
    view_count: Mapped[int]      = mapped_column(Integer, server_default="0")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now())

    author:  Mapped["User"]         = relationship(back_populates="questions")
    answers: Mapped[list["Answer"]] = relationship(
        back_populates="question",
        cascade="all, delete-orphan",
        passive_deletes=True)                                        # ← 见 4.5
    tags:    Mapped[list["Tag"]]    = relationship(
        secondary="question_tags", back_populates="questions")

    __table_args__ = (
        UniqueConstraint("title", name="title"),
        CheckConstraint("status IN ('open','closed','deleted')", name="status"),
        CheckConstraint("char_length(title) BETWEEN 5 AND 200",   name="title_len"),
        CheckConstraint("view_count >= 0",                        name="views_nonneg"),
        Index("idx_questions_status_created",
              "status", text("created_at DESC"), text("id DESC")),
    )


class Answer(Base):
    __tablename__ = "answers"
    id:          Mapped[int]        = mapped_column(BigInteger, primary_key=True)
    question_id: Mapped[int]        = mapped_column(
        BigInteger, ForeignKey("questions.id", ondelete="CASCADE"), index=True)
    author_id:   Mapped[int | None] = mapped_column(                # ← 可空！
        BigInteger, ForeignKey("users.id", ondelete="SET NULL"), index=True)
    body:        Mapped[str]        = mapped_column(Text)
    is_accepted: Mapped[bool]       = mapped_column(Boolean, server_default="false")
    created_at:  Mapped[datetime]   = mapped_column(
        DateTime(timezone=True), server_default=func.now())

    question: Mapped["Question"]  = relationship(back_populates="answers")
    author:   Mapped["User|None"] = relationship()
```

**三条要专门讲的**：

**一、`Mapped[str]` 是 `NOT NULL`，`Mapped[str | None]` 才可空。**

> 这是 SQLAlchemy 2.0 最舒服的一个设计：**类型标注直接生成约束**。
>
> 而它恰好和第 6 次课的纪律一致：**默认 `NOT NULL`，可空要有理由**。在这里"可空"必须写成 `| None`——**它是一个显式的动作，不是遗漏的结果**。
>
> 注意 `Answer.author_id: Mapped[int | None]`——这是全项目唯一一个可空的外键，理由在第 6 次课说过（`ON DELETE SET NULL`，保留注销用户的回答）。**这一个 `| None` 就是那个决定的全部痕迹**，所以它值得在 `decisions.md` 里有一条。

**二、`server_default` 不是 `default`。**

| | 写在哪 | 谁生成值 | 绕过 ORM 的写入 |
|---|---|---|---|
| `default="open"` | Python 侧 | **SQLAlchemy 在 INSERT 时填** | ❌ 没有默认值 |
| `server_default="open"` | 生成 DDL 的 `DEFAULT` | **数据库** | ✅ 有 |

> 看解剖台里 AI 写的：`default="open"`、`default=datetime.now`。
>
> 两个问题：
> 1. **建表语句里没有 `DEFAULT`**，所以手工 `INSERT`、导入脚本、别的服务写入时都没有默认值；
> 2. `default=datetime.now` 是**应用服务器的时间**。多台机器时钟不完全一致，而且它是**无时区的本地时间**（回收第 6 次课：`TIMESTAMPTZ`）。
>
> **判据：时间戳和状态默认值一律用 `server_default`，让数据库生成。** 这是第 6 次课"约束下推"的同一条原则在 ORM 上的体现。

**三、`CheckConstraint` 和 `Index` 写在模型里，不是写在迁移里。**

> 为什么？因为**模型是 Alembic 比对的基准**（单元 9）。不写在模型里的约束，`autogenerate` 看不到，下次它可能生成一个"删掉这个约束"的脚本。
>
> 判据：**数据库里该有什么，模型里就要声明什么。模型是唯一的真相来源。**

### 4.3 命名约定：把第 6 次课的纪律变成结构性的

> 第 6 次课的 15 条清单里，第 15 条是"每个约束都显式命名"。当时是靠人记得写 `CONSTRAINT xxx`。
>
> 现在用 `naming_convention` 解决了：**你只写 `name="title"`，工具自动拼成 `uq_questions_title`。** 忘了写 `name` 的话，PostgreSQL 会自己生成一个名字，而 Alembic 下次比对时会发现名字不一致，**反复生成无意义的 drop/create 脚本**。
>
> 这是本课程的一个反复出现的模式：**把"依赖开发者记得"的规则，换成"工具自动产生一致结果"的机制。**

### 4.4 Session 依赖：改掉第 4 次课的 `get_conn`

```python
# app/deps.py —— 第 4 次课的版本
def get_conn():
    with engine.begin() as conn:
        yield conn

# 今天的版本
def get_session():
    session = SessionLocal()
    try:
        yield session
        session.commit()          # ← 唯一的 commit（见单元 7）
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()

SessionDep = Annotated[Session, Depends(get_session)]    # ← 类型别名
```

**用类型别名的理由（值得单独说）**：

```python
# 之前：每个端点都写一遍
def get_question(qid: int, session: Session = Depends(get_session)): ...

# 之后
def get_question(qid: int, session: SessionDep): ...
```

> 好处不只是短。**下次换实现（比如换成异步 Session），只改一行别名，所有端点的签名不用动。**
>
> 这就是第 4 次课那句话的又一次应用：**依赖的价值与它被复用的次数成正比。**

### 4.5 两层 cascade：一个高频混淆（**醒目页**）

```python
# ① 数据库层
author_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="RESTRICT"))
question_id: Mapped[int] = mapped_column(ForeignKey("questions.id", ondelete="CASCADE"))

# ② ORM 层
answers: Mapped[list["Answer"]] = relationship(
    cascade="all, delete-orphan", passive_deletes=True)
```

| | 写在哪 | 谁执行删除 | 对什么写入路径生效 |
|---|---|---|---|
| `ondelete="CASCADE"` | `ForeignKey` → 生成 DDL | **数据库** | **所有**（含手工 SQL、导入脚本、别的服务） |
| `cascade="all, delete-orphan"` | `relationship` | **ORM Session**（发一堆 DELETE） | **只有**经过 ORM 的操作 |

**三条判据**：

> 1. **数据库层的 `ondelete` 必须有。** 它是第 6 次课那第四道护栏，谁都绕不过。
> 2. **ORM 层的 `cascade` 也要有**，但目的不同：它让**内存里的对象状态**和数据库保持一致。没有它，你从 `q.answers` 里 `remove()` 一个回答，数据库里那行不会被删。
> 3. **`passive_deletes=True` 很重要。** 没有它，`session.delete(q)` 会先把 500 条回答全部 SELECT 出来，再逐条发 DELETE——**501 条 SQL**。加上它，ORM 信任数据库的 `ON DELETE CASCADE`，只发 1 条 DELETE。
>
> 判据：**`ondelete="CASCADE"` 和 `passive_deletes=True` 成对出现。**

### 4.6 回收第 4 次课作业二的预测（**请做成一个专门的页面**）

> 第 4 次课作业二的第三行，我让你们预测："数据库从直接连接改为连接池 + 显式 Session，要改哪些文件？"
>
> **现在验证答案。**

| 层 | 实际改动 | 为什么 |
|---|---|---|
| `db.py` | **新增** | Engine + sessionmaker |
| `deps.py` | 改 1 个函数 | `get_conn` → `get_session` |
| `models.py` | **新增** | ORM 模型 |
| `repositories/` | **全部重写** | 这里才是真正碰数据的地方 |
| `services/` | **只改类型标注** | 业务规则一行没动 |
| `routers/` | **只改类型标注**（用了别名后是 0 处） | HTTP 边界一行没动 |
| `schemas/` | 加一个 `from_attributes=True` | — |

> **对上的举手。**
>
> 我想强调的不是"你猜对了没有"，是**这个答案的形状**：换掉整个数据访问技术栈，`services/` 和 `routers/` 基本不动。
>
> 第 4 次课我说"分层的回报全在被修改这件事上"，第 5 次课加 HTML 界面兑现了一次，**今天是第二次，而且这次换的是地基。**
>
> 反过来说：**如果你的 `routers/` 里散布着 SQL，今天这次改动就是一次全项目重写。**

**顺手回收第 5 次课的一个判断**：

> 第 5 次课讨论 `async def` 时我说过："异步是全链路的。要彻底异步，数据库也得换成异步引擎，那意味着 `deps.py`、`repositories/` 全部要改。"
>
> 今天你看到了 `repositories/` 有多少代码。**这就是当时说"成本不划算"的具体分量。**
>
> 所以本项目的决定仍然是：**同步栈 + `def` 端点**。这个决定要写进 `decisions.md`，包括它的失效条件。

### 材料

- tag `v7-broken`（起始）、`v7-models`（本单元结束）。
- 高光图：`default` vs `server_default` 的两行对照表。
- **高光图**：两层 cascade 对照表（三列）。
- **高光图**：4.6 的"预测验证表"，`services/` 与 `routers/` 两行用绿色高亮。
- 代码片段：完整的 `models.py`（作为对照素材，不逐行念）。

---

## 五、现场必做：N+1 定量与三阶段修复

**约 18 分钟。本次课最高光，绝对不能压缩。**

### 5.1 先把计数器装上

**这是本单元的方法论前提：先有测量手段，再谈优化。**

```python
# app/sqlcount.py
import contextlib
from sqlalchemy import event

@contextlib.contextmanager
def count_sql(engine):
    stats = {"n": 0, "sql": []}
    def before(conn, cursor, statement, params, ctx, many):
        stats["n"] += 1
        stats["sql"].append(statement.split("\n")[0][:90])
    event.listen(engine, "before_cursor_execute", before)
    try:
        yield stats
    finally:
        event.remove(engine, "before_cursor_execute", before)
```

```python
# 临时端点，或者用 scripts/count_sql.py
with count_sql(engine) as s:
    client.get("/questions?size=20")
print(s["n"])          # 41
for q in s["sql"][:6]:
    print("  ", q)
```

> **`echo=True` 适合看单条 SQL 长什么样，不适合数条数**——几十条日志滚过去，你根本数不清。
>
> 这个计数器很小，但它是今天所有判断的依据。**第 9 次课它会变成一条测试断言**：
>
> ```python
> def test_list_questions_sql_count(client):
>     with count_sql(engine) as s:
>         client.get("/questions?size=20")
>     assert s["n"] <= 3          # ← N+1 回归就会让这条测试失败
> ```
>
> 这就是把"性能问题"变成"会出声的错误"的办法。**记住这个思路，它是本次课最可迁移的东西。**

### 5.2 阶段 0：朴素版，数一次

请求 `/questions?size=20`：

```
SQL 条数：41
  SELECT * FROM questions ORDER BY created_at DESC LIMIT 20
  SELECT questions.id, ... FROM questions WHERE questions.id = 1
  SELECT questions.id, ... FROM questions WHERE questions.id = 2
  ... (×20)
  SELECT users.id, ... FROM users WHERE users.id = 7
  ... (×20)
```

拆解来源（**做成一页**）：

| 条数 | 来自 | 在代码的哪一行 |
|---|---|---|
| 1 | 那条 `text()` 查 id | 端点第 1 行，**看得见** |
| 20 | `session.get(Question, i)` | 端点第 2 行，**看得见** |
| 20 | `q.author` 懒加载 | **不在任何 Python 代码里**——在 `QuestionOut` 的字段声明里 |

> 前 21 条是"写法笨"，改改就好。
>
> **后 20 条是本单元真正的主题：它的触发点在 schema 里，执行点在序列化阶段，而端点函数完全看不出来。**

### 5.3 改成正常的 ORM 查询，再数一次

```python
@router.get("/questions", response_model=list[QuestionOut])
def list_questions(session: SessionDep, size: int = 20):
    stmt = (select(Question)
            .where(Question.status == "open")
            .order_by(Question.created_at.desc(), Question.id.desc())
            .limit(size))
    return session.scalars(stmt).all()
```

```
SQL 条数：21          （1 + 20 author）
```

> 好了一点。**但那 20 条序列化懒加载还在。** 而且如果 `QuestionOut` 里还有 `answer_count`，还要再加 20 条。
>
> **注意这个现象：端点代码变短了、变漂亮了，问题一点没解决。** 这也是 AI 常给的"优化"——把写法改对了，把根本问题留下了。

### 5.4 关键一页：Out schema 决定了你必须加载什么

**醒目页，这是本单元的核心洞见**：

> **`response_model` 里声明的每一个嵌套字段，都是一次潜在的懒加载。**
>
> ```python
> class QuestionOut(BaseModel):
>     id: int
>     title: str
>     author: UserBrief       # ← 需要 q.author      → 必须 eager load
>     tags: list[TagBrief]    # ← 需要 q.tags        → 必须 eager load
>     answer_count: int       # ← 需要数 q.answers   → 必须用聚合，不是 eager load
> ```
>
> **判据：写完 Out schema，就知道查询里要加什么 `options()`。**
>
> 这是第 3 次课"契约先行"在数据访问层的直接后果：**契约不只约束响应格式，它还约束你的查询必须取到什么。**

### 5.5 阶段 1：`selectinload` —— 止血

```python
from sqlalchemy.orm import selectinload

stmt = (select(Question)
        .options(selectinload(Question.author),
                 selectinload(Question.tags))
        .where(Question.status == "open")
        .order_by(Question.created_at.desc(), Question.id.desc())
        .limit(size))
```

```
SQL 条数：3
  SELECT ... FROM questions WHERE status='open' ORDER BY ... LIMIT 20
  SELECT ... FROM users WHERE users.id IN (7, 12, 45, ...)
  SELECT ... FROM tags JOIN question_tags ... WHERE question_tags.question_id IN (...)
```

> **41 → 3。** `selectinload` 的做法是：先查主表，收集所有 id，用**一条 `IN` 查询**把关联对象一次取回。
>
> 这是最常用、最安全的加载策略。**如果你只记一个，记它。**

### 5.6 阶段 2：`answer_count` —— `selectinload` 在这里是错的

现在把 `answer_count` 加进 `QuestionOut`。朴素做法：

```python
.options(selectinload(Question.answers))
# schema 里：answer_count: int = Field(...)   通过 len(q.answers) 计算
```

```
SQL 条数：4     ← 看起来很好
```

**但看传输的行数**：

```sql
-- 第 4 条 SQL 实际取回了多少行？
SELECT count(*) FROM answers WHERE question_id IN (那 20 个 id);
-- 1847            ← 有一条热门问题有 1600 条回答
```

> **为了算出 20 个数字，我们把 1847 行完整的回答正文从数据库搬到了 Python 内存里。**
>
> SQL 条数只有 4 条，计数器很满意，**但这是个错的实现**。
>
> **判据：`selectinload` 解决"查询次数"，不解决"传输量"。** 需要的是一个数字时，就让数据库算这个数字。

正确做法：

```python
answer_count = (
    select(func.count(Answer.id))
    .where(Answer.question_id == Question.id)
    .correlate(Question)
    .scalar_subquery()
    .label("answer_count")
)

stmt = (select(Question, answer_count)
        .options(selectinload(Question.author), selectinload(Question.tags))
        .where(Question.status == "open")
        .order_by(Question.created_at.desc(), Question.id.desc())
        .limit(size))

rows = session.execute(stmt).all()
return [QuestionOut(**q.__dict__, answer_count=n) for q, n in rows]
```

```
SQL 条数：3      传输行数：20 + 20 + ~60
```

〔另一种更优雅的写法是把它声明成模型上的 `column_property`，这样 `q.answer_count` 直接可用。代价：**每次查 Question 都会带上这个子查询**，包括不需要它的地方。判据：只在"几乎所有查询都需要它"时用 `column_property`。C 档卡。〕

### 5.7 四阶段数据表（**封面级素材**）

| 阶段 | SQL 条数 | 传输行数 | 本机耗时 | 模拟 RTT=1ms |
|---|---|---|---|---|
| ① 朴素（解剖台原样） | **41** | ~60 | 78 ms | **480 ms** |
| ① 朴素，`size=100` | **201** | ~300 | 390 ms | **2 400 ms** |
| ② `selectinload` 全部关系 | 4 | **1 847** | 61 ms | 66 ms |
| ③ `selectinload` + 聚合子查询 | **3** | ~100 | **11 ms** | 14 ms |

〔制作团队：请在演示机实测填入真实数据。`scripts/count_sql.py --rtt 1` 通过在 `before_cursor_execute` 里 sleep 来模拟网络往返。上表为理论预期，用于校验实验搭建是否正确。〕

**四条观察，逐条讲**：

**观察一：N+1 的成本随页面大小线性增长，别的方案不变。**

> `size` 从 20 到 100，朴素版 41→201 条，耗时 5 倍；阶段③还是 3 条。
>
> 这解释了为什么 N+1 经常"上线后才炸"：**开发时你翻第一页看 10 条，上线后有人把 `size` 设成 100，或者某个问题下有 2000 条回答。**

**观察二：N+1 的真实代价取决于网络往返，不是 SQL 本身。**

> 41 条 SQL 每条都命中了第 6 次课建好的索引，**每条都只要 0.3 毫秒**。所以本机上只慢 7 倍。
>
> 把数据库挪到另一台机器（这是生产环境的常态），每条 SQL 多 1 毫秒往返 → **41 毫秒变成 480 毫秒，慢 44 倍。**
>
> **判据：N+1 不是"慢查询"问题，是"查询次数"问题。** 它无法靠加索引解决——第 6 次课的索引在这里全部生效了，问题还在。
>
> 这一条请务必讲透，它是第 6 次课和本次课之间最重要的区分。

**观察三：阶段②的 SQL 条数最优之一，但它是错的。**

> 只看 SQL 条数会让你停在阶段②。**衡量指标选错，优化就会停在错的地方。**
>
> 所以我们的计数器要配一个第二指标：**传输行数**。第 9 次课写测试时，两个都要断言。

**观察四：三种修法的边界。**

| 你要的是 | 用什么 |
|---|---|
| 关联对象的**内容**（要展示作者名、标签名） | `selectinload` / `joinedload` |
| 关联对象的**数量**（只要个数） | **聚合子查询**，不要加载对象 |
| 关联对象的**存在性**（有没有） | `EXISTS` 子查询（回收第 6 次课 6.7） |

### 5.8 装上会出声的装置：第五道结构性护栏

**醒目页**：

```python
# 方案 A：在关系上声明——这个关系永远不许懒加载
answers: Mapped[list["Answer"]] = relationship(lazy="raise")

# 方案 B：在查询里声明——本次查询未显式加载的关系一律禁止懒加载
stmt = select(Question).options(
    selectinload(Question.author),
    raiseload("*"),
).limit(20)
```

再请求一次，故意不加载 `tags`：

```
sqlalchemy.exc.InvalidRequestError: 'Question.tags' is not available due to
lazy='raise'
```

> **N+1 从"页面正常但慢"变成了"直接报错"。**
>
> 这是本课程第五道结构性护栏，也是第一道**专门对付性能问题**的护栏：

| 次课 | 护栏 | 把什么变成了什么 |
|---|---|---|
| 第 3 次课 | `response_model` | 字段泄漏 → 出不去 |
| 第 4 次课 | 全局异常处理器 | 内部信息泄漏 → 统一错误体 |
| 第 5 次课 | Jinja2 自动转义 | 用户输入变 HTML → 纯文本 |
| 第 6 次课 | 数据库约束 | 脏数据 → 写入失败 |
| **第 7 次课** | **`lazy="raise"`** | **静默的 N+1 → 响亮的报错** |

> 五道护栏的共同点：**把"需要有人足够细心才能发现的问题"，变成"不可能被忽略的问题"。**
>
> 第 5 次课我说过：`async def` + 阻塞这类错误"无法在结构上堵住"。今天你看到，N+1 是能堵住的——**因为"这个关系有没有被显式加载"是 ORM 能知道的信息**。
>
> 判据：**一类错误能不能装护栏，取决于运行时有没有足够的信息判断它。** 有，就装护栏；没有，就用第 5 次课那三层（约定 + 机械检查 + 定量兜底）。

**使用建议（要给，否则学生会全局打开然后到处炸）**：

> `lazy="raise"` 全局打开会很吵——很多地方你确实只想取一个对象然后访问它的关系。
>
> 本课程的建议：**在"列表类查询"上用 `raiseload("*")`，在模型上不设。** 列表查询是 N+1 的主要发生地，单对象查询的一两次懒加载没什么关系。
>
> 写进 `decisions.md`。

### 材料

- `app/sqlcount.py`：计数器，**第 9 次课要复用，请统一设计**。
- `scripts/count_sql.py`：命令行版，参数 `--url --size --rtt`，输出 SQL 条数 + 传输行数 + 耗时 + 前若干条 SQL。
- tag `v7-nplus1`（阶段①）、`v7-eager`（阶段③ + `raiseload`）。
- **封面级素材**：5.7 的四行五列表，`201` 和 `2400 ms` 红色高亮，`1847` 橙色高亮（"SQL 少了但传输爆了"）。
- **封面级素材**：5.2 的"41 条从哪来"三行表，第三行标注"不在任何 Python 代码里"。
- **封面级素材**：五道护栏累加表。
- 高光图：5.4 的 Out schema → 加载策略 的箭头图。
- 截图：`lazy="raise"` 触发的完整报错。
- 截图：seed 里那条 1600 回答的热门问题（`SELECT count(*) ... GROUP BY question_id ORDER BY 2 DESC LIMIT 3`）。

---

## 六、加载策略选择判据

**约 7 分钟。**

### 6.1 三种策略的判据表（**本单元核心**）

| 策略 | 发几条 SQL | 主表行数 | 用在什么关系上 |
|---|---|---|---|
| `lazy="select"`（默认） | **1 + N** | N | 只在"确定不会访问"时 |
| `selectinload` | **2** | N + M | **1:N 集合 → 首选** |
| `joinedload` | **1**（LEFT JOIN） | **N × 每个的子行数** | **N:1 / 1:1 单对象 → 首选** |
| `raiseload` | 0，抛异常 | — | 防御 |

**一句话判据**：

> **取"多个"用 `selectinload`，取"一个"用 `joinedload`。**

### 6.2 为什么 `joinedload` 不适合一对多（**现场演示**）

```python
# 用 joinedload 加载 answers
stmt = (select(Question)
        .options(joinedload(Question.answers))
        .limit(20))
print(len(session.scalars(stmt).unique().all()))    # 20 —— 对象数对了
```

但看实际发出的 SQL 和返回的行数：

```sql
-- SQLAlchemy 会把主查询包进子查询，保证 LIMIT 正确
SELECT ... FROM (SELECT ... FROM questions LIMIT 20) AS anon_1
LEFT JOIN answers ON ...
-- 返回行数：1847        ← 每个问题的每条回答都是一行，主表列被重复
```

**解释（做成一页）**：

> `LEFT JOIN` 的结果是笛卡尔式展开：一个有 1600 条回答的问题，会产生 1600 行，**每一行都重复携带这个问题的 title 和 body**。
>
> 两个代价：
> 1. **传输量放大**：标题和正文被重复传 1600 次；
> 2. **需要去重**：所以上面要写 `.unique()`——忘了写会得到 1847 个对象而不是 20 个。**SQLAlchemy 2.0 在这种情况下会直接报错提醒你，这是好事。**
>
> 反过来，`joinedload` 用在 **N:1** 上完全没有这个问题：一个问题只有一个作者，join 之后行数不变。
>
> **判据重述：**
> - `q.author`（一个）→ `joinedload`，一条 SQL，无放大
> - `q.answers`（多个）→ `selectinload`，两条 SQL，无放大

### 6.3 补两个实用情形

**一、嵌套加载。**

```python
# 问题 → 回答 → 回答的作者
.options(selectinload(Question.answers).selectinload(Answer.author))
```

> 链式写下去。**每一层加一条 SQL，不是乘。** 三层关系 = 4 条 SQL。

**二、单对象详情页。**

```python
def get_detail(session, qid: int) -> Question:
    stmt = (select(Question)
            .options(joinedload(Question.author),          # 一个 → joined
                     selectinload(Question.tags),          # 多个 → selectin
                     selectinload(Question.answers).joinedload(Answer.author))
            .where(Question.id == qid))
    q = session.scalars(stmt).unique().one_or_none()
    if q is None:
        raise QuestionNotFound()
    return q
```

> 注意这个函数：**它把这个页面需要的一切一次性取全。**
>
> 判据：**一个"页面/端点"对应一次"取全"的查询。** 不要让 service 返回一个"半成品对象"，让序列化阶段去补齐——那正是单元 5 那 20 条 SQL 的来源。

### 6.4 一个容易忽略的坑：`lazy` 设在模型上 vs 设在查询上

| 设在哪 | 语法 | 影响范围 |
|---|---|---|
| 模型的 `relationship` | `relationship(lazy="selectin")` | **所有**查这个模型的地方 |
| 查询的 `options()` | `.options(selectinload(...))` | 只有这次查询 |

> **建议：默认策略留在模型上尽量保守（`select` 或 `raise`），具体策略写在查询上。**
>
> 理由：模型上写 `lazy="selectin"` 意味着**每一次**查 Question 都会多一条 SQL——包括那些只要 title 的地方。**"总是多查一点"比"偶尔 N+1"更难发现，因为它均匀地慢。**
>
> 判据：**加载策略是查询的属性，不是模型的属性。** 因为"要不要加载关联数据"取决于这次要干什么。

### 材料

- 高光图：`joinedload` 在 1:N 上的行数放大示意（一个问题 × 3 条回答 = 3 行，问题列重复三次，用颜色标出重复部分）。
- 表：四种策略判据表。
- 截图：`joinedload(Question.answers)` 的 SQL 与返回行数（1847）。

---

## 七、事务边界：一个请求一个事务

**约 11 分钟。本次课第二高光。**

### 7.1 先数一下项目里有多少个 commit

```bash
grep -rn "\.commit()" app/ | wc -l
# 15
```

```bash
grep -rn "\.commit()" app/ --include="*.py" | head
# app/services/question.py:23
# app/services/question.py:31
# app/services/question.py:38
# app/services/answer.py:17
# ...
```

> 15 个 `commit()`，散落在 6 个 service 文件里。
>
> 回顾第 4 次课作业一的第 3 条硬性要求：**"零处 `commit()` 出现在 `routers/` 和 `services/` 中"**。当时用的是 `engine.begin()`，事务边界由上下文管理器管着，所以你们做到了。
>
> **换成 ORM 之后，AI 把它们全加回来了。** 因为网上绝大多数 SQLAlchemy 教程都是"`add` 完就 `commit`"。

### 7.2 复现半截数据，把机制讲清

回到解剖台的 `create`：

```python
session.add(q); session.commit()        # ← 事务 1：问题已经永久写入
for name in tag_names:
    ...; session.commit()               # ← 事务 2..k
    q.tags.append(tag)
session.commit()                        # ← 事务 k+1
```

**画时序图（本单元核心素材）**：

```
事务1 ┌──────────┐
      │ INSERT q │ COMMIT   ← 问题落库，不可撤销
      └──────────┘
事务2            ┌──────────────┐
                 │ INSERT tag   │ COMMIT
                 └──────────────┘
事务3                          ┌────────┐
                               │ 抛异常  │ ROLLBACK
                               └────────┘
                                    ↓
                    数据库里：一条没有标签的问题
                    客户端收到：500
```

> **`commit()` 的含义是"这部分改动永久生效，不能再撤销"。**
>
> 你在一个业务操作中间 commit，就是在说"前半截无论后半截成不成功都要保留"。**这几乎永远不是你想要的。**
>
> 判据：**一个业务操作是一个原子单位。它要么完整发生，要么完全没发生。**

### 7.3 修法：commit 只出现在一个地方

```python
# app/deps.py —— 唯一的 commit
def get_session():
    session = SessionLocal()
    try:
        yield session
        session.commit()           # ← 请求成功 → 提交
    except Exception:
        session.rollback()         # ← 任何异常 → 回滚
        raise
    finally:
        session.close()
```

```python
# app/services/question.py —— 一个 commit 都没有
def create(session, title, body, author_id, tag_names):
    q = Question(title=title, body=body, author_id=author_id)
    session.add(q)
    for name in tag_names:
        q.tags.append(get_or_create_tag(session, name))
    session.flush()                # ← 只 flush，拿到 q.id，不提交
    return q
```

**三个要点**：

> **一、`flush` 不是 `commit`。**
> `flush` 把 SQL 发出去（所以能拿到数据库生成的 id），但**事务还开着，随时能回滚**。需要 id 时用 `flush`，不要用 `commit`。
>
> **二、"事务边界 = 请求边界"是一个默认，不是铁律。**
> 它对 99% 的 Web 请求是对的。例外：批量导入任务（要分批提交，否则一个大事务会锁住太久）、需要"部分成功"语义的操作。**例外要在 `decisions.md` 里写明。**
>
> **三、错误处理器在这个链条里的位置。**
> service 抛 `DuplicateTitle`（一个 `AppError`）→ 穿过 `get_session` 的 `except` → **rollback** → 继续向外抛 → 第 4 次课的异常处理器接住 → 返回 409。
>
> **数据回滚了，客户端拿到了正确的业务错误码。两件事都对，而且没有一行 try/except 写在 service 里。**

### 7.4 现场验证三条路径

| 路径 | 触发方式 | 期望 | 验证 |
|---|---|---|---|
| 成功 | 正常 POST | 数据全部入库 | 查问题和标签都在 |
| 业务错误 | 重复标题 | 409 + **数据库无痕迹** | `SELECT count(*)` 不变 |
| 未预期错误 | service 中间 `raise RuntimeError` | 500 + **数据库无痕迹** | 同上 |

> 第三行要真的跑一次。**这是第 4 次课那个统一错误契约 + 今天这个事务边界共同作用的结果**，两个机制配合起来才有"要么全成要么全不"的保证。

再数一次：

```bash
grep -rn "\.commit()" app/ | wc -l
# 1
```

> **15 → 1。** 这个 1 在 `deps.py`。
>
> 这条可以机械检查，**加入第 9 次课的 CI 检查清单**：
> ```bash
> grep -rn "\.commit()" app/routers app/services && exit 1
> ```

### 7.5 `expire_on_commit` 与 `DetachedInstanceError`（**30 秒演示，必须讲**）

把 `expire_on_commit=False` 去掉（用默认值 `True`），请求一次详情页：

```
sqlalchemy.orm.exc.DetachedInstanceError: Instance <Question at 0x...> is not
bound to a Session; attribute refresh operation cannot proceed
```

**解释（一页）**：

> 默认情况下，`commit()` 之后 Session 会把所有对象标记为"过期"——意思是"数据库可能变了，下次访问属性时我再去查一遍"。
>
> 然后我们 `close()` 了 Session。**于是"下次访问属性"就没地方查了。**
>
> 而"下次访问属性"发生在哪？**序列化阶段**——又是它。
>
> 两个可选做法：
>
> | 做法 | 代价 |
> |---|---|
> | `expire_on_commit=False` | 对象保留 commit 前的值。**如果数据库在 commit 后被别人改了，你返回的是旧值**——对 Web 请求可接受 |
> | service 返回 Pydantic 对象而不是 ORM 对象 | 多写一层映射代码，但彻底摆脱 Session 生命周期 |
>
> **本课程选第一个**，理由是代码量。但要配一条纪律：
>
> **判据：service 返回的 ORM 对象，必须已经加载好 Out schema 需要的一切。** 不要指望序列化阶段还能查库。
>
> 这条纪律和单元 5.4、6.3 是同一条，**今天第三次出现**。它值得做成一句口号：
>
> **"在 service 里取全，序列化阶段不查库。"**

### 7.6 顺手回收：`get_or_create` 在并发下仍然不可靠

```python
def get_or_create_tag(session, name):
    tag = session.scalar(select(Tag).where(Tag.name == name))   # 查
    if tag is None:
        tag = Tag(name=name)                                    # 创建
        session.add(tag)
    return tag
```

> 这是第 6 次课单元 4.4 那个 TOCTOU 模式的第四个实例。两个并发请求都查不到 `python` 这个标签，都尝试创建，**第二个撞 `UNIQUE` 约束报 500**。
>
> 第 6 次课的护栏（`tags.name UNIQUE`）保证了**不会产生两个同名标签**——数据是干净的。但用户体验是 500。
>
> 正确的做法是"插入时冲突则忽略"：
>
> ```python
> from sqlalchemy.dialects.postgresql import insert
> stmt = (insert(Tag).values(name=name)
>         .on_conflict_do_nothing(index_elements=["name"])
>         .returning(Tag.id))
> tag_id = session.scalar(stmt) or session.scalar(
>     select(Tag.id).where(Tag.name == name))
> ```
>
> **判据（本课程第五次重复）："先读后写"在并发下都不可靠。** 要么用数据库的原子操作（`ON CONFLICT`、`UPDATE ... SET x = x + 1`），要么加锁。
>
> 〔完整的并发控制手段——乐观锁 `version_id_col`、悲观锁 `SELECT FOR UPDATE`——**第 11 次课**。今天只把这一处修好。〕

### 材料

- **封面级素材**：7.2 的半截数据时序图。
- **封面级素材**：`grep -c commit` 的 15 → 1 前后截图。
- 高光图：7.4 的三条路径验证表。
- 截图：半截数据的两条 SQL 查询结果（问题在、标签空）。
- 截图：`DetachedInstanceError` 完整报错。
- tag `v7-tx`（本单元结束状态）。

---

## 八、把 SQL 翻译成 ORM，以及什么时候不翻译

**约 11 分钟。**

### 8.1 五条翻译（并排对照，请做成左右分栏）

**#1 列表分页 —— 几乎一一对应**

```sql
SELECT q.*, u.display_name FROM questions q JOIN users u ON u.id = q.author_id
WHERE q.status = 'open' ORDER BY q.created_at DESC, q.id DESC LIMIT 20 OFFSET 40;
```

```python
stmt = (select(Question)
        .options(joinedload(Question.author))
        .where(Question.status == "open")
        .order_by(Question.created_at.desc(), Question.id.desc())
        .limit(20).offset(40))
```

> 注意 `.order_by(Question.created_at.desc(), Question.id.desc())`——**第 6 次课的"稳定排序必须带主键"这条纪律在 ORM 里一模一样**。ORM 不会替你加这个。

**#2 LEFT JOIN + GROUP BY 回复数 —— 已在单元 5.6 用聚合子查询改写**

```python
# 见 5.6。这里给 GROUP BY 版本作为对照
stmt = (select(Question, func.count(Answer.id).label("n"))
        .outerjoin(Answer, Answer.question_id == Question.id)
        .where(Question.status == "open")
        .group_by(Question.id)
        .order_by(Question.created_at.desc(), Question.id.desc())
        .limit(20))
```

> `outerjoin` 就是 `LEFT JOIN`。`func.count(Answer.id)` 就是 `count(a.id)`——**第 6 次课那条"`LEFT JOIN` 之后要 `count(附表主键)` 不是 `count(*)`"的纪律，在 ORM 里也一字不差。**
>
> 判据：**ORM 不会替你修正 SQL 的语义陷阱。** 第 6 次课学的每一条都还生效。

**#5 关键词搜索 —— 翻译后更好**

```python
def search(session, kw: str | None, status: str | None, tag: str | None):
    stmt = select(Question)
    if kw:
        stmt = stmt.where(or_(Question.title.ilike(f"%{kw}%"),
                              Question.body.ilike(f"%{kw}%")))
    if status:
        stmt = stmt.where(Question.status == status)
    if tag:
        stmt = stmt.where(Question.tags.any(Tag.name == tag))
    return session.scalars(stmt.order_by(...).limit(20)).all()
```

> **这是 ORM 明确胜过手写 SQL 的场景：动态拼条件。**
>
> 手写 SQL 要做这件事，你得维护一个 `conditions` 列表和一个 `params` 字典，然后 `" AND ".join(...)`——**那是字符串拼接，是注入的温床**。
>
> ORM 的 `stmt = stmt.where(...)` 是在拼一棵表达式树，**参数化是自动的**。

**#6 存在性判断**

```python
has = session.scalar(
    select(exists().where(and_(Answer.question_id == qid,
                               Answer.author_id == uid))))
```

**#8 UPDATE ... RETURNING**

```python
stmt = (update(Question)
        .where(Question.id == qid)
        .values(view_count=Question.view_count + 1)   # ← 原子递增，不是读-改-写
        .returning(Question.view_count))
new_count = session.scalar(stmt)
```

> `values(view_count=Question.view_count + 1)` 生成的是 `SET view_count = questions.view_count + 1`——**在数据库里算，原子的**。
>
> 对比 ORM 风格的写法：
> ```python
> q = session.get(Question, qid)
> q.view_count += 1               # ← 读-改-写，并发下丢计数
> ```
> **后者是第 6 次课 6.9 那个错误的 ORM 版本。** 它看起来更"面向对象"，但它在并发下丢数据。
>
> 判据：**计数器类的更新一律用 `update()` 语句，不要用对象属性赋值。**
>
> 注意：这条语句绕过了 Session 的对象跟踪（单元 3.4 说的边界），所以**内存里那个 `q.view_count` 还是旧值**。如果同一请求后面还要用它，要 `session.refresh(q)`。

### 8.2 两条不翻译

**#3b 标签 AND 语义**

```python
stmt = (select(Question)
        .join(Question.tags)
        .where(Tag.name.in_(names))
        .group_by(Question.id)
        .having(func.count(func.distinct(Tag.id)) == len(names)))
```

> 这条**能翻译**，而且翻译得还行。给它一个中性评价：**和原 SQL 一样难懂，但不更难懂。** 可以翻。

**#7 `generate_series` 时间序列 —— 不翻**

```python
# app/repositories/stats.py
SQL_DAILY_NEW = text("""
    -- 为什么不用 ORM：generate_series 是 PG 特有的集合返回函数，
    -- 在 ORM 里表达它需要 func.generate_series + 手工 join，
    -- 结果比原 SQL 更长且更难读，而这条查询完全不涉及对象映射。
    SELECT d::date AS day, count(q.id) AS n
    FROM generate_series(:start, :end, interval '1 day') AS d
    LEFT JOIN questions q
           ON q.created_at >= d AND q.created_at < d + interval '1 day'
    GROUP BY d ORDER BY d
""")

def daily_new_questions(session, start, end) -> list[Row]:
    return session.execute(SQL_DAILY_NEW, {"start": start, "end": end}).all()
```

### 8.3 判据：什么时候放弃 ORM（**本单元核心，醒目页**）

| 情形 | 建议 | 理由 |
|---|---|---|
| CRUD、按 id 取、简单列表 | **ORM** | 对象映射的价值最大 |
| 动态拼条件的搜索 | **ORM** | 拼表达式树比拼字符串安全 |
| 需要修改对象并写回 | **ORM** | Unit of Work 就是为这个设计的 |
| 报表、多层聚合、交叉表 | **SQL** | 没有对象要映射，ORM 只是在碍事 |
| 数据库特有功能（`generate_series`、递归 CTE、`tsvector`、窗口函数的复杂用法） | **SQL** | ORM 的抽象在这里漏得最厉害 |
| 批量操作（`INSERT ... SELECT`、百万行 UPDATE） | **SQL** | 逐对象操作会发出百万条语句 |
| 需要精确控制生成的 SQL | **SQL** | — |

**一句话总判据**：

> **如果翻译成 ORM 之后，你还得回头看原 SQL 才能理解它做了什么——那就别翻译。**
>
> ORM 是为"对象和行之间来回搬"服务的。**一条查询里没有对象，只有数字和分组，ORM 就没有东西可以贡献。**

**用 `text()` 的四条纪律（作业三要用）**：

> 1. **必须参数化。**`text()` 里绝不出现 f-string 拼接的值。
> 2. **必须放在 `repositories/`。** 不许出现在 `services/` 或 `routers/`——回收第 4 次课的分层。
> 3. **必须有注释说明"为什么不用 ORM"。** 这条注释是给三个月后的你和你的同事看的。
> 4. **返回值要映射成明确的类型**（`Row` 的字段名、`NamedTuple` 或 Pydantic），不要把裸 `Row` 一路传到 router。

### 8.4 还第 6 次课的账：排序字段白名单

```python
# app/repositories/question.py
SORT_MAP: dict[str, tuple] = {
    "latest":  (Question.created_at.desc(), Question.id.desc()),
    "oldest":  (Question.created_at.asc(),  Question.id.asc()),
    "views":   (Question.view_count.desc(), Question.id.desc()),
}

def list_questions(session, sort: str = "latest", ...):
    order = SORT_MAP.get(sort) or SORT_MAP["latest"]    # ← 不在白名单就用默认
    stmt = select(Question).order_by(*order)
```

更好的做法——**让不合法的值根本进不来**：

```python
# app/schemas/question.py
SortKey = Literal["latest", "oldest", "views"]

@router.get("/questions")
def list_questions(session: SessionDep, sort: SortKey = "latest"): ...
```

> 现在 `?sort=(SELECT count(*) FROM users)` 会被**第 3 次课的入口闸门**挡下，返回 422，并且 `/openapi.json` 里会明确列出三个合法值。
>
> **两道防护，各自的职责：**
> - `Literal` 类型：**给出好的错误信息**，并让契约自我描述
> - `SORT_MAP.get(...) or 默认`：**兜底**，因为这个 repository 函数也可能被定时任务调用
>
> 这和第 6 次课 4.6 说的"schema 负责体验，约束负责正确性"是同一个结构。
>
> 再强调一次：**ORM 在这里的贡献不是"更安全"，是"让安全的写法更自然"。** 你在 `order_by()` 里想拼字符串反而要绕路（得 `text()`），**而绕路这个动作本身就是一个提醒。**

### 材料

- **高光图**：SQL / ORM 左右分栏对照，五条各一页（或两条一页）。
- **高光图**：8.3 的判据表。
- 代码片段：`text()` 四条纪律 + `SQL_DAILY_NEW` 的完整注释示例。
- 截图：修复后 `?sort=(SELECT...)` 返回 422 的响应体（含 `/openapi.json` 里的枚举值）。

---

## 九、Alembic 最小闭环

**约 14 分钟。本次课第三高光。**

### 九.0 先说清它解决什么问题

> 现在的状态：表是我们手工在 psql 里 `CREATE TABLE` 建的，第 6 次课的数据清洗是手工 `UPDATE` 的。
>
> 三个问题：
>
> | 问题 | 具体表现 |
> |---|---|
> | **新人建不出环境** | "你把建表 SQL 发我"——发哪一版？中间改过的那几次呢？ |
> | **不知道生产库是哪一版** | 你在本地加了一列，忘了在生产加，上线后 500 |
> | **改错了回不去** | 手工 `ALTER TABLE` 加错了列，怎么退回？ |
>
> 迁移工具的核心就是一件事：**把"数据库结构的变化"变成一串有顺序、能前进、能后退的脚本，并在数据库里记下"我现在走到第几步"。**

### 9.1 最小闭环：五步

```bash
# 1. 初始化
alembic init -t generic migrations
```

```python
# 2. migrations/env.py 里接上模型
from app.models import Base
from app.config import settings

config.set_main_option("sqlalchemy.url", settings.database_url)
target_metadata = Base.metadata

def run_migrations_online():
    ...
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        compare_type=True,              # ← 检测类型变化
        compare_server_default=True,    # ← 检测默认值变化
    )
```

```bash
# 3. 生成脚本
alembic revision --autogenerate -m "init schema"

# 4. 审读并修正脚本      ← 本单元 80% 的时间花在这一步

# 5. 应用
alembic upgrade head

# 6. 验证能退回
alembic downgrade -1
alembic upgrade head
```

**先把"它在数据库里记什么"打开看**：

```sql
SELECT * FROM alembic_version;
--  version_num
--  a3f91c22e0d7
```

> **一张表，一行，一个字符串。** 这就是"我现在走到第几步"。
>
> 迁移工具的全部魔法就是：比对这个版本号和脚本目录里的链条，决定要跑哪几个脚本。

### 9.2 autogenerate 的盲区（**本单元核心，必须完整讲**）

**先做一个现场实验，让学生亲眼看到最危险的那一个。**

需求：把 `questions.body` 改名为 `questions.content`。

```python
# models.py
- body: Mapped[str] = mapped_column(Text)
+ content: Mapped[str] = mapped_column(Text)
```

```bash
alembic revision --autogenerate -m "rename body to content"
```

生成的脚本：

```python
def upgrade():
    op.add_column('questions', sa.Column('content', sa.Text(), nullable=False))
    op.drop_column('questions', 'body')          # ← 看这里

def downgrade():
    op.add_column('questions', sa.Column('body', sa.Text(), nullable=False))
    op.drop_column('questions', 'content')
```

**停下来提问：执行这个脚本会发生什么？**

引导出答案：

> **十万条问题的正文全部消失。**
>
> 而且注意：
> - 脚本语法完全正确；
> - `alembic upgrade head` 会**成功执行，没有任何警告**；
> - `downgrade` 也能"成功"——它会加回一个空的 `body` 列；
> - **测试可能全部通过**，因为测试库是空的，或者用的是新建的表。
>
> 你会在上线之后、在第一个用户打开问题详情页的时候发现。**而那时候数据已经没了。**
>
> 唯一的补救是从备份恢复——如果你有备份，如果备份够新，如果你发现得够早。

正确的脚本：

```python
def upgrade():
    op.alter_column('questions', 'body', new_column_name='content')

def downgrade():
    op.alter_column('questions', 'content', new_column_name='body')
```

> 一行。**数据完整保留。**
>
> 为什么 autogenerate 给不出这个？因为**它只能比对"两个状态"**：旧结构有 `body`、新结构有 `content`。"改名"这个**意图**只存在于你的脑子里，它看不见。
>
> **判据：autogenerate 能看见结构差异，看不见你的意图。凡是涉及意图的变更，脚本必须人工改写。**

**完整盲区清单（做成一页）**：

| 盲区 | 它会生成什么 | 后果 |
|---|---|---|
| **列/表改名** | `drop` + `add` | **整列数据丢失** |
| **类型变更** | `alter_column(type_=...)` | 不生成数据转换；`TEXT → INTEGER` 直接失败或截断 |
| **`CHECK` 约束** | **什么都不生成**（不可靠地反射） | 约束悄悄消失或反复被 drop |
| **`ON DELETE` 行为变更** | 不检测 | 级联策略静默失效 |
| **数据迁移（DML）** | 完全不管 | 新增 `NOT NULL` 列时旧行无值 → 加约束失败 |
| **视图、触发器、函数、扩展** | 不管 | — |
| **索引/约束命名差异** | 反复 drop + create | 每次 autogenerate 都有噪音（→ 用 4.3 的命名约定解决） |
| **多个 head（协作分支）** | 生成并行分支 | `upgrade head` 报错 "Multiple heads" |

### 9.3 第二个必讲的坑：加 `NOT NULL` 列

需求：给 `questions` 加一列 `slug TEXT NOT NULL UNIQUE`。

autogenerate 给：

```python
def upgrade():
    op.add_column('questions', sa.Column('slug', sa.Text(), nullable=False))
```

执行：

```
psycopg.errors.NotNullViolation: column "slug" of relation "questions"
contains null values
```

> **这次它报错了，这是好事。** 但学生的第一反应往往是"那我改成 `nullable=True` 吧"——那就放弃了约束。
>
> 正确做法是**三步式**（回收第 6 次课 4.7 的清洗流程，现在把它写进迁移）：

```python
def upgrade():
    # 1. 先加可空列
    op.add_column('questions', sa.Column('slug', sa.Text(), nullable=True))
    # 2. 回填数据
    op.execute("""
        UPDATE questions
        SET slug = lower(regexp_replace(title, '[^a-zA-Z0-9]+', '-', 'g'))
                   || '-' || id::text
        WHERE slug IS NULL
    """)
    # 3. 再收紧
    op.alter_column('questions', 'slug', nullable=False)
    op.create_unique_constraint('uq_questions_slug', 'questions', ['slug'])

def downgrade():
    op.drop_constraint('uq_questions_slug', 'questions', type_='unique')
    op.drop_column('questions', 'slug')
```

> **三步：加可空 → 回填 → 收紧。** 这是整个迁移实践里最常用的模式。
>
> 注意第 2 步用的是 `op.execute()` 原生 SQL，**不是 ORM**。理由很重要：
>
> **迁移脚本不能依赖 ORM 模型。** 因为模型代表的是"现在的最新结构"，而这个脚本要在"三个月前的那个结构"上运行。如果你在迁移里 `from app.models import Question`，半年后模型改了，这个老脚本就跑不了了。
>
> **判据：迁移脚本里只用 `op.*` 和原生 SQL，不 import 项目的模型。** 这是一条无例外的纪律。

### 9.4 downgrade 的两个层次（**必须讲清**）

> 第 6 次课和今天反复说"可回滚"。现在必须把它拆成两件事：

| | 能不能回去 | autogenerate 保证吗 |
|---|---|---|
| **结构能回去** | `drop_column` 把列删掉，结构回到旧状态 | ✅ 基本可以 |
| **数据能回去** | 那一列的数据？**没了** | ❌ **完全不保证** |

> 所以"我有 downgrade 脚本"**不等于**"我能安全回滚"。
>
> **判据：破坏性变更要分两次发布。**
>
> | 发布 | 做什么 | 能回滚吗 |
> |---|---|---|
> | 第一次 | 代码不再读写 `body` 这一列，但列还在 | ✅ 完全可回滚 |
> | （观察几天） | 确认没有任何东西在用它 | |
> | 第二次 | `op.drop_column('questions', 'body')` | ❌ 不可逆，但风险已经验证过了 |
>
> 这个模式叫**扩展-收缩（expand/contract）**，是零停机发布的基础。**→ 第 16 次课完整讲。** 今天只要接受这条纪律。

**本课程对 M2 的要求**：

> 1. **每个迁移必须写 downgrade**，哪怕是有损的；
> 2. **必须真的执行过一次 `downgrade -1` 然后 `upgrade head`**，并在提交说明里写明验证过；
> 3. **有损的 downgrade 要在脚本里加注释说明损失什么**。

### 9.5 把第 6 次课的清洗脚本纳入管理

> 第 6 次课我们手工执行了三条 `UPDATE` 修复脏 `status`。**那次执行没有留下任何记录。**
>
> 现在把它变成一个迁移：

```python
"""clean dirty status values

Revision ID: b7d2...
Revises: a3f9...
"""

def upgrade():
    # 数据修复：第 6 次课发现 30253 行 status 为 NULL，
    # 另有大小写与拼写不一致。业务确认：一律视为 open。
    op.execute("UPDATE questions SET status = 'open' WHERE status IS NULL")
    op.execute("UPDATE questions SET status = lower(status) WHERE status <> lower(status)")
    op.execute("UPDATE questions SET status = 'open' WHERE status = 'opened'")
    op.alter_column('questions', 'status', nullable=False)
    op.create_check_constraint(
        'ck_questions_status', 'questions',
        "status IN ('open','closed','deleted')")

def downgrade():
    # 有损：无法恢复原始的 NULL / 'OPEN' / 'opened' 值。
    # 仅移除约束，不还原数据。
    op.drop_constraint('ck_questions_status', 'questions', type_='check')
    op.alter_column('questions', 'status', nullable=True)
```

> 三个收获：
>
> 1. **那次清洗现在有记录了**——谁、什么时候、为什么、改了什么；
> 2. **它变得可重放**——新人建环境时会自动执行到同一个状态；
> 3. **`downgrade` 里那条注释很关键**：它诚实地说明这次回滚是有损的。**一个诚实的有损 downgrade 比一个假装无损的好。**

### 9.6 本次课的课程主题落点

**这一小节请完整制作，它是本次课与课程主题的正式接点。**

> 今天我要给你们一条比前几次更强的判断。
>
> 前几次课的 AI 错误：
>
> | 次课 | 错误 | 可逆性 |
> |---|---|---|
> | 第 3 次课 | 返回裸 dict 泄漏密码哈希 | 改代码就好 |
> | 第 4 次课 | 鉴权写成中间件 | 重构一下 |
> | 第 5 次课 | `async def` + 阻塞 | 改一个关键字 |
> | 第 6 次课 | DDL 漏约束 | 补约束 + 清洗数据（**开始变贵**） |
> | **今天** | **迁移脚本把改名变成 drop+add** | **数据没了** |
>
> 危险程度是递增的，而且**递增的方向是"离数据越近越贵"**。
>
> 所以我要给一条关于工具生成物的分级纪律：

**醒目页**：

> | 生成物 | 能不能"跑跑看" | 为什么 |
> |---|---|---|
> | 一个端点函数 | ✅ 可以 | 错了就报错，改了重跑 |
> | 一个 Pydantic schema | ✅ 可以 | 同上 |
> | 一条查询 | ✅ 可以 | 结果不对能看出来 |
> | **一个迁移脚本** | ❌ **必须先逐行读懂** | **它成功执行 = 数据已经改了** |
>
> **判据：凡是"执行即不可逆"的产物，一律先读懂再执行。**
>
> 落到具体动作上，M2 要求你对每个迁移脚本做三件事：
>
> 1. **逐行读**，特别盯 `drop_` 开头的每一个调用；
> 2. **在一份有数据的库的副本上先跑一次**（不是空库！空库跑不出数据丢失）；
> 3. **跑完对一次数——关键表的行数、关键列的非空数**。

具体到 Alembic，给三层护栏（**又是第 5 次课那套方法**）：

| 层 | 做法 |
|---|---|
| **约定** | 迁移脚本必须人工审读；`drop_column` / `drop_table` 必须在 PR 里被单独指出 |
| **机械检查** | CI 里：① `alembic upgrade head` 在一份带数据的快照上跑通；② `downgrade -1` 再 `upgrade head` 跑通；③ **grep 脚本里的 `drop_` 并要求有注释说明** → **第 9 次课** |
| **定量兜底** | 迁移前后跑一份"行数与非空数对账表"，差异超阈值就失败 |

> 中间那一条第 9 次课会真的写出来。**注意第 ① 条的"带数据的快照"**——这是本次课学到的最实用的一条运维习惯：**空库上跑迁移，测不出数据丢失。**

### 材料

- `migrations/`：完整的迁移链（init → clean status → add slug），**每个脚本都带审读注释**。
- **封面级素材**：9.2 的改名实验——autogenerate 的 `drop_column` 版本 与 `alter_column` 版本左右对照，左边标"十万行正文消失"，右边标"一行，数据完整"。
- **封面级素材**：9.2 的盲区清单（八行）。
- **封面级素材**：9.6 的"生成物分级"四行表。
- 高光图：9.3 的"加可空 → 回填 → 收紧"三步图。
- 高光图：9.4 的"结构能回去 / 数据能回去"两层表 + 扩展-收缩两次发布表。
- 截图：`alembic_version` 表的内容（一行一个字符串）。
- 截图：加 `NOT NULL` 列失败的 `NotNullViolation`。
- 截图：`downgrade -1` 与再次 `upgrade head` 的终端输出。
- **必备**：一份带数据的数据库快照（`pg_dump`），供"在有数据的库上跑迁移"演示。

---

## 十、C 档结论卡

**约 3 分钟。时间不够整体跳过。**

### 10.1 一句话结论卡

| 问题 | 结论 | 展开处 |
|---|---|---|
| Session 的对象状态 | transient / pending / persistent / detached / expired 五态。**日常只需知道"commit 后会过期、close 后会脱离"** | 单元 7.5 |
| `session.no_autoflush` | 临时关掉 autoflush。极少需要；需要时通常说明代码顺序有问题 | 单元 3.3 |
| `column_property` | 把聚合子查询挂到模型属性上。代价：**每次查这个模型都带上它** | 单元 5.6 |
| 异步 ORM（`AsyncSession`） | 需要 `asyncpg` + 全链路 `await`。**本课程不上**，理由见第 5 次课 5.4 与今天 4.6 | 不做 |
| 隔离级别 | 本课程用默认（PG: Read Committed）。**要记住的只有一句：任何隔离级别下，"先读后写"都需要额外手段** | 第 11 次课 |
| 乐观锁 | `mapper_args__ = {"version_id_col": version}`，冲突时抛 `StaleDataError` | **第 11 次课** |
| 悲观锁 | `select(...).with_for_update()` | **第 11 次课** |
| `bulk_insert_mappings` / `insert().values([...])` | 批量插入绕过对象跟踪，快几十倍。**代价：不触发 ORM 事件、不回填 id** | 自读 |
| Alembic 多 head | 协作分支各生成一个 revision → `alembic merge`。**预防：拉最新代码后再生成迁移** | 自读 |
| 零停机迁移 | 扩展-收缩模式；先加列并双写，再切读，最后删旧列 | **第 16 次课** |
| 软删除与 ORM | `with_loader_criteria` 或全局事件可以自动加 `deleted_at IS NULL`，把它变成结构性的 | 自读 |

### 10.2 ORM 跨栈落点对照

| 能力 | SQLAlchemy | Django ORM | Hibernate/JPA | Entity Framework | Prisma |
|---|---|---|---|---|---|
| 模型定义 | `Mapped` + `mapped_column` | `models.Model` | `@Entity` | `DbContext` + 类 | `schema.prisma` |
| Unit of Work | `Session` | **无显式 Session**，`save()` 即 UPDATE | `EntityManager` | `DbContext` | **无**，显式调用 |
| 默认加载策略 | lazy | lazy | lazy | **lazy（需显式开启）** | **不加载**，需 `include` |
| 修 N+1 | `selectinload` / `joinedload` | `prefetch_related` / `select_related` | `JOIN FETCH` / `@BatchSize` | `Include` | `include` |
| 禁止懒加载 | `lazy="raise"` / `raiseload` | 无内建（`Prefetch` 约束） | — | 可配置抛异常 | 天然（不加载就是没有） |
| 迁移 | Alembic | 内建 `makemigrations` | Flyway / Liquibase | `Add-Migration` | `prisma migrate` |
| 自动生成迁移的盲区 | 改名、CHECK、DML | **改名会提示交互确认** ← 更好 | — | 改名需手改 | 改名会提示 |

> 两点值得注意：
>
> **一、Prisma 的默认行为是"不加载关系"**，你必须显式 `include`。**这从根上消除了 N+1**——代价是每次都得写 `include`。这是一个"默认值选择"的好例子：**把危险的默认改成麻烦的默认。**
>
> **二、Django 的 `makemigrations` 检测到可能的改名时会交互式询问"你是把 X 改名成 Y 了吗？"** ——这正是 Alembic 缺的那一步。**知道别的工具在这里做了什么，能让你更清楚 Alembic 要你补什么。**

---

## 十一、M2 交付与作业

**约 6 分钟。本次课是里程碑交付。**

### 11.1 M2 交付清单

> M2 的目标：**数据层可信。**
>
> "可信"的意思是三件事：**数据不会脏**（第 6 次课的约束）、**结构的变化有记录且能退回**（今天的迁移）、**访问数据的代价是已知的**（今天的 SQL 计数）。

**新增要求（本次课）**：

| # | 内容 | 验收方式 |
|---|---|---|
| 1 | 全部数据访问经 ORM，或有理由的 `text()` | `text()` 每处都有"为什么不用 ORM"的注释 |
| 2 | `.commit()` 在 `app/` 下**只出现一次**，在 `deps.py` | `grep -rn "\.commit()" app/ \| wc -l` = 1 |
| 3 | 三条路径验证通过：成功 / 业务错误 / 未预期错误，后两者**数据库无痕迹** | 提交三次 SQL 对账截图 |
| 4 | Alembic 迁移链完整：**空库 `upgrade head` 能建出与模型一致的结构** | `alembic check` 无差异 |
| 5 | 至少一次 `downgrade -1` → `upgrade head` 验证通过 | 终端输出截图 |
| 6 | 第 6 次课的数据清洗已写成迁移 | 脚本 + downgrade 的有损说明 |
| 7 | 所有列表端点 SQL 条数 ≤ 3，且**不加载不需要的行** | N+1 报告 |
| 8 | 列表查询上有 `raiseload("*")` 或关系上有 `lazy="raise"` | grep |
| 9 | 排序参数用 `Literal` + 白名单映射 | `/openapi.json` 里能看到枚举值 |
| 10 | 模型里声明了全部约束与索引（与第 6 次课的 15 条清单一致） | `alembic check` + 清单自检 |

**累加要求（前六次课）**：分层、`response_model`、统一错误契约、配置外置、`def`/`async def` 正确、PRG、模板无 `| safe`。

**交付物**：

- Git 仓库（完整提交历史）；
- `README.md`：启动步骤、**迁移执行步骤**、`.env` 说明、已知欠账；
- `docs/decisions.md`：**本次课至少新增四条**，其中必须包含：
  - 为什么继续用同步栈（回收第 5 次课与今天 4.6）
  - `expire_on_commit=False` 的选择及其代价
  - `raiseload` 的使用范围（哪些查询用、哪些不用）
  - 每一处 `text()` 的理由
- `docs/nplus1.md`：N+1 扫描报告（见作业二）。

### 11.2 作业一：N+1 全项目扫描报告（B 档，必交）

对项目的**每一个 GET 端点**跑一遍 `scripts/count_sql.py`，填表：

| 端点 | 参数 | SQL 条数（前） | SQL 条数（后） | 传输行数（前） | 传输行数（后） | 做了什么修改 |
|---|---|---|---|---|---|---|

**必答四问**：

1. 哪个端点的 SQL 条数最多？那些多出来的 SQL **是从哪一行代码发出的**？（如果答案是"schema 里的某个字段"，请明确指出是哪个字段）
2. 把 `size` 从 20 改成 100，各端点的 SQL 条数怎么变？**哪些是线性增长的？**
3. 有没有哪个端点"SQL 条数很少但传输行数很大"？你怎么改的？
4. 你在哪些查询上加了 `raiseload("*")`，哪些没加？**说出你的判据。**

### 11.3 作业二：迁移链与一次真实的回滚（随 M2 交付）

1. 提交完整的 `migrations/` 目录；
2. 提交终端记录：`upgrade head` → `downgrade -1` → `upgrade head` 全过程；
3. **在一份有数据的库上**做一次"加 `NOT NULL` 列"的迁移，用三步式完成，提交迁移前后的行数/非空数对账：

   | 表 | 迁移前行数 | 迁移后行数 | 新列非空数 | 一致？ |
   |---|---|---|---|---|

4. 从你的迁移里挑一个 downgrade，说明**它是无损的还是有损的**，有损的话损失什么。

### 11.4 作业三：一处"改用 `text()` 的理由"（**本次课的课程主题作业**）

**第一部分：你自己的判断。**

在项目里找出（或构造）一条**你认为不该用 ORM 的查询**，提交：

| 项 | 内容 |
|---|---|
| 原始 SQL | |
| 你尝试的 ORM 写法 | **必须真的写一遍**，不许说"写不出来" |
| 两者的行数与可读性对比 | |
| 你的结论及依据（**引用单元 8.3 判据表的具体一行**） | |
| 四条 `text()` 纪律你各是怎么满足的 | |

**第二部分：AI 对照实验（必做）。**

1. 用这个提示词请 AI 生成一个迁移（原样使用，抄进作业）：

   > 我用 SQLAlchemy + Alembic。我要把 `questions` 表的 `body` 列改名为 `content`，并且新增一列 `slug`，它必须非空且唯一。请给我 Alembic 迁移脚本。

2. **原样保存** AI 的输出。

3. 回答：

   | 问题 | 你的回答 |
   |---|---|
   | 改名这一步它怎么写的？是 `alter_column` 还是 `drop`+`add`？ | |
   | 如果是后者，在十万行数据的库上执行会发生什么？**具体损失什么** | |
   | `slug` 这一列它怎么加的？有回填数据的步骤吗？在有数据的库上会成功吗？ | |
   | `downgrade` 它写了吗？写的那个是无损的还是有损的？ | |
   | 按单元 9.6 的分级，这份产物属于哪一类？你应该怎么处理它？ | |
   | 如果你只能给团队定一条"迁移脚本审读规则"，你定哪一条？ | |

4. 提交你改写后的正确脚本 + diff。

**评分重点是第 2、5、6 问。** 前面几问答对不难，能说清"为什么这类产物必须先读懂再执行"、并且给出一条**可执行的团队规则**，才说明你理解了本次课。

### 本次课新增的欠账登记

| 欠账 | 何时还 |
|---|---|
| SQL 计数变成测试断言 | **第 9 次课** |
| `grep commit` / `alembic check` / `downgrade` 验证进 CI | **第 9 次课** |
| 迁移在"带数据快照"上的 CI 验证 | **第 9 次课** |
| 乐观锁 / 悲观锁，彻底解决"先读后写" | **第 11 次课** |
| keyset 分页替代 OFFSET | **第 11 次课** |
| 全文检索替代 `ILIKE '%kw%'` | **第 11 次课** |
| 缓存与冗余列（`answer_count` 落成实列） | **第 11 次课** |
| SQL 注入完整演示（排序字段、`text()` 拼接） | **第 15 次课** |
| 零停机迁移（扩展-收缩） | **第 16 次课** |
| 连接池 × worker × `max_connections` 联合计算 | **第 16 次课** |
| `author_id=1` 硬编码仍在 | 第 14 次课 |
| Alembic 多 head 的协作处理 | 课后自读 |
| 软删除的 ORM 结构化做法 | 课后自读 |
| 批量插入的高性能写法 | 课后自读 |

---

## 十二、素材清单与制作说明

### 必需素材

| 素材 | 说明 |
|---|---|
| tag `v7-broken` | 起始版：AI 产出的 ORM 代码，含三个问题（N+1 / 到处 commit / 排序拼接）。**三个问题必须稳定复现** |
| tag `v7-models` | 单元 4 结束：模型 + Session 依赖 |
| tag `v7-nplus1` | 单元 5 阶段①（用于学生对照） |
| tag `v7-eager` | 单元 5 阶段③ + `raiseload` |
| tag `v7-tx` | 单元 7 结束：commit 收到 1 处 |
| tag `v7-m2` | M2 参考交付状态 |
| `app/sqlcount.py` | SQL 计数器（事件监听）。**第 9 次课复用，请统一设计** |
| `scripts/count_sql.py` | 命令行版，`--url --size --rtt`；输出 SQL 条数 / 传输行数 / 耗时 / SQL 摘要 |
| `migrations/` | 完整迁移链，含三个脚本，**每个都带审读注释** |
| **带数据的数据库快照** | `pg_dump` 文件，10 万问题。**单元 9 的"在有数据的库上跑迁移"必须用它** |
| `scripts/check_layering.sh` | 扩展前几次课版本，新增 M2 的第 2、4、5、8 条检查 |
| **封面级 A** | 单元 5.7 四阶段数据表（`201` / `2400ms` 红，`1847` 橙） |
| **封面级 B** | 单元 5.2 "41 条 SQL 从哪来"三行表，第三行标"不在任何 Python 代码里" |
| **封面级 C** | 五道结构性护栏累加表 |
| **封面级 D** | 单元 7.2 半截数据时序图 |
| **封面级 E** | 单元 9.2 改名实验左右对照（`drop_column` vs `alter_column`） |
| **封面级 F** | 单元 9.2 autogenerate 盲区清单（八行） |
| **封面级 G** | 单元 9.6 生成物分级四行表 |
| 高光图 H | 单元 3.2 Unit of Work 四步展开图 |
| 高光图 I | 单元 4.5 两层 cascade 对照表 |
| 高光图 J | 单元 4.6 第 4 次课预测验证表 |
| 高光图 K | 单元 5.4 Out schema → 加载策略 箭头图 |
| 高光图 L | 单元 6.2 `joinedload` 行数放大示意 |
| 高光图 M | 单元 8.1 SQL/ORM 左右分栏（五条） |
| 高光图 N | 单元 8.3 何时放弃 ORM 判据表 |
| 高光图 O | 单元 9.3 三步式迁移图 |
| 高光图 P | 单元 9.4 两层可回滚 + 扩展收缩两次发布 |
| 截图 | `grep -c commit` 的 15 → 1 |
| 截图 | 半截数据的两条 SQL 结果 |
| 截图 | `lazy="raise"` 报错；`DetachedInstanceError` 报错 |
| 截图 | autoflush 导致 `IntegrityError` 报在 `select` 那一行 |
| 截图 | `?sort=(SELECT count(*) FROM users)` 修复前能用 / 修复后 422 |
| 截图 | `alembic_version` 表内容 |
| 截图 | 加 `NOT NULL` 列的 `NotNullViolation` |
| 截图 | `downgrade -1` → `upgrade head` 终端输出 |
| 截图 | seed 里最热门问题的回答数（1600+） |

### 可后补

- ORM 跨栈对照表、一句话结论卡（纯文字）。
- 完整 `models.py`（代码已在文中）。

### 备用材料

| 风险 | 备用方案 |
|---|---|
| **N+1 在本机差距不够大，说服力不足**（最高风险） | `count_sql.py` 的 `--rtt` 参数是**必需功能**，不是可选；另备预录 90 秒实验录像。**若只能保留一个数字，保留"SQL 条数"而不是耗时** |
| seed 数据里没有"热门问题"，单元 5.6 的 1847 行演示不出来 | `seed_large.py` 必须显式制造 3 条回答数 >1000 的问题，**固定随机种子** |
| `alembic autogenerate` 在学生环境生成的脚本与底稿不一致 | 提供 `migrations/` 的参考版本；**改名实验请录一份预录视频**，因为它是本单元最关键的演示 |
| 学生的库已经被前几次课改得不一致，`autogenerate` 产生一堆噪音 | 提供 `make reset-db-v7`：drop → restore 带数据快照 → `alembic stamp` 到指定版本 |
| AI 现场调用失败（作业三演示） | 准备一份预先生成并验证的"drop+add 改名"迁移脚本作为讲评素材，标注"预录产物" |
| 时间超支 | 按单元〇的压缩顺序执行；单元 8 的第 4、5 条翻译有自读材料 `docs/orm_translate.md` |

### 环境与运行条件

延用前序环境。**新增依赖**：`alembic`。

**演示开始时的初始状态**：工作区在 tag `v7-broken`；**数据库已从带数据快照恢复**（10 万问题 / 30 万回答 / 含 3 条热门问题）；服务以 `--workers 1` 启动；`echo` 通过 `.env` 的 `SQL_ECHO` 控制，**默认关闭**（单元 5 才打开）；另开一个终端在 `psql` 里。

**复位方式**：`make reset-db-v7`（约 60 秒）。

---

## 十三、与前后课的衔接

**本次课回收的前序埋点**：

| 来源 | 埋点 | 回收位置 |
|---|---|---|
| 第 3 次课 | `response_model` / 契约先行 | **单元 5.4**（Out schema 决定加载策略） |
| 第 3 次课 | 入口闸门 | 单元 8.4（`Literal` 挡住非法排序键） |
| 第 4 次课 | 零 `commit()` 在 routers/services | **单元 7**（ORM 版重新做一次） |
| 第 4 次课 | 作业二第三行：换数据访问技术栈要改哪些文件 | **单元 4.6 验证预测** |
| 第 4 次课 | `lifespan` 管进程级资源 | 单元 4.1（`engine.dispose()`） |
| 第 4 次课 | 依赖的价值与复用次数成正比 | 单元 4.4（`SessionDep` 类型别名） |
| 第 4 次课 | 统一错误契约 | 单元 7.3（与事务回滚配合） |
| 第 5 次课 | worker × 连接池 × max_connections | 单元 4.1（写出算式） |
| 第 5 次课 | 异步是全链路的，换栈成本高 | **单元 4.6**（用 `repositories/` 的代码量具体化这个成本） |
| 第 5 次课 | 五道护栏中的前三道 | 单元 5.8（加上第五道 `lazy="raise"`） |
| 第 5 次课 | "约定 + 机械检查 + 定量兜底"三层 | 单元 9.6（用在迁移审读上） |
| 第 6 次课 | 约束下推到数据库（第四道护栏） | 单元 4.2、4.5（`server_default`、两层 cascade） |
| 第 6 次课 | 默认 `NOT NULL` | 单元 4.2（`Mapped[str]` vs `Mapped[str \| None]`） |
| 第 6 次课 | 每个约束显式命名 | 单元 4.3（`naming_convention` 让它结构化） |
| 第 6 次课 | 稳定排序必须带主键 | 单元 8.1 #1 |
| 第 6 次课 | `LEFT JOIN` 后用 `count(附表主键)` | 单元 8.1 #2 |
| 第 6 次课 | 4.7 三步清洗流程 | **单元 9.5**（写成迁移，含有损 downgrade） |
| 第 6 次课 | "先读后写在并发下不可靠"（三个实例） | 单元 7.6（第四个实例 + `ON CONFLICT` 修法） |
| 第 6 次课 | 排序字段白名单 | **单元 8.4** |
| 第 6 次课 | 索引在 N+1 面前无效 | **单元 5.7 观察二**（41 条 SQL 每条都走了索引） |
| 第 6 次课 | 8 条业务 SQL | **单元 8**（5 条翻译 + 2 条不翻译） |

**本次课埋下、后面必须回引的五处**（请在课件中明显标记）：

- **单元 5.1 的 SQL 计数器** → 第 9 次课变成测试断言，是"把性能问题变成会失败的测试"的样板；
- **单元 7.6 的 `get_or_create` 与四个 TOCTOU 实例** → 第 11 次课统一用乐观锁/悲观锁收口；
- **单元 9.4 的扩展-收缩** → 第 16 次课零停机发布；
- **单元 9.6 的三层护栏（尤其"在带数据快照上跑迁移"）** → 第 9 次课写成 CI 步骤；
- **单元 8.4 的排序拼接修复** → 第 15 次课从这里出发做完整的注入演示（"如果我们没修会怎样"）。

**本次课不承担、请勿提前引入**：测试与 `dependency_overrides`（第 9 次课）、缓存与 keyset 分页与并发控制（第 11 次课）、认证（第 14 次课）、注入/XSS/CSRF 演示（第 15 次课）、部署与零停机迁移（第 16 次课）、异步 ORM（不做）、数据库内核（全课程不讲）。

**给第 8 次课的提示**：

本次课结束时，项目有两套并存的客户端——第 5 次课的 HTML 表单页面和一直存在的 JSON API，**它们共享同一套 `services/` 和 `repositories/`**（第 5 次课单元 8.6 那张对照表已经埋好）。

第 8 次课讲前后端分离时，有两个现成的抓手：

1. **那张 JSON vs HTML 对照表可以直接拿来问"分离到底改变了哪几行"**——答案是只有最上面四行，业务层完全不变。这让"分离"从一个架构口号变成一个可以数清的改动范围。
2. **今天的 `QuestionOut` 嵌套结构 + 加载策略的绑定关系，是"契约决定实现成本"的最好例子**。前端多要一个嵌套字段，后端就要多一次 eager load——**第 8 次课讨论"前端说要什么后端就给什么"的代价时，这是一个有数字支撑的论据**（单元 5.7 的表）。