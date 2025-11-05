from __future__ import annotations

from datetime import datetime
from typing import Optional

import sqlalchemy
from sqlalchemy import (
    Boolean,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    String,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.sql import Base


class MentorDomain(Base):
    """导师领域（如 前端开发/后端开发/数据分析 等）。"""

    __tablename__ = "mentor_domains"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    slug: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(100))
    order: Mapped[int] = mapped_column(Integer, default=0, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=sqlalchemy.func.now(), index=True)

    __table_args__ = (Index("idx_mentor_domain_order", "order"),)


class CommunityMentor(Base):
    """职业导师。"""

    __tablename__ = "community_mentors"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), index=True)
    avatar_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    profession: Mapped[str] = mapped_column(String(100), index=True, comment="所属/擅长职业")
    company: Mapped[Optional[str]] = mapped_column(String(200), nullable=True, comment="在职公司")
    fee_per_hour: Mapped[int] = mapped_column(Integer, default=0, comment="咨询费用（每小时，单位分或元，视前端约定）")
    rating: Mapped[float] = mapped_column(Numeric(3, 2), default=0, comment="星级评分，0-5")
    rating_count: Mapped[int] = mapped_column(Integer, default=0, comment="评分数量")
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, index=True)
    popularity: Mapped[int] = mapped_column(Integer, default=0, index=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=sqlalchemy.func.now(), index=True)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=sqlalchemy.func.now(), onupdate=sqlalchemy.func.now(), index=True
    )

    skills: Mapped[list["CommunityMentorSkill"]] = relationship(
        "CommunityMentorSkill", back_populates="mentor", cascade="all, delete-orphan"
    )
    domains: Mapped[list["MentorDomainMap"]] = relationship(
        "MentorDomainMap", back_populates="mentor", cascade="all, delete-orphan"
    )
    requests: Mapped[list["MentorRequest"]] = relationship(
        "MentorRequest", back_populates="mentor", cascade="all, delete-orphan"
    )

    __table_args__ = (
        Index("idx_mentor_profession", "profession"),
        Index("idx_mentor_popularity", "popularity"),
    )


class CommunityMentorSkill(Base):
    """导师技能标签。"""

    __tablename__ = "community_mentor_skills"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    mentor_id: Mapped[int] = mapped_column(Integer, ForeignKey("community_mentors.id", ondelete="CASCADE"), index=True)
    skill: Mapped[str] = mapped_column(String(50), index=True)

    mentor: Mapped["CommunityMentor"] = relationship("CommunityMentor", back_populates="skills")

    __table_args__ = (
        UniqueConstraint("mentor_id", "skill", name="uniq_mentor_skill"),
        Index("idx_mentor_skill", "skill"),
        Index("idx_mentor_skill_mentor", "mentor_id"),
    )


class MentorDomainMap(Base):
    """导师-领域多对多映射。"""

    __tablename__ = "mentor_domain_maps"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    mentor_id: Mapped[int] = mapped_column(Integer, ForeignKey("community_mentors.id", ondelete="CASCADE"), index=True)
    domain_id: Mapped[int] = mapped_column(Integer, ForeignKey("mentor_domains.id", ondelete="CASCADE"), index=True)

    mentor: Mapped["CommunityMentor"] = relationship("CommunityMentor", back_populates="domains")
    domain: Mapped["MentorDomain"] = relationship("MentorDomain")

    __table_args__ = (
        UniqueConstraint("mentor_id", "domain_id", name="uniq_mentor_domain"),
        Index("idx_mdm_mentor", "mentor_id"),
        Index("idx_mdm_domain", "domain_id"),
    )


class MentorRequest(Base):
    """导师咨询/提问申请。"""

    __tablename__ = "mentor_requests"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    mentor_id: Mapped[int] = mapped_column(Integer, ForeignKey("community_mentors.id", ondelete="CASCADE"), index=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id", ondelete="CASCADE"), index=True)
    type: Mapped[str] = mapped_column(String(20), index=True, comment="question|consult")
    # message: Mapped[str] = mapped_column(Text, comment="问题/需求描述")
    # preferred_time: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, comment="期望沟通时间（自由文本/ISO）")
    # duration_min: Mapped[Optional[int]] = mapped_column(Integer, nullable=True, comment="咨询时长（分钟）")
    status: Mapped[str] = mapped_column(
        String(20), default="pending", index=True, comment="pending/accepted/rejected/cancelled"
    )
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=sqlalchemy.func.now(), index=True)

    mentor: Mapped["CommunityMentor"] = relationship("CommunityMentor", back_populates="requests")

    __table_args__ = (
        Index("idx_mr_user", "user_id"),
        Index("idx_mr_mentor", "mentor_id"),
        Index("idx_mr_status", "status"),
    )
