# 第 9 次课教学底稿（第四版）
## 测试、CI 门禁与故障定位 ｜ 交付 M3

> **备课基线**：[第四版大纲](../syllabus-v4.md)第 9 课与[第 8 课交接](lesson-08.md#82-下一课的明确输入)。本稿尚未移交归档；它定义教学内容与配套工程要求，不代表独立 M3 应用、锁文件、CI 配置和教师脚本已交付。示例模块与命令指学生问答工程，不是本 Slidev 仓库现有入口。

## 〇、这次课学会什么

**讲给学生的目标句**：你能让机器替你把回归跑一遍，并把一次失败缩小到一行代码。

核心解释目标只有一个：**一次失败如何被缩小到一行。** 先写一条正确测试，再认识它依赖的数据与执行入口，随后在已知分页缺陷上完成定位闭环。覆盖率、自制检查器与并行平台不抢占这条主线。

### 95 分钟教学 + 5 分钟缓冲

| 分钟 | 教学单元 | 当场产出 |
|---|---|---|
| 5 | 目标与 M2／第 8 课交接 | 区分规格、实现、测试与证据 |
| 15 | 第一个测试逐行写：正常创建 | 状态、内容、Location 与独立查库断言 |
| 18 | 教师演示测试库、fixture、四门禁与分支保护 | 会运行模板，说明运行检查与禁止合并的区别 |
| 25 | 学生修复已知分页缺陷 | 手算规格 → 红 → 定位 → 一行修复 → 回归绿 |
| 15 | 四件证据关联练习 | 同次执行的报文、request-id 日志、栈帧、SQL |
| 10 | AI 协作规约与三条测试判断 | 允许范围、独立预期、接受或修正的理由 |
| 7 | 写法卡与 M3 交付 | 一个作业包的验收清单 |
| **95** | **教学合计** | **另留 5 分钟缓冲，共 100 分钟** |

本课**不安排计分小测**。超时先压缩附录配置逐行阅读与拓展介绍，保留学生 25 分钟、四件证据练习和分支保护演示。环境课前就绪，课堂不等待依赖下载或云端队列。

### 教师提供什么，学生承担什么

| 内容 | 标注与责任 | 理解边界 |
|---|---|---|
| 第 8 课正确应用、单缺陷副本、测试起点 | 教师提供，要求会用 | 不破坏完成版，不假称真实 AI 必然写错 |
| 第一条正常测试与分页断言 | 要求解释；学生补测试、选择边界输入 | 预期来自固定规格，不自由改字段／排序 |
| 专用库、迁移、schema 隔离与复位 | 教师设施，**黑盒** | 学生会确认目标与使用入口，不开发清库工具、不进口试内部 |
| 资源 override、服务提交、错误出口 | **要求解释** | 只替换资源，不旁路服务 commit／rollback／错误翻译 |
| HTTP／SQL／故障／调试记录设施 | 教师提供，要求会用 | 学生解释证据，不从零写线程同步与跟踪器 |
| 四门禁入口、CI 工作流、快照导出 | 教师提供，要求会用 | 会运行、读失败层与退出状态；不背 YAML |
| 最小 TypeScript 消费者及锁文件 | 教师提供，**黑盒** | 本课只解释检查拦什么；第 10 课学习后再扩展真实前端 |
| AI 规约与 M3 回归 | 学生适配／补齐 | 不重复提交卡片、手册与截图套件 |

## 一、从规格到可执行证据

**课堂 5 分钟。** 前八课已经有教师回归，本课把学生从“会运行”带到“能写断言、缩小失败范围”。不说“有测试就不会坏”。

```text
批准的规格／手算样本 → 测试输入与预期
                         ↓
真实请求 → 业务服务 → SQL／事务 → 响应与数据库状态
                         ↓
             差异 → 缩小范围 → 最小修复 → 回归
```

第 8 课输入保持不变：

| 项目 | 本课沿用的规格 |
|---|---|
| 列表 | keyword/page/page_size；空／1／20；page ≥1、page_size 1–50；字面子串、id DESC；items/total/page；每项五字段 |
| 详情／创建／PATCH | id/title/body/tags/created_at/vote_count/version 七字段；不新增作者摘要、sort/status |
| 创建 | title/body 先 strip 后检查 5–200／10–20000；tags 原列表最多五项，再精确去重保序；拒绝额外字段；201 + Location |
| 投票／PATCH | 同一 UPDATE 判断旧 version；version 严格正整数；投票 200 返回 qid/vote_count/version；PATCH 省略保持、null／空补丁拒绝 |
| 错误 | 404 question_not_found；409 version_conflict／duplicate_title；422 validation_error，detail 为 loc/type/msg 列表；未知错误安全 500 |
| 事务／迁移 | 服务显式提交，依赖仅提供／关闭；001_baseline → 002_question_version；body 列名不变 |
| 继承回归 | HTML 三页、原文回填、成功 303、自动转义、request-id；healthz 单 status 的 200 ok／预期数据库故障 503 degraded |

qid 只按整数解析；不存在的 0／负整数是 404，非整数是 422。JSON 路径即使 Accept:text/html 也不改成 HTML。测试不能用旧稿中不存在的 status 字段或接口来准备数据。

**测试通过的含义**：当前实现通过了这些输入、环境与断言，不代表规格完整、所有并发正确或可以无审查上线。红色也可能来自测试或环境，应先定位，不先删除断言。

## 二、第一条测试：正确创建，而且真的提交了

**课堂 15 分钟。3 分钟确定条件，8 分钟逐行写，4 分钟运行并核对。** 第一条是正例，不先展示空断言或覆盖率陷阱。

### 2.1 先写出完整条件

教师 case 提供本用例独占的 PostgreSQL schema，已经由 001→002 迁移，只有虚构作者 1，没有问题／标签。每次请求使用独立 Session；没有测试外层事务包住业务提交，没有故障注入，也没有其他写者。case.read_question 用新的独立连接读取。

先说预期：创建 201，清洗后文本、标签与默认 0／1 正确，Location 指向新详情；请求返回后，独立连接读到同一问题。

以下放在教师工程 `tests/integration/test_questions.py`，case 的完整参考在 §9.1。

```python
# lesson09: first_test

def test_create_commits_before_success(case):
    response = case.client.post("/questions", json={
        "title": "  第一条正确测试的问题  ",
        "body": "  这是满足最小长度要求的正常正文。  ",
        "tags": ["python", "python", "sql"],
    })
    assert response.status_code == 201
    body = response.json()
    assert set(body) == {
        "id", "title", "body", "tags", "created_at", "vote_count", "version",
    }
    assert body["title"] == "第一条正确测试的问题"
    assert body["body"] == "这是满足最小长度要求的正常正文。"
    assert body["tags"] == ["python", "sql"]
    assert (body["vote_count"], body["version"]) == (0, 1)
    assert response.headers["Location"] == f"/questions/{body['id']}"
    assert response.headers["X-Request-ID"]
    stored = case.read_question(body["id"])
    assert stored is not None
    assert stored["title"] == body["title"]
    assert stored["body"] == body["body"]
    assert (stored["vote_count"], stored["version"]) == (0, 1)
    detail = case.client.get(response.headers["Location"])
    assert detail.status_code == 200
    assert detail.json() == body
```

最后的 GET 无其他写者，才要求完整详情等于刚才结果。新 id 从响应取得，不断言“肯定是 1”；PostgreSQL 序列不随事务回滚恢复。

```bash
uv run --no-sync python -m pytest tests/integration/test_questions.py::test_create_commits_before_success -q
```

这条测试覆盖真实校验、路由、服务、SQL、提交与回读，但还没证明所有错误路径、响应发送时序或真实网络行为。标签另查详情可验证关联读取；更细的关联原子性由故障测试补充。

### 2.2 fixture、assert 与 TestClient 各做什么

- pytest 根据参数名提供 case；fixture 准备与回收本例资源，测试之间不靠全局 created_id 传值。
- assert 把独立预期变成失败点；不只断言 201，也不把当前输出复制成 expected。
- TestClient 是**进程内 HTTP 测试**：经过实际应用处理链，不启动 Uvicorn、不经过真实端口与浏览器。测试报文不是浏览器 Network 截图。
- `raise_server_exceptions=False` 让测试拿到 500 后断言；配合 `debug=False`。它不把错误变为成功，也不替你写数据库断言。

先让这条正例变绿，再进入缺陷练习。

## 三、教师演示：让这条测试安全地反复运行

**课堂 18 分钟。5 分钟专用库／fixture，5 分钟资源替换与事务预测，4 分钟本地四门禁，4 分钟 CI／分支保护。** 只读关键接线，完整配置移附录。

### 3.1 本课主线：独占 schema，真实服务提交

教师提供批准的专用测试库；每个 case 新建随机命名的独占 schema、迁移到 002、seed 作者。结束全部请求后清理自己创建的 schema。小教学数据先选择这条真实提交路径，避免把两种隔离方式同时变成学生必学框架。

配套设施必须满足：

1. 在导入应用配置前检查 APP_ENV=test、TEST_DATABASE_URL 与应用数据库配置一致；无配置立即失败，不回落开发库。
2. 只准教师 profile 指定的本机／CI 实例、端口、数据库与测试角色；连接后核对实际 database／schema。正式示例数据库名 qanda_test，名称本身不是充分安全措施。
3. 测试角色仅有专用库权限；lifespan 不另连开发库、自动 seed、开启业务后台写者。探针独立连接同样接入测试配置。
4. schema 名由设施生成并记录所有权，不接受请求／学生输入；只清理本例成功创建的 schema，绝不无条件重建 public。
5. A 档串行执行测试套件。并发仅发生在指定用例内部，每个请求独立 Session；app 的 override 不在请求仍运行时变更。

这些是教师设施验收，不让学生从零开发。若设施未到位，不能把下文命令说成已可直接运行。

### 3.2 只替换资源，保留业务用例

第 7／8 课 `get_session()` 只有提供和关闭资源。它**没有** Session.begin 提交块，也不承担 DuplicateTitle 翻译。故可使用以下测试依赖；正式服务及其事务和异常映射保持原样：

```python
# lesson09: resource_override

def make_test_dependency(sessions):
    def provide_session():
        with sessions() as session:
            yield session
    return provide_session
```

case 中以原函数对象登记 `app.dependency_overrides[get_session]`；不是字符串路径，也不把整个创建服务换成返回固定字典的 fake。结束恢复原 override，而非永久清空别人的配置。无需为测试给生产依赖添加新的提交位置或 function scope。

**观察点二：先预测。** 在上述真实提交 case 中，只覆盖 get_session，输入合法、作者存在、没有重复标题。正常创建还会调用服务 commit 吗？若 SQL／flush 后、commit 前抛错会怎样？若 commit 确认后、响应启动前抛错呢？

| 固定注入位置 | 响应 | 独立连接回读 |
|---|---|---|
| 无故障 | 201 | 新问题、标签与关联可见 |
| after_flush：最后一次 flush 成功，commit 尚未调用 | 500 internal_error | 本次问题／新标签／关联均不留下 |
| after_commit：commit 已确认，响应尚未启动 | 500 internal_error | 本次数据仍在；rollback 不能撤销已提交事务 |

答案：会执行原服务 commit。两个故障都发生在响应启动前，不能统一写成“500→无写入”。真实提交期间断连／确认丢失是结果未知，这两个开关不模拟它，不自动重试写请求。

**参考边界**：普通串行测试也可用外层事务＋savepoint 加速，但那时服务 commit 可能只是释放 savepoint，不能证明跨连接提交可见性；不能拿测试末尾回滚当“业务失败已回滚”。本课主线不使用这种外层包装。替身可验证服务分支／调用参数，但不能为未执行的 PostgreSQL SQL 与锁行为背书。

### 3.3 四门禁跑同一个入口

教师课前提供 Python／Node 锁文件、正确基线与快照。学生不是在第 9 课编写一个新质量平台。

| 门禁 | 本课执行内容 | 拦不住什么 |
|---|---|---|
| lint | Ruff 已配置的检查＋format --check | 业务分页是否正确 |
| type | 教师 contract-client 的 tsc --noEmit | 未纳入消费者、长度规则、真实网络 JSON |
| test | 单元／HTTP／真实提交与并发回归 | 未覆盖的输入与错误规格 |
| contract | OpenAPI 快照 check＋实际代表响应校验 | 全部语义、授权与完整发布兼容性 |

```bash
uv sync --frozen --group dev
npm --prefix contract-client ci
uv run --no-sync python -m scripts.check all
```

这些命令在**已准备好的独立课程包**运行。check 只检查，不自动改快照、格式、锁文件或预期。默认在第一处失败时停止；缺测试返回非零不能改成成功。四类单缺陷记录由教师提供，不要求真实 AI 一次产出四类错误。

### 3.4 CI 运行和合并保护是两件事

教师展示相同提交的本地命令与 GitHub Actions job `quality`，再打开目标仓库 main 分支的 ruleset／保护规则：

- 要求 PR、把实际报告的 `quality` check 设为 required；核对规则适用分支及绕过名单。
- 用已有受控失败 PR 展示检查未通过时不可合并，再看修复后的成功记录；绿色还可能等待人工审批等规则。
- 不为了截图真的合并代码，不关闭保护。不使用 pull_request_target 执行不可信 PR 代码，不向外部 PR 提供生产凭据。
- 无权限或仓库计划不支持时，记录缺口与需谁配置；可用教师示范仓库，但不能宣称学生仓库已经受保护。网络不可用用注明环境的预录结果。

**CI 执行并报告检查；分支保护决定是否强制阻止合入。** 工作流里写了四条命令，不等于仓库已有禁止合并的规则。

## 四、学生任务：用一条失败缩小到分页的一行

**课堂 25 分钟。4 分钟手算，6 分钟补断言并复现，8 分钟二分定位，4 分钟最小修复与回归，3 分钟保存证据。** 学生只处理教师标注的一个偏移缺陷。

### 4.1 观察点一：条件写全再预测

独立 fixture 有 **25 条问题**，id=1001–1025，没有其他问题、筛选或并发写入；公开排序 **id DESC**。请求 page=2、page_size=10。正确结果是整个倒序集合的**第 11–20 条**，即 1015 到 1006，total=25、page=2。

教师缺陷版只把 `.offset((page - 1) * page_size)` 写成 `.offset(page * page_size)`。它仍返回 200，total 与 page 都正确，却跳过 20 条，只返回 1005 到 1001（第 21–25 条）。不是 created_at 排序问题，不添加 status=open 前提。

```python
# lesson09: pagination_tests
import pytest


@pytest.fixture
def twenty_five(case):
    for qid in range(1001, 1026):
        case.add_question(f"分页样本问题 {qid}", id=qid)
    return case


def test_page_two_matches_spec(twenty_five):
    response = twenty_five.client.get(
        "/questions", params={"page": 2, "page_size": 10},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["page"] == 2
    assert body["total"] == 25
    assert [item["id"] for item in body["items"]] == list(range(1015, 1005, -1))


@pytest.mark.parametrize("page, expected", [
    (1, list(range(1025, 1015, -1))),
    (3, list(range(1005, 1000, -1))),
    (4, []),
])
def test_page_boundaries(twenty_five, page, expected):
    response = twenty_five.client.get(
        "/questions", params={"page": page, "page_size": 10},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["page"] == page
    assert body["total"] == 25
    assert [item["id"] for item in body["items"]] == expected
```

先只展示题面与测试壳，学生写预期，运行后才揭示错误结果和参考断言。失败应在 id 列表断言，不是状态／total 断言。不得把参数写成不存在的 size，或将 expected 改成缺陷输出。

### 4.2 四步定位，不让 AI 重写整个模块

| 步骤 | 本例动作 | 要保留的证据 |
|---|---|---|
| 复现 | 单跑同一个 node id，确认固定 25 条数据 | 预期 10 个 id，实际 5 个 id |
| 最小化 | 只保留第二页请求、固定 seed 与当前列表链路 | 排除筛选、并发、浏览器与外部网络 |
| 二分 | 先看端点解析值，再看查询函数参数，最后看 SQL 绑定 offset | page=2／page_size=10 没错，OFFSET=20 错 |
| 假设验证 | 只改偏移表达式为 (page−1)×page_size | OFFSET=10，目标测试转绿，随后全套回归 |

“二分”是逐段缩小责任范围，不要求机械运行 git bisect。后者需要已知好坏版本和可靠自动判据。这里 200 不意味着正确，计数 SQL 正确也不能证明取页 SQL 正确。

缺陷／修复表达式仅为定位示意，不是独立 Python 程序：

```text
缺陷：.offset(page * page_size)
修复：.offset((page - 1) * page_size)
```

学生在固定规格下自主选择一个补充边界输入及如何缩小调用范围，说明它能排除什么。可选第一页、第三页、越界页、page=0 或 page_size=51；不能自由改排序或参数范围。教师已有其余回归，未选的边界不因此被取消。

### 4.3 绿灯要分层解释

1. 单条目标测试转绿，说明此例修复有效。
2. 分页边界与原契约测试通过，排除一处修复破坏其他页。
3. 同一入口全套检查通过，保存执行版本与退出状态。

不靠删测试、放宽 expected、隐藏 xfail、continue-on-error 来修绿。合理的测试预期可在规格核实后修订，但必须解释规格依据，不能跟着实现任意漂移。不得为偏移缺陷顺手加缓存、索引或改 async。

## 五、四件证据：把同一次执行连起来

**课堂 15 分钟。3 分钟选定执行，8 分钟关联，4 分钟用一句话归因。** 复用刚才的分页用例，不新增第二个编码任务。

### 5.1 同一份数据、同一次请求、同一个版本

教师启动器为专用调试运行固定 seed，并发关闭；附着调试器后只执行该请求一次。通过 TestClient 发出的报文可由测试记录器保存；若演示浏览器 Network，则另开 Uvicorn 的隔离运行，不能把两次运行的四张截图拼成一次。

| 证据 | 本例观察 | 不能据此推出 |
|---|---|---|
| 报文 | GET /questions?page=2&page_size=10；200；total=25；实际五个 id；响应 X-Request-ID | 200 不证明第 2 页正确 |
| 日志 | 同 id 的 request_start／request_end，outcome=200 | 前课中间件默认不记录查询参数，不能伪造日志已有 page 字段 |
| 断点栈帧 | 端点→list_questions_orm；page=2、page_size=10；偏移表达式所在线 | 框架线程调度帧不等于出错业务层；不用背全部调用栈 |
| SQL 日志 | count=25；取页 ORDER BY id DESC、LIMIT=10、OFFSET=20 | 标签查询存在不意味着 N+1；计数正确不代表偏移正确 |

SQLAlchemy 日志默认不会自动带业务 request-id。教师设施以**独占运行、单请求窗口、同一 engine／连接标识**关联 SQL 与报文；若要每条 SQL 都带 id，须另提供已验证的上下文注入器，不能只把 logger 名改掉。参数日志只用于虚构数据，不公开带凭据的 URL、真实正文或生产数据。

应用日志 outcome=200 是本例的事实；未知异常时前课 trace 可能记录 outcome="error"，随后外层才形成 500，不强改旧中间件语义来拼证据。

### 5.2 一份定位记录就够

记录包含：代码版本／缺陷来源、数据条件、测试 node id、request-id、四件证据与那一行修复。结论示例：

> 本次请求参数正确，计数也正确；查询构造把偏移算成 20，导致第二页只剩五条。改成 10 后，同规格断言通过。

修复前后是**两次运行**，分别标识；不复用同一个 request-id 冒充同次执行。断点调试会改变时间与并发调度，本练习不用于证明并发时序或性能。真实课堂四件证据需实测，不拿程序提取的调用栈替代尚未完成的 IDE 断点操作截图。

## 六、把 AI 协作规约用于三条测试

**课堂 10 分钟。4 分钟适配规约，4 分钟判断三条测试，2 分钟记录接受／修正。** 后端进入阶段三；下课前不要求学生再造一个审计框架。

### 6.1 一个工具实际支持的规约入口

教师展示学生仓库的 AGENTS.md 或所用工具确实支持的规则入口，核对作用域／自动加载；不用同时维护三份相同规则，也不修改本课件仓库的代理配置。

```text
职责与契约
- HTTP 适配、业务服务和数据访问保持分工；业务用例服务显式 commit。
- 依赖只提供／关闭资源；内部数据函数不提交；成功响应晚于提交确认。
- 保留 keyword/page/page_size、id DESC、列表五字段及详情七字段。
- 404／409／422／500 按既有 code 与四字段契约；HTML／healthz 分别处理。

允许范围与禁改项
- 先说明规格、涉及文件与风险，按规格补断言，再做最小实现修改。
- 不改教师只读验收包、已发布迁移、评分标准或权限配置来绕过失败。
- 学生自己的 tests 可以维护；生成快照需先审查契约差异，再显式导出。
- 不连接生产库、不获取真实秘密、不自行推送／部署或修改外部仓库保护。

验证与交付
- 先跑目标测试，收尾运行 python -m scripts.check all；记录真实退出结果。
- 故障标明提交前／确认后，独立查库；未知结果不自动重试写入。
- 说明验证范围与未完成项；合理输出可接受，有问题才修改并重跑。
```

规则文件不是权限沙箱，CI 也不会自动理解自然语言规约。权限、检查与人工判断分别负责；禁改项必须对应课程包实际路径。

### 6.2 按独立规格判断，不规定 AI 必错

让 AI 按已确认的规格生成**三条测试**，例如第一页、越界空页、非法 page。逐条回答：输入条件完整吗？预期来自规格吗？验证的是业务结果还是复述被 mock 的返回值？是否使用本课真实 fixture、有没有绕过提交？

合理的直接采纳，附运行证据与接受理由；有问题才修。标题边界示例必须让正文合法，不能让正文先失败而掩盖标题错误。若测试目标是 Pydantic 清洗，直接测模型；若目标是数据库约束／提交，不能用纯模型测试背书。

教师已知缺陷演练与真实 AI 输出分开记录，不把人为构造的错误标成“AI 原样产出”。不强制另写长审计报告或找满三个问题。

## 七、收尾：常用写法卡与 M3 一个作业包

**课堂 7 分钟。3 分钟卡片，2 分钟验收表，2 分钟交接。**

### 常用写法卡 #9

| 写法 | 框架／设施替你做什么 | 必须知道的边界 |
|---|---|---|
| TestClient 请求 | 在进程内穿过真实应用处理链 | 不验证 Uvicorn、网络或浏览器 |
| fixture 准备数据 | 每例得到明确可复现状态并回收 | 不共享全局 id；序列不保证连续 |
| 状态＋业务值＋数据状态断言 | 把规格变成差异 | 只断言 200／201 不足；预期不能照抄实现 |
| dependency_overrides | 替换资源来源 | 不绕过服务事务和错误出口 |
| 复现→最小化→二分→假设验证 | 缩小问题范围 | 先定位到边界，不无关重写 |
| 四门禁同入口 | 本地／CI 重复执行配置好的检查 | 无检查／未执行不算通过，绿灯不证明无 bug |
| required check／分支保护 | 对受保护目标强制合入条件 | 必须真实配置，核对绕过权限 |
| request-id＋四件证据 | 关联一次执行的输入与行为 | 不是认证身份；不混拼两次运行 |

### 至少八条关键路径，不按参数化数量凑数

| 组 | 必须覆盖的行为 | 关键证据 |
|---|---|---|
| T1 列表 | 手算分页／空页／字面搜索／合法与非法参数 | id 顺序、过滤后总数、五字段、422；不测虚构 sort/status |
| T2 详情 | 存在、缺失整数、非整数 | 七字段与标签顺序、404 code／422 |
| T3 正常创建 | 清洗、标签保序、默认值 | 201+Location、详情一致、独立连接已提交 |
| T4 非法输入 | 标题／正文边界、空白、tags 超限、额外管理字段 | 422 detail 的目标 loc/type/msg，业务数据不变 |
| T5 标题冲突 | 创建／PATCH 的命名唯一约束冲突 | 409 duplicate_title；问题／关联／版本无半截改变，后续请求可用 |
| T6 PATCH | 单／双字段、省略／null／空补丁、旧版本／缺失 | 200 新值与版本、422／409／404；拒绝无误写 |
| T7 条件投票 | 同旧版本两请求、重放旧请求、资源缺失 | 一 200 一 409、独立最终只 +1、重放不再加票、404 |
| T8 两种故障位置 | 创建的 after_flush 与 after_commit | 同为 500，但独立查问题／标签／关联结果不同；保留注入位置与响应时序 |

T3／T7／T8 必须真实提交并独立查库，本课统一 case 即可。继承教师 JSON／HTML／探针／405 必要头回归仍须通过，不让学生再从零重写所有端点。第 7 课 N+1 回归沿用固定 20 问题／20 回答、完整相同输出、21／2 SELECT 的独立实验，不新增 50 行公开作者摘要或“所有列表永远 ≤3”要求。

**A 档 M3 只交一个包**：≥8 条关键路径测试；本地与 CI 四门禁记录；分支保护截图或实际状态说明；AI 规约与三条测试的判断；一次含四件证据的定位记录。课堂红绿记录、卡片补例和已有故障证据可以复用，不再加一页新手册作为独立作业。

每个用例能单跑，全套连跑两次无污染；已知缺陷版红、修复版目标与全套绿。课程包缺设施、远端无权限或测试未跑时列缺口，不伪造“CI 全绿”。

## 八、拓展与第 10 课交接

B 档只选**一条 Playwright 端到端冒烟**：优先已有 SSR 创建→303→详情，说明它比进程内 HTTP 多覆盖什么，不能替代 PostgreSQL 提交／并发测试。覆盖率、变异测试、生成式测试、并行 worker、自制 AST 检查器进参考，不新增必交任务或固定覆盖率门槛。

下一课接收：第 8 课 API、001→002、同一门禁入口、OpenAPI 快照、教师最小类型消费者。第 10 课从模块与构建正例开始，扩展真实 Vite／TypeScript 前端、ESLint 与 build；不能假定全体学生第 8 课就完成了前端。

第 10 课底稿已按 v4 重写为正确模块→构建链路→模块改动与公开配置两次学生实验；React 仅作教师展示外壳，补入类型／lint／build 对照并沿用本课四门禁入口。隔离工具与浏览器机制已实测，正式前端包、真实 M3 GET 联调、完整 all 与远端 CI 仍须按该课制作清单验收。第 14 课新增认证、授权与 CSRF 后，写操作测试须升级登录／凭证 fixture，不能承诺本套测试永远原样使用。

## 九、教师附录：配套工程参考

附录是教师制作与学生课后查阅，不占用课堂逐行抄写时间。模块命名固定为 app.main（应用）、app.deps（原 get_session）、app.models（五表）、app.api.questions（端点绑定的服务名）；整合其他工程结构时教师须一次性接好，不让学生猜 import 路径。

### 9.1 真实提交 case 与迁移连接

教师 bootstrap 在应用导入前执行 §3.1 的环境／目标校验，并提供 `base_test_engine` fixture；下段才导入应用。base_test_engine 指向批准的专用测试库，退出时 dispose；不能直接把环境变量中的任意 URL 交给本段。

`tests/conftest.py` 的隔离／case 参考；pytest fixture 从同文件或明确的 pytest_plugins 加载，不能只把它放在任意 helpers.py 后期待自动发现。

```python
# lesson09: fixtures
import uuid
from datetime import datetime, timezone
from types import SimpleNamespace

import pytest
from alembic import command
from alembic.config import Config
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker
from sqlalchemy.schema import CreateSchema, DropSchema

from app.main import app
from app.deps import get_session
from app.models import Base, Question, User


@pytest.fixture
def isolated_engine(base_test_engine):
    schema = "case_" + uuid.uuid4().hex
    owned = False
    engine = None
    try:
        with base_test_engine.begin() as connection:
            connection.execute(CreateSchema(schema))
        owned = True
        url = base_test_engine.url.update_query_dict({
            "options": f"-c search_path={schema} -c timezone=UTC -c statement_timeout=10000",
        })
        engine = create_engine(url, isolation_level="READ COMMITTED", pool_pre_ping=True)
        with engine.begin() as connection:
            cfg = Config("alembic.ini")
            cfg.attributes["connection"] = connection
            command.upgrade(cfg, "head")
        yield engine
    finally:
        if engine is not None:
            engine.dispose()
        if owned:
            with base_test_engine.begin() as connection:
                connection.execute(DropSchema(schema, cascade=True))


@pytest.fixture
def case(isolated_engine):
    sessions = sessionmaker(bind=isolated_engine, expire_on_commit=False)
    with sessions.begin() as session:
        session.add(User(id=1, display_name="测试作者"))

    def read_question(qid):
        with isolated_engine.connect() as connection:
            return connection.execute(
                select(Question.__table__).where(Question.id == qid)
            ).mappings().one_or_none()

    def snapshot():
        with isolated_engine.connect() as connection:
            return {
                table.name: connection.execute(
                    select(table).order_by(*table.primary_key.columns)
                ).mappings().all()
                for table in Base.metadata.sorted_tables
            }

    def add_question(title, **values):
        data = {
            "title": title, "body": "这是教师准备的合法问题正文。",
            "author_id": 1, "created_at": datetime(2026, 9, 1, tzinfo=timezone.utc),
        }
        data.update(values)
        with sessions.begin() as session:
            question = Question(**data)
            session.add(question)
            session.flush()
            return question.id

    def new_client():
        return TestClient(app, raise_server_exceptions=False)

    previous = app.dependency_overrides.copy()
    app.dependency_overrides[get_session] = make_test_dependency(sessions)
    try:
        with new_client() as client:
            yield SimpleNamespace(
                client=client, engine=isolated_engine, sessions=sessions,
                read_question=read_question, snapshot=snapshot,
                add_question=add_question, new_client=new_client,
            )
    finally:
        app.dependency_overrides.clear()
        app.dependency_overrides.update(previous)
```

make_test_dependency 使用 §3.2 的定义，放同一 conftest 或显式导入。工厂的 sessions.begin 只用于教师 seed，并且真实提交；不是把业务事务移回依赖。每例都迁移的成本适用于本课小数据，不据此承诺大工程最佳速度。清理前必须确保线程／客户端已结束；异常清理失败应暴露，而非吞掉后假装隔离成功。

第 7 课 env 原本从 settings 建引擎，仅设置 cfg 的 sqlalchemy.url 不会改变它。本课在线入口增加已提供 connection 分支，不改历史 001／002：

```python
# lesson09: migration_env
from alembic import context
from sqlalchemy import create_engine, pool
from app.config import settings
from app.models import Base


def migrate_on(connection):
    context.configure(
        connection=connection, target_metadata=Base.metadata,
        compare_type=True, compare_server_default=True,
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    provided = context.config.attributes.get("connection")
    if provided is not None:
        migrate_on(provided)
        return
    engine = create_engine(settings.database_url, poolclass=pool.NullPool)
    try:
        with engine.connect() as connection:
            migrate_on(connection)
    finally:
        engine.dispose()
```

保留 Alembic 模板的在线／离线调用分支；本课只验收在线。测试连接 search_path 指向自己的 schema，版本表也落在其中，不扫描其他库。正式 bootstrap 须拒绝会绕过目标约束的额外连接参数，并核对真实连接目标。

### 9.2 错误、投票与两种故障的断言

以下帮助函数放 `tests/helpers.py`：

```python
# lesson09: error_helper

def assert_business_error(response, status, code):
    assert response.status_code == status
    body = response.json()
    assert set(body) == {"code", "message", "detail", "request_id"}
    assert body["code"] == code
    assert isinstance(body["message"], str) and body["message"]
    assert body["request_id"] == response.headers["X-Request-ID"]
    assert isinstance(body["request_id"], str) and body["request_id"]
    if status == 422:
        assert isinstance(body["detail"], list) and body["detail"]
        assert all(set(item) == {"loc", "type", "msg"} for item in body["detail"])
    else:
        assert body["detail"] is None
    return body
```

422 的具体测试还要断言目标 loc，不能让别的字段报错充数。标题四字“`四字标题`”拒绝，五字“`五个字标题`”可接受，但正文和其余条件必须合法。

```python
# lesson09: concurrent_test
from concurrent.futures import ThreadPoolExecutor
from threading import Barrier

from tests.helpers import assert_business_error


def test_same_version_accepts_once(case):
    qid = case.add_question("并发测试的独立问题", vote_count=10, version=5)
    ready = Barrier(2, timeout=5)

    def worker():
        with case.new_client() as client:
            detail = client.get(f"/questions/{qid}")
            assert detail.status_code == 200
            assert detail.json()["version"] == 5
            ready.wait()
            return client.post(f"/questions/{qid}/votes", json={"version": 5})

    with ThreadPoolExecutor(max_workers=2) as pool:
        futures = [pool.submit(worker) for _ in range(2)]
        results = [future.result(timeout=15) for future in futures]
    assert sorted(response.status_code for response in results) == [200, 409]
    conflict = next(response for response in results if response.status_code == 409)
    assert_business_error(conflict, 409, "version_conflict")
    stored = case.read_question(qid)
    assert (stored["vote_count"], stored["version"]) == (11, 6)
    replay = case.client.post(f"/questions/{qid}/votes", json={"version": 5})
    assert_business_error(replay, 409, "version_conflict")
    assert case.read_question(qid) == stored
```

此测试即使两个 UPDATE 被调度成先后执行也应通过；它不单独证明发生过行锁等待。第 8 课的丢失更新复现／等锁观察使用另一个教师同步设施；Barrier 放 SELECT 后，不放可能持锁的 UPDATE 后。future 超时不自动终止线程，教师还配置有限数据库语句／连接超时，失败后等待工作线程退出再清理 schema。

两种故障沿用第 7／8 课服务回调；以下仅绑定原服务的教师注入参数，不用 fake 服务取代生产逻辑。放 `tests/integration/test_faults.py`：

```python
# lesson09: fault_tests
from functools import partial

import pytest
from app.api import questions as routes
from tests.helpers import assert_business_error


@pytest.mark.parametrize("stage", ["after_flush", "after_commit"])
def test_fault_position_controls_data(case, monkeypatch, stage):
    before = case.snapshot()
    observations = []

    def fail():
        observations.append(case.snapshot())
        raise RuntimeError("教师固定故障")

    original = routes.create_question_service
    monkeypatch.setattr(routes, "create_question_service", partial(original, **{stage: fail}))
    response = case.client.post("/questions", json={
        "title": "故障测试中新创建的问题", "body": "这是足够长的合法故障测试正文。",
        "tags": ["故障标签甲", "故障标签乙"],
    })
    assert_business_error(response, 500, "internal_error")
    assert len(observations) == 1
    after = case.snapshot()
    if stage == "after_flush":
        assert observations[0] == before
        assert after == before
    else:
        assert observations[0] == after
        assert len(after["questions"]) == len(before["questions"]) + 1
        assert len(after["tags"]) == len(before["tags"]) + 2
        assert len(after["question_tags"]) == len(before["question_tags"]) + 2
    monkeypatch.setattr(routes, "create_question_service", original)
    recovery = case.client.post("/questions", json={
        "title": "故障之后可以继续创建的问题", "body": "恢复请求同样必须使用合法的正文。",
    })
    assert recovery.status_code == 201
    assert case.read_question(recovery.json()["id"]) is not None
```

patch 的目标是**端点查找服务的实际绑定位置**，不是另一个没被调用的别名。monkeypatch 即使断言失败也恢复绑定。该测试使用全新无其他问题／标签的 case；精确字段与关联目标还由教师回归核对。教师生命周期记录器另验证 `commit_ok → after_commit → http.response.start`，不把回读断言当成响应发送顺序证据。

### 9.3 OpenAPI：导出、check 与实际响应分开

教师提供 `scripts/export_openapi.py`；应用导入不得自动迁移／seed／连接数据库，依赖和配置仍须有效。使用新进程导出，避免动态改路由后沿用旧缓存。

```python
# lesson09: export_openapi
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
            raise SystemExit("OpenAPI 快照不一致：先审查契约，再显式导出")
    else:
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")


if __name__ == "__main__":
    main()
```

快照由批准的第 8 课契约生成并提交，不把生成时间写进 JSON。check 不覆盖文件；快照缺失也失败。正常导出命令 `uv run --no-sync python -m scripts.export_openapi` 只在审查差异后使用。

以下 helper 放 `tests/schema_helper.py`，限定 OpenAPI 3.1 的本课普通 JSON 响应；整份交付快照作为引用根，不丢掉 components。它不是完整 OpenAPI 验证器，头／语义／副作用还要独立断言。

```python
# lesson09: schema_helper
import json
from pathlib import Path
from jsonschema import Draft202012Validator, FormatChecker
from referencing import Registry, Resource
from referencing.jsonschema import DRAFT202012

SPEC_URI = "urn:course:openapi"
SPEC = json.loads(
    (Path(__file__).resolve().parents[1] / "contracts" / "openapi.json").read_text(encoding="utf-8")
)
REGISTRY = Registry().with_resource(
    SPEC_URI, Resource.from_contents(SPEC, default_specification=DRAFT202012),
)


def assert_response_schema(response, path_template, method):
    operation = SPEC["paths"][path_template][method.lower()]
    status = str(response.status_code)
    assert status in operation["responses"]
    assert response.headers["content-type"].split(";", 1)[0] == "application/json"
    escaped = path_template.replace("~", "~0").replace("/", "~1")
    pointer = f"#/paths/{escaped}/{method.lower()}/responses/{status}/content/application~1json/schema"
    Draft202012Validator(
        {"$ref": SPEC_URI + pointer}, registry=REGISTRY, format_checker=FormatChecker(),
    ).validate(response.json())
```

代表性用例调用 `assert_response_schema(response, "/questions/{qid}/votes", "post")`；先通过正确响应，再在内存副本移除 vote_count／把它改成字符串，确认 helper 拒绝。业务错误仍断言特定 code；ErrorOut.detail 宽泛，Schema 通过不能证明 loc/type/msg 或 PATCH“至少一项”规则正确。

最小类型消费者由教师给定源码与 package-lock.json、strict tsconfig.json、`check: tsc --noEmit`；明确只检查已写入的类型与消费者。第 9 课不强制学生开发自动类型生成链，不引用第 8 课不存在的 gen 脚本。Schema 和消费者都改了仍不能替代独立业务断言。

### 9.4 四门禁入口与 CI 参考

教师包提供 app／tests/unit／tests/integration／tests/contract／scripts、Python dev 依赖与锁文件、contract-client 锁文件。依赖包括 pytest、Ruff、TestClient 适配包、Alembic、jsonschema/referencing；测试库准备属于 bootstrap，不在此命令中默认创建任意数据库。

```python
# lesson09: check_script
import argparse
import os
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
NPM = "npm.cmd" if os.name == "nt" else "npm"
GROUPS = {
    "lint": [
        [sys.executable, "-m", "ruff", "check", "app", "tests", "scripts"],
        [sys.executable, "-m", "ruff", "format", "--check", "app", "tests", "scripts"],
    ],
    "type": [[NPM, "--prefix", "contract-client", "run", "check"]],
    "test": [[sys.executable, "-m", "pytest", "tests/unit", "tests/integration", "-q"]],
    "contract": [
        [sys.executable, "-m", "scripts.export_openapi", "--check"],
        [sys.executable, "-m", "pytest", "tests/contract", "-q"],
    ],
}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("gate", choices=["all", *GROUPS], default="all", nargs="?")
    args = parser.parse_args()
    for gate in GROUPS if args.gate == "all" else [args.gate]:
        for command in GROUPS[gate]:
            subprocess.run(command, cwd=ROOT, check=True)


if __name__ == "__main__":
    main()
```

本课所有集成用例都采用真实提交 case，因此没有必须另建的 committed 测试库／目录。pytest 无测试通常退出 5，也应让门禁失败。参考工作流使用一个 job；服务密码是一次性虚构测试值，不复用任何真实账户。

```yaml
# lesson09: workflow
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
      - run: uv run --no-sync python -m scripts.check all
```

PostgreSQL 镜像的初始化账户在这个一次性服务内权限较高，只用于隔离 runner，不将此配置推广到共享服务器；正式本地 bootstrap 使用受限角色。生产凭据、持久数据卷不进入该服务。Actions 主版本标签是教学接线参考，正式模板由教师锁定审核过的版本／提交；本轮不代用户提交工作流或修改远端保护规则。

## 十、制作与验证状态

本轮重写与 M3 全工程交付分开，不沿用旧稿与第 8 课合计的 SQLite 检查数字。

- **本轮实测完成**：从本稿提取 11 个 Python 围栏及 YAML，复用第 3／4／6／7／8 课输入模型、错误／追踪、模型／服务与迁移，动态装配最小 FastAPI 应用。最终临时 pytest 套件 **49 项，连续两次全部通过**；另记录 **47 项机制检查**，包含围栏语法、运行结果、隔离、快照、门禁分发、工作流静态检查、工具正反例与课时核对。参数化用例数不等于关键路径数，复跑和单跑不累计凑数，两类计数也不合并成“完整 M3 验收项”。
- **正例与分页红绿实测**：先单跑正常创建测试通过；只将 OFFSET 改为 page×page_size 后，第二页在 id 列表断言失败，实际为 1005…1001，而 200／total=25／page=2 断言仍通过。恢复一行后同一测试通过，再跑完整套件。捕获真实查询绑定 LIMIT=10／OFFSET=20、函数帧 page=2／page_size=10 与同次 request-id 起止日志；程序采集的调用帧不冒充 IDE 断点截图，本轮未完成课堂四件证据全套。
- **真实提交与隔离实测**：每个 case 经 Alembic 001→002 建表，没有先 create_all，也没有外层回滚包装；迁移使用 cfg 提供的 connection，没有访问故意设为无效地址的回退配置。正常创建独立连接可见，服务 commit_ok 先于响应启动；同旧版本两次投票一 200 一 409，最终 11／6，重放不再增加。故障 after_flush 返回 500 且五表数据不变；after_commit 同为 500，但问题／新标签／关联已提交；两个注入点均先于 500 响应启动，恢复后可正常创建。全套结束 override 已恢复，本轮 case schema 无残留。
- **契约回归实测**：覆盖字面搜索、列表五字段、分页边界、非法创建与目标 loc、创建／PATCH 标题冲突无半截写入、PATCH 单／双字段与省略／拒绝语义、资源缺失及严格版本类型。实际创建／列表／详情／投票／PATCH 与代表错误响应通过 Schema helper；移除 vote_count 或改为字符串均被拒绝。快照 check 对稳定内容只读，对漂移／缺失失败且不覆盖，显式导出恢复稳定内容；不把本次函数装配检查说成完整应用的新进程导出验收。
- **门禁机制实测及边界**：以替身记录子进程分发，核对 all 的六条子命令、各组命令、固定工作目录、check=True 与首错停止；YAML 仅做解析／静态核对。另实际运行 Ruff 正确／未定义变量对照、TypeScript 最小消费者正确／字符串版本 TS2322 对照，以及 pytest 零测试退出 5。**没有运行正式课程包的四门禁 all，不声称完整 lint／type 或远端 CI 全绿。**
- **环境与隔离**：复用前课 Python 3.12.12、FastAPI 0.141.1、Pydantic 2.13.5、SQLAlchemy 2.0.54、psycopg 3.3.6 与工作区专用 PostgreSQL **18.6** 集群；实际使用该集群的 postgres 数据库和随机 case schema，不等同于正式 qanda_test 目标配置验收。仅本地权限 0700 的 Unix socket，UTC／READ COMMITTED。复用 Alembic 1.20.0 临时目录，另在 `.build-check/lesson09-tools` 安装 pytest 9.1.1、Ruff 0.16.9、jsonschema 4.26.0、referencing 0.37.0、PyYAML 6.0.3；TypeScript 使用仓库既有 5.9.3。离线缺包后联网安装到临时目录，未修改项目依赖／锁文件或原虚拟环境。启动时遇到沙箱共享内存权限限制，按原隔离参数获准启动；核验后已正常停库，不将权限问题当业务故障实验。
- **正式课程包待制作**：正确应用／单缺陷副本、批准目标 bootstrap、完整继承回归、Python／Node 锁文件、最小类型消费者、快照与门禁入口；fixture 依赖必须接全，不能拿片段当工程交付。
- **外部与目标环境待验收**：PostgreSQL 16、完整 M2 数据与 HTML／探针回归、真实 GitHub Actions／分支保护、IDE 断点与四件证据、浏览器端到端；未执行不声称通过。
- **试讲待验收**：15 分钟逐行写正例、18 分钟模板与保护演示、25 分钟学生红绿闭环、15 分钟同次证据关联能否完成；不挤掉学生操作时间容纳工具安装。

临时复核入口（依赖上述工具目录与已启动的专用数据库 socket，不是学生启动命令）：

```bash
uv run --offline --project snippets/ch01/m0-tracer --no-sync python .build-check/validate_lesson09.py
```

最终执行记录位于 `.build-check/l09-ca27ebd0bb7e4839b3ebe347a056a861/result.json`，分页运行记录同目录 `pagination-evidence.json`；临时文件不作为已交付课程包。运行有 Starlette 的 httpx 适配弃用提示，以及嵌入式 pytest 对已导入 anyio 的断言重写提示；未为消除提示修改原依赖。IDE 语言服务未就绪，不声称 IDE 检查全绿。最终 Slidev、视觉／导出与真实试讲未在本轮进行。

参考：pytest Fixtures、FastAPI Testing Dependencies、SQLAlchemy Session／PostgreSQL 事务、Alembic Cookbook 连接共享、OpenAPI 3.1、jsonschema/referencing、GitHub Actions 服务容器与 required status checks。最终 Slidev 中教师时间、配置制作与应急切换进入备注，学生所需操作、规则与证据边界留正文。
