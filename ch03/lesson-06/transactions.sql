-- 教师逐段执行；只针对已提交初始化的隔离教学库。
-- UPDATE/DELETE 示例均主动回滚，保持后续讲解的固定数据。

-- #region update
BEGIN;
UPDATE questions
SET body = '更新后的说明仍然围绕表和记录展开。'
WHERE id = 102;
SELECT id, body FROM questions WHERE id = 102;
ROLLBACK;
-- #endregion update

-- #region delete
BEGIN;
DELETE FROM answers WHERE id = 203;
SELECT id FROM answers
WHERE question_id = 101
ORDER BY id;
ROLLBACK;
-- #endregion delete

-- 下面是五表阶段的预期失败。单独 BEGIN 后执行；报错后务必 ROLLBACK。
-- 不要把该预期失败接到遇错即退出、却不能清理事务的脚本里。
-- #region duplicate
INSERT INTO question_tags (question_id, tag_id, position)
VALUES (101, 1, 3);
-- #endregion duplicate
