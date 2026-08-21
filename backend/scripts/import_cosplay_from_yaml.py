"""Utility script to import cosplay scripts from a YAML file into the database.

Usage examples
--------------
默认使用 ``assets/cosplay.yaml``::

    uv run python scripts/import_cosplay_from_yaml.py

指定 YAML 文件::

    uv run python scripts/import_cosplay_from_yaml.py --yaml-path path/to/file.yaml
"""

from __future__ import annotations

import argparse
import asyncio
import sys
from pathlib import Path
from typing import Any, Mapping

import yaml
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

ROOT_PATH = Path(__file__).resolve().parents[1]
if str(ROOT_PATH) not in sys.path:
    sys.path.insert(0, str(ROOT_PATH))

from app.core.logger import logger  # noqa: E402
from app.core.sql import async_session_maker  # noqa: E402
from app.models.career import Career  # noqa: E402
from app.models.cosplay import CosplayScript  # noqa: E402
from app.schemas.cosplay import CosplayScriptContent  # noqa: E402

DEFAULT_BASE_SCORE = 50

SCRIPTS_SECTION_KEY = "scripts"


def load_yaml(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(f"YAML 文件不存在: {path}")
    with path.open("r", encoding="utf-8") as fp:
        payload = yaml.safe_load(fp)
    if not isinstance(payload, Mapping):
        raise ValueError("cosplay 配置文件的根节点必须是对象")
    return dict(payload)


def _coerce_legacy_content(data: dict[str, Any]) -> dict[str, Any]:
    """将旧版/不规范的剧本内容转换为当前 schema 期望的结构。

    - scenes: 允许 list，转换为以 id 为键的 dict
    - option.description -> option.outcome
    - 缺失 effects 则补 {}
    - 缺失 initial_scores：按 abilities + base_score 生成
    - 缺失 evaluations/abilities：补空列表
    - 缺失 is_end：False
    """
    from copy import deepcopy

    payload = deepcopy(data)

    scenes = payload.get("scenes")
    if isinstance(scenes, list):
        scenes_dict: dict[str, Any] = {}
        for scene in scenes:
            if not isinstance(scene, dict):
                continue
            sid = scene.get("id")
            if not sid:
                continue
            opts = []
            for opt in scene.get("options", []) or []:
                if not isinstance(opt, dict):
                    continue
                outcome = opt.get("outcome")
                if outcome is None and "description" in opt:
                    outcome = opt.get("description")
                if outcome is None and "feedback" in opt:
                    outcome = opt.get("feedback")
                opts.append(
                    {
                        "id": opt.get("id"),
                        "text": opt.get("text"),
                        "outcome": outcome or "",
                        "effects": opt.get("effects") or {},
                    }
                )
            scenes_dict[str(sid)] = {
                "id": scene.get("id"),
                "title": scene.get("title", ""),
                "text": scene.get("narrative", ""),
                "options": opts,
                "is_end": bool(scene.get("is_end", False)),
                # 透传扩展字段（用于错题本）：
                "correct_option_id": scene.get("correct_option_id"),
                "explanation": scene.get("explanation"),
            }
        payload["scenes"] = scenes_dict

    if "initial_scores" not in payload:
        abilities = payload.get("abilities") or []
        base = payload.get("base_score") or DEFAULT_BASE_SCORE
        init_scores: dict[str, int] = {}
        for ab in abilities:
            if isinstance(ab, dict) and ab.get("code"):
                init_scores[ab["code"]] = int(base)
        payload["initial_scores"] = init_scores

    if "evaluations" not in payload or payload.get("evaluations") is None:
        payload["evaluations"] = []

    if "abilities" not in payload or payload.get("abilities") is None:
        payload["abilities"] = []

    return payload


def normalize_script_payload(identifier: str, payload: Any) -> tuple[str, str, dict[str, Any]]:
    if not isinstance(payload, Mapping):
        raise ValueError(f"剧本节点 {identifier!r} 必须是对象")
    title_raw = payload.get("title")
    if not isinstance(title_raw, str) or not title_raw.strip():
        raise ValueError(f"剧本 {identifier!r} 缺少 title 字段")
    title = title_raw.strip()

    career_name_raw = payload.get("career_name")
    if not isinstance(career_name_raw, str) or not career_name_raw.strip():
        raise ValueError(f"剧本 {identifier!r} 缺少 career_name 字段")
    career_name = career_name_raw.strip()

    content_payload = {k: v for k, v in payload.items() if k not in {"title", "career_name"}}
    # 先尝试严格校验，不通过则进行一次兼容性规整后再校验
    try:
        CosplayScriptContent.model_validate(content_payload)
    except Exception:
        content_payload = _coerce_legacy_content(content_payload)
        CosplayScriptContent.model_validate(content_payload)
    return title, career_name, content_payload


async def upsert_script(
    session: AsyncSession,
    *,
    identifier: str,
    title: str,
    career_name: str,
    content_payload: dict[str, Any],
) -> tuple[bool, int]:
    stmt = select(Career).where(Career.name == career_name)
    result = await session.execute(stmt)
    career = result.scalars().first()
    if career is None:
        raise ValueError(f"未找到名称为 {career_name!r} 的职业，请先导入职业数据")

    stmt_script = select(CosplayScript).where(
        CosplayScript.career_id == career.id,
        CosplayScript.title == title,
    )
    result_script = await session.execute(stmt_script)
    script = result_script.scalars().first()
    created = False
    if script is None:
        script = CosplayScript(career_id=career.id, title=title, content=content_payload)
        session.add(script)
        created = True
    else:
        script.career_id = career.id
        script.title = title
        script.content = content_payload
    return created, career.id


async def purge_missing(session: AsyncSession, keep_titles: set[str], career_ids: set[int]) -> int:
    if not keep_titles:
        return 0
    stmt = delete(CosplayScript).where(
        CosplayScript.career_id.in_(career_ids),
        ~CosplayScript.title.in_(tuple(keep_titles)),
    )
    result = await session.execute(stmt)
    return result.rowcount or 0


async def async_main(args: argparse.Namespace) -> None:
    yaml_path = Path(args.yaml_path)
    payload = load_yaml(yaml_path)
    scripts_section = payload.get(SCRIPTS_SECTION_KEY, payload)
    if not isinstance(scripts_section, Mapping):
        raise ValueError("scripts 节点必须是对象")

    async with async_session_maker() as session:
        created = 0
        updated = 0
        keep_titles: set[str] = set()
        related_careers: set[int] = set()

        for identifier, script_payload in scripts_section.items():
            title, career_name, content_payload = normalize_script_payload(str(identifier), script_payload)
            keep_titles.add(title)
            is_created, career_id = await upsert_script(
                session,
                identifier=str(identifier),
                title=title,
                career_name=career_name,
                content_payload=content_payload,
            )
            if career_id is not None:
                related_careers.add(career_id)
            if is_created:
                created += 1
            else:
                updated += 1

        removed = 0
        if args.purge_missing and related_careers:
            removed = await purge_missing(session, keep_titles, related_careers)

        await session.commit()

    logger.info(
        "Cosplay 导入完成 ✅ 新增 %d 条，更新 %d 条，删除 %d 条 (YAML: %s)",
        created,
        updated,
        removed,
        yaml_path,
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="导入 YAML Cosplay 配置到数据库")
    parser.add_argument(
        "--yaml-path",
        type=str,
        default=str(Path("assets") / "cosplay.yaml"),
        help="Cosplay 配置文件路径 (默认为 assets/cosplay.yaml)",
    )
    parser.add_argument(
        "--purge-missing",
        action="store_true",
        help="删除数据库中未出现在 YAML 中的剧本 (谨慎使用)",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    asyncio.run(async_main(args))


if __name__ == "__main__":  # pragma: no cover
    main()
