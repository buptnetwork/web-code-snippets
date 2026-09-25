# 第 6 次课教学底稿（第四版）
## 数据建模与 SQL ｜ 含 15 分钟小测

> **备课基线**：[第四版大纲](../syllabus-v4.md)第 6 课与[第 5 课交接](lesson-05.md#64-第-6-课交接)。本稿重写课堂路线、五表参考、学生任务、查询、迁移与验收，尚未移交归档。独立工程、迁移脚本、任务包和课件须随后制作；本稿里的文件名／阶段名是制作约定，不是现有命令入口。

## 〇、这次课建立什么

**讲给学生的目标句**：你能为问答社区画出 ER 图，读懂并补全建表语句，并用两条查询取出页面需要的数据。

核心解释目标：**同一条业务规则，由应用代码保证和由数据库保证，差别在哪。** 先看合法结构和正常查询，再构造一个被数据库拒绝的状态；不是从脏库、坏 DDL 或性能调优开场。

课堂路线：**已有 M1 → 五表关系 → 教师建问题／回答表 → 学生补关联表并构造违规数据 → 两条查询 → 并发与 NULL 短对照 → 小测**。SQLite → PostgreSQL 迁移由教师课前完成；不挤占课堂让学生调驱动，也不提前讲 ORM、完整认证或复杂迁移工具。

### 80 分钟教学 + 15 分钟小测 + 5 分钟缓冲

| 分钟 | 教学单元 | 当场产出 |
|---|---|---|
| 5 | 目标与正常起点 | 指出应用校验和数据库约束各自的位置 |
| 15 | ER 基数与可选性 | 五表关系图、外键所在侧及删除判据 |
| 18 | 教师构建 questions + answers | 两表 DDL、正常插入与查询 |
| 22 | 学生补关联表 | 一处外键、一条组合唯一规则、一条自选违规数据 |
| 12 | 两条业务查询 | 回复数聚合、同时间记录的稳定分页 |
| 8 | 并发预查与 NULL 短演示 | 有／无 UNIQUE 的预测核对、NOT IN 的 NULL 边界 |
| **80** | **教学合计** | **索引实验不占本段时间** |
| 15 | 小测三题 | 读规则、小改动、解释结果 |
| **100** | **总计** | **含 5 分钟缓冲** |

前置是第 3 课已使用的 SELECT、INSERT、值参数绑定，第 4 课的事务提交边界；不要求先会 GROUP BY、外键或 SQLAlchemy。字段规则、数据和提示卡已给定，学生独立选择约束表达方式与测试输入，不自由修改业务要求。

### 教师提供与学生负责

| 提供物 | 标注 | 要求 |
|---|---|---|
| PostgreSQL 连接、隔离库复位、SQLite 导出／迁移器、并发控制器 | 黑盒 | 会按入口运行、读成功／失败摘要，不开发工具、不考内部实现 |
| users、tags、question_tags 三表骨架；questions／answers 演示版 | 要求会用；本课讲到的关系与约束要求解释 | 不从零默写五张表；用同一完成版作课后核对 |
| 两条课堂 SQL、另外两条课后 SQL | 要求解释 | 能说出每行代表什么、预期行与实际行、边界在哪里 |
| 关联表的两处空白、违规样本 | 学生完成并要求解释 | 补一处关系和一条约束，自选一次只触发一个约束的输入 |
| 迁移后的 API 适配、服务事务骨架 | 要求会用，保留前课的事务解释要求 | 不把换库实现追加成学生当堂编码任务 |

超时先压缩附录逐行讲解与 AI 建议讨论，不能吃掉 22 分钟实践或 15 分钟小测。AI 建模对照和两条课后查询进入同一个作业包；不再要求八条查询、必交索引报告或新画一套请求链路图。

## 一、从 M1 出发：已经校验过，为何还需要约束

**课堂 5 分钟。先展示一条正常问题和合法标签关系，再展示同一条规则的两个入口。**

```text
HTML / JSON → QuestionCreate → 服务 → PostgreSQL
导入脚本 / 管理 SQL ────────────────────┘
             应用给出友好反馈       数据库拒绝不允许存在的状态
```

标题唯一已经是 M1 的正确规则，不撤掉交付库的约束制造反例。输入模型保护应用入口，数据库约束保护经过数据库的其他写入路径，并处理竞争；两者互补，不是谁取代谁。

本课正式教学目标为 **PostgreSQL 16、UTF-8**。示例用 PostgreSQL SQL 和 psycopg 3 同步连接；不套用 SQLite 的类型、错误码或锁行为。教师提前核对版本、目标数据库／schema 和虚构数据标记，不把连接串或密码显示给学生。

保留 M1 的三个 JSON 端点、HTML 三页、request-id、错误表现与探针。**课堂 SQL 投影不是新增 HTTP 接口**：回复数和作者查询可以直接在数据库练习，不因此让公开 DTO 自动长出字段。换库期间的批准差异见 §九；原 SQLite 副本留作对照，不覆盖唯一原件。

## 二、先讲业务，再画五表 ER

**课堂 15 分钟。约 5 分钟对象，6 分钟关系与可选性，4 分钟删除预测。**

### 2.1 固定业务规格

- 一个用户可以提出零到多个问题；每个问题必须引用一个用户。
- 一个问题可以有零到多个回答；每个回答必须引用一个问题。
- 回答作者可以未知，因此 author_id 可空；已有非空作者必须存在。
- 一个问题可以有零到多个标签，一个标签可以关联零到多个问题；同一问题与同一标签最多关联一次。
- 问题标题保持精确值唯一，title/body 的长度保持 5–200／10–20000。清洗仍由应用模型负责，数据库不偷偷 trim 文本。
- 用户与作者关系在本课首次建立，但只是虚构身份数据；没有登录、密码、角色、授权，也没有投票、浏览量、状态或采纳功能。

```text
users 1 ── 0..N questions       questions.author_id 必填
users 0..1 ── 0..N answers     answers.author_id 可空
questions 1 ── 0..N answers    answers.question_id 必填
questions 1 ── 0..N question_tags 0..N ── 1 tags
```

讲：外键放在 N 方；question_tags 每行表示“一次关联”，不是一个标签列表字符串。图上“用户可有零个问题”不意味着每个问题的作者都能空，这是关系两端不同的可选性。

### 2.2 类型只选当前确实需要的

| 内容 | 选择 | 为什么与边界 |
|---|---|---|
| 标识 | BIGSERIAL 主键／BIGINT 外键 | 使用数据库序列；允许间隙，不是连续业务编号 |
| 标题、正文、标签 | TEXT；必要处配 CHECK | 类型存文本，规则另写；不机械使用 VARCHAR(255) |
| 创建时间 | TIMESTAMPTZ | 保存时间点；显示受会话时区影响，不保存原时区名称 |
| 标签展示次序 | SMALLINT position | 关系本身无固有顺序，读回必须 ORDER BY |

本课用户表只给 id/display_name/created_at。第 14 课认证要另加注册唯一键、凭据与归属规则；不能把一个显示名当成认证身份。用户名本课不要求唯一，不随意加 UNIQUE 改变规格。

### 2.3 删除策略与第一次预测

本课所有外键均**省略 ON DELETE**，采用 PostgreSQL 默认 NO ACTION；也不声明 DEFERRABLE，因此这里按非延迟约束检查。不会自动删子记录，也不会自动把作者改成 NULL。

**先预测**：问题 101 有三条回答，answers.question_id 外键已存在、未设级联、未延迟检查。对问题 101 执行 DELETE 会怎样？

答案在教师插入 seed 后揭晓：语句被外键拒绝，SQLSTATE **23503**；问题和三条回答都仍在。SQL 失败后的显式事务须先回滚。另一个标签外键也可能阻止相同删除，所以预测验证使用只含 questions/answers 的阶段，确保错误来自所指关系。

这不是“任何删除都 23503”：无子记录时可以成功；CASCADE、SET NULL 或延迟约束会改变结果。可空不等于 SET NULL；本课选默认阻止，其他策略为参考比较，不让不同学生任意更改主线删除契约。

## 三、教师构建：两张主表与一组可手算数据

**课堂 18 分钟。约 8 分钟两表 DDL，5 分钟正常插入与读回，5 分钟约束／删除核对。**

### 3.1 users 是预置骨架，不提前开认证单元

以下各段 `-- lesson06: 名称` 供提取和核验；SQL 在独立空 schema 执行一次。课堂先使用教师准备好的 users 表与用户行，再展示 questions、answers。

```sql
-- lesson06: users_ddl
CREATE TABLE users (
    id BIGSERIAL PRIMARY KEY,
    display_name TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    CONSTRAINT users_name_len CHECK (char_length(display_name) BETWEEN 2 AND 40)
);
```

### 3.2 问题和回答：先满足一个正确插入

```sql
-- lesson06: core_ddl
CREATE TABLE questions (
    id BIGSERIAL PRIMARY KEY,
    title TEXT COLLATE "C" NOT NULL,
    body TEXT NOT NULL,
    author_id BIGINT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    CONSTRAINT questions_author_id_fkey FOREIGN KEY (author_id) REFERENCES users(id),
    CONSTRAINT questions_title_key UNIQUE (title),
    CONSTRAINT questions_title_len CHECK (char_length(title) BETWEEN 5 AND 200),
    CONSTRAINT questions_body_len CHECK (char_length(body) BETWEEN 10 AND 20000)
);

CREATE TABLE answers (
    id BIGSERIAL PRIMARY KEY,
    question_id BIGINT NOT NULL,
    author_id BIGINT,
    body TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    CONSTRAINT answers_question_id_fkey FOREIGN KEY (question_id) REFERENCES questions(id),
    CONSTRAINT answers_author_id_fkey FOREIGN KEY (author_id) REFERENCES users(id),
    CONSTRAINT answers_body_len CHECK (char_length(body) BETWEEN 10 AND 10000)
);
```

回答正文 10–10000 是本课新表的规则，不声称第 3 课已经交付回答接口。title 的 `COLLATE "C"` 为精确比较锁定可复现口径：不同大小写、前后空白仍是不同存储值；应用先 strip 才会把相同清洗标题识别为重复。它不等于自动完成所有 Unicode 归一化。

### 3.3 固定小数据

```sql
-- lesson06: core_seed
INSERT INTO users (id, display_name) VALUES
    (1, '示例用户甲'), (2, '示例用户乙'), (3, '示例用户丙');
INSERT INTO questions (id, title, body, author_id, created_at) VALUES
    (101, 'Python 100% 字面搜索', '练习百分号只是普通文本的查询。', 1, '2026-09-01T08:00:00Z'),
    (102, 'SQL 同时间分页问题', '这条记录与问题一零一时间相同。', 2, '2026-09-01T08:00:00Z'),
    (103, '零回答的较新问题', '这是较新的问题但尚未收到回答。', 1, '2026-09-02T08:00:00Z'),
    (104, '另一个较早的问题', '这条问题创建得更早且暂时没有回答。', 3, '2026-08-31T08:00:00Z');
INSERT INTO answers (id, question_id, author_id, body) VALUES
    (201, 101, 2, '第一条回答提供一个正常的解决思路。'),
    (202, 101, NULL, '第二条回答保留文本但作者暂时未知。'),
    (203, 101, 2, '第三条回答补充另一个有效的说明。'),
    (204, 102, 1, '这个回答用于核对另一个问题的计数。');
```

正常核对：3 位用户、4 个问题、4 条回答；101 有 3 条、102 有 1 条、103/104 为 0。固定数据与 M1 导入数据是两套隔离来源，不能混装后还照抄这些数量。

手动指定 id 不会自动推进序列；教师在 seed／导入后执行 §9.4，再演示自动 id 插入。正常插入成功必须显式 COMMIT 才对另一个连接可见，DDL 成功不等于有数据，INSERT 成功也不等于已提交。默认 now() 取当前事务的开始时间，不是每一行写入瞬间重新读一次时钟；导入已有记录必须显式传原时间。

### 3.4 四种约束与错误信息

| 约束 | 拒绝的状态 | 本课核对的 SQLSTATE |
|---|---|---|
| NOT NULL | 必填列收到 NULL | 23502 |
| CHECK | 条件为 FALSE，如标题只有 4 字符 | 23514 |
| UNIQUE／PRIMARY KEY | 重复业务键或主键 | 23505 |
| FOREIGN KEY | 非空引用不存在，或父行删除破坏引用 | 23503 |

CHECK 为 UNKNOWN（如 NULL 比较）时可通过，所以“长度 CHECK”不能代替 NOT NULL。DEFAULT 只在省略值或显式 DEFAULT 时生效，不能修正显式 NULL。普通 UNIQUE 对可空列通常允许多个 NULL；本课关键列另有 NOT NULL。

一条批量 INSERT 中任一行违反非延迟约束，整条语句不留下部分行；多个 SQL 组成的业务操作仍须统一事务。序列消耗不回滚，不用 id 缺口推断“少存了一条”。

psycopg 取 `exc.sqlstate` 与 `exc.diag.constraint_name`；psql 教师配置详细错误显示。记录实际错误消息、码与约束名即可，不考英文全文。错误消息可能含数据，只用虚构样本，不复制成公开 HTTP 响应。

## 四、学生任务：补关系与组合约束，再自己构造一次失败

**课堂 22 分钟。建议 4 分钟定位两处空白，7 分钟完成 DDL 与合法插入，7 分钟自选违规值并回滚核对，4 分钟互查保存。**

### 4.1 先给 tags 和关联表骨架

教师提供 users、tags、question_tags 三表骨架；questions／answers 来自刚才的正常演示。学生不另写五张表，不开发复位脚本。

```sql
-- lesson06: tags_ddl
CREATE TABLE tags (
    id BIGSERIAL PRIMARY KEY,
    name TEXT COLLATE "C" NOT NULL,
    CONSTRAINT tags_name_key UNIQUE (name)
);
```

迁移规格固定：标签名按原字符串比较，不 trim、大小写归一或过滤空字符串。同一问题的重复标签只保留首次出现，关联位置从 1 开始；这是 §九 登记的标签规范化差异。position 的范围／唯一约束由教师提供，不作为额外学生空白。

```text
CREATE TABLE question_tags (
    question_id BIGINT NOT NULL,
    tag_id BIGINT NOT NULL,
    position SMALLINT NOT NULL,
    CONSTRAINT question_tags_question_id_fkey
        FOREIGN KEY (question_id) REFERENCES questions(id),
    CONSTRAINT question_tags_tag_id_fkey
        FOREIGN KEY (tag_id) REFERENCES ______ (______),
    CONSTRAINT question_tags_pkey ______ (question_id, tag_id),
    CONSTRAINT question_tags_position_key UNIQUE (question_id, position),
    CONSTRAINT question_tags_position_range CHECK (position BETWEEN 1 AND 5)
);
```

两处要实现的需求：① tag_id 必须指向已有标签；② 同一问题与标签不得重复关联。学生可用等价的约束表达，但不能仅让 tag_id 单列 UNIQUE（那会使标签无法复用）。本基线选择联合主键；若用独立主键，仍须有 `(question_id, tag_id)` UNIQUE，核对时说明差异。

完成后再展示参考：

```sql
-- lesson06: association_ddl
CREATE TABLE question_tags (
    question_id BIGINT NOT NULL,
    tag_id BIGINT NOT NULL,
    position SMALLINT NOT NULL,
    CONSTRAINT question_tags_question_id_fkey
        FOREIGN KEY (question_id) REFERENCES questions(id),
    CONSTRAINT question_tags_tag_id_fkey
        FOREIGN KEY (tag_id) REFERENCES tags(id),
    CONSTRAINT question_tags_pkey PRIMARY KEY (question_id, tag_id),
    CONSTRAINT question_tags_position_key UNIQUE (question_id, position),
    CONSTRAINT question_tags_position_range CHECK (position BETWEEN 1 AND 5)
);
```

位置唯一、非空且只能为 1–5，使同一问题最多有五条关联；不会自动保证位置连续。插入辅助函数负责连续编号，数据库并不替它排序。标签列表的输入上限仍在去重之前检查，六个重复输入也不能逃过第 3 课的最多五项规则。

### 4.2 正常样本先跑通

```sql
-- lesson06: association_seed
INSERT INTO tags (id, name) VALUES (1, 'python'), (2, 'sql');
INSERT INTO question_tags (question_id, tag_id, position) VALUES
    (101, 1, 1), (101, 2, 2), (102, 1, 1), (104, 2, 1);
```

预期 4 条关联：101 同时有两个标签，python 也能被 102 使用，103 没有标签。无关联是合法空集合，不写一条 tag_id=NULL 的“占位关联”。

### 4.3 自己选违规输入，但一次只触发一个边界

可选方向：不存在的 tag_id（23503）；重复 `(question_id, tag_id)`（23505）。若已有 `(101,1,1)`，想专测组合主键，应提交 `(101,1,3)`，不要同时复用 position=1，否则可能先报另一条唯一约束。

每轮使用教师的独立事务包装：**正常库状态 → BEGIN → 一条违规 SQL → 记错误／码／约束 → ROLLBACK → 查行数和原关联**。失败后直接 SELECT 可能得到 25P02（事务已失败），不能把它误记为原业务错误；先回滚再核对。SAVEPOINT 为教师设施可选方式，不要求学生自己设计嵌套事务。

保留一条成功对照和一条自选失败即可。不得只交“运行失败”截图；要指出哪条约束在保护哪条业务规则，为什么原记录不变。NOT NULL／CHECK 的其他边界由教师回归器课后帮助核对，不加多份证据配额。

## 五、两条课堂 SQL：先确定每行代表什么

**课堂 12 分钟。约 6 分钟回复数，4 分钟稳定分页，2 分钟逻辑顺序。下列 Q1/Q2 在固定 seed、没有并发写入时核对。**

### Q1：包括零回答的问题与回复数

```sql
-- lesson06: q1_counts
SELECT q.id, q.title, count(a.id) AS answer_count
FROM questions q
LEFT JOIN answers a ON a.question_id = q.id
GROUP BY q.id, q.title
ORDER BY q.id;
```

| 问题 id | 101 | 102 | 103 | 104 |
|---|---|---|---|---|
| answer_count | 3 | 1 | 0 | 0 |

输出粒度为“每个问题一行”。LEFT JOIN 给无回答问题保留一条补空行；`count(a.id)` 不数 NULL，因此为 0。若误用 `count(*)`，103/104 都变成 1；INNER JOIN 则直接漏掉它们。作者为 NULL 的回答仍有非空 a.id，计入回复数。

不要顺手再 JOIN question_tags：101 的三条回答和两个标签会组合成六行，直接计数就被放大。需要两个集合时先各自聚合，再连接结果；本课只要求看懂一处放大风险，不追加多关系查询任务。

### Q2：同时间记录也能确定次序的分页

```sql
-- lesson06: q2_page
SELECT id, title, created_at
FROM questions
ORDER BY created_at DESC, id DESC
LIMIT 2 OFFSET 0;
```

固定 seed 第一页为 **103、102**；同一 SQL 仅把 OFFSET 改成 2，第二页为 **101、104**。总数另查 `SELECT count(*) FROM questions` 为 4，不是当前页的 2。应用绑定参数时 offset=`(page-1)*page_size`；page／page_size 仍须先按既有范围校验。

只按 created_at 排序时，101/102 的相对次序没有保证，不要求每台机器每次都复现漏行。唯一的 id 是决胜键。稳定排序保证的是固定数据下的确定次序，不能阻止并发插删导致 OFFSET 跨页漂移；两条计数／读取语句在 READ COMMITTED 下也不自动共享同一快照。

**Q2 是独立 SQL 学习结果，不直接替换 M1 的公开列表**：本轮公开 API／HTML 仍按 id DESC，不能在“换库”时悄悄改为按创建时间；第 7 课翻译既有列表也须保留这一点。

### 5.1 逻辑顺序卡

```text
FROM / JOIN → WHERE → GROUP BY → HAVING → SELECT → ORDER BY → LIMIT / OFFSET
```

WHERE 过滤分组前的行，HAVING 过滤分组结果；ORDER BY 可用 SELECT 中的输出别名。逻辑顺序帮助解释结果，不是数据库物理执行计划；不把每一段都解释为“服务器必须按这个顺序逐行执行”。

### Q3：同时包含 python 和 sql 的问题（课后）

```sql
-- lesson06: q3_both_tags
SELECT q.id, q.title
FROM questions q
JOIN question_tags qt ON qt.question_id = q.id
JOIN tags t ON t.id = qt.tag_id
WHERE t.name IN ('python', 'sql')
GROUP BY q.id, q.title
HAVING count(DISTINCT t.id) = 2
ORDER BY q.id;
```

预期只有 **101**。这里固定为两个不同标签；IN 先取任一匹配行，HAVING 再要求两种标签都出现。不能只写 IN 就说成“同时具备”；不布置动态标签数量或空列表语义设计。

### Q4：从未被任何回答引用为作者的用户（课后）

```sql
-- lesson06: q4_no_answers
SELECT u.id, u.display_name
FROM users u
WHERE NOT EXISTS (
    SELECT 1 FROM answers a WHERE a.author_id = u.id
)
ORDER BY u.id;
```

预期只有 **3**。未知作者不归给任何现存用户；NULL 不等于用户 0，更不能根据“作者未知”猜其身份。Q4 回收下一单元的短演示，不增加一个独立 NULL 大实验。

## 六、八分钟对照：预查不是约束，NULL 不是普通值

**课堂 8 分钟。5 分钟并发（含预测），3 分钟 NULL。教师工具已准备好，不现场开发双连接控制器。**

### 6.1 有／无唯一约束：条件必须写全

只在两个独立、初始为空的教师实验表运行；不改合格 questions 表：

```sql
-- lesson06: race_ddl
CREATE TABLE race_without_unique (id BIGSERIAL PRIMARY KEY, title TEXT NOT NULL);
CREATE TABLE race_with_unique (
    id BIGSERIAL PRIMARY KEY,
    title TEXT NOT NULL,
    CONSTRAINT race_title_key UNIQUE (title)
);
```

**先预测**：两条独立连接 A/B，READ COMMITTED，非自动提交；相同合法标题，初始无此标题。两者都完成普通 SELECT 预查且结果为空后，A 插入并保持未提交，B 尝试插入，最后让 A 提交。没有其他写入、超时或重试。各表最终多少行？

| 条件 | A | B | 两者事务结束后的独立回读 |
|---|---|---|---|
| 无标题唯一约束 | 插入并提交 | 插入并提交 | 2 行，相同标题 |
| 有标题唯一约束 | 插入并提交 | 等待竞争结果，A 提交后报 23505，再回滚 | 1 行 |

教师控制器的步骤：两次空预查 → A INSERT → 启动 B INSERT → 观察状态 → A COMMIT → B 完成／错误并 ROLLBACK → 第三连接统计。**不要让 A 等待 B 插入完成才提交**，有 UNIQUE 时会互等到超时。用可观测锁状态或同步点安排时序，不靠“同时点两下”猜竞争发生。

实验有超时则如实记录，不能把超时当 23505。A 若回滚，B 可能成功；SERIALIZABLE、重试或其他失败会改变轨迹。保留两张独立表，不能在已经生成重复的表上直接 ADD UNIQUE；真实旧数据必须先核查再决定如何处理。

结论：预查可优化友好提示，但不能保证并发唯一；已知 questions_title_key 冲突才翻译为 DuplicateTitle。其他 23505（如标签名／关联）、23503 或存储故障不能都变成“标题重复”。

### 6.2 NULL 与 NOT IN：短到可以手算

```sql
-- lesson06: null_not_in
WITH sample_users(id) AS (VALUES (1), (2), (3)),
     sample_authors(author_id) AS (VALUES (1), (NULL::integer))
SELECT id, id NOT IN (SELECT author_id FROM sample_authors) AS never_answered
FROM sample_users ORDER BY id;
```

结果依次为 **FALSE、NULL、NULL**。用户 1 命中已知值所以 FALSE；2/3 虽未命中，但右侧含未知值，不能得出 TRUE。WHERE 只保留 TRUE，所以把该条件放进 WHERE 后没有行；不是三行都 UNKNOWN，也不是运行错误。

```sql
-- lesson06: null_not_exists
WITH sample_users(id) AS (VALUES (1), (2), (3)),
     sample_authors(author_id) AS (VALUES (1), (NULL::integer))
SELECT u.id FROM sample_users u
WHERE NOT EXISTS (
    SELECT 1 FROM sample_authors a WHERE a.author_id = u.id
)
ORDER BY u.id;
```

结果 **2、3**，表达“找不到一条引用这个用户的回答”。普通 `NULL = NULL` 不是 TRUE，查空用 IS NULL。这里用独立 VALUES，不往主表灌违反约束的脏数据；NOT EXISTS 不是在所有数据库上更快的承诺。

### 常用写法卡 #6

| 写法 | 数据库替我们做什么 | 必须知道的边界 |
|---|---|---|
| 外键位于 N 方／连接表 | 组织引用与多对多关系 | 可选性和删除策略来自规格，不自动等于级联 |
| 类型 + NOT NULL + CHECK | 拒绝不合法存储状态 | CHECK 不禁止 UNKNOWN，类型不替代完整业务规则 |
| UNIQUE／联合主键 | 在并发下裁决重复键 | 预查不是保证；只能翻译已知约束冲突 |
| LEFT JOIN + count(a.id) | 保留零回答问题并计数 | count(*) 会数补空行，多集合连接可放大行数 |
| ORDER BY 时间, id + LIMIT/OFFSET | 固定数据下确定分页次序 | 不能保证并发插删时跨页无漂移 |
| GROUP BY／HAVING | 按输出粒度汇总和筛组 | SQL 逻辑顺序不是物理执行顺序 |
| NOT EXISTS | 表达没有匹配关系 | NOT IN 遇到右侧 NULL 可能不返回预期行 |

## 七、15 分钟小测：三题，不启动工程

教师发固定片段和小数据；题面包含所需列、约束和初始条件。**3/5/7 分钟，共 15 分钟，10 分**。小测不要求连库、运行迁移器或理解并发控制器内部；三次小测整体覆盖四种能力，本次不强求每种能力各出一题。

### 题 1：读关系与解释拒绝（3 分钟，3 分）

给定 questions(id 主键)，answers(question_id 非空、外键到 questions.id)，未指定 ON DELETE，也未延迟约束检查；问题 101 有三条回答。在显式事务中 DELETE 101：会不会删除回答？问题是否被删？下一步如何恢复事务以便查证？

教师答案：不级联；原问题／回答保留（1 分）；因外键引用而拒绝，23503（1 分，代码给在速查卡上，不考死记）；先 ROLLBACK 再 SELECT 核对（1 分）。

### 题 2：补一条组合规则并选测试值（5 分钟，3 分）

给定关联表的两个外键已经正确，position 非空／范围 1–5／同问题位置唯一。已有 `(question_id,tag_id,position)=(101,1,1)`。补一条“不许同一问题重复关联同一标签”的约束，并给出专测它的违规三元组。

教师答案：PRIMARY KEY(question_id,tag_id) 或等价 UNIQUE（1 分）；例如 (101,1,3)，不用不存在的外键或已有位置混入另一个错误（1 分）；23505 且回滚后原关联不变（1 分）。

### 题 3：手算与局部修复（7 分钟，4 分）

只给两个问题：id 11/12，created_at 相同；11 有两条回答，12 无回答。查询用 LEFT JOIN、按问题分组、`count(*) AS n`，只按 created_at DESC 排序。

1. n 分别是什么，为什么零回答问题不是 0？
2. 改哪一处得到正确回复数？
3. 每页一条，补什么排序才能确定第一页？

教师答案：11→2、12→1，后者有补空行（2 分）；改 count(a.id)，变为 2／0（1 分）；追加 id DESC，第一页 12（1 分）。固定数据无并发，不要求解释优化器或 keyset。

讲评只对照职责和结果，不以背诵特定排版得分；失败题的错误码由速查卡提供。若试讲发现阅读量过大，缩短题面而不是挪用学生实践时间。

## 八、一个作业包与第 7 课交接

### 8.1 A 档：五表、约束、四条查询、一次 AI 判断

1. 五表 ER／DDL：标外键所在侧、可选性及本课默认删除策略，包含自己补的两处内容；不必从空白重画已有正确图。
2. 约束证据：合法关联与一次自选违规输入，错误消息／SQLSTATE／约束名，回滚后数据结果；课堂材料可直接复用。
3. Q1–Q4 四条 SQL 的参数、预期与实际结果：课堂两条，课后两条。说清计数粒度、稳定排序、标签 AND 与未知作者；没有“另写四条”或八条配额。
4. 让 AI 给一版局部建模建议，逐条判断是否满足当前规格。合理则保留，说明依据；如建议级联、加角色、把全部字段设可空，说明为何本课采用或不采用，不要求 AI 必须出错。

常用写法卡只补一个自己的例子，放进同一包。SQL 工具内部、数据库安装及迁移脚本不是学生新增编码任务；本课不要求新增所有回答／标签 HTTP 接口，也不提前交 M2。

### 8.2 选做：只选一条查询评估索引

在可丢弃的性能副本固定数据、参数与重复次数。先核对查询结果一致，再比较 EXPLAIN (ANALYZE, BUFFERS) 的实际行数、扫描／Sort、耗时与波动。可评估 Q2 的 `(created_at DESC, id DESC)` 索引或 Q1 的 answers(question_id)，不机械全部添加。

主键／唯一约束已有支撑索引；PostgreSQL 不自动给所有引用侧外键建索引。小表 Seq Scan 可以合理，未提速也可达标；不承诺固定倍数，不强制十万行。ANALYZE 会实际执行，本课只对 SELECT 使用。采用的索引登记进交接表，候选不能悄悄变成第 7 课必建结构。

### 8.3 第 7 课接收的明确基线

- PostgreSQL 16 目标五表、约束名、默认 NO ACTION、position 顺序规则、虚构用户映射；不沿用旧稿的 CASCADE、密码／角色／状态／浏览量。
- 四条小数据查询及结果；公开 M1 列表仍 id DESC，Q2 的时间排序与 Q1 的回复数投影属于 SQL 练习，不自动改 DTO。
- 同步 psycopg 3 的教师服务基线，QuestionCreate 与五字段输出、API 201／HTML 303、422／409 表现、request-id 和单 status 探针；标签去重的明确回归差异。
- 服务拥有一整个创建操作的事务，内部写问题／标签／关系不各自提交；换 Session 后仍由服务显式 commit，依赖只关闭。提交前和确认后故障均须独立连接核对。
- 按 v4 第 7 课：教师提供创建 ORM 基线并要求解释，学生课堂只迁列表、课后迁详情；N+1 由教师引导同契约对照，Alembic 空库建链与一次 upgrade 按模板会用。

现有第 7 课底稿仍为旧路线，包含依赖退出提交、更多字段、级联策略及八条旧 SQL 的引用，必须另行按 v4 重写；本轮不把它视为已同步，也不扩展为重写该课。

## 九、教师附录：迁移是独立核对流程，不是课堂隐藏任务

### 9.1 分离三个环境和两个阶段

- **M1 迁移副本**：从只读 SQLite 快照导入 PostgreSQL 空 schema，验证旧业务；不混入 101–104 的教学 seed。
- **课堂小库**：五表和本稿固定 seed，用于预测、约束和四查询；演示失败可恢复，不能覆盖学生唯一数据。
- **并发／索引实验副本**：只放专用实验表或受控数据；不能通过删除项目约束复用交付库。

阶段 A 只在副本完成迁移预检／结构／导入／数据核对；阶段 B 才接入教师 API 适配并做 JSON、HTML 与故障回归。任一阶段失败不切换学生主入口。迁移是新目标导入，不是原地删 SQLite 表；两库写入不能并行混用造成分叉。

### 9.2 契约与数据变更表（本课教师基线）

| 项目 | 本课决定 | 必须核对 |
|---|---|---|
| 已有问题 | 保留 id/title/body/created_at；不重新生成时间或按时间重排 id | 逐 id 文本一致、时间点一致、问题总数一致 |
| 用户与作者 | 所有旧问题映射到教师提供的虚构用户 id=1；新教学创建也由服务配置指定该用户 | 不读取客户端 author_id；公开输入仍拒绝额外字段，没有认证保证 |
| 标签 | 按精确字符串去重，保留首次出现顺序；空字符串和带空白名保留，不 trim／排序 | 旧 `['a','a','',' b']` → `['a','',' b']`；保存去重报告与源快照 |
| 标签传输 | JSON 仍 list[str] 且最多五项，先校验原列表再去重；HTML 仍空栏→[]，否则逗号 split | 六个重复项仍 422；失败回填原输入不变，成功读回规范化列表 |
| 公开列表 | keyword/page/page_size 仍默认空／1／20，上限 50，字面搜索，id DESC | total 为过滤后分页前总数；无匹配 200 空列表，%/_ 不变通配符 |
| 输出与错误 | 五字段 id/title/body/tags/created_at；items/total/page；四字段 JSON 错误与 HTML 分流 | 不自动公开作者／回复数；整数缺失 404、非法类型 422；已知标题冲突 409 |
| 成功与探针 | JSON 201 + Location，HTML 提交完成后 303；healthz 查询 SELECT 1，200 ok／预期数据库故障 503 degraded | 探针仍只含 status；服务显式提交，默认依赖只清理 |

标签去重是本次关系规范化的**明确行为变更**，不是“换数据库所以所有测试原封不动”。模型长度、清洗、额外字段规则不变，只有成功返回的重复标签期望及关系存储发生变化；JSON 和 HTML 使用同一辅助函数。原数据未改变的记录仍须逐项相同，不能重写全部快照来掩盖差异。

### 9.3 导入前先预检，不能自动吞掉坏数据

教师迁移器必须检查：源结构／记录数、id 唯一且适合 BIGINT、title/body 已符合当前模型且不需二次清洗、精确标题无冲突、tags_json 可解为最多五个字符串、created_at 含有效时区。拒绝无时区时间，不按本机时区猜测；比较时间点而非 Z／+00:00 的字面形式。

目标 PostgreSQL 文本不接受 U+0000，UTF-8 不接受孤立代理字符；TIMESTAMPTZ 和 Python 时间均有表示范围／精度边界。标签虽为 TEXT，唯一索引仍有索引项大小限制，不能把“不限制标签字符数”理解为任意大字符串都能存入该索引。源数据遇到这些情况应中止并给脱敏问题报告，保留源快照；不能截断、替换字符或直接跳过记录。未完成这类处理前不宣称全量迁移等价。

目标短文本样本和新写入都先经过共享模型；未识别的数据库存储错误仍走回滚与 500，不混成标题 409。若产品要把额外存储限制升级成输入 422，必须另行登记 JSON／HTML 共同规则，本课没有悄悄增加这一规则。

辅助函数参考（教师基础设施，不追加学生编码任务）：

```python
# lesson06: tag_normalization

def ordered_unique_tags(tags: list[str]) -> list[str]:
    return list(dict.fromkeys(tags))
```

它只负责既定去重，不负责类型／五项校验；只能接收共享模型已验证的列表。迁移器也先验证再调用，不能拿函数替代整个预检。

迁移顺序：备份并冻结源快照 → 预检全部问题并生成去重报告 → 在独立目标建五表 → 插虚构用户 → 保留 id 导入问题／时间 → 建精确标签并按首次顺序写 position → 同事务核对数量与关联 → 显式提交 → 校准序列 → 独立连接逐项回读 → 阶段 B HTTP 回归。任一步失败停止切换；保存检查记录，不把已删重复项说成可由结构回退自动恢复。

### 9.4 显式 id 导入后，校准每个序列

以下只在教师独占、没有并发写入的导入目标执行。非空表最大正 id 后继续；空表或只有非正 id 时从 1 开始。

```sql
-- lesson06: reset_sequences
SELECT setval(pg_get_serial_sequence('users', 'id'),
              GREATEST(COALESCE(max(id), 1), 1), COALESCE(max(id) >= 1, false)) FROM users;
SELECT setval(pg_get_serial_sequence('questions', 'id'),
              GREATEST(COALESCE(max(id), 1), 1), COALESCE(max(id) >= 1, false)) FROM questions;
SELECT setval(pg_get_serial_sequence('answers', 'id'),
              GREATEST(COALESCE(max(id), 1), 1), COALESCE(max(id) >= 1, false)) FROM answers;
SELECT setval(pg_get_serial_sequence('tags', 'id'),
              GREATEST(COALESCE(max(id), 1), 1), COALESCE(max(id) >= 1, false)) FROM tags;
```

BIGINT 最大值已被占用时序列不能再生成下一值，预检须阻止该情况。setval／nextval 的序列状态不随普通事务回滚；校准是受控步骤，不与并发新写入混跑。正常回归允许 id 有间隙。

### 9.5 psycopg 3 参数与旧搜索契约

本稿 SQL 围栏中的 Q1–Q4 用固定常量，可直接在隔离 psql 执行；应用不得通过字符串替换注入值。psycopg 用 `%s` 或 `%(name)s`，与 SQLite 的 `:name` 不同，不能把 SQLAlchemy text() 当成前置要求。

保留英文字母样本不区分大小写、关键词 strip、字面子串的教师 SQL 参考：

```python
# lesson06: search_reference

SEARCH_SQL = """
    SELECT id, title, body, created_at
    FROM questions
    WHERE strpos(lower(title COLLATE "C"), lower(%(keyword)s COLLATE "C")) > 0
       OR strpos(lower(body COLLATE "C"), lower(%(keyword)s COLLATE "C")) > 0
    ORDER BY id DESC LIMIT %(limit)s OFFSET %(offset)s
"""
COUNT_SQL = """
    SELECT count(*) AS total FROM questions
    WHERE strpos(lower(title COLLATE "C"), lower(%(keyword)s COLLATE "C")) > 0
       OR strpos(lower(body COLLATE "C"), lower(%(keyword)s COLLATE "C")) > 0
"""
```

调用者传 keyword.strip()、limit=page_size、offset=(page-1)*page_size，同一 keyword 用于 count。strpos 不把 %/_ 当通配符，无需 LIKE 转义；参数绑定防 SQL 语法注入，两者目的不同。仅承诺既有英文样本口径，不保证任意语言的 Unicode 大小写折叠。标签由关联表按 position 读回，再组装既有五字段 DTO。

### 9.6 写服务参考：一个业务操作统一提交

教师连接工厂使用 psycopg 3、dict_row、autocommit=False、READ COMMITTED，每请求独立连接。同步 def 端点调用以下同步服务；依赖仅 yield／finally close，不用连接上下文的退出隐式提交代替服务 commit。第 4 课 AppError／DuplicateTitle 和第 3 课 QuestionOut 继续复用。

```python
# lesson06: create_service
import psycopg


def write_question(conn, payload, *, author_id):
    qid = conn.execute("""
        INSERT INTO questions (title, body, author_id)
        VALUES (%s, %s, %s) RETURNING id
    """, (payload.title, payload.body, author_id)).fetchone()["id"]
    for position, name in enumerate(ordered_unique_tags(payload.tags), start=1):
        row = conn.execute("""
            INSERT INTO tags (name) VALUES (%s)
            ON CONFLICT ON CONSTRAINT tags_name_key DO NOTHING RETURNING id
        """, (name,)).fetchone()
        if row is None:
            row = conn.execute("SELECT id FROM tags WHERE name = %s", (name,)).fetchone()
        if row is None:
            raise RuntimeError("标签状态已变化")
        conn.execute("""
            INSERT INTO question_tags (question_id, tag_id, position) VALUES (%s, %s, %s)
        """, (qid, row["id"], position))
    return qid


def read_question_dto(conn, qid):
    row = conn.execute("""
        SELECT id, title, body, created_at FROM questions WHERE id = %s
    """, (qid,)).fetchone()
    if row is None:
        return None
    labels = conn.execute("""
        SELECT t.name FROM question_tags qt JOIN tags t ON t.id = qt.tag_id
        WHERE qt.question_id = %s ORDER BY qt.position
    """, (qid,)).fetchall()
    return QuestionOut.model_validate({**row, "tags": [t["name"] for t in labels]})


def create_question_service(conn, payload, *, author_id):
    try:
        qid = write_question(conn, payload, author_id=author_id)
        result = read_question_dto(conn, qid)
        if result is None:
            raise RuntimeError("创建后的回读缺失")
        conn.commit()
        return result
    except psycopg.IntegrityError as exc:
        conn.rollback()
        if exc.sqlstate == "23505" and exc.diag.constraint_name == "questions_title_key":
            raise DuplicateTitle() from exc
        raise
    except Exception:
        conn.rollback()
        raise
```

write_question 不单独提交；创建问题、标签、关系、回读校验都属于服务事务。JSON／HTML 端点只做输入适配和 HTTP 翻译，不把 303 提前到服务成功之前。已知标题冲突才映射，其他完整性错误保留给安全 500；输入校验仍为 422，不能把服务输出校验误算成输入错误。

标签并发逻辑以 READ COMMITTED 且无并发删除／重命名为条件：ON CONFLICT 等待竞争结果，DO NOTHING 后下一条 SELECT 可见已提交标签。多标签交错写入仍可能死锁；数据库会中止一个事务，不产生半截成功，不能据此承诺全部请求成功或自动重试。该复杂性不作为课堂现场任务。

沿用第 4 课两种教师故障：write_question 完成且 commit 未调用时抛错，回滚后问题／新标签／关联都无本次新增；commit 已确认成功返回后、HTTP 响应启动前抛错，500 但数据仍在。后者 rollback 不能撤销已提交结果。网络在提交期间断开属于结果未知，不由这两个开关模拟，不自动重复写入。

## 十、制作与验证状态

本稿是教学底稿，不是已交付的 PostgreSQL 课程工程。完整迁移器、API 适配、连接配置、任务骨架、并发设施与课程自检器仍需制作。

- **本轮机制验证已完成**：从本稿提取全部 DDL、seed、四条查询、NULL 对照、序列 SQL 和 Python 服务参考，复用第 3 课实际模型。在独立 PostgreSQL 集群通过 251 项断言（247 项行为／结构／数据检查，4 项课时与任务范围检查），另在该集群正常停止并重启后通过 3 项独立连接回读，累计 254 项；不沿用旧稿的 SQLite 验证结论。
- **实际版本与隔离**：Python 3.12.12、psycopg 3.3.6、PostgreSQL **18.6**，UTF-8、C locale、测试会话 UTC。本机未找到 PostgreSQL 16，Docker daemon 不可用；没有启动 Docker、安装新数据库版本或修改工程依赖／锁文件。新建工作区内专用集群，仅监听权限 0700 的 Unix socket，不连接已有业务库，结束后已停止。**本课目标仍是 PostgreSQL 16，尚未完成目标版本验收，18.6 结果不替代它。**
- **已覆盖**：五表／五个非延迟 NO ACTION 外键、正常 seed、四查询与分页结果、LEFT JOIN 补空／多集合放大、NULL、字面搜索与旧 id 排序、五字段读回、26 组约束拒绝及原错误码／25P02／回滚、合法长度与空标签、三回答删除预测、共享模型拒绝、稳定去重／顺序、已知标题异常分类、服务提交及输出失败回滚、提交确认后异常数据保留、空表／非正 id／导入后序列、小测答案与 80+15+5 时长。
- **并发实测**：两连接均先读到空、READ COMMITTED；无 UNIQUE 两次提交后为 2 行，有 UNIQUE 时观察到 B 等锁，A 提交后 B 为 23505／race_title_key，B 回滚后第三连接读到 1 行。另核对两个问题竞争同一新标签：ON CONFLICT 等待后，两问题共享一条标签、保留两条关联。此为真实 PostgreSQL 连接实验，不是 HTTP 负载或课堂工具验收。
- **证据边界**：本轮使用本稿固定虚构 seed 和独立 schema，未执行完整 M1 SQLite 文件迁移或生产应用切换；服务测试复用实际事务代码，但未接 FastAPI／HTML／中间件，所以不声称 201／303／500 的完整 HTTP 链已验收。正常重启回读只证明本轮专用集群已提交样本仍可见，不证明断电、真实提交期间断连或结果未知。临时核验脚本不等于学生自检器、迁移器或教师并发包。

工作区临时复核入口（须先启动上述专用集群及匹配的本地 socket；不作为学生工程启动命令）：

```bash
uv run --offline --project snippets/ch01/m0-tracer --no-sync python .build-check/validate_lesson06.py
```

- **试讲前必须补齐**：PostgreSQL 16 锁定环境、五表起点／完成版、两个空白的学生任务壳、错误速查卡、三个隔离环境、只读源快照与迁移报告、四查询预期结果、双连接并发控制器和备用记录、小测题面与评分卡。
- **迁移与应用验收**：真实 M1 SQLite 文件到 PostgreSQL 的完整迁移，序列与重启后回读；JSON／HTML 三页／输入失败／标题冲突／303／request-id／healthz 全链回归；提交前／确认后故障均独立查库。只验证 SQL 或服务不能声称这些都已完成。
- **教学负荷验证**：观察学生在 22 分钟完成两个空白与一次违规核对、15 分钟完成三题所需提示；记录把可空当作 SET NULL、把 count(*) 当作回复数、把预查当唯一保证的错因。代码正确不等于试讲负荷已验证。

参考：PostgreSQL 16 文档的 Constraints、Transaction Isolation、Subquery Expressions、Sequence Manipulation Functions、Using EXPLAIN；psycopg 3 的参数绑定、事务与错误诊断。最终课件再把教师时间安排、制作待办放进备注，保留学生必须理解的规则与证据边界。
