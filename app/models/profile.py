from datetime import datetime
from typing import TYPE_CHECKING, Optional

import sqlalchemy
from sqlalchemy import DateTime, ForeignKey, Index, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.sql import Base

if TYPE_CHECKING:
    from app.models.user import User


class UserProfile(Base):
    __tablename__ = "user_profiles"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True, autoincrement=True, comment="主键ID")
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, unique=True, index=True, comment="用户ID"
    )

    college: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, comment="学院")
    major: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, comment="专业")
    grade: Mapped[Optional[int]] = mapped_column(Integer, nullable=True, comment="年级")
    bio: Mapped[Optional[str]] = mapped_column(String(500), nullable=True, comment="个人简介")

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
    user: Mapped["User"] = relationship("User", back_populates="profile")

    __table_args__ = (Index("idx_userprofile_user_id", "user_id"),)
