"""用户中心扩展功能模型"""

import enum
from datetime import datetime
from typing import TYPE_CHECKING, Optional

import sqlalchemy
from sqlalchemy import (
    Boolean,
    DateTime,
    Enum,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.sql import Base

if TYPE_CHECKING:
    from app.models.quiz import QuizReport
    from app.models.user import User


class MessageType(str, enum.Enum):
    """消息类型"""

    system = "system"  # 系统通知
    activity = "activity"  # 活动提醒
    achievement = "achievement"  # 成就通知


class FeedbackStatus(str, enum.Enum):
    """反馈状态"""

    pending = "pending"  # 待处理
    processing = "processing"  # 处理中
    resolved = "resolved"  # 已解决
    rejected = "rejected"  # 已拒绝


class FeedbackType(str, enum.Enum):
    """反馈类型"""

    bug = "bug"  # 错误报告
    feature = "feature"  # 功能建议
    general = "general"  # 一般反馈


class ReportBookmark(Base):
    """报告收藏/标记"""

    __tablename__ = "report_bookmarks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True, autoincrement=True, comment="主键ID")
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True, comment="用户ID"
    )
    report_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("quiz_reports.id", ondelete="CASCADE"), nullable=False, index=True, comment="报告ID"
    )
    is_favorite: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True, comment="是否收藏")
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True, comment="用户备注")

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
    user: Mapped["User"] = relationship("User", back_populates="report_bookmarks")
    report: Mapped["QuizReport"] = relationship("QuizReport", back_populates="bookmarks")

    __table_args__ = (
        Index("idx_bookmark_user_id", "user_id"),
        Index("idx_bookmark_report_id", "report_id"),
        Index("idx_bookmark_created_at", "created_at"),
    )


class Notification(Base):
    """消息/通知"""

    __tablename__ = "notifications"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True, autoincrement=True, comment="主键ID")
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True, comment="用户ID"
    )
    message_type: Mapped[MessageType] = mapped_column(Enum(MessageType), nullable=False, comment="消息类型")
    title: Mapped[str] = mapped_column(String(200), nullable=False, comment="消息标题")
    content: Mapped[str] = mapped_column(Text, nullable=False, comment="消息内容")
    is_read: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False, index=True, comment="是否已读")

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        server_default=sqlalchemy.func.now(),
        index=True,
        comment="创建时间",
    )
    read_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True, comment="阅读时间")

    # 关系
    user: Mapped["User"] = relationship("User", back_populates="notifications")

    __table_args__ = (
        Index("idx_notification_user_id", "user_id"),
        Index("idx_notification_is_read", "is_read"),
        Index("idx_notification_created_at", "created_at"),
    )


class UserPoints(Base):
    """用户积分"""

    __tablename__ = "user_points"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True, autoincrement=True, comment="主键ID")
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, unique=True, index=True, comment="用户ID"
    )
    points: Mapped[int] = mapped_column(Integer, nullable=False, default=0, comment="积分值")

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
    user: Mapped["User"] = relationship("User", back_populates="user_points")
    transactions: Mapped[list["PointTransaction"]] = relationship("PointTransaction", back_populates="user_points")

    __table_args__ = (Index("idx_userpoints_user_id", "user_id"),)


class PointTransaction(Base):
    """积分交易记录"""

    __tablename__ = "point_transactions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True, autoincrement=True, comment="主键ID")
    user_points_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("user_points.id", ondelete="CASCADE"), nullable=False, index=True, comment="用户积分ID"
    )
    amount: Mapped[int] = mapped_column(Integer, nullable=False, comment="积分变动量(正为增加,负为减少)")
    reason: Mapped[str] = mapped_column(String(200), nullable=False, comment="变动原因")

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        server_default=sqlalchemy.func.now(),
        index=True,
        comment="创建时间",
    )

    # 关系
    user_points: Mapped["UserPoints"] = relationship("UserPoints", back_populates="transactions")

    __table_args__ = (
        Index("idx_transaction_userpoints_id", "user_points_id"),
        Index("idx_transaction_created_at", "created_at"),
    )


class UserAchievement(Base):
    """用户成就"""

    __tablename__ = "user_achievements"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True, autoincrement=True, comment="主键ID")
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True, comment="用户ID"
    )
    achievement_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("achievements.id", ondelete="CASCADE"), nullable=False, index=True, comment="成就ID"
    )

    achieved_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        server_default=sqlalchemy.func.now(),
        index=True,
        comment="获得时间",
    )

    # 关系
    user: Mapped["User"] = relationship("User", backref="achievements")
    achievement: Mapped["Achievement"] = relationship("Achievement", back_populates="user_achievements")

    __table_args__ = (
        Index("idx_userachievement_user_id", "user_id"),
        Index("idx_userachievement_achievement_id", "achievement_id"),
        Index("idx_userachievement_achieved_at", "achieved_at"),
    )


class Achievement(Base):
    """成就定义"""

    __tablename__ = "achievements"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True, autoincrement=True, comment="主键ID")
    code: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, comment="成就代码，用于逻辑匹配")
    name: Mapped[str] = mapped_column(String(100), nullable=False, comment="成就名称")
    description: Mapped[str] = mapped_column(Text, nullable=False, comment="成就描述")
    badge_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True, comment="徽章图片URL")
    points: Mapped[int] = mapped_column(Integer, nullable=False, default=0, comment="成就积分")
    condition_type: Mapped[Optional[str]] = mapped_column(String(50), nullable=True, comment="条件类型(简化版本)")
    threshold: Mapped[Optional[int]] = mapped_column(Integer, nullable=True, comment="达成阈值")

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        server_default=sqlalchemy.func.now(),
        comment="创建时间",
    )

    # 关系
    user_achievements: Mapped[list["UserAchievement"]] = relationship("UserAchievement", back_populates="achievement")


class Feedback(Base):
    """反馈/建议"""

    __tablename__ = "feedbacks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True, autoincrement=True, comment="主键ID")
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True, comment="用户ID"
    )
    type: Mapped[FeedbackType] = mapped_column(Enum(FeedbackType), nullable=False, comment="反馈类型")
    content: Mapped[str] = mapped_column(Text, nullable=False, comment="反馈内容")
    status: Mapped[FeedbackStatus] = mapped_column(
        Enum(FeedbackStatus), nullable=False, default=FeedbackStatus.pending, index=True, comment="处理状态"
    )
    admin_reply: Mapped[Optional[str]] = mapped_column(Text, nullable=True, comment="管理员回复")

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
    user: Mapped["User"] = relationship("User", back_populates="feedbacks")

    __table_args__ = (
        Index("idx_feedback_user_id", "user_id"),
        Index("idx_feedback_status", "status"),
        Index("idx_feedback_created_at", "created_at"),
    )


# =========================
#  User Center New Features
# =========================


class FavoriteItemType(str, enum.Enum):
    career = "career"


class Favorite(Base):
    """通用收藏表（目前仅支持收藏职业星球）。"""

    __tablename__ = "favorites"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id", ondelete="CASCADE"), index=True)
    item_type: Mapped[FavoriteItemType] = mapped_column(Enum(FavoriteItemType), nullable=False, index=True)
    item_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=sqlalchemy.func.now(), index=True
    )

    user: Mapped["User"] = relationship("User", backref="favorites")

    __table_args__ = (Index("idx_favorite_user_item", "user_id", "item_type", "item_id", unique=True),)


class ExplorationProgress(Base):
    """职业星球探索进度（按 4 个核心区块计）。"""

    __tablename__ = "exploration_progress"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id", ondelete="CASCADE"), index=True)
    career_id: Mapped[int] = mapped_column(Integer, index=True)
    explored_blocks: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    updated_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=sqlalchemy.func.now(), onupdate=sqlalchemy.func.now(), index=True
    )

    user: Mapped["User"] = relationship("User", backref="exploration_progress")

    __table_args__ = (Index("idx_explore_user_career", "user_id", "career_id", unique=True),)


class CosplayWrongbook(Base):
    """Cosplay 错题本记录。

    当用户在某个剧本的某个场景中选择了错误选项时，记录一条错题，
    用于在个人中心展示正确选项与解析。
    """

    __tablename__ = "cosplay_wrongbook"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id", ondelete="CASCADE"), index=True)
    script_id: Mapped[int] = mapped_column(Integer, ForeignKey("cosplay_scripts.id", ondelete="CASCADE"), index=True)
    scene_id: Mapped[str] = mapped_column(String(100), index=True)
    script_title: Mapped[str] = mapped_column(String(200), comment="剧本标题")
    scene_title: Mapped[str] = mapped_column(String(200), comment="场景标题")
    selected_option_text: Mapped[str] = mapped_column(String(500), comment="用户选择的错误选项文本")
    correct_option_text: Mapped[str] = mapped_column(String(500), comment="正确选项文本")
    analysis: Mapped[Optional[str]] = mapped_column(Text, nullable=True, comment="解析/说明")

    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=sqlalchemy.func.now(), index=True
    )

    user: Mapped["User"] = relationship("User", backref="cosplay_wrongbooks")

    __table_args__ = (
        Index("idx_wrongbook_user_script_scene", "user_id", "script_id", "scene_id", unique=True),
        Index("idx_wrongbook_created_at", "created_at"),
    )
