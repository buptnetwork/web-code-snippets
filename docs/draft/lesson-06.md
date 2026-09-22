# 第 6 次课教学底稿
## 数据建模与 SQL 基础

---

## 〇、给 PPT 制作团队的全局说明

本次课 100 分钟，留 5 分钟缓冲。**本次课的边界必须守住：只教"设计得对 + 查得出来"，不进数据库内核。** 不讲 B+ 树结构、不讲 MVCC、不讲执行计划的 cost 模型、不讲隔离级别（隔离级别在第 7 次课事务边界里只给一句话结论）。凡是学生问到内核，一律回答"这不影响你今天要做的决定"，并记入 C 档卡。

**本次课的教学法仍然是"痛感在前"。** 第 5 次课末尾已经埋好条件：M1 的数据是 seed 出来的几十条。**本次课第一件事就是把数据灌到十万级**，让三个问题自己浮出来，然后才开始讲建模。请务必按这个顺序制作，不要一上来就放 ER 图。

**本次课有三个高光，按重要性排序**：

1. **并发下应用层查重失效（单元 4.4，12 分钟）**。这是本次课最重要的一处，因为它直接回答"为什么约束要下推到数据库"。必须现场用两个并发请求制造出两条重复标题，然后加 `UNIQUE` 约束，再并发，看到数据库把第二个请求挡下来。**这个演示和第 5 次课的并发崩塌是姊妹篇——都是"单请求测不出来"的一类错误。**
2. **NULL 三值逻辑导致漏行（单元 5，12 分钟）**。要做成定量：应该 1000 行，实际返回 850 行，**没有任何报错**。`NOT IN` 子查询含 NULL 导致结果全空那一条，请单独做一页。
3. **十万行下加索引前后对照（单元 7.3，8 分钟）**。数据表要做成封面级素材。

**第四处值得重点制作但常被忽略的**：单元 6.2 的"不稳定排序导致翻页丢数据"。现场翻两页，同一条记录出现两次，另一条从没出现过。这个现象极其隐蔽，也极其常见。

**若时间不够的压缩顺序**：先压单元 8 的 C 档卡（整体移课后）→ 再压单元 6 的第 7、8 条 SQL（留作作业）→ 再压单元 3 的 ER 建模（多数学生有基础，可只保留三条判据页，省 5 分钟）。**单元 4、5、7 不能压缩。**

**一个需要教师裁决的地方**：本次课全程用 PostgreSQL 的语法与行为演示（`ILIKE`、`RETURNING`、`IS DISTINCT FROM`、部分索引）。这些在 MySQL 上行为不同或不存在。底稿在 C 档卡里给了差异表。如果你的学生群体以 MySQL 为主，请告知——需要调整单元 5 和单元 6 的三处示例。

---

## 一、开场：M1 在十万条数据下是什么样

**约 5 分钟。请从现场演示开始，不要先讲概念。**

### 1.1 灌数据，然后什么都不解释，只看现象

```bash
python scripts/seed_large.py --questions 100000 --answers 300000 --users 2000
# 约 40 秒
```

打开 M1 的列表页，**什么代码都没改**，然后做三件事：

**现象一：首页慢了 60 倍。**

```bash
time curl -s "localhost:8000/questions?page=1&size=20" > /dev/null
# seed 前：real 0m0.031s
# seed 后：real 0m1.84s
```

**现象二：往后翻，越来越慢。**

```bash
time curl -s "localhost:8000/questions?page=500&size=20" > /dev/null
# real 0m3.12s
```

**现象三：翻页的时候，有一条问题出现了两次。**

```bash
curl -s "localhost:8000/questions?page=3&size=20" | jq -r '.items[].id' > p3.txt
curl -s "localhost:8000/questions?page=4&size=20" | jq -r '.items[].id' > p4.txt
sort p3.txt p4.txt | uniq -d
# 87341        ← 两页都有它
```

**现象四（顺手一看）：数据里有重复标题。**

```sql
SELECT title, count(*) FROM questions GROUP BY title HAVING count(*) > 1 LIMIT 5;
--  "如何学习 SQL" | 2
--  "求推荐入门书" | 3
```

> 可是第 4 次课我们在 `services/` 里写了查重逻辑，而且它测试通过了。

### 1.2 把这四个现象挂起来，说明本次课要做什么

讲：

> 四个现象，**没有一个是因为代码写错了**。M1 通过了全部验收：分层正确、schema 正确、错误契约统一、PRG 正确、`def`/`async def` 选择正确。
>
> 问题全在**数据这一层**：表怎么建的、有没有索引、有没有约束、SQL 怎么写的。
>
> 这四个现象今天全部解决。但我要先说清楚今天这节课的边界：
>
> **我不教数据库内核。** 我不讲 B+ 树长什么样、不讲 MVCC 怎么实现、不讲执行计划的代价模型。理由很简单：**那些知识不影响你今天要做的任何一个决定。** 你今天要决定的是"这个字段该不该 NOT NULL""这个外键删除时该级联还是置空""这个查询该加什么索引"——这些决定只需要一小组判据，不需要内核。
>
> 本次课结束时你应当能回答：
>
> - 为什么"在应用层保证唯一"这句话在并发下是假的？**能说出具体的时序吗？**
> - `WHERE status != 'deleted'` 为什么会漏行？漏了多少行？为什么不报错？
> - 一个外键该配 `CASCADE` 还是 `SET NULL` 还是 `RESTRICT`？判据是什么？
> - `ORDER BY created_at DESC` 配 `LIMIT/OFFSET` 为什么会丢数据？
> - 该给哪些列加索引？**三条规则，不看执行计划也能定**。
> - 为什么 AI 建的表几乎一定漏约束？

---

## 二、解剖台：AI 建的那张表

**约 12 分钟。本次课痛感来源，四个演示都要做。**

### 2.1 现场把 DDL 拿出来（tag: `v6-bad-schema`）

> 这是 M1 里正在用的建表语句。它不是我编的——这是把第 4 次课的模型描述给 AI，让它"生成建表 SQL"的原样输出。

```sql
-- migrations/001_init.sql —— AI 原样产物
CREATE TABLE users (
    id          SERIAL PRIMARY KEY,
    email       VARCHAR(255),
    display_name VARCHAR(255),
    password_hash VARCHAR(255),
    role        VARCHAR(255),
    created_at  VARCHAR(255)
);

CREATE TABLE questions (
    id          SERIAL PRIMARY KEY,
    title       VARCHAR(255),
    body        VARCHAR(255),
    author_id   INTEGER,
    status      VARCHAR(255),
    view_count  INTEGER,
    created_at  VARCHAR(255)
);

CREATE TABLE answers (
    id          SERIAL PRIMARY KEY,
    question_id INTEGER,
    author_id   INTEGER,
    body        VARCHAR(255),
    is_accepted VARCHAR(255),
    created_at  VARCHAR(255)
);

CREATE TABLE tags (
    id   SERIAL PRIMARY KEY,
    name VARCHAR(255)
);

CREATE TABLE question_tags (
    id          SERIAL PRIMARY KEY,
    question_id INTEGER,
    tag_id      INTEGER
);
```

先让学生看 30 秒，提问：**你能看出几个问题？**

学生通常能说出"全是 VARCHAR(255)"。**这只是最表面的那个。** 下面用四个演示把真正的代价摊开。

### 2.2 演示一：正文被截断，而且是静默的

```sql
INSERT INTO questions (title, body, author_id, status, created_at)
VALUES ('测试', repeat('啊', 300), 1, 'open', '2025-03-20');
```

PostgreSQL 这里会报错（`value too long`），**但在 MySQL 的非严格模式下会静默截断**。

> 这是本次课第一条"跨数据库行为不同"的例子。在 PostgreSQL 上你会收到报错——**这是好事**。在配置不当的 MySQL 上，用户写的 300 字正文变成 255 字入库，**没有任何人知道**。
>
> 而正确的做法根本不是调长度：**问题正文应该是 `TEXT`**。`VARCHAR(255)` 这个数字来自哪里？没有任何业务依据，它纯粹是一个被抄了二十年的默认值。

### 2.3 演示二：`created_at` 是字符串，排序是错的

```sql
SELECT title, created_at FROM questions
ORDER BY created_at DESC LIMIT 5;
```

```
 "旧问题"  | 2025-9-30
 "新问题"  | 2025-10-15      ← 应该在最前面，却排在后面
 "更早的"  | 2025-1-5
```

> 字符串比较是**逐字符比的**。`'2025-9-30' > '2025-10-15'`，因为第六个字符 `9` > `1`。
>
> 于是列表页的"最新问题"排序是错的——**而且它看起来是对的**，因为大部分数据的月份都是两位数，只有跨过 9 月和 10 月的边界才出错。
>
> 这类 bug 的调试成本极高：一个月里只有几天能复现。

顺手指出第二个代价：

```sql
-- 想查"最近 7 天的问题"，你做不到
SELECT * FROM questions WHERE created_at > now() - interval '7 days';
-- ERROR: operator does not exist: character varying > timestamp
```

> 要么每次查询都 `CAST`（那就用不上索引了），要么在应用层过滤（那就要把十万行全拉回来）。
>
> **判据：类型不是"存得下就行"，类型决定了你能对这个字段做什么运算。**

### 2.4 演示三：删掉用户，回答变成孤儿

```sql
DELETE FROM users WHERE id = 42;     -- 成功，没有任何阻拦
SELECT count(*) FROM answers WHERE author_id = 42;
-- 1876
```

打开一个包含这些回答的问题详情页：

```
回答者：None
回答者：None
```

或者直接 500——取决于你的代码有没有处理 `None`。

> 数据库里现在有 1876 条回答，指向一个不存在的用户。**这叫孤儿数据。**
>
> 关键点：`DELETE` 那条语句**成功了**。数据库不知道 `answers.author_id` 和 `users.id` 有关系——因为没人告诉它。
>
> 而且这种数据一旦产生就**很难清理**：你不知道这些回答原来属于谁，也不敢直接删（那是真实内容）。

### 2.5 演示四：并发下的重复标题（**留个悬念，单元 4.4 才解决**）

```sql
SELECT title, count(*) FROM questions GROUP BY title HAVING count(*) > 1;
--  "如何学习 SQL" | 2
```

> 第 4 次课我们在 `services/question.py` 里写了这个：
>
> ```python
> if repo.find_by_title(conn, title) is not None:
>     raise DuplicateTitle()
> ```
>
> 这段代码是对的。它的测试是通过的。你手工点两次"发布"，第二次确实会收到 409。
>
> **但数据库里就是有两条。**
>
> 为什么？**单元 4.4 会现场把它制造出来。** 现在先记住这个矛盾。

### 2.6 把问题分类（**只分类，不给方案**）

| 问题类别 | 解剖台的表现 | 代价的性质 |
|---|---|---|
| **类型选得不对** | 全 `VARCHAR(255)`，时间存字符串 | 排序错、无法做时间运算、静默截断 |
| **缺少约束** | 无 `NOT NULL`、无 `UNIQUE`、无 `FK`、无 `CHECK` | 脏数据能进来；应用层的保证在并发下失效 |
| **缺少索引** | 一条索引都没有（除主键） | 十万行下查询慢 60 倍 |
| **查询写法有问题** | `LIMIT/OFFSET` 没有稳定排序 | 翻页丢数据、重复数据 |

> 这四类的性质不同：
>
> 前两类是**建模问题**——一旦数据进来了就很难补救，脏数据已经在那里了。
> 后两类是**查询问题**——代码改一下就好，数据没坏。
>
> 所以今天的顺序是：**先把建模（单元 3、4、5）讲透，再讲查询（单元 6、7）。** 因为建模的错误是不可逆的。

### 欠账清单

| 问题 | 本次课处理 | 何时还 |
|---|---|---|
| 类型全是 VARCHAR | 单元 4.2 | — |
| 缺 NOT NULL / UNIQUE / FK / CHECK | 单元 4.3–4.6 | — |
| NULL 导致查询漏行 | **单元 5** | — |
| 缺索引，十万行下慢 60 倍 | **单元 7** | — |
| OFFSET 分页不稳定排序 | 单元 6.2 | — |
| 深分页（OFFSET 10000）本身就慢 | 单元 7.5 给结论 | **第 11 次课**（keyset 分页） |
| `LIKE '%kw%'` 用不上索引 | 单元 7.5 给结论 | **第 11 次课**（全文检索） |
| 已经进来的脏数据怎么清 | 单元 4.7 给方法 | **第 7 次课**（迁移脚本里做） |
| 建表语句还是手写 SQL，没有迁移管理 | 记一笔 | **第 7 次课**（Alembic） |

---

## 三、ER 建模：五张表

**约 10 分钟。时间紧张时可压到 5 分钟，只保留 3.3 的三条判据。**

### 3.1 先把名词列出来，再决定谁是表

需求语言里出现的名词：用户、问题、回答、标签、采纳、浏览量、发布时间。

**第一条判据（做成醒目页）**：

> **问它有没有独立的生命周期和身份。**
>
> - 有 → 它是一张表（实体）
> - 没有，它只是附着在某个实体上的一个值 → 它是一个列（属性）

逐个判断：

| 名词 | 判断 | 理由 |
|---|---|---|
| 用户 | **表** | 有独立身份，能被引用，能单独存在 |
| 问题 | **表** | 同上 |
| 回答 | **表** | 有自己的 id、作者、时间，能被单独引用（比如"采纳某条回答"） |
| 标签 | **表** | 同一个标签被多个问题共用，需要独立管理（改名、合并） |
| 浏览量 | **列** | 依附于问题，没有独立身份 |
| 发布时间 | **列** | 同上 |
| 采纳 | **列**（`answers.is_accepted`） | 它是回答的一个状态，不是独立事物 |

> 注意"采纳"这一条是可以争论的。如果业务要求记录"谁在什么时候采纳的、采纳过又取消过"，那它就变成了一张 `acceptances` 表——**因为它有了自己的时间和操作者，就有了自己的生命周期**。
>
> **判据不是背来的，是问出来的：这个东西需要被单独追踪吗？**

### 3.2 关系的两种基本形态

**1:N（一对多）**

```
users  1 ────< N  questions        一个用户发多个问题
questions 1 ──< N  answers         一个问题有多个回答
users  1 ────< N  answers          一个用户写多个回答
```

**第二条判据（这是学生高频出错点）**：

> **1:N 的外键放在"多"的那一边。**
>
> `questions.author_id` → `users.id` ✅
> 而不是在 `users` 里放一个"我的问题列表" ❌
>
> 理由：一个列只能存一个值。"多"的那边每行只对应一个"一"，放得下；反过来放不下。

**M:N（多对多）**

```
questions N ──< question_tags >── N tags
```

**第三条判据**：

> **M:N 必须有一张连接表。** 两边都放不下对方（一个问题多个标签、一个标签多个问题）。

关于连接表的主键，给一个明确选择：

```sql
CREATE TABLE question_tags (
    question_id BIGINT NOT NULL REFERENCES questions(id) ON DELETE CASCADE,
    tag_id      BIGINT NOT NULL REFERENCES tags(id)      ON DELETE CASCADE,
    PRIMARY KEY (question_id, tag_id)        -- ← 复合主键，不要额外的 id
);
```

> 对比解剖台里 AI 的写法：它给了一个 `id SERIAL PRIMARY KEY`，然后 `question_id` 和 `tag_id` 没有任何约束。
>
> 后果：**同一个问题可以打同一个标签三次**。前端标签列表会显示"Python Python Python"。
>
> 用复合主键 `(question_id, tag_id)` 一次解决两件事：**唯一性约束 + 主键**。
>
> 什么时候连接表需要独立 id？当连接本身有属性且需要被引用时——比如"谁在什么时候打了这个标签"，且要支持"撤销某一次打标签操作"。**本项目不需要，所以不加。**

### 3.3 最终 ER 图

```
        ┌─────────┐
        │  users  │
        └────┬────┘
        1    │    1
   ┌─────────┴─────────┐
   │ N               N │
┌──▼────────┐    ┌─────▼─────┐
│ questions │ 1──< │  answers  │
└──┬────────┘  N  └───────────┘
   │ N
   │
┌──▼────────────┐   ┌──────┐
│ question_tags │>──│ tags │
└───────────────┘ N └──────┘
```

〔制作说明：这张图请画规范的 ER 图（Crow's Foot 记号），标注每条关系的基数与可选性（0..1 / 1 / 0..N / 1..N）。**"可选性"很重要**——`answers.author_id` 能不能为空，决定了单元 4.5 的删除策略。〕

---

## 四、手写 DDL：约束下推到数据库

**约 20 分钟。本次课第一高光，绝对不能压缩。**

### 4.1 先给出重写后的 DDL，然后逐条解释每个决定

```sql
-- migrations/001_init.sql —— 重写版
CREATE TABLE users (
    id            BIGSERIAL PRIMARY KEY,
    email         TEXT        NOT NULL,
    display_name  TEXT        NOT NULL,
    password_hash TEXT        NOT NULL,
    role          TEXT        NOT NULL DEFAULT 'member',
    created_at    TIMESTAMPTZ NOT NULL DEFAULT now(),
    CONSTRAINT users_email_key    UNIQUE (email),
    CONSTRAINT users_role_check   CHECK (role IN ('member', 'moderator', 'admin')),
    CONSTRAINT users_name_len     CHECK (char_length(display_name) BETWEEN 2 AND 40)
);

CREATE TABLE questions (
    id          BIGSERIAL PRIMARY KEY,
    title       TEXT        NOT NULL,
    body        TEXT        NOT NULL,
    author_id   BIGINT      NOT NULL
                REFERENCES users(id) ON DELETE RESTRICT,
    status      TEXT        NOT NULL DEFAULT 'open',
    view_count  INTEGER     NOT NULL DEFAULT 0,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT now(),
    CONSTRAINT questions_title_key    UNIQUE (title),
    CONSTRAINT questions_status_check CHECK (status IN ('open', 'closed', 'deleted')),
    CONSTRAINT questions_title_len    CHECK (char_length(title) BETWEEN 5 AND 200),
    CONSTRAINT questions_views_nonneg CHECK (view_count >= 0)
);

CREATE TABLE answers (
    id          BIGSERIAL PRIMARY KEY,
    question_id BIGINT      NOT NULL
                REFERENCES questions(id) ON DELETE CASCADE,
    author_id   BIGINT              -- ← 允许 NULL，见 4.5
                REFERENCES users(id) ON DELETE SET NULL,
    body        TEXT        NOT NULL,
    is_accepted BOOLEAN     NOT NULL DEFAULT false,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT now(),
    CONSTRAINT answers_body_len CHECK (char_length(body) >= 10)
);

CREATE TABLE tags (
    id   BIGSERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    CONSTRAINT tags_name_key UNIQUE (name)
);

CREATE TABLE question_tags (
    question_id BIGINT NOT NULL REFERENCES questions(id) ON DELETE CASCADE,
    tag_id      BIGINT NOT NULL REFERENCES tags(id)      ON DELETE CASCADE,
    PRIMARY KEY (question_id, tag_id)
);
```

**先给一句总纲**：

> 对比一下行数：AI 的版本 5 张表 30 行，这个版本 5 张表 50 行。**多出来的 20 行全部是约束。**
>
> 那 20 行是这节课的全部价值。

### 4.2 类型选择：三条够用的规则

| 场景 | 选什么 | 不要选 |
|---|---|---|
| 短文本（名字、邮箱、标签、枚举值） | `TEXT`（PG）/ `VARCHAR(n)`（MySQL，n 按业务定） | 无依据的 `VARCHAR(255)` |
| 长文本（正文、描述） | `TEXT` | `VARCHAR(255)` |
| 时间 | **`TIMESTAMPTZ`** | `VARCHAR`、`DATE`（除非真的只要日期） |
| 布尔 | `BOOLEAN` | `VARCHAR`、`INTEGER(0/1)`、`CHAR(1)` |
| 整数主键 | `BIGSERIAL` / `BIGINT` | `SERIAL`（`INT` 上限 21 亿） |
| 钱 | `NUMERIC(p, s)` | **`FLOAT` / `DOUBLE`**（浮点误差会让账对不上） |
| 枚举 | `TEXT + CHECK` 或原生 `ENUM` | 裸 `VARCHAR` 无约束 |

三条要专门讲的：

**一、`TIMESTAMPTZ` 而不是 `TIMESTAMP`。**

> 带 tz 的版本在存储时统一转成 UTC，读取时按会话时区呈现。不带 tz 的版本存的是"一个没有时区含义的字面时间"——**你无法知道它是北京时间还是伦敦时间**。
>
> 这个坑的爆发时刻：服务器换了时区、或者加了一个海外节点。那时候历史数据已经全错了，**而且无法修复**，因为你不知道每一行当时是按哪个时区存的。
>
> **判据：只要这个时间可能被不同时区的人看到，就用 `TIMESTAMPTZ`。** 存储成本一样。

**二、`NUMERIC` 而不是 `FLOAT` 存钱。**

> `0.1 + 0.2 != 0.3`，这是二进制浮点的固有性质，不是数据库的 bug。涉及金额、库存、计分，一律 `NUMERIC`。
>
> 本项目没有钱，但这条规则太重要了，顺带说一句。

**三、`BIGSERIAL` 而不是 `SERIAL`。**

> `SERIAL` 是 `INT`，上限 2,147,483,647。听起来很大，但**自增序列不会因为你删了行就回收**。一张高频写入又高频删除的日志表，几年就能撞上限。
>
> 撞上限那天发生什么？**所有 INSERT 全部失败**，而且改类型需要重写整张表（大表上是分钟级到小时级的锁）。
>
> 多 4 个字节，换掉这个风险。**这是一个几乎零成本的决定，没理由不做。**

### 4.3 `NOT NULL`：默认值应该是"必填"

现场提问：

> 看解剖台那张表，**每一个字段都允许 NULL**。这意味着这条记录是合法的：
>
> ```sql
> INSERT INTO questions (id) VALUES (999999);
> -- 成功。一条没有标题、没有正文、没有作者、没有时间的问题。
> ```

执行它，然后打开列表页：

```
（空白）— 作者 None — None
```

或者直接 500。

> **判据：先问"这个字段能不能不填"。绝大多数答案是不能，那就 `NOT NULL`。**
>
> `NOT NULL` 的价值不只是挡住脏数据，还有一条很多人没想到的：
>
> **`NOT NULL` 让你的查询不必考虑 NULL。** 单元 5 你会看到 NULL 如何让最简单的 `WHERE` 出错。一个字段声明了 `NOT NULL`，你就永远不用为它写 `IS NULL` 的分支——**约束换来了代码的简化**。
>
> 反过来：**每一个允许 NULL 的字段，都是一个你必须在所有查询里考虑的分支。** 所以允许 NULL 要有理由。

配合 `DEFAULT`：

```sql
status      TEXT        NOT NULL DEFAULT 'open',
view_count  INTEGER     NOT NULL DEFAULT 0,
created_at  TIMESTAMPTZ NOT NULL DEFAULT now(),
```

> `NOT NULL + DEFAULT` 是一对。有了默认值，`NOT NULL` 就不会给插入造成麻烦——插入时不写这个字段，数据库自己填。
>
> 注意 `view_count NOT NULL DEFAULT 0`：如果允许 NULL，`SUM(view_count)` 和 `view_count + 1` 都会出问题（NULL 参与算术结果是 NULL）。

### 4.4 `UNIQUE`：并发下应用层查重为什么失效（**本次课最高光的一段**）

#### 第一步：重现解剖台的悬念

先把第 4 次课的查重代码放出来：

```python
# app/services/question.py
def create(conn, title, body, author_id):
    if repo.find_by_title(conn, title) is not None:   # ① 查
        raise DuplicateTitle()
    new_id = repo.insert(conn, title, body, author_id) # ② 插
    return repo.find_detail(conn, new_id)
```

**现场打两个并发请求**（脚本提供）：

```bash
python scripts/race_insert.py --title "并发测试标题" --n 2
```

结果：

```
request-1: 201 Created  id=100001
request-2: 201 Created  id=100002       ← 两个都成功了
```

```sql
SELECT id, title FROM questions WHERE title = '并发测试标题';
--  100001 | 并发测试标题
--  100002 | 并发测试标题
```

#### 第二步：画时序图，说清为什么（**这张图是本单元的核心素材**）

```
时间 →

请求 A:  ①查：没有  ─────────────→  ②插入 → 提交
                      ╲
请求 B:        ①查：没有  ─────────→  ②插入 → 提交
               ↑
        此刻 A 还没插入（或已插入但未提交，B 看不到）
        所以 B 查到的结果也是"没有"
```

> **两个请求都在"查"的时候看到了"没有重复"，所以两个都认为自己可以插入。**
>
> 这不是 bug，这是"先查后写"这个模式的固有缺陷。它有个名字：**检查与使用之间的时间窗口（TOCTOU，Time-Of-Check to Time-Of-Use）**。
>
> 窗口有多宽？在我们的代码里，①和②之间有一次 Python 函数调用、一次网络往返、可能还有一次日志写入——**几毫秒**。几毫秒在人的感觉里是零，在每秒几百个请求的服务里是**必然会撞上的**。

#### 第三步：说清为什么这个 bug 特别难被发现

**做成一张表，和第 5 次课的并发崩塌并列**：

| | 第 5 次课：`async def` + 阻塞 | 今天：应用层查重 |
|---|---|---|
| 单请求测试 | ✅ 通过 | ✅ 通过 |
| 单元测试 | ✅ 通过 | ✅ 通过（测试是串行的！） |
| Code review | ❌ 看不出来 | ❌ 看不出来（逻辑完全正确） |
| 开发机手工点 | ✅ 正常 | ✅ 正常（手点不出几毫秒的并发） |
| 什么时候暴露 | 并发上来 | 并发上来 |
| 暴露的样子 | 变慢 | **数据已经脏了，而且不可逆** |

> 注意最后一行的差别：第 5 次课那个问题，你修好代码性能就回来了。
>
> **今天这个问题，你修好代码之后，那两条重复数据还在。** 它们已经在用户的收藏夹里、已经被搜索引擎收录了、已经有人在下面回复了。
>
> **判据：数据层面的错误，比逻辑层面的错误严重一个数量级，因为它不可逆。**

#### 第四步：加约束，再并发一次

```sql
ALTER TABLE questions ADD CONSTRAINT questions_title_key UNIQUE (title);
```

```bash
python scripts/race_insert.py --title "并发测试标题2" --n 2
```

```
request-1: 201 Created  id=100003
request-2: 500 Internal Server Error    ← 数据库挡住了
```

服务端日志：

```
psycopg.errors.UniqueViolation: duplicate key value violates unique constraint
"questions_title_key"
DETAIL:  Key (title)=(并发测试标题2) already exists.
```

> 为什么数据库能挡住而应用层挡不住？
>
> 因为 `UNIQUE` 约束的检查和插入**是同一个原子操作**。没有窗口。数据库用索引上的锁保证了这一点——**这是数据库提供给你的，你在应用层无论怎么写都做不到。**

#### 第五步：把 500 改成 409（完成闭环）

现在体验还不对：用户看到的是 500。要把数据库异常翻译成业务异常。

```python
# app/services/question.py
from sqlalchemy.exc import IntegrityError

def create(conn, title, body, author_id):
    try:
        new_id = repo.insert(conn, title, body, author_id)
    except IntegrityError as e:
        if "questions_title_key" in str(e.orig):     # ← 靠约束名判断
            raise DuplicateTitle() from e
        raise
    return repo.find_detail(conn, new_id)
```

**三个要点**：

1. **查重的 `if` 删掉了。** 不是"两道保险更安全"，而是那道 `if` 给了你虚假的安全感，让你以为不需要约束。**留着它的唯一理由是：它能在高频重复的场景下省掉一次失败的插入。这是性能优化，不是正确性保证。**
2. **靠约束名判断，不靠错误文本。** 所以上面 DDL 里**每个约束都显式命名了**（`CONSTRAINT questions_title_key UNIQUE (title)`）。如果不命名，数据库会自动生成名字，换个数据库版本可能就变了。
   > 回收第 3 次课的判据：**依赖稳定标识（`type`、约束名），不依赖人类可读的文案。** 这是同一条规则的第三次出现。
3. **`from e` 保留异常链**，日志里能看到原始的数据库错误。

#### 第六步：把它升格成本课程的第四道结构性护栏

**醒目页，累加表**：

| 次课 | 护栏 | 它在结构上挡住了什么 | 绕不过它的原因 |
|---|---|---|---|
| 第 3 次课 | `response_model` | 没声明的字段出不去 | 序列化必经之路 |
| 第 4 次课 | 全局异常处理器 | 内部错误信息不泄漏 | 所有异常必经之路 |
| 第 5 次课 | Jinja2 自动转义 | 用户输入不变成可执行 HTML | 所有模板输出必经之路 |
| **第 6 次课** | **数据库约束** | **脏数据进不来** | **所有写入必经之路** |

> 第四道和前三道有一个重要区别，请特别注意：
>
> **前三道都在你的 Python 代码里。第四道在数据库里。**
>
> 这意味着它挡住的东西更多：
>
> | 谁在写数据 | 前三道护栏 | 数据库约束 |
> |---|---|---|
> | 你的 FastAPI 端点 | ✅ 挡得住 | ✅ |
> | AI 生成的新端点 | 看它有没有照着写 | ✅ |
> | 你手工在 psql 里执行的 UPDATE | ❌ | ✅ |
> | 数据导入脚本 / 迁移脚本 | ❌ | ✅ |
> | 另一个团队写的服务 | ❌ | ✅ |
> | 三年后没人记得那条规则的时候 | ❌ | ✅ |
>
> **判据：约束应该放在离数据最近的地方。** 越靠近数据，能绕过它的路径就越少。
>
> 这一条直接回答了本次课的课程主题问题：**AI 写的代码可能不遵守你的业务规则，但它绕不过数据库约束。** 你花 20 行 DDL 建立的护栏，会保护你之后所有的代码——包括你没审过的那些。

### 4.5 外键与 `ON DELETE`：四个选项的判据

**先讲为什么要外键。**

> 回到演示三：删掉用户，1876 条回答变成孤儿。加上外键之后：
>
> ```sql
> DELETE FROM users WHERE id = 42;
> -- ERROR: update or delete on table "users" violates foreign key constraint
> ```
>
> **外键的第一价值不是"级联删除"，是"不让你删出孤儿"。**

**`ON DELETE` 四个选项**（做成判据表）：

| 选项 | 行为 | 什么时候用 | 本项目哪里用 |
|---|---|---|---|
| `RESTRICT` / `NO ACTION` | **拒绝删除**父行 | 子数据是重要资产，删父行一定是误操作 | `questions.author_id` → 用户有问题就不许删 |
| `CASCADE` | 父行删了，**子行一起删** | 子行离开父行没有任何意义 | `answers.question_id`；`question_tags` 两个都是 |
| `SET NULL` | 父行删了，**子行的外键置为 NULL** | 子行本身有价值，但可以没有父 | `answers.author_id` → 用户注销，回答保留显示"已注销用户" |
| `SET DEFAULT` | 置为默认值 | 有一个"兜底的父行"（如"匿名用户"） | 本项目不用 |

**三个要讲的点**：

**一、`SET NULL` 要求这一列允许 NULL。**

> 看 DDL：`answers.author_id` 是**唯一一个没有 `NOT NULL`** 的外键。这不是遗漏，是 `ON DELETE SET NULL` 的必然要求。
>
> 代价：所有涉及 `answers.author_id` 的查询都要考虑 NULL。**单元 5 会看到这个代价具体是什么**——这是一个真实的取舍，不是免费的。

**二、`CASCADE` 是危险的便利。**

> `ON DELETE CASCADE` 在 `answers.question_id` 上是对的：删了问题，回答没有意义。
>
> 但你要知道它有多"能干"：删一个问题，可能连带删掉 500 条回答。**一条 DELETE 语句，一次性删掉大量数据，而且没有确认。**
>
> 判据：**`CASCADE` 只用在"子行的存在完全依附于父行"的关系上。** 如果你对"删父行要不要删子行"有一秒钟的犹豫，就用 `RESTRICT`——让它报错，然后由业务代码显式决定。
>
> **让错误响起来，比让它静默地做对更安全。**

**三、软删除的预告。**

> 你们会想到：真实产品里很少真的 `DELETE`，一般是打个 `deleted_at` 标记。对，这叫软删除。
>
> 但它有代价：**每一条查询都要记得加 `WHERE deleted_at IS NULL`**。忘一次就泄漏已删除内容。
>
> 这又是一个"依赖开发者记得"的做法——和我们的方向相反。
>
> 部分解法：用视图或 PostgreSQL 的行级安全策略把它变成结构性的。**C 档卡给结论，本课程不深入。**

### 4.6 `CHECK`：把业务规则写进数据库

```sql
CONSTRAINT questions_status_check CHECK (status IN ('open', 'closed', 'deleted')),
CONSTRAINT questions_title_len    CHECK (char_length(title) BETWEEN 5 AND 200),
CONSTRAINT questions_views_nonneg CHECK (view_count >= 0)
```

现场演示解剖台的脏枚举值：

```sql
SELECT status, count(*) FROM questions GROUP BY status;
--  open    | 68231
--  OPEN    |  1204          ← 大小写不一致
--  opened  |   312          ← 拼写不一致
--  (null)  | 30253          ← 根本没填
```

> 前端的筛选器写的是 `status = 'open'`，于是那 1516 条问题**在筛选里永远不出现**，而且没人知道。
>
> 加上 `CHECK` 之后，`'OPEN'` 直接被拒绝。**规则从"大家都记得写 'open'"变成了"数据库不接受别的值"。**

**但必须讲清 `CHECK` 的边界，否则学生会滥用**：

| 规则类型 | 放哪 | 例子 |
|---|---|---|
| 单行内、不变的规则 | **`CHECK`** | `view_count >= 0`；`status IN (...)`；`title` 长度 |
| 跨行的规则 | **不能用 CHECK** | "一个问题最多 5 个标签"——需要数别的行 |
| 会变的业务规则 | **不要用 CHECK** | "免费用户每天最多发 3 条"——策略会改，改 CHECK 要改表 |
| 需要查别的表 | **不能用 CHECK** | "作者必须是已验证用户" |

> **判据：`CHECK` 适合"物理上不可能"或"几年都不会变"的规则。**
>
> `view_count >= 0` 是物理规则——浏览量不可能是负数，永远不会变。
> "每天最多发 3 条"是运营策略——下个月可能就改成 5 条。
>
> 后者放在 `services/`，因为第 4 次课说过：**业务规则的位置是服务层。**

**还有一个和第 3 次课的关系要说清**：

> 你们会问：`title` 长度 5–200 这条，第 3 次课已经在 Pydantic schema 里写了 `Field(min_length=5, max_length=200)`。**现在又在数据库里写一遍，这不是重复吗？**
>
> 是重复，而且是**有意的重复**。两者的职责不同：
>
> | | Pydantic schema | 数据库 CHECK |
> |---|---|---|
> | 时机 | 请求进来时 | 写入时 |
> | 目的 | **给出好的错误信息**（422，指明哪个字段） | **保证数据不脏** |
> | 覆盖范围 | 只覆盖走 API 的写入 | 覆盖所有写入 |
> | 缺了它的后果 | 用户体验差（收到 500 而不是 422） | 数据可能脏 |
>
> **判据：schema 负责体验，约束负责正确性。两者都要，不要指望一个替代另一个。**
>
> 唯一要注意的是**两处的数字要一致**。这是一个真实的维护负担。缓解办法：在 `docs/decisions.md` 里记一条，说明这两处必须同步。**第 7 次课用 ORM 模型定义表之后，这个重复会减少一部分**（模型上可以同时生成约束和 schema）。

### 4.7 已经脏了的数据怎么办

> 现在有个现实问题：**我们的数据库里已经有 30253 条 `status` 为 NULL 的问题。加约束会直接失败。**

```sql
ALTER TABLE questions ADD CONSTRAINT questions_status_check
  CHECK (status IN ('open','closed','deleted'));
-- ERROR: check constraint "questions_status_check" is violated by some row
```

**正确顺序（三步，做成一页）**：

```sql
-- 1. 先看有多少、都是什么
SELECT status, count(*) FROM questions
WHERE status IS NULL OR status NOT IN ('open','closed','deleted')
GROUP BY status;

-- 2. 修数据（这一步需要业务判断，不是技术问题）
UPDATE questions SET status = 'open'   WHERE status IS NULL;
UPDATE questions SET status = lower(status) WHERE status <> lower(status);
UPDATE questions SET status = 'open'   WHERE status = 'opened';

-- 3. 再加约束
ALTER TABLE questions ALTER COLUMN status SET NOT NULL;
ALTER TABLE questions ADD CONSTRAINT questions_status_check
  CHECK (status IN ('open','closed','deleted'));
```

> 三个要点：
>
> 1. **第 2 步是业务决定，不是技术决定。** `status IS NULL` 的那 3 万条，到底该是 `open` 还是 `deleted`？**你得去问产品，或者去看它们的其他字段推断。** 这不是你能自己拍的。
> 2. **加约束会失败，这是好事。** 它告诉你"有数据不符合你以为的规则"。如果数据库允许你加一个被违反的约束，那约束就毫无意义。
> 3. **这三步应该写在迁移脚本里，一起执行，一起回滚。** → **第 7 次课的 Alembic。**
>
> **判据：越早加约束越便宜。** 空表上加约束是一行 DDL；十万行脏数据上加约束是一次数据考古 + 一次业务决策 + 一次大表锁。
>
> 这就是为什么建模错误比查询错误严重：**查询错了改代码，建模错了改数据。**

### 材料

- tag `v6-bad-schema`（起始，AI 原样 DDL + 十万行脏数据）、`v6-schema`（本单元结束）。
- `scripts/seed_large.py`：生成 10 万问题 / 30 万回答 / 2000 用户，**含有意制造的脏数据**（NULL status、大小写不一的枚举、重复标题、孤儿 author_id）。**必须可重复执行且结果确定（固定随机种子）。**
- `scripts/race_insert.py`：并发打 N 个相同标题的 POST，输出各自状态码。
- **封面级素材**：4.4 第二步的 TOCTOU 时序图。
- **封面级素材**：4.4 第三步的"两类并发 bug 对照表"（与第 5 次课并列）。
- **封面级素材**：4.4 第六步的"四道护栏累加表" + "谁能绕过哪道护栏"的六行表。
- 截图：并发插入前后的两次结果（两个 201 / 一个 201 一个 409）。
- 截图：`SELECT status, count(*)` 的脏枚举分布。
- 截图：加约束失败的报错。

---

## 五、现场必做：NULL 三值逻辑

**约 12 分钟。本次课第二高光，必须做成定量。**

### 5.1 先制造现象，不解释

我们刚才给 `answers.author_id` 配了 `ON DELETE SET NULL`。现在有一些回答的作者是 NULL（用户注销了）。

**任务**：统计"不是由管理员写的回答"有多少条。

```sql
-- 先看总数与分布
SELECT count(*) FROM answers;                              -- 300000
SELECT count(*) FROM answers WHERE author_id IS NULL;      -- 2143

-- 管理员的 user id 是 1
SELECT count(*) FROM answers WHERE author_id != 1;
-- 291504
```

**让学生自己算**：300000 - (author_id = 1 的条数)。

```sql
SELECT count(*) FROM answers WHERE author_id = 1;   -- 6353
```

300000 − 6353 = **293647**，但查询返回的是 **291504**。

**差 2143 条。正好是 author_id 为 NULL 的条数。**

> **`WHERE author_id != 1` 没有返回 author_id 为 NULL 的行。**
>
> 而且注意：**没有报错，没有警告。** 你得到了一个看起来完全正常的数字，它只是少了 2143。
>
> 如果这是一张报表、一次对账、一次数据导出，**你会带着这个错误的数字做决定**。

### 5.2 解释：SQL 里有三个真值，不是两个

**醒目页**：

> **SQL 的逻辑不是二值的（真/假），是三值的：TRUE / FALSE / UNKNOWN。**
>
> **任何与 NULL 的比较，结果都是 UNKNOWN。**
>
> **`WHERE` 只保留结果为 TRUE 的行。UNKNOWN 和 FALSE 一样被丢弃。**

真值表：

| 表达式 | 结果 | `WHERE` 会保留吗 |
|---|---|---|
| `1 = 1` | TRUE | ✅ |
| `1 = 2` | FALSE | ❌ |
| `NULL = 1` | **UNKNOWN** | ❌ |
| `NULL != 1` | **UNKNOWN** | ❌ |
| `NULL = NULL` | **UNKNOWN** | ❌ |
| `NULL IS NULL` | TRUE | ✅ |

> 关键在第三、四行：**`NULL = 1` 和 `NULL != 1` 都不是 TRUE。**
>
> 直觉上"等于1"和"不等于1"应该覆盖所有情况。**在 SQL 里它们加起来漏掉了 NULL。**
>
> 为什么？因为 NULL 的含义不是"空值"，是**"未知"**。"未知的那个值等于 1 吗？"——答案是"不知道"。"未知的那个值不等于 1 吗？"——还是"不知道"。
>
> 一旦你把 NULL 读成"未知"而不是"空"，三值逻辑就全都讲得通了。

### 5.3 三个高频陷阱（**逐个现场演示**）

#### 陷阱一：`!=` / `NOT IN` 漏行（已演示）

**三种修法**：

```sql
-- 修法 A：显式带上 NULL（最直白）
WHERE author_id != 1 OR author_id IS NULL

-- 修法 B：IS DISTINCT FROM（PostgreSQL，语义最准）
WHERE author_id IS DISTINCT FROM 1

-- 修法 C：从根上解决——让这一列 NOT NULL
-- （本例做不到，因为业务要求 SET NULL）
```

> **优先级：C > B > A。**
>
> C 是从根上消除问题。B 正确且简洁，但 MySQL 不支持（MySQL 用 `<=>` 的取反）。A 到处都能用，但每个查询都要写，**又是一个"依赖记得"的做法**。

#### 陷阱二：`NOT IN` 子查询含 NULL → 结果全空（**最恶劣的一个，必须单独演示**）

任务：查出"从来没写过回答的用户"。

```sql
SELECT count(*) FROM users
WHERE id NOT IN (SELECT author_id FROM answers);
-- 0
```

> **返回 0。** 也就是"每个用户都写过回答"。

验证这是错的：

```sql
SELECT count(*) FROM users;   -- 2000
SELECT count(DISTINCT author_id) FROM answers;  -- 1631
-- 明明有 369 个用户没写过回答
```

**解释（做成一页，一步步展开）**：

> 子查询 `SELECT author_id FROM answers` 的结果里**包含 NULL**（那 2143 条注销用户的回答）。
>
> 于是对某个用户 id = 7：
>
> ```
> 7 NOT IN (1, 3, 5, NULL, ...)
>   = NOT (7 = 1 OR 7 = 3 OR 7 = 5 OR 7 = NULL OR ...)
>   = NOT (FALSE OR FALSE OR FALSE OR UNKNOWN OR ...)
>   = NOT UNKNOWN
>   = UNKNOWN            ← 不是 TRUE，所以这一行被丢掉
> ```
>
> **只要子查询结果里有一个 NULL，`NOT IN` 对所有行都返回 UNKNOWN，结果集必然为空。**
>
> 注意这个 bug 的性质：它不是"少了几行"，是**"一行都没有"**。返回 0 条，而且返回得干干净净。
>
> 你可能会想"返回 0 条这么明显，一定能发现"。不一定——如果这是个"给没写过回答的用户发提醒邮件"的定时任务，**它的正常表现就是"今天没有人需要提醒"。** 它可以静默失效几个月。

**修法（三种，给出明确推荐）**：

```sql
-- 修法 A：子查询里排掉 NULL
WHERE id NOT IN (SELECT author_id FROM answers WHERE author_id IS NOT NULL)

-- 修法 B：改用 NOT EXISTS（推荐）
WHERE NOT EXISTS (SELECT 1 FROM answers a WHERE a.author_id = users.id)

-- 修法 C：LEFT JOIN + IS NULL
LEFT JOIN answers a ON a.author_id = users.id WHERE a.id IS NULL
```

> **推荐修法 B。三个理由：**
>
> 1. **`NOT EXISTS` 对 NULL 天然免疫**——它判断的是"有没有匹配的行"，不做值比较；
> 2. 它通常也更快（可以提前短路，找到一行就停）；
> 3. 它的语义更贴近你想表达的东西："不存在这样的回答"。
>
> **判据：想表达"不存在"的时候，用 `NOT EXISTS`，不要用 `NOT IN`。**
>
> 这条规则简单到可以无条件遵守，**建议直接写进团队规范**。

#### 陷阱三：聚合函数忽略 NULL

```sql
SELECT count(*)         FROM answers;   -- 300000
SELECT count(author_id) FROM answers;   -- 297857   ← 少 2143
SELECT count(DISTINCT author_id) FROM answers;  -- 1631（不含 NULL）
```

```sql
-- 更隐蔽的：AVG 的分母
SELECT avg(score) FROM answers;   -- 分母是"score 非 NULL 的行数"，不是总行数
```

> **`count(*)` 数行，`count(列)` 数该列非 NULL 的值。** 这两个几乎总被混用。
>
> `SUM` / `AVG` / `MAX` 也都忽略 NULL。`AVG` 最危险，因为**分母悄悄变了**：如果一半的 score 是 NULL，你算出的"平均分"只是有分那一半的平均。
>
> **判据：想数行就 `count(*)`；想数"有值的"才用 `count(列)`，而且要在代码注释里说明这是有意的。**

再补一条容易忽略的：

```sql
-- NULL 参与算术，结果是 NULL
SELECT view_count + 1 FROM questions WHERE view_count IS NULL;   -- NULL
-- 想"浏览量+1"，结果整个字段变成了 NULL
UPDATE questions SET view_count = view_count + 1 WHERE id = 5;
-- 如果原值是 NULL，更新后还是 NULL，计数永远不动
```

> 这就是 4.3 里 `view_count NOT NULL DEFAULT 0` 的理由。**约束不只是防脏数据，它还让你的算术能用。**

### 5.4 `UNIQUE` 与 NULL（一个反直觉的点）

```sql
-- users.email 上有 UNIQUE 约束，但如果它允许 NULL：
INSERT INTO users (email, ...) VALUES (NULL, ...);   -- OK
INSERT INTO users (email, ...) VALUES (NULL, ...);   -- 也 OK！
```

> **标准 SQL 下，多个 NULL 不算重复**——因为"未知 = 未知"是 UNKNOWN，不是 TRUE。
>
> 后果：一个允许 NULL 的 `UNIQUE` 列，可以有无限多行是 NULL。
>
> 这是一个常见的意外。判据：**`UNIQUE` 列通常应该同时 `NOT NULL`**，除非你明确想要"多行可以没填"的语义。
>
> 〔PostgreSQL 15+ 支持 `UNIQUE NULLS NOT DISTINCT` 改变这个行为。C 档卡。〕

### 5.5 结论卡：NULL 的四条纪律

**醒目页，这是本单元要带走的东西**：

> 1. **默认 `NOT NULL`。** 允许 NULL 必须有明确理由，且理由要写进 `decisions.md`。
> 2. **不存在性判断用 `NOT EXISTS`，永远不用 `NOT IN`。**
> 3. **`!=` 遇到可空列时，要么 `IS DISTINCT FROM`，要么显式 `OR ... IS NULL`。**
> 4. **数行用 `count(*)`。** 用 `count(列)` 必须是有意的。

然后收一句：

> 你可能觉得这四条很琐碎。但请注意它们的共同点：
>
> **这四类错误全部不报错。** 它们返回一个语法正确、结构正确、看起来完全正常的结果集——只是数字是错的。
>
> 第 5 次课那类错误（阻塞）用压测能发现。**这类错误只能靠"知道它存在"来发现。** 所以它必须被记成纪律，而不是靠临场判断。
>
> 顺带说 AI：**你让 AI 写一个"找出没写过回答的用户"的查询，它给 `NOT IN` 的概率相当高**，因为那是教材里最常见的写法。这个查询会返回 0 条，而 AI 不会告诉你为什么。**作业里你要亲自验证这一点。**

### 材料

- **封面级素材**：5.1 的"漏行"定量对照：三个数字（300000 / 6353 / 291504）+ 一个红色的"差 2143"。
- **封面级素材**：三值真值表六行，第 3、4 行高亮。
- **高光图**：`NOT IN` 含 NULL 的推导过程，逐步展开成四行。
- 截图：`NOT IN` 返回 0 条的 psql 输出；改 `NOT EXISTS` 后返回 369 条的输出，并排。
- 截图：`count(*)` vs `count(author_id)` 的对照。

---

## 六、8 条业务 SQL

**约 20 分钟。这是 A 档实操主体，请按"每条 SQL 解决一个具体页面需求"来组织，不要做成语法教程。**

### 6.0 先给一张地图：SQL 的逻辑执行顺序

**这一页要放在所有 SQL 之前，因为后面两个陷阱都要用它解释。**

```
你写的顺序：    SELECT → FROM → JOIN → WHERE → GROUP BY → HAVING → ORDER BY → LIMIT
数据库的顺序：  FROM → JOIN → WHERE → GROUP BY → HAVING → SELECT → ORDER BY → LIMIT
                                                            ↑
                                              SELECT 在倒数第三步才执行
```

> 这不是数据库真实的物理执行顺序（优化器会重排），是**逻辑顺序**——它决定了"哪一步能看到什么"。
>
> 它能解释两件否则很费解的事：
>
> **一、为什么 `WHERE` 里不能用 `SELECT` 的别名：**
>
> ```sql
> SELECT count(*) AS n FROM answers GROUP BY question_id WHERE n > 5;  -- ✗
> --                                                           ↑ WHERE 先执行，那时 n 还不存在
> SELECT count(*) AS n FROM answers GROUP BY question_id HAVING count(*) > 5;  -- ✓
> ```
>
> **二、为什么 `ORDER BY` 里可以用别名：** 因为 `ORDER BY` 在 `SELECT` 之后。
>
> **三、`WHERE` 和 `HAVING` 的区别，一句话就够：** `WHERE` 在分组前过滤行，`HAVING` 在分组后过滤组。

### 6.1 SQL #1：列表页 —— 稳定排序分页

```sql
-- 需求：问题列表，按时间倒序，第 N 页
SELECT q.id, q.title, q.created_at, q.view_count,
       u.id AS author_id, u.display_name
FROM questions q
JOIN users u ON u.id = q.author_id
WHERE q.status = 'open'
ORDER BY q.created_at DESC, q.id DESC      -- ← 注意第二个排序键
LIMIT 20 OFFSET 40;
```

### 6.2 为什么必须有第二个排序键（**开场现象三的答案，必须现场演示**）

**先复现问题。** 把 `, q.id DESC` 去掉，翻两页：

```bash
psql -c "SELECT id FROM questions WHERE status='open' \
         ORDER BY created_at DESC LIMIT 20 OFFSET 40" > p3.txt
psql -c "SELECT id FROM questions WHERE status='open' \
         ORDER BY created_at DESC LIMIT 20 OFFSET 60" > p4.txt
sort p3.txt p4.txt | uniq -d
# 87341     ← 第 3 页和第 4 页都有它
```

**解释（醒目页）**：

> seed 数据里有很多问题的 `created_at` 完全相同（批量导入的）。
>
> `ORDER BY created_at DESC` 只规定了**不同时间之间**的顺序。对于**时间相同的那些行，SQL 标准不保证任何顺序**——数据库可以每次返回不同的顺序，而且这是合规的。
>
> 于是：
> - 第 3 页查询时，87341 恰好排在第 55 位 → 出现在第 3 页
> - 第 4 页查询时（另一次执行），87341 恰好排在第 62 位 → 又出现在第 4 页
> - **而另一条记录，两次都没进窗口，用户永远看不到它**
>
> **判据：`LIMIT/OFFSET` 必须配一个能完全确定顺序的 `ORDER BY`。**
>
> 做法：**在排序键后面加上主键。** 主键唯一，所以整体顺序唯一确定。
>
> 这条规则简单到可以无条件遵守：**任何带 `LIMIT` 的查询，`ORDER BY` 的最后一项都是主键。**

再追加一句，把它接到后面：

> 顺便说：即使加了稳定排序，`OFFSET` 分页还有两个问题——
>
> 1. **翻页期间有新数据插入，还是会重复或漏**（因为 OFFSET 是按位置数的）；
> 2. **`OFFSET 100000` 本身就慢**（数据库必须扫过前 10 万行再丢掉）。
>
> 彻底的解法叫 **keyset 分页**（用"上一页最后一条的 id"代替 offset）。**→ 第 11 次课。** 今天先把稳定排序做对。

### 6.3 SQL #2：列表页带回复数 —— LEFT JOIN + GROUP BY

```sql
SELECT q.id, q.title, q.created_at,
       u.display_name,
       count(a.id) AS answer_count          -- ← count(a.id) 不是 count(*)
FROM questions q
JOIN users u ON u.id = q.author_id
LEFT JOIN answers a ON a.question_id = q.id
WHERE q.status = 'open'
GROUP BY q.id, q.title, q.created_at, u.display_name
ORDER BY q.created_at DESC, q.id DESC
LIMIT 20;
```

**三个必须讲的点**：

**一、为什么是 `LEFT JOIN` 不是 `JOIN`。**

把它改成 `JOIN` 试一次：**没有回答的问题全部消失了。** 列表页只显示有人回答过的问题。

> `JOIN`（内连接）只保留两边都匹配的行。零回答的问题在 `answers` 里没有对应行，所以被丢掉。
>
> **判据：需要"主表全部保留，附表可有可无"时用 `LEFT JOIN`。**

**二、为什么是 `count(a.id)` 不是 `count(*)`。**

把它改成 `count(*)`：**零回答的问题显示 `1` 而不是 `0`。**

> `LEFT JOIN` 没匹配上时，会给 `a.*` 全部填 NULL，**但那一行仍然存在**。`count(*)` 数行，就数到了这 1 行。`count(a.id)` 数非 NULL 值，得到 0。
>
> **这是单元 5 那条纪律的反向应用：** 大多数时候用 `count(*)`，但 `LEFT JOIN` 之后要数附表的行时，必须用 `count(附表.主键)`。
>
> 记法：**`count(*)` 数的是"连接后的行"，`count(a.id)` 数的是"真实存在的 a"。**

**三、`GROUP BY` 要列出所有非聚合的 SELECT 列。**

> 少一个 PostgreSQL 直接报错（MySQL 默认配置下不报错，返回任意值——**又一个"不报错更危险"的例子**）。
>
> 简化写法：`GROUP BY q.id, u.display_name` 在 PostgreSQL 里就够了，因为 `q.id` 是主键，其他 `q.*` 列**函数依赖**于它。这是 PG 的一个便利特性。

### 6.4 SQL #3：标签筛选（M:N）—— 两种语义要分清

```sql
-- 3a：含有任意一个指定标签（OR 语义）
SELECT DISTINCT q.id, q.title
FROM questions q
JOIN question_tags qt ON qt.question_id = q.id
JOIN tags t           ON t.id = qt.tag_id
WHERE t.name = ANY(ARRAY['python', 'sql'])
ORDER BY q.id DESC
LIMIT 20;
```

```sql
-- 3b：同时含有全部指定标签（AND 语义）—— 注意 HAVING
SELECT q.id, q.title
FROM questions q
JOIN question_tags qt ON qt.question_id = q.id
JOIN tags t           ON t.id = qt.tag_id
WHERE t.name = ANY(ARRAY['python', 'sql'])
GROUP BY q.id, q.title
HAVING count(DISTINCT t.id) = 2            -- ← 匹配上的标签数 = 要求的标签数
ORDER BY q.id DESC
LIMIT 20;
```

> **3a 和 3b 是完全不同的需求，但代码只差一个 `HAVING`。**
>
> 我见过很多项目的标签筛选写成了 3a，而产品要的是 3b。用户勾选"Python + 性能优化"，期待看到同时有这两个标签的问题，结果看到一堆只有 Python 的。**这个 bug 不会报错，只会被用户默默忍受。**
>
> 3b 的思路值得记住：**`WHERE` 先把范围缩到"这几个标签"，`GROUP BY` 按问题聚合，`HAVING` 检查"匹配上的标签数是否等于要求的个数"。** 这是"关系除法"的标准写法。
>
> 注意 `count(DISTINCT t.id)`——如果连接表允许重复（回忆 3.2：没加复合主键的话），不加 `DISTINCT` 会算多。**又一次看到约束如何简化查询。**

### 6.5 SQL #4：聚合排行

```sql
-- 需求：回答数最多的 10 个活跃用户（排除注销用户）
SELECT u.id, u.display_name,
       count(a.id)                              AS answer_count,
       count(a.id) FILTER (WHERE a.is_accepted) AS accepted_count
FROM users u
JOIN answers a ON a.author_id = u.id
WHERE a.created_at >= now() - interval '30 days'
GROUP BY u.id, u.display_name
HAVING count(a.id) >= 3
ORDER BY accepted_count DESC, answer_count DESC, u.id
LIMIT 10;
```

两个要点：

> **一、`FILTER (WHERE ...)` 是条件聚合。** 在同一次扫描里算出"总数"和"其中被采纳的数"。
>
> 通用写法是 `sum(CASE WHEN a.is_accepted THEN 1 ELSE 0 END)`，`FILTER` 是 PG 的语法糖，更好读。MySQL 用 `SUM(条件)`。
>
> **二、注意 `WHERE a.created_at >= ...` 和 `HAVING count(...) >= 3` 的分工。** 前者在分组前筛行（只看最近 30 天的回答），后者在分组后筛组（只要回答数≥3 的用户）。**这是 6.0 那张顺序图的直接应用。**

### 6.6 SQL #5：关键词搜索

```sql
SELECT q.id, q.title, q.created_at
FROM questions q
WHERE q.status = 'open'
  AND (q.title ILIKE '%' || :kw || '%' OR q.body ILIKE '%' || :kw || '%')
ORDER BY q.created_at DESC, q.id DESC
LIMIT 20;
```

**两个必须讲的点**：

**一、参数化，绝不拼字符串。**

```python
# ✅ 参数化
conn.execute(text("... WHERE title ILIKE :kw"), {"kw": f"%{keyword}%"})

# ❌ 拼接 —— SQL 注入
conn.execute(text(f"... WHERE title ILIKE '%{keyword}%'"))
```

> 用户搜索 `'; DROP TABLE questions; --` 会发生什么，**第 15 次课完整演示**。今天只要建立纪律：
>
> **判据：SQL 里的任何值都走参数，一个例外都没有。**
>
> 顺带说一个例外情况的正确做法：**表名、列名、排序方向不能参数化**（参数只能是值）。如果排序字段来自用户输入，正确做法是**白名单映射**：
>
> ```python
> SORT_MAP = {"latest": "q.created_at DESC", "views": "q.view_count DESC"}
> order_by = SORT_MAP.get(sort_key, SORT_MAP["latest"])   # 不在白名单就用默认
> ```
>
> 直接把用户传的 `sort` 拼进 SQL 是注入。**第 7 次课的解剖台会有这个反例。**

**二、`ILIKE '%kw%'` 用不上索引。**

> 前缀匹配 `'kw%'` 能用 B 树索引，**两边都有 `%` 的不能**——索引是按前缀排序的，没有前缀就没法定位。
>
> 所以这条查询在十万行下是全表扫描。单元 7 会量到它有多慢。
>
> 真正的解法是全文检索（PG 的 `tsvector` + GIN 索引，或者外部的搜索引擎）。**→ 第 11 次课。** 今天先知道"模糊搜索用不上普通索引"这个结论。

### 6.7 SQL #6：存在性判断（三种写法的判据）

```sql
-- 需求：当前用户有没有回答过这个问题
SELECT EXISTS (
    SELECT 1 FROM answers WHERE question_id = :qid AND author_id = :uid
) AS has_answered;
```

| 写法 | 什么时候用 |
|---|---|
| `EXISTS (SELECT 1 ...)` | **判断"有没有"**。找到一行就停，不关心有几行 |
| `count(*) > 0` | 不要用来判断存在性——它会数完所有行 |
| `IN (子查询)` | 子查询结果小且**确定无 NULL** 时可用 |
| `NOT EXISTS` | **判断"没有"。永远优先于 `NOT IN`**（单元 5.3） |

### 6.8 SQL #7：时间窗口统计

```sql
-- 需求：最近 14 天每天的新问题数（没有问题的日期也要出现，值为 0）
SELECT d::date AS day, count(q.id) AS n
FROM generate_series(
        current_date - interval '13 days', current_date, interval '1 day') AS d
LEFT JOIN questions q
       ON q.created_at >= d AND q.created_at < d + interval '1 day'
GROUP BY d
ORDER BY d;
```

> 这条 SQL 的价值在**"没有数据的日期也要出现"**这个需求上。
>
> 如果直接 `GROUP BY date(created_at)`，零问题的那天**整行消失**，前端画折线图会把两个不相邻的日期连起来，**趋势图就是错的**。
>
> 做法：先用 `generate_series` 造出完整的日期序列，再 `LEFT JOIN` 真实数据。
>
> **判据：报表类查询要先确定"横轴"，再去 join 数据，不要让数据决定横轴。**
>
> 〔MySQL 没有 `generate_series`，要用日期维度表或应用层补齐。C 档卡。〕

### 6.9 SQL #8：写入并返回

```sql
-- 需求：浏览量 +1，并返回新值
UPDATE questions
SET view_count = view_count + 1
WHERE id = :qid
RETURNING id, view_count;
```

**两个要点**：

> **一、`RETURNING` 让"写+读"变成一次往返。** 不用先 UPDATE 再 SELECT——那是两次往返，而且中间可能被别人改了。
>
> **二、`view_count = view_count + 1` 是原子的。** 对比这种写法：
>
> ```python
> row = conn.execute("SELECT view_count FROM questions WHERE id=:id").fetchone()
> conn.execute("UPDATE questions SET view_count = :v", {"v": row.view_count + 1})
> ```
>
> 这是**单元 4.4 那个 TOCTOU 问题的又一个实例**：两个并发请求都读到 100，都写入 101，**丢了一次计数**。
>
> 而 `SET view_count = view_count + 1` 把读和写放在一条语句里，由数据库保证原子性。
>
> **判据：能用一条语句表达的更新，不要拆成"读-改-写"。**
>
> 请注意这已经是今天第三次看到同一个模式了：查重、计数、还有单元 5 提到的。**"先读后写"在并发下都不可靠。** 这是本次课的一条暗线。

### 材料

- `docs/sql8.sql`：八条 SQL 的完整可执行版本，**每条带注释说明它服务哪个页面需求**。
- 高光图：SQL 逻辑执行顺序图（两行对照 + 箭头指向 SELECT）。
- **封面级素材**：6.2 的翻页重复演示——两页 id 列表并排，重复的那个 id 红框。
- 截图：`JOIN` vs `LEFT JOIN` 的结果条数对照；`count(*)` vs `count(a.id)` 的 0/1 对照。
- 截图：3a 与 3b 的结果条数对照（**同一组标签，结果差很多**）。

---

## 七、索引：三条规则 + 十万行实测

**约 15 分钟。本次课第三高光。**

### 7.1 先量一次，建立基线

```sql
EXPLAIN ANALYZE
SELECT * FROM questions WHERE status = 'open'
ORDER BY created_at DESC, id DESC LIMIT 20;
```

```
Limit  (cost=8934.21..8934.26 rows=20)  (actual time=1831.442..1831.449 rows=20)
  ->  Sort  (cost=8934.21..9105.88 rows=68671)
        Sort Key: created_at DESC, id DESC
        Sort Method: top-N heapsort  Memory: 27kB
        ->  Seq Scan on questions  (actual time=0.019..412.338 rows=68671)
              Filter: (status = 'open'::text)
              Rows Removed by Filter: 31329
Planning Time: 0.142 ms
Execution Time: 1831.503 ms
```

### 7.2 `EXPLAIN` 只看一件事

**醒目页，本单元的边界声明**：

> **`EXPLAIN` 输出很复杂。今天你只需要看一个词：**
>
> **`Seq Scan`（全表扫描）还是 `Index Scan` / `Bitmap Index Scan`（走了索引）？**
>
> 看到 `Seq Scan` 出现在大表上，就是信号。其他所有东西——cost 的两个数字怎么算、rows 怎么估、buffers 是什么、为什么选了 hash join——**今天全部不看。**

为什么划这条线：

> 因为读懂 cost 模型需要知道数据库的存储结构、统计信息、代价参数，那是内核内容。**而它们不影响你今天要做的决定。**
>
> 你今天要做的决定是"加不加索引、加在哪几列"。**这个决定用三条规则就能定，不需要看执行计划。** 执行计划只是用来验证"我加的索引生效了吗"。
>
> 判据：**先按规则加索引，再用 EXPLAIN 验证走没走。** 不要反过来——不要先跑 EXPLAIN 再猜。

补一句关于 `ANALYZE`：

> `EXPLAIN` 只给估算计划，`EXPLAIN ANALYZE` 会**真的执行**并给出实际耗时和实际行数。
>
> **注意：`EXPLAIN ANALYZE` 对 `UPDATE`/`DELETE` 会真的改数据。** 要看写语句的计划，请包在 `BEGIN; ... ROLLBACK;` 里。

### 7.3 三条规则（**本单元核心**）

**醒目页，字要大**：

> **规则一：每个外键列都建索引。**
> **规则二：常用于 `WHERE` 过滤的列建索引。**
> **规则三：常用于 `ORDER BY` 的列建索引，且和过滤列组成复合索引。**

逐条给理由：

#### 规则一：外键列

```sql
CREATE INDEX idx_questions_author   ON questions   (author_id);
CREATE INDEX idx_answers_question   ON answers     (question_id);
CREATE INDEX idx_answers_author     ON answers     (author_id);
CREATE INDEX idx_qtags_tag          ON question_tags (tag_id);
```

> **重要提示：数据库不会自动给外键列建索引。** 它只给主键和 `UNIQUE` 自动建。
>
> 外键列没索引有两个后果，第二个很多人不知道：
>
> 1. `WHERE question_id = 5` 要全表扫描（这个大家都知道）；
> 2. **删除父行时会全表扫子表。** 删一个问题，数据库要检查 `answers` 里有没有引用它 → 三十万行全扫。有 `CASCADE` 的话还要扫一遍去删。
>
> **一个"删除一个问题"的操作可能慢到几秒钟，仅仅因为外键列没索引。**
>
> 注意 `question_tags`：复合主键 `(question_id, tag_id)` 自带了一个以 `question_id` 开头的索引，所以按问题查标签很快。**但按标签查问题用不上它**（最左前缀，见 7.4），所以要单独给 `tag_id` 建索引。
>
> **这条规则可以无脑执行，而且可以机械检查** —— 作业里要写这个检查。

#### 规则二 + 规则三：过滤列与排序列

回到 7.1 那条慢查询：`WHERE status = 'open' ORDER BY created_at DESC, id DESC`。

```sql
CREATE INDEX idx_questions_status_created
    ON questions (status, created_at DESC, id DESC);
```

再测：

```
Limit  (actual time=0.048..0.071 rows=20)
  ->  Index Scan using idx_questions_status_created on questions
        Index Cond: (status = 'open'::text)
Execution Time: 0.094 ms
```

**1831 ms → 0.09 ms，快了约 19000 倍。**

**关键要讲清"为什么排序也能用上索引"**：

> 注意执行计划里**没有 `Sort` 那一步**了。
>
> 索引本身是**有序存储**的。索引 `(status, created_at DESC, id DESC)` 里，`status='open'` 的那一段天然就是按 `created_at DESC, id DESC` 排好的。
>
> 数据库只需要：定位到 `status='open'` 的起点 → 顺着读 20 行 → 结束。
>
> **它读了 20 行，不是 10 万行。** 这就是 19000 倍的来源。
>
> 对比之前：扫 10 万行 → 筛出 68671 行 → 全部排序 → 取前 20。**"排序 68671 行只为了拿 20 行"是最典型的浪费。**

### 7.4 复合索引的列顺序（**最高频的错误**）

**醒目页**：

> **复合索引 `(a, b, c)` 能服务的查询：**
>
> - `WHERE a = ?` ✅
> - `WHERE a = ? AND b = ?` ✅
> - `WHERE a = ? AND b = ? AND c = ?` ✅
> - `WHERE a = ? ORDER BY b` ✅
> - `WHERE b = ?` ❌ **用不上**
> - `WHERE c = ?` ❌ **用不上**
>
> **这叫最左前缀。索引像电话簿：按"姓, 名"排序，你能快速找"张某某"，但没法快速找"所有叫小明的"。**

**列顺序的判据**：

> **等值过滤的列放前面，范围/排序的列放后面。**
>
> `(status, created_at DESC)` ✅ —— status 等值，created_at 排序
> `(created_at DESC, status)` ❌ —— 定位到 status 需要扫过所有时间
>
> 现场可以验证一次：建反向的索引，看 EXPLAIN 里是否仍出现 `Sort` 或 `Filter`。

### 7.5 索引的代价（**必须讲，否则学生会给每列都加索引**）

| 代价 | 说明 |
|---|---|
| **写入变慢** | 每次 INSERT/UPDATE/DELETE 都要维护所有相关索引。5 个索引 ≈ 写入慢几倍 |
| **占空间** | 索引大小常常接近甚至超过表本身 |
| **建索引要锁** | 大表上 `CREATE INDEX` 会阻塞写入。生产环境用 `CREATE INDEX CONCURRENTLY` |
| **可能不被使用** | 选择性差的列（如布尔值、只有两种取值的 status）索引价值很低 |

**判据表**：

| 情况 | 加不加 |
|---|---|
| 外键列 | **一定加** |
| 高频 `WHERE` 且区分度高（如 email、user_id） | **加** |
| 高频 `ORDER BY` + 过滤，组成复合索引 | **加** |
| 只有 2–3 种取值的列，单独加 | **不加**（除非配合部分索引） |
| 从没出现在 `WHERE`/`ORDER BY`/`JOIN` 里的列 | **不加** |
| `LIKE '%kw%'` 涉及的列 | **加了也没用** → 第 11 次课 |

顺带给两个结论（**不展开**）：

> **部分索引**：如果 99% 的查询都带 `status='open'`，可以建 `CREATE INDEX ... WHERE status='open'`——索引更小更快。PG 支持，MySQL 不支持。
>
> **深分页**：即使索引完美，`OFFSET 100000` 仍然要顺着索引读过 10 万条再丢掉。索引解决不了这个。**→ 第 11 次课 keyset 分页。**

### 7.6 B 档：完整的前后对照表

**这是作业一要交的东西，课上先跑两行做示范。**

| 查询 | 索引前 | 索引后 | 用到的索引 | 计划变化 |
|---|---|---|---|---|
| 列表页（status + 时间排序） | 1831 ms | 0.09 ms | `idx_questions_status_created` | Seq Scan + Sort → Index Scan |
| 某问题的回答列表 | 89 ms | 0.31 ms | `idx_answers_question` | Seq Scan → Index Scan |
| 某用户的问题列表 | 412 ms | 0.24 ms | `idx_questions_author` | Seq Scan → Index Scan |
| 标签筛选 | 2140 ms | 3.2 ms | `idx_qtags_tag` | Seq Scan → Bitmap Index Scan |
| 删除一个问题（30 回答） | 1650 ms | 4.1 ms | `idx_answers_question` | 外键检查从全表扫变索引扫 |
| 关键词搜索 `ILIKE '%x%'` | 1520 ms | **1498 ms** | **无** | **Seq Scan → Seq Scan（没变）** |

〔制作团队：请在演示机上实测填入真实数据。最后一行**必须保留**——它证明"不是所有慢查询都能靠索引解决"，是通往第 11 次课的桥。〕

**讲最后一行**：

> 注意最后一行：加了索引**没有任何改善**。
>
> 这一行的教育价值可能是整张表里最高的：**索引不是万能的。** `LIKE '%kw%'` 从根本上用不上 B 树索引，这不是"索引建错了"，是这类查询和这类索引结构不匹配。
>
> **判据：看到加了索引没效果，先问"这个查询能不能用上这种索引"，而不是再加一个索引。**

### 材料

- `docs/indexes.sql`：全部索引的 DDL，**每条带注释说明它服务哪条查询**。
- `scripts/bench_sql.py`：对给定 SQL 跑 N 次取中位数，输出耗时与计划节点类型（**避免学生手工 `\timing` 的抖动**）。
- **封面级素材**：7.6 那张六行对照表，第一行的 `1831 → 0.09` 与最后一行的 `1520 → 1498` 都高亮（一个成功、一个无效）。
- **封面级素材**：同一条查询加索引前后的两份 EXPLAIN 输出并排，`Seq Scan` 和 `Index Scan` 分别红框/绿框，`Sort` 那一步在右侧消失。
- 高光图：最左前缀的电话簿类比图。
- 截图：`CREATE INDEX` 前后的执行计划完整输出。

---

## 八、C 档结论卡

**约 4 分钟。时间不够整体跳过，转课后自读。**

### 8.1 PostgreSQL / MySQL 行为差异（**跨栈必查项**）

| 主题 | PostgreSQL | MySQL |
|---|---|---|
| 超长字符串 | 报错 | 非严格模式**静默截断** |
| `GROUP BY` 缺列 | 报错 | 默认配置下返回任意值 |
| 大小写不敏感匹配 | `ILIKE` | `LIKE` + 不敏感 collation |
| 写入并返回 | `RETURNING` | 8.0 无；需再 SELECT |
| 生成序列 | `generate_series` | 无，用维度表 |
| 部分索引 | 支持 | 不支持 |
| 条件聚合 | `FILTER (WHERE ...)` | `SUM(条件)` |
| NULL 安全比较 | `IS DISTINCT FROM` | `<=>` 取反 |
| UNIQUE 多 NULL | 允许（15+ 可改） | 允许 |
| 默认事务隔离 | Read Committed | **Repeatable Read** |

> **前两行是本表最重要的：MySQL 在若干情况下"不报错"。**
>
> 前几次课反复强调"沉默的失败最贵"。这一条在数据库选型上同样成立：**用 MySQL 的项目请务必开启严格模式与 `ONLY_FULL_GROUP_BY`**，把静默行为变成报错。

### 8.2 一句话结论卡

| 问题 | 结论 | 展开处 |
|---|---|---|
| 主键用自增还是 UUID | 自增：小、有序、索引友好，但可枚举、分布式下需协调。UUIDv7 兼顾有序与不可枚举。**本课程用 BIGSERIAL** | 自读 |
| 软删除怎么做才不漏 | `deleted_at` + 建视图或行级安全，不要靠每条查询记得加条件 | 自读 |
| 时区 | 存 `TIMESTAMPTZ`（UTC），展示时转。**不要在数据库里存本地时间** | 单元 4.2 |
| 枚举用 `TEXT+CHECK` 还是原生 `ENUM` | `TEXT+CHECK`：增删值只改约束；原生 `ENUM` 加值要改类型定义。**本课程用前者** | 单元 4.6 |
| 要不要反范式（存 `answer_count` 冗余列） | 先别。等实测证明 `count()` 是瓶颈，再加，且要有维护它的机制（触发器或应用层） | 第 11 次课 |
| 事务隔离级别 | 本课程一律用默认。**知道"先读后写在任何隔离级别下都需要额外手段"就够** | 第 7 次课一句话 |
| 连接池大小怎么定 | 和 worker 数、数据库 `max_connections` 是一组约束 | 第 5 次课 6.3、第 16 次课 |
| `EXPLAIN` 的 cost 怎么读 | 本课程不读。只看 `Seq Scan` / `Index Scan` | 不展开 |

### 8.3 建表自检清单（**作业三要用，请单独做成一页可打印的卡**）

> 拿到任何一份建表 DDL（尤其是 AI 生成的），逐条过：
>
> 1. □ 每张表有主键吗？
> 2. □ 每个字段的类型有业务依据吗？（有没有无脑的 `VARCHAR(255)`）
> 3. □ 时间字段是 `TIMESTAMPTZ` 吗？
> 4. □ 每个字段问过"能不能不填"吗？不能的都 `NOT NULL` 了吗？
> 5. □ `NOT NULL` 的字段有合适的 `DEFAULT` 吗？
> 6. □ 业务上唯一的字段有 `UNIQUE` 吗？（**不要靠应用层查重**）
> 7. □ `UNIQUE` 的列同时 `NOT NULL` 了吗？
> 8. □ 每个引用别的表的列有 `REFERENCES` 吗？
> 9. □ 每个外键的 `ON DELETE` 明确选过吗？（不是用默认值）
> 10. □ 枚举字段有 `CHECK` 吗？
> 11. □ 数值字段的取值范围有 `CHECK` 吗？
> 12. □ M:N 连接表有复合主键（或联合唯一）吗？
> 13. □ 每个外键列有索引吗？
> 14. □ 高频过滤+排序的组合有复合索引吗？列顺序对吗？
> 15. □ 每个约束都显式命名了吗？（为了在代码里判断）

---

## 九、作业与欠账登记

**约 6 分钟。**

### 作业一：为项目补全约束与索引（主线）

**第一部分：DDL 重写。**

用单元 8.3 的 15 条清单逐条过一遍你项目的建表语句，提交：

1. 重写后的完整 DDL；
2. **一张"每条约束的理由表"**：

   | 约束 | 类型 | 理由 | 缺了它会发生什么 |
   |---|---|---|---|
   | `questions_title_key` | UNIQUE | 业务要求标题唯一 | 并发下应用层查重失效，产生重复问题 |

3. 数据清洗脚本（如果你的数据已经脏了）+ 清洗前后的数量对照。

**第二部分：索引与实测对照表。**

按单元 7.6 的格式提交完整对照表，**至少 6 行，必须包含一行"加了索引但没有改善"的查询**，并说明原因。

每一行要给出：查询、索引前耗时、索引后耗时、用到的索引名、计划节点从什么变成什么。

### 作业二：补 4 条业务 SQL（A 档）

在课上 8 条之外，自己写出下面 4 条，提交 SQL + 执行结果 + 你为它加的索引：

1. **某用户的主页数据**：他发的问题（含回复数）+ 他写的回答（含所属问题标题），各取最近 10 条；
2. **热门标签 Top 20**：按"最近 30 天内被使用的问题数"排序，**使用数为 0 的标签也要出现**；
3. **待回答问题列表**：状态为 open、零回答、创建超过 24 小时的问题，按时间正序；
4. **一次采纳操作**：把某条回答标记为已采纳，同时把同一问题下其他回答的采纳标记清掉，**并返回被影响的行数**。

> 第 2 条要用上单元 6.8 的思路（先定横轴再 join）。
> 第 3 条要用上单元 5.3 的 `NOT EXISTS`。
> 第 4 条要想清楚"两条 UPDATE 必须在一个事务里"——**这是第 7 次课的引子，今天你先用 `BEGIN; ... COMMIT;` 手写。**

### 作业三：一处"AI 漏了外键/唯一约束"的修复证据（**本次课的课程主题作业**）

**步骤**：

1. 向 AI 提出这个需求（原样使用，把提示词抄进作业）：

   > 我在做一个问答网站，有用户、问题、回答、标签四种数据，问题和标签是多对多。请给我 PostgreSQL 的建表语句。

2. **原样保存** AI 的输出（作为附件，不要修改）。

3. 用单元 8.3 的 15 条清单逐条检查，填这张表：

   | # | 清单项 | 通过？ | AI 的实际写法 | 后果（**要具体**） |
   |---|---|---|---|---|
   | 1 | 每张表有主键 | | | |
   | ... | | | | |
   | 15 | 约束显式命名 | | | |

4. 提交修复后的 DDL 与 **diff**。

5. **必答三问**（评分重点）：

   | 问题 | 你的回答 |
   |---|---|
   | AI 漏掉的约束里，哪一个后果最严重？为什么？ | |
   | 为什么 AI 会漏这些？**说出至少两个原因** | |
   | 如果你只能让 AI 记住一条建表规则，你选哪一条？为什么？ | |

**给第 2 问的参考方向**（讲评时用，不要提前给学生）：

> 三个原因：
>
> 1. **训练数据的偏向**：网上大量 DDL 来自教程和快速原型，那些场景确实不需要约束。AI 学到的是"建表语句长什么样"，不是"这个业务需要什么约束"。
> 2. **约束需要业务知识，而 AI 没有**："标题该不该唯一""删用户时回答该级联还是置空"——**这些问题只有你能回答**。AI 不知道，就只能不写。**注意：这一条不是 AI 的缺陷，是信息的缺失。你不说，它就不知道。**
> 3. **没有反馈信号**：不加约束的 DDL 能成功执行、能插入数据、能通过测试。**AI 没有任何机会知道自己漏了东西。**
>
> 对应的三层护栏（呼应第 5 次课单元 6.4 的同一套方法）：
>
> | 层 | 做法 |
> |---|---|
> | **约定** | 建表 DDL 必须人工逐条过 15 项清单，**这一步不外包给 AI** |
> | **机械检查** | CI 里查询系统表：所有表有主键、所有外键列有索引、所有枚举列有 CHECK → **第 9 次课** |
> | **定量兜底** | 上线前跑一遍"脏数据探测"查询（空值率、枚举值分布、孤儿行数） |
>
> 请注意第 2 问的答案指向一个更一般的结论：**AI 在"需要你的业务知识"的地方一定会犯错，而它不会告诉你它缺少这个知识。** 你的职责是识别"哪些决定需要业务输入"，并且在提问时就把它给出来。
>
> 试着重新提问一次，在提示词里加上"标题必须唯一；删除用户时保留其回答并显示为已注销；删除问题时连带删除其回答"——**看看输出有什么变化**。这是第 3 次课"契约先行"在数据层的版本。〔可作为 B 档加分项。〕

### 本次课新增的欠账登记

| 欠账 | 何时还 |
|---|---|
| 建表还是手写 SQL，无版本管理与回滚 | **第 7 次课**（Alembic 最小闭环） |
| 数据清洗脚本要放进迁移里 | **第 7 次课** |
| `raw SQL` 要翻译成 ORM | **第 7 次课**（8 条中的 5 条） |
| "两条 UPDATE 要在一个事务里" | **第 7 次课**（事务边界 = 一个请求一个事务） |
| 先读后写的三个实例都需要更强手段 | 第 7 次课（一句话结论）、第 11 次课 |
| 深分页（OFFSET 大）性能 | **第 11 次课**（keyset 分页） |
| `LIKE '%kw%'` 用不上索引 | **第 11 次课**（全文检索） |
| 反范式冗余列（`answer_count`） | 第 11 次课 |
| 参数化只讲了纪律，没演示注入 | **第 15 次课** |
| 排序字段白名单 | 第 7 次课解剖台 |
| Pydantic 约束与 DB 约束的数字重复 | 第 7 次课（ORM 模型可减少一部分） |
| 约束与索引检查进 CI | **第 9 次课** |
| 连接池 × worker × max_connections | 第 16 次课 |
| 软删除的结构性做法 | 课后自读 |

---

## 十、素材清单与制作说明

### 必需素材

| 素材 | 说明 |
|---|---|
| tag `v6-bad-schema` | 起始版：AI 原样 DDL（全 VARCHAR、无约束、无索引） |
| tag `v6-schema` | 单元 4 结束：约束完整 |
| tag `v6-sql` | 单元 6 结束：8 条 SQL 可执行 |
| tag `v6-indexed` | 单元 7 结束：索引完整，为第 7 次课起点 |
| `scripts/seed_large.py` | **本次课最关键的脚本**。10 万问题 / 30 万回答 / 2000 用户；**必须含有意制造的脏数据**：NULL status（约 30%）、大小写不一的枚举、重复标题（若干组）、孤儿 author_id、大量 created_at 完全相同的行（供 6.2 演示）。**固定随机种子，结果可重复**。40 秒内跑完 |
| `scripts/race_insert.py` | 并发 POST 相同标题，输出各请求状态码 |
| `scripts/bench_sql.py` | 对 SQL 跑 N 次取中位数，输出耗时 + 计划节点类型 |
| `docs/sql8.sql` | 8 条 SQL，每条注释说明服务哪个页面 |
| `docs/indexes.sql` | 全部索引，每条注释说明服务哪条查询 |
| `docs/ddl_checklist.md` | 单元 8.3 的 15 条清单，**做成可打印单页** |
| **封面级 A** | TOCTOU 时序图（单元 4.4） |
| **封面级 B** | 两类并发 bug 对照表（与第 5 次课并列，单元 4.4） |
| **封面级 C** | 四道护栏累加表 + "谁能绕过哪道护栏"六行表（单元 4.4） |
| **封面级 D** | NULL 漏行定量图（300000 / 6353 / 291504 / 差 2143，单元 5.1） |
| **封面级 E** | 索引前后六行对照表（单元 7.6），首行与末行分别高亮 |
| **封面级 F** | 翻页重复演示：两页 id 列表并排（单元 6.2） |
| 高光图 G | 三值真值表（六行，3、4 行高亮） |
| 高光图 H | `NOT IN` 含 NULL 的四步推导 |
| 高光图 I | SQL 逻辑执行顺序图 |
| 高光图 J | 最左前缀的电话簿类比 |
| 高光图 K | ER 图（Crow's Foot，标注基数与可选性） |
| 截图 | 字符串时间排序错误的结果 |
| 截图 | 删用户产生 1876 条孤儿回答 |
| 截图 | 脏枚举值分布 `SELECT status, count(*)` |
| 截图 | 加约束失败的报错 |
| 截图 | 并发插入：加约束前两个 201 / 加约束后一个 201 一个 409 |
| 截图 | `NOT IN` 返回 0 条 vs `NOT EXISTS` 返回 369 条，并排 |
| 截图 | `JOIN` / `LEFT JOIN` 与 `count(*)` / `count(a.id)` 的对照 |
| 截图 | 同一查询加索引前后的两份完整 EXPLAIN（`Seq Scan` 红框 / `Index Scan` 绿框，`Sort` 消失） |

### 可后补

- PG/MySQL 差异表、一句话结论卡（纯文字）。
- 8 条 SQL 的语法说明（代码已在文中）。

### 备用材料

| 风险 | 备用方案 |
|---|---|
| **演示机性能不同导致耗时数字差异大**（最高风险） | 底稿中数字为参考值；**制作时必须在演示机实测替换**。另备一份预先跑好的完整数据表作为兜底，标注"预录数据" |
| seed 40 秒太慢，现场等待尴尬 | 课前提前跑好，课上只演示"数据量确认"；或提供 `pg_dump` 的数据文件直接 restore |
| `race_insert.py` 在慢机器上撞不出并发问题 | 脚本支持 `--delay` 参数人为放大 check-to-use 窗口（在 service 里插入 sleep）；备预录 30 秒录像 |
| 学生用 MySQL | C 档卡 8.1 给出差异；单元 5（`IS DISTINCT FROM`）、单元 6.8（`generate_series`）、单元 6.9（`RETURNING`）需替换写法，请提前准备 MySQL 版 `docs/sql8_mysql.sql` |
| AI 现场调用失败（作业三演示） | 准备一份预先生成并验证的"无约束 DDL"作为讲评素材，标注"预录产物" |
| 时间超支 | 按单元〇的压缩顺序执行；单元 3 有独立自读材料 `docs/er_modeling.md` |

### 环境与运行条件

延用前序环境（PostgreSQL 16+）。**本次课基本不写 Python**，主要在 `psql` 中操作——请提前确认所有学生能进入 `psql` 并有建表权限。建议同时提供一个 GUI 客户端选项（DBeaver / pgAdmin）作为退路。

**演示开始时的初始状态**：工作区在 tag `v6-bad-schema`；**大数据集已 seed 完成**；`psql` 已连接；另开一个终端跑服务（供开场的 curl 演示）。

**复位方式**：`make reset-db-large`（drop → 建 bad schema → restore 大数据集），约 60 秒。

---

## 十一、与前后课的衔接

**本次课回收的前序埋点**：

| 来源 | 埋点 | 回收位置 |
|---|---|---|
| 第 5 次课末 | "把数据灌到十万级，让问题自己浮出来" | **单元 1**（四个现象） |
| 第 5 次课 | 并发崩塌是"单请求测不出来"的一类错误 | **单元 4.4**（并发查重失效是同类的第二个实例，并排对照） |
| 第 5 次课 | 三道结构性护栏 | **单元 4.4**（数据库约束是第四道，且是唯一在 Python 之外的一道） |
| 第 5 次课 | "约定 + 机械检查 + 定量兜底"三层护栏 | 单元 9 作业三（同一套方法用在建表上） |
| 第 4 次课 | `services/` 里的查重逻辑 | **单元 4.4**（证明它在并发下失效，然后删掉它） |
| 第 4 次课 | 业务规则归服务层 | 单元 4.6（`CHECK` 与服务层的分界） |
| 第 4 次课 | 依赖稳定标识不依赖文案 | 单元 4.4 第五步（靠约束名判断 `IntegrityError`） |
| 第 3 次课 | Pydantic 约束 | 单元 4.6（schema 负责体验，约束负责正确性，两者都要） |
| 第 3 次课 | 422 的 `type` vs `msg` | 单元 4.4（同一条判据的第三次出现） |
| 第 2 次课 | 沉默的成本 | 单元 5 全部（NULL 错误全都不报错） |

**本次课埋下、后面必须回引的五处**（请在课件中明显标记）：

- **单元 4.7 的三步清洗流程** → 第 7 次课写成 Alembic 迁移脚本，并演示一次 `downgrade`；
- **单元 6 的 8 条 SQL** → 第 7 次课挑 5 条翻译成 ORM，与原 SQL 并排对照；
- **单元 6.9 "先读后写在并发下不可靠"（三个实例）** → 第 7 次课事务边界、第 11 次课并发控制；
- **单元 7.5 深分页 + 单元 6.6 `LIKE '%kw%'`** → 第 11 次课的两个主题；
- **单元 8.3 的 15 条清单** → 第 9 次课把其中 3–4 条写成 CI 检查（查 `pg_catalog` 系统表）。

**本次课不承担、请勿提前引入**：ORM 与模型定义（第 7 次课）、迁移工具（第 7 次课）、N+1 与加载策略（第 7 次课）、事务隔离级别的细节（不讲）、缓存与 keyset 分页（第 11 次课）、SQL 注入演示（第 15 次课）、数据库内核（全课程不讲）。

**给第 7 次课的提示**：

本次课结束时，项目的状态是**约束和索引都对了，但数据访问层仍然是手写 SQL（`text()`）**，而且建表是手工执行的 DDL、没有版本管理。

第 7 次课有两个天然的起点：

1. **N+1 的现场制造条件已经就绪**：`questions` 表有十万行，`answers` 有三十万行，`GET /questions` 返回 20 条。一旦引入 ORM 关系并在模板或 schema 里遍历 `q.answers`，就是 20 次额外查询。**请在 ORM 模型建好后立刻用 `echo=True` 数一次 SQL 条数**，让 N+1 在真实数据量下暴露（此时每条额外查询都会命中本次课建好的索引，所以单条很快——**这恰好说明 N+1 不是"慢查询"问题，是"查询次数"问题**，这个区分很有价值）。
2. **本次课的 8 条 SQL 是 ORM 翻译练习的现成素材**，其中 6.4 的 `HAVING count(DISTINCT ...)` 和 6.8 的 `generate_series + LEFT JOIN` 两条会很难翻译——**这正好是"什么时候该放弃 ORM 直接写 SQL"的最佳例子**。