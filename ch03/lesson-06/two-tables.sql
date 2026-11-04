-- 两表阶段：仅在教师提供的空 schema 中执行，与五表阶段隔离。
-- 初始化由调用者开启事务；成功后提交，失败则回滚。

-- #region questions-ddl
CREATE TABLE questions (
    id BIGSERIAL PRIMARY KEY,
    title TEXT NOT NULL,
    body TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL
        DEFAULT now()
);
-- #endregion questions-ddl

-- #region answers-ddl
CREATE TABLE answers (
    id BIGSERIAL PRIMARY KEY,
    question_id BIGINT NOT NULL
        REFERENCES questions(id),
    body TEXT NOT NULL
);
-- #endregion answers-ddl

-- #region questions-seed
INSERT INTO questions (id, title, body, created_at) VALUES
    (101, 'Python 如何读取问题列表？',
     '希望理解列表查询如何从数据库取出问题。',
     '2026-09-01T08:00:00Z'),
    (102, 'SQL 查询从哪里开始？',
     '希望先弄清表和记录再逐步学习查询语句。',
     '2026-09-01T08:00:00Z');
-- #endregion questions-seed

-- #region answers-seed
INSERT INTO answers (id, question_id, body) VALUES
    (201, 101, '可以先用 SELECT 读取问题表中的记录。'),
    (202, 101, '再通过 WHERE 保留满足条件的问题记录。'),
    (203, 101, '最后使用 ORDER BY 明确结果的显示顺序。');
-- #endregion answers-seed

-- #region read
SELECT id, title FROM questions ORDER BY id;
SELECT id, question_id FROM answers ORDER BY id;
-- #endregion read

-- 显式 id 不推进序列；仅在独占初始化环境校准。
SELECT setval(pg_get_serial_sequence('questions', 'id'),
              GREATEST(COALESCE(max(id), 1), 1), COALESCE(max(id) >= 1, false)) FROM questions;
SELECT setval(pg_get_serial_sequence('answers', 'id'),
              GREATEST(COALESCE(max(id), 1), 1), COALESCE(max(id) >= 1, false)) FROM answers;
