# 第 6 次课教学底稿（修订版）
## 数据建模与 SQL 基础

## 〇、备课定位与内容取舍

本课只解决两件事：**把业务允许的状态写进数据库；把业务问题翻译成结果可核对的 SQL。** 不展开 B+ 树、MVCC、优化器代价模型，但不说这些知识“永远不影响决定”。遇到性能或并发问题，说明本课判据的适用条件和进一步学习方向。

原稿同时要求五表建模、完整 DDL、并发查重、NULL、八条查询和十万行压测全部现场完成，含缓冲超过 100 分钟。更严重的是把脏结构说成合格 M1 的真实状态、预先规定性能倍数，以及在已有重复数据上直接加 UNIQUE。本版分离教学故障与项目交付，保留完整 SQL 作为课后基础参考。

### 课堂路线：95 分钟教学 + 5 分钟缓冲

| 单元 | 分钟 | 课堂处理 |
|---|---:|---|
| 一、从 M1 的规则进入数据层 | 5 | 用一个业务问题建立目标 |
| 二、坏 DDL 解剖台 | 8 | 独立样例，只展示两处反例 |
| 三、五表 ER 与业务口径 | 12 | 学生补基数、可选性 |
| 四、约束与写入边界 | 18 | 9 分钟问题表，9 分钟唯一约束与失败处理 |
| 五、NULL 三值逻辑 | 17 | 学生现场必做；先预测小表结果再核对 |
| 六、业务 SQL | 20 | 展开 Q1、Q3、Q7，其余思路导读与自学 |
| 七、索引与证据 | 10 | 教师比较一个查询，不现场灌十万行 |
| 八、作业与下一课起点 | 5 | 说明基础交付和可选实验 |
| 合计 | 95 | 另留 5 分钟缓冲 |

完整五表 DDL、八条 SQL、约束验证是 A 档基础阅读与练习，不等于从空白现场默写。十万行索引、复合索引与深分页为 B 档；不再叠加四条新的必交查询。超时先缩减坏 DDL 的第二个现象与查询变体，保留 NULL 推导和一个正确聚合实例。

### 起点与数据库边界

- 保留第五课三个核心 JSON 端点、HTML 表单和 `/healthz`，不要求新增全部回答/标签 HTTP 接口；数据库练习可直接执行 SQL。
- 列表参数仍为 `keyword/page/page_size`，默认 20、上限 50；集合仍为 `items/total/page`。SQL 参数 `:page_size/:offset` 是内部绑定参数。
- 参考数据库统一为 **PostgreSQL 16+**。SQLite 可用于部分最小验证，不替代 PostgreSQL 的类型、异常、并发或迁移验收；MySQL 仅作差异阅读。
- 若学生仍用早期 SQLite，教师提供已验证的 PostgreSQL 连接与虚构数据起点，迁移连接环境不计作本课现场任务。不要宣称换驱动后所有 SQL 无需适配。

## 一、从 M1 出发：让规则不仅存在于 Python

**课堂 5 分钟。**

问：“表单和 JSON 都限制标题长度，为什么数据库还要约束？”用三个入口解释：HTTP、数据导入脚本、管理 SQL 都可能写同一张表。Pydantic 改善入口反馈；数据库约束保护所有写入路径以及并发竞争。

不假定 M1 已有重复标题，更不先往交付库灌十万条数据。若已有唯一约束正确生效，这正是应该保留的成果。

本课结束时学生应能：

1. 从业务规则说出字段类型、关系可选性和删除策略。
2. 区分 NOT NULL、CHECK、UNIQUE 和应用预查的职责。
3. 手算 NULL 对比较、NOT IN、聚合的影响。
4. 对分页、JOIN 与聚合说明“每一行代表什么”。
5. 用结果、计划与测量判断一个索引建议，而非只找 Index Scan 字样。

## 二、解剖台：故障库不是项目库

**课堂 8 分钟。** 教师准备三种互相隔离的数据环境；这些是制作要求，不是本仓库已经存在的数据库或脚本。

| 环境 | 目的 | 允许的操作 |
|---|---|---|
| 坏结构/脏数据副本 | 类型、孤儿、重复、清洗反例 | 可丢弃；明确故障阶段 |
| 正确的小型教学库 | 五表约束、手算查询、下次课基线 | 每轮恢复到记录的初始状态 |
| 性能库 | 十万级数据与索引实验 | 独立连接；不覆盖前两者 |

### 2.1 只保留说明问题所需的坏结构

```sql
-- 仅在独立故障库执行；不是 M1 的建表脚本。
CREATE TABLE bad_questions (
    id INTEGER PRIMARY KEY,
    title VARCHAR(255),
    body VARCHAR(255),
    author_id INTEGER,
    status VARCHAR(255),
    created_at VARCHAR(255)
);
```

没有业务依据的 255、字符串时间、缺失的约束分别是什么问题？不能只凭“用了 VARCHAR”就判错，长度合适的短文本完全可以使用它。

```sql
INSERT INTO bad_questions (id, title, body, created_at)
VALUES (1, '旧问题标题', '一段正常的测试正文内容', '2025-9-30'),
       (2, '新问题标题', '另一段正常测试正文内容', '2025-10-15');
SELECT id, created_at FROM bad_questions ORDER BY created_at DESC;
```

字符串排序与时间排序不同；固定这两个值即可复现，不需要等到某个月。类型不仅决定存储，也决定运算和比较语义。

第二个现象课内可选：插入 300 字正文，PostgreSQL 对 `VARCHAR(255)` 报超长错误，**不是静默截断**。MySQL 行为取决于版本与严格模式，不能作为本课实测结果替换。

### 2.2 孤儿与重复：先识别，再修

缺外键时，删除用户后回答可能指向不存在的 id；有外键且选择 SET NULL 时，NULL 则是明确允许的状态。这两者不能混称“脏数据”。

缺唯一约束时，“先 SELECT 没有，再 INSERT”存在竞争窗口；有唯一约束则由数据库裁决。是否产生重复还取决于时序，现场演示需用同步屏障控制两个事务都先完成预查，不能保证随便发两个请求必撞。

AI 输出只是被审查的对象，不预设它必定漏约束；教学故障标注为人为构造，不伪称原样输出。

## 三、先说业务，再画五表 ER

**课堂 12 分钟。**

### 3.1 本课程采用的业务规则

- 用户可以提出多个问题，每个问题必须有一位作者。
- 问题可以有零到多个回答，每个回答必须属于一个问题。
- 回答作者允许为空，表示原作者已不可引用；不把未知作者自动算成普通成员。
- 问题和标签是多对多，同一标签对同一问题最多关联一次。
- 标题在本课程项目内唯一，这是教学业务选择，不是所有问答网站的通用规则。
- 问题状态限 `open/closed/deleted`；浏览量非负。软删除状态不等于物理 DELETE。

```text
users 1 ── 0..N questions
users 0..1 ── 0..N answers
questions 1 ── 0..N answers
questions 1 ── 0..N question_tags 0..N ── 1 tags
```

学生在图上标出外键在哪边、能否为空、删除时如何处理。ER 图的价值在这些决定，不在绘图工具。

### 3.2 三个建模判断

1. **1:N**：外键放在 N 方。把回答 id 拼成逗号字符串放问题表，难以约束、查询和更新。
2. **M:N**：连接表记录每一条关系；联合主键防止重复关联。连接本身需被其他对象引用时也可用独立 id，但仍要保证业务组合唯一。
3. **可选性来自业务**：不要因为“不想处理插入错误”把所有列设成 NULL；也不要为了避开三值逻辑把真正未知的数据硬填为 0 或空串。

### 3.3 删除策略不能孤立看

| 关系 | 本课选择 | 后果 |
|---|---|---|
| questions.author_id → users | RESTRICT | 有提问的用户不能直接物理删除 |
| answers.author_id → users | SET NULL | 保留回答；模板显示匿名或未知作者 |
| answers.question_id → questions | CASCADE | 物理删除问题时一并删除回答 |
| question_tags → questions/tags | CASCADE | 删除任一端时清理关系 |

同一用户可能既提问又回答，所以 SET NULL 不意味着“所有用户都能直接 DELETE 注销”。注销可匿名化或停用，完整身份生命周期留第十四课。删除内容有审计/保留要求时，本表策略也需重新评估。

## 四、DDL 与约束：数据库是最后一道规则边界

**课堂 18 分钟；完整 DDL 为 A 档课后参考。**

### 4.1 五表目标结构

在一个空的教学数据库中执行。显式命名约束，便于错误翻译和第七课迁移对齐。类型选择沿用 BIGSERIAL，IDENTITY 也是可行选择；不要求为了新语法改动已稳定的键。

```sql
CREATE TABLE users (
    id BIGSERIAL PRIMARY KEY,
    email TEXT NOT NULL,
    display_name TEXT NOT NULL,
    password_hash TEXT NOT NULL,
    role TEXT NOT NULL DEFAULT 'member',
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    CONSTRAINT users_email_key UNIQUE (email),
    CONSTRAINT users_role_check CHECK (role IN ('member','moderator','admin')),
    CONSTRAINT users_name_len CHECK (char_length(display_name) BETWEEN 2 AND 40)
);

CREATE TABLE questions (
    id BIGSERIAL PRIMARY KEY,
    title TEXT NOT NULL,
    body TEXT NOT NULL,
    author_id BIGINT NOT NULL,
    status TEXT NOT NULL DEFAULT 'open',
    view_count INTEGER NOT NULL DEFAULT 0,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    CONSTRAINT questions_author_id_fkey FOREIGN KEY (author_id)
        REFERENCES users(id) ON DELETE RESTRICT,
    CONSTRAINT questions_title_key UNIQUE (title),
    CONSTRAINT questions_status_check CHECK (status IN ('open','closed','deleted')),
    CONSTRAINT questions_title_len CHECK (char_length(title) BETWEEN 5 AND 200),
    CONSTRAINT questions_body_len CHECK (char_length(body) BETWEEN 10 AND 20000),
    CONSTRAINT questions_views_nonneg CHECK (view_count >= 0)
);

CREATE TABLE answers (
    id BIGSERIAL PRIMARY KEY,
    question_id BIGINT NOT NULL,
    author_id BIGINT,
    body TEXT NOT NULL,
    is_accepted BOOLEAN NOT NULL DEFAULT false,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    CONSTRAINT answers_question_id_fkey FOREIGN KEY (question_id)
        REFERENCES questions(id) ON DELETE CASCADE,
    CONSTRAINT answers_author_id_fkey FOREIGN KEY (author_id)
        REFERENCES users(id) ON DELETE SET NULL,
    CONSTRAINT answers_body_len CHECK (char_length(body) BETWEEN 10 AND 10000)
);

CREATE TABLE tags (
    id BIGSERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    CONSTRAINT tags_name_key UNIQUE (name)
);

CREATE TABLE question_tags (
    question_id BIGINT NOT NULL,
    tag_id BIGINT NOT NULL,
    CONSTRAINT question_tags_pkey PRIMARY KEY (question_id, tag_id),
    CONSTRAINT question_tags_question_id_fkey FOREIGN KEY (question_id)
        REFERENCES questions(id) ON DELETE CASCADE,
    CONSTRAINT question_tags_tag_id_fkey FOREIGN KEY (tag_id)
        REFERENCES tags(id) ON DELETE CASCADE
);
```

标题、问题正文长度与第五课共享 schema 对齐；回答正文沿第三课参考约束。数据库长度保护存储边界，输入规范化仍由共享入口规则负责。例如 Python `strip()` 和数据库字符处理不应被假定完全等价。

邮箱目前按存储值比较唯一，大小写归一策略须在注册规格中定义；本课不假装已经实现可上线的认证。`password_hash` 在教学数据中使用不可登录的占位值，不提供真实账号密码。

### 4.2 每一种约束挡什么

| 机制 | 能保证 | 不能代替 |
|---|---|---|
| NOT NULL | 列值不是 NULL | 非空字符串、合法范围 |
| CHECK | 表达式不能为 FALSE | NULL 禁止、跨表复杂业务 |
| UNIQUE | 非空值的唯一性；本例再配 NOT NULL | 输入规范化、HTTP 错误表现 |
| FOREIGN KEY | 引用存在并遵守删除策略 | 用户是否有权操作该对象 |
| DEFAULT | 未提供值时使用默认值 | 显式 NULL 的校正、NOT NULL |

PostgreSQL 的 CHECK 对 TRUE 或 UNKNOWN 都通过，只有 FALSE 被拒绝。若要禁止 NULL，必须另写 NOT NULL。普通 UNIQUE 通常允许多个 NULL；本例的非空业务键同时有 NOT NULL。

类型选择只讲必要结论：时间点用 TIMESTAMPTZ（不保留原时区名称，显示受会话时区影响）；布尔用 BOOLEAN；整数计数用合适范围的整数；金额需要精度规则时考虑 NUMERIC，不把所有数字都改成 NUMERIC。

### 4.3 应用预查与数据库唯一约束

```text
事务 A：查同标题 → 没有
事务 B：查同标题 → 没有
事务 A：插入并提交
事务 B：尝试插入 → 唯一约束冲突
```

如果没有数据库约束，两次写入可能都成功；有约束时，B 可能等待 A 的提交，然后报冲突。A 回滚则结果不同。应用预查仍可用于友好提示，但它不是并发下的权威保证。

演示分两阶段：在无唯一约束的隔离副本控制时序，保存重复证据；恢复到无重复的初始副本后添加唯一约束再测。**不要直接在刚制造重复的表上 ADD UNIQUE。** 实际旧库要先查重复，按业务决定合并、保留和引用迁移，不随意删掉其中一行。

### 4.4 失败先回滚，随后翻译异常

PostgreSQL 事务里一次语句失败后，不能继续当正常事务查询或提交。沿第五课函数作用域依赖，将数据库异常翻译放在事务上下文外面：

```python
from typing import Annotated
from fastapi import Depends
from sqlalchemy import Connection
from sqlalchemy.exc import IntegrityError

def get_conn():
    try:
        with engine.begin() as conn:
            yield conn
    except IntegrityError as exc:
        # 到这里上下文已退出并回滚，包括提交阶段的失败。
        constraint = getattr(getattr(exc.orig, "diag", None), "constraint_name", None)
        if constraint == "questions_title_key":
            raise DuplicateTitle() from exc
        raise

ConnDep = Annotated[Connection, Depends(get_conn, scope="function")]
```

此处结构化异常字段针对 PostgreSQL/psycopg；不要搜索 `str(exc.orig)` 中的英文报错，也不要把所有 IntegrityError 一律改成“标题重复”。其他驱动需有经验证的适配。

service 可以在写入前预查并抛 DuplicateTitle，但 repository/service 不各自 commit。HTTP 层让异常穿过边界回滚，再按第五课转 JSON 409 或 HTML 409 回填。提交失败不能先发 201/303。

### 4.5 约束验证与数据清洗

每项测试独立事务或 SAVEPOINT，失败后先 ROLLBACK 再继续。至少核对：缺作者、重复标题、不存在的作者、非法状态、过短正文、负浏览量和重复标签关系；另核对允许匿名回答、零回答问题等合法边界。

旧表加约束的顺序：

1. 盘点 NULL、非法非空值、重复和孤儿，保存原值与数量。
2. 由业务确定处理策略；无法自动判断的记录隔离人工核查，不统一随意填 open。
3. 在副本中处理数据，复核结果，再加约束。
4. 保存 SQL、执行环境、时间与前后证据；第七课用最终结构建立基线。

```sql
-- 盘点口径明确区分 NULL 与非法非空值。
SELECT count(*) FILTER (WHERE status IS NULL) AS missing,
       count(*) FILTER (
           WHERE status IS NOT NULL
             AND status NOT IN ('open','closed','deleted')
       ) AS invalid
FROM questions;
```

这条盘点在旧表或故障副本使用；已执行目标约束的新表两项应为零。清洗后删除约束并不能恢复原始脏值，结构 downgrade 不等于数据恢复。

## 五、现场必做：NULL 不是普通值

**课堂 17 分钟。** 先使用独立 VALUES 数据，不需要十万行，也不破坏已经要求 status 非空的项目表。

### 5.1 WHERE 只保留 TRUE

```sql
WITH sample(id, status) AS (
    VALUES (1, 'open'), (2, 'deleted'), (3, NULL::text), (4, 'closed')
)
SELECT id, status, status != 'deleted' AS keep
FROM sample ORDER BY id;
```

| id | status | `status != 'deleted'` |
|---:|---|---|
| 1 | open | TRUE |
| 2 | deleted | FALSE |
| 3 | NULL | UNKNOWN（结果显示 NULL） |
| 4 | closed | TRUE |

学生先写出结果 id，再加 WHERE 对照。只保留 1、4；不是报错，也不是 NULL 自动被视为 deleted。

如果业务定义“保留未知状态”，可写：

```sql
WHERE status != 'deleted' OR status IS NULL
-- PostgreSQL 也可写：
WHERE status IS DISTINCT FROM 'deleted'
```

这些是替换 WHERE 的片段，不是独立完整 SQL。若业务不允许未知状态，正确修复是清理和 NOT NULL，而不是在所有查询里一律加 `OR IS NULL`。

### 5.2 三值逻辑最小规则

普通比较遇 NULL 常得到 UNKNOWN；`IS NULL`、`IS DISTINCT FROM` 是专门处理 NULL 的谓词。`NOT UNKNOWN` 仍是 UNKNOWN，`TRUE OR UNKNOWN` 为 TRUE，`FALSE AND UNKNOWN` 为 FALSE。

`NULL = NULL` 不是 TRUE；因此不能用 `= NULL` 查空值。不要把 UNKNOWN 翻译成“数据库认为这是 false”，它只是同样不会被 WHERE 留下。

### 5.3 NOT IN 的陷阱

```sql
WITH users(id) AS (VALUES (1), (2), (3)),
     authors(author_id) AS (VALUES (1), (NULL::integer))
SELECT id, id NOT IN (SELECT author_id FROM authors) AS never_answered
FROM users ORDER BY id;
```

1 匹配到了作者，结果是 FALSE；2、3 没匹配到已知值，但列表含 NULL，结果是 UNKNOWN。加 WHERE 后没有行，**不是三行全部 UNKNOWN**。

业务问题是“没有任何回答引用这个用户”，改写：

```sql
WITH users(id) AS (VALUES (1), (2), (3)),
     authors(author_id) AS (VALUES (1), (NULL::integer))
SELECT u.id FROM users u
WHERE NOT EXISTS (
    SELECT 1 FROM authors a WHERE a.author_id = u.id
)
ORDER BY u.id;
```

结果是 2、3。另一种方式是在 NOT IN 子查询排除 NULL；NOT EXISTS 更直接表达“没有匹配关系”，不承诺在所有数据库上更快。

### 5.4 聚合中的 NULL

```sql
WITH scores(value) AS (VALUES (10), (20), (NULL::integer))
SELECT count(*) AS rows, count(value) AS known, avg(value) AS mean
FROM scores;
```

行数 3，已知值 2，均值 15。把 NULL 用 COALESCE 改成 0 会改变业务口径，不是只改变显示。Q3 再回收 `count(*)` 与 `count(a.id)` 的区别。

### 课堂提交的小证据

写出两个 VALUES 例子的预期 id、实际 id、修复 SQL 和业务口径。预测正确也得分，不要求学生先犯错。匿名回答究竟是否计入“非管理员回答”必须先定义，不能把未知作者身份直接归入某个角色。

## 六、八条业务 SQL：完整参考，课堂展开三条

**课堂 20 分钟。** Q1、Q3、Q7 主讲；其他只指出输入、输出粒度和关键操作，课后按同一数据核对。

### 6.1 小数据契约与参数约定

教学 seed 需满足下表；完整可执行 seed 在独立演示工程制作时提供并验证，以下不是声称已经执行的输出。

| 对象 | 数据规格 |
|---|---|
| users | id 1、2、3；不同合法邮箱/姓名 |
| questions | 101/102 为 open 且 created_at 相同；103 为 closed 且更新；104 为 open 且更早 |
| 作者 | 101、103 属用户 1；102 属用户 2；104 属用户 3 |
| answers | 201→101/作者2/采纳；202→101/作者NULL/未采纳；203→102/作者1/未采纳；204→103/作者2/采纳 |
| tags | 1=python、2=sql |
| question_tags | (101,1)、(101,2)、(102,1)、(104,2) |

标题与正文必须满足长度约束；101 标题包含字面 `100%`，其余不含，用于搜索边界。日期使用显式 UTC 时间。若 seed 手动指定 BIGSERIAL id，需要同步调整相应序列，避免后续 INSERT 主键冲突。

以下 `:name` 形式均为 **SQLAlchemy text() 的绑定参数**，不能原封不动粘进 psql。psql 手工练习时将它们替换为指定的常量；脚本使用参数绑定，不做字符串替换。

```python
from sqlalchemy import text

rows = conn.execute(
    text("SELECT id, title FROM questions WHERE id = :qid"),
    {"qid": 101},
).mappings().all()
```

### Q1：稳定排序分页（课堂）

```sql
SELECT q.id, q.title, q.created_at, u.id AS author_id, u.display_name
FROM questions q
JOIN users u ON u.id = q.author_id
WHERE q.status = 'open'
ORDER BY q.created_at DESC, q.id DESC
LIMIT :page_size OFFSET :offset;
```

第一、二个 open 问题同时间，id 是唯一决胜键。指定第一页两条时预期 102、101，第二页为 104。没有唯一决胜键时顺序**不受保证**，不要求每台机器都稳定复现某个重复 id。

`total` 使用同过滤条件的计数查询，而非只数当前页：

```sql
SELECT count(*) FROM questions WHERE status = 'open';
```

过滤参数存在时两条查询也要同时应用；READ COMMITTED 下两语句可能看到不同快照，严格一致性需另作设计。唯一排序不阻止并发插删导致 OFFSET 跨页漂移；keyset 为课后拓展，不虚构为第十一课数据库内容。

### Q2：问题详情（自学）

```sql
SELECT q.id, q.title, q.body, q.created_at,
       u.id AS author_id, u.display_name
FROM questions q
JOIN users u ON u.id = q.author_id
WHERE q.id = :qid;
```

预期每个合法 id 最多一行；不存在返回空结果，由业务层决定 404。示例不查询用户 email/password_hash。若要屏蔽软删除，须与现有详情契约明确同步，不在 SQL 翻译时偷偷变更。

### Q3：包括零回答的问题列表（课堂）

```sql
SELECT q.id, q.title, q.created_at,
       u.id AS author_id, u.display_name,
       count(a.id) AS answer_count
FROM questions q
JOIN users u ON u.id = q.author_id
LEFT JOIN answers a ON a.question_id = q.id
WHERE q.status = 'open'
GROUP BY q.id, q.title, q.created_at, u.id, u.display_name
ORDER BY q.created_at DESC, q.id DESC
LIMIT :page_size OFFSET :offset;
```

open 问题按 102、101、104 顺序，回答数为 1、2、0。LEFT JOIN 保留没有匹配的左侧问题；它的补空行会被 `count(*)` 数为 1，`count(a.id)` 才为 0。

输出粒度是“每个问题一行”。再同时连接 tags 会放大回答行数，不能随意堆 JOIN；应先聚合、用相关子查询，或经证明后用 DISTINCT。WHERE 对右表施加非空过滤可能消掉 LEFT JOIN 留下的行，也要核对位置。

### Q4：同时带 python 与 sql 的问题（导读）

```sql
SELECT q.id, q.title
FROM questions q
WHERE q.status = 'open'
  AND q.id IN (
      SELECT qt.question_id
      FROM question_tags qt JOIN tags t ON t.id = qt.tag_id
      WHERE t.name IN (:tag1, :tag2)
      GROUP BY qt.question_id
      HAVING count(DISTINCT t.id) = 2
  )
ORDER BY q.created_at DESC, q.id DESC;
```

固定两个不同标签时预期 101。任意一个标签则不需要 HAVING=2；动态列表要先去重，将需要匹配的数量设为去重后长度，空标签列表定义为不筛选。不能把 AND/OR 语义混用。

### Q5：回答贡献排行（自学）

```sql
SELECT u.id, u.display_name,
       count(a.id) AS answer_count,
       count(a.id) FILTER (WHERE a.is_accepted) AS accepted_count
FROM users u
LEFT JOIN answers a ON a.author_id = u.id
GROUP BY u.id, u.display_name
ORDER BY accepted_count DESC, answer_count DESC, u.id ASC
LIMIT :page_size;
```

口径：先按采纳数，再按回答数，最后用户 id。种子数据中用户 2 为 2/2，用户 1 为 1/0，用户 3 为 0/0；匿名回答不归入任一现存用户。这里展示计数查询，不等于已实现采纳业务的并发约束。

### Q6：关键词字面子串搜索（自学）

```sql
SELECT q.id, q.title
FROM questions q
WHERE q.status = 'open'
  AND (q.title ILIKE :pattern ESCAPE '!'
       OR q.body ILIKE :pattern ESCAPE '!')
ORDER BY q.created_at DESC, q.id DESC
LIMIT :page_size OFFSET :offset;
```

```python
def literal_pattern(keyword: str) -> str:
    escaped = keyword.replace("!", "!!").replace("%", "!%").replace("_", "!_")
    return f"%{escaped}%"
```

pattern 仍通过参数绑定传入。参数化防止输入变成 SQL 语法；转义 `%/_` 则保证**字面搜索语义**，两者目的不同。`keyword="100%"` 应只匹配含字面 100% 的问题，而不是任意 100 开头内容。空关键字在业务层定义为不筛选。

### Q7：从未回答过的用户（课堂，回收 NULL）

```sql
SELECT u.id, u.display_name
FROM users u
WHERE NOT EXISTS (
    SELECT 1 FROM answers a WHERE a.author_id = u.id
)
ORDER BY u.id;
```

预期只有用户 3；匿名回答中的 NULL 不会让结果全空。先从业务含义读成“找不到一条属于他的回答”，再对应 SQL。

### Q8：原子增加浏览量（自学，埋点第八课）

```sql
UPDATE questions
SET view_count = view_count + 1
WHERE id = :qid
RETURNING id, view_count;
```

一个 SQL 在数据库里对当前值递增，避免“客户端读旧值再覆盖”的窗口。以下只用来演示预期缺陷；SQLAlchemy 2.x 仍必须使用 text 和参数绑定：

```python
row = conn.execute(
    text("SELECT view_count FROM questions WHERE id = :qid"), {"qid": qid}
).one()
conn.execute(
    text("UPDATE questions SET view_count = :v WHERE id = :qid"),
    {"v": row.view_count + 1, "qid": qid},
)
```

两事务读到相同旧值后可能相互覆盖。不要再夹带遗漏 WHERE 或缺 text 的第二种错误。Q8 是受控 SQL 练习，不要求把业务 GET 改成有副作用的接口；投票、版本冲突与重试在第八课展开。

### 6.2 SQL 逻辑顺序与常见误读

便于理解的逻辑顺序：FROM/JOIN → WHERE → GROUP BY → HAVING → SELECT → ORDER BY → LIMIT/OFFSET。优化器实际执行计划可重排，不能把这条线当作物理执行顺序。

```sql
SELECT question_id, count(*) AS n
FROM answers
GROUP BY question_id
HAVING count(*) > 1
ORDER BY n DESC, question_id;
```

WHERE 过滤聚合前的行，HAVING 过滤分组结果。这里 ORDER BY 可以使用 n，WHERE 不能用该 SELECT 别名。避免一条反例同时写错语法顺序、别名和分组列而无法定位重点。

现代 MySQL 默认通常启用 ONLY_FULL_GROUP_BY，不能用“它默认允许随便选非分组列”作为跨栈结论。

## 七、索引：从查询提出假设，再验证

**课堂 10 分钟；大数据实验为 B 档。**

### 7.1 三类候选，不是三条机械建索引规则

- 外键引用列：常用于连接和父行删除检查，优先评估。PostgreSQL 不自动为所有引用侧外键建索引；其他数据库行为需分别核对。
- 经常过滤的列或列组合：结合选择性、数据分布和常用条件判断。
- 排序/分页列组合：结合过滤条件设计顺序，稳定排序的 id 决胜键也要考虑。

主键/唯一约束已有支撑索引，别再重复建立同样索引。索引占空间并增加写入维护成本，不是越多越好。

供查询验证的候选集如下；不是要求每个学生机械全部添加：

```sql
CREATE INDEX idx_questions_author ON questions(author_id);
CREATE INDEX idx_answers_question ON answers(question_id);
CREATE INDEX idx_answers_author ON answers(author_id);
CREATE INDEX idx_qtags_tag ON question_tags(tag_id);
CREATE INDEX idx_questions_status_created
    ON questions(status, created_at DESC, id DESC);
```

联合主键 `(question_id, tag_id)` 已支持从 question_id 找标签；反向从 tag_id 找问题需要另作评估。多列 B-tree 通常受前导列条件影响较大，但不能断言“不筛最左列就绝不使用索引”；数据库版本、分布及扫描策略可能改变计划。

### 7.2 教师演示一个查询

在独立性能库使用同一条查询：

```sql
EXPLAIN (ANALYZE, BUFFERS)
SELECT id, title FROM questions
WHERE author_id = 42
ORDER BY created_at DESC, id DESC
LIMIT 20;
```

先核对结果，再比较加候选索引前后：扫描方式、实际输出/过滤行数、是否额外 Sort、执行时间和缓冲命中。若作者 42 没数据，应先调整受控样本，而不是用空结果证明性能好。

| 环境/数据量 | 查询与参数 | 索引方案 | 结果是否相同 | 实际行数/Sort | 多轮耗时与波动 |
|---|---|---|---|---|---|
| 待记录 | 同一查询 | 前 / 后 | 待核对 | 待记录 | 待测 |

Seq Scan 可能是合理选择，例如小表或大比例结果；Index Scan 也可能因大量回表而更慢。不存在本课预先承诺的“19000 倍”。若课程材料展示实测值，需附机器、版本、数据分布和重复次数。

### 7.3 B 档性能实验协议

在隔离库生成十万问题及相关回答，固定随机种子、分布和数据规模。导入后更新统计信息，使用一致的参数和连接条件；记录冷/热缓存说明，多轮测量，不把第一次与预热后的结果直接对比。

只选一条有业务价值的查询评估，允许不添加索引。`EXPLAIN ANALYZE` 会真正执行语句；本课只对 SELECT 使用。写操作分析需更严格隔离，ROLLBACK 也不能撤销序列消耗或外部副作用。

### 7.4 课后阅读边界

- 普通 B-tree 通常不适合 `%keyword%` 任意子串；PostgreSQL 的 pg_trgm 可支持 LIKE/ILIKE，需评估扩展与维护成本。
- 全文检索解决分词与相关度等问题，不是字面子串搜索的语义等价替代。
- 深分页与 keyset 是拓展，不归入第十一课（该课实际讲 React）。keyset 仍需稳定排序、游标契约和并发语义。
- “每个问题最多一个采纳回答”若正式采用，需数据库并发约束，例如按 question_id 的条件唯一索引及配套写入流程；不能仅靠两条 UPDATE 放在同一事务就宣称并发安全。此项不列入本课基础交付。

## 八、作业、交付与评价

**课堂 5 分钟。** 基础任务预估 3—4 小时，已有课堂证据可以复用，不重复提交同一份结果。

### 8.1 A 档：规则与查询可核对

1. 五表 ER 与目标 DDL，解释一个可空字段和一组 ON DELETE 选择；已有正确结构可保留，不强制制造修改 diff。
2. 约束验证：非法输入被拒绝、合法边界被接受，失败后事务已回滚。至少覆盖唯一、外键、NOT NULL/CHECK 和正文边界。
3. 完成八条提供 SQL 的结果核对，重点解释 Q1、Q3、Q7；记录输入参数、预期行与实际行，不只截图“执行成功”。Q8 在隔离事务里验证。
4. 为一条查询提出索引建议，提交结果一致性与计划/耗时证据，或解释为何不加。可用教师提供的受控数据，不强求十万规模。
5. 选本次一条 AI 建模或查询建议，给出保留/修改理由与验证。不要推断模型内部训练原因，不要求 AI 必须漏外键或唯一约束。

取消“另写四条 SQL”“至少六行索引表且必须一行无提升”等配额。评分关注业务口径、边界、证据和解释，而不是凑错误、凑索引。

### 8.2 B 档：任选一个问题深入

大数据索引对照、标签 AND/OR 动态参数、LEFT JOIN 多关系聚合放大、keyset 分页或 pg_trgm 子串查询。给出前提和局限；未选部分仍保留自学内容，不因未做拓展扣基础分。

### 8.3 第七课接收什么

- 已校验的五表结构与约束名称，数据库版本及驱动信息。
- 八条查询和小数据结果基线；核心 HTTP 契约快照与第五课表单回归证据。
- 如执行过清洗，保留原值备份、决策与记录；不把不可恢复清洗称为可逆迁移。
- 索引区分“已采用”与“待评估”。第七课模型与迁移只记录已采用的结构，不把候选集全部混入。

## 九、素材与运行验收

需在制作独立演示工程时补齐并验证：

- PostgreSQL 16+ 锁定版本、psycopg、SQLAlchemy 2.x 连接配置；不得在示例中写真实凭据。
- 三类隔离数据库/副本的初始化与复位方案，小型 seed 和预期结果文件。
- 并发唯一性演示的受控同步点、事务日志及复位步骤；不要在对外请求里保留测试屏障。
- `Form` 与 JSON 共用事务依赖的正常、重复标题、提交失败回归；健康检查契约保持不变。
- 索引前后计划与多轮实测；现场失败时使用注明环境的预录证据，模拟数值须标“模拟”。

本轮用内存 SQLite 最小样例核对了 NOT IN/NOT EXISTS 的 NULL 行为、CHECK 允许 NULL、LEFT JOIN 的两种 count，以及 LIKE 字面通配符转义。该验证不覆盖 PostgreSQL 的 ILIKE、FILTER、类型、并发锁或完整八条查询。

示例 SQL 为 PostgreSQL 参考，完整 PostgreSQL 实验和独立工程尚未完成运行验收。课堂不临时安装数据库，不对真实数据演示删除、加约束或恢复。

## 十、前后课衔接与教师收束

第五课说明一次请求如何执行和回应；第六课把“什么状态允许存在”交给数据库，并建立可手算的查询基线；第七课再换成 ORM，核对**结果不变、SQL 可见、事务与结构演进有边界**。

第八课继续写操作、并发冲突与幂等；第九课把本课核对固化为自动测试；第十四课回收用户与身份的唯一性/注销策略。第十一课是 React，不承接本课数据库性能内容。

讲：会写 SQL 不只是语法通顺。你要说明这条查询的每一行代表什么，缺失值算不算，排序是否唯一，以及数据库是否拒绝了业务不允许的状态。

参考：PostgreSQL 文档的 Constraints、Comparison Functions、Subquery Expressions、Using EXPLAIN、Multicolumn Indexes、pg_trgm；SQLAlchemy 2.x 的 text 与参数绑定。跨数据库差异以相应版本实测为准。
