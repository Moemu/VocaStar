"""Utility script to import career definitions from a YAML file into the database.

Usage examples
Default import using ``assets/careers.yaml``::

    uv run python scripts/import_careers_from_yaml.py

Specify a different YAML file::

    uv run python scripts/import_careers_from_yaml.py --yaml-path path/to/file.yaml

Remove careers that are not present in the YAML payload (dangerous)::

    uv run python scripts/import_careers_from_yaml.py --purge-missing
"""

from __future__ import annotations

import argparse
import asyncio
import sys
from pathlib import Path
from typing import Iterable

import yaml
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

ROOT_PATH = Path(__file__).resolve().parents[1]
if str(ROOT_PATH) not in sys.path:
    sys.path.insert(0, str(ROOT_PATH))

from app.core.logger import logger  # noqa: E402
from app.core.sql import async_session_maker  # noqa: E402
from app.models.career import Career, CareerGalaxy  # noqa: E402


class YamlModel(BaseModel):
    model_config = ConfigDict(extra="allow")


class SkillEnhancementStage(YamlModel):
    name: str | None = None
    description: str | None = None
    tags: list[str] = Field(default_factory=list)


class SkillMapNode(YamlModel):
    skills_snapshot: list[str] = Field(default_factory=list)
    related_courses: list[str] = Field(default_factory=list)
    important_but_not_offered_courses: list[str] = Field(default_factory=list)
    skill_enhancement_path: list[SkillEnhancementStage] = Field(default_factory=list)


class SalaryAndDistributionNode(YamlModel):
    salary_level: dict[str, int] = Field(default_factory=dict)
    distribution_of_popular_cities: dict[str, int] = Field(default_factory=dict)


class KnowledgeBackgroundNode(YamlModel):
    education_requirements: str | None = None
    industry_knowledge: str | None = None
    professional_knowledge: str | None = None
    professional_requirements: list[str] = Field(default_factory=list)


class CompetencyRequirementsNode(YamlModel):
    core_competency_model: dict[str, float] = Field(default_factory=dict)
    knowledge_background: KnowledgeBackgroundNode | None = None


class OverviewNode(YamlModel):
    description: str
    work_contents: list[str] = Field(default_factory=list)
    career_outlook: str | None = None
    development_path: list[str] = Field(default_factory=list)


class GalaxyReference(YamlModel):
    name: str


class CareerNode(YamlModel):
    name: str
    galaxy: GalaxyReference | str
    planet_image_url: str | None = None
    career_header_image: str | None = None
    holland_dimensions: list[str] = Field(default_factory=list)
    overview: OverviewNode
    competency_requirements: CompetencyRequirementsNode
    salary_and_distribution: SalaryAndDistributionNode | None = None
    skill_map: SkillMapNode | None = None

    def galaxy_name(self) -> str:
        if isinstance(self.galaxy, GalaxyReference):
            return self.galaxy.name.strip()
        return str(self.galaxy).strip()


class GalaxyNode(YamlModel):
    name: str
    category: str
    description: str | None = None
    cover_image_url: str | None = None


class CareerDataset(YamlModel):
    careers: dict[str, CareerNode]
    galaxies: dict[str, GalaxyNode]


def load_yaml(path: Path) -> dict:
    if not path.exists():
        raise FileNotFoundError(f"YAML 文件不存在: {path}")
    with path.open("r", encoding="utf-8") as fp:
        payload = yaml.safe_load(fp)
    if not isinstance(payload, dict):
        raise ValueError("职业配置文件的根节点必须是一个对象")
    return payload


def _clean_list(items: Iterable[str] | None) -> list[str]:
    if not items:
        return []
    return [str(item).strip() for item in items if str(item).strip()]


def _strip_or_none(value: str | None) -> str | None:
    if value is None:
        return None
    stripped = value.strip()
    return stripped or None


async def upsert_galaxy(
    session: AsyncSession,
    *,
    identifier: str,
    payload: GalaxyNode,
) -> tuple[CareerGalaxy, bool]:
    name = _strip_or_none(payload.name) or identifier.replace("_", " ")

    stmt = select(CareerGalaxy).where(CareerGalaxy.name == name)
    result = await session.execute(stmt)
    galaxy = result.scalars().first()

    created = False
    category_value = _strip_or_none(payload.category) or name

    if not galaxy:
        galaxy = CareerGalaxy(
            name=name,
            category=category_value,
        )
        session.add(galaxy)
        created = True

    galaxy.category = category_value or galaxy.category
    galaxy.description = _strip_or_none(payload.description) or galaxy.description
    galaxy.cover_image_url = _strip_or_none(payload.cover_image_url)

    return galaxy, created


async def upsert_career(
    session: AsyncSession,
    *,
    identifier: str,
    payload: CareerNode,
    galaxy_index: dict[str, CareerGalaxy],
) -> bool:
    name = _strip_or_none(payload.name) or identifier.replace("_", " ")

    stmt = select(Career).where(Career.name == name)
    result = await session.execute(stmt)
    career = result.scalars().first()

    created = False
    if not career:
        career = Career(name=name)
        session.add(career)
        created = True

    career.career_header_image = _strip_or_none(payload.career_header_image)
    career.planet_image_url = _strip_or_none(payload.planet_image_url)

    overview = payload.overview
    description = _strip_or_none(overview.description) or name
    work_contents = _clean_list(overview.work_contents)
    development_path = _clean_list(overview.development_path)
    career_outlook = _strip_or_none(overview.career_outlook)
    overview_data: dict[str, object] = {"description": description}
    if work_contents:
        overview_data["work_contents"] = work_contents
    if career_outlook:
        overview_data["career_outlook"] = career_outlook
    if development_path:
        overview_data["development_path"] = development_path

    holland_dimensions = _clean_list(payload.holland_dimensions)

    competency = payload.competency_requirements
    competency_data: dict[str, object] = {}
    core_competency_model = {
        str(key): float(value) for key, value in competency.core_competency_model.items() if value is not None
    }
    if core_competency_model:
        competency_data["core_competency_model"] = core_competency_model

    knowledge_background_data: dict[str, object] | None = None
    if competency.knowledge_background:
        kb = competency.knowledge_background
        kb_data: dict[str, object] = {}
        education = _strip_or_none(kb.education_requirements)
        if education:
            kb_data["education_requirements"] = education
        industry = _strip_or_none(kb.industry_knowledge)
        if industry:
            kb_data["industry_knowledge"] = industry
        professional = _strip_or_none(kb.professional_knowledge)
        if professional:
            kb_data["professional_knowledge"] = professional
        professional_requirements = _clean_list(kb.professional_requirements)
        if professional_requirements:
            kb_data["professional_requirements"] = professional_requirements
        if kb_data:
            knowledge_background_data = kb_data
            competency_data["knowledge_background"] = kb_data

    salary_min: int | None = None
    salary_max: int | None = None
    salary_data: dict[str, object] = {}
    if payload.salary_and_distribution:
        salary = payload.salary_and_distribution
        salary_data = {
            key: value for key, value in salary.model_dump(exclude_none=True).items() if value not in (None, [], {})
        }
        salary_levels = {k: int(v) for k, v in salary.salary_level.items() if v is not None}
        if salary_levels:
            salary_data["salary_level"] = salary_levels
            salary_min = min(salary_levels.values())
            salary_max = max(salary_levels.values())
        else:
            salary_data.pop("salary_level", None)

        city_distribution = {
            city: int(count) for city, count in salary.distribution_of_popular_cities.items() if count is not None
        }
        if city_distribution:
            salary_data["distribution_of_popular_cities"] = city_distribution
        else:
            salary_data.pop("distribution_of_popular_cities", None)

    skills_snapshot: list[str] = []
    related_courses: list[str] = []
    skill_map_data: dict[str, object] = {}
    if payload.skill_map:
        skill_map = payload.skill_map
        skill_map_data = {
            key: value for key, value in skill_map.model_dump(exclude_none=True).items() if value not in (None, [], {})
        }
        skills_snapshot = _clean_list(skill_map.skills_snapshot)
        if skills_snapshot:
            skill_map_data["skills_snapshot"] = skills_snapshot
        else:
            skill_map_data.pop("skills_snapshot", None)

        related_courses = _clean_list(skill_map.related_courses)
        if related_courses:
            skill_map_data["related_courses"] = related_courses
        else:
            skill_map_data.pop("related_courses", None)

        important_courses = _clean_list(skill_map.important_but_not_offered_courses)
        if important_courses:
            skill_map_data["important_but_not_offered_courses"] = important_courses
        else:
            skill_map_data.pop("important_but_not_offered_courses", None)

        enhancement_path: list[dict[str, object]] = []
        for stage in skill_map.skill_enhancement_path:
            stage_name = _strip_or_none(stage.name)
            stage_description = _strip_or_none(stage.description)
            tags = _clean_list(stage.tags)
            stage_data: dict[str, object] = {}
            if stage_name:
                stage_data["name"] = stage_name
            if stage_description:
                stage_data["description"] = stage_description
            if tags:
                stage_data["tags"] = tags
            if stage_data:
                enhancement_path.append(stage_data)
        if enhancement_path:
            skill_map_data["skill_enhancement_path"] = enhancement_path
        else:
            skill_map_data.pop("skill_enhancement_path", None)

    galaxy_name = payload.galaxy_name()
    if galaxy_name:
        galaxy_obj = galaxy_index.get(galaxy_name)
        if galaxy_obj:
            career.galaxy_id = galaxy_obj.id
        else:
            logger.warning("未找到名称为 %s 的星系，职业 %s 保持原有关联", galaxy_name, name)

    career.name = name
    career.description = description
    career.holland_dimensions = holland_dimensions or None
    career.work_contents = work_contents or None
    career.career_outlook = career_outlook
    career.development_path = development_path or None
    career.overview = overview_data
    career.competency_requirements = competency_data or None
    career.core_competency_model = core_competency_model or None
    career.knowledge_background = knowledge_background_data
    career.salary_and_distribution = salary_data or None
    career.salary_min = salary_min
    career.salary_max = salary_max
    career.skill_map = skill_map_data or None
    career.skills_snapshot = skills_snapshot or None
    career.related_courses = related_courses or None
    career.required_skills = "\n".join(skills_snapshot) if skills_snapshot else None

    return created


async def purge_missing(session: AsyncSession, keep_names: Iterable[str]) -> int:
    names = {name for name in keep_names if name}
    if not names:
        logger.warning(
            "purge_missing called with empty names set; no careers will be deleted to prevent accidental data loss."
        )
        return 0
    stmt = delete(Career).where(~Career.name.in_(tuple(names)))
    result = await session.execute(stmt)
    return result.rowcount or 0


async def async_main(args: argparse.Namespace) -> None:
    yaml_path = Path(args.yaml_path)
    raw_payload = load_yaml(yaml_path)
    dataset = CareerDataset.model_validate(raw_payload)

    async with async_session_maker() as session:
        galaxy_records: dict[str, CareerGalaxy] = {}
        galaxy_created = 0
        galaxy_updated = 0

        if not dataset.galaxies:
            print("galaxies 条目为空，请检查职业配置文件")
            return

        for identifier, galaxy_payload in dataset.galaxies.items():
            galaxy, created = await upsert_galaxy(
                session,
                identifier=str(identifier),
                payload=galaxy_payload,
            )
            galaxy_records[galaxy.name] = galaxy
            if created:
                galaxy_created += 1
            else:
                galaxy_updated += 1
        await session.flush()

        # Ensure缓存包含所有现有星系，防止 YAML 未覆盖的旧记录丢失关联
        existing_result = await session.execute(select(CareerGalaxy))
        for galaxy in existing_result.scalars():
            galaxy_records.setdefault(galaxy.name, galaxy)

        created_count = 0
        updated_count = 0
        imported_names: list[str] = []

        for identifier, career_payload in dataset.careers.items():
            created = await upsert_career(
                session,
                identifier=str(identifier),
                payload=career_payload,
                galaxy_index=galaxy_records,
            )
            name_value = _strip_or_none(career_payload.name) or str(identifier)
            imported_names.append(name_value)
            if created:
                created_count += 1
            else:
                updated_count += 1

        removed = 0
        if args.purge_missing:
            removed = await purge_missing(session, imported_names)

        await session.commit()

    logger.info(
        "职业导入已完成 ✅ 新增职业 %d 条，更新职业 %d 条，删除职业 %d 条；新增星系 %d 条，更新星系 %d 条 (YAML: %s)",
        created_count,
        updated_count,
        removed,
        galaxy_created,
        galaxy_updated,
        yaml_path,
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="导入 YAML 职业配置到数据库")
    parser.add_argument(
        "--yaml-path",
        type=str,
        default=str(Path("assets") / "careers.yaml"),
        help="职业配置文件路径 (默认为 assets/careers.yaml)",
    )
    parser.add_argument(
        "--purge-missing",
        action="store_true",
        help="删除数据库中未出现在 YAML 中的职业 (谨慎使用)",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    asyncio.run(async_main(args))


if __name__ == "__main__":  # pragma: no cover
    main()
