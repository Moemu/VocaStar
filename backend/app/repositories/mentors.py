from __future__ import annotations

from collections import defaultdict
from typing import Iterable, Optional

from sqlalchemy import Select, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.mentors import (
    CommunityMentor,
    CommunityMentorSkill,
    MentorDomain,
    MentorDomainMap,
    MentorRequest,
)

DEFAULT_DOMAINS: list[tuple[str, str, int]] = [
    ("frontend", "前端开发", 1),
    ("backend", "后端开发", 2),
    ("mobile", "移动开发", 3),
    ("product", "产品管理", 4),
    ("design", "设计创意", 5),
    ("data", "数据分析", 6),
    ("ai", "人工智能", 7),
    ("marketing", "市场营销", 8),
    ("operation", "运营管理", 9),
    ("devops", "DevOps", 10),
    ("qa", "测试工程", 11),
]


class MentorsRepository:
    """数据访问：职业导师。

    提供导师搜索、领域列表、创建申请等方法。
    """

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def ensure_domains(self) -> None:
        """确保默认领域存在（可重复调用）。"""
        existing = {slug for slug, in (await self.session.execute(select(MentorDomain.slug))).all()}
        created = 0
        for slug, name, order in DEFAULT_DOMAINS:
            if slug in existing:
                continue
            self.session.add(MentorDomain(slug=slug, name=name, order=order))
            created += 1
        if created:
            await self.session.flush()

    async def list_domains_with_counts(self) -> list[tuple[MentorDomain, int]]:
        """返回所有领域及其导师数量。"""
        await self.ensure_domains()
        stmt = (
            select(MentorDomain, func.count(MentorDomainMap.id))
            .select_from(MentorDomain)
            .join(MentorDomainMap, MentorDomainMap.domain_id == MentorDomain.id, isouter=True)
            .group_by(MentorDomain.id)
            .order_by(MentorDomain.order.asc(), MentorDomain.id.asc())
        )
        rows = (await self.session.execute(stmt)).all()
        return [(r[0], int(r[1] or 0)) for r in rows]

    async def _skills_for(self, mentor_ids: Iterable[int]) -> dict[int, list[str]]:
        if not mentor_ids:
            return {}
        stmt: Select = (
            select(CommunityMentorSkill.mentor_id, CommunityMentorSkill.skill)
            .where(CommunityMentorSkill.mentor_id.in_(list(mentor_ids)))
            .order_by(CommunityMentorSkill.mentor_id.asc(), CommunityMentorSkill.skill.asc())
        )
        rows = (await self.session.execute(stmt)).all()
        mapping: dict[int, list[str]] = defaultdict(list)
        for mid, skill in rows:
            mapping[int(mid)].append(str(skill))
        return mapping

    async def _domains_for(self, mentor_ids: Iterable[int]) -> dict[int, list[str]]:
        if not mentor_ids:
            return {}
        stmt: Select = (
            select(MentorDomainMap.mentor_id, MentorDomain.slug)
            .join(MentorDomain, MentorDomain.id == MentorDomainMap.domain_id)
            .where(MentorDomainMap.mentor_id.in_(list(mentor_ids)))
            .order_by(MentorDomainMap.mentor_id.asc(), MentorDomain.order.asc())
        )
        rows = (await self.session.execute(stmt)).all()
        mapping: dict[int, list[str]] = defaultdict(list)
        for mid, slug in rows:
            mapping[int(mid)].append(str(slug))
        return mapping

    async def search(
        self,
        *,
        q: Optional[str],
        skill: Optional[str],
        domain_slug: Optional[str],
        page: int,
        page_size: int,
    ) -> tuple[list[CommunityMentor], int, dict[int, list[str]], dict[int, list[str]]]:
        stmt = select(CommunityMentor).where(CommunityMentor.is_active.is_(True))
        if q:
            # Escape % and _ for SQL LIKE
            def escape_like(val: str) -> str:
                return val.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")

            escaped_q = escape_like((q or "").lower())
            like = f"%{escaped_q}%"
            stmt = stmt.where(
                (func.lower(CommunityMentor.name).like(like, escape="\\"))
                | (func.lower(CommunityMentor.profession).like(like, escape="\\"))
            )
        if skill:
            sub = select(CommunityMentorSkill.mentor_id).where(CommunityMentorSkill.skill == skill)
            stmt = stmt.where(CommunityMentor.id.in_(sub))
        if domain_slug and domain_slug != "all":
            sub = (
                select(MentorDomainMap.mentor_id)
                .join(MentorDomain, MentorDomain.id == MentorDomainMap.domain_id)
                .where(MentorDomain.slug == domain_slug)
            )
            stmt = stmt.where(CommunityMentor.id.in_(sub))

        count_stmt = stmt.with_only_columns(func.count()).order_by(None)
        total = int((await self.session.execute(count_stmt)).scalar() or 0)

        stmt = stmt.order_by(CommunityMentor.popularity.desc(), CommunityMentor.id.asc())
        stmt = stmt.offset((page - 1) * page_size).limit(page_size)
        mentors = list((await self.session.execute(stmt)).scalars().all())

        skills_map = await self._skills_for(m.id for m in mentors)
        domains_map = await self._domains_for(m.id for m in mentors)
        return mentors, total, skills_map, domains_map

    async def create_request(
        self,
        *,
        mentor_id: int,
        user_id: int,
        type_: str,
        # message: str,
        # preferred_time: Optional[str],
        # duration_min: Optional[int],
    ) -> MentorRequest:
        obj = MentorRequest(
            mentor_id=mentor_id,
            user_id=user_id,
            type=type_,
            # message=message,
            # preferred_time=preferred_time,
            # duration_min=duration_min,
        )
        self.session.add(obj)
        await self.session.commit()
        await self.session.refresh(obj)
        return obj

    async def my_mentors(self, *, user_id: int) -> list[CommunityMentor]:
        """返回用户已提交过申请的导师（去重）。

        逻辑：找到 MentorRequest 中 user_id 匹配的所有 mentor_id，去重后取导师基本信息。
        """
        sub = select(MentorRequest.mentor_id).where(MentorRequest.user_id == user_id).distinct()
        stmt = (
            select(CommunityMentor)
            .where(CommunityMentor.id.in_(sub))
            .where(CommunityMentor.is_active.is_(True))
            .order_by(CommunityMentor.popularity.desc(), CommunityMentor.id.asc())
        )
        mentors = list((await self.session.execute(stmt)).scalars().all())
        return mentors
