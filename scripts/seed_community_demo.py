import asyncio
import sys
from pathlib import Path

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

ROOT_PATH = Path(__file__).resolve().parents[1]
if str(ROOT_PATH) not in sys.path:
    sys.path.insert(0, str(ROOT_PATH))

from app.core.sql import async_session_maker  # noqa: E402
from app.models.community import CommunityCategory, CommunityGroup  # noqa: E402


async def upsert_category(session: AsyncSession, slug: str, name: str, order: int) -> CommunityCategory:
    res = await session.execute(select(CommunityCategory).where(CommunityCategory.slug == slug))
    obj = res.scalars().first()
    if obj:
        obj.name = name
        obj.order = order
        await session.commit()
        return obj
    obj = CommunityCategory(slug=slug, name=name, order=order)
    session.add(obj)
    await session.commit()
    await session.refresh(obj)
    return obj


async def upsert_group(
    session: AsyncSession,
    *,
    title: str,
    summary: str,
    category_id: int,
    cover_url: str | None = None,
    owner_name: str | None = None,
    owner_avatar_url: str | None = None,
    rules: list[str] | None = None,
):
    import json as _json

    res = await session.execute(select(CommunityGroup).where(CommunityGroup.title == title))
    existing_group = res.scalars().first()
    if existing_group:
        existing_group.summary = summary
        existing_group.category_id = category_id
        existing_group.cover_url = cover_url
        existing_group.owner_name = owner_name
        existing_group.owner_avatar_url = owner_avatar_url
        if rules is not None:
            existing_group.rules_json = _json.dumps(rules, ensure_ascii=False)
        await session.commit()
        return existing_group

    new_group = CommunityGroup(
        title=title,
        summary=summary,
        category_id=category_id,
        cover_url=cover_url,
        owner_name=owner_name,
        owner_avatar_url=owner_avatar_url,
        rules_json=_json.dumps(rules or [], ensure_ascii=False),
    )
    session.add(new_group)
    await session.commit()
    return new_group


async def main():
    async with async_session_maker() as session:
        cats = [
            ("all", "全部", 0),
            ("frontend", "前端", 1),
            ("product", "产品", 2),
            ("design", "设计", 3),
            ("backend", "后端", 4),
            ("data", "数据", 5),
            ("ai", "AI", 6),
        ]
        created = {}
        for slug, name, order in cats:
            created[slug] = await upsert_category(session, slug, name, order)

        await upsert_group(
            session,
            title="前端开发学习小组",
            summary="专注于前端技术学习与交流，包括HTML、CSS、JavaScript、React等",
            category_id=created["frontend"].id,
            owner_name="前端组长",
            owner_avatar_url="/static/avatars/fe_lead.png",
            rules=["互相尊重，友善交流", "提问请提供复现或截图", "避免广告与灌水"],
        )
        await upsert_group(
            session,
            title="产品经理实战圈",
            summary="分享产品管理工作经验，学习产品设计与用户体验知识",
            category_id=created["product"].id,
            owner_name="产品主理人",
            owner_avatar_url="/static/avatars/pm_owner.png",
            rules=["聚焦产品话题", "尊重不同观点", "注意保密与合规"],
        )
        await upsert_group(
            session,
            title="UI/UX设计交流群",
            summary="探讨界面设计与用户体验，分享设计资源和创作思路",
            category_id=created["design"].id,
            owner_name="设计猫",
            owner_avatar_url="/static/avatars/design_cat.png",
            rules=["作品请标注来源", "禁止盗图与抄袭", "鼓励点评与改进建议"],
        )
        await upsert_group(
            session,
            title="后端技术研讨组",
            summary="深入后端架构、数据库与微服务实践",
            category_id=created["backend"].id,
            owner_name="后端侠",
            owner_avatar_url="/static/avatars/be_hero.png",
            rules=["严禁发布攻击性内容", "代码示例注意脱敏", "技术为先，少水多干货"],
        )
        await upsert_group(
            session,
            title="数据分析与可视化",
            summary="从入门到进阶，掌握数据分析方法与可视化技巧",
            category_id=created["data"].id,
            owner_name="数据达人",
            owner_avatar_url="/static/avatars/data_guru.png",
            rules=["欢迎分享数据集", "禁止传播隐私数据", "图表请标注图例与单位"],
        )
        print("✔️  Seeded community demo data")


if __name__ == "__main__":
    asyncio.run(main())
