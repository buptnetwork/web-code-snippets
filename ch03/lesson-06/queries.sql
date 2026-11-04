-- 下列查询使用完整五表种子，不改变数据。

-- #region unknown-author
SELECT id, question_id
FROM answers
WHERE author_id IS NULL;
-- #endregion unknown-author

-- #region q1
SELECT id, title
FROM questions
WHERE author_id = 1
ORDER BY id;
-- #endregion q1

-- #region q2
SELECT q.id AS question_id, q.title, a.id AS answer_id
FROM questions AS q
JOIN answers AS a ON a.question_id = q.id
ORDER BY q.id, a.id;
-- #endregion q2

-- #region tag-read
SELECT t.name
FROM question_tags AS qt
JOIN tags AS t ON t.id = qt.tag_id
WHERE qt.question_id = 101
ORDER BY qt.position;
-- #endregion tag-read

-- #region left-rows
SELECT q.id AS question_id, a.id AS answer_id, a.author_id
FROM questions AS q
LEFT JOIN answers AS a ON a.question_id = q.id
ORDER BY q.id, a.id;
-- #endregion left-rows

-- #region q3
SELECT q.id, q.title, count(a.id) AS answer_count
FROM questions AS q
LEFT JOIN answers AS a ON a.question_id = q.id
GROUP BY q.id, q.title
ORDER BY q.id;
-- #endregion q3

-- #region count-compare
SELECT q.id, count(*) AS joined_rows,
       count(a.id) AS answers, count(a.author_id) AS known_authors
FROM questions AS q
LEFT JOIN answers AS a ON a.question_id = q.id
GROUP BY q.id
ORDER BY q.id;
-- #endregion count-compare

-- #region q4
SELECT id, title
FROM questions
ORDER BY id DESC
LIMIT 1 OFFSET 0;
-- #endregion q4

-- #region total
SELECT count(*) AS total FROM questions;
-- #endregion total

-- #region filtered-total
SELECT count(*) AS total FROM questions WHERE author_id = 1;
-- #endregion filtered-total

-- #region time-order
SELECT id, title, created_at
FROM questions
ORDER BY created_at DESC, id DESC;
-- #endregion time-order
