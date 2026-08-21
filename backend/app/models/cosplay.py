"""Cosplay剧本相关模型"""

import enum
from datetime import datetime
from typing import TYPE_CHECKING, Any, Optional

import sqlalchemy
from sqlalchemy import JSON, DateTime, Enum, ForeignKey, Index, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.sql import Base

if TYPE_CHECKING:
    from app.models.career import Career
    from app.models.user import User


class SessionState(str, enum.Enum):
    """会话状态"""

    in_progress = "in_progress"  # 进行中
    completed = "completed"  # 已完成
    abandoned = "abandoned"  # 已放弃


class CosplayScript(Base):
    """Cosplay剧本"""

    __tablename__ = "cosplay_scripts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True, autoincrement=True, comment="主键ID")
    career_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("careers.id", ondelete="CASCADE"), nullable=False, index=True, comment="职业ID"
    )
    title: Mapped[str] = mapped_column(String(200), nullable=False, comment="剧本标题")
    content: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False, comment="剧本内容(JSON格式,包含剧情步骤)")

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
    career: Mapped["Career"] = relationship("Career", foreign_keys=[career_id])
    sessions: Mapped[list["CosplaySession"]] = relationship("CosplaySession", back_populates="script")

    __table_args__ = (Index("idx_script_career_id", "career_id"),)


class CosplaySession(Base):
    """Cosplay会话"""

    __tablename__ = "cosplay_sessions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True, autoincrement=True, comment="主键ID")
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True, comment="用户ID"
    )
    script_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("cosplay_scripts.id", ondelete="CASCADE"), nullable=False, index=True, comment="剧本ID"
    )
    progress: Mapped[int] = mapped_column(Integer, nullable=False, default=0, comment="当前进度(0-100)")
    state: Mapped[SessionState] = mapped_column(
        Enum(SessionState), nullable=False, default=SessionState.in_progress, comment="会话状态"
    )
    state_payload: Mapped[dict[str, Any]] = mapped_column(
        JSON, nullable=False, default=dict, comment="会话状态详情(JSON: 进度、分数、历史)"
    )

    started_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        server_default=sqlalchemy.func.now(),
        index=True,
        comment="开始时间",
    )
    finished_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True, comment="完成时间")

    # 关系
    user: Mapped["User"] = relationship("User", back_populates="cosplay_sessions")
    script: Mapped["CosplayScript"] = relationship("CosplayScript", back_populates="sessions")
    report: Mapped[Optional["CosplayReport"]] = relationship("CosplayReport", back_populates="session", uselist=False)

    __table_args__ = (
        Index("idx_session_user_id", "user_id"),
        Index("idx_session_script_id", "script_id"),
        Index("idx_session_started_at", "started_at"),
        Index("idx_session_state", "state"),
    )


class CosplayReport(Base):
    """Cosplay体验报告"""

    __tablename__ = "cosplay_reports"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True, autoincrement=True, comment="主键ID")
    session_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("cosplay_sessions.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True,
        comment="会话ID",
    )
    result_json: Mapped[dict] = mapped_column(JSON, nullable=False, comment="体验总结(JSON格式)")

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        server_default=sqlalchemy.func.now(),
        index=True,
        comment="创建时间",
    )

    # 关系
    session: Mapped["CosplaySession"] = relationship("CosplaySession", back_populates="report")

    __table_args__ = (
        Index("idx_cosplay_report_session_id", "session_id"),
        Index("idx_cosplay_report_created_at", "created_at"),
    )
