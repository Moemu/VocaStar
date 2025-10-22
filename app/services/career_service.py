from __future__ import annotations

from typing import Optional

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.career import Career, CareerGalaxy
from app.models.user import User
from app.repositories.career import CareerRepository
from app.repositories.quiz import QuizRepository
from app.schemas.career import (
    CareerDetail,
    CareerExploreFilters,
    CareerExploreGalaxy,
    CareerExplorePlanet,
    CareerExploreResponse,
    CareerExploreSalaryRange,
    CareerListResponse,
    CareerSummary,
)

MAX_PAGE_SIZE = 50
DEFAULT_PAGE_SIZE = 20


class CareerService:
    """职业相关业务逻辑封装，负责职业列表、详情与探索页聚合数据"""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.repo = CareerRepository(session)
        self.quiz_repo = QuizRepository(session)

    @staticmethod
    def _split_lines(value: Optional[str]) -> list[str] | None:
        """将多行文本按行拆分为去空白的列表"""
        if not value:
            return None
        items = [line.strip() for line in value.splitlines() if line.strip()]
        return items or None

    @staticmethod
    def _extract_skills_snapshot(career: Career) -> list[str] | None:
        """提取职业的技能亮点摘要，优先使用结构化字段"""
        if career.skills_snapshot:
            return [item for item in career.skills_snapshot if item]
        return CareerService._split_lines(career.required_skills)

    @staticmethod
    def _resolve_galaxy_meta(career: Career) -> tuple[Optional[int], Optional[str], Optional[str]]:
        """从职业对象中读取星系元信息"""
        if career.galaxy:
            return (
                career.galaxy.id,
                career.galaxy.name,
                career.galaxy.category,
            )
        return (None, None, None)

    @staticmethod
    def _build_summary(career: Career) -> CareerSummary:
        """将职业模型转换为列表页展示所需的概要数据"""
        galaxy_id, galaxy_name, category = CareerService._resolve_galaxy_meta(career)
        return CareerSummary(
            id=career.id,
            name=career.name,
            description=career.description,
            holland_dimensions=career.holland_dimensions,
            planet_image_url=career.planet_image_url,
            related_courses=career.related_courses,
            core_competency_model=career.core_competency_model,
            knowledge_background=career.knowledge_background,
            galaxy_id=galaxy_id,
            galaxy_name=galaxy_name,
            category=category,
            salary_min=career.salary_min,
            salary_max=career.salary_max,
            skills_snapshot=CareerService._extract_skills_snapshot(career),
        )

    @staticmethod
    def _build_planet(career: Career) -> CareerExplorePlanet:
        """构建探索页面中的职业星球数据块"""
        return CareerExplorePlanet(
            id=career.id,
            name=career.name,
            description=career.description,
            planet_image_url=career.planet_image_url,
            holland_dimensions=career.holland_dimensions,
            salary_min=career.salary_min,
            salary_max=career.salary_max,
            skills_snapshot=CareerService._extract_skills_snapshot(career),
        )

    def _build_galaxy(self, galaxy: CareerGalaxy, careers: list[Career]) -> CareerExploreGalaxy:
        """组装星系与其下星球的展示结构"""
        planets = [self._build_planet(career) for career in careers]
        return CareerExploreGalaxy(
            id=galaxy.id,
            name=galaxy.name,
            category=galaxy.category,
            description=galaxy.description,
            cover_image_url=galaxy.cover_image_url,
            planets=planets,
        )

    def _build_detail(self, career: Career) -> CareerDetail:
        """构建职业详情响应，补充星系与技能信息"""
        galaxy = career.galaxy
        return CareerDetail(
            id=career.id,
            name=career.name,
            cosplay_script_id=career.cosplay_script_id,
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
            galaxy_id=galaxy.id if galaxy else None,
            galaxy_name=galaxy.name if galaxy else None,
            category=galaxy.category if galaxy else None,
            salary_min=career.salary_min,
            salary_max=career.salary_max,
            skills_snapshot=CareerService._extract_skills_snapshot(career),
            galaxy_description=galaxy.description if galaxy else None,
            galaxy_cover_image_url=galaxy.cover_image_url if galaxy else None,
        )

    async def _get_users_holland_letters(self, user: Optional[User]) -> list[str]:
        """获取用户最近测评对应的霍兰德维度集合，未登录返回空列表"""
        # 未登录时默认返回全部职业，即返回空列表
        if not user:
            return []

        latest_submission = await self.quiz_repo.get_latest_completed_submission(user.id)
        report_payload = (
            latest_submission.report.result_json if latest_submission and latest_submission.report else None
        )
        code = (report_payload or {}).get("holland_code") if isinstance(report_payload, dict) else None
        if isinstance(code, str) and code.strip():
            holland_letters = [letter.upper() for letter in code if letter.isalpha()]
        else:
            holland_letters = []

        return holland_letters

    async def list_careers(
        self,
        *,
        dimension: Optional[str] = None,
        keyword: Optional[str] = None,
        limit: int = DEFAULT_PAGE_SIZE,
        offset: int = 0,
    ) -> CareerListResponse:
        """按条件分页查询职业列表"""
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
        """查询职业详情，若不存在则返回 404"""
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
        """获取推荐职业列表，可按维度筛选"""
        safe_limit = min(max(limit, 1), MAX_PAGE_SIZE)
        if dimension:
            items = await self.repo.list_careers_with_dimension(dimension.upper(), limit=safe_limit)
        else:
            items = await self.repo.list_featured_careers(limit=safe_limit)
        return [self._build_summary(item) for item in items]

    async def explore_careers(
        self,
        *,
        category: Optional[str] = None,
        salary_avg: Optional[int] = None,
        recommended: bool = False,
        current_user: Optional[User] = None,
    ) -> CareerExploreResponse:
        """汇总职业探索页面数据，支持分类、薪资与推荐过滤"""
        holland_letters: list[str] | None = None
        if recommended:
            holland_letters = await self._get_users_holland_letters(current_user)

        if recommended and holland_letters is not None and len(holland_letters) == 0:
            grouped: list[tuple[CareerGalaxy, list[Career]]] = []
        else:
            grouped = await self.repo.list_galaxy_exploration(
                category=category,
                salary_avg=salary_avg,
                holland_letters=holland_letters,
            )

        galaxies: list[CareerExploreGalaxy] = []
        for galaxy, careers in grouped:
            if not careers:
                continue
            galaxies.append(self._build_galaxy(galaxy, careers))

        categories = await self.repo.list_explore_categories()
        salary_bounds = await self.repo.get_salary_bounds()
        filters = CareerExploreFilters(
            categories=categories,
            salary=(
                None
                if salary_bounds is None
                else CareerExploreSalaryRange(
                    min=salary_bounds[0],
                    max=salary_bounds[1],
                )
            ),
        )

        return CareerExploreResponse(galaxies=galaxies, filters=filters)
