# 第 3 次课教学底稿（修订版）
## 框架机制 I：路由、参数校验与响应模型

---

## 〇、给 PPT 制作团队的全局说明

本次课 95 分钟，留 5 分钟缓冲。前两次课站在**链路整体**看问题；本次课把第 1 次课链路图里的一个环节——「路由与参数解析」——**放大来看**，把框架的"魔法"拆成可以打印出来、可以下断点、可以逐字段验证的东西。

**本次课的主线是一个心智模型，请贯穿全课**：应用有**两道闸门**——进来的数据在入口收窄一次，出去的数据在出口收窄一次。两道闸门之间的代码，才配假设自己拿到的是干净的、类型正确的对象。学生现在的状态是两道闸门**一道都没有**，所以业务代码里全是 `if not title`、`str(row["id"])` 这类补丁。

**课堂与课后边界**：
- **课堂完成**：路由打印、校验演示、泄漏复现（单元 5、6、8）
- **课后自学**：三类参数完整对照（单元 4）、OpenAPI 完整说明（单元 7）、跨框架对照（单元 9）、B 档边界输入实验

**本次课的课程主题落点（请在收尾明确点出）**：`response_model` 是本课程出现的**第一道"结构性护栏"**——它不依赖人去审查，即使 AI 写错了查询、返回了不该返回的字段，它也能兜住。这与第 0 次课说的"靠机器把关"直接接上，也是第 9 次课 CI 门禁的先声。

**最难讲清、优先制作的三处**：

1. **「你的函数根本没有被调用」（单元 5）**。学生对"校验发生在什么时候"没有概念，讲多少遍都不如现场下一个断点让它**不命中**。这一段请配调试器截图，并与第 1 次课的调用栈图呼应。
2. **密码哈希泄漏的复现与修复（单元 6）**。这是本次课的现场必做，也是第 0 次课那道找错题的正式回收。两个响应体必须**同屏对照、泄漏字段高亮**。
3. **契约先行的小循环（单元 8）**。注意：第 0 次课已经做过"两个提示词对比"，**本次课不要重复那个形式**。这里做的是完整循环——先写 schema → 让 AI 只填实现 → 用 schema 当验收判据。请在课件上标明它与第 0 次课那个演示的区别。

**若时间不够的压缩顺序**：先压单元 9 的跨栈对照表（改为课后自读）→ 再压单元 4 中与第 2 次课重复的报文对照部分（第 2 次课已详细做过四种编码，这里只需一句话指回去）→ 再把 B 档边界输入实验整体移到课后。**单元 5、6、8 不能压缩。**

**一个需要教师裁决的地方（请在审读时确认）**：第 2 次课给的判据是"400 = 请求没法解析，422 = 能解析但内容不合法"，但 FastAPI **默认把 JSON 语法错误也归为 422**。本底稿单元 5 选择了"如实指出这个不一致，并挂为第 4 次课的欠账"，而不是回避。如果你希望改为在本次课就修正，请告知，这会增加约 4 分钟。

**response_model 边界说明**：
- 普通数据返回路径（返回 dict、ORM 对象等）执行模型校验和序列化
- 直接返回 `JSONResponse` 或 `Response` 会绕过该过程
- 这不是"已校验对象就安全"的保证，而是"业务 JSON 响应必须受明确出口契约约束"

---

## 一、开场：把链路图的一个环节放大

**约 4 分钟。**

内容：

把第 1 次课的请求全链路图重新放上来，**高亮「路由与参数解析」这一格**。

前两次课我们知道了这一格由框架负责，出问题的表现是 404 和 422。但"框架负责"这四个字，现在对你们来说还是一个黑盒。今天要做的事就一句话：**把这个黑盒打开，看看里面是什么数据结构。**

本次课结束时你应当能回答：

- `@app.get("/questions")` 这一行执行之后，程序里**多了一个什么东西**？它存在哪？
- 一个请求进来，框架**怎么决定**调用你写的哪个函数？
- `/questions/latest` 返回 422，为什么？（这个现象今天会现场制造出来）
- 校验在什么时候发生？**发生在你的函数被调用之前还是之后？**
- 为什么 `SELECT *` 直接返回会泄漏密码哈希，而加一行 `response_model=` 就能堵住？

讲：

> 我特别想让你们摆脱一种状态：把框架当成一个"你按规则写它就工作"的东西。只要它是黑盒，你遇到诡异现象就只能搜索、试错、问 AI，而 AI 给你的也往往是"再试试这样写"。
>
> 今天之后，`app.routes` 对你来说是一个**可以 print 出来的 list**，校验是一个**可以下断点观察的时刻**。这就是"驾驭"和"使用"的区别。

---

## 二、解剖台：三个 bug，一个比一个隐蔽

**约 12 分钟。**

### 情境设定

> 这是你的项目现在的样子（第 2 次课作业之后）。AI 帮你补了几个端点。你测了一圈，看起来都对。
>
> 然后：
> 第一，你加了一个"最新问题"端点 `/questions/latest`，浏览器打开，返回 **422**，错误信息说 `qid` 不是整数。可你这个端点**根本没有 qid 参数**。
> 第二，有人发了一条标题只有一个空格的问题，进库了；有人发了一条正文 50 万字的，也进库了。
> 第三，这一条最安静：**什么都没发生。**

### 代码（tag: `v3-ai-endpoints`，可运行，教学反例，已验证三个问题均可稳定复现）

```python
# app/main.py —— AI 补出来的端点，可运行，用于解剖
from fastapi import FastAPI, Request
from sqlalchemy import create_engine, text
import os

app = FastAPI()
engine = create_engine(os.getenv("DATABASE_URL"))

@app.get("/questions")
def list_questions(keyword: str = "", page: int = 1):
    with engine.connect() as conn:
        rows = conn.execute(
            text("SELECT * FROM questions WHERE title ILIKE :kw "
                 "ORDER BY id DESC LIMIT 20 OFFSET :off"),
            {"kw": f"%{keyword}%", "off": (page - 1) * 20},
        ).fetchall()
    return {"items": [dict(r._mapping) for r in rows]}

@app.get("/questions/{qid}")
def get_question(qid: int):
    with engine.connect() as conn:
        row = conn.execute(
            text("SELECT q.*, u.* FROM questions q "
                 "JOIN users u ON u.id = q.author_id WHERE q.id = :qid"),
            {"qid": qid},
        ).fetchone()
    if row is None:
        return {"code": "question_not_found"}
    return dict(row._mapping)

@app.get("/questions/latest")
def latest_question():
    with engine.connect() as conn:
        row = conn.execute(
            text("SELECT * FROM questions ORDER BY created_at DESC LIMIT 1")
        ).fetchone()
    return dict(row._mapping)

@app.post("/questions")
async def create_question(request: Request):
    payload = await request.json()
    with engine.connect() as conn:
        r = conn.execute(
            text("INSERT INTO questions (title, body, author_id) "
                 "VALUES (:t, :b, :a) RETURNING id"),
            {"t": payload["title"], "b": payload["body"], "a": payload["author_id"]},
        )
        conn.commit()
    return {"success": True, "id": r.scalar()}
```

### 现场演示顺序

**第一个：`/questions/latest` 返回 422**

```json
{"detail":[{"type":"int_parsing","loc":["path","qid"],
 "msg":"Input should be a valid integer, unable to parse string as an integer",
 "input":"latest"}]}
```

提问：**这个错误是哪个端点返回的？**

学生会困惑：`latest_question` 没有 `qid`。让他们盯住 `loc: ["path","qid"]` 这一行——**这是 `get_question` 报出来的**。也就是说，请求被送进了错误的函数。原因在单元 3 揭晓。

> 这里请注意一件事：这个报错**不是无用信息**，它把真相写在 `loc` 里了，只是你还不知道怎么读。第 5 单元会教怎么读 422。

**第二个：不校验直接入库**

用 `/docs` 或 curl 发三条：

```bash
# 空白标题
curl -X POST localhost:8000/questions -H 'Content-Type: application/json' \
  -d '{"title":" ","body":"x","author_id":1}'
# 超长正文（省略）
# 篡改作者
curl -X POST localhost:8000/questions -H 'Content-Type: application/json' \
  -d '{"title":"正常标题","body":"正常内容","author_id":99}'
```

全部成功入库。第三条尤其值得停一下：**客户端自己决定了这条问题的作者是谁。** 今天先记一笔，第 14 次课会把它上升为一类漏洞。

再发一条缺字段的：

```bash
curl -X POST localhost:8000/questions -H 'Content-Type: application/json' -d '{"title":"x"}'
```

得到 **500**，日志里是 `KeyError: 'body'`。

> 注意这个状态码。用户发了一个不合法的请求，我们却告诉他"服务器出错了"。**这是把 4xx 的问题报成了 5xx。** 回收第 2 次课的判据：4xx 是"你错了，原样重试没意义"，5xx 是"我错了，重试可能有用"。现在客户端会傻乎乎地一直重试。

**第三个：什么都没发生（本单元的重点）**

打开 `/questions/1`，看响应体：

```json
{
  "id": 1, "title": "React 怎么学", "body": "...", "author_id": 3,
  "created_at": "2025-03-01T10:00:00",
  "email": "alice@example.com",
  "password_hash": "$2b$12$Kx9vQ...",
  "is_admin": true,
  "last_login_ip": "10.0.3.17"
}
```

**停在这里，让它在屏幕上待够时间。**

> 这个接口是"正常的"。它返回 200，前端拿到了需要的 title 和 body，页面渲染正确，没有任何报错，没有任何测试会失败。
>
> 它同时把全站每一个问题作者的**邮箱、密码哈希、管理员标记、登录 IP**，公开给了任何一个会打开浏览器的人。
>
> 这是第 2 次课说的"沉默的成本"的极端版本：**代价不是延迟出现，是根本不出现，直到有人来收。**

补一句回收：

> 第 0 次课那道"10 分钟找错"里，第 3 条就是这个——"返回整个 author 对象"。当时我说它对应第 3 次课。今天就是。

### 欠账清单（接住但不展开）

| 发现的问题 | 本次课处理 | 何时还 |
|---|---|---|
| 路由顺序导致误匹配 | **单元 3 回收** | — |
| 无入参校验 / 缺字段报 500 | **单元 5 回收** | — |
| `SELECT *` 全列返回导致泄漏 | **单元 6 回收** | — |
| 客户端自己指定 `author_id` | 今天用 schema 挡住一半 | 第 14 次课（作者应取自会话） |
| `conn.commit()` 散落在端点里 | 记一笔 | 第 7 次课（事务边界） |
| 数据库连接每次现开 | 记一笔 | 第 4 次课（依赖注入） |
| 404 场景返回了 200 | 第 2 次课已判过，今天作业修 | — |
| 分页无稳定排序 | 记一笔 | 第 6、8 次课 |

---

## 三、现场必做 A：装饰器执行完，程序里多了什么

**约 11 分钟。本次课第一个现场必做。**

### 3.1 先回收 Week 0 那道题

Week 0 的 Python 必做练习是这段：

```python
ROUTES = {}

def route(path):
    def decorator(func):
        ROUTES[path] = func
        return func
    return decorator

@route("/hello")
def hello():
    return "hi"
```

当时要求你回答三件事：`ROUTES` 里存了什么、装饰器什么时候执行、不写 `return func` 会怎样。

现在揭晓：**FastAPI 做的就是这件事。** `@app.get("/questions")` 在**模块被导入的那一刻**执行，把你的函数登记进 `app` 内部的一个列表。所谓"框架自动帮你路由"，就是它在这个列表里找。

### 3.2 打印出来看

现场加一段，重启：

```python
# 放在所有路由定义之后
for r in app.routes:
    print(f"{type(r).__name__:12} {getattr(r, 'methods', '-')!s:12} {r.path}")
```

输出（节选）：

```
Route        -            /openapi.json
Route        -            /docs
Route        -            /redoc
APIRoute     {'GET'}      /questions
APIRoute     {'GET'}      /questions/{qid}
APIRoute     {'GET'}      /questions/latest
APIRoute     {'POST'}     /questions
```

两个立刻要说的观察：

1. **`/docs` 和 `/openapi.json` 也在这个列表里。** 它们不是什么特殊机制，就是框架替你注册的两个普通路由。第 1 次课我说"`/docs` 从哪来，第 3 次课讲"——就是这里。
2. **列表是有顺序的，顺序就是你写代码的顺序。**

再打印一个路由对象的内部：

```python
r = app.routes[4]          # /questions/{qid}
print(r.path)              # /questions/{qid}
print(r.path_regex)        # re.compile('^/questions/(?P<qid>[^/]+)$')
print(r.endpoint)          # <function get_question at 0x...>
print(r.response_model)    # None      ← 今天后半节课的主角
```

### 3.3 匹配规则，以及 bug 的成因

> **路由匹配 = 按注册顺序，逐个用正则去试，第一个匹配上的胜出。**

把 `/questions/latest` 这个请求代入：

| 顺序 | 路由 | 正则 | 匹配？ |
|---|---|---|---|
| 1 | `/questions` | `^/questions$` | ✗ |
| 2 | `/questions/{qid}` | `^/questions/(?P<qid>[^/]+)$` | **✓ 命中，qid = "latest"** |
| 3 | `/questions/latest` | `^/questions/latest$` | 轮不到它 |

命中之后，框架把字符串 `"latest"` 交给参数校验，试图转成你声明的 `qid: int`，转不成 → 422。

**这就是那个"没有 qid 的端点报 qid 错误"的全部真相。**

请特别指出正则里的 `[^/]+`：**路径参数默认匹配"除斜杠外的任何字符"**，它不知道你想要整数。类型是在下一个环节（校验）才起作用的。

### 3.4 回答"为什么是 list 不是 dict"

提问（值得停 20 秒）：Week 0 那个原型用的是 `dict`，查找是 O(1)，为什么框架要用 list 逐个试？

答：因为要支持**路径参数**。`dict` 只能做精确匹配，`/questions/7`、`/questions/8`、`/questions/999` 是无穷多个 key，没法预先放进 dict。所以只能存成"模式 + 正则"，逐个匹配。

> 顺带一个真实世界的推论：**路由表很长时，匹配是有成本的**。大型框架会做前缀树等优化，但"有顺序、逐个试"这个模型不变。

### 3.5 修复

把静态路径移到动态路径**之前**：

```python
@app.get("/questions")          # 1
@app.get("/questions/latest")   # 2  ← 提到前面
@app.get("/questions/{qid}")    # 3
```

重新打印 `app.routes` 确认顺序变了，再访问 `/questions/latest`，正常返回。

**给一条可执行的判据**（做成醒目页）：

> **具体路径写在参数路径前面。** 更一般地说：**越具体的路由越靠前。**
>
> 这条规则在所有"按顺序匹配"的框架里都成立——Express、Flask、Django 的 urlpatterns 都一样。它不是 FastAPI 的特性，是这类路由机制的性质。

〔C 档补充，不在主线讲：Starlette 支持路径转换器 `{qid:int}`，它会把正则收紧成 `\d+`，于是 `/questions/latest` 压根匹配不上这条路由，直接落到下一条。这是另一种修法，但 FastAPI 生态里更常见的还是调顺序，因为类型已经由函数签名声明了。〕

### 讲

> 今天这一段没教你任何新 API。我教的是一个动作：**当框架的行为让你困惑时，把它的内部状态打印出来。**
>
> 这个动作能用在很多地方——第 4 次课我们会打印依赖树，第 7 次课会打印 ORM 实际发出的 SQL。都是同一件事：**不要对着黑盒猜，把它变成可观察的数据结构。** 这也是第 1 次课"可观察性"那条线的延续。

### 材料

- 演示仓库 tag `v3-ai-endpoints`，`app/dump_routes.py` 提供打印脚本（避免现场手敲出错）。
- 截图需求：`app.routes` 打印输出全文（终端截图，**需完整可读**）；以及一个 `APIRoute` 对象四个属性的打印结果。

---

## 四、三类参数：它们各自从报文的哪个部分来

**约 10 分钟。这一单元与第 2 次课的报文对照有衔接，若时间紧可压缩到 6 分钟。**

### 内容

第 2 次课我们看过：同一份数据可以放在查询串里，也可以放在请求体里，编码还分好几种。今天把它和函数签名对上。

**核心对照表**（请与第 2 次课的四种报文图并排，做成一页）

| 参数来源 | 在报文的哪里 | FastAPI 写法 | 什么时候用 |
|---|---|---|---|
| **路径参数** | 请求行的 URL 路径段 | 函数参数名与 `{}` 中的名字一致 | **定位唯一资源**：`/questions/7` |
| **查询参数** | 请求行 URL 的 `?` 之后 | 声明为标量且不在路径中 | **修饰查询**：筛选、排序、分页 |
| **请求体** | 请求体（`Content-Type` 决定编码） | 声明类型为 Pydantic 模型 | **提交数据**：创建、更新 |
| 请求头 | 请求头 | `Header(...)` | 元信息、认证凭据 |
| Cookie | `Cookie` 请求头 | `Cookie(...)` | 会话 —— 第 14 次课 |

### FastAPI 的判定规则（这是学生最容易糊涂的地方，请单独成页）

框架看你的函数签名，按这个顺序判定每个参数：

1. 参数名出现在路径模板的 `{}` 里 → **路径参数**
2. 类型是 Pydantic 模型 → **请求体**
3. 其余标量类型（int / str / bool / float …）→ **查询参数**

```python
@app.get("/questions/{qid}/answers")
def list_answers(
    qid: int,                       # 1 → 路径参数
    page: int = 1,                  # 3 → 查询参数
    sort: str = "new",              # 3 → 查询参数
):
```

```python
@app.post("/questions/{qid}/answers")
def create_answer(
    qid: int,                       # 1 → 路径参数
    payload: AnswerCreate,          # 2 → 请求体
    notify: bool = False,           # 3 → 查询参数
):
```

**要现场演示一次的点**：在 `/docs` 里打开这两个端点，看框架把参数分到了 Parameters 区还是 Request body 区。**框架对你签名的理解，是可以直接看到的**，不用猜。

### 两个坑

**坑一：查询参数全都是字符串。** `?page=2` 传过来的是 `"2"`，是 Pydantic 把它转成了 `2`。所以 `?page=abc` 会得到 422 而不是崩溃——**这是校验在替你工作**。

**坑二：`?flag=false` 会变成 `False`。** Pydantic 在宽松模式下把 `"false"`、`"0"`、`"no"` 都识别为 `False`。这方便，但**不要依赖它**——不同框架、不同语言的规则不一样，边界情况写清楚更安全。

### 欠账

> HTML 原生表单提交的是 `application/x-www-form-urlencoded`，**不是 JSON**，FastAPI 要用 `Form(...)` 接。这是两条不同的解析路径，第 2 次课埋过这一笔，**第 5 次课做表单闭环时正式处理**。今天的所有请求体都按 JSON 处理。

---

## 五、入口闸门：校验发生在你的函数被调用之前

**约 15 分钟。含本次课第一个关键演示。**

### 5.1 给参数装上约束

把 `create_question` 改掉：

```python
from pydantic import BaseModel, Field, ConfigDict, field_validator

class QuestionCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")      # ← 多传字段直接拒绝

    title: str = Field(min_length=5, max_length=200)
    body: str  = Field(min_length=10, max_length=20000)
    tags: list[str] = Field(default_factory=list, max_length=5)

    @field_validator("title")
    @classmethod
    def title_not_blank(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("标题不能为空白")
        return v                                    # ← 校验器可以顺便清洗


@app.post("/questions", status_code=201)
def create_question(payload: QuestionCreate):
    ...
```

三个要讲出来的设计点：

1. **`extra="forbid"` 不是洁癖。** 默认情况下 Pydantic 会**静默忽略**多余字段。也就是说客户端多传一个 `author_id` 或 `is_admin`，你不会知道。开着 forbid，多传就是 422。〔这条在第 14 次课会重新出现，那时它有个名字叫 mass assignment〕
2. **校验器可以顺便清洗**（这里 `strip()` 后返回）。入口闸门不只是"判断是否合法"，也是"规整成内部想要的形状"。
3. **`status_code=201`**：创建成功应当是 201，不是 200。回收第 2 次课。

### 5.2 现场必做：证明校验发生在函数之前

**这一段是本单元的核心，请配调试器截图。**

在 `create_question` 函数体的**第一行**下断点。然后发一个非法请求：

```bash
curl -X POST localhost:8000/questions -H 'Content-Type: application/json' -d '{"title":"x"}'
```

结果：**断点没有命中**，客户端直接收到 422。

再发一个合法请求：断点命中，此时看 Variables 面板——`payload` 是一个 `QuestionCreate` 对象，`payload.title` 已经是 strip 过的字符串。

结论（醒目页）：

> **校验不通过时，你的函数根本没有被调用。**
>
> 所以在第 1 次课那张链路图上，入口闸门的位置是在「路由与参数解析」这一格里，**在「应用代码」这一格之前**。
>
> 推论：**你的业务代码不需要再写基础校验。** 如果你在函数里看到 `if not title: raise ...`，说明有个约束写错了地方。

追加一条判据：

> **能表达为类型和约束的，就不要写成 if。**
>
> 适用边界（请保留）：跨字段的规则（"结束时间必须晚于开始时间"）用 `model_validator` 仍属于 schema 层；**需要查数据库才能判断的规则**（"标题是否已存在"）不属于 schema，它是业务逻辑，第 4 次课分层时会给它安排位置。

### 5.3 读懂 422

这是第 1 次课留的作业之一——"说出 422 是谁生成的、在链路哪个环节产生"。现在可以完整回答，并且要会**读**它。

```json
{
  "detail": [
    {
      "type": "string_too_short",
      "loc": ["body", "title"],
      "msg": "String should have at least 5 characters",
      "input": "x"
    },
    {
      "type": "missing",
      "loc": ["body", "body"],
      "msg": "Field required",
      "input": {"title": "x"}
    }
  ]
}
```

**读法（做成一页）**：

| 字段 | 怎么用 |
|---|---|
| `loc[0]` | **告诉你错误来自报文的哪个部分**：`body` / `query` / `path` / `header` / `cookie` |
| `loc[1:]` | 字段路径，嵌套模型时是多级，数组时含下标（如 `["body","tags",2]`） |
| `type` | 机器可读的错误种类，**前端应该拿它做分支**，而不是去匹配 `msg` 的文字 |
| `msg` | 给人看的英文说明，**会随版本变化，不要依赖它做逻辑判断** |
| `detail` 是**数组** | 一次会报出**所有**错误，不是只报第一个——这对表单回填很重要 |

回头看单元 2 那个诡异的 422：`loc: ["path","qid"]` 早就把真相写清楚了——错误来自 **path**，字段是 **qid**。当时不会读，现在会了。

### 5.4 一个必须如实说明的不一致

第 2 次课给过判据：**400 = 请求没法解析，422 = 能解析但内容不合法。**

现场发一个 JSON 语法坏掉的请求：

```bash
curl -X POST localhost:8000/questions -H 'Content-Type: application/json' -d '{"title": '
```

FastAPI 返回的是 **422**（`type: "json_invalid"`），不是 400。

> 这和我们上次讲的判据对不上。怎么办？
>
> 三件事要说清楚：
> 1. **422 本身就不在最初的 HTTP 规范里**，它来自 WebDAV，被 API 圈广泛借用。很多团队对所有客户端输入错误一律返回 400，这也是合理的。
> 2. **框架的默认行为不等于你必须接受的行为。** FastAPI 允许你替换默认的校验异常处理器。
> 3. **本课程的选择**：第 4 次课建立统一错误契约时，会把校验错误改写成课程约定的格式；第 8 次课设计 API 契约时再决定对外用 400 还是 422。今天先如实记下这个不一致。

〔挂欠账 → 第 4 次课改写默认 422〕

讲：

> 我特意把这个不一致摆出来，不是为了挑框架的刺。是想让你们习惯一件事：**判据和实现经常对不上。** 这时候正确的反应不是"那判据是不是错的"，而是"判据说明了应该怎样，实现说明了默认怎样，我决定采用哪个，并在文档里写清楚"。
>
> 这门课后面会遇到很多这种情况。能做出决定并说明理由，就是第 0 次课说的第五项能力：方案取舍。

### 5.5 B 档：五组边界输入（课堂留 3 分钟起个头，其余课后）

给一个设计方法，而不是给一份题目：

> 对每一个字段，找这五类输入：
> ① 缺失 / null ② 下界与下界减一 ③ 上界与上界加一 ④ 类型错误 ⑤ 多余字段与非法组合

以 `QuestionCreate` 为例，在 `/docs` 里逐个发，**记录实际返回的 `loc` 与 `type`**，填成一张表。作业里要交。

---

## 六、现场必做 B：出口闸门——密码哈希是怎么消失的

**约 16 分钟。本次课高光，必须现场做，不能只看截图。**

### 6.1 复现

回到 `/questions/1`，把那个泄漏的响应体再调出来，**这次把 `password_hash`、`email`、`is_admin`、`last_login_ip` 四行高亮**。

追问一句：

> 这段代码错在哪一行？

学生通常会说 `SELECT q.*, u.*`。对，但**只对一半**。

> 真正的问题是：**这个端点没有声明它承诺返回什么。** 它返回的内容完全由查询语句决定。今天是 `SELECT *`，明天有人给 users 表加一列 `id_card_no`，这个接口就自动把身份证号也发出去了——**没有人会改这个端点的代码，它就泄漏了。**
>
> 这是本课程反复要建立的判断：**不要靠"当前代码恰好没问题"，要靠"结构上不可能出问题"。**

### 6.2 定义出口模型并挂上

```python
class AuthorOut(BaseModel):
    id: int
    display_name: str

class QuestionOut(BaseModel):
    id: int
    title: str
    body: str
    created_at: datetime
    author: AuthorOut

@app.get("/questions/{qid}", response_model=QuestionOut)
def get_question(qid: int):
    ...
    return {                       # 注意：返回的仍然是一个"多出很多字段"的结构
        "id": row.id, "title": row.title, "body": row.body,
        "created_at": row.created_at,
        "author": {
            "id": row.author_id, "display_name": row.display_name,
            "email": row.email, "password_hash": row.password_hash,
            "is_admin": row.is_admin,
        },
    }
```

**这里故意保留了泄漏字段。** 重新请求：

```json
{
  "id": 1, "title": "React 怎么学", "body": "...",
  "created_at": "2025-03-01T10:00:00",
  "author": {"id": 3, "display_name": "Alice"}
}
```

**password_hash 消失了。函数还在返回它，但它出不去。**

### 6.3 结论：这是本课程第一道结构性护栏

做成醒目页：

> **`response_model` 不是文档，是一道过滤器。**
>
> 它的工作方式是：拿你声明的模型去**重新构造**响应，模型里没有的字段一律丢弃。
>
> 所以——**即使你的查询写错了、即使 AI 返回了不该返回的东西、即使有人给表加了新列，只要出口模型没声明，它就出不去。**

紧接着点出课程主题（这是本次课与第 0 次课的接点）：

> 对比一下两种做法：
>
> 做法 A：每次 code review 时，人去看一眼"这个接口有没有返回敏感字段"。
> 做法 B：声明一个出口模型，让不该出去的东西**在结构上出不去**。
>
> A 依赖人的注意力，AI 参与开发之后代码量上去了，人的注意力是最先耗尽的资源。B 是一次性投入，之后永远生效。
>
> **第 0 次课我说这门课要把"人肉审查"换成"机器把关"。`response_model` 是你见到的第一个。第 9 次课我们会把这类护栏批量装进 CI。**

### 6.4 为什么入口和出口要用两个不同的模型

学生一定会问：能不能一个 `Question` 模型进出通用？

列出四条理由（做成对照表）：

| 差异点 | Create（入） | Out（出） |
|---|---|---|
| `id`、`created_at` | **不能有** —— 服务端生成，客户端指定是伪造 | 必须有 |
| `password_hash` | 不适用 | **绝不能有** |
| `author_id` | **不能有** —— 应从会话取〔→ 第 14 次课〕 | 以嵌套的 `AuthorOut` 呈现 |
| 字段可选性 | Create 全必填；**Update 全可选**（PATCH 语义） | 全部必有 |

所以一个资源通常至少三个模型：

```
QuestionCreate   ← POST 的入口
QuestionUpdate   ← PATCH 的入口，字段全部 Optional
QuestionOut      ← 所有读取端点的出口
```

**判据**：

> **入口模型回答"客户端被允许提交什么"，出口模型回答"我承诺返回什么"。这是两个不同的问题，所以是两个不同的模型。**
>
> 合并它们省下来的十几行代码，换来的是这两个问题永远纠缠在一起。

〔顺带说明：Update 模型的"全可选"会带来一个新问题——**怎么区分"没传这个字段"和"传了 null"**。这是 PATCH 的经典难题，第 8 次课讲 PUT/PATCH 差异时处理。今天挂欠账。〕

### 6.5 两个实现细节

**其一，两种写法等价**：

```python
@app.get("/questions/{qid}", response_model=QuestionOut)   # 写法 A
def get_question(qid: int): ...

@app.get("/questions/{qid}")                                # 写法 B
def get_question(qid: int) -> QuestionOut: ...
```

**本课程统一用写法 A。** 理由不是 A 更好，而是：它在 diff 里更显眼，也更容易被 CI 脚本机械检查出"有没有漏写"。〔→ 第 9 次课会真的写这个检查〕这也是一个"为可验收性而做的选择"的例子。

**其二，列表端点的出口模型怎么写**：

```python
class QuestionListOut(BaseModel):
    items: list[QuestionBriefOut]
    total: int
    page: int
```

顺便点一句：列表里通常**不返回完整正文**（用 `QuestionBriefOut`，只有 title 和摘要）。这既是体积考虑，也是一次"接口该承诺什么"的设计决定。

### 材料

- seed 数据需新增 `users` 表：`id / email / password_hash / display_name / is_admin / last_login_ip / created_at`，**全部为虚构数据**，password_hash 用一个明显是假值的 bcrypt 格式字符串。`questions.author_id` 关联到它。
- **高光图**：修复前后两个响应体同屏左右对照，左侧四个泄漏字段红框高亮，右侧同位置标注"已被出口模型过滤"。这是本次课的封面级素材。
- **高光图**：两道闸门示意图（见单元 7），需与第 1 次课链路图风格统一。

---

## 七、两道闸门：本次课的心智模型

**约 7 分钟。这一单元是把前面所有内容收束成一张图。**

### 核心图：两道闸门

图的要素（画法交给制作团队）：

```
   外部世界
   不可信 · 全是字符串 · 结构任意
        │
   ═════╪═════  入口闸门：Pydantic 校验
        │        · 类型转换   · 约束检查
        │        · 多余字段拒绝  · 顺手清洗
        ▼
   应用内部
   可信 · 强类型对象 · 结构已知
        │           （这里才是你写业务逻辑的地方）
        ▼
   ═════╪═════  出口闸门：response_model 序列化
        │        · 只保留声明过的字段
        │        · 类型收敛
        ▼
   外部世界
   只看到你承诺给它的东西
```

**这张图要和第 1 次课的链路图叠在一起看**：两道闸门都位于「路由与参数解析」那一格里，把「应用代码」那一格夹在中间。请在课件里做一次这个叠加动画或并排对照。

### 三条判据

1. **数据跨过入口闸门之前，不许进入业务逻辑。** 所以不该有 `request.json()` 之后手工 `payload["title"]` 这种写法——那是在闸门外取水。
2. **数据跨过出口闸门之前，不许假设它是安全的。** 所以不该有"我查出来的这行没有敏感字段，直接返回"这种判断——今天没有，明天加了列就有了。
3. **闸门之间的代码可以放心假设类型正确。** 这是两道闸门带给你的最大好处：业务代码干净了。

### 讲

> 我想让你们注意这个模型的一个性质：**它是位置性的，不是技巧性的。**
>
> 校验这件事你以前也做，但你是在业务逻辑里东一个 if 西一个 if 地做。今天的变化不是"多学了 Pydantic"，是**把这件事统一挪到了一个固定的位置**，于是它可以被集中审查、被自动检查、被写进文档。
>
> 这门课后面还会做好几次同样性质的事：第 4 次课把错误处理挪到一个位置，第 7 次课把事务边界挪到一个位置，第 14 次课把授权挪到一个位置。**把散落的东西收拢到一个可被检查的位置**——这是应对"代码量爆炸"最有效的一招。

---

## 八、契约先行：为什么这是约束 AI 最有效的抓手

**约 11 分钟。本次课的课程主题落点，不能压缩。请在课件上标注：这与第 0 次课的"两个提示词对比"不是同一个演示。**

### 8.1 先看契约长什么样

打开 `/openapi.json`（建议用浏览器的 JSON 格式化视图或 `curl | jq`）。

指出三件事：

1. **`/docs` 页面不是框架"生成文档"，它只是一个前端页面在渲染这份 JSON。** 你可以用任何工具渲染它。
2. 这份 JSON 里包含了每个端点的：方法、路径、参数、**入口 schema、出口 schema、所有可能的状态码**。
3. **它是机器可读的。** 这一点是后面一切的前提。

顺手做一下 `tags`，让 `/docs` 分组，说明这只是可读性改进：

```python
@app.get("/questions", tags=["questions"], summary="问题列表")
```

### 8.2 契约能被机器拿去做什么（列举，指向后续课）

| 用途 | 在哪次课做 |
|---|---|
| 生成前端 TypeScript 类型，**后端改了字段前端立刻编译报错** | 第 8 次课 B 档、第 10 次课 |
| 作为前后端之间的正式交付物，不再靠聊天记录对接口 | 第 8 次课 |
| 在 CI 里对比"契约有没有被意外改动" | 第 9 次课 |
| 作为给 AI 的输入，让它按契约生成实现或生成测试 | **今天** |

### 8.3 现场演示：一个完整的契约先行小循环

**请按这个顺序做，不要跳步。每一步的耗时写在括号里，这是这个演示的说服力所在。**

**第一步（约 60 秒）：人来写 schema。**

```python
class AnswerCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")
    body: str = Field(min_length=10, max_length=10000)

class AnswerOut(BaseModel):
    id: int
    body: str
    created_at: datetime
    author: AuthorOut
```

**第二步：给 AI 的指令是"填空"，不是"实现功能"。**

```
在现有项目中实现 POST /questions/{qid}/answers。
硬性约束：
1. 入口模型必须使用已定义的 AnswerCreate，出口模型必须使用已定义的
   AnswerOut，不得修改这两个类，不得新增字段。
2. 端点必须声明 response_model=AnswerOut 与 status_code=201。
3. 作者暂时固定为 author_id=1（会话机制尚未引入，此处留 TODO）。
4. 问题不存在时返回 404。
5. 不得引入新的第三方依赖，不得修改其他文件。
```

**第三步：拿契约当验收判据，当场跑四项检查。**

| 检查 | 怎么做 | 判什么 |
|---|---|---|
| 契约一致 | 打开 `/docs` 看该端点的 Request/Response schema | 是否就是我定义的那两个 |
| 入口收窄有效 | 发 `{"body":"短"}` 和 `{"body":"够长的内容","author_id":9}` | 是否都 422 |
| 出口收窄有效 | 在 handler 里故意多返回一个 `secret` 字段 | 响应里是否**没有**它 |
| 状态码正确 | 成功 / 问题不存在 | 是否 201 / 404 |

### 8.4 结论（醒目页，这是本次课的收尾）

> **schema 同时是三样东西：需求说明书、给 AI 的约束、验收判据。**
>
> 这是第 0 次课列的五项能力里，**"需求规格化""约束表达""验收判据"三项第一次落在同一个具体产物上**。
>
> 为什么这比"把提示词写详细"更有效？因为：
> - 提示词是**一次性的**，schema 是**留在仓库里、每次请求都在执行的**；
> - 提示词靠 AI 理解，schema 靠框架**强制执行**——AI 理解错了也绕不过去；
> - 提示词无法被 CI 检查，schema **可以**。

**适用边界（请保留，避免讲成万能药）**：

> 契约先行管得住"接口形状"，管不住"业务逻辑对不对"。
>
> AI 完全可以写出一个**契约完美但把答案存错问题下**的实现。那一类正确性要靠测试来保证——**第 9 次课**。
>
> 所以完整的说法是：**契约管形状，测试管行为，CI 管两者都不许退化。** 今天你拿到的是第一块。

---

## 九、C 档结论卡

**约 4 分钟，明确说明"课后查阅，不要求现在理解推导"。时间紧张时整体跳过。**

### 9.1 ASGI 一句话结论

给一个能跑的、8 行的裸 ASGI 应用：

```python
async def app(scope, receive, send):
    await send({"type": "http.response.start", "status": 200,
                "headers": [(b"content-type", b"text/plain")]})
    await send({"type": "http.response.body", "body": b"hello"})
```

> **ASGI 就是这个约定：服务器给你一个 `scope`（这次请求的元信息）、一个 `receive`（读请求体）、一个 `send`（发响应）。**
>
> FastAPI 在这之上做的事情是：把 scope 包成 `Request` 对象 → 匹配路由 → 按签名提取并校验参数 → 调你的函数 → 把返回值经 `response_model` 变成 Response → 通过 send 发出去。
>
> **今天讲的一切，都发生在这个夹层里。** 第 1 次课调用栈底部你看到的 uvicorn 那几层，就是 ASGI 服务器那一侧。
>
> WSGI（同步版本）与 ASGI 的差别、为什么需要异步 → **第 5 次课**。

### 9.2 Starlette 路由的实现细节

路径模板 → 正则的转换规则；路径转换器 `{x:int}` / `{x:float}` / `{x:uuid}` / `{x:path}`；`APIRouter` 的 prefix 拼接。→ 自读框架源码 `starlette/routing.py`，约 200 行，是很好的读源码入门。

### 9.3 跨栈落点对照（本表的用途是"换栈时知道去找什么"）

| 能力 | FastAPI | Flask | Django | Express | Spring Boot |
|---|---|---|---|---|---|
| 路由注册 | `@app.get` | `@app.route` | `urls.py` 的 `path()` | `app.get()` | `@GetMapping` |
| 入口校验 | Pydantic 模型 | 手写 / marshmallow | Form / DRF Serializer | 手写 / zod | `@Valid` + Bean Validation |
| 出口收窄 | `response_model` | 手写 dict | DRF Serializer | 手写 | DTO + Jackson |
| 契约文档 | 自动 OpenAPI | flasgger 等 | drf-spectacular | swagger-jsdoc | springdoc |

> 结论：**"入口收窄 / 出口收窄 / 契约可导出"是跨框架通用的结构，不是 FastAPI 的特性。** 换栈时不要重新学概念，只要找到对应物。
>
> 顺便：如果某个框架**没有**出口收窄的机制（比如裸 Express 直接 `res.json(row)`），那不是它更自由，是这道护栏需要你自己补上——而这正是 Node 生态里字段泄漏事故偏多的原因之一。

---

## 十、作业与欠账登记

**约 5 分钟。**

### 作业一：三个核心端点的 In/Out schema（主线作业）

为以下三个核心端点定义明确的入口和出口模型：

| # | 端点 | 入口模型 | 出口模型 | 成功状态码 |
|---|---|---|---|---|
| 1 | `GET /questions` | 查询参数（keyword / page / page_size，**page_size 必须有上界**） | `QuestionListOut` | 200 |
| 2 | `GET /questions/{qid}` | — | `QuestionOut` | 200 |
| 3 | `POST /questions` | `QuestionCreate` | `QuestionOut` | **201** |

要求：

- 所有端点声明 `response_model=` 与 `status_code=`；
- 所有入口模型设 `extra="forbid"`；
- 所有端点加 `tags` 与 `summary`；
- **出口模型中不得出现 `password_hash`、`email`、`is_admin`、`last_login_ip`**；
- 写操作的 SQL 由课程模板提供（`app/sql_snippets.py`），**本次课只考 schema 设计，不考 SQL**；
- 路由顺序正确（自检：`/questions/latest` 若存在则必须可访问）。

> **扩展端点（可选）**：健康检查、回答端点、PATCH 端点可作为扩展练习。PATCH 留到第 8 次课详细讲解。

### 作业二：一处"裸 dict → response_model"的 diff 与说明

提交 `git diff`，并附三句话：
1. 修改前这个端点实际会返回哪些字段？（把响应体贴出来）
2. 其中哪些是不该出去的？
3. **如果将来有人给表加一列，修改前后的行为分别是什么？**

第 3 问是重点，它检验你是否真的理解了"结构性护栏"。

### 作业三：边界输入表（B 档，课后自学）

对 `QuestionCreate` 的每个字段，按单元 5.5 的五类方法设计输入，在 `/docs` 逐个验证，填表：

| 字段 | 输入 | 期望结果 | 实际状态码 | 实际 `loc` | 实际 `type` | 是否符合预期 |
|---|---|---|---|---|---|---|

> **注意**：如果判断某个输入的校验行为符合预期，无需特别说明。只需记录"结果与你的预期不一致"的案例并说明原因。

### 作业四：契约快照（为后续课准备）

```bash
curl -s localhost:8000/openapi.json | python -m json.tool > contract/openapi.snapshot.json
```

提交这个文件。**第 8 次课会以它为基线，第 9 次课会在 CI 里比对它。** 现在只是存档。

### 本次课新增的欠账登记

| 欠账 | 何时还 |
|---|---|
| 422 的格式与课程统一错误契约不一致 | 第 4 次课 |
| JSON 语法错误返回 422 而非 400 | 第 4、8 次课 |
| 数据库连接每次现开、`commit()` 散落 | 第 4、7 次课 |
| 基础校验放 schema，那查库才能判断的校验放哪 | 第 4 次课（服务层） |
| `author_id` 应该从会话取，不能由客户端给 | 第 14 次课 |
| PATCH 如何区分"没传"与"传了 null" | 第 8 次课 |
| `Form(...)` 与 JSON 两条解析路径 | 第 5 次课 |
| 契约导出为前端类型 | 第 8、10 次课 |
| 契约在 CI 中比对 | 第 9 次课 |
| WSGI / ASGI 与异步的必要性 | 第 5 次课 |

---

## 十一、素材清单与制作说明

### 必需素材（缺了讲不下去）

| 素材 | 说明 |
|---|---|
| tag `v3-ai-endpoints` | 解剖台反例。**需验证三个问题稳定复现**：`/questions/latest` 返回 422 且 `loc` 为 `["path","qid"]`；缺字段返回 500 而非 422；`/questions/1` 响应体含 `password_hash` |
| tag `v3-contracts` | 修复后的目标状态：路由顺序正确 + 六个端点的 In/Out schema 齐备 |
| seed 数据新增 `users` 表 | 全虚构数据；`password_hash` 用明显的假 bcrypt 串；含 `is_admin`、`last_login_ip` 以增强泄漏的冲击力 |
| `app/dump_routes.py` | 打印路由表的脚本，避免现场手敲 |
| `app/sql_snippets.py` | 作业用的参数化 SQL 片段（含 INSERT / UPDATE），学生只需填 schema |
| 断点演示配置 | 延用第 1 次课 `.vscode/launch.json`，**必须关闭 `--reload`** |
| **高光图 A**：响应体修复前后同屏对照 | 左侧四个泄漏字段红框高亮，右侧标注"已被出口模型过滤"。封面级素材 |
| **高光图 B**：两道闸门示意图 | 需与第 1 次课链路图风格统一，并能与之叠加对照 |
| **高光图 C**：路由匹配过程表 | 三条路由逐个试正则，第二条命中并高亮，配 `path_regex` 实际打印结果 |
| 图 D：断点未命中的调试器截图 | 需能看清断点标记存在、但程序已返回 422 |
| 表 E：422 响应字段读法 | 纯表格 |
| 表 F：In / Out 模型差异对照 | 纯表格 |

### 可后补

- `/openapi.json` 的格式化截图（可用文字片段替代）。
- 跨栈落点对照表（纯文字）。
- 裸 ASGI 应用示例（代码已在文中，无需配图）。

### 备用材料

| 风险 | 备用方案 |
|---|---|
| 断点未命中的演示因环境问题失败 | 改用"在函数第一行加 `print('进入函数')`"的等价演示，效果稍弱但稳定；同时准备预录 30 秒录像 |
| 现场调用 AI 生成代码失败或超时（单元 8.3） | 准备一份**预先生成并验证过**的 AI 输出，标注"预录产物"；四项验收检查仍现场跑 |
| `/docs` 页面因网络问题加载不出（依赖 CDN） | 项目已配置本地静态资源版 Swagger UI；若仍失败，改用 `curl /openapi.json \| jq` 展示 |
| 学生环境 Pydantic 版本差异导致 422 文案不同 | 强调**只依赖 `loc` 与 `type`，不依赖 `msg`**——这本身就是本课要讲的判据 |

### 环境与运行条件

延用前两次课环境（Python 3.12 / FastAPI / Pydantic v2 / SQLAlchemy 2.x / PostgreSQL 16+）。**请在课件的环境页标明 Pydantic 主版本为 2.x**，v1 的 API 差异较大。

**演示开始时的初始状态**：数据库已 seed（含 users 表与至少一条关联数据）、服务未启动（第一个动作就是启动并打印路由表）、浏览器已打开 `/docs`。

**复位方式**：`git checkout v3-ai-endpoints && make reset-db`，可完整重演。

---

## 十二、与前后课的衔接（供制作团队理解引用关系）

**本次课回收的前序埋点**：

| 来源 | 埋点 | 本次课在哪回收 |
|---|---|---|
| 第 0 次课 | 找错题第 3 条"返回整个 author 对象" | 单元 2、6 |
| 第 0 次课 | Week 0 装饰器原型 `ROUTES` | 单元 3.1 |
| 第 0 次课 | "靠机器把关，不靠肉眼审查" | 单元 6.3 |
| 第 1 次课 | `/docs` 从哪来 | 单元 3.2 |
| 第 1 次课 | 422 是谁生成的、在链路哪个环节 | 单元 5.2、5.3 |
| 第 1 次课 | `SELECT *` 返回全部列 | 单元 6 |
| 第 1 次课 | 调用栈与链路图对应 | 单元 5.2、9.1 |
| 第 2 次课 | 400 vs 422 判据 | 单元 5.4（如实指出不一致） |
| 第 2 次课 | 201 应带创建语义 | 单元 5.1 |
| 第 2 次课 | 四种请求编码 | 单元 4 |
| 第 2 次课 | "沉默的成本" | 单元 2 第三个 bug |

**本次课埋下、后面必须回引的三处**（请在课件中做明显标记）：

- 单元 6「结构性护栏」→ 第 9 次课 CI 门禁会回到这一页，说明"从一道护栏到一整排"；
- 单元 7「两道闸门图」→ 第 4 次课分层时会在这张图上继续画，第 14 次课授权也会挂在这张图上；
- 单元 8「契约管形状、测试管行为」→ 第 9 次课开场直接接这句话。

**本次课不承担、请勿提前引入的内容**：依赖注入与 `Depends`（第 4 次课，本次课所有端点仍然各自 `engine.connect()`，**这个重复是有意保留的，它是第 4 次课的痛感来源**）、分层目录结构（第 4 次课）、统一错误契约（第 4 次课）、ORM 与 `relationship`（第 7 次课）、异步与 `async def` 的选择（第 5 次课）、认证与会话（第 14 次课）。