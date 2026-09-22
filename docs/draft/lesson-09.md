# 第 9 次课教学底稿
## 测试与质量守卫：把纪律变成会失败的东西

---

## 〇、给 PPT 制作团队的全局说明

本次课 100 分钟，留 5 分钟缓冲。**本次课是全课程"把纪律变成结构"这条主线的总收口。** 前八次课积累了十三条纪律，每一条到今天为止都还靠"我记得"。今天的任务是把它们一条条变成"会红的东西"。

**本次课的核心思想，请让它贯穿始终，并在单元 5、6、8 各回引一次**：

> **测试的价值不在于它通过，在于它失败。**
>
> **一条从来没有红过的检查，你无法知道它是不是真的在工作。**

这句话要做成开场后的第一张封面级素材。它同时也是本次课的方法论要求：**今天写的每一条检查，都必须当场制造一次违反、看到它变红、再修复。红-绿两步都演示，缺一不可。**

**本次课有三个高光，按重要性排序**：

1. **把纪律变成检查，四条，红-绿全演示（单元 5，20 分钟）**。这是本次课的主体，也是与全课程主线的接点。其中第 1 条（`response_model` 检查用 `app.routes`）必须做，因为它回收第 3 次课"打印 app.routes 看清它是数据结构"——**当时是为了破除魔法，今天那个数据结构变成了检查的输入。可检视是可检查的前提。**
2. **"测试通过但代码是错的"（单元 2 演示一 + 单元 4）**。AI 把 repository mock 掉，然后 service 测试在测 mock。现场把 service 的核心逻辑整段删掉，测试**依然全绿**。这是解剖台的最高潮。
3. **覆盖率的真相（单元 6，7 分钟）**。现场把所有 `assert` 删掉，覆盖率**一点不变**。这个演示只要 40 秒，杀伤力极大。

**第四处值得重点制作的**：单元 3.4 的测试隔离方案。它回收第 7 次课"commit 只在 deps.py"——**正因为 commit 集中在一处，测试才能接管事务边界**。这是"当初那个架构决定今天才兑现"的又一个例子，和第 8 次课的 request_id 闭环是同一类素材。

**若时间不够的压缩顺序**：先压单元 9 的 C 档卡（整体移课后）→ 再压单元 7 的 Playwright 部分（只给结论，移作业）→ 再压单元 5 的第 4 条检查（留作业）。**单元 2、3、5、6 不能压缩。**

**一个需要教师裁决的地方**：单元 3.4 的事务回滚隔离方案用到 SQLAlchemy 2.0 的 `join_transaction_mode="create_savepoint"`。这个参数是 2.0.0 之后才有的，且行为依赖数据库对 savepoint 的支持。如果你的学生环境版本杂乱，底稿在单元 3.4 给了一个降级方案（每个测试 truncate）。**请提前统一版本，这是本次课最可能翻车的地方。**

---

## 一、开场：十三条纪律，全都靠"我记得"

**约 4 分钟。请从这张表开始，不要先讲测试。**

### 1.1 把八次课的欠账摊在桌面上

**封面级素材，本次课的第一张图**：

| # | 来源 | 纪律 | 现在靠什么保证 |
|---|---|---|---|
| 1 | 第 3 次课 | 每个端点必须有 `response_model` | 我记得 |
| 2 | 第 3 次课 | Out schema 不含敏感字段 | 我记得 |
| 3 | 第 4 次课 | `services/` 不 `import fastapi` | 我记得 |
| 4 | 第 4 次课 | 错误响应体结构统一 | 我记得 |
| 5 | 第 5 次课 | `async def` 里不许有阻塞调用 | 我记得 |
| 6 | 第 5 次课 | 模板里不许出现 `\| safe` | 我记得 |
| 7 | 第 6 次课 | 所有表有主键、所有外键有索引 | 我记得 |
| 8 | 第 7 次课 | `.commit()` 只出现在 `deps.py` | 我记得 |
| 9 | 第 7 次课 | 迁移能 upgrade 也能 downgrade | 我记得 |
| 10 | 第 7 次课 | 列表端点 SQL 条数 ≤ 3 | 我记得 |
| 11 | 第 8 次课 | `api.d.ts` 与后端契约一致 | 我记得 |
| 12 | 第 8 次课 | `tsc --noEmit` 零错误 | 我记得 |
| 13 | 第 8 次课 | 前端不用 `innerHTML` 接用户数据 | 我记得 |

停顿，然后问：

> **这十三条，哪一条是你三个月后还记得的？**
>
> 更实际的问题：**哪一条是新来的同事会知道的？哪一条是 AI 会遵守的？**

### 1.2 本次课的定位

讲：

> 这门课从第 2 次课开始，反复出现同一个模式：
>
> - "记得给 Out schema 排除密码字段" → 不如 **`response_model` 让它出不去**
> - "记得转义用户输入" → 不如 **Jinja2 默认转义**
> - "记得在应用层查重" → 不如 **数据库 `UNIQUE` 约束**
> - "记得不要懒加载" → 不如 **`lazy="raise"` 直接报错**
> - "记得字段名别写错" → 不如 **生成类型让 tsc 报错**
>
> 每一次我都说同一句话：**把依赖人记得的规则，换成会出声的机制。**
>
> 但那五道护栏只覆盖了五类问题。**上面那十三条里，大部分目前还是"我记得"。**
>
> 今天要做的，就是把剩下的也变过去。手段有两个：**测试**和 **CI**。
>
> 不过在开始之前，我必须先把一件事讲清楚，否则今天做的全是白费——

**封面级素材，单独一页**：

> **测试的价值不在于它通过，在于它失败。**
>
> **一条从来没有红过的检查，你无法知道它是不是真的在工作。**

> 这句话听起来像绕口令，但它是今天所有内容的地基。
>
> 一个全绿的测试套件有两种可能：**代码是对的**，或者**测试什么都没测**。
>
> 而这两种情况，从 CI 的绿色对勾上**完全看不出区别**。
>
> 所以今天有一条铁律：**我们写的每一条检查，都要当场破坏一次，看它变红。红过了，才算它存在。**

### 1.3 本次课要回答的问题

- 一个"测试通过但代码是错的"的测试套件长什么样？**我怎么识别它？**
- 什么该 mock，什么不该 mock？**判据是什么？**
- 测试之间为什么会互相影响？怎么彻底隔离？
- 覆盖率 92% 意味着什么？**意味着代码有 92% 是对的吗？**
- 怎么把"`commit` 只能在 `deps.py`"这种规则变成一条会红的检查？
- CI 里该放什么，不该放什么？
- **AI 写的测试，为什么会把 bug 一起固化下来？**

---

## 二、解剖台：AI 写的那套测试

**约 12 分钟。四个演示都要做，第一个是重点。**

### 情境设定

> 你对 AI 说："给我的项目写单元测试，覆盖率要高一点。"
>
> 它给了你 `tests/` 目录，23 个测试，全部通过，覆盖率 92%。
>
> 你很满意，提交了。

### 代码（tag: `v9-broken`）

```python
# tests/test_question_service.py —— AI 原样产出
from unittest.mock import MagicMock, patch
from app.services import question as svc

def test_create_question():
    mock_session = MagicMock()
    mock_repo = MagicMock()
    mock_repo.insert.return_value = 1
    mock_repo.find_detail.return_value = {"id": 1, "title": "测试标题"}

    with patch("app.services.question.repo", mock_repo):
        result = svc.create(mock_session, "测试标题", "测试正文内容", 1, [])

    assert result["id"] == 1
    assert result["title"] == "测试标题"


def test_get_question():
    mock_session = MagicMock()
    mock_repo = MagicMock()
    mock_repo.find_detail.return_value = {"id": 5, "title": "某问题"}
    with patch("app.services.question.repo", mock_repo):
        result = svc.get(mock_session, 5)
    assert result is not None
```

```python
# tests/test_api.py
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_list_questions():
    res = client.get("/questions")
    assert res.status_code == 200

def test_create_question_api():
    res = client.post("/questions", json={
        "title": "一个新问题的标题", "body": "这是问题的正文内容"})
    assert res.status_code == 201
    global created_id
    created_id = res.json()["id"]                     # ← 记住这里

def test_get_created_question():
    res = client.get(f"/questions/{created_id}")      # ← 和上面这个
    assert res.status_code == 200

def test_question_not_found():
    res = client.get("/questions/999999")
    assert res.status_code == 404
    assert res.json()["message"] == "问题不存在"       # ← 还有这里

def test_health():
    res = client.get("/healthz")
    assert res.status_code in (200, 503)              # ← 以及这里
```

先让学生看 40 秒，问：**你觉得这套测试怎么样？**

多数人会说"还行""看起来挺正常"。**这就是问题所在。**

### 演示一：把业务逻辑整段删掉，测试依然全绿（**本单元最高光**）

打开 `app/services/question.py`，把 `create` 的函数体**整个换成一行**：

```python
def create(session, title, body, author_id, tag_names):
    return {"id": 1, "title": "测试标题"}       # ← 什么也不做，直接返回
```

```bash
pytest tests/test_question_service.py -q
# ..                                    [100%]
# 2 passed in 0.08s
```

**停下来，让这个结果停留 10 秒。**

> **我把业务逻辑全删了。不写库、不建标签、不查重。测试全绿。**
>
> 为什么？因为这个测试把 `repo` mock 掉了，**然后断言 mock 的返回值等于 mock 的返回值**。
>
> 它测的不是 `svc.create`，**它测的是 `MagicMock` 能不能正常工作**。而 `MagicMock` 当然能正常工作，它是标准库的一部分。

**做成一页醒目图**：

```
测试以为在测：   svc.create  →  repo.insert  →  数据库
测试实际在测：   svc.create  →  MagicMock  →  （空）
                              ↑
                       所有真实行为都在这条线的右边
                       而这条线被切断了
```

> 判据：**如果你把被测函数的实现删掉，测试还能通过——那这个测试没有测任何东西。**
>
> 这是一条可以立刻拿去用的自检手段，我们等下会给它起个名字。

### 演示二：打乱顺序，测试塌方

```bash
pip install pytest-randomly
pytest -q
```

```
tests/test_api.py::test_get_created_question FAILED
NameError: name 'created_id' is not defined

tests/test_api.py::test_create_question_api FAILED
AssertionError: assert 409 == 201
```

> 两个失败，两个不同的原因：
>
> 1. `test_get_created_question` 依赖 `test_create_question_api` **先跑**，靠一个全局变量传值。顺序一变就找不到。
> 2. `test_create_question_api` 第二次跑就是 409——**因为第一次跑的时候那条数据真的写进数据库了，而且再也没被清掉**。标题唯一约束（第 6 次课那道护栏）把它挡下来了。

> 这两个问题的共同根源：**测试之间共享了状态。**
>
> 后果比"顺序敏感"严重得多：
>
> | 现象 | 真实后果 |
> |---|---|
> | 单跑一个测试会失败 | 你没法只跑一个测试调试 |
> | 本地全跑通过，CI 挂 | CI 的库是干净的 |
> | 今天通过，明天挂 | 数据库里攒了一堆前几次跑剩的数据 |
> | 并行跑测试就炸 | 永远没法加速 |
>
> **判据：每个测试必须能单独跑、能以任意顺序跑、能重复跑，结果都一样。**
>
> 这条性质有个名字：**测试的独立性**。单元 3 会给出实现它的具体办法。

### 演示三：改一个字，五个测试红

把错误文案从"问题不存在"改成"该问题不存在或已删除"：

```bash
pytest -q
# 5 failed
# AssertionError: assert '该问题不存在或已删除' == '问题不存在'
```

> **一次纯文案修改，五个测试失败。而代码的行为一点没变。**
>
> 这是**脆弱测试**：它把实现细节（具体文案）当成了契约。
>
> 正确的断言对象是第 4 次课那个**稳定标识**：
>
> ```python
> assert res.status_code == 404
> assert res.json()["code"] == "question_not_found"    # ← 稳定的
> # 不要断言 message
> ```
>
> **回收判据：依赖稳定标识，不依赖人类可读的文案。**
>
> 这是这条判据在本课程的**第五次**出现——422 的 `type`（第 3 次课）、数据库约束名（第 6 次课）、错误 `code`（第 4 次课）、前端错误分支（第 8 次课）、今天的测试断言。
>
> 五次出现在五个完全不同的场景。**这说明它不是一个技巧，是一条原则。**

### 演示四：永远不会失败的断言

```python
assert res.status_code in (200, 503)          # 健康检查
assert result is not None                      # get 测试
```

现场把 `/healthz` 端点改成永远返回 503：

```bash
pytest tests/test_api.py::test_health -q
# 1 passed         ← 当然通过
```

> `in (200, 503)` 覆盖了这个端点**可能返回的全部状态码**。这条断言的信息量是零。
>
> `assert result is not None` 也一样——只要函数不返回 `None` 就通过，**返回一个错误的对象照样通过**。
>
> 判据：**写完一条断言，问自己"什么情况下它会失败"。答不上来就是废的。**

### 四个问题的性质对照（**做成一页**）

| # | 问题 | 名字 | 后果 |
|---|---|---|---|
| ① | mock 掉了要测的东西 | **测试替身滥用** | 测试通过但代码是错的 |
| ② | 测试间共享状态 | **测试不独立** | 顺序敏感、无法并行、CI 与本地不一致 |
| ③ | 断言人类可读文案 | **脆弱测试** | 改文案就红，改行为不红（**方向完全反了**） |
| ④ | 断言永远为真 | **空断言** | 覆盖率有了，保护没有 |
| —— | | | |
| **共同点** | **全部通过，覆盖率 92%** | | |

> 请注意这个对照表和前几次课的一个重要差别：
>
> 前几次课的问题是"代码有毛病，但测试和检查发现不了"。
> **今天的问题是"检查本身有毛病"。**
>
> 这更危险——因为它提供的是**虚假的安全感**。没有测试的时候你会小心；有一套绿色的假测试，你就不小心了。
>
> **判据：一套坏的测试比没有测试更糟。**

### 欠账清单

| 问题 | 本次课处理 | 何时还 |
|---|---|---|
| mock 滥用 | **单元 4** | — |
| 测试不独立 | **单元 3.4** | — |
| 脆弱断言 | 单元 3.6 | — |
| 空断言 | 单元 6.3（变异思路） | — |
| 覆盖率高但没保护 | **单元 6** | — |
| 十三条纪律没有检查 | **单元 5、7** | 剩余项 → 作业 |
| 没有 CI | **单元 8** | — |
| 测试跑得慢 | 单元 8.4 给判据 | 第 16 次课（部署流水线） |
| 端到端测试 | 单元 7.4 给结论 | 作业 B 档 |
| 性能回归的基线 | 单元 5.3 给做法 | 第 11 次课 |

---

## 三、测试基础设施：让每个测试都干净

**约 14 分钟。**

### 3.1 先划清三层测试的分工

**醒目页**：

| 层 | 测什么 | 有没有数据库 | 数量 | 跑多快 |
|---|---|---|---|---|
| **单元测试** | 纯逻辑：schema 校验、业务规则函数、工具函数 | ❌ | 少 | 毫秒 |
| **集成测试** | 端点 → service → repo → **真实数据库** | ✅ | **最多** | 几十毫秒 |
| **端到端测试** | 浏览器 → 前端 → 后端 → 数据库 | ✅ | 极少 | 秒级 |

**然后给一个和常见说法不同的判断**：

> 你可能听过"测试金字塔"：单元测试要最多，集成测试次之，端到端最少。
>
> **对我们这类项目，我给一个不一样的建议：集成测试最多。**
>
> 理由：**Web 应用的 bug 大部分发生在"层与层的接缝处"**——
>
> | 真实 bug | 发生在哪 | 单元测试能发现吗 |
> |---|---|---|
> | schema 字段名和 ORM 属性对不上 | router ↔ schema | ❌ |
> | service 忘了 flush，拿不到 id | service ↔ session | ❌ |
> | 外键约束触发，报了 500 不是 409 | repo ↔ 数据库 | ❌ |
> | 排序没带主键，翻页重复 | repo ↔ SQL | ❌ |
> | N+1 | ORM ↔ 序列化 | ❌ |
>
> **而单元测试恰恰是通过 mock 把这些接缝切断的。** 它测的是每一层内部，而 bug 在层之间。
>
> 判据：**逻辑复杂的地方写单元测试，边界多的地方写集成测试。** 我们的项目业务逻辑不复杂，边界很多，所以重心在集成测试。
>
> 〔反过来说：如果你在写一个定价引擎、一个规则解析器、一个状态机，单元测试就该是主力。**判据跟着代码形态走，不跟着口号走。**〕

### 3.2 测试数据库：不要用生产库，也不要用 SQLite

**三个选项的判据表**：

| 方案 | 优点 | 致命问题 |
|---|---|---|
| 用开发库 | 省事 | 测试会污染你的开发数据；跑完一次就脏了 |
| **用 SQLite 内存库** | **快** | **它不是 PostgreSQL** ← 见下 |
| **独立的 PostgreSQL 测试库** | 与生产同构 | 稍慢，要配置 |

**SQLite 那一行要专门讲**，因为它是最常见的诱惑：

> 用 SQLite 跑测试，下面这些第 6、7 次课学过的东西**全部测不出来**：
>
> | 你依赖的 | SQLite 的行为 |
> |---|---|
> | `CHECK` 约束里的 `char_length()` | 函数不存在 |
> | 外键约束 | **默认关闭** |
> | `ON DELETE CASCADE` | 外键关了就不生效 |
> | `TIMESTAMPTZ` | 没有时区概念 |
> | `ILIKE` | 不支持 |
> | `RETURNING` | 旧版本不支持 |
> | `generate_series` | 不存在 |
> | 并发行为 | 整库锁 |
>
> **判据：测试数据库必须和生产是同一个引擎、同一个大版本。** 否则你测的是另一个系统。
>
> 这条判据的代价是：本地要跑一个 Postgres。用 Docker 一行命令的事，**不要为了省这一行去换引擎**。

### 3.3 用迁移建测试库，不要用 `create_all`

```python
# tests/conftest.py
@pytest.fixture(scope="session")
def engine():
    eng = create_engine(settings.test_database_url)
    _reset_schema(eng)                           # drop schema 重建
    cfg = Config("alembic.ini")
    cfg.set_main_option("sqlalchemy.url", settings.test_database_url)
    command.upgrade(cfg, "head")                 # ← 用迁移建表
    yield eng
    eng.dispose()
```

> 有一个更简单的写法是 `Base.metadata.create_all(engine)`。**不要用它。**
>
> 两个理由：
>
> 1. **`create_all` 绕过了迁移链。** 于是"模型对但迁移写错了"这类 bug 测不出来——而第 7 次课我们刚见识过迁移脚本能有多危险。
> 2. **用迁移建库，等于每次跑测试都在测你的迁移。** 这是白送的第 9 条纪律检查。
>
> 判据：**测试环境要用和生产一样的方式搭建。** `create_all` 是一条生产上不存在的路径。

### 3.4 测试隔离：每个测试一个事务，结束回滚（**本单元核心**）

**先给三个方案的判据表**：

| 方案 | 怎么做 | 一个测试耗时 | 问题 |
|---|---|---|---|
| A. 每个测试重建库 | drop + migrate | **~2 s** | 100 个测试要 3 分钟 |
| B. 每个测试 TRUNCATE | 清空所有表 | ~20 ms | 要维护表清单；序列要重置 |
| **C. 每个测试一个事务，结束回滚** | 见下 | **~2 ms** | **需要接管事务边界** |

**C 的实现**：

```python
# tests/conftest.py
@pytest.fixture
def session(engine):
    conn = engine.connect()
    outer = conn.begin()                       # ① 外层事务，整个测试都在它里面

    s = Session(bind=conn,
                join_transaction_mode="create_savepoint",   # ② 关键
                expire_on_commit=False)
    try:
        yield s
    finally:
        s.close()
        outer.rollback()                       # ③ 一切撤销，数据库回到测试前
        conn.close()
```

**逐行讲三处**：

> **① 外层事务**：整个测试期间的所有写入都在这一个事务里。
>
> **③ 回滚**：测试结束时 rollback，**这个测试写的一切全部消失**。不用删数据、不用 truncate、不用重置序列——因为它们从来没有真正提交过。
>
> **② `join_transaction_mode="create_savepoint"` 是关键的一行**，它解决一个具体的问题：

**停下来，提一个问题**：

> 被测的代码里会调 `session.commit()`（我们的 `get_session` 依赖里就有一个）。
>
> **如果被测代码 commit 了，那外层事务是不是就提交了？那我还怎么回滚？**

> 答案：**普通情况下确实会，这正是这个方案最大的坑。**
>
> `join_transaction_mode="create_savepoint"` 的作用是：Session 的 `begin`/`commit` 映射成 **savepoint 的建立和释放**，而不是真正的事务提交。**外层事务始终没有提交**，所以最后那个 `outer.rollback()` 能把一切撤销。

**然后做一个重要的回收（做成醒目页）**：

> 请注意这个方案能成立的前提：
>
> **我们的项目里，`.commit()` 只出现在一个地方。**
>
> 第 7 次课我们把 15 处 commit 收敛成 1 处，当时给的理由是"事务边界 = 请求边界"。
>
> **今天它兑现了第二个好处：因为事务边界只有一处，测试才能干净地接管它。**
>
> 反过来想：如果 service 里散布着 15 个 commit，每一个都可能提前把事务结束掉，**这个隔离方案根本无法工作**，你只能退回方案 B 或 A，测试慢 10 到 1000 倍。
>
> **判据：一个架构决定的价值，往往在几层之外才显现。** 第 8 次课的 request_id 是一次，今天是第二次。

〔**教师裁决点**：如果环境里 SQLAlchemy 版本不足 2.0，或者 savepoint 行为异常，降级到方案 B。`conftest.py` 里提供了 `truncate_all()` 的备用实现，切换只需改一个 fixture。**不要在课上调试版本问题，直接切。**〕

### 3.5 `dependency_overrides`：第 4 次课的伏笔兑现

```python
# tests/conftest.py
@pytest.fixture
def client(session):
    def _override():
        yield session                 # ← 把测试的 session 塞给应用

    app.dependency_overrides[get_session] = _override
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()
```

**做成醒目页**：

> 第 4 次课讲依赖注入时，我给的理由是"消除重复""让依赖有名字"。
>
> 当时有同学问："就为了少写几行，值得引入一个机制吗？"
>
> **今天是那个问题的完整答案。**
>
> `dependency_overrides` 是一个字典：`{原依赖函数: 替代函数}`。FastAPI 在解析依赖时先查这张表。
>
> **应用代码一个字都不用改**，测试就能把数据库换成测试库、把当前用户换成假用户、把外部服务换成桩。
>
> | | 没有依赖注入 | 有依赖注入 |
> |---|---|---|
> | 测试时换数据库 | 改 `app/db.py` 读环境变量，**测试和生产共用一条代码路径** | 一行 override |
> | 测试时伪造用户 | 只能真的走一遍登录 | 一行 override |
> | 测试时让外部服务失败 | 改代码或 monkeypatch 到处打补丁 | 一行 override |
>
> **判据：依赖注入最大的回报不在生产代码里，在测试里。**
>
> 而且注意 `app.dependency_overrides` 这个东西本身——**它就是一个普通的字典**。和第 3 次课的 `app.routes` 一样：
>
> **框架没有魔法，只有你还没打印出来的数据结构。**（第 3 次课，今天第二次用上）

### 3.6 一个可用的测试长什么样

```python
# tests/test_questions_api.py
def test_create_question_returns_201_and_persists(client, session):
    res = client.post("/questions", json={
        "title": "如何理解三值逻辑", "body": "我在第六次课没听懂这一段"})

    assert res.status_code == 201
    body = res.json()
    assert body["title"] == "如何理解三值逻辑"

    # 真的落库了吗
    row = session.scalar(select(Question).where(Question.id == body["id"]))
    assert row is not None
    assert row.status == "open"              # server_default 生效了吗


def test_duplicate_title_returns_409(client, question_factory):
    question_factory(title="一个已经存在的标题")

    res = client.post("/questions", json={
        "title": "一个已经存在的标题", "body": "正文内容够长了"})

    assert res.status_code == 409
    assert res.json()["code"] == "duplicate_title"      # ← 稳定标识


def test_get_missing_question_returns_404(client):
    res = client.get("/questions/999999")
    assert res.status_code == 404
    assert res.json()["code"] == "question_not_found"
    assert "request_id" in res.json()                   # ← 错误契约完整性
```

**四个要点**：

| 要点 | 说明 |
|---|---|
| **测试名说清"什么条件下、期望什么"** | 测试失败时，名字本身就是报告 |
| **断言状态码 + `code`，不断言 `message`** | 稳定标识（第五次） |
| **不只断言响应，还查一次数据库** | 回到解剖台演示一：只断言返回值，mock 也能骗过你 |
| **失败路径和成功路径同等重要** | AI 的 23 个测试里只有 1 个测失败路径 |

**关于 factory（一定要给，学生最缺这个）**：

```python
# tests/factories.py
@pytest.fixture
def question_factory(session, user_factory):
    created = []
    def _make(**kw):
        kw.setdefault("title", f"测试问题标题 {uuid4().hex[:8]}")   # ← 唯一
        kw.setdefault("body", "这是一段足够长的测试正文内容")
        kw.setdefault("author", user_factory())
        q = Question(**kw)
        session.add(q); session.flush()
        created.append(q)
        return q
    return _make
```

> 两个设计点：
>
> 1. **唯一值用随机后缀**。否则第二次调用就撞 `UNIQUE` 约束——解剖台演示二那个 409 就是这么来的。
> 2. **`flush` 不是 `commit`**（第 7 次课）。拿到 id，但不提交，让 3.4 的回滚兜底。

### 材料

- `tests/conftest.py`：完整可用，含方案 C 与方案 B 的降级开关。
- `tests/factories.py`：三个 factory（user / question / answer）。
- **高光图**：单元 3.1 的"bug 发生在接缝处"五行表。
- **封面级素材**：单元 3.4 的"commit 收敛 → 测试能接管事务"回收页。
- **封面级素材**：单元 3.5 的 `dependency_overrides` 对照表 + "框架没有魔法"回收。
- 截图：`pytest -q` 从 23 passed（假测试）到重写后的测试数与耗时对比。
- 截图：方案 A/B/C 三种隔离方式的实测耗时（100 个测试）。

---

## 四、测试替身：什么该 mock，什么不该

**约 10 分钟。**

### 4.1 先给判据表（**本单元核心，醒目页**）

| 对象 | mock 吗 | 理由 |
|---|---|---|
| **外部 HTTP 服务**（支付、短信、第三方 API） | ✅ **必须** | 慢、要钱、不稳定、可能真的发出去 |
| **邮件 / 推送发送** | ✅ **必须** | 同上 |
| **当前时间** | ✅ 需要时 | "7 天后过期"这类逻辑没法等 |
| **随机数 / UUID** | ✅ 需要时 | 要可复现 |
| **你自己的数据库** | ❌ **不要** | 它是被测行为的一部分（见 4.2） |
| **你自己的 repository** | ❌ **不要** | mock 掉它，service 就只剩胶水了 |
| **你自己的 service** | ❌ **不要** | 同上 |
| **ORM / 框架** | ❌ **绝对不要** | 你会重新实现一遍它的行为，然后测你的实现 |

**一句话总判据**：

> **mock 是用来切断"你控制不了的东西"的，不是用来切断"你要测的东西"的。**
>
> 每加一个 mock，问一句：**这个东西不受我控制吗？慢吗？有副作用吗？** 三个都不是，就不要 mock。

### 4.2 为什么数据库不能 mock

回到解剖台演示一，再补一刀：

```python
# mock 掉数据库，下面这些你全部测不到
```

| 你想验证的 | mock 后能测吗 |
|---|---|
| `UNIQUE` 约束真的挡住重复标题了吗 | ❌ |
| `CHECK` 约束真的拒绝了非法 status 吗 | ❌ |
| `ON DELETE CASCADE` 真的级联了吗 | ❌ |
| `server_default` 真的填了默认值吗 | ❌ |
| 那条 SQL 真的能跑吗（语法对吗） | ❌ |
| 迁移脚本和模型一致吗 | ❌ |
| `LEFT JOIN` 后 `count(a.id)` 返回 0 而不是 1 吗 | ❌ |

> 第 6 次课花了 20 分钟讲"约束下推到数据库的价值"，第 7 次课花了 14 分钟讲迁移的危险。
>
> **把数据库 mock 掉，那两节课的全部内容都不在测试范围内。**
>
> 判据：**你的护栏在哪一层，测试就要能穿透到哪一层。** 护栏在数据库，测试就必须真的打到数据库。

### 4.3 该 mock 的那些，怎么 mock

```python
# app/deps.py —— 外部服务也走依赖注入
def get_mailer() -> Mailer:
    return SmtpMailer(settings.smtp_url)

# tests/conftest.py
class FakeMailer:
    def __init__(self): self.sent = []
    def send(self, to, subject, body): self.sent.append((to, subject, body))

@pytest.fixture
def mailer(client):
    fake = FakeMailer()
    app.dependency_overrides[get_mailer] = lambda: fake
    yield fake
    app.dependency_overrides.pop(get_mailer)


def test_answer_notifies_question_author(client, mailer, question_factory):
    q = question_factory()
    client.post(f"/questions/{q.id}/answers", json={"body": "这是我的回答内容"})
    assert len(mailer.sent) == 1
    assert mailer.sent[0][0] == q.author.email
```

**两个要点**：

> **一、用"假实现"（fake）优于用 `MagicMock`。**
>
> | | `MagicMock` | 手写的 Fake |
> |---|---|---|
> | 方法名写错 | **静默通过**（mock 有任意属性） | AttributeError |
> | 参数签名变了 | 静默通过 | 报错 |
> | 能检查"发了什么" | 要写 `assert_called_with` | 直接看 `fake.sent` |
>
> `MagicMock` 最危险的性质：**你访问它任何属性都不会报错**。所以你把 `mailer.send` 打错成 `mailer.sned`，测试照样绿。
>
> **二、外部服务也要走依赖注入。** 这是 3.5 那条判据的直接应用——**能被 override 的前提是它是一个依赖。**
>
> 如果代码里是 `smtplib.SMTP(...)` 直接 new 出来的，你就只能 monkeypatch，那是打补丁，不是设计。

### 4.4 时间和随机数

```python
# 不要这样：业务代码里直接 datetime.now()
def is_expired(token):
    return token.expires_at < datetime.now(UTC)      # ← 测试没法控制

# 这样：时间作为参数或依赖
def is_expired(token, now: datetime):
    return token.expires_at < now
```

> 判据：**把"不确定性"推到边界上。** 纯函数接受时间作为参数，只有最外层的端点去取当前时间。
>
> 这样内层逻辑变成纯函数，**用单元测试就能测，不需要任何 mock**——这才是单元测试该存在的地方（回收 3.1）。
>
> 〔`freezegun` / `time-machine` 可以冻结时间，适合改造成本高的老代码。**新代码优先用参数化。** C 档卡。〕

### 材料

- **封面级素材**：4.1 的八行 mock 判据表。
- **高光图**：4.2 的"mock 掉数据库就测不到的七件事"。
- 高光图：`MagicMock` vs 手写 Fake 三行对照。
- 截图：`mailer.sned`（拼错）在 MagicMock 下通过、在 Fake 下报错。

---

## 五、现场必做：把纪律变成会红的检查

**约 20 分钟。本次课最高光，绝对不能压缩。**

### 5.0 本单元的方法论（**先讲，再做**）

**醒目页**：

> **每一条检查，走两步：**
>
> **第一步：写出来，故意违反一次，看它变红。** ← 这一步不能省
> **第二步：修复，看它变绿。**
>
> **只有红过的检查，才算存在。**
>
> 因为一条写错的检查（比如 grep 的路径打错了、断言永远为真）看起来和一条正确的检查**完全一样**——都是绿色的对勾。

### 5.1 检查一：每个端点必须有 `response_model`（第 3 次课的纪律）

**这一条要放第一个，因为它是本次课最漂亮的一个回收。**

先提问：

> 第 3 次课我们做过一件事：打印 `app.routes`，看清"装饰器没有魔法，它只是往一个列表里塞了一条记录"。
>
> **那个列表现在还在。我们能不能用它来做检查？**

```python
# tests/test_conventions.py
from fastapi.routing import APIRoute
from app.main import app

def test_every_endpoint_declares_response_model():
    missing = [
        f"{list(r.methods)[0]} {r.path}"
        for r in app.routes
        if isinstance(r, APIRoute)
        and r.response_model is None
        and r.path not in {"/healthz", "/metrics"}      # 白名单，要有理由
    ]
    assert missing == [], f"这些端点缺少 response_model：{missing}"
```

**第一步：让它红。** 随便找一个端点，把 `response_model=` 删掉：

```bash
pytest tests/test_conventions.py -q
```

```
AssertionError: 这些端点缺少 response_model：['GET /questions/{qid}/answers']
assert [...] == []
```

**第二步：加回去，绿。**

**然后停下来，讲透这个回收（醒目页）**：

> **第 3 次课我们打印 `app.routes`，目的是"破除魔法"——让你知道框架里没有不可理解的东西。**
>
> **今天，同一个数据结构变成了自动检查的输入。**
>
> 这两件事之间有一条因果链：
>
> **可检视 → 可检查 → 可防止**
>
> 一个你能打印出来的东西，你就能对它写断言；能写断言，就能让它在违反时变红。
>
> 反过来：**一个你无法检视的框架内部状态，你就无法对它建立任何保证。**
>
> 判据：**选框架时问一句"它的关键状态能不能被读出来"。** 能读出来的框架，你可以给它加护栏；读不出来的，你只能相信文档。
>
> 顺带：这条检查还白送了一件事——**第 3 次课那个"返回裸 dict 泄漏 password_hash"的事故，从此不可能再发生。** 因为没有 `response_model` 的端点根本过不了 CI。

### 5.2 检查二：`.commit()` 只在 `deps.py`（第 7 次课的纪律）

```python
# tests/test_conventions.py
import subprocess

def test_commit_only_in_deps():
    out = subprocess.run(
        ["grep", "-rn", r"\.commit()", "app/routers", "app/services"],
        capture_output=True, text=True).stdout
    assert out == "", f"routers/services 里不允许 commit：\n{out}"
```

**第一步：让它红。** 在某个 service 里加一行 `session.commit()`：

```
AssertionError: routers/services 里不允许 commit：
app/services/question.py:41:    session.commit()
```

**第二步：删掉，绿。**

**要讲的点**：

> 注意失败信息里**带了文件名和行号**。这很重要：
>
> **判据：一条检查失败时，必须让人一眼看出"哪里违反了、怎么改"。**
>
> 对比一个坏的写法：
> ```python
> assert "commit" not in code      # 失败信息：assert False
> ```
> 这条检查是对的，但它红了之后你要花十分钟找原因。**CI 的红色如果需要调查，人就会开始忽略它。**

**一个诚实的边界要说明**：

> grep 是**文本匹配**，它有假阳性和假阴性：
>
> - 注释里写了 `.commit()` → 假阳性
> - 写成 `getattr(session, "commit")()` → 假阴性
>
> 更严谨的做法是解析 AST。**但对本课程，grep 的性价比更高**：它一行就能写完，覆盖了 99% 的真实情况。
>
> 判据：**检查的严谨程度要配得上问题的严重程度。** 不要为了堵住一个没人会写的绕路写法，把检查复杂化到没人维护。

### 5.3 检查三：列表端点的 SQL 条数 ≤ 3（第 7 次课的纪律）

**把第 7 次课写的 `sqlcount.py` 直接拿来用。**

```python
# tests/test_performance_guards.py
from app.sqlcount import count_sql
from app.db import engine

def test_list_questions_sql_count(client, seeded_questions):
    with count_sql(engine) as s:
        res = client.get("/questions?size=20")
    assert res.status_code == 200
    assert s["n"] <= 3, f"SQL 条数 {s['n']} 超标：\n" + "\n".join(s["sql"])


def test_list_questions_sql_count_is_independent_of_size(client, seeded_questions):
    with count_sql(engine) as a:
        client.get("/questions?size=5")
    with count_sql(engine) as b:
        client.get("/questions?size=50")
    assert a["n"] == b["n"], (
        f"SQL 条数随页面大小变化（{a['n']} → {b['n']}），说明存在 N+1")
```

**第一步：让它红。** 把查询里的 `selectinload(Question.author)` 删掉：

```
AssertionError: SQL 条数随页面大小变化（3 → 3）...
```

等等——**第一次可能不红**，因为 `raiseload("*")`（第 7 次课第五道护栏）会先抛异常。**这正好说明护栏在工作**，顺手演示一下：

```
sqlalchemy.exc.InvalidRequestError: 'Question.author' is not available due to lazy='raise'
```

> 两道保护叠在一起：`raiseload` 在**运行时**立刻炸，SQL 计数断言在**测试时**兜底。
>
> 然后把 `raiseload` 也去掉，这次断言红了：
>
> ```
> AssertionError: SQL 条数随页面大小变化（6 → 51），说明存在 N+1
> ```

**第二步：加回去，绿。**

**要讲的点（醒目页）**：

> **第二条测试比第一条好，因为它测的是"性质"而不是"数字"。**
>
> | | 断言 `n <= 3` | 断言 `n 不随 size 变化` |
> |---|---|---|
> | 加一个新的 eager load | **误红**，要改阈值 | 不受影响 |
> | 出现 N+1 | 红 | **红** |
> | 表达的意思 | "现在是 3 条" | **"查询次数与数据量无关"** |
>
> 第二条抓住了 N+1 的**本质定义**：查询次数随结果条数增长。
>
> **判据：能断言性质就不要断言具体数值。** 数值会随着正常演进变化，性质不会。
>
> 这是"性能测试"最实用的形态：**不测耗时（机器不同数字就不同、会抖动），测次数和复杂度的增长关系。**

### 5.4 检查四：`api.d.ts` 与后端契约一致（第 8 次课的纪律）

这一条不是 pytest，是 shell：

```bash
# scripts/check_contract.sh
set -e
python scripts/dump_openapi.py > /tmp/openapi.json       # 不用起服务器
cd web
npx openapi-typescript /tmp/openapi.json -o src/api.d.ts
git diff --exit-code src/api.d.ts
```

```python
# scripts/dump_openapi.py —— 离线导出，CI 里不用起服务
import json
from app.main import app
print(json.dumps(app.openapi(), ensure_ascii=False, indent=2))
```

**第一步：让它红。** 改一个 schema 字段名，不重新生成：

```
diff --git a/web/src/api.d.ts b/web/src/api.d.ts
-    answer_count: number;
+    reply_count: number;
error: 前端类型与后端契约不一致，请运行 npm run gen 并提交
```

**第二步：`npm run gen`，提交，绿。**

**要讲的点**：

> 第 8 次课我说"后端改了 schema，第一件事是 `npm run gen`"，然后自己吐槽"这靠人记得"。
>
> **现在它不靠人记得了。** 忘了生成，CI 直接红，而且红的信息里就写了怎么修。
>
> 注意 `dump_openapi.py` 这个小脚本：**它让 CI 不需要启动服务器就能拿到契约。** 因为 `app.openapi()` 就是一个普通的方法调用，返回一个 dict。
>
> **又一次：框架没有魔法。** 第 3 次课是 `app.routes`，今天是 `app.openapi()` 和 `app.dependency_overrides`——**三个都是普通的 Python 对象，三个都变成了工具。**

### 5.5 阶段小结：第七道结构性护栏

**封面级素材，累加表，请加一列"拦截时机"**：

| 次课 | 护栏 | 拦住什么 | **拦截时机** |
|---|---|---|---|
| 第 3 次课 | `response_model` | 字段泄漏 | 运行时 |
| 第 4 次课 | 全局异常处理器 | 内部信息泄漏 | 运行时 |
| 第 5 次课 | Jinja2 自动转义 | 输入变 HTML | 运行时 |
| 第 6 次课 | 数据库约束 | 脏数据写入 | 运行时 |
| 第 7 次课 | `lazy="raise"` | 静默 N+1 | 运行时 |
| 第 8 次课 | 生成的类型 | 字段名写错 | **编译期** |
| **第 9 次课** | **CI 检查** | **违反任何一条约定** | **合并前** |

> 时机在不断往前移：**运行时 → 编译期 → 合并前。**
>
> 第七道和前六道有一个本质区别：
>
> **前六道各自只管一类问题。第七道是一个容器——任何你能写成断言的规则，都能装进去。**
>
> 这就是为什么今天这节课是"把纪律变成结构"这条主线的收口：**从今天起，每当你在代码评审里说出一句"我们约定了不要这样写"，下一步就应该是"那把它写成检查"。**

### 5.6 判据：什么该变成检查，什么不该

**必须给这个，否则学生会无限堆检查**：

| 特征 | 该不该变成检查 |
|---|---|
| **违反过至少一次**（真实踩过坑） | ✅ 优先 |
| 违反的后果严重且不可逆 | ✅ |
| 能用一行 grep / 一条断言表达 | ✅ |
| 误报率低 | ✅ |
| 只是"风格偏好"（命名、引号） | ❌ 交给 formatter，不要自己写 |
| 要判断"意图"才能定对错 | ❌ 写不准，交给 code review |
| 误报多到需要一堆 `# noqa` | ❌ **会训练人忽略红色** |

> 最后一行是最重要的：
>
> **判据：CI 里每多一条误报的检查，人对红色的信任就少一分。**
>
> 一个经常误报的 CI，最终的结果是团队养成"红了就 re-run，再红就 skip"的习惯。**那时候你所有的检查都失效了，包括对的那些。**
>
> 所以：**宁可少几条检查，也不要有一条会误报的检查。**

### 5.7 剩余纪律的检查方案（**只给表，不现场做，留作业**）

| # | 纪律 | 检查怎么写 | 归属 |
|---|---|---|---|
| 2 | Out schema 不含敏感字段 | 遍历 `app.routes` 的 `response_model`，检查字段名不在黑名单（`password*`、`*_hash`、`token`、`secret`） | pytest |
| 3 | `services/` 不 `import fastapi` | `grep -rn "import fastapi\|from fastapi" app/services app/repositories` | shell |
| 4 | 错误响应体结构统一 | 参数化测试：对 5 类错误各打一次，断言四个键都在 | pytest |
| 5 | `async def` 里没有阻塞调用 | AST：遍历 `AsyncFunctionDef`，查子节点里有没有 `requests.`/`time.sleep`/同步 session 调用 | pytest（AST） |
| 6 | 模板里没有 `\| safe` | `grep -rn "| safe" app/templates` | shell |
| 7 | 所有表有主键、所有外键有索引 | 查 `pg_catalog`（第 6 次课那两条元数据 SQL 直接搬过来） | pytest |
| 9 | 迁移能 upgrade 也能 downgrade | CI step：`upgrade head` → `downgrade -1` → `upgrade head` | CI |
| 12 | `tsc --noEmit` 零错误 | CI step | CI |
| 13 | 前端不用 `innerHTML` 接用户数据 | `grep -rn "innerHTML" web/src`，白名单需注释说明 | shell |

**第 5 条和第 7 条各说一句**：

> **第 5 条要用 AST，不能用 grep。** 因为 `time.sleep` 出现在一个 `def` 里是合法的，出现在 `async def` 里才是问题——**grep 看不到嵌套关系，AST 能。**
>
> 判据：**需要上下文才能判断对错的规则，grep 做不了，要用 AST。** 但先用 grep 试一次，如果误报能接受就别上 AST。
>
> **第 7 条很特别：它检查的不是代码，是数据库的实际状态。** 第 6 次课我们写过两条查 `pg_catalog` 的 SQL 找"没索引的外键"和"没主键的表"，当时是手工跑的。今天把它们变成 pytest——**在测试库（由迁移建出来的）上跑，所以它实际在检查迁移的产物。**
>
> 这说明"检查"的对象可以比代码更宽：**代码、契约、数据库结构、构建产物，全都能检查。**

### 材料

- `tests/test_conventions.py`：四条现场检查 + 5.7 表里的其余若干条（作业参考实现另存 `solutions/`）。
- `tests/test_performance_guards.py`：SQL 计数断言两条。
- `scripts/dump_openapi.py`、`scripts/check_contract.sh`。
- **封面级素材**：单元 5.0 的"红-绿两步"方法论页。
- **封面级素材**：5.1 的"可检视 → 可检查 → 可防止"因果链页，并列出三个普通 Python 对象（`app.routes` / `app.openapi()` / `app.dependency_overrides`）。
- **封面级素材**：5.5 的七道护栏累加表（新增"拦截时机"列，第 7 行"合并前"高亮）。
- **高光图**：5.3 的"断言数值 vs 断言性质"三行对照表。
- **高光图**：5.6 的"什么该变成检查"七行判据表，最后一行标红。
- 截图（**每条检查两张，红 + 绿，共八张**）：这是本单元最重要的素材，必须完整。
- 截图：删掉 `selectinload` 后先撞 `raiseload` 报错，再删 `raiseload` 后 SQL 计数断言变红（**两级保护的叠加效果**）。

---

## 六、覆盖率的真相

**约 7 分钟。**

### 6.1 先量一次

```bash
pytest --cov=app --cov-report=term-missing -q
```

```
---------- coverage: platform linux, python 3.12 ----------
Name                              Stmts   Miss  Cover   Missing
-----------------------------------------------------------------
app/routers/questions.py             48      3    94%   67, 81-82
app/services/question.py             36      2    94%   44, 52
app/repositories/question.py         41      5    88%   58-62
-----------------------------------------------------------------
TOTAL                               312     24    92%
```

> 92%。看起来很好。**现在做一个实验。**

### 6.2 40 秒实验：删掉所有断言（**必须现场做**）

```bash
# 把所有 assert 行注释掉
sed -i 's/^\( *\)assert /\1# assert /' tests/*.py
pytest --cov=app -q
```

```
23 passed in 1.84s
TOTAL   312   24   92%          ← 一点没变
```

**停下来，让这个数字停留。**

> **我删掉了所有断言。覆盖率一点没变，测试全部通过。**
>
> 原因很简单，说出来大家都懂，但很少有人真的想过：
>
> **覆盖率测量的是"哪些行被执行过"，不是"哪些行被验证过"。**

**醒目页**：

> | 覆盖率能告诉你 | 覆盖率不能告诉你 |
> |---|---|
> | 哪些代码**从没跑过** | 跑过的代码**结果对不对** |
> | 哪些分支**从没进过** | 断言**有没有意义** |
> | —— | 边界值**测了没有** |
> | —— | 失败路径**处理对不对** |
>
> **判据：覆盖率是"下界"，不是"评分"。**
>
> 覆盖率 30% 一定不够，这个信息有用。
> 覆盖率 92% 不说明任何事——它和解剖台那套假测试的覆盖率是同一个数字。

### 6.3 怎么才知道测试真的有效：变异的思路

> 那怎么知道测试有没有用？
>
> **解剖台演示一已经给了答案：把被测代码改坏，看测试会不会红。**
>
> 这个思路有个正式名字：**变异测试（mutation testing）**。工具自动把你的代码改坏（`>` 改成 `>=`、`+` 改成 `-`、删掉一行），然后跑测试。
>
> - 测试红了 → 这个变异被"杀死"了，说明测试有效
> - 测试还是绿的 → 变异"存活"，**说明这行代码没有被真正验证**
>
> 变异测试跑起来很慢（每个变异都要跑一遍全套测试），**本课程不要求上工具**。但那个手工版本你必须会：

**醒目页**：

> **自检三问，写完一个测试就问一遍：**
>
> 1. **如果我把被测函数的实现删空，这个测试会红吗？**（→ 排除 mock 滥用）
> 2. **如果我把一个 `>` 改成 `>=`，会红吗？**（→ 排除边界没测）
> 3. **如果我把某个 `if` 分支删掉，会红吗？**（→ 排除分支没测）
>
> 三个都答不出"会"，这个测试就是装饰品。

**现场做一次第 2 问**：

```python
# app/services/question.py
- if len(title.strip()) < 5:
+ if len(title.strip()) < 4:        # ← 改坏边界
```

```bash
pytest -q
# 23 passed              ← 没红！边界没测
```

> 补一个边界测试：

```python
@pytest.mark.parametrize("title,expect", [
    ("四个字标", 201),        # 刚好 5 个字 → 应该通过
    ("四个字", 422),          # 4 个字 → 应该拒绝
])
def test_title_length_boundary(client, title, expect):
    res = client.post("/questions", json={"title": title, "body": "正文够长了的内容"})
    assert res.status_code == expect
```

再把边界改坏，这次红了。

> **判据：每个数值边界、每个分支，至少要有一个测试踩在它的两侧。**
>
> 这也回答了一个常见问题："测试要写多少？"
>
> **答案不是"覆盖率到 80%"，是"每个判断的两侧都有测试"。**

### 6.4 覆盖率的正确用法

| 用法 | 评价 |
|---|---|
| 当作 KPI，要求 ≥ 80% | ❌ **会催生假测试**——最快提升覆盖率的方法就是写空断言测试 |
| 看 `Missing` 列，找"完全没测过的代码" | ✅ 这是它真正的价值 |
| 设一条**不允许下降**的基线 | ✅ 便宜且有效 |
| 对新增代码要求覆盖 | ✅ 比全局阈值合理 |

> 判据：**覆盖率用来找"我忘了测什么"，不用来证明"我测得好"。**
>
> 我们的 CI 只做一件事：**覆盖率不许比上次低。** 不设绝对数字。

### 材料

- **封面级素材**：6.2 的删断言实验前后对比（两个终端输出并排，`92%` 两处都圈红）。
- **封面级素材**：6.3 的"自检三问"。
- 高光图：6.1 的"覆盖率能/不能告诉你"两列表。
- 高光图：6.4 的四行用法表。
- 截图：边界改坏后"23 passed"、补测试后变红。

---

## 七、契约测试与端到端：把第 8 次课的两笔账还上

**约 9 分钟。若时间紧，7.4 只给结论。**

### 7.1 契约测试：后端真的守约了吗

> 第 8 次课我们做到了"前端按契约写代码"。但还有一半没验证：
>
> **后端返回的东西，真的符合它自己声明的契约吗？**
>
> `response_model` 能保证吗？**大部分能，但有两个口子：**

| 口子 | 例子 |
|---|---|
| 错误响应不走 `response_model` | 404 的响应体结构没人校验 |
| `response_model` 声明了但类型不严 | `detail: dict` 可以是任何东西 |

用 schemathesis 按契约自动生成请求：

```python
# tests/test_contract.py
import schemathesis
from app.main import app

schema = schemathesis.from_asgi("/openapi.json", app)

@schema.parametrize()
@settings(max_examples=30, deadline=None)
def test_api_conforms_to_contract(case, session):
    app.dependency_overrides[get_session] = lambda: session
    response = case.call_asgi()
    case.validate_response(response)        # ← 校验响应符合契约
```

跑一次，看它报什么：

```
FAILED test_api_conforms_to_contract[GET /questions/{qid}]
  - Undocumented HTTP status code
    Received: 500
    Documented: 200, 404
  Falsifying example: qid = -1
```

> **它自动发现了一个我们没写过的用例：`qid = -1`。**
>
> 我们的路径参数写的是 `qid: int`，没写 `gt=0`。传 `-1` 进去，查库返回空，但某处代码在处理这个情况时抛了别的异常 → 500。
>
> **而 500 不在我们声明的响应码里——契约被违反了。**
>
> 两个收获：
>
> 1. **修法**：`qid: int = Path(gt=0)`。回收第 3 次课的"入口闸门"——**约束越靠前，后面越简单。**
> 2. **方法论**：契约测试的价值是它**按契约穷举**，会去试你不会想到的输入。这是"定量兜底"那一层（第 5 次课起的三层护栏方法）的又一个实例。
>
> 判据：**手写测试覆盖你想到的情况，契约测试/属性测试覆盖你想不到的情况。** 两者不互相替代。

〔属性测试（hypothesis）的完整用法是 C 档卡。**最有价值的一条：对"解析-序列化"这类往返操作，断言 `parse(dump(x)) == x`**，一条测试顶一百个用例。〕

### 7.2 一个更便宜的契约检查

> schemathesis 有学习成本，如果不想上，有一个五行的替代品：

```python
def test_all_error_responses_match_contract(client):
    cases = [
        ("GET",  "/questions/999999", None, 404),
        ("POST", "/questions", {"title": "短"}, 422),
        ("GET",  "/questions?sort=bogus", None, 422),
    ]
    for method, url, body, expect in cases:
        res = client.request(method, url, json=body)
        assert res.status_code == expect
        ErrorBody.model_validate(res.json())        # ← 用后端自己的 schema 校验
```

> **用 Pydantic 模型校验响应体**，一行搞定"结构统一"这条纪律（第 4 次课第 4 条）。
>
> 这就是 5.7 表里第 4 条的实现。

### 7.3 前端检查：`tsc` 与契约一致性

第 8 次课欠的两条，一行 CI 就还上了：

```yaml
- run: npm ci && npm run check          # tsc --noEmit
- run: bash scripts/check_contract.sh   # gen + git diff --exit-code
```

### 7.4 端到端测试：少而关键

```python
# e2e/test_smoke.py —— Playwright
def test_create_and_view_question(page, live_server):
    page.goto(f"{live_server}/new.html")
    page.fill("[name=title]", "端到端测试创建的问题")
    page.fill("[name=body]", "这是端到端测试写入的正文内容")
    page.click("button[type=submit]")

    page.wait_for_url("**/detail.html?id=*")
    assert page.text_content("h1") == "端到端测试创建的问题"


def test_list_page_request_count(page, live_server):
    reqs = []
    page.on("request", lambda r: reqs.append(r.url))
    page.goto(f"{live_server}/")
    page.wait_for_selector("li")
    api_calls = [u for u in reqs if "/api/" in u]
    assert len(api_calls) <= 2, f"列表页发了 {len(api_calls)} 个 API 请求：{api_calls}"
```

> **第二个测试就是第 8 次课那条纪律（列表页请求数 ≤ 2）。** 前端 N+1 从此会红。
>
> **端到端测试的判据（醒目页）**：
>
> | 该写 | 不该写 |
> |---|---|
> | 最关键的 2–5 条主流程 | 每一个按钮、每一个字段 |
> | "能不能走通" | 具体文案、具体样式 |
> | 跨层的集成点 | 业务规则的各种分支 |
>
> 理由：**端到端测试最贵也最脆**。一次 UI 调整能红掉二十条。所以它只负责"整条链没断"，细节交给集成测试。
>
> 判据：**端到端测试的数量，应该少到你能手工重跑它们。** 超过这个数量，维护成本会超过它的价值。

### 材料

- `tests/test_contract.py`、`tests/test_error_contract.py`。
- `e2e/test_smoke.py` + Playwright 配置。
- 截图：schemathesis 报出 `qid = -1` 导致 500 的完整输出（**这是本单元最有说服力的素材**）。
- 高光图：7.4 的端到端"该写/不该写"对照表。

---

## 八、CI：让检查在合并前发生

**约 10 分钟。**

### 8.1 先讲清 CI 到底是什么

**醒目页**：

> **CI 不是一个工具，是一句承诺：**
>
> **"任何代码在合并进主干之前，必须通过这一组检查。"**
>
> 工具（GitHub Actions / GitLab CI / Jenkins）只是执行它。真正起作用的是两件事：
>
> 1. **检查是自动跑的**（不靠人记得）
> 2. **不通过就不能合并**（不靠人自律）
>
> **第 2 条比第 1 条重要。** 一个跑了但可以忽略的 CI，等于没有 CI。

### 8.2 最小可用的 CI

```yaml
# .github/workflows/ci.yml
name: ci
on: [push, pull_request]

jobs:
  backend:
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgres:16
        env: {POSTGRES_PASSWORD: postgres, POSTGRES_DB: app_test}
        options: >-
          --health-cmd pg_isready --health-interval 5s --health-retries 10
        ports: ["5432:5432"]
    env:
      TEST_DATABASE_URL: postgresql+psycopg://postgres:postgres@localhost:5432/app_test
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: {python-version: "3.12", cache: pip}
      - run: pip install -r requirements.txt -r requirements-dev.txt

      # ① 静态检查：最快，先跑
      - run: ruff check app tests
      - run: ruff format --check app tests
      - run: mypy app

      # ② 约定检查：单元 5 那四条
      - run: pytest tests/test_conventions.py -q

      # ③ 迁移检查：第 7 次课的纪律
      - run: alembic upgrade head
      - run: alembic check                     # 模型与迁移是否一致
      - run: alembic downgrade -1 && alembic upgrade head

      # ④ 测试
      - run: pytest -q --cov=app --cov-report=xml
      - run: python scripts/check_coverage_not_dropped.py

  frontend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with: {node-version: "20", cache: npm, cache-dependency-path: web/package-lock.json}
      - run: cd web && npm ci
      - run: cd web && npm run check           # tsc --noEmit
      - run: bash scripts/check_contract.sh    # 契约一致性
```

**四个设计要点**：

> **一、顺序按"快且常红"排。**
>
> `ruff` 跑 2 秒，`pytest` 跑 40 秒。**把快的放前面**，格式错误 2 秒就告诉你，不用等 1 分钟。
>
> 判据：**CI 的步骤顺序 = 反馈速度优先。**
>
> **二、`alembic check` 是白送的一条护栏。**
>
> 它比对"模型"和"迁移链的终点"，不一致就失败。**这堵住了一个非常常见的错误：改了模型忘了生成迁移。**
>
> **三、`downgrade -1 && upgrade head` 就是第 7 次课那条纪律。**
>
> 注意它只回滚一步——回滚全部太慢。**一步足够抓住"downgrade 写错了"这类问题。**
>
> 〔第 7 次课还有一条更强的要求："在带数据的快照上跑迁移"。CI 里要做需要准备一份 dump 文件，**作业里要求你加上它**。〕
>
> **四、前后端分两个 job，可以并行。**

### 8.3 本地也要能跑同一套

```makefile
# Makefile
check: lint type conventions test          ## 提交前跑这个

lint:
	ruff check app tests && ruff format --check app tests
type:
	mypy app
conventions:
	pytest tests/test_conventions.py -q
test:
	pytest -q
e2e:
	pytest e2e/ -q
```

```yaml
# .pre-commit-config.yaml —— 只放极快的
repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    hooks: [{id: ruff, args: [--fix]}, {id: ruff-format}]
```

> **判据：CI 里的每一条检查，本地必须能用一条命令跑。**
>
> 如果只有 CI 能跑，开发者的循环就变成"推上去等三分钟看红不红"，**一天推十次**。
>
> **pre-commit 只放秒级的东西。** 把 pytest 放进 pre-commit，人的第一反应是 `git commit --no-verify`——**又一次训练人绕过检查。**
>
> 三层的分工：
>
> | 层 | 放什么 | 耗时上限 |
> |---|---|---|
> | pre-commit | 格式化、lint --fix | **2 秒** |
> | `make check`（本地手动） | + 类型检查、约定检查、单元+集成测试 | **1 分钟** |
> | CI | + 迁移检查、前端、契约、e2e | 5 分钟 |

### 8.4 测试跑得慢怎么办

| 手段 | 效果 | 代价 |
|---|---|---|
| 单元 3.4 的事务回滚隔离 | **~100 倍** | 已经做了 |
| `pytest -n auto`（xdist 并行） | 4 核 ≈ 3 倍 | **要求测试真的独立**（→ 3.4 的回报） |
| session 级 fixture 共享贵资源 | 显著 | 要小心别共享可变状态 |
| 标记慢测试，PR 只跑快的，夜间跑全套 | 显著 | **有漏网风险** |

> 注意第 2 行：**并行加速的前提是测试独立**。解剖台演示二那套测试永远没法并行。
>
> **判据：测试慢的时候，先查隔离方式，再考虑并行。** 大部分"测试慢"的真实原因是每个测试都在重建数据库。

### 8.5 CI 之外：两条必须说的纪律

> **一、分支保护要打开。**
>
> 在仓库设置里勾上"required status checks"。**没打开的话，CI 只是一个装饰性的对勾。**
>
> 这是本次课最短也最重要的一句操作指导。
>
> **二、CI 红了必须立刻修。**
>
> 主干红着不管，一天之后就没人知道是谁的锅了，两天之后大家开始习惯红色。
>
> 判据：**主干的 CI 是一个二值信号。它只能是绿的。**

### 材料

- `.github/workflows/ci.yml`（完整）、`Makefile`、`.pre-commit-config.yaml`。
- `scripts/check_coverage_not_dropped.py`。
- **封面级素材**：8.1 的"CI 是一句承诺"。
- **高光图**：8.3 的三层分工表（pre-commit / make check / CI，含耗时上限）。
- 截图：GitHub PR 页面上，一条检查红着、合并按钮被禁用（**这张图最能说明"结构性"是什么意思**）。
- 截图：CI 全绿的步骤列表（含耗时，证明总时长可接受）。

---

## 九、C 档结论卡

**约 3 分钟。时间不够整体跳过。**

### 9.1 一句话结论卡

| 问题 | 结论 | 展开处 |
|---|---|---|
| 属性测试（hypothesis） | 最有价值的一条：往返断言 `parse(dump(x)) == x` | 单元 7.1 |
| 变异测试工具（mutmut / cosmic-ray） | 很慢，本课程不上；**手工版"自检三问"够用** | 单元 6.3 |
| 快照测试 | 适合复杂输出（渲染结果、报表）；**缺点是没人真的读 diff** | 自读 |
| `freezegun` / `time-machine` | 冻结时间。**新代码优先把时间作为参数传入** | 单元 4.4 |
| `factory_boy` / `polyfactory` | factory 库。手写 fixture 到 20 个以上再考虑 | 单元 3.6 |
| 测试容器（testcontainers） | 让测试自己起 Postgres 容器，不依赖外部环境 | 自读 |
| 并行测试的数据库隔离 | 每个 worker 一个 schema 或一个库（`pytest-xdist` + `worker_id`） | 单元 8.4 |
| 测试里断言日志 | `caplog`。**适合验证"出错时有没有记下 request_id"** | 自读 |
| 负载测试 / 压测 | locust / k6。**它不属于 CI**，属于发布前的容量验证 | **第 16 次课** |
| 性能基线与回归 | 把 SQL 条数、请求数写成断言（今天做了）；耗时基线要专门的环境 | **第 11 次课** |
| flaky 测试怎么办 | **先查共享状态和时间依赖，不要加 retry**。retry 是把问题藏起来 | 单元 3.4 |
| 测试代码要不要审、要不要 lint | **要**。测试代码和生产代码同等对待 | — |

### 9.2 测试栈跨语言对照

| 能力 | Python | JS/TS | Java | Go |
|---|---|---|---|---|
| 测试框架 | pytest | vitest / jest | JUnit 5 | 内建 `testing` |
| fixture / 依赖注入 | fixture | `beforeEach` | `@BeforeEach` + DI | 手写 helper |
| HTTP 测试客户端 | `TestClient` | supertest | `MockMvc` / `WebTestClient` | `httptest` |
| 测试替身 | `unittest.mock` | `vi.mock` | Mockito | 接口 + 手写 fake |
| 覆盖率 | `coverage.py` | c8 / istanbul | JaCoCo | `go test -cover` |
| 契约测试 | schemathesis | pact / msw | Spring Cloud Contract / pact | pact |
| 属性测试 | hypothesis | fast-check | jqwik | `testing/quick` |
| 端到端 | Playwright | Playwright / Cypress | Selenium | Playwright(go) |
| 容器化依赖 | testcontainers | testcontainers | **testcontainers（起源）** | testcontainers |

> 两点值得注意：
>
> **一、Go 的社区文化明确反对 mock 框架**，提倡"定义小接口 + 手写 fake"。这和本课程单元 4.3 的判断一致——**手写 fake 在"方法名写错"这类问题上比 MagicMock 安全**。
>
> **二、`TestClient` 这类"不经过网络的 HTTP 测试客户端"是所有主流栈都有的能力。** 它是集成测试能跑得快的关键：**没有端口、没有 TCP、没有进程启动。**

---

## 十、作业与欠账

**约 6 分钟。**

### 10.1 作业一：重写测试套件（主线，必交）

**第一步：先给旧测试判罪。**

对 `v9-broken` 的 23 个测试逐个分类，交一张表：

| 测试名 | 属于哪类问题（替身滥用/不独立/脆弱/空断言/正常） | 依据 |
|---|---|---|

**第二步：重建基础设施。**

| # | 要求 | 自检命令 |
|---|---|---|
| 1 | 独立的 PostgreSQL 测试库，用 **Alembic 迁移**建表 | 看 `conftest.py` |
| 2 | 每个测试事务隔离，**跑完数据库无残留** | 连跑两次 `pytest`，结果一致 |
| 3 | `pytest -p randomly` 通过 | 随机顺序 |
| 4 | `pytest -n auto` 通过 | 并行 |
| 5 | 至少三个 factory（user / question / answer） | — |
| 6 | 数据库、repository、service **一律不 mock** | grep `MagicMock` |
| 7 | 外部服务（邮件）用手写 Fake + `dependency_overrides` | — |

**第三步：写测试。**

| # | 要求 |
|---|---|
| 8 | 每个端点至少：成功路径 1 条 + 失败路径 1 条 |
| 9 | 所有错误断言用 `code`，**零处断言 `message`** |
| 10 | 每个数值边界（标题长度、分页 size、status 枚举）两侧各一条 |
| 11 | 至少一条测试验证**数据库约束生效**（重复标题 → 409，非法 status → 拒绝） |
| 12 | 至少一条测试验证 `server_default` 生效 |

**第四步：自检三问（**评分重点**）。**

任选**三个**你写的测试，对每一个做单元 6.3 的三问实验，交表：

| 测试名 | 删空实现会红吗 | 改一个边界会红吗 | 删一个分支会红吗 | 不红的话你补了什么 |
|---|---|---|---|---|

### 10.2 作业二：把纪律变成检查（**本次课核心作业**）

从单元 5.7 的表里**选五条**（其中**必须包含第 5 条 async 阻塞检查和第 7 条数据库元数据检查**）实现出来。

每一条都要交**三样东西**：

| 交付项 | 说明 |
|---|---|
| ① 检查的实现 | 代码 |
| ② **违反时的红色截图** | 故意违反一次，截图失败输出 |
| ③ 修复后的绿色截图 | — |

**必答四问**：

1. 第 5 条为什么不能用 grep？**举一个 grep 会误判的具体例子。**
2. 第 7 条检查的对象是代码还是数据库？**它是在检查什么东西的正确性？**
3. 你选的五条里，哪一条的**误报风险**最高？你怎么降低它的？
4. 单元 5.6 说"宁可少几条检查，也不要有一条会误报的检查"。**你有没有想做但最后放弃的检查？为什么放弃？**

> 第 4 问不是凑数的。**能说出"我放弃了什么以及为什么"，比多交两条检查更说明你理解了判据。**

### 10.3 作业三：AI 测试对照实验（**课程主题作业**）

**第一部分：让 AI 给一个有 bug 的函数写测试（必做）。**

1. 先在 `app/services/question.py` 里**人为植入一个 bug**（建议：把分页的 `offset` 算成 `page * size` 而不是 `(page - 1) * size`，**这是极常见的差一错误**）。

2. 把这个**带 bug 的函数**原样发给 AI：

   > 给这个函数写 pytest 测试。

3. **原样保存输出**，然后回答：

   | 问题 | 你的回答 |
   |---|---|
   | AI 写的测试通过了吗？ | |
   | 它有没有发现这个 bug？ | |
   | 如果没有，它的断言是根据什么写出来的？ | |
   | **如果你把这套测试提交了，这个 bug 会怎样？** | |

4. **然后做第二轮**：不给它代码，只给它需求描述：

   > 分页接口：`page` 从 1 开始，`size` 默认 20。请写 pytest 测试，覆盖第一页、第二页、边界情况。

   对比两轮的输出，回答：

   | 问题 | 你的回答 |
   |---|---|
   | 第二轮的测试能抓住那个 bug 吗？ | |
   | 两轮的区别说明了什么？ | |

**第二部分：必答三问（评分重点）。**

| 问题 | 你的回答 |
|---|---|
| **为什么"给 AI 看代码让它写测试"会把 bug 一起固化？** 用你的实验数据说明 | |
| 对照第 8 次课的结论（"给 AI 契约比给描述好"）——**为什么写测试这件事上结论反过来了？** | |
| 据此给一条"让 AI 写测试"的操作规则。这条规则要具体到能写进团队文档 | |

> **第二问是本次作业的核心。** 提示一个思路：第 8 次课要的是"**实现**符合契约"，今天要的是"**验证**契约被满足"。
>
> 给 AI 看实现，它会把实现当成规格——**于是测试变成了实现的镜子，而镜子照不出实现自己的错。**
>
> 这条判断可以更一般地说：**测试的规格来源必须独立于被测实现。** 这条纪律对人一样成立——你自己写完代码马上写测试，也会掉进同一个坑。

### 10.4 本次课新增的欠账登记

| 欠账 | 何时还 |
|---|---|
| CI 里在"带数据快照"上跑迁移 | **作业二加分项** |
| 耗时类性能基线与回归检测 | **第 11 次课** |
| 缓存引入后的测试策略（缓存要不要 mock） | **第 11 次课** |
| 认证相关的测试（伪造当前用户） | **第 14 次课**（`dependency_overrides` 直接复用） |
| 安全测试（注入/XSS 的自动化验证） | **第 15 次课** |
| 压测与容量验证 | **第 16 次课** |
| CI 到 CD：自动部署 | **第 16 次课** |
| 并行测试的库隔离（每 worker 一个 schema） | 课后自读 |
| 测试容器（testcontainers） | 课后自读 |
| 变异测试工具 | 课后自读 |
| 快照测试 | 课后自读 |

---

## 十一、素材清单与制作说明

### 必需素材

| 素材 | 说明 |
|---|---|
| tag `v9-broken` | 起始版：AI 产出的 23 个测试，**92% 覆盖率、全绿、四个问题齐备**。四个演示必须稳定复现 |
| tag `v9-infra` | 单元 3 结束：conftest + factories 就绪 |
| tag `v9-guards` | 单元 5 结束：四条约定检查 + SQL 计数断言 |
| tag `v9-ci` | 单元 8 结束：CI 配置完整、全绿 |
| tag `v9-final` | 作业参考交付状态 |
| `tests/conftest.py` | **含方案 C 与方案 B 的切换开关**（教师裁决点） |
| `tests/factories.py` | user / question / answer 三个 factory |
| `tests/test_conventions.py` | 现场四条 + 作业参考实现（另存 `solutions/`） |
| `tests/test_performance_guards.py` | SQL 计数两条断言 |
| `scripts/dump_openapi.py`、`scripts/check_contract.sh` | 离线契约校验 |
| `scripts/check_coverage_not_dropped.py` | 覆盖率基线 |
| `.github/workflows/ci.yml`、`Makefile`、`.pre-commit-config.yaml` | 完整可用 |
| **封面级 A** | 单元 1.1 的"十三条纪律，全靠我记得"表 |
| **封面级 B** | "测试的价值在于它失败"核心句 |
| **封面级 C** | 单元 2 演示一的"测试以为在测 / 实际在测"示意图 |
| **封面级 D** | 单元 3.4 的"commit 收敛 → 测试能接管事务"回收页 |
| **封面级 E** | 单元 3.5 的 `dependency_overrides` 对照表 + "框架没有魔法"（列出三个普通对象） |
| **封面级 F** | 单元 4.1 的八行 mock 判据表 |
| **封面级 G** | 单元 5.0 的"红-绿两步"方法论 |
| **封面级 H** | 单元 5.1 的"可检视 → 可检查 → 可防止" |
| **封面级 I** | 单元 5.5 的七道护栏累加表（新增"拦截时机"列） |
| **封面级 J** | 单元 6.2 的删断言实验前后对比（两处 `92%` 圈红） |
| **封面级 K** | 单元 6.3 的"自检三问" |
| **封面级 L** | 单元 8.1 的"CI 是一句承诺" |
| 高光图 M | 单元 2 的四个问题性质对照表 |
| 高光图 N | 单元 3.1 的"bug 发生在接缝处"五行表 |
| 高光图 O | 单元 3.2 的 SQLite 测不出的八件事 |
| 高光图 P | 单元 3.4 的三种隔离方案耗时对照 |
| 高光图 Q | 单元 4.2 的"mock 掉数据库就测不到的七件事" |
| 高光图 R | 单元 5.3 的"断言数值 vs 断言性质" |
| 高光图 S | 单元 5.6 的"什么该变成检查"（最后一行标红） |
| 高光图 T | 单元 6.4 的覆盖率四种用法 |
| 高光图 U | 单元 7.4 的端到端"该写/不该写" |
| 高光图 V | 单元 8.3 的三层分工表 |
| **截图组（关键）** | 单元 5 四条检查的红/绿各一张，**共八张。这是本次课最重要的素材** |
| 截图 | 删空 service 实现后 `2 passed` |
| 截图 | `pytest -p randomly` 的两个失败（NameError + 409） |
| 截图 | 改文案后 5 个测试红 |
| 截图 | 删断言后覆盖率不变（两个终端并排） |
| 截图 | 边界改坏后 `23 passed`、补测试后变红 |
| 截图 | `mailer.sned` 在 MagicMock 下通过 / 在 Fake 下报错 |
| 截图 | schemathesis 报出 `qid = -1` → 500 |
| 截图 | 三种隔离方案的 100 测试实测耗时 |
| **截图（关键）** | **GitHub PR 页面：一条检查红着、合并按钮被禁用** |
| 截图 | CI 全绿步骤列表（含各步耗时） |

### 可后补

- 跨语言测试栈对照表、一句话结论卡（纯文字）。
- Playwright 配置与 e2e 代码（**若单元 7.4 压缩，只需代码不需截图**）。

### 备用材料

| 风险 | 备用方案 |
|---|---|
| **`join_transaction_mode="create_savepoint"` 在学生环境行为异常**（最高风险，教师裁决点） | `conftest.py` 里提供方案 B（truncate）实现，**一个 fixture 切换**。课前务必统一 SQLAlchemy 版本并实测一次 |
| CI 现场演示依赖网络（GitHub Actions 要等） | **预先准备一个已经跑完的 PR 页面**（含红/绿两种状态截图）；现场只演示本地 `make check` |
| `pytest -n auto` 在教室机器上不稳定 | 只演示 `-p randomly`，并行作为作业要求 |
| schemathesis 版本差异导致 API 变化 | 锁版本；备 7.2 的五行替代方案作为主讲内容 |
| Playwright 浏览器下载慢 | 课前预装；或整个单元 7.4 只讲结论 |
| 教室机器跑全套测试太慢，演示节奏断 | 准备一个**只含本次课相关测试**的子集 `pytest tests/test_conventions.py tests/test_questions_api.py` |
| AI 现场调用失败（作业三演示） | 准备预录的两轮输出。**第一轮那份必须真实体现"测试固化了 bug"**，不要人工编造 |
| 时间超支 | 按单元〇的压缩顺序执行；单元 7 有自读材料 `docs/contract_testing.md` |

### 环境与运行条件

延用前序环境。**新增依赖**：`pytest`、`pytest-cov`、`pytest-randomly`、`pytest-xdist`、`schemathesis`（可选）、`ruff`、`mypy`；Playwright（可选）。

**新增基础设施**：一个独立的测试数据库 `app_test`（`docker compose` 里加一个 service 或同一个实例的另一个库）。

**演示开始时的初始状态**：工作区在 tag `v9-broken`；开发库有数据（seed 过）；**测试库存在但为空**；三个终端（一个跑 pytest、一个跑 psql、一个编辑）；浏览器开一个预备好的 PR 页面标签。

**复位方式**：`make reset-test-db`（约 10 秒）+ `git checkout v9-broken -- tests/ app/`。

---

## 十二、与前后课的衔接

**本次课回收的前序埋点（本次课是回收最密集的一次，请在课件中显式标记每一处）**：

| 来源 | 埋点 | 回收位置 |
|---|---|---|
| 第 2 次课 | "把依赖人记得的规则换成会出声的机制" | **贯穿全课，单元 5 是总收口** |
| 第 3 次课 | 打印 `app.routes` 破除装饰器魔法 | **单元 5.1**（同一个数据结构变成检查的输入） |
| 第 3 次课 | `response_model` 是第一道护栏 | 单元 5.1（现在它自己也被检查了） |
| 第 3 次课 | 依赖稳定标识不依赖文案 | 单元 2 演示三、3.6（**第五次出现**） |
| 第 3 次课 | 入口闸门：约束越靠前越好 | 单元 7.1（`qid: int = Path(gt=0)`） |
| 第 4 次课 | 依赖注入"就为少写几行值得吗" | **单元 3.5 完整回答** |
| 第 4 次课 | 统一错误契约 `code/message/detail/request_id` | 单元 3.6、7.2（用它自己的 schema 校验自己） |
| 第 4 次课 | 分层：`services/` 不 import fastapi | 单元 5.7 第 3 条 |
| 第 5 次课 | "约定 + 机械检查 + 定量兜底"三层 | **单元 7.1**（契约测试是"定量兜底"层，**第六次使用这套方法**） |
| 第 5 次课 | `async def` + 阻塞"无法在结构上堵住" | 单元 5.7 第 5 条（**AST 可以堵住，修正了当时的判断**） |
| 第 5 次课 | 模板不许 `\| safe` | 单元 5.7 第 6 条 |
| 第 6 次课 | 数据库约束是第四道护栏 | **单元 4.2**（mock 掉数据库 = 放弃这道护栏） |
| 第 6 次课 | 查 `pg_catalog` 找无索引外键/无主键表 | **单元 5.7 第 7 条**（手工 SQL 变成 pytest） |
| 第 6 次课 | 数据库特性（CHECK 函数、TIMESTAMPTZ、ILIKE） | 单元 3.2（SQLite 测不出这些） |
| 第 7 次课 | `.commit()` 从 15 处收到 1 处 | **单元 3.4**（这才是它第二个、也更大的回报） |
| 第 7 次课 | `sqlcount.py` 计数器 | **单元 5.3**（变成断言，如约兑现） |
| 第 7 次课 | `lazy="raise"` 第五道护栏 | 单元 5.3（与 SQL 计数断言叠加，两级保护） |
| 第 7 次课 | 迁移必须能 downgrade | 单元 8.2（CI step） |
| 第 7 次课 | `alembic check` / 模型是唯一真相来源 | 单元 8.2 |
| 第 7 次课 | `flush` 不是 `commit` | 单元 3.6（factory 用 flush） |
| 第 8 次课 | `npm run gen` + `git diff --exit-code` | **单元 5.4**（如约进 CI） |
| 第 8 次课 | `tsc --noEmit` 零错误 | 单元 7.3 |
| 第 8 次课 | 列表页请求数 ≤ 2 | **单元 7.4**（Playwright 断言） |
| 第 8 次课 | 契约测试（schemathesis） | **单元 7.1** |
| 第 8 次课 | "最有价值的约束是能被自动检查的约束" | **单元 5.6 给出判据，作业二让学生实践** |
| 第 8 次课 | 作业三第四问"还有哪些约定能变成检查" | **单元 5.7 的表就是答案，作业二实现它** |

**本次课埋下、后面必须回引的五处**（请在课件中明显标记）：

- **单元 3.5 的 `dependency_overrides`** → 第 14 次课伪造当前用户，一行 override 就能测所有权限分支；
- **单元 5.3 的"断言性质不断言数值"** → 第 11 次课做缓存和 keyset 分页时，用同一手法写性能守卫；
- **单元 4.1 的 mock 判据表** → 第 11 次课要回答"缓存该不该 mock"（答案：不该，Redis 也要真起一个，理由同 4.2）；
- **单元 5.5 的第七道护栏（CI 是容器）** → 第 15 次课把安全检查装进这个容器；
- **单元 8.2 的 CI 骨架** → 第 16 次课从 CI 延伸到 CD，同一个文件继续加 job。

**本次课不承担、请勿提前引入**：缓存与性能优化（第 11 次课）、CORS（第 12 次课）、认证与权限（第 14 次课）、安全攻防（第 15 次课）、部署与压测（第 16 次课）、变异测试工具/快照测试/testcontainers（C 档卡）。

**给第 10 次课的提示**：

本次课交付了三样**可以立刻复用的基础设施**，后续每一次课引入新能力时都应该先用它们：

| 资产 | 后续怎么用 |
|---|---|
| `conftest.py` 的隔离 fixture | 任何新特性的集成测试，零成本接入 |
| `dependency_overrides` 的替身模式 | 引入任何新的外部依赖（缓存、队列、第三方 API）时，**先让它成为一个依赖**，测试就自动可控 |
| `tests/test_conventions.py` | 引入任何新约定时，**先写检查，再写实现** |

**建议后续每一次课都增加一个固定动作：本次课新增了什么纪律，当场把它的检查补进 `test_conventions.py`。**

这个动作会让"把纪律变成结构"从一次专题课变成一个持续的习惯——**而这正是本课程希望学生带走的最核心的工作方式。**

另外，本次课留下了一个**尚未兑现的判断**，值得在后续课程中检验：单元 5.6 说"宁可少几条检查，也不要有一条会误报的检查"。随着项目变复杂（尤其引入缓存和并发之后），学生会遇到第一批**真正 flaky 的测试**——那时候 C 档卡里"先查共享状态和时间依赖，不要加 retry"这条结论会变得非常具体。**建议在遇到时明确回引一次。**