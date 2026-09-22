# 第 4 次课教学底稿
## 框架机制 II：依赖注入、分层与统一错误契约

---

## 〇、给 PPT 制作团队的全局说明

本次课 100 分钟，留 5 分钟缓冲。**本次课的定位写在大纲上就一句话：先痛感，后命名。请严格按这个顺序制作，不要提前给出结论。**

具体来说：课件中**不允许在单元 2 结束之前出现"依赖注入""分层架构"这两个词**，也不要出现目录结构图。学生必须先经历"改一个小需求要动 11 个地方"，才有资格听"所以我们把它抽出来"。如果颠倒顺序，这节课就退化成一堂架构名词介绍课——那正是本课程要避免的教法。

**本次课的主线**：第 3 次课把"数据的进出"收拢到了两道闸门。本次课收拢的是**代码本身的位置**——同一件事只在一个地方写，并且那个地方是可以被指认的。

**本次课的核心证据，是一组可以量化的数据。** 请务必保留并做成高光对照：同一个需求变更（把分页上限从 100 改成 50、给所有错误响应加上 request_id），在重构前需要改动多少个文件多少处，重构后需要改动多少。这个 before/after 数字是整节课的说服力来源，比任何架构图都有效。

**最难讲清、优先制作的三处**：

1. **需求变更的痛感演示（单元 2）**。难点在于学生会觉得"改 11 个地方也就多花五分钟"。必须补上第二层：**改 11 个地方意味着漏改 1 个地方不会有任何提示**。请把"漏改一处"的后果现场演示出来。
2. **全局异常处理器修了一半（单元 5.5）**。这是本次课最精彩、也最容易被做浅的一处。`AppError` 的处理器能让第 1 次课的中间件恢复正常，但 `Exception` 兜底处理器**不能**——因为它运行在用户中间件的外层。这个"位置决定行为"的结论需要一张洋葱层次图支撑，并明确埋点到第 5 次课。
3. **依赖方向为什么是单向的（单元 6.3）**。不要讲成架构教条。要给两个具体后果：一个是循环导入当场崩溃，另一个是"service 里 raise HTTPException 会导致你的定时任务抛出 HTTP 异常"。后者才是本质理由。

**若时间不够的压缩顺序**：先压单元 9 的 C 档卡（整体移到课后自读）→ 再压单元 4 的"第五种用法：依赖工厂"（只留一句话，第 14 次课会正式用）→ 再压单元 7 的 git 历史演示（改为课件静态截图 + 一句话）。**单元 2、5、6 不能压缩，它们是本次课的全部价值。**

**一个需要教师裁决的地方**：本次课的统一错误契约采用课程自定义的扁平格式（`code/message/detail/request_id`），而不是 RFC 9457 的 `problem+json`。底稿在单元 5.3 给出了选择理由并把 RFC 9457 放进 C 档卡。如果你希望直接采用 RFC 9457，请告知——这会改变第 8、12 次课的前端解析代码。

---

## 一、开场：两道闸门之间的那一堆代码

**约 4 分钟。**

内容：

把第 3 次课的"两道闸门"图重新放上来，然后**把中间那一格放大**。

第 3 次课我们解决了"数据怎么进来、怎么出去"。今天的问题是：**闸门之间的那些代码，应该放在哪里？**

现在你的项目里，这个问题的答案是"全都放在路由函数里"。它能跑。第 3 次课的六个端点全部通过验收。所以今天要先回答一个更基本的问题：

> **既然能跑，为什么要改？**

这个问题必须先回答，否则今天讲的一切都是"因为大家都这么写"。

本次课结束时你应当能回答：

- 同一件事写在 6 个地方，多出来的成本**具体是什么**？（不是"不优雅"，要说得出可度量的东西）
- `Depends` 到底做了什么？它和"直接调用一个函数"的区别在哪？
- 为什么 `services/` 里不许 `import` `routers/`？违反了会发生什么？
- 一段横切逻辑，怎么判断它该写成中间件、依赖、还是服务层的函数？
- 为什么第 1 次课那个日志中间件在出错时会失灵，今天怎么修，**为什么只能修一半**？

讲：

> 今天这节课的风险是变成"架构名词介绍"。我不打算那样上。
>
> 顺序是这样的：我们先一起改一个非常小的需求，改完你们自己数改了几个地方。然后我再告诉你这些东西叫什么名字。
>
> **名字是最没价值的部分。** 你去问 AI "帮我做分层架构"，它能给你一套目录，甚至比我给的更漂亮。但它不知道你的项目里哪些东西重复了、哪些边界正在被越过——**那需要有人看着具体代码做判断。今天练的是这个。**

---

## 二、解剖台：一个小需求，改十一个地方

**约 15 分钟。本次课的痛感来源，请严格按三步顺序展开。**

### 2.1 现在的代码（tag: `v4-flat`，第 3 次课作业的参考答案状态）

这不是一段"烂代码"。它通过了第 3 次课的全部验收：路由顺序正确、每个端点都有 In/Out schema、状态码规范。**请在课件上明确说明这一点**，否则学生会以为今天是在改烂代码。

```python
# app/main.py —— 第 3 次课交付状态，约 230 行，此处节选 3 个端点
from fastapi import FastAPI, Request, HTTPException
from sqlalchemy import create_engine, text
import os, logging, uuid, time

app = FastAPI()
engine = create_engine(os.getenv("DATABASE_URL"))
logger = logging.getLogger("app")


@app.get("/questions", response_model=QuestionListOut, tags=["questions"])
def list_questions(keyword: str = "", page: int = 1, page_size: int = 20):
    if page < 1:
        page = 1
    if page_size < 1 or page_size > 100:        # ← 记住这行
        page_size = 20
    offset = (page - 1) * page_size
    try:
        with engine.connect() as conn:           # ← 记住这行
            rows = conn.execute(text(
                "SELECT q.id, q.title, q.created_at, u.id AS author_id, "
                "u.display_name FROM questions q "
                "JOIN users u ON u.id = q.author_id "
                "WHERE q.title ILIKE :kw "
                "ORDER BY q.created_at DESC, q.id DESC "
                "LIMIT :lim OFFSET :off"),
                {"kw": f"%{keyword}%", "lim": page_size, "off": offset},
            ).fetchall()
            total = conn.execute(text(
                "SELECT count(*) FROM questions WHERE title ILIKE :kw"),
                {"kw": f"%{keyword}%"},
            ).scalar()
    except Exception as e:                       # ← 记住这行
        logger.error("list_questions failed: %s", e)
        raise HTTPException(status_code=500, detail="数据库错误")
    return {"items": [...], "total": total, "page": page}


@app.get("/questions/{qid}", response_model=QuestionOut, tags=["questions"])
def get_question(qid: int):
    try:
        with engine.connect() as conn:           # ← 又一次
            row = conn.execute(text(
                "SELECT q.*, u.display_name FROM questions q "
                "JOIN users u ON u.id = q.author_id WHERE q.id = :qid"),
                {"qid": qid},
            ).fetchone()
    except Exception as e:
        logger.error("get_question failed: %s", e)
        return JSONResponse(status_code=500,
                            content={"error": "db error"})   # ← 格式又变了
    if row is None:
        raise HTTPException(status_code=404, detail="Question not found")
    return {...}


@app.post("/questions", response_model=QuestionOut, status_code=201,
          tags=["questions"])
def create_question(payload: QuestionCreate):
    with engine.connect() as conn:               # ← 第三次
        dup = conn.execute(text(
            "SELECT 1 FROM questions WHERE title = :t"), {"t": payload.title}
        ).fetchone()
        if dup:
            raise HTTPException(status_code=409,
                                detail={"code": "duplicate_title"})  # ← 格式第三种
        r = conn.execute(text(
            "INSERT INTO questions (title, body, author_id) "
            "VALUES (:t, :b, 1) RETURNING id"),
            {"t": payload.title, "b": payload.body},
        )
        new_id = r.scalar()
        conn.commit()                            # ← 散落的 commit
    return get_question(new_id)                  # ← 路由函数互相调用
```

### 2.2 第一步：让学生数

先不评价，只提一个问题：

> 产品同学说："分页一次最多给 50 条，100 条太多了，手机上加载太慢。"
>
> **打开你的项目，数一下你要改几个地方。**

留 90 秒，让学生真的去数。答案是 **4 处**（三个列表端点 + 一个搜索端点），而且每一处的写法还略有不同——有的写 `> 100`，有的写 `>= 100`，有的忘了处理 `page_size = 0`。

接着追加第二个需求：

> 运维同学说："出错的时候用户截图给我，我看不出是哪一次请求。所有错误响应里都要带上 request_id。"
>
> **数一下要改几个地方。**

答案是 **11 处**——所有 `HTTPException`、所有 `JSONResponse`、所有 `raise`。而且第 3 次课留下的 422 自动响应**你压根改不到**，它是框架生成的。

把结果做成一张表放在屏幕上：

| 需求 | 需要改动的位置数 | 附带问题 |
|---|---|---|
| 分页上限 100 → 50 | 4 处 | 现有 4 处写法本来就不一致 |
| 所有错误响应带 request_id | 11 处 | 框架自动产生的 422 改不到 |
| 数据库连接池满时返回 503 而非 500 | **不知道** | 每个 except 都写着 500，得逐个判断 |

### 2.3 第二步：追加真正的代价（**这一层不能省**）

学生此时的想法是："改 11 个地方，也就是多花五分钟。"

必须把话说到底：

> 改 11 个地方要花五分钟，这不是问题。问题是：
>
> **如果你漏改了 1 个地方，没有任何东西会告诉你。**

现场演示：故意漏改一个端点（比如 `PATCH /questions/{qid}`），然后触发它的错误路径。

结果：接口正常返回 404，格式是旧的。**没有报错、没有测试失败、没有日志告警。** 用户报障时截图给你，上面没有 request_id，你查不到——而你以为这件事已经做完了。

> 这就是第 2 次课说的"沉默的成本"，在代码组织上的版本。
>
> 一件事分散在 N 个地方，它的真实成本不是"改 N 次"，是"**正确性依赖于你每次都记得改全 N 次**"。这是一个随代码量增长而必然失败的赌注。

然后把它接到课程主题上（这是本次课的关键一句）：

> 现在把 AI 加进来考虑。
>
> 你让 AI "加一个收藏问题的端点"。它会照着你现有代码的样子写——**因为那是它能看到的模式**。于是你的项目里多了第 12 个错误格式、第 5 处分页上限。
>
> **代码里的重复，在 AI 参与之后不是线性增长，是自我复制。** 它会把你现在的任何一个坏模式，忠实地复制到每一个新文件里。
>
> 所以今天要做的事，本质上不是"让代码好看"。是**让"只有一个地方可以改"这件事成为结构上的事实**，这样 AI 就没有第二个地方可抄。

### 2.4 第三步：把重复分类，但还不给解决方案

把六个端点并排贴出来，让学生指出**重复的是什么**。整理成四类，**先只命名重复的种类，不给方案**：

| 重复种类 | 表现 | 每个端点都写了什么 |
|---|---|---|
| ① 资源获取与清理 | `with engine.connect()` | 6 处 |
| ② 入参的规整与约束 | page / page_size 的边界处理 | 4 处，写法不一致 |
| ③ 错误的捕获与格式化 | try/except + 各种响应格式 | 11 处，4 种格式 |
| ④ 业务逻辑与 HTTP 混在一起 | "查重"和"返回 409"写在一起 | 全部 |

> 注意这四类的性质不一样。
>
> ①②是"每个端点都要做的准备工作"。
> ③是"每个端点都可能发生的意外"。
> ④不是重复，是**混淆**——两种不同层次的东西写在了一行里。
>
> 前三类要靠"抽出来"解决，第四类要靠"分开"解决。今天两件事都做。

### 欠账清单（本次课要还的）

| 前序课的欠账 | 在本次课哪里还 |
|---|---|
| 第 1 次课：中间件在异常路径下失灵 | 单元 5.5（只能修一半，如实说明） |
| 第 1 次课：密钥硬编码只做了 `os.getenv` | 单元 7 |
| 第 3 次课：422 格式与统一错误契约不一致 | 单元 5.4 |
| 第 3 次课：`conn.commit()` 散落在端点里 | 单元 3.4（事务边界初版） |
| 第 3 次课：查库才能判断的校验放哪 | 单元 6（服务层） |
| 第 3 次课：数据库连接每次现开 | 单元 3 |

---

## 三、现场必做 A：抽掉第一种重复

**约 13 分钟。这是"命名"阶段的开始。**

### 3.1 先用最朴素的办法，然后看它为什么不够

学生的第一反应通常是"写个函数"：

```python
def get_conn():
    return engine.connect()

@app.get("/questions")
def list_questions(...):
    conn = get_conn()
    ...
    conn.close()        # ← 还是要每个端点自己 close
```

指出问题：

1. **还是要每个端点自己 close**，而且异常时不会执行——重复只减少了一半；
2. 要写 `try/finally` 才对，于是每个端点又多了三行样板；
3. 这个 `conn` 是端点函数内部变量，**测试时没有任何办法替换它**。（第 3 点先留个印象，第 9 次课才有分量）

### 3.2 命名：`Depends`

现在给出框架的做法：

```python
# app/deps.py
from typing import Iterator
from sqlalchemy import Connection
from app.db import engine

def get_conn() -> Iterator[Connection]:
    with engine.begin() as conn:      # begin: 正常退出 commit，异常自动 rollback
        yield conn
```

```python
# app/routers/questions.py
from fastapi import Depends

@app.get("/questions", response_model=QuestionListOut)
def list_questions(conn: Connection = Depends(get_conn)):
    ...
    # 不需要 close，不需要 commit，不需要 try/finally
```

**`Depends` 做的事情，用一句话说清楚**（醒目页）：

> **你在函数签名里声明"我需要一个 X"，框架在调用你之前把 X 准备好，调用之后把它收拾干净。**
>
> 和自己调用函数的区别在三点：
> 1. **清理是框架保证的**——`yield` 之后的代码在端点返回后一定执行，包括抛异常的情况；
> 2. **它写在签名里，是显式契约**——看一眼函数签名就知道这个端点需要什么；
> 3. **它是一个可替换的挂点**——框架允许你在运行时把 `get_conn` 换成别的东西（第 9 次课测试时会用到）。

### 3.3 yield 依赖的执行时序（必须讲清，否则后面事务讲不明白）

画一条时间轴：

```
请求进入
  → 依赖求值：get_conn 执行到 yield，交出 conn
      → 端点函数执行（拿到 conn）
      → 端点函数 return
  → 依赖清理：yield 之后的代码执行（with 退出 → commit 或 rollback）
  → 响应发出
```

两个要点：

- **清理发生在端点函数返回之后**，所以端点里不需要也不应该 `commit()`；
- **端点抛异常时清理同样执行**，`engine.begin()` 的上下文会自动 rollback。

现场验证：在一个端点里故意 `raise ValueError`，观察数据库里那条 INSERT **没有生效**。

### 3.4 顺手还掉第 3 次课的欠账：事务边界

> 第 3 次课我们看到 `conn.commit()` 散落在端点各处，当时记了一笔。现在它消失了——**因为事务的开始和结束都由这个依赖决定了**。
>
> 这句话可以说得更一般一些：**一个请求，一个事务。** 请求开始时开事务，端点正常返回就提交，抛异常就回滚。
>
> 判据：**端点函数里不应该出现 `commit()`。** 如果你看到了，说明有人在闸门里面又开了一道小门。
>
> 〔这只是事务边界的初版。真正的讨论——什么时候一个请求需要多个事务、嵌套怎么办——在**第 7 次课**，那时候 `Connection` 会换成 SQLAlchemy 的 `Session`，而**只有 `deps.py` 这一个文件要改**。〕

最后一句要停一下说：

> 请记住我刚说的"只有一个文件要改"。第 7 次课我们会验证它。**这就是今天做这件事的回报——回报不在今天，在下一次变更。**

### 3.5 数一下战果

| | 重构前 | 重构后 |
|---|---|---|
| 写 `engine.connect()` 的地方 | 6 | **1** |
| 写 `commit()` 的地方 | 3 | **0** |
| 换数据库连接方式要改的文件 | 6 | **1** |

### 材料

- tag `v4-flat`（起始版）、`v4-deps`（本单元结束状态）。
- 截图需求：故意 `raise ValueError` 后查询数据库确认 INSERT 未生效的终端截图，**需同时显示异常栈与查询结果为空**。

---

## 四、Depends 的四种用法与依赖树

**约 12 分钟。这是一个 API 讲授单元，请控制在 12 分钟内，用"每种用法解决哪一类重复"来组织，不要做成 API 手册。**

### 4.1 用法一：普通依赖——把入参规整抽出来（解决重复种类 ②）

```python
# app/deps.py
from dataclasses import dataclass
from fastapi import Query

@dataclass
class Page:
    page: int
    size: int
    offset: int

def pagination(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=50),      # ← 上限只在这一行
) -> Page:
    return Page(page=page, size=size, offset=(page - 1) * size)
```

```python
@app.get("/questions", response_model=QuestionListOut)
def list_questions(pg: Page = Depends(pagination),
                   conn: Connection = Depends(get_conn)):
    ...  # 直接用 pg.size, pg.offset
```

**两个要讲的点**：

1. **约束回到了 schema 层。** 注意这里用的是 `Query(..., ge=1, le=50)`，不是 `if size > 50`。回收第 3 次课的判据："能表达为类型和约束的，就不要写成 if"。现在 `?size=999` 返回的是 **422**，而不是被静默改成 20——**静默修正用户的输入是不好的行为，它让客户端永远不知道自己传错了**。
2. **依赖的返回值可以是任何对象。** 这里返回一个 dataclass，于是端点拿到的是结构化的 `Page`，而不是三个散落的整数。

现在回到开场的需求："上限改成 50"——**改 1 行，1 个文件**。

### 4.2 用法二：带 yield 的依赖——资源生命周期（已在单元 3 讲过，此处只做归类）

规则：**需要"用完要收拾"的东西，就用 yield 依赖**。数据库连接、文件句柄、分布式锁、临时目录。

### 4.3 用法三：子依赖——依赖也可以有依赖

```python
# app/deps.py
def get_question_or_404(
    qid: int,                                  # ← 自动从路径参数取
    conn: Connection = Depends(get_conn),      # ← 依赖的依赖
) -> Row:
    row = repo.find_question(conn, qid)
    if row is None:
        raise QuestionNotFound(qid)            # ← 单元 5 会定义这个异常
    return row
```

```python
@app.get("/questions/{qid}", response_model=QuestionOut)
def get_question(q: Row = Depends(get_question_or_404)):
    return q

@app.patch("/questions/{qid}", response_model=QuestionOut)
def update_question(payload: QuestionUpdate,
                    q: Row = Depends(get_question_or_404),
                    conn: Connection = Depends(get_conn)):
    ...
```

**这个例子值得多说一句，因为它是本次课通往第 14 次课的桥**：

> 注意 `get_question_or_404` 干了什么：它把"取出资源，不存在就 404"这个每个单项端点都要做的动作，抽成了一个可以声明的依赖。
>
> **第 14 次课我们会在这个函数里再加一句话**——检查当前登录用户是不是这条问题的作者，不是就 403。那个依赖叫 `get_owned_question`。
>
> 也就是说：**授权检查最终会挂在这个位置上。** 今天先把这个位置腾出来。

### 4.4 依赖缓存：同一个请求内只求值一次（**必须现场演示，这是高频踩坑点**）

上面 `update_question` 同时依赖了 `get_question_or_404` 和 `get_conn`，而前者内部又依赖 `get_conn`。

提问（先让学生预测）：

> `get_conn` 会执行几次？会开两个连接吗？

在 `get_conn` 里加一行日志，发一次请求。答案：**一次**。

> **同一个请求内，同一个依赖函数默认只求值一次，结果被缓存并共享。**
>
> 这一条非常重要，因为它意味着：`update_question` 里的 `conn`，和 `get_question_or_404` 里用的 `conn`，**是同一个连接、同一个事务**。
>
> 如果不是这样，你在一个事务里查出的数据，在另一个事务里更新，就会出现各种诡异的不一致。
>
> 需要关闭缓存时用 `Depends(f, use_cache=False)`，但请先问自己"我为什么需要两份"。

### 4.5 第五种：依赖工厂（一句话，留给第 14 次课）

依赖可以带参数——写一个返回依赖函数的函数：

```python
def require_role(role: str):
    def checker(user = Depends(get_current_user)):
        if user.role != role: raise Forbidden()
    return checker

@app.delete("/questions/{qid}", dependencies=[Depends(require_role("admin"))])
```

> 注意 `dependencies=[...]` 这种写法：**这个依赖的返回值我不需要，我只要它执行**。这是"纯检查型"依赖的标准写法。第 14 次课正式用。

### 4.6 B 档：打印依赖树与求值顺序

延续第 3 次课那个动作——**把框架的内部状态打印出来**：

```python
# app/dump_deps.py
def dump(dep, indent=0):
    name = dep.call.__name__ if dep.call else "(endpoint)"
    print("  " * indent + f"- {name}")
    for sub in dep.dependencies:
        dump(sub, indent + 1)

for r in app.routes:
    if hasattr(r, "dependant"):
        print(f"{list(r.methods)[0]:6} {r.path}")
        dump(r.dependant, 1)
```

输出（节选）：

```
PATCH  /questions/{qid}
  - update_question
    - get_question_or_404
      - get_conn
    - get_conn
```

配合在每个依赖里打日志，观察实际求值顺序：

```
[a3f9] dep: get_conn       ← 先求最深的
[a3f9] dep: get_question_or_404
[a3f9] endpoint: update_question
[a3f9] cleanup: get_conn   ← 最后清理
```

> **规则：依赖树是深度优先、自底向上求值的；清理反序执行。**
>
> 这和第 1 次课调用栈那张图是同一件事的另一个侧面——**框架的行为都是可以打印出来的，不需要猜。**

---

## 五、现场必做 B：统一错误契约

**约 17 分钟。本次课高光，绝对不能压缩。**

### 5.1 先把现状摊开

把项目里所有错误响应的实际格式列出来（这是学生自己项目的真实状态）：

```json
{"detail": "Question not found"}                          ← HTTPException 默认
{"error": "db error"}                                     ← 手写 JSONResponse
{"detail": {"code": "duplicate_title"}}                   ← HTTPException 带 dict
{"detail":[{"type":"string_too_short","loc":["body","title"],...}]}  ← 框架 422
{"success": false, "message": "..."}                      ← 第 1 次课残留
```

提问：

> 你现在要写前端的错误提示。**你怎么写这个函数？**

学生会发现要写成这样：

```js
const msg = data.detail?.code
         ?? data.detail
         ?? data.error
         ?? data.message
         ?? (Array.isArray(data.detail) ? data.detail[0].msg : null)
         ?? '未知错误';
```

> 这段代码就是代价本身。而且它**永远写不完**——后端每加一个端点，就可能多一种格式，前端就要多一个 `??`。
>
> 更糟的是第 12 次课你会发现：这段代码要在**每一个**发请求的地方都写一遍。

### 5.2 契约：先定形状，再谈实现（回收第 3 次课的方法）

第 3 次课学的方法是"契约先行"。这里用同样的方法——**先定错误响应的形状**：

```json
{
  "code": "question_not_found",
  "message": "问题不存在",
  "detail": null,
  "request_id": "a3f91c22e0d7"
}
```

四个字段的分工（**这张表是本单元的核心，请做成醒目页**）：

| 字段 | 给谁看 | 性质 | 前端怎么用 |
|---|---|---|---|
| `code` | **机器** | 稳定、可枚举、不随文案变化 | **用它做分支判断** |
| `message` | **人** | 可以改、可以国际化 | 直接展示给用户 |
| `detail` | 人 + 机器 | 字段级细节，如校验失败的字段列表 | 表单错误回填 |
| `request_id` | **排查者** | 贯通客户端与服务端日志 | 显示在错误提示角落 |

**两条判据**：

> **判据一：`code` 是契约的一部分，`message` 不是。**
> 前端不许对 `message` 的文字做判断（`if (msg === '问题不存在')`），因为那句话明天可能改成"该问题已删除"，或者要翻译成英文。这一条回收第 3 次课读 422 时的同一个判据：**依赖 `type`，不依赖 `msg`。**
>
> **判据二：`request_id` 是错误响应的必填字段。**
> 这是第 1 次课那条线的收尾。第 1 次课我们把 request-id 放进了响应头和日志，今天把它放进错误响应体——因为**用户截图的是页面，不是响应头**。

### 5.3 为什么不用 RFC 9457（这是一次方案取舍的示范）

> 有一个正式标准叫 RFC 9457 `application/problem+json`，字段是 `type/title/status/detail/instance`。
>
> 本课程**不采用**它，理由有三条：
> 1. 它的 `type` 是一个 URI，要求你为每类错误维护一个可访问的文档地址——对本课程规模是净成本；
> 2. `Content-Type: application/problem+json` 会让部分前端 HTTP 库的默认解析路径变化，增加联调噪音；
> 3. 它没有 `request_id` 的位置，还是要放进扩展字段。
>
> **但你要知道它存在**，因为对外开放的公共 API、或者要和其他团队/其他公司的系统对接时，用一个已有标准比自己发明一套更省沟通成本。C 档卡里有它的完整字段表。
>
> 这是本课程第一次让你们看到**一个完整的方案取舍**：不是"哪个更好"，是"**在什么条件下，哪个的净收益更高**"。条件变了（比如你的 API 要开放给第三方），结论就该变。第 0 次课列的第五项能力就是这个。

### 5.4 实现：异常分类 + 全局处理器

**第一步：定义应用自己的异常体系。**

```python
# app/errors.py
class AppError(Exception):
    """应用内所有预期错误的基类。"""
    status_code: int = 500
    code: str = "internal_error"
    message: str = "服务器内部错误"

    def __init__(self, message: str | None = None, detail=None):
        self.message = message or self.message
        self.detail = detail
        super().__init__(self.message)


class NotFound(AppError):
    status_code, code, message = 404, "not_found", "资源不存在"

class QuestionNotFound(NotFound):
    code, message = "question_not_found", "问题不存在"

class Conflict(AppError):
    status_code, code, message = 409, "conflict", "状态冲突"

class DuplicateTitle(Conflict):
    code, message = "duplicate_title", "已存在同名问题"

class Forbidden(AppError):                       # ← 第 14 次课会大量使用
    status_code, code, message = 403, "forbidden", "没有权限执行此操作"
```

**这里有一个必须讲出来的设计决定**（请做成提问）：

> 为什么定义 `AppError` 而不是直接用 FastAPI 的 `HTTPException`？
>
> 因为 `HTTPException` 里有 `status_code`——**它是一个 HTTP 概念**。
>
> 而抛出这个异常的地方是 `services/`，那里的代码不应该知道 HTTP 存在。理由不是"分层教条"，是一个具体后果：
>
> **第 16 次课你会写一个定时任务，它复用同一个 service 函数。那个任务没有 HTTP 请求、没有响应可发。如果 service 抛的是 `HTTPException`，你的定时任务就会抛出一个"HTTP 404"——这毫无意义，而且没有任何东西会接住它。**
>
> 所以：`AppError` 描述的是"业务上发生了什么"，把它翻译成 HTTP 状态码是**路由层的职责**。这个翻译动作发生在下面的处理器里。

**第二步：注册三个处理器。**

```python
# app/exception_handlers.py
from fastapi import Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
import logging

logger = logging.getLogger("app")

def _body(code, message, detail, request_id):
    return {"code": code, "message": message,
            "detail": detail, "request_id": request_id}


def register(app):

    # ① 应用自己的预期错误
    @app.exception_handler(AppError)
    async def handle_app_error(request: Request, exc: AppError):
        rid = getattr(request.state, "request_id", "-")
        logger.warning("app_error code=%s rid=%s", exc.code, rid)
        return JSONResponse(
            status_code=exc.status_code,
            content=_body(exc.code, exc.message, exc.detail, rid),
        )

    # ② 框架的校验错误 —— 还第 3 次课的欠账
    @app.exception_handler(RequestValidationError)
    async def handle_validation(request: Request, exc: RequestValidationError):
        rid = getattr(request.state, "request_id", "-")
        return JSONResponse(
            status_code=422,
            content=_body(
                "validation_error", "请求参数不合法",
                [{"loc": e["loc"], "type": e["type"], "msg": e["msg"]}
                 for e in exc.errors()],
                rid,
            ),
        )

    # ③ 兜底：完全没想到的错误
    @app.exception_handler(Exception)
    async def handle_unexpected(request: Request, exc: Exception):
        rid = getattr(request.state, "request_id", "-")
        logger.exception("unhandled rid=%s", rid)      # ← 必须 exception，要栈
        return JSONResponse(
            status_code=500,
            content=_body("internal_error", "服务器内部错误", None, rid),
        )
```

**三个处理器各自的判据**（醒目页）：

| 处理器 | 接什么 | 日志级别 | 响应里能不能有内部信息 |
|---|---|---|---|
| `AppError` | **我预料到的**业务错误 | `warning`，不需要栈 | 可以有（`detail` 是给客户端的） |
| `RequestValidationError` | 客户端传错了 | 通常不记 | 可以有（字段级错误要回填表单） |
| `Exception` | **我没预料到的** | `exception`，**必须有完整栈** | **绝对不能有** —— 只给 code 和 request_id |

第三条要专门停下来讲：

> 兜底处理器**绝对不能把异常信息返回给客户端**。
>
> `str(exc)` 里可能有：SQL 语句、表结构、文件路径、连接串、内网 IP。把它返回出去，等于免费给攻击者做了一次信息收集。
>
> 那排查怎么办？**靠 request_id。** 用户给你 `a3f91c22e0d7`，你去日志里 grep 这一串，完整的栈就在那里。
>
> 这一条在第 16 次课部署时会重新出现，那时它的名字叫"生产环境必须关闭 debug 模式"。**今天你已经用结构解决了它——不是靠一个开关。**

**第三步：把 raise 换掉。**

```python
# 之前
raise HTTPException(status_code=404, detail="Question not found")
raise HTTPException(status_code=409, detail={"code": "duplicate_title"})
return JSONResponse(status_code=500, content={"error": "db error"})
try: ... except Exception as e: logger.error(...); raise HTTPException(500, ...)

# 之后
raise QuestionNotFound()
raise DuplicateTitle()
# ↓ 后两种直接删掉：
#   数据库异常由兜底处理器接，不需要每个端点写 try/except
```

**这一步的战果要明确数出来**：

| | 重构前 | 重构后 |
|---|---|---|
| 错误响应格式种数 | **5** | **1** |
| `try/except Exception` 的数量 | 11 | **0** |
| 加一个字段到所有错误响应，要改几处 | 11（且 422 改不到） | **1** |
| 前端错误解析代码 | 5 个 `??` 分支 | `data.code` |

### 5.5 现场必做：全局处理器修好了中间件——但只修好一半

**这是本单元最有价值的一段，请完整制作。**

回收第 1 次课的欠账。第 1 次课那个耗时日志中间件是这么写的：

```python
@app.middleware("http")
async def timing(request: Request, call_next):
    rid = uuid.uuid4().hex[:12]
    request.state.request_id = rid
    t0 = time.perf_counter()
    response = await call_next(request)              # ← 端点抛异常时这里会抛出
    cost = (time.perf_counter() - t0) * 1000
    logger.info("rid=%s %s %s %.1fms", rid, request.method, request.url.path, cost)
    response.headers["X-Request-Id"] = rid
    return response
```

第 1 次课发现的问题：**端点抛异常时，`await call_next` 直接抛出，后面的日志和响应头都不执行。** 出错的请求在日志里查不到耗时，响应里也没有 request-id——**恰恰是最需要排查的那些请求**。

**现在做两个实验，让学生自己看出区别。**

**实验一：触发一个 `AppError`（访问 `/questions/999999`）**

结果：
- 响应是统一格式的 404，**含 request_id**；
- 中间件的耗时日志**正常打印**；
- `X-Request-Id` 响应头**存在**。

**修好了。** 原因：`AppError` 被处理器接住并转换成了一个正常的 `JSONResponse`，对中间件来说这就是一次正常返回——`await call_next` 没有抛出。

**实验二：触发一个真正未预期的异常（在端点里 `raise RuntimeError("boom")`）**

先让学生预测：**这次中间件的日志会打印吗？**

结果：
- 响应是统一格式的 500，含 request_id（**处理器生效了**）；
- 中间件的耗时日志**没有打印**；
- `X-Request-Id` 响应头**不存在**。

**这就是"只修好一半"。**

**画那张洋葱图解释为什么**（本单元的核心素材）：

```
        ┌──────────────────────────────────────────┐
        │  ServerErrorMiddleware                    │  ← Exception 处理器在这一层
        │   ┌──────────────────────────────────┐   │     它在你的中间件外面
        │   │  你的 timing 中间件               │   │
        │   │   ┌──────────────────────────┐   │   │
        │   │   │  ExceptionMiddleware      │   │   │  ← AppError / 422 处理器在这一层
        │   │   │   ┌──────────────────┐   │   │   │     它在你的中间件里面
        │   │   │   │   路由 → 端点      │   │   │   │
        │   │   │   └──────────────────┘   │   │   │
        │   │   └──────────────────────────┘   │   │
        │   └──────────────────────────────────┘   │
        └──────────────────────────────────────────┘
```

> **位置决定行为。**
>
> `AppError` 的处理器在**内层**，它把异常在你的中间件**之前**就转成了响应，所以中间件看到的是正常返回 → 日志正常。
>
> `Exception` 兜底处理器在**外层**，异常已经穿透了你的中间件才被接住 → 你的中间件那一半代码永远执行不到。
>
> 这不是 bug，是 ASGI 的层次结构决定的必然结果。

**那怎么彻底解决？给出方向，但明确说今天不做**：

> 两条路：
> 1. 把中间件改成 `try/finally` 结构，让日志写在 `finally` 里；
> 2. 不用 `@app.middleware`，改写成纯 ASGI 中间件，自己控制在哪一层。
>
> **这两条都要等第 5 次课**，因为它需要先讲清楚中间件的洋葱穿越顺序和 ASGI 的调用协议。今天要带走的是这个判断：
>
> **当你发现"某段代码在某些情况下不执行"，先问它在哪一层，而不是先改它的逻辑。**

〔挂欠账 → 第 5 次课：中间件顺序与 `try/finally` 改法〕

### 材料

- tag `v4-errors`（本单元结束状态）。
- **高光图 A**：五种错误格式并排 → 一种格式。左边五个 JSON，右边一个 JSON，中间一个箭头。
- **高光图 B**：洋葱层次图（上面那张），需与第 5 次课的中间件顺序图风格统一、可复用。
- **高光图 C**：两次实验的对照表——`AppError` 与 `RuntimeError` 两行，三列（响应格式 / 中间件日志 / X-Request-Id），第二行后两列打叉。
- 截图需求：实验二的终端日志（能看清 500 的栈被 `logger.exception` 记下来了，但没有 timing 那一行）。

---

## 六、分层：把第四类重复（混淆）拆开

**约 14 分钟。**

### 6.1 先看一段混在一起的代码，指出混了什么

```python
@app.post("/questions", response_model=QuestionOut, status_code=201)
def create_question(payload: QuestionCreate,
                    conn: Connection = Depends(get_conn)):
    dup = conn.execute(text("SELECT 1 FROM questions WHERE title = :t"),
                       {"t": payload.title}).fetchone()
    if dup:
        raise DuplicateTitle()
    if len(payload.body) < 10:
        raise AppError("正文太短")
    r = conn.execute(text("INSERT INTO questions (title, body, author_id) "
                          "VALUES (:t, :b, 1) RETURNING id"),
                     {"t": payload.title, "b": payload.body})
    return repo_get(conn, r.scalar())
```

提问：**这 10 行代码里有几种不同性质的事情？**

引导出四种：

| 性质 | 这里的哪一行 | 它关心什么 |
|---|---|---|
| **HTTP 相关** | 路径、方法、状态码、`response_model` | 请求怎么进来、响应怎么出去 |
| **业务规则** | "标题不能重复" | 这个领域的规矩 |
| **数据访问** | 那两条 SQL | 数据存在哪、怎么取 |
| **放错位置的校验** | `len(payload.body) < 10` | 这条应该在 schema 里 |

第四条要点名：

> `len(payload.body) < 10` 这一行是**第 3 次课就该消灭的**。它能表达为 `Field(min_length=10)`。
>
> 回收判据：**能表达为类型和约束的，不要写成 if。** 它放在这里的代价是：它不会出现在 `/openapi.json` 里，所以前端不知道这条规则，AI 生成前端表单校验时也不知道。

### 6.2 分层的划法，以及每层的判据

**这不是"一种流行的目录结构"，是对"这段代码关心什么"的分类。**

```
app/
├── main.py            组装：创建 app、注册路由与处理器、挂中间件
├── config.py          配置（单元 7）
├── deps.py            依赖：连接、分页、当前用户、资源获取
├── errors.py          异常体系
├── exception_handlers.py
├── routers/
│   └── questions.py   HTTP 边界：路径、方法、状态码、schema 绑定
├── schemas/
│   └── question.py    In/Out 模型（第 3 次课的产物）
├── services/
│   └── question.py    业务规则、编排、跨资源一致性
└── repositories/
    └── question.py    数据访问：SQL 或 ORM 查询
```

**每一层的判据（这张表才是本单元要带走的东西，请做成醒目页）**：

| 层 | 只应该出现 | **绝不应该出现** | 一句话判据 |
|---|---|---|---|
| `routers/` | 路径、方法、状态码、Depends 声明、调 service | SQL、业务分支、循环 | **超过 10 行就该怀疑** |
| `services/` | 业务规则、调多个 repo、抛 `AppError` | `Request`、`HTTPException`、SQL | **不许 import fastapi** |
| `repositories/` | 查询、映射成行/对象 | 业务判断、抛业务异常 | **只回答"数据是什么"，不判断"该不该"** |
| `schemas/` | 字段、类型、约束 | 数据库查询 | 纯声明 |

### 6.3 拆完的样子

```python
# app/repositories/question.py —— 只管数据
def find_by_title(conn, title: str) -> Row | None:
    return conn.execute(text("SELECT id FROM questions WHERE title = :t"),
                        {"t": title}).fetchone()

def insert(conn, title: str, body: str, author_id: int) -> int:
    return conn.execute(text(
        "INSERT INTO questions (title, body, author_id) "
        "VALUES (:t, :b, :a) RETURNING id"),
        {"t": title, "b": body, "a": author_id}).scalar()

def find_detail(conn, qid: int) -> Row | None: ...
```

```python
# app/services/question.py —— 只管规则，不 import fastapi
from app.errors import DuplicateTitle, QuestionNotFound
from app.repositories import question as repo

def create(conn, title: str, body: str, author_id: int) -> Row:
    if repo.find_by_title(conn, title) is not None:
        raise DuplicateTitle()
    new_id = repo.insert(conn, title, body, author_id)
    return repo.find_detail(conn, new_id)
```

```python
# app/routers/questions.py —— 只管 HTTP
@router.post("", response_model=QuestionOut, status_code=201)
def create_question(payload: QuestionCreate,
                    conn: Connection = Depends(get_conn)):
    return svc.create(conn, payload.title, payload.body, author_id=1)  # TODO: 会话
```

路由函数剩下 **2 行**。

### 6.4 依赖方向：为什么是单向的

画一张箭头图：

```
routers  ──→  services  ──→  repositories
   │              │
   └──→ schemas ←─┘            errors ← 所有层都可以用
```

**规则：箭头只能从上往下。`services` 不许 import `routers`。**

不要讲成教条，给**两个具体后果**：

**后果一（立刻发生）：循环导入。**

现场演示：在 `services/question.py` 里加一行 `from app.routers.questions import router`，启动，得到：

```
ImportError: cannot import name 'router' from partially initialized module
'app.routers.questions' (most likely due to a circular import)
```

> 这个后果是**立刻的、响亮的**。所以它其实不太危险——你一定会发现。

**后果二（延迟发生，真正危险的那个）：层次污染。**

```python
# services/question.py —— 看起来很合理，而且能跑
from fastapi import HTTPException

def create(conn, title, body, author_id):
    if repo.find_by_title(conn, title):
        raise HTTPException(status_code=409, detail="duplicate")
```

> 这段代码**能跑，测试也能过，没有任何报错**。
>
> 代价在三个月后到来：
>
> 1. **第 16 次课**你写一个定时任务导入数据，复用 `svc.create()`。它抛出 `HTTPException` —— 一个没有 HTTP 请求的进程里抛出了"HTTP 409"。这个异常没人接，任务直接崩，而且日志里的信息完全是误导性的。
> 2. **第 9 次课**你给这个 service 写单元测试。为了断言"重复标题会被拒绝"，你的测试必须 import fastapi、必须知道 409 这个数字——**业务测试被 HTTP 细节绑住了**。
> 3. 哪天要给这个功能开一个 gRPC 接口或 CLI，你得把 service 重写。
>
> **判据：`services/` 目录下，`import fastapi` 是一个错误。**
>
> 这一条是可以被机械检查的——**第 9 次课我们会在 CI 里加一条 grep，让它自动失败。** 又一次"结构性护栏"。

### 6.5 现在能回答第 3 次课的欠账了

> 第 3 次课问过：基础校验放 schema，那**"标题是否已存在"这种要查库才能判断的校验**放哪？
>
> 答案现在很清楚：**`services/`**。
>
> 判据：
> - 只看单个请求的数据就能判断 → **schema**（入口闸门）
> - 需要查询现有数据才能判断 → **service**
> - 需要判断"这个人有没有资格" → **依赖**（第 14 次课）

### 6.6 适用边界（**必须讲，否则学生会过度分层**）

> 我必须说清楚这套分层**不是无条件正确的**。
>
> 它的成本是真实的：一个 CRUD 端点要写四个文件，一次跳转变成三次跳转，新人读代码变慢。
>
> 判断标准：
>
> | 情况 | 建议 |
> |---|---|
> | 端点只是"查一下返回" | **router 直接调 repo，跳过 service**。本课程允许这样做 |
> | 有业务规则、要编排多个数据源、有事务一致性要求 | 走完整三层 |
> | 一个人的周末项目、脚本、一次性工具 | 全写在一个文件里也没问题 |
>
> 本课程要求分层，不是因为分层本身有价值，是因为**这个项目会在后面十几次课里反复被修改**——第 7 次课换 ORM、第 12 次课接前端、第 14 次课加授权、第 16 次课加定时任务。分层的回报全在"被修改"这件事上。
>
> **如果一段代码永远不会被改，给它分层是纯粹的浪费。**

---

## 七、配置外置与密钥管理

**约 8 分钟。还第 1 次课的欠账。**

### 7.1 现在的样子

```python
engine = create_engine(os.getenv("DATABASE_URL"))
SECRET = os.getenv("SECRET_KEY", "dev-secret-change-me")
DEBUG = os.getenv("DEBUG", "false") == "true"
```

第 1 次课把硬编码的连接串改成了 `os.getenv`，当时说"这只是最低要求"。现在指出它剩下的三个问题：

| 问题 | 后果 |
|---|---|
| **没有校验** | `DATABASE_URL` 忘记设置 → `os.getenv` 返回 `None` → 报错发生在第一次请求时，信息是 `NoneType has no attribute`。**启动时不报错，运行时才炸** |
| **没有类型** | 环境变量全是字符串，`DEBUG` 要手写 `== "true"`。写成 `"True"` 就静默失效 |
| **散落各处** | 要知道这个项目需要哪些配置，只能全局搜索 `getenv` |

### 7.2 pydantic-settings

```python
# app/config.py
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore")

    database_url: str                                    # ← 必填，没有默认值
    secret_key: str = Field(min_length=32)               # ← 带约束
    debug: bool = False                                  # ← 自动类型转换
    page_size_max: int = Field(default=50, ge=1, le=200)
    log_level: str = "INFO"

settings = Settings()        # ← 模块导入时执行 = 启动时校验
```

**这就是第 3 次课那两道闸门的第三个应用**（请明确点出这个呼应）：

> 第 3 次课：入口闸门校验**请求数据**，出口闸门收窄**响应数据**。
>
> 今天：同一个 Pydantic，校验**配置数据**。
>
> 三者是同一个动作：**不可信的外部输入，在进入应用之前收窄一次。** 环境变量和用户请求一样是外部输入——它同样可能缺失、类型错误、超出范围。

现场演示：把 `.env` 里的 `DATABASE_URL` 注释掉，启动：

```
pydantic_core._pydantic_core.ValidationError: 1 validation error for Settings
database_url
  Field required [type=missing]
```

> **启动即失败，错误信息直接说了缺哪个。** 这叫 fail fast。
>
> 对比之前：服务正常启动、健康检查通过、部署脚本报告成功，然后第一个用户请求进来才 500。**而那时你已经认为发布完成了。**
>
> 〔第 16 次课部署时这一条会救你一次——配置错误在启动阶段暴露，CI/CD 就能拦住，不会发到生产。〕

### 7.3 密钥永不入仓（本单元的硬性纪律）

| 文件 | 进不进 git | 内容 |
|---|---|---|
| `.env` | **绝对不进**，必须在 `.gitignore` 里 | 真实值 |
| `.env.example` | **进** | 所有键名 + 占位值 + 注释说明 |
| `config.py` | 进 | 只有 schema，**没有任何真实值** |

**三条必须讲的实践**：

1. **`.env.example` 是一份文档。** 新人 clone 之后 `cp .env.example .env`，就知道要填哪些东西。这比 README 里的文字更不容易过期。
2. **默认值不能是可用的密钥。** `secret_key: str = Field(min_length=32)` 没有默认值，所以忘了设就启动失败。**不要写 `default="dev-secret"`**——那种默认值最终一定会出现在生产环境。
3. **密钥一旦进过仓库，就等于已经泄漏。** 删掉那次 commit 不管用，git 历史里还在，fork 和克隆里也还在。**唯一的正确处置是：换掉那个密钥。**

现场演示（30 秒，很有说服力）：

```bash
git log -p --all -S "postgres://" -- . | head -40
```

在第 1 次课的历史版本里，那条硬编码的连接串**原封不动地躺在那里**，尽管当前代码早就改了。

> 第 16 次课我们会在 CI 里加一个密钥扫描，让这种 commit 压根推不上去。今天先把纪律立下来。

〔时间紧张时：这个 git 演示可改为课件静态截图 + 一句话。〕

---

## 八、横切逻辑归属判据

**约 7 分钟。这是本次课的方法论收尾，也是作业三的直接依据。**

### 8.1 问题

一段"每个请求都要做"的逻辑，有三个可以放的地方：**中间件、依赖、服务层**。怎么选？

这是学生最容易做错、也是 **AI 最容易做错**的判断。

### 8.2 判据表（本单元核心，请做成醒目页）

| 放哪 | 选它的条件 | 典型例子 | 关键限制 |
|---|---|---|---|
| **中间件** | ① 对**所有**请求生效，包括 404 和静态文件；② 需要**处理响应**（改响应头、压缩）；③ 不需要知道是哪个端点 | request-id 生成、耗时日志、CORS、GZip | **拿不到路径参数，拿不到解析后的 body，无法只对部分端点生效** |
| **依赖** | ① 只对**部分端点**生效；② 需要路径/查询参数；③ 需要**向端点提供一个值**；④ 失败时要中止请求 | 当前用户、权限检查、DB 连接、分页参数、资源取出或 404 | 不参与响应处理；对未匹配路由的请求不执行 |
| **服务层** | 它其实是**业务规则**，只是碰巧每次都要做 | 发帖前检查用户是否被禁言、扣减配额 | 不是横切逻辑，别硬塞到框架机制里 |

### 8.3 三个判断题（现场提问，每题约 40 秒）

**题一：给所有响应加 `X-Request-Id` 头。**
→ **中间件**。要改响应头，而且 404、静态文件、校验失败的请求都需要它。依赖做不到。

**题二：检查请求头里的 token，取出当前用户，端点里要用到这个用户对象。**
→ **依赖**。三个理由：要**向端点提供一个值**（`user`）；公开端点不需要它；失败时要返回 401 并中止。

写成中间件的话会怎样：得把 user 塞进 `request.state`，端点里 `request.state.user` 取——于是**它从函数签名里消失了**。签名不再说明这个端点需要登录，`/docs` 里也不会显示这是受保护端点，测试时也没有替换点。

**题三：记录每个用户对每个端点的调用次数，用于限流。**
→ **两者都要**。计数需要知道用户是谁（依赖的产物），但要对所有请求生效且要能在超限时改响应头（`Retry-After`）。

> 正确答案是"**拆开**"：中间件做计数与限流响应，用户识别做成依赖。第 16 次课会真的做一次。
>
> 这一题的价值在于：**"该放哪"有时候答案是"两个地方各放一半"**。不要因为要选一个而硬选。

### 8.4 为什么这一条是 AI 高频错误（作业三的铺垫）

> 你让 AI "加一个鉴权功能"，它有相当高的概率给你一个中间件。
>
> 原因不难理解：**Express 生态里鉴权几乎总是中间件**（`app.use(authMiddleware)`），而那是 AI 见过最多的 Web 代码。它把那个模式搬到了 FastAPI 上。
>
> 搬过来能跑吗？能。代价是什么？
> - 公开端点也被拦了，于是代码里出现一个白名单路径数组，**一个硬编码的字符串列表**；
> - `user` 从签名里消失，改藏在 `request.state`；
> - `/docs` 不再标注哪些端点需要认证；
> - 第 9 次课写测试时没有替换点，只能起整个服务。
>
> 这是第 2 次课"已失效的老优化"的同一类问题：**AI 给的不是错的代码，是在别的前提下正确的代码。** 判断前提是不是你的前提，是你的工作。
>
> 〔第 14 次课会正式做认证依赖，届时会回到这一页。〕

---

## 九、C 档结论卡

**约 3 分钟，明确说"课后查阅"。时间不够整体跳过。**

### 9.1 IoC 容器跨栈对照

| 能力 | FastAPI | Spring | .NET | Angular | NestJS | Django |
|---|---|---|---|---|---|---|
| 依赖声明 | 函数签名 + `Depends` | `@Autowired` / 构造器 | 构造器注入 | 构造器 + `@Injectable` | 构造器 + `@Injectable` | 无内建 DI |
| 生命周期 | 请求级（默认缓存） | singleton/prototype/request | singleton/scoped/transient | 模块级 | 模块级 | — |
| 覆盖替换 | `dependency_overrides` | `@MockBean` | 替换注册 | `TestBed.overrideProvider` | 覆盖 provider | 手工 monkeypatch |

> 结论：**"声明需要什么，由容器准备好，测试时可替换"是跨栈通用结构。** FastAPI 的特别之处只是它借用了函数签名和类型标注来做声明，没有单独的容器配置。
>
> `dependency_overrides` 这一格是第 9 次课的关键，届时会回到这张表。

### 9.2 DI 的代价（**不要跳过这一段，它是取舍训练**）

| 收益 | 代价 |
|---|---|
| 消除重复；清理有保证 | **隐式性**：函数签名看不出实际执行了多少代码 |
| 测试时可替换 | **调试链变长**：一个请求要穿过多层依赖才到你的代码 |
| 需求是"我要什么"而非"怎么造" | **依赖树错误的报错难读**，尤其是循环依赖 |

> 判据：**依赖的价值与"它被复用的次数"成正比。只用一次的依赖，往往就该是一个普通函数调用。**

### 9.3 RFC 9457 problem+json 全套

| 字段 | 含义 |
|---|---|
| `type` | 错误类型的 URI（应可访问，返回该类型的文档） |
| `title` | 人类可读的简短摘要，同一 `type` 下应一致 |
| `status` | HTTP 状态码（与响应状态码一致） |
| `detail` | 本次出现的具体说明 |
| `instance` | 本次问题的 URI |
| 扩展字段 | 可自由添加，如 `errors`、`trace_id` |

`Content-Type: application/problem+json`。对外开放 API 时优先考虑它。

### 9.4 一句话结论卡

| 问题 | 结论 | 展开处 |
|---|---|---|
| `Depends` 能不能用在 WebSocket | 能 | 本课程不涉及 |
| 依赖能不能是 class | 能，实现 `__call__` 或用 `Depends(MyClass)` | 第 14 次课会用一次 |
| 中间件顺序怎么定 | 注册顺序 = 洋葱层序 | **第 5 次课** |
| `lifespan` 与启动/关闭钩子 | 用来管进程级资源（连接池、模型加载） | **第 7、16 次课** |

---

## 十、作业与欠账登记

**约 5 分钟。**

### 作业一：消除项目全部重复（主线，交付重构后的项目）

对第 3 次课的六个端点做完整重构，硬性要求：

1. **零处** `engine.connect()` 出现在 `routers/` 中；
2. **零处** `try/except Exception` 出现在 `routers/` 中；
3. **零处** `commit()` 出现在 `routers/` 和 `services/` 中；
4. 分页参数**只有一个**定义处，上限只在一行；
5. 所有错误响应格式统一为 `code/message/detail/request_id`，**包括 422**；
6. `services/` 下 `grep -r "import fastapi"` **结果为空**；
7. 目录结构符合单元 6.2；
8. 配置改用 pydantic-settings，`.env` 在 `.gitignore` 中，`.env.example` 已提交；
9. 每个路由函数**不超过 10 行**（超过的要在提交说明里解释为什么）。

提供自检脚本 `scripts/check_layering.sh`（课程提供），跑通再提交。

> **注意**：这个脚本就是第 9 次课要进 CI 的东西的雏形。今天你手工跑，第 9 次课让机器在每次 push 时跑。

### 作业二：before/after 变更成本对照表（**核心作业，必交**）

对下面三个需求，分别统计重构前后需要改动的**文件数**和**位置数**，并各附一句话说明：

| 需求 | 重构前文件/位置 | 重构后文件/位置 | 为什么变了 |
|---|---|---|---|
| 分页上限 50 → 30 | | | |
| 所有错误响应增加 `timestamp` 字段 | | | |
| 数据库从直接连接改为连接池 + 显式 Session | | | |

第三行特别说明：**不需要真的实现它**，只需要回答"要改哪些文件"。这是第 7 次课的预演——那次课我们会真的做，然后**验证你今天的答案对不对**。

### 作业三：一处"AI 写成中间件但应为依赖"的判断说明（**本次课的课程主题作业**）

**步骤**：

1. 向 AI 提出这个需求（原样使用，请把提示词抄进作业）：
   > 给我的 FastAPI 项目加上鉴权：请求头里带 `Authorization: Bearer <token>`，校验后把当前用户放进上下文，端点里能拿到。公开端点 `/healthz` 和 `GET /questions` 不需要认证。

2. **原样保存** AI 的输出（不要修改，作为作业附件）。

3. 填这张判断表：

| 问题 | 你的回答 |
|---|---|
| AI 给的是中间件还是依赖？ | |
| 它如何处理"公开端点"？（引用具体代码行） | |
| 端点里怎么拿到 user？签名里看得出来吗？ | |
| `/docs` 里能看出哪些端点需要认证吗？ | |
| 按单元 8.2 的判据，它应该是什么？**引用判据表里的具体条件** | |
| 如果照 AI 的方案做，第 9 次课写单元测试时会遇到什么困难？ | |

4. 写出你的改法（**只写签名和 20 行以内的骨架，不要求实现完整认证**）。

**评分重点不是改对，是第 5、6 两问**——能不能引用判据说明理由，能不能预判延迟出现的代价。

### 本次课新增的欠账登记

| 欠账 | 何时还 |
|---|---|
| 中间件在未预期异常下失灵（只修了一半） | **第 5 次课** |
| 中间件注册顺序与洋葱穿越 | **第 5 次课** |
| `def` 还是 `async def`——依赖和端点都要选 | **第 5 次课** |
| `Connection` → `Session`，事务边界完整讨论 | **第 7 次课** |
| `get_owned_question`：授权挂在依赖上 | **第 14 次课** |
| `dependency_overrides` 在测试中替换依赖 | **第 9 次课** |
| 分层检查脚本进 CI | **第 9 次课** |
| 密钥扫描进 CI | **第 16 次课** |
| 限流：中间件 + 依赖各一半 | **第 16 次课** |
| `lifespan` 管连接池 | 第 7、16 次课 |
| 对外 API 是否改用 RFC 9457 | 第 8 次课 |

---

## 十一、素材清单与制作说明

### 必需素材

| 素材 | 说明 |
|---|---|
| tag `v4-flat` | 起始版 = 第 3 次课交付状态。**必须是"合格但扁平"的代码**，不是烂代码。约 230 行单文件 |
| tag `v4-deps` | 单元 3、4 结束状态 |
| tag `v4-errors` | 单元 5 结束状态 |
| tag `v4-layered` | 本次课最终状态，即作业一的参考答案 |
| `app/dump_deps.py` | 打印依赖树脚本（B 档） |
| `scripts/check_layering.sh` | 九条硬性要求的自检脚本，**同时是第 9 次课 CI 的雏形**，请与第 9 次课统一设计 |
| `.env.example` | 含全部键名 + 注释 |
| **高光图 A**：变更成本 before/after | 两列表格：需求 × (改动文件数, 位置数)。**整节课的说服力来源，请做成封面级** |
| **高光图 B**：洋葱层次图 | `ServerErrorMiddleware / 你的中间件 / ExceptionMiddleware / 端点` 四层，标注两类处理器各在哪层。**需与第 5 次课复用** |
| **高光图 C**：五种错误格式 → 一种 | 左五右一 + 箭头 |
| **高光图 D**：两次实验对照表 | `AppError` vs `RuntimeError`，三列，第二行后两列打叉 |
| 图 E：分层与依赖方向箭头图 | 需与第 3 次课"两道闸门"图叠加对照——**闸门在 routers 层，service 在闸门之间** |
| 表 F：四层职责判据表 | 纯表格，作业一的评分依据 |
| 表 G：横切逻辑归属判据表 | 纯表格，作业三的评分依据 |
| 截图：循环导入报错 | 完整 `ImportError` 信息 |
| 截图：配置缺失的启动失败 | 完整 `ValidationError` |
| 截图：`git log -S` 找出历史中的密钥 | 需能看清连接串仍在历史里 |

### 可后补

- 依赖树打印输出（文字即可）。
- IoC 跨栈对照表、RFC 9457 字段表（纯文字）。

### 备用材料

| 风险 | 备用方案 |
|---|---|
| 单元 5.5 两次实验在学生环境表现不一致（中间件写法差异） | 固定使用 tag `v4-errors` 的中间件代码；准备 60 秒预录对照录像 |
| 现场调用 AI（作业三演示）失败或输出过长 | 准备一份预先生成并验证的"中间件版鉴权"输出作为讲评素材，标注"预录产物" |
| 重构步骤过多导致现场卡住 | 每个单元结束都有对应 tag，**允许 `git checkout` 跳到下一步继续**，不要现场逐行敲完 |
| 学生 pydantic-settings 未安装 | Week 0 环境清单已含；备用方案是用 `BaseModel` + 手工读 `os.environ` 演示同一原理 |

### 环境与运行条件

延用前序环境（Python 3.12 / FastAPI / Pydantic v2 / pydantic-settings / SQLAlchemy 2.x / PostgreSQL 16+）。

**演示开始时的初始状态**：数据库已 seed；工作区在 tag `v4-flat`；`.env` 已配置好；服务已启动；浏览器停在 `/docs`。

**复位方式**：`git checkout v4-flat -- app/ && make reset-db`。

---

## 十二、与前后课的衔接

**本次课回收的前序埋点**：

| 来源 | 埋点 | 回收位置 |
|---|---|---|
| 第 1 次课 | 中间件在异常路径下失灵 | 单元 5.5（修一半，另一半留给第 5 次课） |
| 第 1 次课 | request-id 只在响应头和日志里，用户看不到 | 单元 5.2（进错误响应体） |
| 第 1 次课 | 密钥只做了 `os.getenv`，"这只是最低要求" | 单元 7 |
| 第 3 次课 | 422 格式与统一契约不一致 | 单元 5.4 |
| 第 3 次课 | `conn.commit()` 散落 | 单元 3.4 |
| 第 3 次课 | 查库才能判断的校验放哪 | 单元 6.5 |
| 第 3 次课 | "能表达为约束的不要写成 if" | 单元 4.1、6.1 |
| 第 3 次课 | 两道闸门 | 单元 6.2（闸门之间的分层）、单元 7（配置也是闸门） |
| 第 3 次课 | "结构性护栏" | 单元 6.4（分层检查可机械化） |
| 第 2 次课 | 沉默的成本 | 单元 2.3（漏改一处不报错） |
| 第 2 次课 | AI 给的是"在别的前提下正确的代码" | 单元 8.4 |

**本次课埋下、后面必须回引的四处**（请在课件中明显标记）：

- **单元 5.5 洋葱图** → 第 5 次课开场直接接这张图，讲中间件顺序并把另一半修好；
- **单元 4.3 `get_question_or_404`** → 第 14 次课在这个函数里加授权，变成 `get_owned_question`；
- **单元 6.4 "services 不许 import fastapi"** → 第 9 次课写成 CI 检查；
- **作业二第三行（连接改连接池）** → 第 7 次课真的做一次，验证今天的预判。

**本次课不承担、请勿提前引入**：中间件的洋葱穿越顺序与编写细节（第 5 次课）、`async def` 与并发模型（第 5 次课）、ORM 与 Session（第 7 次课）、测试与 `dependency_overrides`（第 9 次课）、认证的具体实现（第 14 次课）。

**特别提示**：本次课的所有端点仍然是 `def`（同步），依赖也是同步的。**这是有意的**——第 5 次课要在这个基础上做"`async def` 里放阻塞调用导致并发崩塌"的定量实验，需要一个干净的同步基线做对照。