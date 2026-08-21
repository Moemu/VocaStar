from __future__ import annotations

from typing import Optional, Tuple

from sqlalchemy import and_, case, func, literal, or_, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.community import CommunityCategory, CommunityGroup, CommunityGroupMember


class CommunityRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def list_categories_with_counts(self) -> list[tuple[CommunityCategory, int]]:
        stmt = (
            select(CommunityCategory, func.count(CommunityGroup.id))
            .select_from(CommunityCategory)
            .join(CommunityGroup, CommunityGroup.category_id == CommunityCategory.id, isouter=True)
            .group_by(CommunityCategory.id)
            .order_by(CommunityCategory.order.asc(), CommunityCategory.id.asc())
        )
        res = await self.session.execute(stmt)
        rows = res.all()
        return [(row[0], int(row[1] or 0)) for row in rows]

    async def list_groups(
        self,
        *,
        q: Optional[str] = None,
        category_slug: Optional[str] = None,
        sort: Optional[str] = None,
        page: int = 1,
        page_size: int = 20,
        user_id: Optional[int] = None,
    ) -> tuple[list[CommunityGroup], int, dict[int, bool]]:
        conds: list = [CommunityGroup.is_active.is_(True)]
        if q:
            like = f"%{q}%"
            conds.append(or_(CommunityGroup.title.ilike(like), CommunityGroup.summary.ilike(like)))
        if category_slug and category_slug != "all":
            conds.append(CommunityCategory.slug == category_slug)

        base = (
            select(CommunityGroup)
            .options(selectinload(CommunityGroup.category))
            .join(CommunityCategory, CommunityCategory.id == CommunityGroup.category_id, isouter=True)
            .where(and_(*conds))
        )

        # total
        total_stmt = (
            select(func.count(CommunityGroup.id))
            .select_from(CommunityGroup)
            .join(CommunityCategory, CommunityCategory.id == CommunityGroup.category_id, isouter=True)
            .where(and_(*conds))
        )
        total = (await self.session.execute(total_stmt)).scalar() or 0

        # sorting
        if sort == "popular":
            base = base.order_by(CommunityGroup.members_count.desc(), CommunityGroup.id.desc())
        elif sort == "recommended":
            base = base.order_by(CommunityGroup.last_activity_at.desc().nullslast(), CommunityGroup.id.desc())
        else:  # latest
            base = base.order_by(CommunityGroup.id.desc())

        # pagination
        base = base.limit(page_size).offset((page - 1) * page_size)
        result = await self.session.execute(base)
        groups = list(result.scalars().unique().all())

        joined_map: dict[int, bool] = {}
        if user_id and groups:
            group_ids = [g.id for g in groups]
            j_stmt = select(CommunityGroupMember.group_id).where(
                CommunityGroupMember.user_id == user_id, CommunityGroupMember.group_id.in_(group_ids)
            )
            j_res = await self.session.execute(j_stmt)
            for gid in j_res.scalars().all():
                joined_map[int(gid)] = True

        return groups, int(total), joined_map

    async def get_group(self, group_id: int) -> Optional[CommunityGroup]:
        res = await self.session.execute(
            select(CommunityGroup).options(selectinload(CommunityGroup.category)).where(CommunityGroup.id == group_id)
        )
        return res.scalars().first()

    async def is_member(self, user_id: int, group_id: int) -> bool:
        stmt = select(func.count(CommunityGroupMember.id)).where(
            CommunityGroupMember.user_id == user_id, CommunityGroupMember.group_id == group_id
        )
        return bool((await self.session.execute(stmt)).scalar())

    async def join_group(self, user_id: int, group_id: int) -> Tuple[bool, int]:
        # idempotent: if exists, return joined True and current count
        if await self.is_member(user_id, group_id):
            count = await self._members_count(group_id)
            return True, count

        membership = CommunityGroupMember(user_id=user_id, group_id=group_id)
        self.session.add(membership)
        try:
            await self.session.flush()
        except IntegrityError:
            await self.session.rollback()
            # Likely unique constraint hit in race; treat as joined
            count = await self._members_count(group_id)
            return True, count

        # update group members_count
        await self.session.execute(select(literal(1)))  # no-op to ensure we have a valid transaction
        g = await self.get_group(group_id)
        if g:
            g.members_count = (g.members_count or 0) + 1
        await self.session.commit()
        return True, await self._members_count(group_id)

    async def leave_group(self, user_id: int, group_id: int) -> Tuple[bool, int]:
        # delete membership if exists
        res = await self.session.execute(
            select(CommunityGroupMember).where(
                CommunityGroupMember.user_id == user_id, CommunityGroupMember.group_id == group_id
            )
        )
        obj = res.scalars().first()
        if not obj:
            # idempotent
            return False, await self._members_count(group_id)

        await self.session.delete(obj)
        g = await self.get_group(group_id)
        if g and (g.members_count or 0) > 0:
            g.members_count = int(g.members_count) - 1
        await self.session.commit()
        return False, await self._members_count(group_id)

    async def _members_count(self, group_id: int) -> int:
        stmt = select(func.count(CommunityGroupMember.id)).where(CommunityGroupMember.group_id == group_id)
        return int((await self.session.execute(stmt)).scalar() or 0)

    async def list_my_groups(self, user_id: int, *, page: int = 1, page_size: int = 20) -> list[CommunityGroup]:
        stmt = (
            select(CommunityGroup)
            .options(selectinload(CommunityGroup.category))
            .join(CommunityGroupMember, CommunityGroupMember.group_id == CommunityGroup.id)
            .where(CommunityGroupMember.user_id == user_id)
            .order_by(CommunityGroup.id.desc())
            .limit(page_size)
            .offset((page - 1) * page_size)
        )
        res = await self.session.execute(stmt)
        return list(res.scalars().unique().all())

    async def list_group_members(
        self, group_id: int, *, page: int = 1, page_size: int = 20
    ) -> tuple[list[tuple[CommunityGroupMember, str, Optional[str]]], int]:
        # total
        total_stmt = select(func.count(CommunityGroupMember.id)).where(CommunityGroupMember.group_id == group_id)
        total = int((await self.session.execute(total_stmt)).scalar() or 0)

        # order: leader first, then joined_at desc
        leader_first = case((CommunityGroupMember.role == "leader", 0), else_=1)

        from app.models.user import User  # local import to avoid circulars

        stmt = (
            select(
                CommunityGroupMember, func.coalesce(User.nickname, User.username).label("display_name"), User.avatar_url
            )
            .join(User, User.id == CommunityGroupMember.user_id)
            .where(CommunityGroupMember.group_id == group_id)
            .order_by(leader_first.asc(), CommunityGroupMember.joined_at.desc())
            .limit(page_size)
            .offset((page - 1) * page_size)
        )
        res = await self.session.execute(stmt)
        rows = res.all()
        return [(row[0], row[1], row[2]) for row in rows], total

    async def get_group_leader(self, group_id: int) -> Optional[tuple[str, Optional[str]]]:
        """获取小组组长的展示名与头像（若存在）。

        返回: (display_name, avatar_url) 或 None
        """
        from app.models.user import User  # local import to avoid circulars

        stmt = (
            select(func.coalesce(User.nickname, User.username).label("display_name"), User.avatar_url)
            .select_from(CommunityGroupMember)
            .join(User, User.id == CommunityGroupMember.user_id)
            .where(CommunityGroupMember.group_id == group_id, CommunityGroupMember.role == "leader")
            .order_by(CommunityGroupMember.joined_at.asc())
            .limit(1)
        )
        res = await self.session.execute(stmt)
        row = res.first()
        if not row:
            return None
        return str(row[0]), row[1]
