from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class Pagination(BaseModel):
    """通用分页信息。"""

    page: int = Field(1, ge=1, description="当前页码，从 1 开始")
    page_size: int = Field(20, ge=1, le=100, description="每页数量，建议 10-50，最大 100")
    total: int = Field(..., ge=0, description="总记录数")


class CategoryItem(BaseModel):
    """学习小组分类条目。"""

    id: int = Field(..., description="分类 ID")
    name: str = Field(..., description="分类名称")
    slug: str = Field(..., description="分类英文标识，前端用于筛选，如 frontend/product")
    count: int = Field(0, description="该分类下的小组数量")


class CategoryListResponse(BaseModel):
    """分类列表响应。"""

    items: list[CategoryItem] = Field(default_factory=list, description="分类列表")


class GroupCategory(BaseModel):
    """小组归属分类（嵌入在小组条目/详情中）。"""

    id: int = Field(..., description="分类 ID")
    name: str = Field(..., description="分类名称")
    slug: str = Field(..., description="分类标识")


class GroupItem(BaseModel):
    """小组卡片数据（用于列表页）。"""

    id: int = Field(..., description="小组 ID")
    title: str = Field(..., description="小组名称")
    cover_url: Optional[str] = Field(None, description="封面图 URL，可为空")
    summary: str = Field(..., description="小组简介，简要描述")
    category: GroupCategory = Field(..., description="所属分类")
    members_count: int = Field(..., description="成员数量")
    last_activity_at: Optional[datetime] = Field(None, description="最近活跃时间，可能为空")
    joined: bool = Field(False, description="当前登录用户是否已加入该小组；未登录恒为 false")


class GroupListResponse(BaseModel):
    """小组列表响应。"""

    items: list[GroupItem] = Field(..., description="小组卡片列表")
    pagination: Pagination = Field(..., description="分页信息")


class GroupMeta(BaseModel):
    """小组基础信息（用于详情页头部展示）。

    包含：创建时间、组长信息、所属分类。
    """

    created_at: datetime = Field(..., description="小组创建时间")
    owner: Optional["OwnerInfo"] = Field(None, description="组长信息（拥有者）")
    category: GroupCategory = Field(..., description="所属分类")


class GroupDetailResponse(BaseModel):
    """小组详情（进入小组页使用）。"""

    id: int = Field(..., description="小组 ID")
    title: str = Field(..., description="小组名称")
    cover_url: Optional[str] = Field(None, description="封面图 URL")
    summary: str = Field(..., description="简介")
    meta: GroupMeta = Field(..., description="基础信息：创建时间、组长信息、所属分类")
    members_count: int = Field(..., description="成员数量")
    posts_count: int | None = Field(None, description="帖子数量（预留），可能为空")
    last_activity_at: Optional[datetime] = Field(None, description="最近活跃时间")
    joined: bool = Field(False, description="当前用户是否已加入")
    liked: bool = Field(False, description="当前用户是否已为该小组点赞")
    rules: list[str] = Field(default_factory=list, description="小组规则，字符串列表")


class OwnerInfo(BaseModel):
    name: str = Field(..., description="拥有者名称（展示名或昵称）")
    avatar_url: Optional[str] = Field(None, description="拥有者头像 URL")


class MembershipState(BaseModel):
    """成员状态（加入/退出操作返回）。"""

    joined: bool = Field(..., description="加入后为 true，退出后为 false（幂等）")
    members_count: int = Field(..., description="当前成员数量")


class MemberItem(BaseModel):
    """小组成员条目。"""

    user_id: int = Field(..., description="用户 ID")
    username: str = Field(..., description="用户名（展示）")
    avatar_url: Optional[str] = Field(None, description="头像 URL")
    role: str = Field(..., description="成员身份：leader|member")
    joined_at: datetime = Field(..., description="加入时间")


class MemberListResponse(BaseModel):
    """小组成员列表响应（分页）。"""

    items: list[MemberItem] = Field(default_factory=list, description="成员列表")
    pagination: Pagination = Field(..., description="分页信息")
