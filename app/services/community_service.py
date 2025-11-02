from __future__ import annotations

import json
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.community import CommunityRepository
from app.repositories.posts import PostsRepository
from app.schemas.community import (
    CategoryItem,
    CategoryListResponse,
    GroupCategory,
    GroupDetailResponse,
    GroupItem,
    GroupListResponse,
    GroupMeta,
    MemberItem,
    MemberListResponse,
    MembershipState,
    OwnerInfo,
    Pagination,
)


class CommunityService:
    """学习社区服务层。

    封装社区相关的业务逻辑，向上为 API 层提供稳定的数据契约：
    - 分类列表与计数
    - 小组搜索/筛选/排序（分页），含是否已加入的标记
    - 小组详情（含组规与拥有者信息）
    - 成员加入/退出（幂等）与“我加入的小组”
    - 小组成员列表（分页，组长优先）

    说明：本服务不做权限判断，由上层路由保证入参 user_id 的合法性。
    """

    def __init__(self, session: AsyncSession) -> None:
        """初始化服务。

        Args:
            session: SQLAlchemy 异步会话，用于数据库访问。
        """
        self.repo = CommunityRepository(session)
        self.post_repo = PostsRepository(session)

    async def list_categories(self) -> CategoryListResponse:
        """获取学习小组分类列表及每类小组数量。

        Returns:
            CategoryListResponse: 包含分类条目 `items=[{id,name,slug,count}, ...]`。

        Notes:
            - 结果可被上层缓存，用于前端筛选 chips。
        """
        rows = await self.repo.list_categories_with_counts()
        items = [CategoryItem(id=cat.id, name=cat.name, slug=cat.slug, count=count) for cat, count in rows]
        return CategoryListResponse(items=items)

    def _map_group_category(self, g) -> GroupCategory:
        """将组对象的分类信息映射为 GroupCategory。"""
        return GroupCategory(
            id=g.category_id or 0,
            name=g.category.name if g.category and getattr(g, "category", None) else "",
            slug=g.category.slug if g.category and getattr(g, "category", None) else "",
        )

    async def list_groups(
        self,
        *,
        q: Optional[str] = None,
        category: Optional[str] = None,
        sort: Optional[str] = None,
        page: int = 1,
        page_size: int = 20,
        user_id: Optional[int] = None,
    ) -> GroupListResponse:
        """搜索/筛选学习小组（分页）。

        Args:
            q: 关键字，匹配标题与简介（模糊）。
            category: 分类 slug；传 `all` 或 None 表示全部。
            sort: 排序方式：`latest|popular|recommended`。
            page: 页码，从 1 开始。
            page_size: 每页数量，最大建议 100。
            user_id: 当前登录用户 ID；用于计算返回项中的 `joined`。

        Returns:
            GroupListResponse: 含 items 与分页信息；items 中 `joined` 在未登录时恒为 False。
        """
        groups, total, joined_map = await self.repo.list_groups(
            q=q, category_slug=category, sort=sort, page=page, page_size=page_size, user_id=user_id
        )
        items: list[GroupItem] = []
        for g in groups:
            cat = self._map_group_category(g)
            items.append(
                GroupItem(
                    id=g.id,
                    title=g.title,
                    cover_url=g.cover_url,
                    summary=g.summary,
                    category=cat,
                    members_count=int(g.members_count or 0),
                    last_activity_at=g.last_activity_at,
                    joined=bool(joined_map.get(g.id, False)),
                )
            )
        return GroupListResponse(items=items, pagination=Pagination(page=page, page_size=page_size, total=total))

    async def group_detail(self, group_id: int, *, user_id: Optional[int]) -> Optional[GroupDetailResponse]:
        """获取小组详情。

        Args:
            group_id: 小组 ID。
            user_id: 当前登录用户 ID；用于标记 `joined`。

        Returns:
            GroupDetailResponse | None: 找不到小组时返回 None。

        Notes:
            - 解析 `rules_json` 为字符串列表 `rules`，异常时回退为空列表。
            - `owner` 直接来自小组表字段（简化模型）。
        """
        g = await self.repo.get_group(group_id)
        if not g:
            return None
        joined = False
        liked = False
        if user_id:
            joined = await self.repo.is_member(user_id, group_id)
            liked = await self.post_repo.is_group_liked(user_id, group_id)
        cat = self._map_group_category(g)
        # parse rules from JSON stored on model (if any)
        rules: list[str] = []
        try:
            if getattr(g, "rules_json", None):
                data = json.loads(g.rules_json or "null")
                if isinstance(data, list):
                    rules = [str(x) for x in data]
        except Exception:
            rules = []

        owner = None
        if getattr(g, "owner_name", None) or getattr(g, "owner_avatar_url", None):
            owner = OwnerInfo(name=g.owner_name or "", avatar_url=getattr(g, "owner_avatar_url", None))

        return GroupDetailResponse(
            id=g.id,
            title=g.title,
            cover_url=g.cover_url,
            summary=g.summary,
            meta=GroupMeta(created_at=g.created_at, owner=owner, category=cat),
            members_count=int(g.members_count or 0),
            posts_count=None,
            last_activity_at=g.last_activity_at,
            joined=joined,
            liked=liked,
            rules=rules,
        )

    async def join(self, user_id: int, group_id: int) -> MembershipState:
        """加入小组（幂等）。

        Args:
            user_id: 用户 ID。
            group_id: 小组 ID。

        Returns:
            MembershipState: `joined=True` 与最新 `members_count`。

        Notes:
            - 若已加入，返回当前计数，不重复插入。
            - 并发情况下命中唯一约束会视为加入成功并返回计数。
        """
        joined, count = await self.repo.join_group(user_id, group_id)
        return MembershipState(joined=joined, members_count=count)

    async def leave(self, user_id: int, group_id: int) -> MembershipState:
        """退出小组（幂等）。

        Args:
            user_id: 用户 ID。
            group_id: 小组 ID。

        Returns:
            MembershipState: `joined=False` 与最新 `members_count`。

        Notes:
            - 若未加入，则直接返回当前计数。
        """
        joined, count = await self.repo.leave_group(user_id, group_id)
        # joined False expected after leave
        return MembershipState(joined=joined, members_count=count)

    async def my_groups(self, user_id: int, *, page: int = 1, page_size: int = 20) -> GroupListResponse:
        """我加入的小组列表（分页）。

        Args:
            user_id: 用户 ID。
            page: 页码，从 1 开始。
            page_size: 每页数量，最大建议 100。

        Returns:
            GroupListResponse: items 中 `joined` 恒为 True；`total` 以当前页长度返回（非严格总数）。
        """
        groups = await self.repo.list_my_groups(user_id, page=page, page_size=page_size)
        items: list[GroupItem] = []
        for g in groups:
            cat = self._map_group_category(g)
            items.append(
                GroupItem(
                    id=g.id,
                    title=g.title,
                    cover_url=g.cover_url,
                    summary=g.summary,
                    category=cat,
                    members_count=int(g.members_count or 0),
                    last_activity_at=g.last_activity_at,
                    joined=True,
                )
            )
        # For my groups, total is not strictly required; set conservatively as len(items)
        return GroupListResponse(
            items=items,
            pagination=Pagination(page=page, page_size=page_size, total=len(items)),
        )

    async def group_members(self, group_id: int, *, page: int = 1, page_size: int = 20) -> MemberListResponse:
        """获取小组成员列表（分页）。

        成员包含用户名、头像与身份；排序为组长优先、加入时间倒序。

        Args:
            group_id: 小组 ID。
            page: 页码，从 1 开始。
            page_size: 每页数量，最大建议 100。

        Returns:
            MemberListResponse: 成员条目与分页信息。

        Notes:
            - 角色目前为 `leader|member` 两类；默认 `member`。
        """
        rows, total = await self.repo.list_group_members(group_id, page=page, page_size=page_size)
        items: list[MemberItem] = []
        for member, username, avatar_url in rows:
            items.append(
                MemberItem(
                    user_id=member.user_id,
                    username=username,
                    avatar_url=avatar_url,
                    role=member.role,
                    joined_at=member.joined_at,
                )
            )
        return MemberListResponse(items=items, pagination=Pagination(page=page, page_size=page_size, total=total))
