"""职业星球相关模型"""

from datetime import datetime
from typing import TYPE_CHECKING, Optional

import sqlalchemy
from sqlalchemy import JSON, DateTime, Float, ForeignKey, Index, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.sql import Base

if TYPE_CHECKING:
    from app.models.cosplay import CosplayScript
    from app.models.quiz import QuizReport


class Career(Base):
    """职业"""

    __tablename__ = "careers"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True, autoincrement=True, comment="主键ID")
    name: Mapped[str] = mapped_column(String(100), nullable=False, index=True, comment="职业名称")
    code: Mapped[Optional[str]] = mapped_column(String(50), nullable=True, unique=True, comment="职业编码")
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True, comment="职业简介")
    holland_dimensions: Mapped[Optional[list[str]]] = mapped_column(JSON, nullable=True, comment="匹配的霍兰德维度列表")
    work_content: Mapped[Optional[list[str]]] = mapped_column(JSON, nullable=True, comment="主要工作内容列表")
    career_outlook: Mapped[Optional[str]] = mapped_column(Text, nullable=True, comment="职业前景")
    development_path: Mapped[Optional[list[str]]] = mapped_column(JSON, nullable=True, comment="发展路径列表")
    required_skills: Mapped[Optional[str]] = mapped_column(Text, nullable=True, comment="核心技能要求")
    planet_image_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True, comment="星球图片URL")

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        server_default=sqlalchemy.func.now(),
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
    tags: Mapped[list["CareerTag"]] = relationship(
        "CareerTag", secondary="career_tag_relations", back_populates="careers"
    )
    recommendations: Mapped[list["CareerRecommendation"]] = relationship(
        "CareerRecommendation", back_populates="career"
    )
    scripts: Mapped[list["CosplayScript"]] = relationship("CosplayScript", back_populates="career")

    __table_args__ = (
        Index("idx_career_name", "name"),
        Index("idx_career_code", "code"),
    )


class CareerTag(Base):
    """职业标签"""

    __tablename__ = "career_tags"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True, autoincrement=True, comment="主键ID")
    name: Mapped[str] = mapped_column(String(50), nullable=False, unique=True, index=True, comment="标签名称")

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        server_default=sqlalchemy.func.now(),
        comment="创建时间",
    )

    # 关系
    careers: Mapped[list["Career"]] = relationship("Career", secondary="career_tag_relations", back_populates="tags")

    __table_args__ = (Index("idx_careertag_name", "name"),)


class CareerTagRelation(Base):
    """职业-标签关联表"""

    __tablename__ = "career_tag_relations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True, autoincrement=True, comment="主键ID")
    career_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("careers.id", ondelete="CASCADE"), nullable=False, index=True, comment="职业ID"
    )
    tag_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("career_tags.id", ondelete="CASCADE"), nullable=False, index=True, comment="标签ID"
    )

    __table_args__ = (
        Index("idx_career_tag_career_id", "career_id"),
        Index("idx_career_tag_tag_id", "tag_id"),
    )


class CareerRecommendation(Base):
    """职业推荐"""

    __tablename__ = "career_recommendations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True, autoincrement=True, comment="主键ID")
    report_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("quiz_reports.id", ondelete="CASCADE"), nullable=False, index=True, comment="报告ID"
    )
    career_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("careers.id", ondelete="CASCADE"), nullable=False, index=True, comment="职业ID"
    )
    score: Mapped[float] = mapped_column(Float, nullable=False, comment="推荐度分数")
    match_reason: Mapped[Optional[str]] = mapped_column(Text, nullable=True, comment="匹配理由")

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        server_default=sqlalchemy.func.now(),
        comment="创建时间",
    )

    # 关系
    report: Mapped["QuizReport"] = relationship("QuizReport", back_populates="career_recommendations")
    career: Mapped["Career"] = relationship("Career", back_populates="recommendations")

    __table_args__ = (
        Index("idx_recommendation_report_id", "report_id"),
        Index("idx_recommendation_career_id", "career_id"),
        Index("idx_recommendation_score", "score"),
    )
