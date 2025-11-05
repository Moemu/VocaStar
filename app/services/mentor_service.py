from __future__ import annotations

from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.repositories.mentors import MentorsRepository
from app.schemas.community import Pagination
from app.schemas.mentors import (
    DomainItem,
    DomainListResponse,
    MentorItem,
    MentorListResponse,
    MentorRequestCreate,
    MentorRequestItem,
)


class MentorService:
    """职业导师服务层。

    职责：
      - 对接仓库层，组装响应 Schema
      - 应用业务规则（领域筛选、隐藏/展示字段等）
    """

    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.repo = MentorsRepository(session)

    async def list_domains(self) -> DomainListResponse:
        """列出导师领域（含数量）。"""
        rows = await self.repo.list_domains_with_counts()
        items = [DomainItem(slug=d.slug, name=d.name, count=c) for d, c in rows]
        return DomainListResponse(items=items)

    async def search(
        self,
        *,
        q: Optional[str],
        skill: Optional[str],
        domain: Optional[str],
        page: int,
        page_size: int,
    ) -> MentorListResponse:
        """搜索导师：按姓名/职业模糊匹配，按技能/领域过滤。"""
        mentors, total, skills_map, domains_map = await self.repo.search(
            q=q, skill=skill, domain_slug=domain, page=page, page_size=page_size
        )
        items = [
            MentorItem(
                id=m.id,
                name=m.name,
                avatar_url=m.avatar_url,
                profession=m.profession,
                company=m.company,
                fee_per_hour=m.fee_per_hour,
                rating=float(m.rating or 0),
                rating_count=m.rating_count,
                tech_stack=skills_map.get(m.id, []),
                domains=domains_map.get(m.id, []),
            )
            for m in mentors
        ]
        return MentorListResponse(items=items, pagination=Pagination(page=page, page_size=page_size, total=total))

    async def create_request(
        self,
        *,
        current_user: User,
        mentor_id: int,
        payload: MentorRequestCreate,
    ) -> MentorRequestItem:
        """创建提问/咨询申请。"""
        o = await self.repo.create_request(
            mentor_id=mentor_id,
            user_id=current_user.id,
            type_=payload.type,
            # message=payload.message,
            # preferred_time=payload.preferred_time,
            # duration_min=payload.duration_min,
        )
        return MentorRequestItem(id=o.id, status=o.status)
