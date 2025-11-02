from __future__ import annotations

from typing import Iterable, Optional, Tuple

from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.community import (
    CommunityGroup,
    CommunityGroupLike,
    CommunityPost,
    CommunityPostAttachment,
    CommunityPostComment,
    CommunityPostLike,
)
from app.models.user import User


class PostsRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    # Feed
    async def list_posts(
        self,
        *,
        sort: str = "latest",
        page: int = 1,
        page_size: int = 20,
        group_id: Optional[int] = None,
    ) -> Tuple[list[CommunityPost], int]:
        conds = []
        if group_id:
            conds.append(CommunityPost.group_id == group_id)

        base = select(CommunityPost).where(and_(*conds)) if conds else select(CommunityPost)
        # total
        total_stmt = (
            select(func.count(CommunityPost.id)).where(and_(*conds)) if conds else select(func.count(CommunityPost.id))
        )
        total = int((await self.session.execute(total_stmt)).scalar() or 0)

        if sort == "hottest":
            base = base.order_by(CommunityPost.likes_count.desc(), CommunityPost.id.desc())
        else:  # latest
            base = base.order_by(CommunityPost.id.desc())

        base = base.limit(page_size).offset((page - 1) * page_size)
        res = await self.session.execute(base)
        posts = list(res.scalars().unique().all())
        return posts, total

    async def post_attachments(self, post_ids: Iterable[int]) -> dict[int, list[CommunityPostAttachment]]:
        if not post_ids:
            return {}
        stmt = select(CommunityPostAttachment).where(CommunityPostAttachment.post_id.in_(list(post_ids)))
        res = await self.session.execute(stmt)
        items = res.scalars().all()
        m: dict[int, list[CommunityPostAttachment]] = {}
        for a in items:
            m.setdefault(a.post_id, []).append(a)
        return m

    async def post_authors(self, user_ids: Iterable[int]) -> dict[int, tuple[str, Optional[str]]]:
        if not user_ids:
            return {}
        stmt = select(User.id, User.username, User.avatar_url).where(User.id.in_(list(user_ids)))
        res = await self.session.execute(stmt)
        m: dict[int, tuple[str, Optional[str]]] = {}
        for uid, username, avatar in res.all():
            m[int(uid)] = (str(username), avatar)
        return m

    async def post_preview_comments(
        self, post_ids: Iterable[int], limit: int = 3
    ) -> dict[int, list[CommunityPostComment]]:
        if not post_ids or limit <= 0:
            return {}
        # Fetch recent comments per post - naive approach, limit will be applied at service level
        stmt = (
            select(CommunityPostComment)
            .where(CommunityPostComment.post_id.in_(list(post_ids)))
            .order_by(CommunityPostComment.post_id.asc(), CommunityPostComment.created_at.desc())
        )
        res = await self.session.execute(stmt)
        items = res.scalars().all()
        m: dict[int, list[CommunityPostComment]] = {}
        for c in items:
            lst = m.setdefault(c.post_id, [])
            if len(lst) < limit:
                lst.append(c)
        return m

    # Publish
    async def create_post(
        self,
        *,
        group_id: int,
        user_id: int,
        title: str,
        content: str,
    ) -> CommunityPost:
        p = CommunityPost(group_id=group_id, user_id=user_id, title=title, content=content)
        self.session.add(p)
        await self.session.flush()
        return p

    async def add_attachments(self, post_id: int, items: list[tuple[str, str, Optional[str], Optional[int]]]) -> None:
        # items: list[(type, url, title, file_size)]
        for t, url, title, size in items:
            self.session.add(CommunityPostAttachment(post_id=post_id, type=t, url=url, title=title, file_size=size))
        await self.session.flush()

    # Likes on posts
    async def is_post_liked(self, user_id: int, post_id: int) -> bool:
        stmt = select(func.count(CommunityPostLike.id)).where(
            CommunityPostLike.user_id == user_id, CommunityPostLike.post_id == post_id
        )
        return bool((await self.session.execute(stmt)).scalar())

    async def like_post(self, user_id: int, post_id: int) -> Tuple[bool, int]:
        # idempotent
        if await self.is_post_liked(user_id, post_id):
            return True, await self.post_likes_count(post_id)
        self.session.add(CommunityPostLike(user_id=user_id, post_id=post_id))
        # update count
        p = await self.session.get(CommunityPost, post_id)
        if p:
            p.likes_count = int(p.likes_count or 0) + 1
        await self.session.flush()
        await self.session.commit()
        return True, await self.post_likes_count(post_id)

    async def post_likes_count(self, post_id: int) -> int:
        stmt = select(func.count(CommunityPostLike.id)).where(CommunityPostLike.post_id == post_id)
        return int((await self.session.execute(stmt)).scalar() or 0)

    # Comments
    async def create_comment(self, user_id: int, post_id: int, content: str) -> CommunityPostComment:
        c = CommunityPostComment(user_id=user_id, post_id=post_id, content=content)
        self.session.add(c)
        # update post comments_count
        p = await self.session.get(CommunityPost, post_id)
        if p:
            p.comments_count = int(p.comments_count or 0) + 1
        await self.session.flush()
        await self.session.commit()
        return c

    # Group likes
    async def is_group_liked(self, user_id: int, group_id: int) -> bool:
        stmt = select(func.count(CommunityGroupLike.id)).where(
            CommunityGroupLike.user_id == user_id, CommunityGroupLike.group_id == group_id
        )
        return bool((await self.session.execute(stmt)).scalar())

    async def like_group(self, user_id: int, group_id: int) -> Tuple[bool, int]:
        if await self.is_group_liked(user_id, group_id):
            return True, await self.group_likes_count(group_id)
        self.session.add(CommunityGroupLike(user_id=user_id, group_id=group_id))
        g = await self.session.get(CommunityGroup, group_id)
        if g:
            g.likes_count = int(getattr(g, "likes_count", 0) or 0) + 1
        await self.session.flush()
        await self.session.commit()
        return True, await self.group_likes_count(group_id)

    async def unlike_group(self, user_id: int, group_id: int) -> Tuple[bool, int]:
        stmt = select(CommunityGroupLike).where(
            CommunityGroupLike.user_id == user_id, CommunityGroupLike.group_id == group_id
        )
        res = await self.session.execute(stmt)
        obj = res.scalars().first()
        if not obj:
            return False, await self.group_likes_count(group_id)
        await self.session.delete(obj)
        g = await self.session.get(CommunityGroup, group_id)
        if g and int(getattr(g, "likes_count", 0) or 0) > 0:
            g.likes_count = int(g.likes_count) - 1
        await self.session.commit()
        return False, await self.group_likes_count(group_id)

    async def group_likes_count(self, group_id: int) -> int:
        stmt = select(func.count(CommunityGroupLike.id)).where(CommunityGroupLike.group_id == group_id)
        return int((await self.session.execute(stmt)).scalar() or 0)
