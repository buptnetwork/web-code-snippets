# 第 8 次课教学底稿（修订版）
## API 契约设计与写操作正确性

## 〇、备课定位与内容取舍

本课承接合格 M2：已经能持久化、管理事务和迁移，但“事务内执行”不等于“多个请求不会互相覆盖”，“客户端没收到成功”也不等于“服务端没有提交”。主线是：**先说明一次写操作承诺什么，再用并发、重试和响应证据核对承诺。** 契约包含方法、参数、状态、数据结构和业务语义，不只是字段类型。

原稿把本课变成了 Vite、类型生成和三个前端页面的实现课，遗漏并发写入；还误把第七课数据库列改名当成公开 API 改名。修订后恢复大纲主线。类型生成保留为 B 档参考，第十课学习前端工程化，第十一至十三课再构建 React 页面，不在今天重复造一套 UI。

### 课堂路线：75 分钟教学 + 20 分钟诊断小测 + 5 分钟缓冲

| 单元 | 分钟 | 课堂处理 |
|---|---:|---|
| 一、起点与写操作解剖 | 5 | GET 投票、先查再改与重试三个问题 |
| 二、资源、方法和可观察契约 | 8 | 方法判据与成功含义 |
| 三、丢失更新与条件写入 | 24 | 唯一学生现场必做；中途核对初始状态 |
| 四、PUT/PATCH 与输入边界 | 10 | PATCH 教师演示，完整接入课后复做 |
| 五、幂等与提交结果未知 | 9 | 时间线与方案选择，不现场造防重平台 |
| 六、列表与 OpenAPI 交付 | 12 | 稳定排序、白名单、错误声明与快照 |
| 七、交付与收尾 | 7 | 验收清单与 AI 约束 |
| 教学合计 | 75 | 另有小测 20、缓冲 5 |

小测在教学单元后进行，不额外叠加到 100 分钟之外。超时压缩类型生成演示和方法变体，保留并发证据、409 含义和小测。A 档包含课后基础复做；B 档完全选做，不能标成“B 档必交”。

### 输入基线与允许变更

| 已有能力 | 本课处理 |
|---|---|
| `GET /questions` | 保留 `keyword/page/page_size`；page≥1、page_size 默认20、范围1—50；容器仍为 `items/total/page` |
| 列表项 | 保留 `id/title/created_at/author={id,display_name}`，不默认已有 answer_count、tags 或 has_next |
| 详情和创建 | `GET /questions/{qid}`、`POST /questions`；HTTP 字段仍叫 `body`；创建201＋Location |
| 创建输入 | title 先 strip 后长度5—200；body 先 strip 后长度10—20000；tags 最多5项、可省略；拒绝额外字段 |
| 错误 | 第四课 `code/message/detail/request_id`；422 的 detail 是 `loc/type/msg` 列表 |
| HTML 与探针 | 保留第五课 SSR 页面与 `/healthz` 的200/503正文；不统一改成业务 JSON |
| 持久层 | 第七课五表、函数作用域事务、001/002迁移；数据库 `content` 对应 Python/API 的 `body` |
| 本课批准的增量 | 问题增加 `vote_count/version`；详情/创建输出增加这两项；新增投票与 PATCH；列表新增 sort/status 白名单 |

列表摘要不必增加版本字段；写操作前从详情获取版本。客户端仍须接受原有字段，不把增加两个输出字段当成全面换约。课堂固定虚构作者身份，不声称已有认证或“一人一票”；写端点只在本地教学环境开放，第十四课补认证与对象授权。

文中为教学参考与配套工程规格；尚不存在的迁移、runner、tag 和截图不能写成已交付资产。正式制作须锁定 Python/FastAPI/SQLAlchemy/PostgreSQL/Alembic 版本并完成文末验收。

## 一、解剖台：200、事务和按钮禁用都不够

**课堂 5 分钟。** 使用教师构造的缺陷样本，明确标注来源；真实 AI 输出另行记录，不要求它一定有错。

```python
# 预期缺陷示意，不接入最终工程。
@router.get("/questions/{qid}/vote")
def vote(qid: int, session: SessionDep):
    question = session.get(Question, qid)
    question.vote_count = question.vote_count + 1
    return {"ok": True}
```

三个独立问题：

1. GET 被设计为读取，不应用于投票等业务写入；预取、爬虫或重复访问都可能触发它。
2. `SELECT → 在内存加一 → UPDATE 常量` 即使位于事务内，也可能覆盖另一个请求的结果。
3. 禁用按钮、PRG 和事务都不自动识别“这是同一个意图的重试”。

讲：今天不凭“看起来专业”判断代码。把两次请求的旧值、新值、状态和最终数据库值排在一起，才能知道系统兑现了什么。

## 二、从资源与方法写出验收标准

**课堂 8 分钟。** URI 主要描述资源；方法表达操作性质。但资源化命名本身不解决并发、权限或重试。

### 2.1 本课端点表

| 方法与路径 | 成功与输入 | 失败/边界 |
|---|---|---|
| GET `/questions` | 200；筛选后稳定排序分页 | 非法参数422；读操作无投票副作用 |
| GET `/questions/{qid}` | 200；原详情＋vote_count/version | qid非法422；缺失404 |
| POST `/questions` | 原创建契约；201＋Location；版本初值1、票数0 | 校验422；标题唯一冲突409；不是通用防重接口 |
| POST `/questions/{qid}/votes` | `{"version":1}`；200返回 `qid/vote_count/version` | 缺失404；版本过期409；输入422 |
| PATCH `/questions/{qid}` | 必填version；至少一个title/body字段；200返回更新后详情 | 缺失404、版本/标题冲突409、输入422 |

投票这里定义为**接受一次计数加一意图**，不是创建可查询的 Vote 资源，因此成功用200而非虚构一个资源 Location。系统允许同一演示身份多次主动投票；真实一人一票模型放在第五单元拓展。

### 2.2 方法性质与幂等的严格含义

幂等：多次相同请求对服务端的**预期效果**与一次相同；不要求每次响应体、状态码、日志条数完全相同。安全：客户端请求的语义是读取，不要求服务器连访问日志都不能写。

| 方法 | 通常语义 | 不能推出的结论 |
|---|---|---|
| GET | 安全、幂等读取 | GET 请求体能稳定承载业务参数；任何实现都不会写库 |
| PUT | 替换目标资源的可写表示，按协议语义幂等 | 只要命名 PUT 就自动防重；一定把数据库每列覆盖 |
| PATCH | 应用部分修改，幂等性由补丁语义决定 | PATCH 天生幂等或天生不幂等 |
| POST | 由目标资源处理请求，通常不承诺幂等 | 永远无法做防重 |
| DELETE | 删除的预期效果幂等 | 第二次必须与第一次返回相同状态 |

`PATCH {"title":"固定标题"}` 与“把票数加一”不是同一种效果；使用版本条件后，同一旧版本的再次提交可以返回409，同时避免重复改变数据。409仍不是“原请求成功”的证明。

短写请求的成功含义继续沿用第七课：**事务提交成功后才发送200/201/303**。`Depends(get_session, scope="function")` 必须实际用于新端点，不能只在参考代码里定义别名。

## 三、现场必做：两个请求都成功，为什么只多一票

**课堂 24 分钟。** 前8分钟复现，中间10分钟修复，后6分钟核对边界。准备两个独立连接/Session；不能跨线程共享 Session，也不能用单连接事务 fixture 冒充并发。

### 3.1 先明确数据与迁移

在第七课 `002_body_content` 后增加 `003_question_version`。模型新增：

```python
vote_count: Mapped[int] = mapped_column(Integer, server_default="0")
version: Mapped[int] = mapped_column(Integer, server_default="1")
# 加入 Question.__table_args__：
CheckConstraint("vote_count >= 0", name="questions_votes_nonneg")
CheckConstraint("version >= 1", name="questions_version_positive")
```

迁移主体参考，保留实际 revision/down_revision 元数据；不在历史迁移中 import 当前业务模型：

```python
from alembic import op
import sqlalchemy as sa

def upgrade():
    op.add_column("questions", sa.Column(
        "vote_count", sa.Integer(), nullable=False, server_default="0"))
    op.add_column("questions", sa.Column(
        "version", sa.Integer(), nullable=False, server_default="1"))
    op.create_check_constraint("questions_votes_nonneg", "questions", "vote_count >= 0")
    op.create_check_constraint("questions_version_positive", "questions", "version >= 1")

def downgrade():
    op.drop_constraint("questions_version_positive", "questions", type_="check")
    op.drop_constraint("questions_votes_nonneg", "questions", type_="check")
    op.drop_column("questions", "version")
    op.drop_column("questions", "vote_count")
```

旧行得到票数0、版本1；两字段非空。回退会丢票数和版本，**不是保数据回退**，只能在副本演示并说明备份或前向修复方案。保留第七课已经验证的正文改名迁移，不把它重新做成公开接口改名。

### 3.2 受控复现：先读到同一个旧值，再放行写入

初始指定测试问题：`vote_count=10, version=1`。使用 PostgreSQL READ COMMITTED、两个独立事务；教师 runner 在两次 SELECT 后设置 `Barrier(2, timeout=5)`，双方都读取后才各自继续写。

```python
# 预期缺陷 service，仅注册在独立本地实验应用。
def vote_broken(session, qid, after_read):
    question = session.get(Question, qid)
    if question is None:
        raise QuestionNotFound()
    before = question.vote_count
    after_read()  # 测试同步点，不暴露成可被远程控制的生产参数。
    question.vote_count = before + 1
    session.flush()
    return {"qid": qid, "vote_count": question.vote_count}
```

| 时刻 | 请求A | 请求B |
|---|---|---|
| 读取 | 10 | 10 |
| 同步点放行 | 准备写11 | 准备写11 |
| 写入并提交 | UPDATE 为11 | 等待行锁后 UPDATE 为11 |
| 最终 | 两个成功响应，数据库11 | 预期两个意图应为12 |

这是指定调度下的预期结果，不是说每次随机并发都会丢失。Barrier只用于控制实验，不使用 `SELECT FOR UPDATE`，否则会在读取阶段阻塞而无法同时到达同步点。设置等待超时并输出失败位置；不靠反复 sleep 碰运气。

### 3.3 修复：把“仍是我读到的版本”放进写语句

前端先读取详情，两次意图都基于version=1提交。repository 核心：

```python
from sqlalchemy import select, update

def vote_once(session, qid, expected_version):
    statement = (
        update(Question)
        .where(Question.id == qid, Question.version == expected_version)
        .values(vote_count=Question.vote_count + 1, version=Question.version + 1)
        .returning(Question.id, Question.vote_count, Question.version)
        .execution_options(synchronize_session=False)
    )
    row = session.execute(statement).mappings().one_or_none()
    if row is not None:
        return {"qid": row["id"], "vote_count": row["vote_count"],
                "version": row["version"]}
    if session.scalar(select(Question.id).where(Question.id == qid)) is None:
        raise QuestionNotFound()
    raise VersionConflict()
```

对应 SQL 形态：

```sql
UPDATE questions
SET vote_count = vote_count + 1, version = version + 1
WHERE id = :qid AND version = :expected_version
RETURNING id, vote_count, version;
```

**版本判断与写入必须是同一条原子语句。** 在 Python 中先比较version再无条件UPDATE，仍有竞争窗口。PostgreSQL READ COMMITTED 下等待另一写者完成后，UPDATE会对更新后的行重新判断条件；旧version不再匹配。

这里用 RETURNING 有无结果判断是否匹配，也可在驱动可靠支持时检查影响行数。关闭ORM状态同步后，不从旧的已加载对象拼响应；投票使用返回行，PATCH重新查询时须刷新对象。业务异常继承第四课 `AppError`；HTTP边界新增映射：

```python
BUSINESS_HTTP[VersionConflict] = (409, "version_conflict", "资源已变化，请刷新后确认")
```

继续使用既有统一处理器，不在 service 写 HTTPException。没有匹配行后的二次查询只能报告当时的资源状态；并发删除会影响404/409分类，不承诺“存在性判断与前一语句同一快照”。课堂不安排并发删除。

输入、输出与路由接线参考：

```python
from typing import Annotated
from fastapi import Path
from pydantic import BaseModel, ConfigDict, Field

class VoteIn(BaseModel):
    model_config = ConfigDict(extra="forbid")
    version: int = Field(ge=1, strict=True)

class VoteOut(BaseModel):
    qid: int
    vote_count: int = Field(ge=0)
    version: int = Field(ge=1)

@router.post("/questions/{qid}/votes", response_model=VoteOut,
             responses={404: {"model": ErrorOut}, 409: {"model": ErrorOut}})
def vote_question(qid: Annotated[int, Path(ge=1)],
                  payload: VoteIn, session: SessionDep):
    return vote_once(session, qid, payload.version)
```

router继续继承第四课422/500声明，ErrorOut、SessionDep、异常与Question从配套工程的现有模块导入。必须实际更新详情/创建的响应模型和DTO；仅在ORM加字段、却从未返回version，客户端就无法完成条件写入。

### 3.4 四组验收与结论

| 请求安排 | 应观察到 | 能说明什么 |
|---|---|---|
| 缺陷版，两次读完再写 | 200/200，最终11 | 一次增量被覆盖 |
| 修复版，两次都携带version=1 | 200/409，最终11、version=2 | 拒绝陈旧写入；**不是两票都已接受** |
| 冲突方刷新、用户确认另一次意图后携带version=2 | 200，最终12、version=3 | 重做的是新的已确认操作 |
| 再发送旧version=1；另测不存在qid | 409且值不变；缺失资源404 | 冲突与缺失的响应和数据边界 |

提交证据包含两份请求体、两份状态/错误code、SQL条件、最终新连接查库结果。请求使用不同request-id；id用于关联，不等于幂等键。初始数据由独立seed恢复，不覆盖学生唯一数据库。

### 3.5 为什么不直接使用原子加一

```sql
UPDATE questions SET vote_count = vote_count + 1 WHERE id = :qid;
```

对于“不依赖旧状态、每个独立请求都应计数”的业务，原子加一往往更合适，两个并发成功可以得到12。**它仍会把网络重试当成另一次加一。** 本课用投票教授条件写入，不把乐观锁说成计数器唯一正确方案；它更典型地用于“基于我看到的旧内容编辑”。下一单元正好将同一思想用于改帖。

## 四、PUT/PATCH：缺省、清空和覆盖不是一回事

**课堂 10 分钟；代码细节课后参考。** A 档落地PATCH标题/正文；PUT做契约判据与模型对照，不要求再造一个全量编辑端点。

### 4.1 定义本课 PATCH

```json
{"version": 3, "title": "修改后的有效标题"}
```

本例是课程自定义JSON部分更新，不自称 JSON Patch 或 JSON Merge Patch：

- version必须提交，只用于条件判断，不让客户端指定新版本。
- title/body可省略，省略表示保持；显式null拒绝422，因为这两列不允许为空。
- 空白值先strip，再按创建规则校验；至少提供title/body之一。
- tags、author_id、vote_count等不属于此补丁，拒绝额外字段；本课不暗中改作者或标签。
- 匹配版本时只更新提供字段并version+1；陈旧版本409；标题唯一约束仍翻译duplicate_title。

### 4.2 完整输入参考：可省略不等于可空

以下选择 TypedDict 表示“键可缺少，但出现时必须是字符串”，由Pydantic负责校验；这是配套模板，不要求初学者记忆 typing 的全部API。

```python
from typing import Annotated
from typing_extensions import Required, TypedDict
from pydantic import AfterValidator, BeforeValidator, ConfigDict, Field, with_config

def strip_text(value):
    return value.strip() if isinstance(value, str) else value

Title = Annotated[str, BeforeValidator(strip_text), Field(min_length=5, max_length=200)]
Body = Annotated[str, BeforeValidator(strip_text), Field(min_length=10, max_length=20000)]

@with_config(ConfigDict(extra="forbid"))
class QuestionPatch(TypedDict, total=False):
    version: Required[Annotated[int, Field(ge=1, strict=True)]]
    title: Title
    body: Body

def require_change(value):
    if not ({"title", "body"} & value.keys()):
        raise ValueError("至少提供title或body")
    return value

PatchPayload = Annotated[QuestionPatch, AfterValidator(require_change)]
```

FastAPI端点参数写 `payload: PatchPayload`，得到已经清洗过的字典。OpenAPI中version必填、title/body非必填且非nullable；“至少一项修改”仍需在operation描述和运行测试中核对，普通AfterValidator不会自动生成全部业务约束。

```python
# repository主体；复用第三单元未匹配时的404/409判断。
changes = {name: payload[name] for name in ("title", "body") if name in payload}
statement = (
    update(Question)
    .where(Question.id == qid, Question.version == payload["version"])
    .values(**changes, version=Question.version + 1)
    .returning(Question.id)
    .execution_options(synchronize_session=False)
)
updated_id = session.scalar(statement)
# updated_id为None时抛业务异常；匹配后用populate_existing重新读取详情与作者、构造DTO。
```

新版本与票数、既有详情字段一起返回。不可先 `get` 比较后无条件写，也不可把payload中的version直接写回旧值。所有修改同一资源的课程写路径都要遵守版本递增规则；绕过它的其他写者会使保护失效。

常见错误：把部分更新模型直接dump后覆盖全部列；或者一律过滤None，悄悄把非法null当成未提交。使用BaseModel方案时通常需要 `exclude_unset=True` 保留“有没有提交”的信息，但这并不自动定义null的业务含义。

### 4.3 PUT 的替换边界

若另行设计PUT，先定义完整**可写表示**。例如title/body/tags全部必填；tags省略不是“保留旧标签”，空列表才是明确清空。id、作者身份、票数等服务端管理字段不由客户端覆盖；不存在目标时选创建还是404也须明文约定。本课程对照方案选择仅替换已有资源、缺失404。

```python
# PUT设计参考，不作为A档新增端点。
class QuestionReplace(QuestionCreate):
    tags: list[str] = Field(max_length=5)  # 不继承创建时的省略默认值。
    version: int = Field(ge=1, strict=True)
```

若将它实现为条件PUT，同一个旧version的第二次请求可以409，不要求响应相同。服务端修订号、审计记录不是协议中“替换内容”的全部预期效果。不要用PUT/PATCH命名掩盖“增加余额/票数”这种增量语义。

## 五、幂等、重试与提交结果未知

**课堂 9 分钟；幂等键工程实现为B档。** 回收第二课方法矩阵、第五课PRG、第七课提交时断线。

### 5.1 同一条时间线，三种不同问题

```text
客户端发POST → 数据库提交成功 → 响应在途中丢失
客户端只看到超时 → 再发一次POST → 服务端如何识别同一意图？
```

| 手段 | 能解决 | 不能解决 |
|---|---|---|
| 事务 | 一个操作内部全部成功或回滚 | 不自动防止两个事务互相覆盖 |
| 版本条件 | 拒绝基于陈旧状态的写入 | 不直接提供第一次成功的响应或身份防重 |
| 原子加一 | 不丢独立增量 | 不识别相同意图重试 |
| UNIQUE(title) | 执行业务标题唯一规则 | 不证明409对应的帖子就是刚才那次创建，也不重放结果 |
| PRG/按钮禁用 | 减少刷新或交互重复 | 不替代服务端防重或并发控制 |
| 幂等键/稳定操作ID | 在约定范围内识别同一意图 | 不自动提供授权或无限期“恰好一次” |

本课保留标题唯一约束，不能先删掉它来演示主项目“同标题重复发帖”。若展示重复记录，使用明确允许重名的隔离模型；主项目则展示超时后409仍无法仅靠状态确认第一次结果。

A档规则：没有专门防重协议的POST，客户端不得在结果未知时自动循环重试。版本冲突先读最新状态并确认意图；不能收到409就自动刷新version不断加票。

### 5.2 幂等键的参考设计（课后B档）

限定同一PostgreSQL事务中的创建，不牵涉支付、邮件等外部副作用。建议记录：

| 数据 | 作用 |
|---|---|
| principal + method + route + key 的唯一约束 | 防不同用户/不同操作串用，仲裁并发抢占 |
| 规范化请求指纹 | 同键不同内容返回409，不能重放另一个请求的结果 |
| 业务资源ID、状态与结果快照 | 同键同请求重放原结果；保留原Location等业务头 |
| 创建时间、过期策略 | 明确有效期、容量与过期后重试边界 |

事务内先争取唯一键，再执行业务写入并保存结果，**同事务提交**；失败全部回滚。竞争者用唯一约束等待/判定，原事务提交后读取其已完成记录；不能先查内存字典再无条件插入。PostgreSQL可用 `INSERT ... ON CONFLICT DO NOTHING RETURNING`，后续读取的可见性按READ COMMITTED验证。

同键同请求即使重试，也只产生一次业务写入；同键异请求拒绝。重放业务结果时当前请求的request-id仍须与本次日志一致，不盲目复制第一次的追踪头。只保存必要安全字段；过期、并发删除、跨资源副作用需要额外方案，不包装为通用分布式“恰好一次”。

### 5.3 “一人一票”是另一条业务规格

若以后规定每人每题最多一票，应建投票记录并加 `UNIQUE(question_id, user_id)`；身份来自服务端认证而非任意提交的user_id。可用 `PUT /questions/{qid}/my-vote` 表示当前用户投票状态，再选择聚合计数或同事务维护冗余计数。本课A档不增加第六张业务表，不宣称计数器已完成真实投票系统。

HTTP条件写入拓展：ETag/`If-Match`也能表达“仅在版本匹配时写入”，前置条件失败通常是412；本课JSON version冲突用409。它不同于第十二课前端“乐观UI更新”，不再把未安排的ETag教学承诺给后课。

## 六、把 API 交付成能核对的契约

**课堂 12 分钟；完整检查和类型生成留课后。** 单体描述部署/组织边界，前后端分离描述通信和交付方式；单体也可以用HTTP。Python函数调用不天然有编译期检查，TypeScript类型也不自动验证网络JSON。

### 6.1 筛选、排序与分页

新增公开参数：`sort`允许 `created_at/title/view_count`，默认created_at，均降序且id降序决胜；`status`允许 `open/closed`，默认open。deleted不在普通列表公开；这是批准的能力扩展，不把第七课实验参数误当成早已发布。

```python
SORTS = {"created_at": Question.created_at, "title": Question.title,
         "view_count": Question.view_count}
# router用Literal/枚举校验sort/status，service仅接收已验证值。
conditions = [Question.status == status]
if keyword:
    pattern = literal_pattern(keyword)  # 沿用第六课 !/%/_ 的字面转义。
    conditions.append(or_(Question.title.ilike(pattern, escape="!"),
                          Question.body.ilike(pattern, escape="!")))
stmt = (
    select(Question).where(*conditions)
    .options(selectinload(Question.author))
    .order_by(SORTS[sort].desc(), Question.id.desc())
    .offset((page - 1) * page_size).limit(page_size)
)
total_stmt = select(func.count()).select_from(Question).where(*conditions)
```

对应新增参数签名 `sort: Literal["created_at", "title", "view_count"] = "created_at"`、`status: Literal["open", "closed"] = "open"`，非法值进入既有422处理器。

绑定参数用于**值**，列名/排序方向须映射受控表达式，不能任意getattr或拼接SQL。白名单缩小可用语法、便于维护，但不代替其他值参数化、LIKE转义或授权。

id决胜保证同一静态数据集有确定顺序；offset不是跨请求快照。翻页期间有插入/删除仍可能重复或漏项，同一请求的count与列表在READ COMMITTED下也可能看到不同已提交状态。A档用固定数据核对结果并说明这个边界；深分页与keyset为第六/七课拓展，不转嫁给讲React的第十一课。

### 6.2 错误声明和真实响应分开看

既有422例子：

```json
{"code":"validation_error","message":"请求参数不合法","detail":[{"loc":["body","title"],"type":"string_too_short","msg":"该字段不符合接口约束"}],"request_id":"l08-422"}
```

客户端按 `detail` 列表与loc映射字段，不读不存在的 `detail.fields`。message可显示，code供分支；不要暴露原始input、数据库异常或SQL。未知500、业务404/409、框架405的Allow头、探针503和HTML错误仍保持第四/五课边界。

| 层 | 本课证据 | 不能保证 |
|---|---|---|
| OpenAPI声明 | 每个operation的参数、成功与422/404/409/500模型 | 不自动推断所有异常或验证所有业务语义 |
| 实际响应 | 请求样本＋状态/正文/头，与声明对照 | 几个样本不代表所有输入 |
| 生成类型（B档） | 从已确认快照生成，消费者通过tsc | 不验证线上JSON、权限或防止XSS |
| 业务验收 | 并发、边界和失败后查库 | 不能替代发布时版本协调 |

`responses={422: {"model": ErrorOut}, ...}` 必须接到实际router，覆盖默认422声明；仅定义ErrorOut不会让它自动出现。直接JSONResponse会绕过成功response_model过滤，仍需真实响应检查。SSR不强制声明JSON response_model。

### 6.3 可离线交付的快照

教师配套 `scripts/export_openapi.py` 通过 `app.openapi()` 导出规范化JSON，`sort_keys=True`、固定缩进与末尾换行；`--check`时只比较，不自动覆盖。第九课提供参考实现并进入CI。

学生工程根目录的预期入口：

```bash
uv run python -m scripts.export_openapi
uv run python -m scripts.export_openapi --check
```

交付 `contracts/openapi.json` 与一页契约说明：公开端点、字段、错误语义、分页边界、version规则、哪些POST不承诺重试防重。应用导入不应启动服务器、自动迁移或联网；导出仍须具备后端依赖和合法配置。现场访问 `/openapi.json` 与离线快照应一致。

变更必须先有批准的语义说明，再改实现/测试/快照。自动生成意味着“和当前声明同步”，不意味着声明正确；不能看到差异就更新快照掩盖破坏性变更。

### 6.4 类型生成与最小消费者（B档）

使用教师预装并锁定依赖的 `contract-client` 小模板，不要求实现三个页面；其职责仅为契约消费者检查。`openapi-typescript`和TypeScript写入package-lock，脚本：

```json
{"scripts":{"gen":"openapi-typescript ../contracts/openapi.json -o src/api.d.ts","check":"tsc --noEmit"}}
```

```typescript
import type { components } from "./api";
type Question = components["schemas"]["QuestionOut"];

export function renderTitle(q: Question, node: HTMLElement) {
  node.textContent = q.title;
}
```

实际schema名以生成产物为准；不手写生成文件。试一次字段拼写错误，并记录tsc是否发现；`any`、断言、未纳入tsconfig的文件会削弱检查。没用类型生成也能做契约/运行测试，不把它们贬成“只能人肉grep”。

必填不等于非null；输入放宽与输出放宽对兼容性的影响不同。新增输出字段通常可兼容忽略未知字段的客户端，不保证所有严格消费者都兼容。改名、删除、输出可空化、收紧输入等需审查消费者与发布顺序，不能靠“生成后全绿”批准。

保留第二课四态和错误分类：HTTP错误、正文解析失败、网络异常、渲染异常不能都叫网络断开。任何用户标题、正文、作者名和错误信息都用textContent或安全模板渲染，不拼进innerHTML。联合类型若要检查switch穷尽，需显式 `never` 断言；单独声明联合类型并不强制处理所有分支。

## 七、作业、小测与 M3 交接

**课堂 7 分钟。** 基础作业按教师提供迁移、并发runner和契约导出模板复做，预估3—4小时。不是从零实现通用事务/防重框架。

### 7.1 A 档必交

| 交付 | 验收证据 |
|---|---|
| 保留M2核心能力 | 三个旧JSON端点、SSR和探针回归；body/page_size等名称不漂移 |
| 投票条件写入 | 003迁移与模型；两个独立连接；200/409、最终值与版本；原子加一对照说明 |
| PATCH标题/正文 | 缺省保持、null/空补丁/非法长度422、旧版本409、唯一标题409；其他字段不被改坏 |
| 列表契约 | sort/status白名单；同时间数据的id决胜；筛选与total条件一致；保留page_size边界 |
| 契约交付 | OpenAPI快照＋一页《API契约说明》；错误实例与声明对照 |
| 一次AI协作记录 | 给出规格和可改范围、保留原输出；依据证据决定修复或保留，不要求固定错误数 |

幂等键实现、完整PUT、一人一票、类型生成和发布兼容实验均为B档，任选一项不超过一小时。不将B档变成M3隐形前提；第九课类型门禁的小消费者由教师统一提供。

### 7.2 提示词约束骨架

> 在现有同步FastAPI/SQLAlchemy项目中补全条件投票。保持body、page_size、SSR和healthz契约；version条件必须进入同一UPDATE，失败不改变票数；service不处理HTTP，沿用统一错误和函数作用域事务。先列验收表与改动范围，再给最小diff。禁止取消唯一约束、关闭检查或将同步点暴露到生产。请说明原子加一、版本冲突与幂等重试的区别，并列出尚未验证的条件。

评分看能否说明“哪层保证什么、失败如何观察”，不按文件数量、生成行数或代码速度评分。

### 7.3 20 分钟诊断小测

| 题目 | 分钟 | 核心判据 |
|---|---:|---|
| 两请求读取10各写11，画执行序列 | 6 | 找出丢失更新；事务不等于无竞争 |
| 选择GET/POST/PUT/PATCH并说明重试效果 | 5 | 安全、幂等与相同响应分开 |
| 修读版本更新与PATCH代码 | 5 | 条件写入、缺省/null、409后不能盲重试 |
| 比较OpenAPI与一份422响应 | 4 | detail列表、声明不等于实际保证 |

采用课堂已讲机制的诊断题，不考TypedDict语法、幂等表完整实现或尚未讲授的React。

## 八、素材、验证边界与后课衔接

制作阶段必须补齐：

- 独立第八课工程与锁文件；002→003迁移、无数据丢失的前向检查及回退风险说明。
- 缺陷/修复两个隔离应用、Barrier超时、两个连接身份记录、seed复位和四组并发证据；不假定已有v8 tag。
- PATCH真实路由、共享长度规则、统一异常、详情DTO与version接线；原有JSON/SSR/探针回归。
- 离线快照导出、真实OpenAPI/错误响应、可选类型消费者；无网络备用为标明环境的预录证据。

本轮使用现有Python 3.12、FastAPI 0.141.1、Pydantic 2.13.5、SQLAlchemy 2.0.54环境，对两课合计完成71项语法/机制/时长检查：直接提取正文输入代码，验证PATCH缺省、null、长度、额外字段和OpenAPI形状；用内存SQLite验证条件更新成功、旧版本冲突、缺失资源及最终值，并编译核对PostgreSQL条件UPDATE形态。另有13项实际课时表、JSON、YAML与门禁命令接线检查通过。

完整PostgreSQL并发、Alembic迁移及HTTP配套工程尚未执行，不能把上文预期表写成实测报告。SQLite验证不替代PostgreSQL锁与隔离行为；本轮未安装新依赖。临时检查脚本执行后清理，不作为已经交付的第八课配套工程。

第九课接手这些验收表并转成至少八条关键路径测试、四门禁和AI规约；第十课为所有学生提供Vite/React/TS模板，不能假定人人已完成类型生成或独立前端页面。原第十课底稿的相应前置假设应在后续修订时同步。第十二课复用错误契约处理数据获取失败；版本冲突界面可作为后续适配点，不承诺新增ETag强制实验；第十四课补身份与对象授权，第十六课讨论迁移和发布顺序。

参考：RFC 9110（安全、幂等、条件请求）、RFC 5789（PATCH）、PostgreSQL Transaction Isolation、SQLAlchemy UPDATE/RETURNING、FastAPI Additional Responses与Advanced Dependencies、Pydantic TypedDict校验。以锁定版本和配套实测为准。
