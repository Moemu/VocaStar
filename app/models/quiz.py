"""测评系统相关模型"""

import enum
from datetime import datetime
from typing import TYPE_CHECKING, Optional

import sqlalchemy
from sqlalchemy import (
    JSON,
    Boolean,
    DateTime,
    Enum,
    Float,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.sql import Base

if TYPE_CHECKING:
    from app.models.career import CareerRecommendation
    from app.models.extensions import ReportBookmark
    from app.models.user import User


class QuestionType(str, enum.Enum):
    """题目类型"""

    single_choice = "single_choice"  # 单选
    multiple_choice = "multiple_choice"  # 多选
    rating = "rating"  # 打分


class Quiz(Base):
    """测评题库"""

    __tablename__ = "quizzes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True, autoincrement=True, comment="主键ID")
    title: Mapped[str] = mapped_column(String(200), nullable=False, comment="测评标题")
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True, comment="测评描述")
    is_published: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False, comment="是否发布")

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        server_default=sqlalchemy.func.now(),
        index=True,
        comment="创建时间",
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        server_default=sqlalchemy.func.now(),
        onupdate=sqlalchemy.func.now(),
        comment="更新时间",
    )

    # 关系
    questions: Mapped[list["Question"]] = relationship("Question", back_populates="quiz", cascade="all, delete-orphan")
    submissions: Mapped[list["QuizSubmission"]] = relationship("QuizSubmission", back_populates="quiz")

    __table_args__ = (
        Index("idx_quiz_created_at", "created_at"),
        Index("idx_quiz_published", "is_published"),
    )


class Question(Base):
    """题目"""

    __tablename__ = "questions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True, autoincrement=True, comment="主键ID")
    quiz_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("quizzes.id", ondelete="CASCADE"), nullable=False, index=True, comment="测评ID"
    )
    content: Mapped[str] = mapped_column(Text, nullable=False, comment="题目内容")
    question_type: Mapped[QuestionType] = mapped_column(Enum(QuestionType), nullable=False, comment="题目类型")
    order: Mapped[int] = mapped_column(Integer, nullable=False, default=0, comment="题目顺序")
    is_required: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True, comment="是否必答")

    # 关系
    quiz: Mapped["Quiz"] = relationship("Quiz", back_populates="questions")
    options: Mapped[list["Option"]] = relationship("Option", back_populates="question", cascade="all, delete-orphan")
    answers: Mapped[list["QuizAnswer"]] = relationship("QuizAnswer", back_populates="question")

    __table_args__ = (
        Index("idx_question_quiz_id", "quiz_id"),
        Index("idx_question_order", "quiz_id", "order"),
    )


class Option(Base):
    """选项"""

    __tablename__ = "options"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True, autoincrement=True, comment="主键ID")
    question_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("questions.id", ondelete="CASCADE"), nullable=False, index=True, comment="题目ID"
    )
    content: Mapped[str] = mapped_column(String(500), nullable=False, comment="选项内容")
    weight: Mapped[float] = mapped_column(Float, nullable=False, default=0.0, comment="权重(用于计算结果)")
    order: Mapped[int] = mapped_column(Integer, nullable=False, default=0, comment="选项顺序")

    # 关系
    question: Mapped["Question"] = relationship("Question", back_populates="options")
    answers: Mapped[list["QuizAnswer"]] = relationship("QuizAnswer", back_populates="option")

    __table_args__ = (
        Index("idx_option_question_id", "question_id"),
        Index("idx_option_order", "question_id", "order"),
    )


class QuizSubmission(Base):
    """用户答题记录"""

    __tablename__ = "quiz_submissions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True, autoincrement=True, comment="主键ID")
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True, comment="用户ID"
    )
    quiz_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("quizzes.id", ondelete="CASCADE"), nullable=False, index=True, comment="测评ID"
    )

    submitted_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        server_default=sqlalchemy.func.now(),
        index=True,
        comment="提交时间",
    )

    # 关系
    user: Mapped["User"] = relationship("User", back_populates="quiz_submissions")
    quiz: Mapped["Quiz"] = relationship("Quiz", back_populates="submissions")
    answers: Mapped[list["QuizAnswer"]] = relationship(
        "QuizAnswer", back_populates="submission", cascade="all, delete-orphan"
    )
    report: Mapped[Optional["QuizReport"]] = relationship("QuizReport", back_populates="submission", uselist=False)

    __table_args__ = (
        Index("idx_submission_user_id", "user_id"),
        Index("idx_submission_quiz_id", "quiz_id"),
        Index("idx_submission_submitted_at", "submitted_at"),
    )


class QuizAnswer(Base):
    """具体答案"""

    __tablename__ = "quiz_answers"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True, autoincrement=True, comment="主键ID")
    submission_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("quiz_submissions.id", ondelete="CASCADE"), nullable=False, index=True, comment="提交记录ID"
    )
    question_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("questions.id", ondelete="CASCADE"), nullable=False, index=True, comment="题目ID"
    )
    option_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("options.id", ondelete="SET NULL"), nullable=True, index=True, comment="选项ID(单选)"
    )
    option_ids: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True, comment="选项IDs(多选,JSON数组)")
    rating_value: Mapped[Optional[float]] = mapped_column(Float, nullable=True, comment="打分值")

    # 关系
    submission: Mapped["QuizSubmission"] = relationship("QuizSubmission", back_populates="answers")
    question: Mapped["Question"] = relationship("Question", back_populates="answers")
    option: Mapped[Optional["Option"]] = relationship("Option", back_populates="answers")

    __table_args__ = (
        Index("idx_answer_submission_id", "submission_id"),
        Index("idx_answer_question_id", "question_id"),
    )


class QuizReport(Base):
    """测评报告"""

    __tablename__ = "quiz_reports"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True, autoincrement=True, comment="主键ID")
    submission_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("quiz_submissions.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True,
        comment="提交记录ID",
    )
    result_json: Mapped[dict] = mapped_column(JSON, nullable=False, comment="报告内容(JSON格式)")

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        server_default=sqlalchemy.func.now(),
        index=True,
        comment="创建时间",
    )

    # 关系
    submission: Mapped["QuizSubmission"] = relationship("QuizSubmission", back_populates="report")
    career_recommendations: Mapped[list["CareerRecommendation"]] = relationship(
        "CareerRecommendation", back_populates="report"
    )
    bookmarks: Mapped[list["ReportBookmark"]] = relationship("ReportBookmark", back_populates="report")

    __table_args__ = (
        Index("idx_report_submission_id", "submission_id"),
        Index("idx_report_created_at", "created_at"),
    )
