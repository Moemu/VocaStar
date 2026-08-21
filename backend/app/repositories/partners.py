from __future__ import annotations

from collections import defaultdict
from typing import Iterable, Optional

from sqlalchemy import Select, delete, distinct, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.partners import (
    CommunityPartner,
    CommunityPartnerSkill,
    UserPartnerBinding,
)


class PartnersRepository:
    """数据访问：职业伙伴。

    提供搜索、热门技能、推荐、绑定/解绑、我的伙伴等查询与写操作。
    所有查询均为异步，且尽量使用批量查询避免 N+1。
    """

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def _get_skills_for_partners(self, partner_ids: Iterable[int]) -> dict[int, list[str]]:
        if not partner_ids:
            return {}
        stmt: Select = (
            select(CommunityPartnerSkill.partner_id, CommunityPartnerSkill.skill)
            .where(CommunityPartnerSkill.partner_id.in_(list(partner_ids)))
            .order_by(CommunityPartnerSkill.partner_id.asc(), CommunityPartnerSkill.skill.asc())
        )
        rows = (await self.session.execute(stmt)).all()
        mapping: dict[int, list[str]] = defaultdict(list)
        for pid, skill in rows:
            mapping[int(pid)].append(skill)
        return mapping

    async def search_partners(
        self,
        *,
        q: Optional[str],
        skill: Optional[str],
        page: int,
        page_size: int,
    ) -> tuple[list[CommunityPartner], int, dict[int, list[str]]]:
        """搜索职业伙伴。

        - q 模糊匹配 name 或 profession
        - skill 若给定，则按技能过滤（基于 skills 关系）
        返回：伙伴列表、总数、技能映射
        """
        stmt = select(CommunityPartner)
        if q:
            like = f"%{(q or '').lower()}%"
            stmt = stmt.where(
                (func.lower(CommunityPartner.name).like(like)) | (func.lower(CommunityPartner.profession).like(like))
            )
        if skill:
            sub = select(distinct(CommunityPartnerSkill.partner_id)).where(CommunityPartnerSkill.skill == skill)
            stmt = stmt.where(CommunityPartner.id.in_(sub))
        # 统计总数
        count_stmt = stmt.with_only_columns(func.count()).order_by(None)
        total = int((await self.session.execute(count_stmt)).scalar() or 0)
        # 分页结果
        stmt = stmt.order_by(CommunityPartner.popularity.desc(), CommunityPartner.id.asc())
        stmt = stmt.offset((page - 1) * page_size).limit(page_size)
        partners_list: list[CommunityPartner] = list((await self.session.execute(stmt)).scalars().all())
        skills_map = await self._get_skills_for_partners(p.id for p in partners_list)
        return partners_list, total, skills_map

    async def hot_skills(self, *, limit: int = 20) -> list[tuple[str, int]]:
        """按技能统计伙伴数量，按多到少排序。"""
        stmt = (
            select(CommunityPartnerSkill.skill, func.count().label("cnt"))
            .group_by(CommunityPartnerSkill.skill)
            .order_by(func.count().desc(), CommunityPartnerSkill.skill.asc())
            .limit(limit)
        )
        rows = (await self.session.execute(stmt)).all()
        return [(str(r[0]), int(r[1])) for r in rows]

    async def recommended_for_user(
        self,
        *,
        user_id: Optional[int],
        limit: int = 10,
        skill: Optional[str] = None,
    ) -> tuple[list[CommunityPartner], dict[int, list[str]]]:
        """为用户推荐伙伴：
        - 排序：按被绑定次数降序，其次按 popularity，再次按 id 升序
        - 若提供 skill，仅筛选具备该技能的伙伴
        - 若提供 user_id，排除已绑定的伙伴
        返回：伙伴列表及技能映射
        """
        # 聚合绑定次数
        bind_count = func.count(UserPartnerBinding.id)
        base = (
            select(CommunityPartner, bind_count.label("bc"))
            .join(UserPartnerBinding, UserPartnerBinding.partner_id == CommunityPartner.id, isouter=True)
            .group_by(CommunityPartner.id)
        )
        if skill:
            base = base.join(CommunityPartnerSkill, CommunityPartnerSkill.partner_id == CommunityPartner.id).where(
                CommunityPartnerSkill.skill == skill
            )
        if user_id:
            # 排除用户已绑定
            sub = select(UserPartnerBinding.partner_id).where(UserPartnerBinding.user_id == user_id)
            base = base.where(~CommunityPartner.id.in_(sub))
        base = base.order_by(bind_count.desc(), CommunityPartner.popularity.desc(), CommunityPartner.id.asc()).limit(
            limit
        )
        partners = [row[0] for row in (await self.session.execute(base)).all()]
        skills_map = await self._get_skills_for_partners(p.id for p in partners)
        return partners, skills_map

    async def bind_partner(self, *, user_id: int, partner_id: int) -> bool:
        """绑定伙伴（幂等）。返回是否已绑定状态。"""
        # 已存在则直接返回
        exists_stmt = select(UserPartnerBinding).where(
            UserPartnerBinding.user_id == user_id, UserPartnerBinding.partner_id == partner_id
        )
        if (await self.session.execute(exists_stmt)).scalars().first():
            return True
        self.session.add(UserPartnerBinding(user_id=user_id, partner_id=partner_id))
        await self.session.flush()
        await self.session.commit()
        return True

    async def unbind_partner(self, *, user_id: int, partner_id: int) -> bool:
        """解绑伙伴（幂等）。返回解绑后状态 False。"""
        stmt = select(UserPartnerBinding).where(
            UserPartnerBinding.user_id == user_id, UserPartnerBinding.partner_id == partner_id
        )
        row = (await self.session.execute(stmt)).scalars().first()
        if row:
            await self.session.execute(
                delete(UserPartnerBinding).where(
                    UserPartnerBinding.user_id == user_id, UserPartnerBinding.partner_id == partner_id
                )
            )
            await self.session.commit()
        return False

    async def my_partners(
        self, *, user_id: int, page: int, page_size: int
    ) -> tuple[list[CommunityPartner], int, dict[int, list[str]]]:
        """列出用户绑定的伙伴（分页）。"""
        base_ids = select(UserPartnerBinding.partner_id).where(UserPartnerBinding.user_id == user_id)
        count_stmt = select(func.count()).select_from(base_ids.subquery())
        total = int((await self.session.execute(count_stmt)).scalar() or 0)

        stmt = (
            select(CommunityPartner)
            .where(CommunityPartner.id.in_(base_ids))
            .order_by(CommunityPartner.id.asc())
            .offset((page - 1) * page_size)
            .limit(page_size)
        )
        partners_list: list[CommunityPartner] = list((await self.session.execute(stmt)).scalars().all())
        skills_map = await self._get_skills_for_partners(p.id for p in partners_list)
        return partners_list, total, skills_map
