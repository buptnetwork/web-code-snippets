"""固定基线：空库建立第 6 课五表结构，不包含 seed；不 import 会继续变化的业务模型。"""

from alembic import op
import sqlalchemy as sa

revision = "001_baseline"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # region users-questions
    op.create_table(
        "users",
        sa.Column("id", sa.BigInteger(), primary_key=True),
        sa.Column("display_name", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.CheckConstraint("char_length(display_name) BETWEEN 2 AND 40", name="users_name_len"),
    )
    op.create_table(
        "questions",
        sa.Column("id", sa.BigInteger(), primary_key=True),
        sa.Column("title", sa.Text(collation="C"), nullable=False),
        sa.Column("body", sa.Text(), nullable=False),
        sa.Column("author_id", sa.BigInteger(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(["author_id"], ["users.id"], name="questions_author_id_fkey"),
        sa.UniqueConstraint("title", name="questions_title_key"),
        sa.CheckConstraint("char_length(title) BETWEEN 5 AND 200", name="questions_title_len"),
        sa.CheckConstraint("char_length(body) BETWEEN 10 AND 20000", name="questions_body_len"),
    )
    # endregion users-questions
    # region answers-tags
    op.create_table(
        "answers",
        sa.Column("id", sa.BigInteger(), primary_key=True),
        sa.Column("question_id", sa.BigInteger(), nullable=False),
        sa.Column("author_id", sa.BigInteger(), nullable=True),
        sa.Column("body", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(["question_id"], ["questions.id"], name="answers_question_id_fkey"),
        sa.ForeignKeyConstraint(["author_id"], ["users.id"], name="answers_author_id_fkey"),
        sa.CheckConstraint("char_length(body) BETWEEN 10 AND 10000", name="answers_body_len"),
    )
    op.create_table(
        "tags",
        sa.Column("id", sa.BigInteger(), primary_key=True),
        sa.Column("name", sa.Text(collation="C"), nullable=False),
        sa.UniqueConstraint("name", name="tags_name_key"),
    )
    op.create_table(
        "question_tags",
        sa.Column("question_id", sa.BigInteger(), nullable=False),
        sa.Column("tag_id", sa.BigInteger(), nullable=False),
        sa.Column("position", sa.SmallInteger(), nullable=False),
        sa.ForeignKeyConstraint(["question_id"], ["questions.id"], name="question_tags_question_id_fkey"),
        sa.ForeignKeyConstraint(["tag_id"], ["tags.id"], name="question_tags_tag_id_fkey"),
        sa.PrimaryKeyConstraint("question_id", "tag_id", name="question_tags_pkey"),
        sa.UniqueConstraint("question_id", "position", name="question_tags_position_key"),
        sa.CheckConstraint("position BETWEEN 1 AND 5", name="question_tags_position_range"),
    )
    # endregion answers-tags


def downgrade():
    raise NotImplementedError("本教学基线不提供自动回退；回退需在副本另行设计并核对数据损失")
