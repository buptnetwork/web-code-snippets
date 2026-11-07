-- 五表阶段：独立的空 schema，不能叠加执行在两表阶段上。
-- 教学基线：PostgreSQL 16+、UTF-8、UTC；本文件不迁移 M1 数据。

-- #region users
CREATE TABLE users (
    id BIGSERIAL PRIMARY KEY,
    display_name TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    CONSTRAINT users_name_len
        CHECK (char_length(display_name) BETWEEN 2 AND 40)
);
-- #endregion users

-- #region questions
CREATE TABLE questions (
    id BIGSERIAL PRIMARY KEY,
    title TEXT COLLATE "C" NOT NULL,
    body TEXT NOT NULL,
    author_id BIGINT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    CONSTRAINT questions_author_id_fkey
        FOREIGN KEY (author_id) REFERENCES users(id),
    CONSTRAINT questions_title_key UNIQUE (title),
    CONSTRAINT questions_title_len
        CHECK (char_length(title) BETWEEN 5 AND 200),
    CONSTRAINT questions_body_len
        CHECK (char_length(body) BETWEEN 10 AND 20000)
);
-- #endregion questions

-- #region answers
CREATE TABLE answers (
    id BIGSERIAL PRIMARY KEY,
    question_id BIGINT NOT NULL,
    author_id BIGINT,
    body TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    CONSTRAINT answers_question_id_fkey
        FOREIGN KEY (question_id) REFERENCES questions(id),
    CONSTRAINT answers_author_id_fkey
        FOREIGN KEY (author_id) REFERENCES users(id),
    CONSTRAINT answers_body_len
        CHECK (char_length(body) BETWEEN 10 AND 10000)
);
-- #endregion answers

-- #region tags
CREATE TABLE tags (
    id BIGSERIAL PRIMARY KEY,
    name TEXT COLLATE "C" NOT NULL,
    CONSTRAINT tags_name_key UNIQUE (name)
);
-- #endregion tags

-- #region associations
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
-- #endregion associations
