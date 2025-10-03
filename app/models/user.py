import enum
from datetime import datetime
from typing import TYPE_CHECKING, Optional

import sqlalchemy
from sqlalchemy import Boolean, DateTime, Enum, Index, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.sql import Base

if TYPE_CHECKING:
    from app.models.cosplay import CosplaySession
    from app.models.extensions import Feedback, Notification, ReportBookmark, UserPoints
    from app.models.quiz import QuizSubmission


class UserRole(str, enum.Enum):
    user = "user"
    admin = "admin"


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True, autoincrement=True, comment="主键ID")
    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True, comment="用户名")
    email: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True, comment="邮箱")
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False, comment="密码哈希")
    nickname: Mapped[Optional[str]] = mapped_column(String(50), nullable=True, comment="昵称")
    avatar_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True, comment="头像URL")

    role: Mapped[UserRole] = mapped_column(Enum(UserRole), nullable=False, comment="角色", default=UserRole.user)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True, comment="账户状态")
    last_login_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True, comment="最后登录时间")

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
    quiz_submissions: Mapped[list["QuizSubmission"]] = relationship("QuizSubmission", back_populates="user")
    cosplay_sessions: Mapped[list["CosplaySession"]] = relationship("CosplaySession", back_populates="user")
    report_bookmarks: Mapped[list["ReportBookmark"]] = relationship("ReportBookmark", back_populates="user")
    notifications: Mapped[list["Notification"]] = relationship("Notification", back_populates="user")
    user_points: Mapped[Optional["UserPoints"]] = relationship("UserPoints", back_populates="user", uselist=False)
    feedbacks: Mapped[list["Feedback"]] = relationship("Feedback", back_populates="user")

    __table_args__ = (
        Index("idx_user_email", "email"),
        Index("idx_user_username", "username"),
        Index("idx_user_created_at", "created_at"),
    )
