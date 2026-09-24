# 第 9 次课教学底稿（修订版）
## 测试、CI 门禁、AI 协作规约与故障定位 ｜ 交付 M3

## 〇、备课定位与取舍

前八课已经有教师回归检查，不是所有规则都还靠“我记得”。今天把学生从“会运行验收脚本”带到“能根据规格补测试、解释检查失败、约束AI的改动”。**测试验证有限条件下的行为，CI重复执行检查，人工仍负责规格、取舍与证据解释。** 不承诺全绿等于无bug。

原稿主线被十三条纪律、自制AST/元数据检查和并行基础设施挤占，还沿用了前课已取消的“所有列表SQL≤3”“全仓恰好一次commit”。本稿以一个缺陷修复闭环组织课堂；数据库/CI模板由教师提供，学生读懂接线并补业务断言，不现场重写一套质量平台。

### 课堂路线：95 分钟教学 + 5 分钟缓冲

| 单元 | 分钟 | 课堂处理 |
|---|---:|---|
| 一、从规格到可执行证据 | 5 | 回收第八课验收表 |
| 二、解剖台：测试也可能写错 | 10 | 空断言、边界与覆盖率微型对照 |
| 三、测试边界与隔离 | 14 | 读模板，保留生产事务行为 |
| 四、现场必做：补测试并修复分页bug | 20 | 四步定位＋红绿证据，唯一学生主任务 |
| 五、八条关键路径与写操作 | 12 | 并发/提交边界导读；课后补齐 |
| 六、契约检查 | 12 | 快照、实际响应、类型消费者的不同职责 |
| 七、同一入口接入CI | 10 | 教师演示四门禁和合并保护 |
| 八、AI协作规约落地 | 7 | 规格、权限边界、审查与留痕 |
| 九、M3交付与收尾 | 5 | 验收表和后续衔接 |
| 合计 | 95 | 另留5分钟缓冲 |

超时压缩fixture实现细节与B档介绍，不压缩“从规格写断言→失败定位→修复→全套回归”。A档作业3—4小时，允许复用教师基础设施和前课证据。类型生成、并行测试、生成式测试、AST规则和浏览器自动化不是额外隐形必交。

### 本课输入与基础设施边界

- 第八课API：body/page_size不改名；列表items/total/page；详情/创建新增vote_count/version；投票200/409，PATCH缺省/null/版本边界。
- 统一错误沿用第四课；422 detail为loc/type/msg列表；SSR和healthz仍是明确例外。
- Python 3.12、同步SQLAlchemy 2.0、PostgreSQL 16+、支持函数作用域依赖的FastAPI。依赖与锁文件由教师统一，不现场升级版本。
- 教师提供两类测试库：普通串行测试库、真实提交/并发专用可丢弃库；均不使用开发库。
- 教师提供小型 `contract-client` TypeScript消费者及锁文件，让全体学生看到类型门禁；学生不必先完成第八课B档，也不必已经有Vite/React页面。
- 下文路径指**学生问答项目的目标结构**，不是声称本Slidev仓库已有完整第九课应用、脚本、迁移或v9 tag。

## 一、先写“应该怎样”，再决定怎么测

**课堂 5 分钟。** 从第八课三个句子开始：同一个旧版本不能成功写两次；非法输入不能落库；列表页码从1开始。

```text
业务规格/契约 → 可观察预期 → 测试输入与断言
                           ↓
                      当前实现与实际结果
```

规格来源可以是经批准的契约、手算样本、业务规则；不能只把当前实现输出复制到expected。实现可帮助选择测试边界，不应独自决定正确答案。

| 检查 | 能拦什么 | 拦不住什么 |
|---|---|---|
| lint/格式 | 已配置的静态规则、未使用导入等 | 票数是否正确 |
| 类型 | 纳入检查的消费者是否符合声明类型 | 网络JSON真实形状、数据库事务语义 |
| 测试 | 已覆盖场景的行为回归 | 没有被检查的状态与需求错误 |
| 契约 | 快照漂移、样本响应不守约 | 所有业务语义和发布兼容性 |

讲：红色不一定是实现错，也可能是测试、环境或规格错。绿色有价值，但只对声明的检查范围负责。

## 二、解剖台：检查本身也需要审查

**课堂 10 分钟。** 以下是标明来源的教师缺陷样本，不以真实AI必然生成它们为前提。

### 2.1 只断言200与只复述替身结果

```python
# 覆盖范围太窄，不是毫无价值：只能检查这个请求返回200。
def test_list_too_weak(client):
    response = client.get("/questions")
    assert response.status_code == 200
```

如果第一页从第三条开始，该测试仍可能通过。测试名称与它实际能证明的事情不匹配，才是问题。

repository被mock后，测试可验证service的分支、调用参数和错误翻译，但**不能证明真实SQL、约束和持久化**。不能泛称“用了mock就只是在测试mock”。使用 `create_autospec`/`spec_set` 可限制MagicMock的接口；手写fake也需要符合真实依赖契约。

另两个反例：跨测试用全局created_id传状态；健康检查只断言 `status_code in (200, 503)`。前者单跑失败，后者没说明当前环境到底应该健康还是故障。分别改为用例自己准备数据、健康/故障两种受控输入各断言一种结果。

### 2.2 覆盖率微实验：执行过不等于验证过

用独立小模块和两个显式测试版本，不批量注释整个tests目录的assert，不破坏多行语法。只测应用模块覆盖率：

```python
# 隔离微型应用；故意遗漏优惠金额上限。
def payable(price, discount):
    return price - discount
```

```python
# 两版执行同一次调用，差别仅为对结果的断言。
def test_without_business_assertion():
    payable(100, 120)

def test_with_business_assertion():
    result = payable(100, 120)
    assert result == 0  # 独立规格：应付金额最低为0。
```

预期：两版都执行该应用行，业务断言版本才暴露负数结果。具体覆盖率数字以锁定环境实测为准，不预定92%。line coverage不等于branch coverage；二者都不能证明断言正确。

变异测试思路：在独立实验版本中故意改坏一条已承诺的行为，检查测试是否拦截。一次变异被拦只说明对该缺陷敏感；存活可能因为漏测、等价变异或无关范围，不能断言所有未红代码都没有被验证。

### 2.3 标题边界不要写错测试数据

```python
@pytest.mark.parametrize("title, expected", [
    ("四字标题", 422),
    ("五个字标题", 201),
    ("   短   ", 422),
])
def test_title_boundary(client, title, expected):
    response = client.post("/questions", json={
        "title": title, "body": "这是一段满足最小长度要求的正文。"})
    assert response.status_code == expected
```

正文必须合法，不能让它先触发422而掩盖标题边界。每例独立数据；作者1由fixture准备。Pydantic与数据库CHECK可能都有长度护栏：若要单独验证Pydantic，直接对QuestionCreate做模型测试；改坏入口约束后，数据库仍可能拦下，HTTP500不是“正确地返回422”。不修改假想的service长度if。

## 三、测试穿过哪些层，隔离哪些状态

**课堂 14 分钟；完整模板课后阅读。** 测试金字塔表达快速反馈与成本取舍，不规定本项目必须多少单元/集成测试。纯规则用单元测试，HTTP—事务—约束接缝用集成测试，浏览器保留少数关键流程。

### 3.1 替身的选择跟随测试目标

| 目标 | 保留真实对象 | 可替换 |
|---|---|---|
| 长度清洗 | Pydantic模型 | 无需数据库 |
| 唯一约束/条件UPDATE | SQLAlchemy＋PostgreSQL | 外部通知、时钟等无关副作用 |
| service分支 | service | 可用有规格的repository fake，但不声称测了SQL |
| 提交失败的HTTP表现 | 生产事务边界和异常处理 | 精确失败点，可注入before_commit异常 |
| 邮件/第三方API调用策略 | 自己的调用代码 | stub响应、fake记录、mock交互；不真实发邮件 |

SQLite可用于简化机制、纯逻辑或便携层测试；PostgreSQL特有的约束、迁移、隔离与并发必须在目标引擎验证。不同数据库不能直接互相背书，也不能说SQLite“什么都测不出”。

### 3.2 测试库安全接线

A档选择**串行运行**。普通测试使用外层事务回滚；真实提交/并发单独用专用库。数据库由课前模板建立，测试只迁移，不在fixture里无条件重建公共schema。

进程必须在导入应用配置前确认环境。下面是 `tests/conftest.py` 顶部的接线参考：

```python
import os
from sqlalchemy import create_engine, text
from sqlalchemy.engine import make_url

# 缺配置立即失败，不回落到开发库，也不打印带密码的URL。
TEST_URL = os.environ["TEST_DATABASE_URL"]
if os.environ.get("APP_ENV") != "test":
    raise RuntimeError("测试必须显式使用APP_ENV=test")
url = make_url(TEST_URL)
if url.get_backend_name() != "postgresql" or url.database != "qanda_test":
    raise RuntimeError("普通测试仅允许专用qanda_test库")
if os.environ.get("DATABASE_URL") != TEST_URL:
    raise RuntimeError("应用和测试数据库配置不一致")

# 上述检查必须早于app.main/app.config等应用模块的导入。
from app.main import app  # noqa: E402  必须先检查测试环境。
from app.deps import get_session_factory  # noqa: E402
```

名称检查不是充分安全措施：教师还须限制host/port到批准的本机或CI实例，测试角色仅拥有专用库权限。连接后核对 `current_database()`、`current_schema()`；本模板只用public schema，发现不匹配直接失败。不要仅依靠URL字符串判断实际连接目标。

第七课env.py读取settings.database_url，因此只 `cfg.set_main_option("sqlalchemy.url", ...)` 不会切换那个引擎。第九课明确增加**注入迁移连接**的分支：

```python
# migrations/env.py：在第七课基础上替换在线入口，保留离线/在线调度。
def migrate_on(connection):
    context.configure(connection=connection, target_metadata=target_metadata,
                      compare_type=True, compare_server_default=True)
    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online():
    provided = context.config.attributes.get("connection")
    if provided is not None:
        migrate_on(provided)
        return
    connectable = create_engine(settings.database_url, poolclass=pool.NullPool)
    try:
        with connectable.connect() as connection:
            migrate_on(connection)
    finally:
        connectable.dispose()
```

导入仍沿用第七课context、pool、settings和完整Base.metadata。测试引擎fixture：

```python
import pytest
from alembic import command
from alembic.config import Config

@pytest.fixture(scope="session")
def engine():
    eng = create_engine(TEST_URL, pool_pre_ping=True)
    try:
        with eng.begin() as connection:
            actual = connection.execute(
                text("SELECT current_database(), current_schema()")
            ).one()
            if tuple(actual) != ("qanda_test", "public"):
                raise RuntimeError("实际数据库或schema不在允许范围内")
            cfg = Config("alembic.ini")
            cfg.attributes["connection"] = connection
            command.upgrade(cfg, "head")
        yield eng
    finally:
        eng.dispose()
```

普通串行套件重复运行可以复用这份专用库。第一次CI从空库迁移，证明建链可用；只upgrade不能证明downgrade保数据。第七课的带数据往返证据仍单独保存，不在这里盲加 `downgrade -1`。

### 3.3 替换资源来源，保留生产事务行为

第七课get_session内有 `Session.begin()` 及IntegrityError翻译。不能把整个依赖替换为“只yield一个Session”，否则恰好绕过要验证的commit、rollback和DuplicateTitle。

本课允许一次小范围可测性重构：抽出Session工厂依赖，原事务正文不变，旧HTTP回归先跑。目标形态：

```python
from typing import Annotated, Iterator
from fastapi import Depends
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, sessionmaker

def get_session_factory():
    return SessionLocal

FactoryDep = Annotated[sessionmaker, Depends(get_session_factory)]

def get_session(factory: FactoryDep) -> Iterator[Session]:
    try:
        with factory() as session:
            with session.begin():
                yield session
    except IntegrityError as exc:
        constraint = getattr(getattr(exc.orig, "diag", None), "constraint_name", None)
        if constraint == "questions_title_key":
            raise DuplicateTitle() from exc
        raise

SessionDep = Annotated[Session, Depends(get_session, scope="function")]
```

使用test factory提供受控连接，每个请求创建**新Session**。外层事务由fixture拥有，请求事务使用savepoint：

```python
@pytest.fixture
def db_connection(engine):
    with engine.connect() as connection:
        outer = connection.begin()
        try:
            yield connection
        finally:
            if outer.is_active:
                outer.rollback()

@pytest.fixture
def session_factory(db_connection):
    return sessionmaker(bind=db_connection, expire_on_commit=False,
                        join_transaction_mode="create_savepoint")

@pytest.fixture
def client(session_factory, seeded_author):
    previous = app.dependency_overrides.copy()
    app.dependency_overrides[get_session_factory] = lambda: session_factory
    try:
        with TestClient(app, raise_server_exceptions=False) as client:
            yield client
    finally:
        app.dependency_overrides.clear()
        app.dependency_overrides.update(previous)
```

补充导入 `TestClient`；seeded_author用同一factory创建虚构作者1并正常结束其savepoint，确保后续请求可见。factory和seed属于提供模板，不能拿开发库现成作者充数。应用lifespan不得自动写业务数据、启动后台任务或另连开发库；探针独立使用的引擎同样由测试环境配置约束。

讲清三层：**测试外层事务 → 请求savepoint → 当前Session工作单元**。请求commit释放savepoint，不提交测试外层事务；测试末尾回滚数据。它不以“全仓恰好一个commit”为前提，也不能挽救业务中途提交导致的语义错误。

限制：

- 单连接仅供串行请求；HTTP响应返回后再用它查库，不做并发调用。连接/Session不能同时跨线程使用。
- PostgreSQL序列值不会随事务回滚，不断言每个用例id都从1开始；作者固定1是显式seed，不依赖序列。
- 该方案能验证事务控制路径、flush与回滚；不能证明真实提交后的跨连接可见性、提交期延迟约束或并发锁行为。
- 直接执行连接级commit、另起连接写库、后台任务会绕过隔离，需专门测试策略，不能偷偷加入本fixture。
- `raise_server_exceptions=False`用于断言500响应；不要把未捕获异常自动重抛误当成“返回500”。检查应用debug=False。

### 3.4 用例自己准备数据

factory至少提供用户/问题；回答或标签仅在对应测试需要时提供，不按数量评分。问题标题可用明确编号或UUID后缀，碰撞测试反而要故意复用同一标题。测试预期不得硬编码随机id，应保存创建返回值。

```python
@pytest.fixture
def question_factory(session_factory, seeded_author):
    def make(title, **kwargs):
        with session_factory.begin() as session:
            question = Question(
                title=title, body="这是一段满足最小长度要求的正文。",
                author_id=1, **kwargs)
            session.add(question)
            session.flush()
            return question.id
    return make
```

这段仍需从应用导入Question；在测试外层事务中，工厂begin正常退出是释放自己的savepoint，不是实际提交。不要把返回的ORM对象跨Session当作永不过期的共享状态。

## 四、现场必做：一条分页测试推动一次可解释修复

**课堂 20 分钟。** 教师提供只含一个分页偏移缺陷的独立实验版本。不要同时改字段、排序、过滤条件来制造多个干扰因素。

### 4.1 先固定规格与手算数据（4分钟）

同一created_at、status=open的五条问题，id按插入递增，排序created_at DESC、id DESC。`page_size=2`时：第一页后两条、第二页中间两条、第三页最早一条，total始终5。数据来自独立fixture，不与其他用例共享。

```python
def test_page_two_matches_hand_calculated_ids(client, five_questions):
    # fixture返回按id升序排列的5个实际id；created_at完全相同。
    ids = five_questions
    response = client.get("/questions", params={"page": 2, "page_size": 2})
    assert response.status_code == 200
    body = response.json()
    assert body["page"] == 2
    assert body["total"] == 5
    assert [item["id"] for item in body["items"]] == [ids[2], ids[1]]
```

不能使用无效参数size让服务器退回默认20，再假称测了小页长。

### 4.2 四步定位（10分钟）

| 步骤 | 本例动作 | 证据 |
|---|---|---|
| 复现 | 单跑该测试；用同数据同参数再次请求 | 预期两个id，实际只有最早一个 |
| 最小化 | 只留5条静态数据、一个过滤条件、一个页码 | 排除网络、并发和数据量影响 |
| 二分 | 先比较HTTP解析后的page/page_size，再比较repository收到的值和SQL绑定offset | 输入正确、偏移错误；定位到查询构造 |
| 假设验证 | 假设用了page×page_size；只改成(page−1)×page_size | offset从4变2，目标测试变绿 |

“二分”是逐段缩小责任范围，不必机械使用git bisect；只有已知好坏版本且自动判定可靠时才适合按提交二分。日志可用request-id关联该请求，但不要把生产数据或完整凭据贴给AI。

```python
# 缺陷版
.offset(page * page_size)
# 修复版
.offset((page - 1) * page_size)
```

本例没有ORM关系数量问题，不用“加索引”“换缓存”“改async”解释第一页错位。测试失败先看差异和调用边界，不立刻让AI重写整个模块。

### 4.3 补边界并回归（6分钟）

补第一页、第三页、越界空页、page=0/page_size=51返回422；目标测试和全套回归都跑。关闭故障注入，保留缺陷来源和修复diff，不把坏实现提交为正常路径。

一次故意变异证明这条断言能识别该缺陷；不要求每个测试都做三种不相干的破坏实验。真实AI若一次给出正确实现，允许保留，只需用这些相同标准验证。

## 五、M3至少八条关键路径：名字、输入与断言对应

**课堂 12 分钟；学生课后补齐。** 下列是八个必覆盖行为组，可拆成多个pytest用例；不能用八次“返回200”充数。

| 编号/建议测试名 | 场景 | 关键断言与边界 |
|---|---|---|
| T1 `test_list_contract` | 稳定分页、keyword/status筛选、非法sort/page_size | 手算id顺序、筛选后的total、空页、422；至少核对实际条数 |
| T2 `test_detail_and_missing` | 存在/缺失详情 | body、author及版本字段；404 code；无password_hash/email等非公开字段 |
| T3 `test_create_commits_before_success` | 合法创建 | 201＋Location；清洗后内容；**独立连接**能读取已提交记录；tags保存 |
| T4 `test_invalid_input_does_not_write` | 标题4/5边界、空白、正文边界、额外字段 | 422的loc/type；非法用例业务行数不变；不以id是否连续判断 |
| T5 `test_duplicate_title_rolls_back` | 同标题创建及DB唯一冲突 | 409 duplicate_title；仅保留原记录，关联无残留；下个合法请求成功 |
| T6 `test_patch_contract` | 只改title、null、空补丁、重复标题和旧version | body保持；200新版本；非法422；冲突409且数据不变 |
| T7 `test_concurrent_votes` | 两连接同旧version写入 | 200/409；最终只增1且version增1；旧请求重放不再增票 |
| T8 `test_write_failure_rolls_back` | flush后失败和提交前故障 | 不提前201/303；500四字段＋追踪头；无半截数据；后续请求可用 |

T3/T7以及提交期数据库约束测试使用真实提交专用库；其他可用串行savepoint模板。继承教师对SSR、healthz正常/故障、框架404/405头的回归测试也必须通过，不要求学生在本课从零再写一整套。

### 5.1 普通错误检查不能只有“键存在”

```python
def assert_business_error(response, status, code):
    assert response.status_code == status
    body = response.json()
    assert set(body) == {"code", "message", "detail", "request_id"}
    assert body["code"] == code
    assert isinstance(body["message"], str) and body["message"]
    assert isinstance(body["request_id"], str) and body["request_id"]
    assert response.headers["X-Request-ID"] == body["request_id"]
    return body
```

对422再断言detail是列表、元素loc/type/msg形状及目标字段，不返回input/ctx/SQL。对404/409/500按各自契约检查detail和敏感信息。message字段与非空有意义，只有规格明确约定文案时才断言具体文本；不能定成“零处断言message”的教条。

### 5.2 真提交与真并发不能藏在单连接savepoint里

教师提供 `committed_case` fixture：

1. 使用专用 `COMMIT_TEST_DATABASE_URL`，实际数据库必须为 `qanda_commit_test`，同样核对host、权限与schema；不回落普通库。
2. 按迁移链初始化；每例在独立隔离数据集合上准备并**真实提交**作者和问题；fixture记录本例拥有的id。
3. factory绑定Engine而不是共享Connection，不设外层回滚，每个请求独立连接/Session；工厂仍接入生产get_session。
4. 普通提交测试收到201后，用另一个连接读取对应id；并发测试先完成两次详情读取，再发送相同version。两个客户端独立请求，不共享Session。
5. 所有请求结束后按本例拥有的数据清理，恢复override并释放资源；异常也执行清理。教师模板必须处理关联和测试新建标签，不能只清问题留下脏状态。CI服务库每job重建。

参考并发断言（由fixture暴露 `post_vote` 和 `read_question`，前者每次独立HTTP客户端、后者独立连接）：

```python
from concurrent.futures import ThreadPoolExecutor

def test_concurrent_votes(committed_case):
    case = committed_case
    before = case.read_question()
    version = before["version"]
    with ThreadPoolExecutor(max_workers=2) as pool:
        results = list(pool.map(lambda _: case.post_vote(version), range(2)))
    assert sorted(r.status_code for r in results) == [200, 409]
    conflict = next(r for r in results if r.status_code == 409)
    assert_business_error(conflict, 409, "version_conflict")
    after = case.read_question()
    assert after["vote_count"] == before["vote_count"] + 1
    assert after["version"] == version + 1
```

此测试验证同旧版本竞争与最终值；即使调度先后执行也应成立。要稳定重现**缺陷版**丢失更新，仍用第八课两个SELECT后的Barrier。真实HTTP并发记录需保留连接身份/事务边界，不能仅凭启动两个线程认定已使用两条连接。

### 5.3 精确故障注入

T8可在session的before_commit事件或标签处理指定位置注入异常；只限本测试factory/session，finally移除listener。不能patch一个实际未被上下文调用的Session.commit方法后声称测过提交失败。flush后异常需要确认故障点确实到达。

注入“提交前失败”能断言未提交事务回滚；网络断开发生于提交中间时可能结果未知，不能概括为“任何提交异常都没有落库”。延迟约束真正到COMMIT才检查，必须走专用真实提交测试。

### 5.4 N+1回归：承接第七课而非恢复旧阈值

A档保留一个已有代表性列表的计数验证，教师提供断言骨架，不再额外要求五种自制检查。沿用 `count_sql(engine)` 的 `executions/statements` 字段，监听**被测factory实际使用的engine**。

- seed至少50条固定数据，记录作者/关系分布，每个请求新Session。
- 请求使用 `page_size=5/50`；先断言实际返回5/50条，否则条数相等没有意义。
- 计数覆盖DTO、序列化和依赖退出，seed和DDL在计数外；区分SAVEPOINT等事务语句与SELECT。
- 用当前查询/加载方案推导受控范围内的预算，保留SQL分类。页大小增长可能触发正常selectin分批，不以“条数永不变化”为普遍定义。
- 正确性优先：响应字段和顺序要一致，不以减少返回字段“优化”掉需求；不固定宣称所有列表≤3条。

## 六、契约门禁：快照、运行结果与消费者

**课堂 12 分钟。** A档包含OpenAPI快照与实际响应检查；类型门禁使用教师提供的最小消费者。B档才要求学生配置完整类型生成链。

### 6.1 离线导出不依赖正在运行的服务

完整参考 `scripts/export_openapi.py`，在学生工程根目录用模块方式启动，避免脚本目录影响应用导入：

```python
import argparse
import json
from pathlib import Path
from app.main import app

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    target = Path(__file__).resolve().parents[1] / "contracts" / "openapi.json"
    content = json.dumps(app.openapi(), ensure_ascii=False, sort_keys=True, indent=2) + "\n"
    if args.check:
        if not target.is_file() or target.read_text(encoding="utf-8") != content:
            raise SystemExit("OpenAPI快照不一致：先审查契约变更，再显式导出")
    else:
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")

if __name__ == "__main__":
    main()
```

新进程导出，避免运行时改路由后沿用app.openapi缓存。应用导入不执行迁移/seed/网络请求；但Python依赖与配置仍须就绪。比较格式稳定，不把生成时间等易变元数据写进快照。

### 6.2 实际响应也要与交付快照核对

只重生成文件，最多证明声明同步；只拿应用自己的宽泛ErrorOut校验，也可能让错误形状和模型一起改坏。两者都要配合独立业务断言。

课程限定OpenAPI 3.1普通JSON响应，使用锁定版本jsonschema/referencing对**交付快照**验证。以下helper只负责选定operation的正文；头、状态含义、分页结果、写入副作用另断言，不能称为完整OpenAPI验证器。

```python
import json
from pathlib import Path
from jsonschema import Draft202012Validator, FormatChecker
from referencing import Registry, Resource
from referencing.jsonschema import DRAFT202012

SPEC_URI = "urn:qanda:openapi"
SPEC = json.loads(Path("contracts/openapi.json").read_text(encoding="utf-8"))
REGISTRY = Registry().with_resource(
    SPEC_URI, Resource.from_contents(SPEC, default_specification=DRAFT202012)
)

def assert_response_schema(response, path_template, method):
    operation = SPEC["paths"][path_template][method.lower()]
    status = str(response.status_code)
    assert status in operation["responses"], f"未声明状态：{status}"
    media = response.headers.get("content-type", "").split(";", 1)[0]
    assert media == "application/json"
    escaped = path_template.replace("~", "~0").replace("/", "~1")
    pointer = f"#/paths/{escaped}/{method.lower()}/responses/{status}/content/application~1json/schema"
    validator = Draft202012Validator(
        {"$ref": SPEC_URI + pointer}, registry=REGISTRY, format_checker=FormatChecker())
    validator.validate(response.json())
```

JSON Pointer中的路径键要先转义 `~→~0`、再转义 `/→~1`；引用保留整份快照作为根，才能解析 `#/components/schemas/...`，不能只把局部schema拿出来丢失引用上下文。

调用例：`assert_response_schema(response, "/questions/{qid}/votes", "post")`。先用正确响应验证，再在内存副本中移除vote_count或把它改成字符串，确认validator确实拒绝。引用、nullable、枚举和日期格式按锁定工具验证；不支持的schema方言不得静默当作通过。

T1—T8的代表性成功/错误响应均可调用此helper。另检查404/409/422/500的code、detail与追踪头，SSR和探针按各自契约检查。快照比较、schema校验、业务断言互补，不能互相替代。

### 6.3 类型消费者与B档生成

最小 `contract-client` 包由教师提供已提交的package-lock、strict tsconfig、`check: tsc --noEmit` 和已确认的消费者样本；其类型断言范围要写明，不装成已经验证完整SPA。

B档使用第八课gen脚本从快照重生成api.d.ts；应先生成到临时位置再逐字比较已提交文件，检查失败不自动改工作树。更新顺序为：批准契约 → 修改后端/测试 → 显式导出 → 显式生成类型 → 消费者检查。不要仅凭tsc通过认定长度规则、授权或运行响应都正确。

契约反例：只改schema未更新快照，快照门禁红；快照/类型都跟着改，但原接口字段被未授权删掉，独立验收测试仍应红。维护者不能为“修绿”同时随意改实现和预期。

## 七、CI四门禁与本地使用同一入口

**课堂 10 分钟。** 单job配齐Python、Node和两个专用数据库，先保证可执行，再考虑并行。不同job不共享已安装的后端依赖。

### 7.1 共用命令入口

目标目录：`tests/unit`、`tests/integration`、`tests/committed`、`tests/contract`。教师模板含这些测试与fixture；缺目录或无测试要失败，不能当作绿色。

`scripts/check.py` 完整参考：

```python
import argparse
import os
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
NPM = "npm.cmd" if os.name == "nt" else "npm"
GROUPS = {
    "lint": [[sys.executable, "-m", "ruff", "check", "app", "tests", "scripts"],
             [sys.executable, "-m", "ruff", "format", "--check", "app", "tests", "scripts"]],
    "type": [[NPM, "--prefix", "contract-client", "run", "check"]],
    "test": [[sys.executable, "-m", "pytest", "tests/unit", "tests/integration",
              "tests/committed", "-q"]],
    "contract": [[sys.executable, "-m", "scripts.export_openapi", "--check"],
                 [sys.executable, "-m", "pytest", "tests/contract", "-q"]],
}

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("gate", choices=["all", *GROUPS], default="all", nargs="?")
    args = parser.parse_args()
    gates = list(GROUPS) if args.gate == "all" else [args.gate]
    for gate in gates:
        for command in GROUPS[gate]:
            subprocess.run(command, cwd=ROOT, check=True)

if __name__ == "__main__":
    main()
```

本地已准备专用数据库和环境后：

```bash
uv sync --frozen --group dev
npm --prefix contract-client ci
uv run --no-sync python -m scripts.check all
```

Python dev依赖至少含pytest、ruff、httpx、jsonschema、referencing、Alembic及应用所需包；coverage为教师演示可选，xdist/Schemathesis/Playwright为B档。Node锁文件对应教师消费者；不强制再引入mypy一套学习任务。第十课扩展TypeScript/ESLint和真实前端构建。

### 7.2 GitHub Actions参考

下面数据库密码只用于一次性CI服务，不是生产凭据；服务位于隔离runner。第二个数据库由受限的 `scripts.prepare_commit_db` 创建，不挂载开发库数据。本地也在开始测试前执行同一入口；它只准备库，迁移由对应fixture执行。

```yaml
name: ci
on: [push, pull_request]
permissions:
  contents: read
jobs:
  quality:
    runs-on: ubuntu-latest
    timeout-minutes: 15
    services:
      postgres:
        image: postgres:16
        env:
          POSTGRES_USER: course_test
          POSTGRES_PASSWORD: local_test_only
          POSTGRES_DB: qanda_test
        ports: ["5432:5432"]
        options: >-
          --health-cmd "pg_isready -U course_test -d qanda_test"
          --health-interval 5s --health-timeout 5s --health-retries 10
    env:
      APP_ENV: test
      DATABASE_URL: postgresql+psycopg://course_test:local_test_only@127.0.0.1:5432/qanda_test
      TEST_DATABASE_URL: postgresql+psycopg://course_test:local_test_only@127.0.0.1:5432/qanda_test
      COMMIT_TEST_DATABASE_URL: postgresql+psycopg://course_test:local_test_only@127.0.0.1:5432/qanda_commit_test
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"
      - uses: astral-sh/setup-uv@v6
      - uses: actions/setup-node@v4
        with:
          node-version: "22"
      - run: uv sync --frozen --group dev
      - run: npm --prefix contract-client ci
      - name: 创建专用提交测试库
        run: uv run --no-sync python -m scripts.prepare_commit_db
      - name: lint
        run: uv run --no-sync python -m scripts.check lint
      - name: type
        run: uv run --no-sync python -m scripts.check type
      - name: test
        run: uv run --no-sync python -m scripts.check test
      - name: contract
        run: uv run --no-sync python -m scripts.check contract
```

`prepare_commit_db`是教师提供的受限初始化入口：仅APP_ENV=test、批准host/角色/实际qanda_test连接可运行，autocommit连接检查目标库是否已存在，仅创建固定名qanda_commit_test；不存在创建权限则明确失败，绝不回落开发库。它与本地环境准备一致。实施时必须校验COMMIT_TEST_DATABASE_URL只改变库名、仍指向同一批准实例；创建能力限定在可丢弃教学环境，不复用生产角色。

课堂只演示一次已完成的红/绿CI记录；学生本地跑相同命令，不等云端队列消耗课堂。顺序执行在第一处失败时停止属于正常fail-fast；不是要求一个真实AI提交同时命中四类错误。教师分别提供lint、类型、业务、快照四个单缺陷样本，记录实际由哪道门拦住。

### 7.3 自动运行不等于强制禁止合并

仓库ruleset/分支保护需把job `quality`设为required status check，并核对适用分支、管理员绕过、权限和仓库计划。用户有权限时自行配置；无权限如实记录，不伪造“不能合并”截图。不要用pull_request_target运行不可信PR代码，也不向外部PR开放生产凭据。

没有覆盖率基线数据就不调用不存在的“覆盖率不得下降”脚本。A档读懂教师覆盖率报告的证明范围，不额外要求生成报告；自行生成时可按风险解释变化，不按固定百分比或机器耗时评分。检查失败不得用删测试、改expected、continue-on-error或关闭门禁蒙混过关。

## 八、把AI协作规约放进仓库

**课堂 7 分钟。** 文件选工具实际支持的一个入口即可，例如AGENTS.md；是否自动加载、目录作用域与优先级由工具验证，不要求同时维护三份相同规则，也不把.cursorrules当跨工具标准。

### 8.1 可直接适配的规约内容

```text
项目边界
- 同步FastAPI/SQLAlchemy单体；HTTP适配、业务规则、数据访问职责保持清晰。
- 保留body/page_size、统一错误与healthz/SSR例外；新增契约须先说明并获得批准。

修改流程
- 先给验收表、涉及文件和风险；依据规格补测试，再实现最小变更。
- 一次diff只处理一个可验证目的；不按固定文件数机械划分，但禁止无关整库重写。
- 每步运行目标测试，收尾运行 python -m scripts.check all；记录真实结果。
- 新迁移追加，已发布历史迁移、生成类型和契约快照不可随意手改；显式生成前先审读差异。

权限与安全
- 不读取/提交真实密钥，不连接生产库，不在未批准路径执行清理或迁移。
- 不修改评分器、锁定验收标准、权限配置来绕过失败；依赖变更须说明理由并更新锁文件。
- 不自动推送、部署或改外部仓库设置；需要时请求授权。

交付
- 说明哪些规格被验证、哪些没验证；保留提示词、输出、审查判断和证据。
- 正确产出可以保留；发现问题再提交修复diff，不要求AI必错。
```

“禁改目录”按实际仓库填具体路径，例如只读教师验收包；不是把学生自己应维护的全部tests永久冻结。规则文件只是约束入口，不是安全沙箱；CI、权限与人工审核分别承担强制和判断职责。

### 8.2 生成、测试与审查要有独立依据

给AI规格、已有接口、相关实现和允许变更范围，让它写测试或评审都可以；关键是预期来自已确认规则，而不是复述实现。生成者自评可能沿用同一假设，另开一次审查也不保证独立正确；通过手算样本、反例、不同检查层交叉验证。

不适合直接委派实现的情况：验收标准尚不稳定、上下文涉密、核心抽象取舍未决定。先澄清或人工决策；不把“核心抽象永远不能借助AI讨论”作为禁令。

真实AI协作记录与已知缺陷演练分开：

| 记录 | 允许结果 |
|---|---|
| 教师人为变异/已知缺陷 | 必须说明哪个检查拦下、如何定位修复；来源明确 |
| 本次真实AI产出 | 有问题则修；全绿且规格满足可以保留；检查不足则补证据 |

不挑选“无规格必错、有规格必对”的样本来冒充普遍规律。一次对照只能说明本次输出和检查范围。

## 九、M3交付与验收

**课堂 5 分钟。** 以同一张表连接第八课输出与第九课门禁，基础交付不超过现有主线范围。

| 交付 | M3判定 |
|---|---|
| 契约化API | 第八课版本投票/PATCH、稳定分页白名单、统一错误、OpenAPI快照；旧JSON/SSR/探针回归通过 |
| ≥8条关键路径 | 覆盖T1—T8；断言业务结果和失败后数据，能说明测试边界；不按参数化数量凑数 |
| 测试基础设施 | 专用库、Alembic接线、串行隔离、override恢复；目标用例单跑、全套连跑两次均通过 |
| 真提交/并发证据 | 独立连接可见性、同旧版本200/409及最终值；与savepoint测试明确分开 |
| 四道门禁 | lint/type/test/contract；本地与CI共用入口，锁文件齐全；报告合并保护的实际状态 |
| 一次已知缺陷记录 | 初始红、四步定位、最小diff、目标与全套绿；可使用课堂分页案例 |
| 仓库AI规约＋真实协作记录 | 规格、可改范围、输出、判断与证据；有错附diff，无错说明保留依据 |
| 一页手册 | “规格→测试→门禁→人工判断”图，说明一个门禁能力边界和一次测试取舍 |

B档任选一项：三个植入bug定位报告（含并发）、Playwright一条SSR或后续SPA冒烟、Schema生成式测试、类型生成一致性、AST规则或并行测试。建议一小时以内，有教师模板；不作为M3必交条件。

## 十、拓展参考与不得泛化的结论

- **并行pytest**：每worker独立数据库/schema和迁移/seed，不能多个worker重建同一个schema。A档不用 `pytest -n auto`；函数级事务隔离不等于多进程DDL隔离。
- **Schemathesis/Hypothesis**：锁定版本并按当前API接线，每生成样本管理独立状态；函数级fixture并不会每个生成样本重建。恢复override，避免样本互相污染。它们是生成/搜索，不是穷举所有请求。
- **AST与约定检查**：限定明确路径、区分正反例并测试检查器自身。AST不自动理解动态调用、跨函数阻塞或业务意图；文本grep也不保证覆盖所有别名。不要宣称“从此不可能泄漏”。
- **response_model检查**：只检查登记的业务JSON出口，HTML/303/探针分别处理；注解推导、直接Response等会改变行为。真实敏感字段断言不可省。
- **数据库元数据检查**：主键、唯一、外键等按业务规格；外键是否另建索引要有查询/修改证据，不恢复“所有外键必须加索引”的规则。
- **浏览器冒烟**：优先现有SSR创建→303→详情，后续扩展React。统计API请求须限定端点/观察终点，不能一有li就断言总请求完成；前端端到端测试不是数据库事务测试的替代。
- **慢/不稳定测试**：先记录阶段耗时、共享状态、同步点与外部依赖，再决定隔离/并行/重试策略；不承诺固定加速倍数，不用无条件retry掩盖失败。

## 十一、素材、验证边界与衔接

制作前必须提供并实测：

1. 对应第八课基线的独立工程、Python/Node锁文件、两个专用库准备入口；普通engine与Alembic注入连接的真实数据库核对。
2. 完整seed/factory、提交专用fixture及异常清理、生产get_session_factory接线；连接身份、before_commit故障注入与override恢复证据。
3. T1—T8和继承回归包、SQL计数骨架、四类单缺陷样本、微型覆盖率两个版本；不假定存在23条旧测试或92%报告。
4. OpenAPI导出/快照/响应validator、最小TS消费者、共用check入口、可执行CI工作流；required check红绿截图标注实际仓库权限。
5. 网络不可用时使用注明环境的预录CI；数据库失败时先区分环境故障，不把SQLite结果冒充目标引擎验收。

本轮与第八课合计通过71项语法/机制/时长检查，其中直接提取本稿get_session_factory/get_session代码，在内存SQLite与TestClient中验证：普通成功、flush后异常回滚、before_commit故障不提前返回201、失败后继续请求，以及测试外层事务最终回滚。另通过13项实际课时表、JSON、YAML与四门禁命令接线检查。使用现有依赖，未安装新包；临时验证脚本执行后清理。

现有Python示例环境缺pytest、Alembic、jsonschema/referencing，故未执行完整pytest套件、迁移连接注入、JSON Schema helper及真实PostgreSQL提交/并发。远端GitHub Actions和浏览器端到端也未执行；文中模板必须在配套工程制作阶段完成集成，不以语法检查通过宣称CI全绿。

第十课在这套四门禁上增加真实Vite/React/TS工程、ESLint和构建检查；不得要求全体学生已在第八课独立完成前端。第十二课补数据获取竞态与错误恢复，第十四课扩展认证/授权测试，第十五课加入安全回归，第十六课衔接发布检查。Redis、keyset、窗口函数不是第十一课的教学承诺。

参考：pytest Fixtures、FastAPI Testing Dependencies、SQLAlchemy Joining a Session into an External Transaction、Alembic Cookbook连接共享、OpenAPI 3.1、jsonschema/referencing、GitHub Actions服务容器与required status checks。工具行为以教学锁定版本为准。
