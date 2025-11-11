from __future__ import annotations

from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.repositories.partners import PartnersRepository
from app.schemas.community import Pagination
from app.schemas.partners import (
    BindState,
    PartnerItem,
    PartnerListResponse,
    PartnerMyItem,
    PartnerMyListResponse,
    PartnerRecommendItem,
    PartnerRecommendListResponse,
    SkillStat,
)


class PartnerService:
    """职业伙伴服务。

    负责协调仓库层，组装响应模型并施加业务规则，例如不同列表隐藏不同字段。
    """

    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.repo = PartnersRepository(session)

    async def search(self, *, q: Optional[str], skill: Optional[str], page: int, page_size: int) -> PartnerListResponse:
        """搜索职业伙伴。

        参数：
          - q: 模糊搜索关键字，匹配 name 或 profession
          - skill: 技能过滤（精确技能标签）
          - page/page_size: 分页
        返回：完整信息的伙伴列表（包含学习进度与技术栈）
        """
        partners, total, skills_map = await self.repo.search_partners(q=q, skill=skill, page=page, page_size=page_size)
        items = [
            PartnerItem(
                id=p.id,
                name=p.name,
                avatar_url=p.avatar_url,
                profession=p.profession,
                learning_progress=p.learning_progress,
                tech_stack=skills_map.get(p.id, []),
            )
            for p in partners
        ]
        return PartnerListResponse(items=items, pagination=Pagination(page=page, page_size=page_size, total=total))

    async def hot_skills(self, *, limit: int = 20) -> list[SkillStat]:
        """返回按出现频次排序的技能标签。"""
        rows = await self.repo.hot_skills(limit=limit)
        return [SkillStat(skill=s, count=c) for s, c in rows]

    async def recommended(
        self, *, current_user: Optional[User], limit: int = 6, skill: Optional[str] = None
    ) -> PartnerRecommendListResponse:
        """为当前用户返回推荐伙伴列表（隐藏学习进度）。

        - 若用户已登录：排除已绑定的伙伴
        - 可选按技能过滤
        - 排序按绑定次数/受欢迎度
        """
        uid = current_user.id if current_user else None
        partners, skills_map = await self.repo.recommended_for_user(user_id=uid, limit=limit, skill=skill)
        items = [
            PartnerRecommendItem(
                id=p.id,
                name=p.name,
                avatar_url=p.avatar_url,
                profession=p.profession,
                tech_stack=skills_map.get(p.id, []),
            )
            for p in partners
        ]
        return PartnerRecommendListResponse(items=items)

    async def bind(self, *, current_user: User, partner_id: int) -> BindState:
        """绑定伙伴（幂等）。"""
        await self.repo.bind_partner(user_id=current_user.id, partner_id=partner_id)
        # 可按需更新受欢迎度/统计，这里先保持简单
        # 成就：伙伴绑定事件
        from app.services.achievement_service import AchievementService

        await AchievementService(self.session).evaluate_and_award(current_user.id, events=["partner_bind"])
        return BindState(bound=True)

    async def unbind(self, *, current_user: User, partner_id: int) -> BindState:
        """解绑伙伴（幂等）。"""
        await self.repo.unbind_partner(user_id=current_user.id, partner_id=partner_id)
        return BindState(bound=False)

    async def my_partners(self, *, current_user: User, page: int, page_size: int) -> PartnerMyListResponse:
        """返回用户已绑定的伙伴（隐藏技术栈）。"""
        partners, total, _skills_map = await self.repo.my_partners(
            user_id=current_user.id, page=page, page_size=page_size
        )
        items = [
            PartnerMyItem(
                id=p.id,
                name=p.name,
                avatar_url=p.avatar_url,
                profession=p.profession,
                learning_progress=p.learning_progress,
                updated_at=p.updated_at,
            )
            for p in partners
        ]
        return PartnerMyListResponse(items=items, pagination=Pagination(page=page, page_size=page_size, total=total))
