-- 第 5 步 · 修改与回滚：update／delete 区段自带 BEGIN…ROLLBACK，可整段执行，跑完数据不变。
-- 这两个区段在两表阶段和五表阶段都适用（只动 questions 与 answers）。
-- duplicate 区段是五表阶段的预期失败：必须单独 BEGIN，捕获错误后 ROLLBACK，不能整文件盲跑。
-- 运行入口：examples/ex02_update_delete.py（两表）与 examples/ex04_constraints.py（五表）。

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
