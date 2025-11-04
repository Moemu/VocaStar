"""Import community partners (职业伙伴) data from a YAML file.

Usage examples:
  uv run python scripts/import_partners_from_yaml.py
  uv run python scripts/import_partners_from_yaml.py --yaml-path assets/partners.yaml --apply-bindings

YAML format (assets/partners.yaml):

partners:
  - name: Ada
    avatar_url: /static/avatars/ada.png
    profession: 数据分析师
    learning_progress: 60          # 可选，默认 0
    popularity: 12                 # 可选，默认 0
    skills: [sql, pandas, tableau] # 可选，列表元素将会规范化为小写
    # 可选：若提供并开启 --apply-bindings，将为这些用户名创建绑定关系（幂等）
    bindings: [demo_user_1, demo_user_2]

Notes:
- Upsert by (name, profession) 作为“自然唯一键”：若存在则更新字段，否则创建。
- Skills 对该伙伴执行“同步”：新增缺失的技能，并移除 YAML 中不存在的技能标签。
- Bindings 需要通过参数 --apply-bindings 显式启用；仅对已存在的用户生效。
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
from app.models.partners import (  # noqa: E402
    CommunityPartner,
    CommunityPartnerSkill,
    UserPartnerBinding,
)
from app.models.user import User  # noqa: E402


def _norm_skill(s: str) -> str:
    return (s or "").strip().lower()


def load_yaml(path: Path) -> Dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(f"YAML 文件不存在: {path}")
    with path.open("r", encoding="utf-8") as fp:
        data = yaml.safe_load(fp)
    if not isinstance(data, dict):
        raise ValueError("partners.yaml 的根节点必须是一个字典对象")
    return data


async def upsert_partner(
    session: AsyncSession,
    *,
    name: str,
    profession: str,
    avatar_url: Optional[str],
    learning_progress: Optional[int],
    popularity: Optional[int],
) -> CommunityPartner:
    """按 (name, profession) 查找或创建伙伴，并更新基础字段。"""
    stmt = select(CommunityPartner).where(
        and_(CommunityPartner.name == name, CommunityPartner.profession == profession)
    )
    res = await session.execute(stmt)
    obj = res.scalars().first()
    if obj:
        obj.avatar_url = avatar_url
        obj.learning_progress = max(0, min(100, int(learning_progress or 0)))
        obj.popularity = max(0, int(popularity or 0))
        await session.flush()
        logger.info("更新伙伴: %s (%s)", name, profession)
        return obj

    obj = CommunityPartner(
        name=name,
        profession=profession,
        avatar_url=avatar_url,
        learning_progress=max(0, min(100, int(learning_progress or 0))),
        popularity=max(0, int(popularity or 0)),
    )
    session.add(obj)
    await session.flush()
    logger.info("创建伙伴: %s (%s)", name, profession)
    return obj


async def sync_partner_skills(session: AsyncSession, *, partner_id: int, skills: List[str]) -> None:
    """将伙伴技能与 YAML 对齐：新增缺失、移除多余（幂等）。"""
    norm: Set[str] = {_norm_skill(x) for x in skills if _norm_skill(x)}
    # 读取当前技能
    rows = (
        (await session.execute(select(CommunityPartnerSkill).where(CommunityPartnerSkill.partner_id == partner_id)))
        .scalars()
        .all()
    )
    current = {r.skill for r in rows}

    to_add = norm - current
    to_del = current - norm

    for s in sorted(to_add):
        session.add(CommunityPartnerSkill(partner_id=partner_id, skill=s))
    if to_del:
        # 批量删除
        from sqlalchemy import delete

        del_stmt = delete(CommunityPartnerSkill).where(
            and_(
                CommunityPartnerSkill.partner_id == partner_id,
                CommunityPartnerSkill.skill.in_(list(to_del)),
            )
        )
        await session.execute(del_stmt)

    if to_add or to_del:
        await session.flush()
        logger.info("同步技能: +%d -%d (pid=%s)", len(to_add), len(to_del), partner_id)


async def ensure_bindings(session: AsyncSession, *, partner_id: int, usernames: List[str]) -> None:
    """为伙伴创建与用户的绑定关系（幂等）。仅对存在的用户生效。"""
    if not usernames:
        return
    # 读现有绑定，避免重复
    bound_stmt = select(UserPartnerBinding).where(UserPartnerBinding.partner_id == partner_id)
    current_users = {b.user_id for b in (await session.execute(bound_stmt)).scalars().all()}

    # 查用户 id
    users = (await session.execute(select(User).where(User.username.in_(list(set(usernames)))))).scalars().all()
    to_add = [u for u in users if u.id not in current_users]
    for u in to_add:
        session.add(UserPartnerBinding(user_id=u.id, partner_id=partner_id))
    if to_add:
        await session.flush()
        logger.info("新增绑定 %d 条 (pid=%s)", len(to_add), partner_id)


async def async_main(args: argparse.Namespace) -> None:
    yaml_path = Path(args.yaml_path)
    payload = load_yaml(yaml_path)

    items: List[Dict[str, Any]] = payload.get("partners") or []
    if not isinstance(items, list):
        raise ValueError("partners 字段必须是列表")

    async with async_session_maker() as session:
        for item in items:
            if not isinstance(item, dict):
                raise ValueError("partners 列表中的元素必须是对象")
            name = str(item.get("name") or "").strip()
            profession = str(item.get("profession") or "").strip()
            if not name or not profession:
                raise ValueError("partner 条目缺少 name 或 profession")

            avatar_url = item.get("avatar_url")
            learning_progress = item.get("learning_progress")
            popularity = item.get("popularity")
            skills = item.get("skills") or []
            bindings = item.get("bindings") or []

            partner = await upsert_partner(
                session,
                name=name,
                profession=profession,
                avatar_url=avatar_url,
                learning_progress=learning_progress,
                popularity=popularity,
            )
            await sync_partner_skills(session, partner_id=partner.id, skills=list(skills))

            if args.apply_bindings and bindings:
                await ensure_bindings(session, partner_id=partner.id, usernames=list(bindings))
        await session.commit()

    logger.info("职业伙伴导入完成 ✅")


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="从 YAML 导入职业伙伴数据到数据库")
    p.add_argument(
        "--yaml-path",
        type=str,
        default=str(ROOT_PATH / "assets" / "partners.yaml"),
        help="伙伴配置文件路径 (默认为 assets/partners.yaml)",
    )
    p.add_argument(
        "--apply-bindings",
        action="store_true",
        help="为 YAML 中提供的 bindings（用户名列表）创建绑定关系（幂等）",
    )
    return p.parse_args()


def main() -> None:
    args = parse_args()
    asyncio.run(async_main(args))


if __name__ == "__main__":  # pragma: no cover
    main()
