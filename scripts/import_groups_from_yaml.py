"""Import community groups from a YAML file into the database.

Usage examples:
  uv run python scripts/import_groups_from_yaml.py
  uv run python scripts/import_groups_from_yaml.py --yaml-path assets/groups.yaml --force

YAML format (assets/groups.yaml):

  groups:
    - title: 前端开发学习小组
      summary: ...
      cover_url: /static/groups/frontend.webp
      owner_name: 张小明
      owner_avatar_url: /static/groups/xxx.webp
      rules_json: ["rule1", "rule2"]
      category: 前端   # 支持中文名或 slug(frontend/product/design/backend/data/ai)
      members_count: 128
      last_activity_at: "2025.11.03 09:22:26"  # 可选

"""

from __future__ import annotations

import argparse
import asyncio
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

ROOT_PATH = Path(__file__).resolve().parents[1]
if str(ROOT_PATH) not in sys.path:
    sys.path.insert(0, str(ROOT_PATH))

from app.core.logger import logger  # noqa: E402
from app.core.sql import async_session_maker  # noqa: E402
from app.models.community import CommunityCategory, CommunityGroup  # noqa: E402

# Map display name -> slug
CATEGORY_SLUG_MAP: Dict[str, str] = {
    "全部": "all",
    "前端": "frontend",
    "产品": "product",
    "设计": "design",
    "后端": "backend",
    "数据": "data",
    "AI": "ai",
}


def load_yaml(path: Path) -> Dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(f"YAML 文件不存在: {path}")
    with path.open("r", encoding="utf-8") as fp:
        data = yaml.safe_load(fp)
    if not isinstance(data, dict):
        raise ValueError("groups.yaml 的根节点必须是一个字典对象")
    return data


async def upsert_category(session: AsyncSession, *, slug_or_name: str) -> CommunityCategory:
    """Find category by slug or display name; create if not exists (with best-effort name)."""
    slug = CATEGORY_SLUG_MAP.get(slug_or_name, slug_or_name)

    # Try by slug
    res = await session.execute(select(CommunityCategory).where(CommunityCategory.slug == slug))
    obj = res.scalars().first()
    if obj:
        return obj

    # Try by display name
    res = await session.execute(select(CommunityCategory).where(CommunityCategory.name == slug_or_name))
    obj = res.scalars().first()
    if obj:
        return obj

    # Create new with name fallback
    name = next((k for k, v in CATEGORY_SLUG_MAP.items() if v == slug), slug_or_name)
    obj = CommunityCategory(slug=slug, name=name, order=0)
    session.add(obj)
    await session.commit()
    await session.refresh(obj)
    logger.info("创建新分类: %s(%s)", name, slug)
    return obj


def parse_dt(value: Optional[str]) -> Optional[datetime]:
    if not value:
        return None
    for fmt in ("%Y.%m.%d %H:%M:%S", "%Y-%m-%d %H:%M:%S", "%Y/%m/%d %H:%M:%S"):
        try:
            return datetime.strptime(value, fmt)
        except ValueError as e:
            logger.debug("解析日期格式失败: %s 格式: %s 错误: %s", value, fmt, e)
            continue
    logger.warning("last_activity_at 无法解析: %s", value)
    return None


async def upsert_group(
    session: AsyncSession,
    *,
    item: Dict[str, Any],
) -> CommunityGroup:
    title = item.get("title")
    if not title:
        raise ValueError("group 条目缺少 title")

    summary = item.get("summary") or ""
    cover_url = item.get("cover_url")
    owner_name = item.get("owner_name")
    owner_avatar_url = item.get("owner_avatar_url")
    rules = item.get("rules_json") or []
    category_raw = item.get("category")
    members_count = item.get("members_count")
    last_activity_at = parse_dt(item.get("last_activity_at"))

    if not category_raw:
        raise ValueError(f"group {title!r} 缺少 category")

    category = await upsert_category(session, slug_or_name=str(category_raw))

    # find group by title
    res = await session.execute(select(CommunityGroup).where(CommunityGroup.title == title))
    g = res.scalars().first()
    if g:
        g.summary = summary
        g.category_id = category.id
        g.cover_url = cover_url
        g.owner_name = owner_name
        try:
            g.rules_json = json.dumps(rules, ensure_ascii=False) if isinstance(rules, list) else str(rules)
        except TypeError as e:
            logger.error("JSON 序列化失败: %s, rules_json: %r", e, rules)
            g.rules_json = None
        except Exception as e:
            logger.error("未知错误序列化 rules_json: %s, rules_json: %r", e, rules)
            g.rules_json = None
        if isinstance(members_count, int):
            g.members_count = members_count
        if last_activity_at is not None:
            g.last_activity_at = last_activity_at
        await session.flush()
        logger.info("更新小组: %s", title)
        return g

    g = CommunityGroup(
        title=title,
        summary=summary,
        category_id=category.id,
        cover_url=cover_url,
        owner_name=owner_name,
        owner_avatar_url=owner_avatar_url,
        rules_json=json.dumps(rules, ensure_ascii=False) if isinstance(rules, list) else None,
    )
    if isinstance(members_count, int):
        g.members_count = members_count
    if last_activity_at is not None:
        g.last_activity_at = last_activity_at
    session.add(g)
    await session.flush()
    logger.info("创建小组: %s", title)
    return g


async def async_main(args: argparse.Namespace) -> None:
    yaml_path = Path(args.yaml_path)
    payload = load_yaml(yaml_path)

    items: List[Dict[str, Any]] = payload.get("groups") or []
    if not isinstance(items, list):
        raise ValueError("groups 字段必须是列表")

    async with async_session_maker() as session:
        for item in items:
            if not isinstance(item, dict):
                raise ValueError("groups 列表中的元素必须是对象")
            await upsert_group(session, item=item)
        await session.commit()

    logger.info("学习小组导入完成 ✅")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="从 YAML 导入学习小组到数据库")
    parser.add_argument(
        "--yaml-path",
        type=str,
        default=str(ROOT_PATH / "assets" / "groups.yaml"),
        help="小组配置文件路径 (默认为 assets/groups.yaml)",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    asyncio.run(async_main(args))


if __name__ == "__main__":  # pragma: no cover
    main()
