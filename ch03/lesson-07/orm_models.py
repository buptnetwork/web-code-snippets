"""第 7 课完整五表映射；与第 6 课 schema.sql、001_baseline 迁移三方一致。

ORM 模型单独成模块，不与第 5 课的 Pydantic 输入输出模型（schemas）同名。
"""

from datetime import datetime

from sqlalchemy import BigInteger, CheckConstraint, DateTime, ForeignKey, SmallInteger, Text, UniqueConstraint, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


# region base-user
class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    display_name: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    __table_args__ = (CheckConstraint("char_length(display_name) BETWEEN 2 AND 40", name="users_name_len"),)
# endregion base-user


# region question
class Question(Base):
    __tablename__ = "questions"
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    title: Mapped[str] = mapped_column(Text(collation="C"))
    body: Mapped[str] = mapped_column(Text)
    author_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.id", name="questions_author_id_fkey"))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    answers: Mapped[list["Answer"]] = relationship(
        back_populates="question", order_by="Answer.id", passive_deletes="all",
    )
    tag_links: Mapped[list["QuestionTag"]] = relationship(
        back_populates="question", order_by="QuestionTag.position", passive_deletes="all",
    )
    __table_args__ = (
        UniqueConstraint("title", name="questions_title_key"),
        CheckConstraint("char_length(title) BETWEEN 5 AND 200", name="questions_title_len"),
        CheckConstraint("char_length(body) BETWEEN 10 AND 20000", name="questions_body_len"),
    )
# endregion question


# region answer
class Answer(Base):
    __tablename__ = "answers"
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    question_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("questions.id", name="answers_question_id_fkey"))
    author_id: Mapped[int | None] = mapped_column(BigInteger, ForeignKey("users.id", name="answers_author_id_fkey"))
    body: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    question: Mapped["Question"] = relationship(back_populates="answers")
    __table_args__ = (CheckConstraint("char_length(body) BETWEEN 10 AND 10000", name="answers_body_len"),)
# endregion answer


# region tags
class Tag(Base):
    __tablename__ = "tags"
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    name: Mapped[str] = mapped_column(Text(collation="C"))
    __table_args__ = (UniqueConstraint("name", name="tags_name_key"),)


class QuestionTag(Base):
    __tablename__ = "question_tags"
    question_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("questions.id", name="question_tags_question_id_fkey"), primary_key=True,
    )
    tag_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("tags.id", name="question_tags_tag_id_fkey"), primary_key=True,
    )
    position: Mapped[int] = mapped_column(SmallInteger)
    question: Mapped["Question"] = relationship(back_populates="tag_links")
    tag: Mapped["Tag"] = relationship()
    __table_args__ = (
        UniqueConstraint("question_id", "position", name="question_tags_position_key"),
        CheckConstraint("position BETWEEN 1 AND 5", name="question_tags_position_range"),
    )
# endregion tags
