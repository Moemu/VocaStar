from __future__ import annotations

from typing import Optional, Sequence

from sqlalchemy import and_, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.career import Career, CareerGalaxy


class CareerRepository:
    """职业信息数据访问层，封装职业与星系相关的数据查询逻辑"""

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
        """按维度、关键字与分页参数返回职业列表与总数量"""
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

        stmt = select(Career).options(selectinload(Career.galaxy)).order_by(Career.created_at.desc(), Career.id.desc())
        if filters:
            stmt = stmt.where(*filters)
        stmt = stmt.offset(max(offset, 0)).limit(max(limit, 1))
        items_result = await self.session.execute(stmt)
        items = items_result.scalars().unique().all()
        return list(items), int(total)

    async def get_career_by_id(self, career_id: int) -> Optional[Career]:
        """根据职业 ID 获取单条职业记录，预加载 galaxy 以避免异步懒加载错误"""
        stmt = select(Career).options(selectinload(Career.galaxy)).where(Career.id == career_id)
        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def list_featured_careers(self, limit: int = 6) -> list[Career]:
        """按更新时间倒序获取推荐职业列表"""
        stmt = (
            select(Career)
            .options(selectinload(Career.galaxy))
            .order_by(Career.updated_at.desc(), Career.id.desc())
            .limit(max(limit, 1))
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().unique().all())

    async def get_careers_by_ids(self, career_ids: Sequence[int]) -> list[Career]:
        """批量根据职业 ID 查询职业信息"""
        if not career_ids:
            return []
        stmt = select(Career).options(selectinload(Career.galaxy)).where(Career.id.in_(career_ids))
        result = await self.session.execute(stmt)
        return list(result.scalars().unique().all())

    async def list_careers_with_dimension(self, dimension: str, *, limit: int = 20) -> list[Career]:
        """按照霍兰德维度筛选指定数量的职业"""
        dimension_token = dimension.upper()
        stmt = (
            select(Career)
            .where(
                or_(
                    Career.holland_dimensions.contains([dimension_token]),
                    func.instr(Career.holland_dimensions, f'"{dimension_token}"') > 0,
                )
            )
            .options(selectinload(Career.galaxy))
            .order_by(Career.created_at.desc(), Career.id.desc())
            .limit(max(limit, 1))
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().unique().all())

    async def list_galaxy_exploration(
        self,
        *,
        category: Optional[str],
        salary_avg: Optional[int],
        holland_letters: Optional[list[str]],
    ) -> list[tuple[CareerGalaxy, list[Career]]]:
        """为探索页按星系列出职业，可选分类、平均薪资与霍兰德维度过滤"""
        if holland_letters is not None and len(holland_letters) == 0:
            return []

        stmt = (
            select(CareerGalaxy, Career)
            .join(Career, Career.galaxy_id == CareerGalaxy.id)
            .options(selectinload(CareerGalaxy.careers))
        )

        filters = []
        category = category or ""
        if normalized := category.strip().lower():
            filters.append(
                or_(
                    func.lower(CareerGalaxy.category) == normalized,
                )
            )

        if salary_avg is not None and salary_avg > 0:
            filters.append(
                or_(
                    Career.salary_min.is_(None),
                    Career.salary_max.is_(None),
                    and_(
                        Career.salary_min <= salary_avg,
                        Career.salary_max >= salary_avg,
                    ),
                )
            )
        if holland_letters:
            dimension_filters = []
            for letter in holland_letters:
                token = letter.upper()
                dimension_filters.append(
                    or_(
                        Career.holland_dimensions.contains([token]),
                        func.instr(Career.holland_dimensions, f'"{token}"') > 0,
                    )
                )
            if dimension_filters:
                filters.append(or_(*dimension_filters))

        if filters:
            stmt = stmt.where(*filters)

        stmt = stmt.order_by(
            CareerGalaxy.id.asc(),
            Career.salary_min.asc(),
            Career.id.asc(),
        )

        result = await self.session.execute(stmt)
        grouped: dict[int, dict[str, object]] = {}
        for galaxy, career in result.all():
            if galaxy.id not in grouped:
                grouped[galaxy.id] = {"galaxy": galaxy, "careers": [career]}
            else:
                careers_list = grouped[galaxy.id]["careers"]
                assert isinstance(careers_list, list)
                careers_list.append(career)
        aggregated: list[tuple[CareerGalaxy, list[Career]]] = []
        for entry in grouped.values():
            galaxy_obj = entry.get("galaxy")
            careers_obj = entry.get("careers")
            if isinstance(galaxy_obj, CareerGalaxy) and isinstance(careers_obj, list):
                aggregated.append((galaxy_obj, list(careers_obj)))
        return aggregated

    async def list_explore_categories(self) -> list[str]:
        """汇总所有有效分类标识，供前端构建筛选项"""
        stmt = (
            select(
                CareerGalaxy.category,
                func.min(CareerGalaxy.id).label("order_weight"),
            )
            .group_by(CareerGalaxy.category)
            .order_by(func.min(CareerGalaxy.id).asc(), CareerGalaxy.category.asc())
        )
        result = await self.session.execute(stmt)
        rows = result.all()
        return [row.category for row in rows]

    async def get_salary_bounds(self) -> Optional[tuple[Optional[int], Optional[int]]]:
        """计算职业数据中的全局薪资最小值与最大值"""
        stmt = select(func.min(Career.salary_min), func.max(Career.salary_max))
        result = await self.session.execute(stmt)
        min_value, max_value = result.first() or (None, None)
        if min_value is None and max_value is None:
            return None
        return (min_value, max_value)
