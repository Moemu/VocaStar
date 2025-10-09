from __future__ import annotations

from typing import Optional, Sequence

from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.career import Career


class CareerRepository:
    """职业信息数据访问层"""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def list_careers(
        self,
        *,
        dimension: Optional[str] = None,
        keyword: Optional[str] = None,
        limit: int = 20,
        offset: int = 0,
    ) -> tuple[list[Career], int]:
        filters = []
        if dimension:
            dimension_token = dimension.upper()
            dimension_filter = or_(
                Career.holland_dimensions.contains([dimension_token]),
                func.instr(Career.holland_dimensions, f'"{dimension_token}"') > 0,
            )
            filters.append(dimension_filter)
        if keyword:
            like_pattern = f"%{keyword.strip()}%"
            filters.append(
                or_(
                    Career.name.ilike(like_pattern),
                    Career.description.ilike(like_pattern),
                )
            )

        count_stmt = select(func.count()).select_from(Career)
        if filters:
            count_stmt = count_stmt.where(*filters)
        total_result = await self.session.execute(count_stmt)
        total = total_result.scalar_one()

        stmt = select(Career).order_by(Career.created_at.desc(), Career.id.desc())
        if filters:
            stmt = stmt.where(*filters)
        stmt = stmt.offset(max(offset, 0)).limit(max(limit, 1))
        items_result = await self.session.execute(stmt)
        items = items_result.scalars().unique().all()
        return list(items), int(total)

    async def get_career_by_id(self, career_id: int) -> Optional[Career]:
        stmt = select(Career).where(Career.id == career_id)
        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def list_featured_careers(self, limit: int = 6) -> list[Career]:
        stmt = select(Career).order_by(Career.updated_at.desc(), Career.id.desc()).limit(max(limit, 1))
        result = await self.session.execute(stmt)
        return list(result.scalars().unique().all())

    async def get_careers_by_ids(self, career_ids: Sequence[int]) -> list[Career]:
        if not career_ids:
            return []
        stmt = select(Career).where(Career.id.in_(career_ids))
        result = await self.session.execute(stmt)
        return list(result.scalars().unique().all())

    async def list_careers_with_dimension(self, dimension: str, *, limit: int = 20) -> list[Career]:
        dimension_token = dimension.upper()
        stmt = (
            select(Career)
            .where(
                or_(
                    Career.holland_dimensions.contains([dimension_token]),
                    func.instr(Career.holland_dimensions, f'"{dimension_token}"') > 0,
                )
            )
            .order_by(Career.created_at.desc(), Career.id.desc())
            .limit(max(limit, 1))
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().unique().all())
