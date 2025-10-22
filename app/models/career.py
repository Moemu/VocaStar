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


class CareerGalaxy(Base):
    """职业探索星系，用于将职业星球按主题和类目进行分组"""

    __tablename__ = "career_galaxies"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True, autoincrement=True, comment="主键ID")
    name: Mapped[str] = mapped_column(String(100), nullable=False, comment="星系名称")
    category: Mapped[str] = mapped_column(String(100), nullable=False, comment="对应的职业分类显示名称")
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True, comment="星系简介")
    cover_image_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True, comment="星系封面图 URL")

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
    careers: Mapped[list["Career"]] = relationship("Career", back_populates="galaxy")


class Career(Base):
    """职业"""

    __tablename__ = "careers"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True, autoincrement=True, comment="主键ID")
    name: Mapped[str] = mapped_column(String(100), nullable=False, index=True, comment="职业名称")
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True, comment="职业简介")
    cover: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, comment="职业描述图")
    planet_image_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True, comment="星球图片URL")

    holland_dimensions: Mapped[Optional[list[str]]] = mapped_column(JSON, nullable=True, comment="匹配的霍兰德维度列表")
    work_contents: Mapped[Optional[list[str]]] = mapped_column(JSON, nullable=True, comment="主要工作内容列表")
    career_outlook: Mapped[Optional[str]] = mapped_column(Text, nullable=True, comment="职业前景")
    development_path: Mapped[Optional[list[str]]] = mapped_column(JSON, nullable=True, comment="发展路径列表")
    required_skills: Mapped[Optional[str]] = mapped_column(Text, nullable=True, comment="核心技能要求")
    related_courses: Mapped[Optional[list[str]]] = mapped_column(JSON, nullable=True, comment="相关课程列表")
    core_competency_model: Mapped[Optional[dict[str, float]]] = mapped_column(
        JSON,
        nullable=True,
        comment="核心胜任力模型分布(JSON)",
    )
    knowledge_background: Mapped[Optional[dict[str, str]]] = mapped_column(
        JSON,
        nullable=True,
        comment="知识背景要求(JSON)",
    )
    galaxy_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        ForeignKey("career_galaxies.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
        comment="所属探索星系ID",
    )
    salary_min: Mapped[Optional[int]] = mapped_column(Integer, nullable=True, comment="建议薪资范围最小值")
    salary_max: Mapped[Optional[int]] = mapped_column(Integer, nullable=True, comment="建议薪资范围最大值")
    skills_snapshot: Mapped[Optional[list[str]]] = mapped_column(JSON, nullable=True, comment="技能亮点简表(JSON 列表)")

    cosplay_script_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        ForeignKey("cosplay_scripts.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
        comment="关联的Cosplay剧本ID",
    )

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
    recommendations: Mapped[list["CareerRecommendation"]] = relationship(
        "CareerRecommendation", back_populates="career"
    )
    # NOTE: The relationship name was changed from 'scripts' to 'cosplay_script' for clarity.
    # This is a breaking change from the previous schema. Please update any code referencing the old relationship name.
    cosplay_script: Mapped[Optional["CosplayScript"]] = relationship(
        "CosplayScript",
        primaryjoin="Career.cosplay_script_id==CosplayScript.id",
        foreign_keys=[cosplay_script_id],
        uselist=False,
    )
    galaxy: Mapped[Optional[CareerGalaxy]] = relationship("CareerGalaxy", back_populates="careers")

    __table_args__ = (
        Index("idx_career_name", "name"),
        Index("idx_career_salary_range", "salary_min", "salary_max"),
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
