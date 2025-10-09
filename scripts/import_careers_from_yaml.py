"""Utility script to import career definitions from a YAML file into the database.

Usage examples
--------------
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
from app.models.career import Career  # noqa: E402

CAREERS_SECTION_KEY = "careers"


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


async def upsert_career(
    session: AsyncSession,
    *,
    identifier: str,
    payload: Mapping[str, Any],
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
        created_count = 0
        updated_count = 0
        imported_names: list[str] = []

        for identifier, career_payload in careers_section.items():
            if not isinstance(career_payload, Mapping):
                raise ValueError(f"职业节点 {identifier!r} 必须是对象")
            created = await upsert_career(session, identifier=str(identifier), payload=career_payload)
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
        "职业导入已完成 ✅ 新增 %d 条，更新 %d 条，删除 %d 条 (YAML: %s)",
        created_count,
        updated_count,
        removed,
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
