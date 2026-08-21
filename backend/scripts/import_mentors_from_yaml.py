"""Import mentors (职业导师) data from a YAML file.

Usage examples:
  uv run python scripts/import_mentors_from_yaml.py
  uv run python scripts/import_mentors_from_yaml.py --yaml-path assets/mentors.yaml

YAML format (assets/mentors.yaml):

mentors:
  - name: 陈教授
    avatar_url: /static/avatars/chen.png
    profession: 资深前端架构师
    company: 阿里巴巴
    fee_per_hour: 399
    rating: 4.9
    rating_count: 128
    skills: [前端架构, React, 性能优化, 工程化]
    domains: [frontend]

Notes:
- Upsert mentors by the natural key (name, profession, company) to avoid duplicates across companies.
- Sync skills and domain mappings: add missing and remove extra ones not present in YAML (idempotent).
- Domains are ensured by slug; if slug unknown, a record will be created with name = slug.
"""

from __future__ import annotations

import argparse
import asyncio
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

import yaml
from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

ROOT_PATH = Path(__file__).resolve().parents[1]
if str(ROOT_PATH) not in sys.path:
    sys.path.insert(0, str(ROOT_PATH))

from app.core.logger import logger  # noqa: E402
from app.core.sql import async_session_maker  # noqa: E402
from app.models.mentors import (  # noqa: E402
    CommunityMentor,
    CommunityMentorSkill,
    MentorDomain,
    MentorDomainMap,
)

# Default domain slug -> display name mapping
DEFAULT_DOMAIN_NAMES: Dict[str, str] = {
    "frontend": "前端开发",
    "backend": "后端开发",
    "mobile": "移动开发",
    "product": "产品管理",
    "design": "设计创意",
    "data": "数据分析",
    "ai": "人工智能",
    "marketing": "市场营销",
    "operation": "运营管理",
    "devops": "DevOps",
    "qa": "测试工程",
}


def _norm_skill(s: str) -> str:
    return (s or "").strip().lower()


def load_yaml(path: Path) -> Dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(f"YAML 文件不存在: {path}")
    with path.open("r", encoding="utf-8") as fp:
        data = yaml.safe_load(fp)
    if not isinstance(data, dict):
        raise ValueError("mentors.yaml 的根节点必须是一个字典对象")
    return data


async def ensure_domain(session: AsyncSession, *, slug: str) -> MentorDomain:
    """Ensure a domain exists by slug; create it if missing."""
    res = await session.execute(select(MentorDomain).where(MentorDomain.slug == slug))
    obj = res.scalars().first()
    if obj:
        return obj
    # create with display name from defaults, fallback to slug
    name = DEFAULT_DOMAIN_NAMES.get(slug, slug)
    # order: use position in defaults if present, else a high number
    try:
        order = list(DEFAULT_DOMAIN_NAMES.keys()).index(slug) + 1
    except ValueError:
        order = 999
    obj = MentorDomain(slug=slug, name=name, order=order)
    session.add(obj)
    await session.flush()
    logger.info("创建导师领域: %s(%s)", name, slug)
    return obj


async def upsert_mentor(
    session: AsyncSession,
    *,
    name: str,
    profession: str,
    company: Optional[str],
    avatar_url: Optional[str],
    fee_per_hour: Optional[int],
    rating: Optional[float],
    rating_count: Optional[int],
) -> CommunityMentor:
    """Upsert mentor by (name, profession, company)."""
    stmt = select(CommunityMentor).where(
        and_(
            CommunityMentor.name == name,
            CommunityMentor.profession == profession,
            CommunityMentor.company.is_(None) if company is None else CommunityMentor.company == company,
        )
    )
    res = await session.execute(stmt)
    obj = res.scalars().first()
    if obj:
        obj.avatar_url = avatar_url
        if isinstance(fee_per_hour, int):
            obj.fee_per_hour = max(0, fee_per_hour)
        if isinstance(rating, (int, float)):
            obj.rating = float(rating)
        if isinstance(rating_count, int):
            obj.rating_count = max(0, rating_count)
        await session.flush()
        logger.info("更新导师: %s (%s%s)", name, profession, f" @ {company}" if company else "")
        return obj

    obj = CommunityMentor(
        name=name,
        profession=profession,
        company=company,
        avatar_url=avatar_url,
        fee_per_hour=max(0, int(fee_per_hour or 0)),
        rating=float(rating or 0),
        rating_count=max(0, int(rating_count or 0)),
        is_active=True,
    )
    session.add(obj)
    await session.flush()
    logger.info("创建导师: %s (%s%s)", name, profession, f" @ {company}" if company else "")
    return obj


async def sync_skills(session: AsyncSession, *, mentor_id: int, skills: List[str]) -> None:
    """Sync mentor skills to match YAML exactly (add/remove)."""
    norm: Set[str] = {s for s in (_norm_skill(x) for x in skills) if s}
    rows = (
        (await session.execute(select(CommunityMentorSkill).where(CommunityMentorSkill.mentor_id == mentor_id)))
        .scalars()
        .all()
    )
    current = {r.skill for r in rows}

    to_add = norm - current
    to_del = current - norm

    for s in sorted(to_add):
        session.add(CommunityMentorSkill(mentor_id=mentor_id, skill=s))
    if to_del:
        del_rows = (
            (
                await session.execute(
                    select(CommunityMentorSkill).where(
                        CommunityMentorSkill.mentor_id == mentor_id,
                        CommunityMentorSkill.skill.in_(list(to_del)),
                    )
                )
            )
            .scalars()
            .all()
        )
        for r in del_rows:
            await session.delete(r)  # type: ignore[arg-type]

    if to_add or to_del:
        await session.flush()
        logger.info("同步导师技能: +%d -%d (mid=%s)", len(to_add), len(to_del), mentor_id)


async def sync_domains(session: AsyncSession, *, mentor_id: int, slugs: List[str]) -> None:
    """Sync mentor domains to match YAML exactly (add/remove).

    Unknown slugs will be created as domains.
    """
    norm = [s.strip().lower() for s in slugs if s and str(s).strip()]

    # Ensure all required domains exist, collect ids
    domain_rows: Dict[str, int] = {}
    for slug in norm:
        dom = await ensure_domain(session, slug=slug)
        domain_rows[slug] = dom.id

    existing_maps = (
        (await session.execute(select(MentorDomainMap).where(MentorDomainMap.mentor_id == mentor_id))).scalars().all()
    )
    current_ids = {m.domain_id for m in existing_maps}
    desired_ids = {domain_rows[slug] for slug in norm}

    to_add_ids = desired_ids - current_ids
    to_del_ids = current_ids - desired_ids

    for did in sorted(to_add_ids):
        session.add(MentorDomainMap(mentor_id=mentor_id, domain_id=did))
    if to_del_ids:
        del_rows = (
            (
                await session.execute(
                    select(MentorDomainMap).where(
                        MentorDomainMap.mentor_id == mentor_id,
                        MentorDomainMap.domain_id.in_(list(to_del_ids)),
                    )
                )
            )
            .scalars()
            .all()
        )
        for r in del_rows:
            await session.delete(r)  # type: ignore[arg-type]

    if to_add_ids or to_del_ids:
        await session.flush()
        logger.info("同步导师领域: +%d -%d (mid=%s)", len(to_add_ids), len(to_del_ids), mentor_id)


async def async_main(args: argparse.Namespace) -> None:
    yaml_path = Path(args.yaml_path)
    payload = load_yaml(yaml_path)

    items: List[Dict[str, Any]] = payload.get("mentors") or []
    if not isinstance(items, list):
        raise ValueError("mentors 字段必须是列表")

    async with async_session_maker() as session:
        for item in items:
            if not isinstance(item, dict):
                raise ValueError("mentors 列表中的元素必须是对象")
            name = str(item.get("name") or "").strip()
            profession = str(item.get("profession") or "").strip()
            company = str(item.get("company")).strip() if item.get("company") is not None else None
            if not name or not profession:
                raise ValueError("mentor 条目缺少 name 或 profession")

            avatar_url = item.get("avatar_url")
            fee_per_hour = item.get("fee_per_hour")
            rating = item.get("rating")
            rating_count = item.get("rating_count")
            skills = list(item.get("skills") or [])
            domains = list(item.get("domains") or [])

            mentor = await upsert_mentor(
                session,
                name=name,
                profession=profession,
                company=company,
                avatar_url=avatar_url,
                fee_per_hour=fee_per_hour,
                rating=rating,
                rating_count=rating_count,
            )
            await sync_skills(session, mentor_id=mentor.id, skills=skills)
            await sync_domains(session, mentor_id=mentor.id, slugs=domains)
        await session.commit()

    logger.info("职业导师导入完成 ✅")


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="从 YAML 导入职业导师数据到数据库")
    p.add_argument(
        "--yaml-path",
        type=str,
        default=str(ROOT_PATH / "assets" / "mentors.yaml"),
        help="导师配置文件路径 (默认为 assets/mentors.yaml)",
    )
    return p.parse_args()


def main() -> None:
    args = parse_args()
    asyncio.run(async_main(args))


if __name__ == "__main__":  # pragma: no cover
    main()
