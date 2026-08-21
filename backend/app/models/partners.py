from __future__ import annotations

from datetime import datetime
from typing import Optional

import sqlalchemy
from sqlalchemy import DateTime, ForeignKey, Index, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.sql import Base


class CommunityPartner(Base):
    """职业伙伴。

    字段：
      - name: 名称（展示名）
      - avatar_url: 头像 URL，可空
      - profession: 职业/岗位，如“前端开发”“数据分析师”
      - learning_progress: 学习进度（0-100），推荐端不展示
      - popularity: 受欢迎程度（用于推荐排序，备用）
      - created_at/updated_at: 时间戳
    """

    __tablename__ = "community_partners"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), index=True)
    avatar_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    profession: Mapped[str] = mapped_column(String(100), index=True)
    learning_progress: Mapped[int] = mapped_column(Integer, default=0)
    popularity: Mapped[int] = mapped_column(Integer, default=0, index=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=sqlalchemy.func.now(), index=True)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=sqlalchemy.func.now(), onupdate=sqlalchemy.func.now(), index=True
    )

    skills: Mapped[list["CommunityPartnerSkill"]] = relationship(
        "CommunityPartnerSkill", back_populates="partner", cascade="all, delete-orphan"
    )

    bindings: Mapped[list["UserPartnerBinding"]] = relationship(
        "UserPartnerBinding", back_populates="partner", cascade="all, delete-orphan"
    )

    __table_args__ = (
        Index("idx_partner_profession", "profession"),
        Index("idx_partner_popularity", "popularity"),
    )


class CommunityPartnerSkill(Base):
    """伙伴技能标签（范式化，便于搜索和热门统计）。"""

    __tablename__ = "community_partner_skills"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    partner_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("community_partners.id", ondelete="CASCADE"), index=True
    )
    skill: Mapped[str] = mapped_column(String(50), index=True, comment="技能小写规范化")

    partner: Mapped["CommunityPartner"] = relationship("CommunityPartner", back_populates="skills")

    __table_args__ = (
        UniqueConstraint("partner_id", "skill", name="uniq_partner_skill"),
        Index("idx_partner_skill", "skill"),
        Index("idx_partner_skill_partner", "partner_id"),
    )


class UserPartnerBinding(Base):
    """用户-伙伴绑定关系（我的伙伴）。"""

    __tablename__ = "user_partner_bindings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id", ondelete="CASCADE"), index=True)
    partner_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("community_partners.id", ondelete="CASCADE"), index=True
    )
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=sqlalchemy.func.now(), index=True)

    partner: Mapped["CommunityPartner"] = relationship("CommunityPartner", back_populates="bindings")

    __table_args__ = (
        UniqueConstraint("user_id", "partner_id", name="uniq_user_partner"),
        Index("idx_bind_user", "user_id"),
        Index("idx_bind_partner", "partner_id"),
    )
