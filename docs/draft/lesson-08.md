# 第 8 次课教学底稿（第四版）
## 写操作的正确性：为什么票会丢

> **备课基线**：[第四版大纲](../syllabus-v4.md)第 8 课与[第 7 课交接](lesson-07.md#83-下一课接收什么)。本稿尚未移交归档，定义教学内容、固定契约与配套工程要求；不是已经交付的独立问答应用。文中教师脚本、模型模块与命令须在课程包中落地，不把示意路径或阶段名说成现有入口。

## 〇、这次课解释一件什么事

**讲给学生的目标句**：你能复现并发投票导致的丢失更新，用条件更新修复，并解释 409 的含义。

核心解释目标：**两个人同时投票，票为什么会丢。** 先跑正常操作，再把两个合法请求的读取、写入和提交排在同一条时间线上。事务保护一次操作内部的完整性，但不能单靠“使用了事务”就避免两个读—改—写互相覆盖。

### 95 分钟教学 + 5 分钟缓冲

| 分钟 | 教学单元 | 当场产出 |
|---|---|---|
| 5 | 目标与已有 M2 | 说清一次投票的输入、输出与成功含义 |
| 12 | 正常路径：一次投票成功 | 详情取得版本，投票 +1，独立回读 |
| 20 | 教师复现丢失更新 | 两连接读到相同旧值，两个成功却只增加 1 |
| 25 | 学生改成条件 UPDATE | 选择成功判据、区分 404／409、判断四个情境 |
| 15 | 原子加一与乐观并发控制 | 比较接受意图与拒绝陈旧状态，不自动重试 |
| 10 | 最简 PATCH | 只改提交字段，复用版本条件与标题唯一规则 |
| 8 | 写法卡、契约说明与交接 | 一个作业包、一次 AI 对照判断 |
| **95** | **教学合计** | **另有 5 分钟缓冲，共 100 分钟** |

本课**不安排计分小测**。四个情境属于 25 分钟任务中的解释检查，不再增加 20 分钟诊断题。超时压缩附录逐行讲解与幂等键拓展，不挤占正常演示、学生实践或四情境核对。

### 教师提供什么，学生决定什么

| 内容 | 提供者／标注 | 边界 |
|---|---|---|
| 正常投票完成版、已知缺陷副本 | 教师提供，要求解释 | 先看正确路径；缺陷只在隔离副本，不破坏合格 M2 |
| 条件写入函数壳 | 学生课堂完成 | 自选 RETURNING 或可靠影响行数；自选无匹配时的存在性查询方式 |
| 模型增量、迁移、详情／创建 DTO 接线 | 教师提供，要求会用 | 不把迁移和旧路由适配再加成学生编码任务 |
| 服务事务、异常出口 | 沿用前课，要求解释 | 服务显式 commit；内部辅助函数不提交；依赖只提供与关闭 |
| 双连接同步、复位、日志与故障脚本 | 教师设施，要求会用；内部黑盒 | 会读初值、连接标识、注入点与结果；不开发控制器、不进口试内部细节 |
| PATCH 输入模板和端点壳 | 教师提供，要求会用；更新语义要求解释 | 课堂讲一个正常补丁，课后完成标题／正文与边界回归 |
| 一页契约说明 | 教师给固定规格，学生补实例与解释 | 不自由改状态码、字段或公开排序 |

本课不前置 React、Vite、TypeScript 类型生成或完整认证。幂等键、PUT 全量替换、ETag、复杂迁移只在参考层；不作为 M3 的隐藏前提。

## 一、从 M2 出发：一次成功到底承诺什么

**课堂 5 分钟。先看已有详情，再展示本课新增的两个字段。**

第 7 课交付五表、列表／详情／创建 ORM、服务事务和 `001_baseline`。数据库列仍为 questions.body；没有状态、浏览量或作者摘要接口。列表原有五字段、`items/total/page`、id DESC 和字面搜索都继续保留。

### 本课契约与迁移交接表

这张表是本课实现、教师回归与第 9 课接线的依据，不把旧稿的参数扩展当成既有规格。

| 项目 | 本课决定 | 变更与核对 |
|---|---|---|
| 列表 | GET /questions，keyword/page/page_size，默认空／1／20，page_size 为 1–50 | 不变；仍五字段、id DESC、字面 %／_，total 为筛选后分页前总数；不加 sort/status |
| 创建输入 | title/body 先 strip，长度 5–200／10–20000；tags 最多五项、默认 []；拒绝额外字段 | 不允许客户端指定 vote_count/version/author_id；标签仍精确去重保首次顺序 |
| 详情／创建输出 | 原五字段 + vote_count + version | 明确增量；票数初值 0，版本初值 1；创建仍 201 + Location |
| 条件投票 | POST /questions/{qid}/votes，JSON `{"version":5}` | version 必填、严格正整数；200 返回 qid/vote_count/version |
| PATCH | PATCH /questions/{qid}，version 必填，title/body 至少出现一个 | 省略保持；显式 null 拒绝；200 返回扩展详情 |
| 资源标识 | qid 仍按整数解析，不新增 ge=1 | 不存在的 0／负整数是业务 404，非整数 422 |
| 错误体 | code/message/detail/request_id 四字段 | 缺失 question_not_found→404；陈旧 version_conflict→409；标题 duplicate_title→409；输入 validation_error→422 |
| 数据结构 | questions 加非空 vote_count/version 与 CHECK | 001_baseline → **002_question_version**；其他五表关系、标签 position 不变 |
| HTML／探针 | 原三页、失败回填、303、自动转义、request-id、单 status 探针 | 不新增投票／PATCH 表单页；内部详情可带新增字段，原模板仍能使用；200 ok／预期数据库故障 503 degraded 不改 |

version 是服务端管理的修订号，客户端提交的是**自己看到的旧版本**，不是希望写进去的新版本。详情、投票和 PATCH 必须连成闭环，否则客户端无从取得条件值。

投票在本课表示“接受一次计数加一意图”，不是创建一个可独立查询的 Vote 资源，成功用 200，不伪造 Location。允许演示者再次确认新的加一意图；没有登录、投票记录或“一人一票”保证。新增写接口只用于本地虚构数据，第 14 课补认证与对象授权。

讲：今天既要问数据库最后是多少，也要问**两次意图到底接受了几次**。两个请求都成功和一个成功一个冲突，不是同一种结果。

## 二、先跑通正常路径：取得版本，再投一票

**课堂 12 分钟。4 分钟读详情与输入，5 分钟执行正确服务，3 分钟回读并指认 SQL／COMMIT。教师先提供完成版，学生之后在任务副本补同一个核心函数。**

### 2.1 给定初始数据

教师已经在独立副本完成 002 迁移，保留第 6 课 seed；为本轮观察把问题 101 设置为 **vote_count=10、version=5**，提交后再开始请求。这是教师复位，不是公开接口允许客户端改计数；正常新建问题仍从 0／1 开始。

```http
GET /questions/101

POST /questions/101/votes
Content-Type: application/json

{"version":5}
```

详情中看见 10／5；成功投票响应为 `{"qid":101,"vote_count":11,"version":6}`。等成功响应返回后，用独立连接查询 101，仍为 11／6。响应中的数字是这次成功操作的结果，不保证此后永不被其他请求更新。

### 2.2 输入／输出与业务异常

```python
# lesson08: vote_contract
from pydantic import BaseModel, ConfigDict, Field


class VoteIn(BaseModel):
    model_config = ConfigDict(extra="forbid")
    version: int = Field(ge=1, strict=True)


class VoteOut(BaseModel):
    qid: int
    vote_count: int = Field(ge=0)
    version: int = Field(ge=1)


class QuestionDetailOut(QuestionOut):
    vote_count: int = Field(ge=0)
    version: int = Field(ge=1)


class VersionConflict(AppError):
    pass


BUSINESS_HTTP[VersionConflict] = (409, "version_conflict", "资源已变化，请刷新后确认")
```

这里复用第 3／4 课 QuestionOut、AppError、BUSINESS_HTTP；新增映射，不另建一套 HTTP 错误格式。`strict=True` 拒绝 true、"5"、5.0；合法值是 JSON 正整数。输入不合法优先返回 422，不能拿非法 version 测资源是否存在。

**正常数据访问函数的完整参考在 §4.2**。第一次演示只指出：把 id 与旧 version 同时放入 WHERE，在数据库里完成票数和版本加一，返回实际更新值；不先在 Python 中算一个固定新票数。

### 2.3 服务确认提交，端点才返回成功

教师在引入 SQL 函数时配好下列服务。`no_fault` 是第 7 课默认空回调；两个回调只供教师本地脚本，不通过请求参数开放。

```python
# lesson08: vote_service

def vote_question_service(
    session, qid, payload, *, after_flush=no_fault, after_commit=no_fault,
):
    try:
        result = vote_once(session, qid, payload.version)
        session.flush()
        after_flush()
        session.commit()
        after_commit()
        return result
    except Exception:
        session.rollback()
        raise
```

UPDATE 已经执行，flush 不是第二次加票；它让事务中待写工作完成。结果模型在 commit 前构造并校验。服务返回之后，HTTP 边界才生成成功响应；`get_session()` 仍是 yield／close，不在依赖退出阶段提交。

正常例先通过再讨论故障：SQL／flush 成功、commit 调用前抛错，500 且计数／版本保持原值；commit 确认返回后、响应启动前抛错，500 但计数／版本已更新。沿用 M2 教师脚本，记录位置、响应与独立回读；**500 不等于没投上**。真实提交期间断连属于结果未知，这两个注入点不模拟它。

## 三、教师复现：两个事务都成功，为什么只多一票

**课堂 20 分钟。5 分钟读缺陷与预测，7 分钟同步运行，5 分钟排列 SQL／结果，3 分钟核对独立连接证据。**

### 3.1 已知缺陷样本，只用于隔离实验

先明确缺陷来源：下面是教师构造的读—改—写反例，不是真实 AI 一定会给出的代码，也不是主项目的正确服务。端点方法依旧 POST，输入合法，事务会提交；只改变“怎样写入”，不同时叠加 GET 写操作、缺失字段或依赖未提交等问题。

```python
# lesson08: broken_demo

def vote_broken_service(session, qid, *, after_read):
    try:
        question = session.get(Question, qid)
        if question is None:
            raise QuestionNotFound()
        old_votes, old_version = question.vote_count, question.version
        after_read()
        question.vote_count = old_votes + 1
        question.version = old_version + 1
        session.flush()
        result = VoteOut(qid=qid, vote_count=question.vote_count, version=question.version)
        session.commit()
        return result
    except Exception:
        session.rollback()
        raise
```

隔离适配器仍接合法 VoteIn，但缺陷函数没有把 payload.version 加到 UPDATE 条件；这是待修复点。不要把它接回正确 `/questions/{qid}/votes`。公开端点固定版本条件，不能让用户选择 broken 策略。

### 3.2 观察点一：先完整写出条件

初始 101=10／5；PostgreSQL READ COMMITTED；两条**独立**连接／Session、非自动提交；A/B 都成功读取 10／5 后再放行。没有第三个写者、删除、超时、触发器或重试。A/B 都执行上述常量覆盖并提交。最终票数、版本与两个响应是什么？

| 时刻 | A | B |
|---|---|---|
| 读取并到达同步点 | 10／5 | 10／5 |
| 计算 | 准备写 11／6 | 准备写 11／6 |
| UPDATE／提交 | 按主键写常量 11／6，然后提交 | 若撞上行锁则等待，之后仍写常量 11／6并提交 |
| 结果 | 成功 200，返回 11／6 | 成功 200，返回 11／6 |
| 独立回读 | **最终 11／6，不是 12／7** | 两个成功意图中一个增量被覆盖 |

丢失的不是一条 HTTP 响应，而是一次加一效果。数据库把两条 UPDATE 按锁顺序执行了，但第二条指令本身就是“写 11”，不是“对当前值加一”。row lock 防止物理写入混乱，不自动修正应用根据旧数据算出的常量。

### 3.3 教师同步设施与证据

教师 runner 在两个 SELECT 完成后用带超时的 Barrier 放行，每个线程创建自己的 Session。记录 backend pid、request-id、读到的旧值、UPDATE 参数与提交结果。Barrier 不能放在 UPDATE 之后：第一条 UPDATE 持锁、第二条等锁时，双方可能无法抵达同一同步点。

不要加 SELECT FOR UPDATE 再要求两者都读完才放行，这会让第二个读取先被阻塞。隔离数据每轮复位为 10／5，确认两连接不同；不能在同一个连接上排两段代码假装并发，也不能靠随机 sleep 或快速双击证明读到了同一旧值。

同步超时不是复现成功；应报告失败阶段、释放等待和回滚。真实 HTTP 演示必须通过教师测试适配器连接到同一受控同步设施；只有服务函数调用时就标明服务级实验，不把它称为网络并发压测。

## 四、学生任务：把旧版本条件放进同一条 UPDATE

**课堂 25 分钟。4 分钟读固定规格，10 分钟补函数，6 分钟正反核对，5 分钟四情境判断与保存证据。**

### 4.1 任务壳与可以自主选择的地方

教师提供原有路由、VoteIn/VoteOut、服务事务、异常映射、迁移完成的数据和独立测试入口。学生只补数据函数：

```text
vote_once(session, qid, expected_version)
  ① 在同一 UPDATE 中判断 id 与 version，并让两个值在数据库内 +1
  ② 判断是否匹配成功：RETURNING 或驱动可靠支持的影响行数
  ③ 无匹配时查询是否仍存在：不存在 → QuestionNotFound；存在 → VersionConflict
  ④ 返回本次更新的 qid／票数／新版本；不在这里 commit
```

如果选影响行数，本例是一条不带 RETURNING 的 UPDATE，需确认当前驱动 rowcount 的语义／支持情况；成功后在本事务内读取新值构造响应。不是拿 SELECT 的 rowcount 或 executemany 的未知计数判断。若选 RETURNING，**有行是成功，None 是未匹配**，不同时依赖未验证的 rowcount。

学生的独立决定是成功判据与查询组织方式，不是把所有无匹配都改成 409，也不是修改错误体或自动刷新版本重发。

### 4.2 完成后对照的正确数据函数

```python
# lesson08: conditional_vote
from sqlalchemy import select, update


def raise_unmatched(session, qid):
    exists = session.scalar(select(Question.id).where(Question.id == qid))
    if exists is None:
        raise QuestionNotFound()
    raise VersionConflict()


def vote_once(session, qid, expected_version):
    statement = (
        update(Question)
        .where(Question.id == qid, Question.version == expected_version)
        .values(vote_count=Question.vote_count + 1, version=Question.version + 1)
        .returning(Question.id, Question.vote_count, Question.version)
        .execution_options(synchronize_session=False)
    )
    row = session.execute(statement).mappings().one_or_none()
    if row is None:
        raise_unmatched(session, qid)
    return VoteOut(qid=row["id"], vote_count=row["vote_count"], version=row["version"])
```

SQL 形状如下，`:qid` 等是 SQLAlchemy 绑定参数示意，不是可直接粘贴到 psql 的变量：

```sql
UPDATE questions
SET vote_count = vote_count + 1, version = version + 1
WHERE id = :qid AND version = :expected_version
RETURNING id, vote_count, version;
```

两个关键点：**校验旧版本与修改必须是同一语句**；修改使用列当前值加一，不是 Python 里提前算好的常量。在 READ COMMITTED 下，若等待另一写者提交，PostgreSQL 会针对更新后的行重新判断条件，旧 version 就不再匹配。

`synchronize_session=False` 不同步已加载 ORM 对象的内存值。本函数直接用 RETURNING 行构造输出；不从旧对象读票数。普通 `session.get()` 可能命中旧 identity map，不等于“重新查库”；PATCH 的刷新参考见 §6.3。

存在性查询只说明**第二条语句当时**能否找到资源，不与前一条 UPDATE 自动共用快照。课堂排除并发删除／重建同 id；如发生删除，第二次查询可能返回 404，不能据此追溯 UPDATE 前的全部历史。不要用 `if not exists`，合法整数 id=0 在别的导入场景可能存在，应判断 `is None`。

### 4.3 观察点二：两个请求都看到了 version=5

继续用初始 101=10／5；两客户端都在写前取得 version=5，分别提交同一版本。没有其他写入，第一条成功提交后第二条完成条件 UPDATE；假定无超时、无重试。

预测：第一条匹配 1 行，200→11／6；第二条匹配 0 行，资源存在→409 version_conflict；最终 11／6。这表示**只接受了一次意图**，不是“两票都成功但系统补救了计数”。若第一条回滚，第二条可以成功，这不在上述“第一条已提交”的前提里。

冲突方读取最新详情，让用户确认新的意图后，携带 version=6 再投，成功后为 12／7。**不能由程序收到 409 就自动读版本、再发直到成功**；那会把用户未见的新状态当成他同意了。

### 4.4 观察点三与四个情境

先问：合法请求访问不存在的 qid，UPDATE 同样匹配 0 行。若一律返回 version_conflict，客户端会误以为“刷新版本还能继续”，掩盖资源不存在。正确处理为 404 question_not_found。

四个情境都规定：输入合法、没有并发删除／重建，且查询与写入期间只有题面所述变化。写判断后再运行教师用例。

| 情境 | 当前事实 | 应答与解释 |
|---|---|---|
| A | qid=999999 不存在，提交 version=5 | 404 question_not_found；没有可更新资源 |
| B | qid=101 存在且 version=6，提交旧 version=5 | 409 version_conflict；资源还在，状态已变化 |
| C | 用户读到 101 的 version=5，教师在请求开始前已删除该无引用实验行 | 404 question_not_found；过去存在不代表现在存在 |
| D | 101 存在且 version=5，提交不匹配的未来 version=99 | 409 version_conflict；不是“只有小于当前版本才冲突” |

C 使用独立无引用样本，不对带回答／标签的 101 直接 DELETE 造成外键拒绝后还声称“删除成功”。教师在该情境的专用库预置一个 id=101、没有回答／关联的问题，完成删除并提交，再请求；不与第 6 课 seed 的有引用 101 混用。

非法 version=0、null、true 或非整数 qid 属于 422，不是四情境中的 404／409 选择题。每次拒绝都查当前票数／版本或确认资源确实不存在，不能只保留一张错误截图。

## 五、机制：原子加一、版本条件、幂等分别保护什么

**课堂 15 分钟。6 分钟三轨迹对照，5 分钟冲突／重试判断，4 分钟保证范围。**

### 5.1 三种写法，同一个初值，不同承诺

每一行使用新复位的独立副本，初始为 10／5，两次合法意图，无其他写者。条件版双方都提交 version=5；不把三个策略在同一库累加执行。

| 写法 | 两次结果 | 最终状态 | 保护与不足 |
|---|---|---|---|
| 读旧值后写常量 | 两次成功 | 11／6 | 未保护并发读—改—写，丢失增量 |
| 原子增量，不判断旧版本 | 两次成功 | 12／7 | 两个独立增量都保留；重复请求仍算另一次增量 |
| 原子增量 + 旧版本条件 | 成功／冲突各一次 | 11／6 | 拒绝陈旧状态的写入，不表示两个意图都接受 |

隔离原子增量对照也递增 version，避免在同一资源定义中展示一个悄悄绕过修订号的写者；它不是主项目可选公开策略。

```python
# lesson08: atomic_demo

def vote_atomic_demo_service(session, qid):
    try:
        statement = (
            update(Question).where(Question.id == qid)
            .values(vote_count=Question.vote_count + 1, version=Question.version + 1)
            .returning(Question.id, Question.vote_count, Question.version)
            .execution_options(synchronize_session=False)
        )
        row = session.execute(statement).mappings().one_or_none()
        if row is None:
            raise QuestionNotFound()
        result = VoteOut(qid=row["id"], vote_count=row["vote_count"], version=row["version"])
        session.commit()
        return result
    except Exception:
        session.rollback()
        raise
```

如果产品要求“每个独立加一都接受”，原子增量可以是正确选择；本课程明确选择**基于所见版本确认一次写入**的协议，用它学习条件更新，随后用于改帖。不要说“任何投票系统都必须乐观锁”，也不要把条件更新称作前端乐观 UI。

### 5.2 冲突不是成功回执，重试不是免费动作

幂等指重复请求的**预期效果**与一次相同，不要求响应、状态或日志条数相同。GET 用于读取；不能用 GET 实现业务投票，浏览器预取等可能触发它。

- 原请求成功提交但响应丢失，重发相同旧 version 可以得到 409；这不能证明前一次一定成功，也可能有其他写者先改了版本。
- 刷新详情只能看当前状态，不一定知道哪一次意图造成变化。request-id 用于关联日志，不是认证身份或幂等键。
- 事务保证内部原子性；版本条件拒绝不匹配状态；标题唯一规则保护标题；PRG 减少成功页面刷新重发；它们都不是“重放第一次业务结果”的完整协议。
- 本课不自动重试任何结果未知的写请求；也不通过更换 version 绕过冲突。已知业务 409、输入 422与基础设施 500／结果未知分别判断。

客户端收到与本次请求对应的 200，且服务遵守先提交后响应的契约，便可确认本次条件写入已接受；没有收到成功响应，不能反推未接受。`UPDATE ... RETURNING` 返回一行本身还不等于事务已提交。

### 5.3 版本保护成立的范围

本课投票和 PATCH 都给同一问题的 version 加一，所以一次投票也可能使同时进行的正文编辑变成陈旧版本，这是本课固定的**整行修订号**语义。即使 PATCH 提交的文本与当前值相同，只要匹配并接受该补丁，本课也递增一次版本；不另外设计无变化优化。

所有主线修改问题的写入口都须遵守版本协议。第 7 课的无条件正文修改演示退出主线，只保留在隔离实验；其他脚本直接 UPDATE、复位版本或重用已删除 id 都可能破坏保证。教师复位发生在无并发写入的可丢弃库，不当成真实业务操作。

数据库 INTEGER 和应用数值有范围边界，不承诺无限加一。计数／版本溢出属于未识别数据库错误时回滚并走安全 500，不一律翻为版本 409；本课尚未增加新的计数上限产品规则。

## 六、十分钟 PATCH：只改出现的字段

**课堂 10 分钟。3 分钟省略／null 规格，4 分钟正确更新与回读，3 分钟三种失败对照。教师给输入模板与端点壳，学生课后补齐完整回归。**

### 6.1 先定义本课补丁，不背新协议名

```json
{"version":6,"title":"修改后的有效问题标题"}
```

这是课程自定义 JSON 部分更新，不宣称实现了 JSON Patch 或 JSON Merge Patch。

| 输入 | 本课含义 |
|---|---|
| 不提交 body | 保持原正文 |
| `body: null` | 422，不接受把非空正文清空，也不能静默当省略 |
| 空白 title/body | 先 strip，按创建时的长度限制判断 |
| 只有 version | 422，至少提交 title/body 一项 |
| tags、author_id、vote_count 等额外键 | 422，不允许通过补丁改这些字段 |
| version 不匹配／资源缺失 | 分别 409／404，不执行修改 |

### 6.2 输入模板：键可省略，出现时必须是有效字符串

TypedDict／Annotated 是教师提供的校验接线，**要求会用，不考模板内部语法**；学生须解释上表。FastAPI 解析后给出只包含已提交键的字典。

```python
# lesson08: patch_contract
from typing import Annotated
from typing_extensions import Required, TypedDict
from pydantic import AfterValidator, BeforeValidator, with_config


def strip_patch_text(value):
    return value.strip() if isinstance(value, str) else value


PatchTitle = Annotated[str, BeforeValidator(strip_patch_text), Field(min_length=5, max_length=200)]
PatchBody = Annotated[str, BeforeValidator(strip_patch_text), Field(min_length=10, max_length=20000)]


@with_config(ConfigDict(extra="forbid"))
class QuestionPatch(TypedDict, total=False):
    version: Required[Annotated[int, Field(ge=1, strict=True)]]
    title: PatchTitle
    body: PatchBody


def require_patch_change(value):
    if not ({"title", "body"} & value.keys()):
        raise ValueError("至少提供 title 或 body")
    return value


PatchPayload = Annotated[QuestionPatch, AfterValidator(require_patch_change)]
```

title/body 在 OpenAPI 中是非必填、非 nullable 字符串；version 必填。AfterValidator 的“至少一个字段”不自动完整变成 Schema 条件，operation 描述与运行测试必须一起保留。换用 BaseModel 也可以，但需保留“键是否提交”的信息，不能 dump 全部默认字段覆盖原记录。

### 6.3 PATCH 沿用服务层事务

下面的 read_versioned_question_dto 定义在 §9.2，使用 populate_existing 刷新已有对象，并按 position 取标签。它与列表的五字段 DTO 分开，不全局改掉列表输出。

```python
# lesson08: patch_service
from sqlalchemy.exc import IntegrityError


def patch_once(session, qid, payload):
    changes = {key: payload[key] for key in ("title", "body") if key in payload}
    statement = (
        update(Question)
        .where(Question.id == qid, Question.version == payload["version"])
        .values(**changes, version=Question.version + 1)
        .returning(Question.id)
        .execution_options(synchronize_session=False)
    )
    updated_id = session.scalar(statement)
    if updated_id is None:
        raise_unmatched(session, qid)
    return updated_id


def patch_question_service(
    session, qid, payload, *, after_flush=no_fault, after_commit=no_fault,
):
    try:
        updated_id = patch_once(session, qid, payload)
        session.flush()
        after_flush()
        result = read_versioned_question_dto(session, updated_id)
        if result is None:
            raise RuntimeError("更新后的回读缺失")
        session.commit()
        after_commit()
        return result
    except IntegrityError as exc:
        session.rollback()
        constraint = getattr(getattr(exc.orig, "diag", None), "constraint_name", None)
        if getattr(exc.orig, "sqlstate", None) == "23505" and constraint == "questions_title_key":
            raise DuplicateTitle() from exc
        raise
    except Exception:
        session.rollback()
        raise
```

只更新提交的 title/body，票数、标签、作者、created_at 不改，版本由数据库加一。标题精确唯一仍由 questions_title_key 裁决；已知冲突回滚整条更新，包括版本，不变成“文字没改但版本加了”。陈旧版本同时携带重复标题时，若没有行匹配 UPDATE，则先得到 version_conflict；不承诺先检查未被接受补丁的全部业务冲突。

课堂对照：只改标题、正文不变；非法 null→422；匹配版本但与另一标题冲突→409 duplicate_title。课后再核对同时改两个字段、旧版本、缺失资源、空补丁与长度边界。使用已加载的旧对象运行 PATCH 时，返回正文和版本也必须是新值，不能只检查数据库正确。

## 七、收尾：常用写法卡与一页契约说明

**课堂 8 分钟。3 分钟写法卡，3 分钟契约说明与 AI 判断，2 分钟作业交接。**

### 常用写法卡 #8

| 写法 | 数据库／框架替你做什么 | 常见错处与边界 |
|---|---|---|
| vote_count/version + 数据库默认 | 初始化合法计数与修订号 | 修改模型不替代迁移；客户端不能指定新版本 |
| UPDATE SET 列=列+1 | 原子地保留每个匹配的增量 | 无条件增量不识别重复意图 |
| WHERE id AND version | 将旧状态判断与写入合成一条语句 | Python 先比较再无条件写仍有竞争窗口 |
| RETURNING／可靠 rowcount | 判断当前语句是否匹配 | 无匹配须区分缺失与不匹配；有返回行还不等于提交 |
| 服务 commit／rollback | 统一业务事务，提交后再响应成功 | 确认提交后的故障不能靠 rollback 撤销 |
| PATCH 只选择提交字段 | 部分更新，不覆盖未提交值 | 省略不等于 null；不能让客户端覆盖 version |
| code 区分错误与重试 | 稳定表达缺失、版本冲突、标题冲突 | 409 不是成功，不自动换版本重发 |

一页《API 契约说明》直接复用 §一 的表，补一次正常报文、一次 404／409 说明与 PATCH 省略／null 例子；不要求抄完整底稿。错误仍是四字段，422 detail 为 loc/type/msg 列表，不写成 detail.fields，不投影数据库原始异常。

AI 对照：先完成自己的条件函数，再给 AI 固定契约和允许改动范围。检查它有没有把版本放入同一 UPDATE、如何判定 0 行、是否保留服务提交、如何回读新值。合理则接受并附证据，有问题才修；不要求必须找出错误或额外交一份长审计报告。

### A 档：只交一个作业包

1. 条件投票：正常 200、相同旧版本一成功一冲突、缺失 404；四情境判断与无误写证据。
2. PATCH 标题／正文：省略保持、明确 null／空补丁／非法长度／额外键 422，旧版本／标题冲突 409，合法修改与新版本回读。
3. 并发记录：固定初值、两连接身份、两个请求／结果、SQL 条件与独立查库；说明原子增量与条件更新各接受几次意图。
4. 一页契约说明、卡片补一例、一次局部 AI 对照。课堂记录直接复用，不重复交截图套件。

教师包代办模型迁移、旧详情／创建接线、OpenAPI 生成和同步工具，学生执行并核对；不要求另写并发平台、全量接口、独立前端、类型生成或新 CI。本课还不是 M3 交付，第 9 课将这些验收变成至少八条关键路径测试。

## 八、选做与第 9 课交接

### 8.1 B 档：隔离的幂等键练习

只针对同一 PostgreSQL 事务内的业务，不牵涉支付、邮件等外部副作用。可以研究“操作范围 + key”唯一约束、请求指纹、结果快照：同键同内容重放已完成结果，同键不同内容拒绝；业务写入和结果记录同事务提交。说明并发抢占、过期和结果未知的边界，不承诺无限期恰好一次。

本课没有认证 principal，隔离练习用教师明确分配的虚构调用者范围，不能把客户端随意提交 user_id 当可信身份。第 14 课后才绑定认证身份。重放业务结果也不照搬旧 request-id，当前请求仍有自己的日志关联。

“一人一票”需要身份与投票记录的唯一关系，和本课的修订号计数器不是一个需求；不要求新增第六张业务表。ETag/If-Match 是另一种条件协议，失败通常用 412，本课 JSON version 固定 409，不混用。

### 8.2 下一课的明确输入

- 001_baseline → 002_question_version；数据库 body 不改名；五表约束、标签顺序和公开列表保持 M2 基线。
- 列表五字段；详情／创建／PATCH 七字段；投票 qid/vote_count/version；创建输入仍不收新字段。
- 版本正整数、PATCH 字段语义、404／两种 409 与四字段错误、request-id、200/201/303 提交时机。
- 三种受控并发轨迹、四情境、同一旧版本重复写入拒绝、M2 两种故障位置；真实提交测试必须独立查库。
- 教师提供 OpenAPI 导出／check 入口与最小类型消费者，分别标注要求会用／黑盒；学生本课不必先会 TypeScript。

第 9 课底稿已按 v4 重写：先写正确创建测试，使用独占 schema 与真实服务提交，再按固定 25 条数据定位分页缺陷；保留四件证据关联、四门禁／分支保护和 M3 一个作业包。已区分提交前／确认后同为 500 的数据结果，不将本课四情境变成额外工具考试。独立课程包、目标 PostgreSQL 16、真实 CI／保护与课堂断点证据仍须按第 9 课制作清单落地验收。

## 九、教师附录：数据增量、DTO 与真实端点接线

### 9.1 模型与 002 迁移

以下完整 Question 定义**替换**第 7 课模型中的同名类，不与旧映射同时注册。Base、Mapped、relationship、其余四表及导入来自第 7 课模型模块，另外导入 Integer；所有外键与原约束保持。

```python
# lesson08: question_model
from sqlalchemy import Integer


class Question(Base):
    __tablename__ = "questions"
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    title: Mapped[str] = mapped_column(Text(collation="C"))
    body: Mapped[str] = mapped_column(Text)
    author_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.id", name="questions_author_id_fkey"))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    vote_count: Mapped[int] = mapped_column(Integer, server_default="0")
    version: Mapped[int] = mapped_column(Integer, server_default="1")
    answers: Mapped[list["Answer"]] = relationship(back_populates="question", passive_deletes="all")
    tag_links: Mapped[list["QuestionTag"]] = relationship(
        back_populates="question", order_by="QuestionTag.position", passive_deletes="all",
    )
    __table_args__ = (
        UniqueConstraint("title", name="questions_title_key"),
        CheckConstraint("char_length(title) BETWEEN 5 AND 200", name="questions_title_len"),
        CheckConstraint("char_length(body) BETWEEN 10 AND 20000", name="questions_body_len"),
        CheckConstraint("vote_count >= 0", name="questions_votes_nonneg"),
        CheckConstraint("version >= 1", name="questions_version_positive"),
    )
```

迁移文件为固定版本代码，不 import 当前业务模型；保留第 7 课基线，不重写历史迁移。

```python
# lesson08: migration
from alembic import op
import sqlalchemy as sa

revision = "002_question_version"
down_revision = "001_baseline"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("questions", sa.Column("vote_count", sa.Integer(), nullable=False, server_default="0"))
    op.add_column("questions", sa.Column("version", sa.Integer(), nullable=False, server_default="1"))
    op.create_check_constraint("questions_votes_nonneg", "questions", "vote_count >= 0")
    op.create_check_constraint("questions_version_positive", "questions", "version >= 1")


def downgrade():
    op.drop_constraint("questions_version_positive", "questions", type_="check")
    op.drop_constraint("questions_votes_nonneg", "questions", type_="check")
    op.drop_column("questions", "version")
    op.drop_column("questions", "vote_count")
```

教师独立工程已安装锁定依赖、已完成第 7 课 Alembic 配置后，在备份副本执行：

```bash
uv run --no-sync alembic current
uv run --no-sync alembic upgrade head
uv run --no-sync alembic current
```

核对 current 从 001 到 002；旧问题 id/title/body/created_at、作者、标签与关联不变，全部旧行初始为 0／1，新行省略两列也为 0／1。迁移不会把课堂指定 101 自动变成 10／5，实验复位是另一步。

升级后用新模型／路由，暂不并发混跑不维护版本的旧写者。普通 CHECK 不替代 NOT NULL，两者都核对。downgrade 会丢票数／版本，再升级只得到默认值，不能恢复历史投票；不在唯一数据上试。正式发布的锁等待、停机窗口与多版本兼容留给第 16 课，不用本地小库瞬时完成承诺线上无锁。

### 9.2 详情／创建扩展，列表不跟着漂移

```python
# lesson08: detail_adapter

def read_versioned_question_dto(session, qid):
    statement = (
        select(Question).where(Question.id == qid).options(tag_load_option())
        .execution_options(populate_existing=True)
    )
    question = session.scalar(statement)
    if question is None:
        return None
    return QuestionDetailOut(
        id=question.id, title=question.title, body=question.body,
        tags=[link.tag.name for link in question.tag_links],
        created_at=question.created_at,
        vote_count=question.vote_count, version=question.version,
    )


def get_question_service(session, qid):
    result = read_versioned_question_dto(session, qid)
    if result is None:
        raise QuestionNotFound()
    return result


def create_question_service(
    session, payload, *, author_id, after_flush=no_fault, after_commit=no_fault,
):
    try:
        question = write_question(session, payload, author_id=author_id)
        session.flush()
        after_flush()
        result = read_versioned_question_dto(session, question.id)
        if result is None:
            raise RuntimeError("创建后的回读缺失")
        session.commit()
        after_commit()
        return result
    except IntegrityError as exc:
        session.rollback()
        constraint = getattr(getattr(exc.orig, "diag", None), "constraint_name", None)
        if getattr(exc.orig, "sqlstate", None) == "23505" and constraint == "questions_title_key":
            raise DuplicateTitle() from exc
        raise
    except Exception:
        session.rollback()
        raise
```

write_question、tag_load_option 直接复用第 7 课；服务接收的 Session 不含别的业务待提交工作。populate_existing 负责刷新之前已加载的对象，本例不存在需要保留的未刷写编辑；不要拿它无条件覆盖其他未完成操作的内存状态。列表仍调用旧 list_questions_orm／question_to_dto，输出 QuestionListOut 中的原五字段。

### 9.3 端点与 OpenAPI 声明一起接

本段替换原创建／详情注册，并新增投票／PATCH；不能留下两个同路径同方法的端点，也不把正文数据库列改名。router 挂载到已注册第 4 课处理器／中间件的 FastAPI 应用，SessionDep 来自第 7 课，固定虚构作者来自教师配置（示例为 1）。

```python
# lesson08: routes
from fastapi import Response


ERROR_RESPONSES = {status: {"model": ErrorOut} for status in (404, 409, 422, 500)}


@router.get("/questions/{qid}", response_model=QuestionDetailOut, responses=ERROR_RESPONSES)
def get_question(qid: int, session: SessionDep):
    return get_question_service(session, qid)


@router.post("/questions", status_code=201, response_model=QuestionDetailOut, responses=ERROR_RESPONSES)
def create_question(payload: QuestionCreate, response: Response, session: SessionDep):
    result = create_question_service(session, payload, author_id=1)
    response.headers["Location"] = f"/questions/{result.id}"
    return result


@router.post("/questions/{qid}/votes", response_model=VoteOut, responses=ERROR_RESPONSES)
def vote_question(qid: int, payload: VoteIn, session: SessionDep):
    return vote_question_service(session, qid, payload)


@router.patch(
    "/questions/{qid}", response_model=QuestionDetailOut, responses=ERROR_RESPONSES,
    description="version 必填；title/body 至少提供一个，省略保持，显式 null 拒绝；仅版本匹配时修改。",
)
def patch_question(qid: int, payload: PatchPayload, session: SessionDep):
    return patch_question_service(session, qid, payload)
```

成功响应模型必须实际换成 QuestionDetailOut；只在 ORM 加列却仍按旧模型过滤，会把 version 丢掉。ERROR_RESPONSES 是声明，不负责运行时翻译；VersionConflict 必须继承并接入既有 AppError 映射。新接口 422 声明覆盖默认 FastAPI 错误模型，实际 detail 仍按旧处理器脱敏。

教师复用导出入口以 `app.openapi()` 生成规范化 JSON，固定键排序、缩进、末尾换行；check 只比较、不自动覆盖。正式脚本由第 9 课提供并接门禁，本课只按模板读 `/openapi.json` 与报文、在一页说明中登记增量。导出不应启动服务器、自动迁移或要求访问数据库；新增声明不能自动证明所有业务约束。

## 十、制作与验证状态

本轮底稿与最终课程包分开验收，不沿用旧第 8／9 课合计的 SQLite 检查结果。

- **本轮实测完成**：提取本稿 11 个 Python 围栏，复用第 3 课真实输入／输出模型、第 4 课错误／追踪代码、第 6 课 seed 和第 7 课模型／服务／迁移。完成 420 项检查（包含 11 项围栏语法、3 项课时检查），专用数据库正常停机再启动后另通过 2 项独立回读，累计 **422 项**；重复执行不累加计数。
- **环境与隔离**：Python 3.12.12、FastAPI 0.141.1、Pydantic 2.13.5、SQLAlchemy 2.0.54、psycopg 3.3.6、PostgreSQL **18.6**／UTF-8，测试会话为 UTC／READ COMMITTED。复用前课工作区专用集群，仅新建 l08 独立 schema；仅监听权限 0700 的本地 Unix socket，不连接既有业务库。复用 `.build-check/lesson07-tools` 中 Alembic 1.20.0 等临时依赖，本课没有新增安装或修改项目锁文件／原虚拟环境；核验后已停库。
- **正常路径与输入实测**：新旧行默认值、创建七字段与原列表五字段／字面搜索／排序、严格正整数版本、PATCH 省略／null／长度／额外键、标签保序；核对缺失、陈旧、删除后请求、未来版本的业务分类与拒绝后无误写。删除用独立无引用问题，不绕过主 seed 外键。
- **真实并发实测**：两独立连接读取相同 10／5 后放行，常量覆盖得到两成功与 11／6，原子增量得到两成功与 12／7，条件版得到一成功一冲突与 11／6；逐次核对返回值。另观察实际等锁后重检旧版本失败，以及投票／PATCH 共用版本时只接受一个写者。这些是服务级受控实验，不称为网络压测。
- **PATCH 与故障实测**：单字段／双字段／相同文本补丁、旧 ORM 对象刷新、命名标题冲突连版本一同回滚；计数／版本溢出及输出校验错误不冒充业务 409／输入 422。服务与最小 HTTP 装配均覆盖提交前故障无本次更新、提交确认后故障仍有更新，以独立连接回读，不用外层事务回滚替代提交证据。
- **最小 HTTP／OpenAPI 实测**：真实路由、资源依赖与服务经过临时 FastAPI 装配，核对 201+Location、投票／PATCH 200、404／409／422／500、GET 投票 405 与 Allow、错误四字段及 422 的 loc/type/msg、request-id 起止日志和资源关闭、commit 早于响应。两个 TestClient 先读取相同版本再投票，得到 200／409 和独立库状态；这属于进程内 HTTP 链，不经过真实端口。OpenAPI 导出时零数据库 SQL，列表／详情字段分开，PATCH 必填／非 nullable 和错误响应声明正确；跨字段规则仍由说明与运行测试补足。
- **真实 Alembic 实测**：从本稿和第 7 课提取固定 001／002 与在线 env 主体，通过 Alembic 命令 API 核对带 seed 的 001 升级保留五表旧数据、旧行／新行默认 0／1、002 版本与新增 CHECK／NOT NULL；另一个空 schema 完整升级、重复升级、check 通过。迁移目标没有预先 create_all；普通服务 fixture 与迁移实验分开。只在可丢弃副本回退再升级，确认票数／版本历史不能恢复。
- **正常重启回读**：核对并发最终 11／6 和提交确认后故障留下的 PATCH 正文仍在。首次启动因沙箱共享内存权限失败，按原本地隔离参数恢复启动后完成回读；不将启动权限问题或正常重启当成提交期间断连／崩溃恢复实验。
- **正式素材待制作**：独立第 8 课起点／完成版、正常／缺陷隔离应用、教师迁移与 DTO 接线、四情境数据、连接身份／同步超时／复位工具、故障入口、契约说明模板与备用记录。不得将临时核验脚本称为已交付教学工具。
- **目标环境与全工程待验收**：PostgreSQL 16、真实 M2 数据升级、完整 JSON／HTML／探针回归、浏览器与 Uvicorn 网络链、正式命令／锁文件。未做的内容逐项保留，不用模型编译或服务测试代替。
- **试讲负荷待验收**：学生能否在 25 分钟内完成条件更新并解释四情境；PATCH 模板能否支持 10 分钟正常讲解；不靠挤掉实践时间容纳工具内部细节。

临时复核入口（依赖上述临时工具目录与已启动的专用数据库 socket，不是学生启动命令）：

```bash
uv run --offline --project snippets/ch01/m0-tracer --no-sync python .build-check/validate_lesson08.py
```

本轮 TestClient 仍有 Starlette 对 httpx 适配的弃用提示，未为消除提示升级依赖；IDE 语言服务未就绪，不声称 lint 全绿。最终 Slidev、视觉／导出和真实课堂试讲未在本轮进行。

参考：PostgreSQL 16 Transaction Isolation／UPDATE、SQLAlchemy 2.0 ORM UPDATE 与 populate_existing、RFC 9110 的安全／幂等定义、Pydantic TypedDict／校验器、FastAPI Additional Responses。制作最终 Slidev 时，教师时间、应急切换与制作待办放备注，学生所需规则、操作前提与证据边界留正文。
