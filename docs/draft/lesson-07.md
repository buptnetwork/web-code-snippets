# 第 7 次课教学底稿（第四版）
## ORM 入门：保存、查询与它发出的 SQL ｜ 交付 M2

> **备课基线**：[第四版大纲](../syllabus-v4.md)第 7 课与[第 6 课交接](lesson-06.md#83-第-7-课接收的明确基线)。本稿尚未移交归档；它定义教学内容与配套工程规格，不代表独立 M2 工程、迁移文件、教师脚本和最终课件已经交付。文中模块名、命令和阶段名须在制作包中落地后才能作为学生入口。

## 〇、这次课学会什么

**讲给学生的目标句**：你能用 ORM 存一条、查一条数据，并指着日志说出它发了哪些 SQL、什么时候写进数据库。

核心解释目标只有一个：**ORM 什么时候发 SQL、什么时候提交。** 模型、Session、查询、关系加载与迁移围绕这条主线展开。先看正确的保存与回读，再解释未提交可见性和 N+1；不从三个坏例子、性能调优或复杂迁移开场。

### 95 分钟教学 + 5 分钟缓冲

| 分钟 | 教学单元 | 当场产出 |
|---|---|---|
| 5 | 四个入门问题 | 说清 ORM 的作用和不负责的事 |
| 13 | 模型与 Session 在链路中的位置 | 对照一张表、一个对象、一个请求 |
| 20 | 教师存／查／改与事务演示 | SQL 轨迹、同／异连接可见性、两种 500 的数据结果 |
| 25 | 学生迁移列表端点 | 响应不变的查询、自己的写法选择和测试输入 |
| 15 | 教师引导 N+1 对照 | 同响应、不同查询次数与原因 |
| 10 | Alembic 空库建链与 upgrade | 基线版本、五表与正常读写核对 |
| 7 | 写法卡、解释检查与 M2 交接 | 一个作业包的验收清单 |
| **95** | **教学合计** | **另留 5 分钟缓冲，共 100 分钟** |

本课**不安排计分小测**；末尾三问只是课堂解释检查，不另加 15 分钟。超时先压缩完整模型／配置的逐行阅读，保留学生的 25 分钟、两种故障的位置解释与 N+1 同契约核对。

### 三处读写，谁负责什么

| 提供物或任务 | 谁完成／标注 | 理解与验收边界 |
|---|---|---|
| 列表 ORM 实现 | 学生，课堂独立完成 | 在固定契约下选择查询组织方式，不设计新接口 |
| 详情 ORM 实现 | 学生，课后独立完成 | 复用 DTO／加载帮助函数，保留 404／422 |
| 创建 ORM 服务 | 教师基线，**要求解释** | 解释 add、flush、服务 commit、失败 rollback；不追加学生从零写服务任务 |
| 五表模型与 DTO 帮助函数 | 教师提供，要求会用；课堂展开的映射／关系要求解释 | 不默写五表；关联表的 position 必须会保留 |
| Session 依赖与异常出口 | 教师接好，**要求解释** | 依赖只提供／关闭；端点只翻译 HTTP；服务拥有业务事务 |
| 故障脚本与 SQL 计数入口 | 教师提供，**要求会用** | 会选择阶段、读日志、独立查库；不用编写注入／监听设施 |
| Alembic 配置与基线命令 | 教师提供，**要求会用** | 确认目标空库、运行与核对结果，不考 env.py 内部 |
| 库复位、连接配置、扩展 seed | 教师设施，**黑盒** | 不改内部，不进口试；只操作标记的虚构数据副本 |

前置卡：第 6 课五表、Python 类与属性、第 4 课服务层显式提交、第 5 课 JSON／HTML 分流。换 ORM 不等于“只改依赖一行”：查询表达、返回类型和异常包装也变了；分层限制修改范围，不消除这些工作。

## 一、四个入门问题：先给一条正常路径

**课堂 5 分钟。**

| 问题 | 本课答案 |
|---|---|
| 为什么需要 ORM？ | 用对象组织数据访问，减少反复把一行拆成字典、再组装对象的工作 |
| 最少认识什么？ | 模型类、Session、查询、事务 |
| 正常怎么用？ | 创建对象 → add → 服务 commit → 新 Session select 查回 → 改属性 → 服务 commit |
| 它负责什么、不负责什么？ | 负责 SQL 构造、映射与工作单元；不替代业务规则、数据库约束，也不保证查询高效 |

```text
JSON / HTML → 输入模型 → 业务服务 → Session → SQL → PostgreSQL
                    服务 commit 成功 → DTO → 201 / 303
依赖提供 Session ───────────────────────────→ 最终 close
```

本课同步 SQLAlchemy 2.0 + psycopg 3，教学目标 PostgreSQL 16／UTF-8；同步 `def` 端点运行同步服务。Session 每请求独立，不跨线程或并行任务共用；engine／sessionmaker 可以复用，Session 不是全局缓存。

**先保留能工作的 M1。** 列表、详情和创建共同使用五字段 `id/title/body/tags/created_at`；列表外壳仍是 `items/total/page`。作者和回答数留在数据库与独立实验中，不因访问 ORM 关系就自动进入公开 DTO。

## 二、模型、Session 和对象分别在做什么

**课堂 13 分钟。约 5 分钟映射，4 分钟 Session，4 分钟关系和资源边界。完整五表放 §九，课堂只展开 Question 的关键列和 answers 关系。**

### 2.1 一张表与一个模型类

- `Question.__tablename__` 对应 questions；一条记录映射成一个 Question 对象。
- `Mapped[int]` 是属性类型，`mapped_column(BigInteger, primary_key=True)` 描述主键列；本例在 PostgreSQL 上使用自增序列，与第 6 课 BIGSERIAL 基线对应。
- `Mapped[int | None]` 可推导可空，显式 nullable 配置仍可覆盖；不能看到 Python 注解就忽略真实 DDL。
- `relationship` 是对象导航／加载规则，不是新数据库列。`question.answers` 首次读取可能发 SELECT。
- `server_default=func.now()` 是数据库默认，沿用事务开始时间；不是 Python 构造对象时必然已有时间。INSERT／flush 后由 RETURNING 取得 id／时间。

第 6 课关联表有 position，因此本课把它映射成 **QuestionTag 关联对象**，不是丢掉 position 的普通 secondary 多对多列表。按 position 读取标签，不能改成字母排序。完整模型保留五个非延迟、默认 NO ACTION 外键；不加入 ORM 删除级联绕过第 6 课的删除规格。

### 2.2 三种状态，不能合成一句“保存了”

| 操作 | 框架做了什么 | 不能推出什么 |
|---|---|---|
| 构造对象／改属性 | 改变 Python 内存 | 不表示已经发 INSERT／UPDATE |
| session.add | 让 Session 跟踪新对象 | 不保证此刻已经发 SQL |
| session.flush | 把待写变更发送到当前事务，可取得生成键 | 不等于已提交；可能因约束失败 |
| session.commit | 必要时 flush，随后尝试提交 | 不是所有失败都能断言没有写入 |
| session.rollback | 撤销仍未提交的事务，恢复失败 Session 的可用状态 | 不能撤销已经确认提交的数据；序列消耗也不回滚 |
| session.close | 结束使用、释放资源，未提交工作不会因此被提交 | 不是成功提交入口 |

本课 Session 使用默认 `autoflush=True`。**ORM select** 等操作会在需要时触发 autoflush；不是任意原生 SQL、任意属性读取都触发它。commit 即使关闭 autoflush 也仍会 flush。

同一 Session 的 identity map 通常让同一主键对应同一对象；再次 get 一个未过期对象可以不发 SQL。普通条件 SELECT 仍可执行查询。当前内存对象的值、当前事务里的行、另一个连接可见的行是三个不同观察点。

### 2.3 资源依赖不接管提交

教师在独立包配置 settings，数据库 URL 使用 `postgresql+psycopg` 驱动。配置／连接池细节为参考层，课堂认识工厂与一次资源生命周期即可。

```python
# lesson07: resources
from typing import Annotated, Iterator
from fastapi import Depends
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker


def make_session_factory(database_url, *, echo=False):
    engine = create_engine(
        database_url, echo=echo, pool_pre_ping=True,
        isolation_level="READ COMMITTED",
    )
    return engine, sessionmaker(bind=engine, expire_on_commit=False)


def get_session() -> Iterator[Session]:
    with SessionLocal() as session:
        yield session


SessionDep = Annotated[Session, Depends(get_session)]
```

工程启动时以配置调用 `engine, SessionLocal = make_session_factory(...)`，关闭工程时 dispose engine。`with SessionLocal()` 这里只负责关闭，不自动 commit；不在 yield 退出时提交。读请求结束可关闭仍打开的只读事务，不为了“每请求都有 commit”加无意义写提交。

`expire_on_commit=False` 便于本课观察已加载属性，但未加载关系仍可能在访问时发 SQL。公开响应在 Session 可用时构造为独立 Pydantic DTO，不把裸 ORM 对象交给关闭后的序列化流程。pre_ping 不能保证执行中的事务永不掉线。

## 三、教师演示：存一条、查一条、改一条

**课堂 20 分钟。约 8 分钟正常存／查／改，5 分钟可见性预测，7 分钟两组故障及解释。**

### 3.1 完整创建基线：服务显式提交

教师给定第 3 课 QuestionCreate／QuestionOut、第 4 课 DuplicateTitle／QuestionNotFound。输入依旧 title/body 先 strip 后检查 5–200／10–20000，tags 最多五个字符串、默认 []，拒绝额外字段。第 6 课开始的标签精确去重保持首次顺序，先验证原输入最多五项，再去重；六个重复值仍 422。

以下是**要求解释的正常服务**。`after_flush/after_commit` 为教师测试注入点，默认不做事；不从 URL、表单、JSON 或生产配置开放，学生只运行教师脚本，不开发注入工具。

```python
# lesson07: create_service
from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.exc import IntegrityError


def no_fault():
    pass


def get_or_create_tag_id(session, name):
    statement = (
        insert(Tag).values(name=name)
        .on_conflict_do_nothing(constraint="tags_name_key")
        .returning(Tag.id)
    )
    tag_id = session.scalar(statement)
    if tag_id is None:
        tag_id = session.scalar(select(Tag.id).where(Tag.name == name))
    if tag_id is None:
        raise RuntimeError("标签状态已变化")
    return tag_id


def write_question(session, payload, *, author_id):
    question = Question(title=payload.title, body=payload.body, author_id=author_id)
    session.add(question)
    session.flush()
    for position, name in enumerate(dict.fromkeys(payload.tags), start=1):
        tag_id = get_or_create_tag_id(session, name)
        session.add(QuestionTag(question_id=question.id, tag_id=tag_id, position=position))
    return question


def create_question_service(
    session, payload, *, author_id, after_flush=no_fault, after_commit=no_fault,
):
    try:
        question = write_question(session, payload, author_id=author_id)
        session.flush()
        after_flush()
        result = read_question_dto(session, question.id)
        if result is None:
            raise RuntimeError("创建后的回读缺失")
        session.commit()
        after_commit()
        return result
    except IntegrityError as exc:
        session.rollback()
        original = exc.orig
        constraint = getattr(getattr(original, "diag", None), "constraint_name", None)
        if getattr(original, "sqlstate", None) == "23505" and constraint == "questions_title_key":
            raise DuplicateTitle() from exc
        raise
    except Exception:
        session.rollback()
        raise
```

read_question_dto 的教师参考在 §4.4；write_question 与标签辅助函数**都不提交**。业务成功包括问题、标签、关联、DTO 回读校验；一次服务 commit 在它们之后。author_id 来自教师虚构用户配置（本课为 1），不接受客户端作者字段，不宣称已有登录授权。

标签使用 PostgreSQL ON CONFLICT，不采用不受约束保护的“先查再插”。这是教师提供的并发帮助函数：READ COMMITTED、无并发删除／改名时，等待冲突完成后的下一条 SELECT 能见到已提交标签。多标签交错仍可能死锁，不承诺自动重试或全部请求成功；复杂竞争分析不进本课考核。

**正常观察**：以合法标题、正文和 `["python", "sql"]` 创建；记录 INSERT questions、标签插入／读取、INSERT question_tags、回读、COMMIT 的顺序。RETURNING 取回主键不一定另发 SELECT。不同批量组织方式可能改变写语句次数，课堂不背固定 INSERT 条数。

### 3.2 查回后改属性，UPDATE 从哪里来

下面是教师隔离演示服务，不新增公开更新端点；真实 PATCH 留给第 8 课。payload 仍使用同一已验证输入模型，本演示只取其中 body。

```python
# lesson07: update_demo

def update_body_demo_service(session, qid, payload):
    try:
        question = session.get(Question, qid)
        if question is None:
            raise QuestionNotFound()
        question.body = payload.body
        session.flush()
        result = read_question_dto(session, qid)
        session.commit()
        return result
    except Exception:
        session.rollback()
        raise
```

演示从新 Session 查刚创建的记录 → 改正文 → 暂停看内存 → flush 看 UPDATE → commit → **另开连接**按 id 核对。没有手写 UPDATE，是 Session 根据被跟踪对象的变化生成；只看同一对象值变了不能证明数据库已提交。

### 3.3 观察点一：add 之后、commit 之前，谁能查到

**先给条件再预测**：空闲的新 Session A，默认 autoflush=True、READ COMMITTED；已存在作者 1，新标题合法且不冲突；add 后尚未 flush/commit，无其他写入。A 执行 `select(Question).where(Question.title == 新标题)`；B 是另一条独立数据库连接，只查相同标题。两边分别看到什么？

```python
# lesson07: visibility_probe

def add_and_query_probe(session, payload, *, author_id):
    question = Question(title=payload.title, body=payload.body, author_id=author_id)
    session.add(question)
    found = session.scalar(select(Question).where(Question.title == payload.title))
    return question, found
```

| 时刻 | A：同一 Session／事务 | B：独立连接的查询 |
|---|---|---|
| 只 add，尚未查询 | 对象已在内存，尚无 INSERT | 看不到新行 |
| A 执行上述 ORM select | 先 autoflush 发 INSERT，再 SELECT，找到同一对象 | 看不到未提交行 |
| A 明确 commit 后 | 已提交 | READ COMMITTED 的下一条查询能看到 |
| 若 A 改为 rollback | 本次行不存在，可能留下序列间隙 | 始终看不到本次行 |

教师探针只用于隔离实验，不是公开服务。若用 `session.no_autoflush` 包住 select，未插入的新行通常查不到，不能把 identity map 当条件查询缓存。B 不能偷偷复用 A 的连接；REPEATABLE READ 已建立快照时的结果不在此题条件内。

### 3.4 观察点二：都是 500，为什么数据库结果不同

先跑正常创建，再运行**两条不同合法标题**的教师故障请求，每次从受控基线开始。故障是本地固定 RuntimeError，不是输入 422、标题冲突或真实网络断连；HTTP 响应均尚未启动。

| 脚本阶段 | 精确注入点 | HTTP 预期 | 事务结束后独立连接核对 |
|---|---|---|---|
| before_commit | 最后一次 flush 已成功，服务 commit 还未调用 | 500，沿用安全错误出口 | 无本次问题、新标签、关联；原有标签不受影响 |
| after_commit | 服务 commit 已确认成功返回，DTO 已构造，响应启动前 | 500，沿用安全错误出口 | 问题、标签和关联仍存在 |

教师在对应回调抛错；两者都会进入服务 except 中的 rollback，但第二次 rollback **不能撤销已提交的事务**。运行脚本须保留 request-id、触发阶段、HTTP 状态和独立查询结果；不能用测试夹具最后统一回滚来“证明”没有写入。

提交期间断连、确认丢失是**结果未知**，既不能保证已写也不能保证未写。这两个开关不模拟它；不能看到 500 就自动重发。已知标题唯一冲突才是业务 409，其他完整性错误不统一改成 409／422。输出模型校验失败位于服务内部，应为 500 并在提交前回滚，不冒充输入 422。

## 四、学生任务：只替换列表实现，不改变响应

**课堂 25 分钟。建议 4 分钟读固定契约，12 分钟写查询，6 分钟运行对照，3 分钟保存自己的选择与证据。**

### 4.1 起点包必须已经能正常工作

教师提供：完整五表模型、真实 Session 依赖、创建完成版、正常 SQL 列表／详情基线、输入／输出模型、异常出口、HTML 页面、按 position 映射标签的 DTO 帮助函数、固定数据与回归入口。学生只替换列表数据读取函数，路由接线由教师预留。

**过渡期规则**：完成版统一用 Session；若起点详情仍保留 psycopg SQL，它使用独立的原连接依赖，不能把 Session 当作 psycopg Connection 调旧函数。两者连接同一教学库，各自清理。课后详情换好后再去掉该过渡分支，不把驱动适配变成隐藏任务。

| 契约项 | 不变的要求 |
|---|---|
| 参数 | keyword 默认空；page 默认 1 且 ≥1；page_size 默认 20，范围 1–50 |
| 搜索 | keyword.strip()；标题或正文的字面子串；既有英文样本不区分大小写，%／_ 不是通配符 |
| 次序 | **id DESC** 后分页；不是第 6 课 Q2 的 created_at 排序 |
| 数量 | total 为过滤后、分页前总数；page 原样回显；空页允许 total 非零 |
| 输出 | items 中每项五字段；tags 精确去重且保持 position 次序，允许空列表／空字符串标签 |
| 错误 | 参数不合法 422；无匹配列表 200，不是 404；四字段 JSON 错误不变 |

先核对第 6 课固定 seed：公开列表 page_size=2，第一页 **104、103**，第二页 **102、101**，total=4；搜索 `"  PYTHON  "` 或 `"%"` 都只命中 101。这与课堂时间排序第一页 103、102 不同，是特意保留的契约区别。

### 4.2 学生的小决定与任务壳

学生可决定：把 where 条件单独组织为函数还是内联；将查询与服务分离还是保留一个读取函数；自己选一组能区分正确／错误实现的关键词或空页输入。不得改变排序、字段、标签次序或参数上限。

任务壳只给四步提示，不给新的业务设计题：① 同一个搜索条件；② 计数；③ id 倒序、offset、limit；④ 用教师 DTO 帮助函数组装外壳。标签加载帮助函数已提供，不要求在 N+1 讲解之前独立设计加载策略。

完成后再展示参考：

```python
# lesson07: queries
from sqlalchemy import func, literal, or_, select
from sqlalchemy.orm import joinedload, selectinload


def tag_load_option():
    return selectinload(Question.tag_links).joinedload(QuestionTag.tag)


def question_to_dto(question):
    return QuestionOut(
        id=question.id, title=question.title, body=question.body,
        created_at=question.created_at,
        tags=[link.tag.name for link in question.tag_links],
    )


def search_condition(keyword):
    needle = func.lower(literal(keyword.strip()).collate("C"))
    return or_(
        func.strpos(func.lower(Question.title.collate("C")), needle) > 0,
        func.strpos(func.lower(Question.body.collate("C")), needle) > 0,
    )


def list_questions_orm(session, *, keyword="", page=1, page_size=20):
    condition = search_condition(keyword)
    total = session.scalar(select(func.count()).select_from(Question).where(condition))
    statement = (
        select(Question).where(condition).options(tag_load_option())
        .order_by(Question.id.desc())
        .offset((page - 1) * page_size).limit(page_size)
    )
    items = [question_to_dto(q) for q in session.scalars(statement).all()]
    return QuestionListOut(items=items, total=total, page=page)
```

这是**已校验参数之后**调用的读取函数，page/page_size 范围由原路由／适配层检查，不把函数当输入校验器。列表 count 和页查询使用同一条件；SQLAlchemy 绑定值防止值成为语法，strpos 负责字面子串，两者目的不同。仍只承诺既有英文大小写口径，不新承诺所有语言的 Unicode casefold。

教师解释 tags 帮助函数：一次批量取当前页关联，关联中 JOIN 单个标签；关系自身 `order_by=QuestionTag.position` 保证顺序。普通非空页通常是 count、问题、标签关联三类 SELECT；无标签的父行仍保留。不是直接 JOIN 两个集合后再 LIMIT，以免一页的问题数量被展开行影响。

两条 SQL 在 READ COMMITTED 下不承诺相同快照；课堂对比固定数据、没有并发写入。稳定 id 排序也不解决 OFFSET 跨请求遇到插删后的漂移。

### 4.3 正常接线与回归，不新增学生端点

教师 JSON 路由示意如下；完整包继续使用原 response_model、异常处理和 request-id 中间件，HTML 列表也调用同一读取函数。

```python
# lesson07: list_route
from fastapi import Query


@router.get("/questions", response_model=QuestionListOut)
def list_questions(
    session: SessionDep,
    keyword: str = "",
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=50),
):
    return list_questions_orm(session, keyword=keyword, page=page, page_size=page_size)
```

自己先写，再让 AI 做同一列表。对照它的 where、JOIN／加载、分页和 DTO：语句少是否只是漏字段？直接 JOIN 回答是否改变行粒度？合理方案可以保留，不要求 AI 必须犯错，不因用了另一种正确写法扣分。

### 4.4 详情是课后独立迁移，参考答案供核对

起点包提供函数壳与行为规格；学生独立完成按 qid 查询、加载标签、构造 DTO、缺失返回业务 404。下面的帮助函数也供教师创建服务回读使用，不能让创建基线依赖学生课后才写好的功能。

```python
# lesson07: detail_reference

def read_question_dto(session, qid):
    statement = select(Question).where(Question.id == qid).options(tag_load_option())
    question = session.scalar(statement)
    return None if question is None else question_to_dto(question)


def get_question_service(session, qid):
    result = read_question_dto(session, qid)
    if result is None:
        raise QuestionNotFound()
    return result
```

qid 只要求整数，不能额外加 ge=1：不存在的 0／负整数同样业务 404；非整数由入口校验为 422。列表、详情、创建与 HTML 必须回读同一数据表示，不给详情偷偷加作者、回答数或数据库内部字段。

## 五、N+1：一个关系访问为什么变成很多查询

**课堂 15 分钟，教师引导。4 分钟固定条件与预测，4 分钟 lazy，4 分钟 selectin，3 分钟核对和解释。不是第二个学生从零编码大任务。**

### 5.1 独立实验契约与种子

独立本地路径约定 `/lab/orm/questions`，不替代 `/questions`，不进入主 API 的 OpenAPI。两个策略共用响应：

```json
{"items":[{"id":101,"title":"示例标题文字","answer_count":3}]}
```

这是形状示意，不是 20 条数据的实测响应。教师提供 **20 个问题**的隔离 seed，id=1001–1020：按 `id % 3` 分配 0／1／2 条回答，含零回答和未知作者；总计 20 条回答。没有作者／标签读取、没有 total 计数、无其他并发数据库活动。初始化、连接预热和 seed 在计数外。

### 5.2 观察点三：同响应，查询从 21 条变 2 条

**先预测**：每轮新 Session，无预加载；默认 lazy 的 Question.answers 集合；每页 20 个问题，selectin 一批内完成。仅测下面函数从 SELECT 到 DTO 构造；两个策略 SQL 各几条，响应是否相同？

```python
# lesson07: nplusone

def read_answer_counts_lab(session, *, strategy, page_size=20):
    statement = select(Question).order_by(Question.id.desc()).limit(page_size)
    if strategy == "selectin":
        statement = statement.options(selectinload(Question.answers))
    elif strategy != "lazy":
        raise ValueError("未知实验策略")
    questions = session.scalars(statement).all()
    return {"items": [
        {"id": q.id, "title": q.title, "answer_count": len(q.answers)}
        for q in questions
    ]}
```

| 阶段 | 数据库动作 | 上述非空 20 行条件下的 SELECT |
|---|---|---:|
| 只查问题，不访问回答 | 一次 SELECT questions；尚未满足实验响应 | 1，仅为中间观察，不能作为等价实现交付 |
| lazy 完整响应 | 一次问题查询，每个问题访问 answers 时再查一次 | 1+20=21 |
| selectin 完整响应 | 一次问题查询，一次按问题 id 集合查询回答 | 2 |

两完整阶段 JSON 必须相同，包括零回答为 0、顺序不变。即使结果没有回答，lazy 查询也要执行才能知道是空；多对一作者的 identity map 复用规律不能直接套到这里的每个父对象集合。

若只用第 6 课四个问题，计数应为 5／2，不是 21／2；空结果是 1／1。把 total、标签或其他读取加入响应后要重新分类计数。不要硬写“所有列表最多两条 SQL”；本课公开列表还要总数和标签。

### 5.3 教师计数设施：执行事件不是日志行数

```python
# lesson07: sql_counter
from contextlib import contextmanager
from sqlalchemy import event


@contextmanager
def count_sql(engine):
    statements = []
    def before_execute(conn, cursor, statement, parameters, context, executemany):
        statements.append(statement)
    event.listen(engine, "before_cursor_execute", before_execute)
    try:
        yield statements
    finally:
        event.remove(engine, "before_cursor_execute", before_execute)
```

echo 用于指认 SQL；教师脚本用执行事件计数，包住**查询和 DTO 构造**，不只包主 SELECT。HTTP 版本用同进程、专用 engine 的 TestClient，监听包住整个请求；外部 curl 不能在自己的进程监听另一个服务的 engine。监听期间不并发访问，否则会混入其他请求。

本事件不等于网络往返／行数／事务日志统计；BEGIN／COMMIT 不一定以 cursor SQL 事件出现。固定实验里记录的是 SELECT 类执行次数，不拿 echo 的日志行数当条数，不据一次耗时宣称性能提升倍数。

预加载减少这些按父行增长的查询，但仍加载了完整回答对象。若只需计数，聚合投影可避免加载正文，作为参考选项，不增加第三个必交阶段。joinedload 集合通常需要 `.unique()`，可能增加传输行数；多对一 JOIN 与集合 JOIN 不混为一谈。raiseload、复杂计划分析与全仓扫描是拓展，不进本课基础验收。

## 六、Alembic：让另一个空环境得到同样的五张表

**课堂 10 分钟。2 分钟确认目标，3 分钟审读教师基线，3 分钟 upgrade／核对，2 分钟说明边界。模板标注「要求会用」。**

### 6.1 本课只有一条必要迁移

本课选择 `001_baseline`，**head 就是第 6 课五表结构**。不改 questions.body 的数据库列名，不新增状态、浏览量、投票、角色或密码列，不强制做第二条迁移或回退。第 8 课再为自己的新增字段建立下一条迁移，不依赖旧稿的正文改名链。

教师提供初始化好的 migrations 配置、已审读的固定基线与命令卡。若展示生成过程，只在额外空库执行 autogenerate，并在执行前核对候选；学生不在已有五表的 M1 数据库上生成一个空 init 充当基线。

```text
当前连接库的结构 ← autogenerate 比较 → 已导入的 Base.metadata
                    生成候选，仍需人工审读
固定的 001_baseline + 空库 → upgrade → 五张业务表 + alembic_version
```

模型描述目标，迁移记录如何到达；修改模型不会自动改现有表。`create_all()` 不是迁移替代品，不能先用它建表再宣布“空库 upgrade 成功”。autogenerate 对 CHECK、重命名等的检测有边界，不能用一条 check 命令替代结构／数据核验。

### 6.2 命令卡与成功判据

在教师独立 Python 工程、已安装锁定 Alembic 的环境执行；不是本 Slidev 根目录的即用命令。教师先确认目标是**独占的可丢弃空库**，不打印带密码 URL。

```bash
uv run --no-sync alembic current
uv run --no-sync alembic upgrade head
uv run --no-sync alembic current
```

第一次 current 应无已应用 revision；升级后为 001_baseline。重复 upgrade head 无新变更。核对五表的列／可空性／默认／命名约束／五个 NO ACTION 外键／position 顺序约束；alembic_version 是迁移管理表，不是第六张业务表。

**基线不含 seed。** 空库升级后先看表，再运行教师的第 6 课虚构 seed 和序列校准，随后正常 ORM 创建、列表、详情回读。若未插作者 1 就写问题，外键失败是合理结果，不是 ORM 不会存。版本表存在也不等于数据已导入。

已有 M1 PostgreSQL 数据库只在备份副本走教师核对流程：与空库基线逐项匹配，才可 stamp 001_baseline；stamp 只记版本，不执行建表、不导入、不修约束。**不能对已有五表直接跑创建五表的 upgrade，也不能用 stamp 掩盖结构差异。** 此流程由教师课前处理，不追加学生现场数据库修复。

### 6.3 固定基线主体参考

以下是教师参考迁移文件的完整主体，保留 revision 元数据；不 import 会继续变化的业务模型。配置参考在 §9.2。学生会运行并检查结果即可，基线制作／生成细节不进口试。

```python
# lesson07: migration_baseline
from alembic import op
import sqlalchemy as sa

revision = "001_baseline"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "users",
        sa.Column("id", sa.BigInteger(), primary_key=True),
        sa.Column("display_name", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.CheckConstraint("char_length(display_name) BETWEEN 2 AND 40", name="users_name_len"),
    )
    op.create_table(
        "questions",
        sa.Column("id", sa.BigInteger(), primary_key=True),
        sa.Column("title", sa.Text(collation="C"), nullable=False),
        sa.Column("body", sa.Text(), nullable=False),
        sa.Column("author_id", sa.BigInteger(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(["author_id"], ["users.id"], name="questions_author_id_fkey"),
        sa.UniqueConstraint("title", name="questions_title_key"),
        sa.CheckConstraint("char_length(title) BETWEEN 5 AND 200", name="questions_title_len"),
        sa.CheckConstraint("char_length(body) BETWEEN 10 AND 20000", name="questions_body_len"),
    )
    op.create_table(
        "answers",
        sa.Column("id", sa.BigInteger(), primary_key=True),
        sa.Column("question_id", sa.BigInteger(), nullable=False),
        sa.Column("author_id", sa.BigInteger(), nullable=True),
        sa.Column("body", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(["question_id"], ["questions.id"], name="answers_question_id_fkey"),
        sa.ForeignKeyConstraint(["author_id"], ["users.id"], name="answers_author_id_fkey"),
        sa.CheckConstraint("char_length(body) BETWEEN 10 AND 10000", name="answers_body_len"),
    )
    op.create_table(
        "tags",
        sa.Column("id", sa.BigInteger(), primary_key=True),
        sa.Column("name", sa.Text(collation="C"), nullable=False),
        sa.UniqueConstraint("name", name="tags_name_key"),
    )
    op.create_table(
        "question_tags",
        sa.Column("question_id", sa.BigInteger(), nullable=False),
        sa.Column("tag_id", sa.BigInteger(), nullable=False),
        sa.Column("position", sa.SmallInteger(), nullable=False),
        sa.ForeignKeyConstraint(["question_id"], ["questions.id"], name="question_tags_question_id_fkey"),
        sa.ForeignKeyConstraint(["tag_id"], ["tags.id"], name="question_tags_tag_id_fkey"),
        sa.PrimaryKeyConstraint("question_id", "tag_id", name="question_tags_pkey"),
        sa.UniqueConstraint("question_id", "position", name="question_tags_position_key"),
        sa.CheckConstraint("position BETWEEN 1 AND 5", name="question_tags_position_range"),
    )


def downgrade():
    for table in ("question_tags", "tags", "answers", "questions", "users"):
        op.drop_table(table)
```

上述 downgrade 会删业务表和数据，**不在唯一数据上运行**，不是“数据可恢复”的证明。B 档如研究回退，只在可丢弃副本执行、提前保存证据并说明损失；基础 M2 不要求往返。索引仅保留第 6 课已采纳并登记的项，本公共基线没有额外候选索引。

## 七、收尾：写法卡与三问

**课堂 7 分钟：3 分钟写法卡、2 分钟解释检查、2 分钟作业交接。**

### 常用写法卡 #7

| 写法 | ORM／工具替我们做什么 | 常见错处与本课边界 |
|---|---|---|
| 声明式模型 + relationship | 行—对象映射、关联导航 | 模型不自动更新现库；关系访问可能发 SQL |
| Session 依赖 | 提供一次请求资源并最终关闭 | 不跨并发任务共享；依赖不提交 |
| add → flush → 服务 commit | 跟踪、写入事务、确认提交 | flush 不等于提交；rollback 不撤销已提交数据 |
| select + where + 显式 DTO | 绑定值、取结果并表达公开字段 | 保留字面搜索、id 排序、总数、标签顺序；不泄漏内部列 |
| echo / SQL 计数 | 看见触发 SQL 的位置 | 覆盖关系访问与 DTO，不数日志行、不等于网络压测 |
| selectinload | 批量加载关系、减少逐父行查询 | 不保证任何查询都快，不替代只需计数时的聚合 |
| Alembic 基线 + upgrade | 按版本构建数据库结构 | stamp 不建表，版本正确不证明数据正确 |

**三问只回收刚才的观察，不另开计分小测**：

1. add 后的 ORM SELECT 能看到新行，但 psql 看不到，矛盾吗？——不矛盾；同事务 autoflush 与跨连接提交可见性不同。
2. 新 Session、20 个问题、每个访问 answers、没有 total／其他关系时，lazy 和 selectin 的完整响应各多少 SELECT？——21／2，响应应一致；只查询问题的 1 条尚未满足响应。
3. 两种 500 都执行了 rollback，为何一组无新增、一组仍有？——故障分别在 commit 调用前和确认成功后；rollback 只能撤销未提交工作。

学生在卡片补一个自己的输入或判断，直接进入同一个 M2 作业包，不再交独立卡片报告。

## 八、M2 作业与第 8 课交接

### 8.1 A 档：一个作业包

| 交付 | 必须核对的结果 |
|---|---|
| 三处 ORM 读写 | 列表课堂写、详情课后写、创建使用教师基线；JSON／HTML 共用服务与 DTO，解释分工 |
| 列表／详情回归 | 默认与边界参数、关键词 strip／字面 % 和 _、id 排序、空页 total、标签顺序；缺失整数 404／非法类型 422 |
| 创建与事务解释 | 输入 422、已知标题冲突 409、正常 JSON 201+Location／HTML 303；提交前完成回读校验 |
| 两组故障证据 | 按教师脚本在自己的项目运行；标注 flush 成功且 commit 未调用／commit 已确认且响应未启动；500＋独立查库，分别无／有本次写入 |
| 一处 N+1 对照 | 固定数据与同一响应，新的 Session，计数含 DTO；记录 SQL 分类并断言两个响应相同 |
| 空库迁移到 head | 未依赖 create_all 或手工建表；revision、五表规则、seed 后三处读写都能核对 |
| 一次局部 AI 对照 | 先自行列表，再比较 AI 方案；接受或修改均给依据，合理就保留 |

不要求五条／八条 SQL 全部翻译，不要求新增回答／标签／作者 HTTP 端点，不要求全项目 N+1 扫描、复杂迁移、重复提交故障工具源码或编写新的测试框架。已有课堂记录可以直接复用。参考层代码多不等于学生要当堂默写。

HTML 延续第 5 课：空 tags 栏为 []，否则按英文逗号 split；422／409 回填原文本，成功后 303；textarea 的首换行与自动转义规则不改。服务错误按 /ui 路径表现为 HTML，JSON 即使 Accept:text/html 仍走 JSON 契约；request-id、结构化日志、`/healthz` 的单 status 200 ok／503 degraded 都保留。

### 8.2 B 档选做

只选一项：在可丢弃副本研究一次 downgrade 并解释丢失的数据；或者比较 selectin 与聚合在同一输出下读取的数据量。不要求证明一定更快。完整状态机、连接池调优、复杂迁移／slug、多 head 和更复杂并发属于参考，不是隐藏必交。

### 8.3 下一课接收什么

- 五表最小结构、NO ACTION、命名约束、标签精确去重与 position，列名仍为 questions.body；单一 001_baseline。
- 列表／详情／创建五字段，列表 id DESC 与 items/total/page；没有公开作者摘要、回答数、sort/status 参数。
- 服务显式 commit；依赖只清理；两种故障证据与真实提交可见性条件。
- 第 8 课按 v4 新增 vote_count/version 与条件投票／PATCH，先跑正常路径再复现并发丢失更新；404／版本409要分开，不能自动换新版本重发。

第 8 课底稿已按 v4 重写，沿用本课服务层提交、body 列名与原列表契约；按 001_baseline → 002_question_version 增加计数／版本，采用正常投票、受控并发、条件 UPDATE 与 PATCH 的 95+5 路线。独立课程包仍须按该课制作清单落地验收；第 9 课底稿也已按 v4 将证据组织为自动回归、分页定位与四门禁主线，其完整课程包和远端 CI／分支保护仍待制作验收，不在本课提前追加 CI 开发。

## 九、教师附录：完整模型与迁移接线

### 9.1 五表完成版模型

教师模块 app.models 的参考；第 6 课 DDL、迁移和模型应三方核对。课堂主要读 Question，剩余模型用于课后查阅和工具运行。没有新增业务列。

```python
# lesson07: models
from datetime import datetime
from sqlalchemy import BigInteger, CheckConstraint, DateTime, ForeignKey, SmallInteger, Text, UniqueConstraint, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    display_name: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    __table_args__ = (CheckConstraint("char_length(display_name) BETWEEN 2 AND 40", name="users_name_len"),)


class Question(Base):
    __tablename__ = "questions"
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    title: Mapped[str] = mapped_column(Text(collation="C"))
    body: Mapped[str] = mapped_column(Text)
    author_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.id", name="questions_author_id_fkey"))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    answers: Mapped[list["Answer"]] = relationship(back_populates="question", passive_deletes="all")
    tag_links: Mapped[list["QuestionTag"]] = relationship(
        back_populates="question", order_by="QuestionTag.position", passive_deletes="all",
    )
    __table_args__ = (
        UniqueConstraint("title", name="questions_title_key"),
        CheckConstraint("char_length(title) BETWEEN 5 AND 200", name="questions_title_len"),
        CheckConstraint("char_length(body) BETWEEN 10 AND 20000", name="questions_body_len"),
    )


class Answer(Base):
    __tablename__ = "answers"
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    question_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("questions.id", name="answers_question_id_fkey"))
    author_id: Mapped[int | None] = mapped_column(BigInteger, ForeignKey("users.id", name="answers_author_id_fkey"))
    body: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    question: Mapped["Question"] = relationship(back_populates="answers")
    __table_args__ = (CheckConstraint("char_length(body) BETWEEN 10 AND 10000", name="answers_body_len"),)


class Tag(Base):
    __tablename__ = "tags"
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    name: Mapped[str] = mapped_column(Text(collation="C"))
    __table_args__ = (UniqueConstraint("name", name="tags_name_key"),)


class QuestionTag(Base):
    __tablename__ = "question_tags"
    question_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("questions.id", name="question_tags_question_id_fkey"), primary_key=True,
    )
    tag_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("tags.id", name="question_tags_tag_id_fkey"), primary_key=True,
    )
    position: Mapped[int] = mapped_column(SmallInteger)
    question: Mapped["Question"] = relationship(back_populates="tag_links")
    tag: Mapped["Tag"] = relationship()
    __table_args__ = (
        UniqueConstraint("question_id", "position", name="question_tags_position_key"),
        CheckConstraint("position BETWEEN 1 AND 5", name="question_tags_position_range"),
    )
```

未显式命名的主键由 PostgreSQL 生成 users_pkey 等默认名，需与 DDL 对照。`passive_deletes="all"` 加上**没有 delete／delete-orphan cascade**，使 Session.delete(question) 不先清理或置空子关系，交给数据库拒绝仍有引用的父行；即使集合已经加载也应测试。它不把任意集合编辑变成合法操作，不意味着提供了删除 API。

User／Tag 未声明反向集合，避免为尚未使用的导航增加概念；外键照样存在并执行约束。以后需要新增关系时要重新核对 ORM 行为，不默认所有关系都应双向、级联。

### 9.2 在线迁移配置参考

教师在已初始化 Alembic 的独立工程替换 env.py 在线函数，导入包含五个模型的 app.models；settings 来自教师配置。保留模板对在线／离线模式的调用分支；离线模式不列入本课验收。

```python
# lesson07: migration_env
from alembic import context
from sqlalchemy import create_engine, pool
from app.config import settings
from app.models import Base


def run_migrations_online():
    connectable = create_engine(settings.database_url, poolclass=pool.NullPool)
    try:
        with connectable.connect() as connection:
            context.configure(
                connection=connection, target_metadata=Base.metadata,
                compare_type=True, compare_server_default=True,
            )
            with context.begin_transaction():
                context.run_migrations()
    finally:
        connectable.dispose()
```

URL 直接来自教师配置，不把含 `%` 的凭据原样写进 ini 插值，也不打印 URL。主线一个独占数据库，使用其默认 schema；使用自定义 schema 的教师测试还需正确配置 search_path／版本表位置，不让 autogenerate 扫描其他课程库。

## 十、制作与验证状态

本轮重写不等于 M2 全工程交付。以下机制检查、目标版本、完整 HTTP／HTML 和真实课堂负荷分开记录，不沿用旧稿精简 SQLite 模型的 9／5／4 结果冒充本课验收。

- **本轮实测完成**：提取本稿全部 Python 围栏，复用第 3 课真实输入／输出模型、第 4 课业务异常／JSON 错误处理器／request-id 中间件、第 6 课 DDL／seed。完成 300 项检查（包含 12 项代码语法与 4 项课时／分工检查），正常停止并重启专用数据库后另通过 3 项独立回读，累计 **303 项**。不是沿用旧稿的精简模型结果。
- **环境与隔离**：Python 3.12.12、SQLAlchemy 2.0.54、psycopg 3.3.6、PostgreSQL **18.6**／UTF-8／UTC 测试会话；目标仍为 PostgreSQL 16，尚未完成目标版本验收。复用前课工作区专用集群，只新建 l07 独立 schema，不改前课测试数据；仅监听权限 0700 的本地 Unix socket。核验结束后停止本轮启动的集群。
- **临时迁移依赖**：m0-tracer 的项目环境本身没有 Alembic。本轮将 Alembic 1.20.0、Mako 1.4.1 从缓存装入 `.build-check/lesson07-tools`；离线缓存缺 MarkupSafe 后，仅为该临时目录下载并安装 MarkupSafe 3.0.3。未更改项目 pyproject、锁文件或原虚拟环境；正式课程包仍须提供自己的锁定环境，不能依赖此临时目录。
- **结构／服务实测**：对比第 6 课 DDL、完整 ORM metadata 和真实迁移产物的列、可空性、类型、默认、约束定义／名称／删除策略。验证列表字面搜索／分页／总数／五字段／标签顺序、缺失详情、共享输入拒绝、创建与 UPDATE、autoflush／no_autoflush／独立连接可见性、已加载与未加载集合的父行删除拒绝、已知标题冲突翻译、输出校验失败回滚。
- **N+1 与标签竞争实测**：固定 20 个问题、20 条回答时 lazy／selectin 为 **21／2** 条 SELECT；4 行为 5／2，空结果为 1／1，完整响应相等。另用两个独立 Session 竞争同一新标签，观察真实等锁、提交后下一语句可见，两问题共享一条标签并各有一条关联；不据此承诺所有复杂并发都成功。
- **最小 JSON 装配实测**：临时 FastAPI 装配使用本稿列表路由、真实资源依赖／服务与前课错误／日志代码，覆盖 201+Location、422／404／409、Accept 不改 JSON、资源关闭与只读不提交；计数覆盖列表 DTO／响应处理，普通非空页 3 条、越界空页 2 条。两组 500 均验证 flush／commit／ASGI 响应启动顺序，并独立查问题、标签、关联，确认提交前无新增、提交确认后仍存在。它不是完整 M1／HTML 课程应用。
- **真实 Alembic 实测**：从本稿提取固定基线与在线 env 主体，在临时配置中通过 Alembic 命令 API 对两个独立空 schema 执行 current／upgrade head／重复 upgrade／check；没有先用 create_all 建迁移目标。核对版本、五表、seed／序列校准后的创建／列表／详情。仅在第二个可丢弃副本运行参考 downgrade，再升级后数据为空，验证“结构回退不恢复数据”。正常重启后的额外回读核对服务已提交问题／标签和第一个迁移副本的版本／数据，不代表崩溃恢复或提交期间断连。
- **试讲前素材**：列表任务起点／完成版、详情壳／教师创建回读独立帮助函数、完整模型、20 问题实验 seed、计数入口、两个故障脚本、固定基线和独立库配置、回归与安全复位入口、带环境说明的备用记录。不存在的脚本或工程 tag 不写成可直接执行。
- **完整应用验收仍须完成**：独立 M2 工程的 JSON／HTML 三处读写、原文回填、303、异常分流、request-id、单 status 探针及浏览器刷新；在完整应用重跑两种故障与计数。临时 JSON 装配不覆盖真实 HTML 模板、Uvicorn 网络链路或浏览器。
- **目标版本与迁移验收仍须完成**：PostgreSQL 16、真实 M1 数据迁移／已有库接入核对、正式独立包的 CLI 命令与锁定配置；在该环境重跑空库升级、三处读写和重启核对。固定 seed／临时配置不代表全量 M1 已迁移。
- **教学负荷待试讲**：25 分钟内独立完成列表并解释选择；15 分钟内根据完整条件预测 N+1；不要求学生开发教师设施。本课没有独立计分小测。

临时复核入口（依赖上述临时工具目录和已启动的专用数据库 socket；不是学生启动命令）：

```bash
uv run --offline --project snippets/ch01/m0-tracer --no-sync python .build-check/validate_lesson07.py
```

本轮 TestClient 出现现有 Starlette 对 httpx 适配的弃用提示；未为消除提示升级课堂应用依赖。IDE 语言服务未就绪，不能把它说成 lint 全绿；Python 围栏已编译并运行上述核验。最终 Slidev、视觉／导出和真实课堂试讲未在本轮进行。

参考：SQLAlchemy 2.0 Session Basics／Relationship Loading Techniques／Association Object、PostgreSQL 16 Transaction Isolation／Constraints、Alembic Tutorial／Autogenerate。制作最终 Slidev 时把教师时间、接线待办与应急切换放备注，学生必需的规则、运行条件和证据边界保留正文。
