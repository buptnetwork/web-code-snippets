-- PostgreSQL / SQLite 共用结构；固定主键与 50 行虚构数据由 seed.py 写入。
-- 不使用数据库专属的自增语法；本课没有写业务数据的端点。
CREATE TABLE IF NOT EXISTS questions (
    id INTEGER PRIMARY KEY,
    title TEXT NOT NULL,
    body TEXT NOT NULL,
    created_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS answers (
    id INTEGER PRIMARY KEY,
    question_id INTEGER NOT NULL REFERENCES questions(id),
    body TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS tags (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL
);
