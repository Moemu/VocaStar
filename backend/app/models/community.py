"""社区模块模型：学习小组、分类、成员关系"""

from __future__ import annotations

import enum
from datetime import datetime
from typing import Optional

import sqlalchemy
from sqlalchemy import (
    Boolean,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.sql import Base


class CommunityCategory(Base):
    __tablename__ = "community_categories"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    slug: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(100))
    order: Mapped[int] = mapped_column(Integer, default=0, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=sqlalchemy.func.now(), index=True)

    groups: Mapped[list["CommunityGroup"]] = relationship("CommunityGroup", back_populates="category")


class CommunityGroup(Base):
    __tablename__ = "community_groups"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(200), index=True)
    summary: Mapped[str] = mapped_column(String(300))
    cover_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    # 拥有者信息（简化为直接存储名称与头像 URL）
    owner_name: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    owner_avatar_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    # 小组规则（JSON 数组字符串）
    rules_json: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    category_id: Mapped[int] = mapped_column(Integer, ForeignKey("community_categories.id", ondelete="SET NULL"))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, index=True)

    members_count: Mapped[int] = mapped_column(Integer, default=0, index=True)
    likes_count: Mapped[int] = mapped_column(Integer, default=0, index=True, comment="小组点赞数")
    last_activity_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True, index=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=sqlalchemy.func.now(), index=True)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=sqlalchemy.func.now(), onupdate=sqlalchemy.func.now(), index=True
    )

    # relationships
    category: Mapped["CommunityCategory"] = relationship("CommunityCategory", back_populates="groups")
    members: Mapped[list["CommunityGroupMember"]] = relationship(
        "CommunityGroupMember", back_populates="group", cascade="all, delete-orphan"
    )

    __table_args__ = (
        Index("idx_group_category", "category_id"),
        Index("idx_group_active", "is_active"),
        Index("idx_group_last_activity", "last_activity_at"),
    )


class CommunityGroupMember(Base):
    __tablename__ = "community_group_members"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    group_id: Mapped[int] = mapped_column(Integer, ForeignKey("community_groups.id", ondelete="CASCADE"), index=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id", ondelete="CASCADE"), index=True)
    role: Mapped[str] = mapped_column(String(20), default="member", index=True, comment="成员身份 leader/member")
    joined_at: Mapped[datetime] = mapped_column(DateTime, server_default=sqlalchemy.func.now(), index=True)

    group: Mapped["CommunityGroup"] = relationship("CommunityGroup", back_populates="members")

    __table_args__ = (
        UniqueConstraint("group_id", "user_id", name="uniq_group_user"),
        Index("idx_member_user", "user_id"),
        Index("idx_member_group", "group_id"),
    )


class CommunityGroupLike(Base):
    __tablename__ = "community_group_likes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    group_id: Mapped[int] = mapped_column(Integer, ForeignKey("community_groups.id", ondelete="CASCADE"), index=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id", ondelete="CASCADE"), index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=sqlalchemy.func.now(), index=True)

    __table_args__ = (
        UniqueConstraint("group_id", "user_id", name="uniq_group_like"),
        Index("idx_group_like_group", "group_id"),
        Index("idx_group_like_user", "user_id"),
    )


class CommunityPost(Base):
    __tablename__ = "community_posts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    group_id: Mapped[int] = mapped_column(Integer, ForeignKey("community_groups.id", ondelete="CASCADE"), index=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id", ondelete="CASCADE"), index=True)
    title: Mapped[str] = mapped_column(String(200))
    content: Mapped[str] = mapped_column(Text)
    likes_count: Mapped[int] = mapped_column(Integer, default=0, index=True)
    comments_count: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=sqlalchemy.func.now(), index=True)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=sqlalchemy.func.now(), onupdate=sqlalchemy.func.now(), index=True
    )

    __table_args__ = (
        Index("idx_post_group", "group_id"),
        Index("idx_post_user", "user_id"),
        Index("idx_post_created", "created_at"),
        Index("idx_post_likes", "likes_count"),
    )


class AttachmentType(str, enum.Enum):
    image = "image"
    url = "url"
    document = "document"
    video = "video"
    pdf = "pdf"
    code = "code"


class CommunityPostAttachment(Base):
    __tablename__ = "community_post_attachments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    post_id: Mapped[int] = mapped_column(Integer, ForeignKey("community_posts.id", ondelete="CASCADE"), index=True)
    type: Mapped[str] = mapped_column(String(20), index=True)
    url: Mapped[str] = mapped_column(String(1000))
    title: Mapped[Optional[str]] = mapped_column(String(300), nullable=True, comment="附件标题/文件名/URL标题")
    file_size: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    download_count: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=sqlalchemy.func.now(), index=True)

    __table_args__ = (
        Index("idx_attach_post", "post_id"),
        Index("idx_attach_type", "type"),
    )


class CommunityPostLike(Base):
    __tablename__ = "community_post_likes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    post_id: Mapped[int] = mapped_column(Integer, ForeignKey("community_posts.id", ondelete="CASCADE"), index=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id", ondelete="CASCADE"), index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=sqlalchemy.func.now(), index=True)

    __table_args__ = (
        UniqueConstraint("post_id", "user_id", name="uniq_post_like"),
        Index("idx_post_like_post", "post_id"),
        Index("idx_post_like_user", "user_id"),
    )


class CommunityPostComment(Base):
    __tablename__ = "community_post_comments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    post_id: Mapped[int] = mapped_column(Integer, ForeignKey("community_posts.id", ondelete="CASCADE"), index=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id", ondelete="CASCADE"), index=True)
    content: Mapped[str] = mapped_column(String(1000))
    likes_count: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=sqlalchemy.func.now(), index=True)

    __table_args__ = (
        Index("idx_comment_post", "post_id"),
        Index("idx_comment_user", "user_id"),
        Index("idx_comment_created", "created_at"),
    )


class CommunityCommentLike(Base):
    __tablename__ = "community_comment_likes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    comment_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("community_post_comments.id", ondelete="CASCADE"), index=True
    )
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id", ondelete="CASCADE"), index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=sqlalchemy.func.now(), index=True)

    __table_args__ = (
        UniqueConstraint("comment_id", "user_id", name="uniq_comment_like"),
        Index("idx_comment_like_comment", "comment_id"),
        Index("idx_comment_like_user", "user_id"),
    )
