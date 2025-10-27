from __future__ import annotations

from typing import Optional, Type, TypeVar

from fastapi import HTTPException, status
from pydantic import BaseModel, ValidationError
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
    CareerOverview,
    CareerSummary,
    CompetencyRequirements,
    SalaryAndDistribution,
    SkillMap,
)

MAX_PAGE_SIZE = 50
DEFAULT_PAGE_SIZE = 20

_ModelT = TypeVar("_ModelT", bound=BaseModel)


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
    def _coerce_section(model_cls: Type[_ModelT], data: object) -> _ModelT | None:
        """将数据库中的 JSON 字段安全转换为 Pydantic 模型，容错异常数据"""
        if not data:
            return None
        if isinstance(data, model_cls):
            return data
        if isinstance(data, dict):
            try:
                return model_cls.model_validate(data)
            except ValidationError:
                return None
        return None

    @staticmethod
    def _build_overview_section(career: Career) -> CareerOverview | None:
        """返回结构化的职业总览数据，兼容旧字段回填"""
        overview_model = CareerService._coerce_section(CareerOverview, career.overview)
        if overview_model:
            return overview_model
        fallback: dict[str, object] = {}
        if career.description:
            fallback["description"] = career.description
        if career.work_contents:
            fallback["work_contents"] = [item for item in career.work_contents if item]
        if career.career_outlook:
            fallback["career_outlook"] = career.career_outlook
        if career.development_path:
            fallback["development_path"] = [item for item in career.development_path if item]
        if not fallback:
            return None
        try:
            return CareerOverview.model_validate(fallback)
        except ValidationError:
            return None

    @staticmethod
    def _build_competency_section(career: Career) -> CompetencyRequirements | None:
        """返回结构化的胜任力信息，兼容旧字段回填"""
        competency_model = CareerService._coerce_section(CompetencyRequirements, career.competency_requirements)
        if competency_model:
            return competency_model
        fallback: dict[str, object] = {}
        if career.core_competency_model:
            fallback["core_competency_model"] = career.core_competency_model
        if career.knowledge_background:
            fallback["knowledge_background"] = career.knowledge_background
        if not fallback:
            return None
        try:
            return CompetencyRequirements.model_validate(fallback)
        except ValidationError:
            return None

    @staticmethod
    def _build_salary_section(career: Career) -> SalaryAndDistribution | None:
        """返回结构化的薪资信息，兼容旧字段回填"""
        salary_model = CareerService._coerce_section(SalaryAndDistribution, career.salary_and_distribution)
        if salary_model:
            return salary_model
        if career.salary_min is None and career.salary_max is None:
            return None
        try:
            return SalaryAndDistribution.model_validate(
                {
                    "salary_level": {},
                    "distribution_of_popular_cities": {},
                }
            )
        except ValidationError:
            return None

    @staticmethod
    def _build_skill_map_section(career: Career) -> SkillMap | None:
        """返回结构化的技能图谱，兼容旧字段回填"""
        skill_model = CareerService._coerce_section(SkillMap, career.skill_map)
        if skill_model:
            return skill_model
        fallback: dict[str, object] = {}
        snapshot = CareerService._extract_skills_snapshot(career)
        if snapshot:
            fallback["skills_snapshot"] = snapshot
        courses = CareerService._extract_related_courses(career)
        if courses:
            fallback["related_courses"] = courses
        if career.required_skills and not snapshot:
            fallback["skills_snapshot"] = CareerService._split_lines(career.required_skills) or []
        if not fallback:
            return None
        try:
            return SkillMap.model_validate(fallback)
        except ValidationError:
            return None

    @staticmethod
    def _extract_skills_snapshot(career: Career) -> list[str] | None:
        """提取职业的技能亮点摘要，优先使用结构化字段"""
        skill_map = career.skill_map if isinstance(career.skill_map, dict) else None
        if skill_map:
            snapshot = skill_map.get("skills_snapshot")
            if isinstance(snapshot, list):
                cleaned = [str(item).strip() for item in snapshot if str(item).strip()]
                if cleaned:
                    return cleaned
        if career.skills_snapshot:
            return [item for item in career.skills_snapshot if item]
        return CareerService._split_lines(career.required_skills)

    @staticmethod
    def _extract_related_courses(career: Career) -> list[str] | None:
        """提取职业关联课程列表，兼容旧字段"""
        skill_map = career.skill_map if isinstance(career.skill_map, dict) else None
        if skill_map:
            courses = skill_map.get("related_courses")
            if isinstance(courses, list):
                cleaned = [str(item).strip() for item in courses if str(item).strip()]
                if cleaned:
                    return cleaned
        if career.related_courses:
            return [item for item in career.related_courses if item]
        return None

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
            career_header_image=career.career_header_image,
            overview=CareerService._build_overview_section(career),
            competency_requirements=CareerService._build_competency_section(career),
            salary_and_distribution=CareerService._build_salary_section(career),
            skill_map=CareerService._build_skill_map_section(career),
            related_courses=CareerService._extract_related_courses(career),
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
            career_header_image=career.career_header_image,
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
        summary = self._build_summary(career)
        summary_data = summary.model_dump()
        return CareerDetail(
            **summary_data,
            cosplay_script_id=career.cosplay_script_id,
            created_at=career.created_at,
            updated_at=career.updated_at,
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
