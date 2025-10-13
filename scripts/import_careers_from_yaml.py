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
from collections.abc import Mapping
from pathlib import Path
from typing import Any, Iterable

import yaml
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

ROOT_PATH = Path(__file__).resolve().parents[1]
if str(ROOT_PATH) not in sys.path:
    sys.path.insert(0, str(ROOT_PATH))

from app.core.logger import logger  # noqa: E402
from app.core.sql import async_session_maker  # noqa: E402
from app.models.career import Career, CareerGalaxy  # noqa: E402

CAREERS_SECTION_KEY = "careers"
GALAXIES_SECTION_KEY = "galaxies"


def load_yaml(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(f"YAML 文件不存在: {path}")
    with path.open("r", encoding="utf-8") as fp:
        payload = yaml.safe_load(fp)
    if not isinstance(payload, Mapping):
        raise ValueError("职业配置文件的根节点必须是一个对象")
    return dict(payload)


def normalize_list(value: Any, *, allow_string: bool = True) -> list[str] | None:
    if value is None:
        return None
    if isinstance(value, list):
        normalized = [str(item).strip() for item in value if str(item).strip()]
        return normalized or None
    if allow_string and isinstance(value, str):
        normalized = [segment.strip() for segment in value.splitlines() if segment.strip()]
        return normalized or None
    raise ValueError("预期为字符串列表或多行字符串")


def normalize_skills(value: Any) -> str | None:
    if value is None:
        return None
    if isinstance(value, str):
        stripped = value.strip()
        return stripped or None
    if isinstance(value, list):
        normalized = [str(item).strip() for item in value if str(item).strip()]
        return "\n".join(normalized) if normalized else None
    raise ValueError("required_skills 字段仅支持字符串或字符串列表")


def normalize_core_competency(value: Any) -> dict[str, float] | None:
    if value is None:
        return None
    if not isinstance(value, Mapping):
        raise ValueError("core_competency_model 字段必须是对象")
    normalized: dict[str, float] = {}
    for key, raw in value.items():
        if raw is None:
            continue
        try:
            normalized[str(key)] = float(raw)
        except (TypeError, ValueError) as exc:
            raise ValueError(f"core_competency_model 字段中 {key!r} 的取值无法转换为数字") from exc
    return normalized or None


def normalize_mapping_of_strings(value: Any, *, field_name: str) -> dict[str, str] | None:
    if value is None:
        return None
    if not isinstance(value, Mapping):
        raise ValueError(f"{field_name} 字段必须是对象")
    normalized: dict[str, str] = {}
    for key, raw in value.items():
        if raw is None:
            continue
        normalized[str(key)] = str(raw).strip()
    return normalized or None


def normalize_optional_int(value: Any, *, field_name: str) -> int | None:
    if value is None or value == "":
        return None
    try:
        return int(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{field_name} 字段必须是整数") from exc


async def upsert_galaxy(
    session: AsyncSession,
    *,
    identifier: str,
    payload: Mapping[str, Any],
) -> tuple[CareerGalaxy, bool]:
    name = payload.get("name") or identifier.replace("_", " ")
    if not isinstance(name, str) or not name.strip():
        raise ValueError(f"星系节点 {identifier!r} 缺少有效的 name 字段")
    name = name.strip()

    stmt = select(CareerGalaxy).where(CareerGalaxy.name == name)
    result = await session.execute(stmt)
    galaxy = result.scalars().first()

    created = False
    category_value = payload.get("category") or name

    if not galaxy:
        galaxy = CareerGalaxy(
            name=name,
            category=category_value,
        )
        session.add(galaxy)
        created = True

    galaxy.category = category_value or galaxy.category
    galaxy.description = payload.get("description") or None
    galaxy.cover_image_url = payload.get("cover_image_url") or None

    return galaxy, created


async def upsert_career(
    session: AsyncSession,
    *,
    identifier: str,
    payload: Mapping[str, Any],
    galaxy_index: Mapping[str, CareerGalaxy],
) -> bool:
    name = payload.get("name") or identifier.replace("_", " ")
    if not isinstance(name, str) or not name.strip():
        raise ValueError(f"职业节点 {identifier!r} 缺少有效的 name 字段")
    name = name.strip()

    stmt = select(Career).where(Career.name == name)
    result = await session.execute(stmt)
    career = result.scalars().first()

    created = False
    if not career:
        career = Career(name=name)
        session.add(career)
        created = True

    career.description = payload.get("description") or None
    career.planet_image_url = payload.get("planet_image_url") or None
    career.career_outlook = payload.get("career_outlook") or None

    holland_dimensions = normalize_list(payload.get("holland_dimensions"), allow_string=False)
    career.holland_dimensions = holland_dimensions

    work_contents = normalize_list(payload.get("work_contents"))
    career.work_contents = work_contents

    development_path = normalize_list(payload.get("development_path"))
    career.development_path = development_path

    career.required_skills = normalize_skills(payload.get("required_skills"))
    career.core_competency_model = normalize_core_competency(payload.get("core_competency_model"))
    career.related_courses = normalize_list(payload.get("related_courses"))
    career.knowledge_background = normalize_mapping_of_strings(
        payload.get("knowledge_background"), field_name="knowledge_background"
    )
    career.salary_min = normalize_optional_int(payload.get("salary_min"), field_name="salary_min")
    career.salary_max = normalize_optional_int(payload.get("salary_max"), field_name="salary_max")
    career.skills_snapshot = normalize_list(payload.get("skills_snapshot"))

    galaxy_ref = payload.get("galaxy")
    galaxy_name: str | None = None
    if isinstance(galaxy_ref, str):
        galaxy_name = galaxy_ref.strip()
    elif isinstance(galaxy_ref, Mapping):
        raw_name = galaxy_ref.get("name")
        galaxy_name = str(raw_name).strip() if raw_name else None

    if galaxy_name:
        galaxy_obj = galaxy_index.get(galaxy_name)
        if galaxy_obj:
            career.galaxy_id = galaxy_obj.id
        else:
            logger.warning("未找到名称为 %s 的星系，职业 %s 保持原有关联", galaxy_name, name)

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
    payload = load_yaml(yaml_path)

    careers_section = payload.get(CAREERS_SECTION_KEY, payload)
    if not isinstance(careers_section, Mapping):
        raise ValueError("careers 节点必须是对象")

    async with async_session_maker() as session:
        galaxy_records: dict[str, CareerGalaxy] = {}
        galaxy_created = 0
        galaxy_updated = 0

        galaxies_section = payload.get(GALAXIES_SECTION_KEY)
        if galaxies_section is None:
            print("galaxies 条目为空，请检查职业配置文件")
            return

        for identifier, galaxy_payload in galaxies_section.items():
            if not isinstance(galaxy_payload, Mapping):
                raise ValueError(f"星系节点 {identifier!r} 必须是对象")
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

        for identifier, career_payload in careers_section.items():
            if not isinstance(career_payload, Mapping):
                raise ValueError(f"职业节点 {identifier!r} 必须是对象")
            created = await upsert_career(
                session,
                identifier=str(identifier),
                payload=career_payload,
                galaxy_index=galaxy_records,
            )
            name = career_payload.get("name") or str(identifier)
            imported_names.append(str(name).strip())
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
