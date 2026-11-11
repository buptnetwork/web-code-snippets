-- 第 3 步 · 五表固定数据：在 02-five-tables.sql 成功执行后运行。
-- 两位用户、两条问题、三条回答、两个标签；回答 202 的作者未知（NULL）。
-- 末尾校准序列：显式插入 id 不会推进序列，校准后下一条新增才拿到 103、204 等。
-- 所有记录均为教学虚构；不要与迁移副本或其他练习数据混用。

-- #region users
INSERT INTO users (id, display_name) VALUES
    (1, '示例用户甲'), (2, '示例用户乙');
-- #endregion users

-- #region questions
INSERT INTO questions (id, title, body, author_id, created_at) VALUES
    (101, 'Python 如何读取问题列表？',
     '希望理解列表查询如何从数据库取出问题。', 1,
     '2026-09-01T08:00:00Z'),
    (102, 'SQL 查询从哪里开始？',
     '希望先弄清表和记录再逐步学习查询语句。', 2,
     '2026-09-01T08:00:00Z');
-- #endregion questions

-- #region answers
INSERT INTO answers (id, question_id, author_id, body, created_at) VALUES
    (201, 101, 2, '可以先用 SELECT 读取问题表中的记录。',
     '2026-09-01T09:00:00Z'),
    (202, 101, NULL, '再通过 WHERE 保留满足条件的问题记录。',
     '2026-09-01T09:10:00Z'),
    (203, 101, 2, '最后使用 ORDER BY 明确结果的显示顺序。',
     '2026-09-01T09:20:00Z');
-- #endregion answers

-- #region tags
INSERT INTO tags (id, name) VALUES (1, 'python'), (2, 'sql');
INSERT INTO question_tags (question_id, tag_id, position) VALUES
    (101, 1, 1), (101, 2, 2), (102, 1, 1);
-- #endregion tags

-- #region sequences
SELECT setval(pg_get_serial_sequence('users', 'id'),
              GREATEST(COALESCE(max(id), 1), 1), COALESCE(max(id) >= 1, false)) FROM users;
SELECT setval(pg_get_serial_sequence('questions', 'id'),
              GREATEST(COALESCE(max(id), 1), 1), COALESCE(max(id) >= 1, false)) FROM questions;
SELECT setval(pg_get_serial_sequence('answers', 'id'),
              GREATEST(COALESCE(max(id), 1), 1), COALESCE(max(id) >= 1, false)) FROM answers;
SELECT setval(pg_get_serial_sequence('tags', 'id'),
              GREATEST(COALESCE(max(id), 1), 1), COALESCE(max(id) >= 1, false)) FROM tags;
-- #endregion sequences
