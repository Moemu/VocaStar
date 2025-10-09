from __future__ import annotations

from typing import Optional

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.career import Career
from app.repositories.career import CareerRepository
from app.schemas.career import CareerDetail, CareerListResponse, CareerSummary

MAX_PAGE_SIZE = 50
DEFAULT_PAGE_SIZE = 20


class CareerService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.repo = CareerRepository(session)

    @staticmethod
    def _split_lines(value: Optional[str]) -> list[str] | None:
        if not value:
            return None
        items = [line.strip() for line in value.splitlines() if line.strip()]
        return items or None

    @staticmethod
    def _build_summary(career: Career) -> CareerSummary:
        return CareerSummary(
            id=career.id,
            name=career.name,
            description=career.description,
            holland_dimensions=career.holland_dimensions,
            planet_image_url=career.planet_image_url,
            related_courses=career.related_courses,
            core_competency_model=career.core_competency_model,
            knowledge_background=career.knowledge_background,
        )

    def _build_detail(self, career: Career) -> CareerDetail:
        return CareerDetail(
            id=career.id,
            name=career.name,
            description=career.description,
            holland_dimensions=career.holland_dimensions,
            planet_image_url=career.planet_image_url,
            work_contents=career.work_contents,
            career_outlook=career.career_outlook,
            development_path=career.development_path,
            required_skills=self._split_lines(career.required_skills),
            core_competency_model=career.core_competency_model,
            related_courses=career.related_courses,
            knowledge_background=career.knowledge_background,
            created_at=career.created_at,
            updated_at=career.updated_at,
        )

    async def list_careers(
        self,
        *,
        dimension: Optional[str] = None,
        keyword: Optional[str] = None,
        limit: int = DEFAULT_PAGE_SIZE,
        offset: int = 0,
    ) -> CareerListResponse:
        safe_limit = min(max(limit, 1), MAX_PAGE_SIZE)
        safe_offset = max(offset, 0)
        dimension_upper = dimension.upper() if dimension else None
        items, total = await self.repo.list_careers(
            dimension=dimension_upper,
            keyword=keyword,
            limit=safe_limit,
            offset=safe_offset,
        )
        summaries = [self._build_summary(item) for item in items]
        return CareerListResponse(total=total, items=summaries)

    async def get_career_detail(self, career_id: int) -> CareerDetail:
        career = await self.repo.get_career_by_id(career_id)
        if not career:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="职业不存在或已下线")
        return self._build_detail(career)

    async def list_featured_careers(
        self,
        *,
        limit: int = 6,
        dimension: Optional[str] = None,
    ) -> list[CareerSummary]:
        safe_limit = min(max(limit, 1), MAX_PAGE_SIZE)
        if dimension:
            items = await self.repo.list_careers_with_dimension(dimension.upper(), limit=safe_limit)
        else:
            items = await self.repo.list_featured_careers(limit=safe_limit)
        return [self._build_summary(item) for item in items]
