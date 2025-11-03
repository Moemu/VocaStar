"""Seed a small set of fake members for each community group (方案二：少量“逼真”成员+真实关系).

This script creates (or reuses) demo users and adds them to each community group
until a per-group target is reached. It is idempotent and safe to run multiple times.

Usage examples:
  uv run python scripts/seed_fake_members.py
  uv run python scripts/seed_fake_members.py --per-group 20 --prefix demo --domain demo.invalid --password 12345678

Notes:
- A leader membership will be ensured for each group (role=leader). The leader user
  uses a deterministic username: "{prefix}_leader_{group_id}" and nickname from
  group.owner_name if available.
- Member usernames follow: "{prefix}_{group_id}_{index:02d}".
- Avatar URLs rotate through a small set of placeholders under /static/avatars.
- The script only adds missing users/members to reach the target; it will not remove.
"""

from __future__ import annotations

import argparse
import asyncio
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

ROOT_PATH = Path(__file__).resolve().parents[1]
if str(ROOT_PATH) not in sys.path:
    sys.path.insert(0, str(ROOT_PATH))

from app.core.logger import logger  # noqa: E402
from app.core.sql import async_session_maker  # noqa: E402
from app.models.community import CommunityGroup, CommunityGroupMember  # noqa: E402
from app.models.user import User, UserRole  # noqa: E402
from app.services.auth_service import get_password_hash  # noqa: E402

AVATAR_POOL = [
    "/static/placeholders/placeholder_01.png",
    "/static/placeholders/placeholder_02.png",
    "/static/placeholders/placeholder_03.png",
    "/static/placeholders/placeholder_04.png",
    "/static/placeholders/placeholder_05.png",
    "/static/placeholders/placeholder_06.png",
    "/static/placeholders/placeholder_07.png",
    "/static/placeholders/placeholder_08.png",
    "/static/placeholders/placeholder_09.png",
    "/static/placeholders/placeholder_10.png",
]

# ---------------- internal nickname pool helpers ----------------


class NicknamePool:
    def __init__(self, path: Optional[str] = None):
        self.nicknames: List[str] = []
        self._load_nicknames(path)

    def _load_nicknames(self, path: Optional[str]) -> None:
        candidates: List[str] = []
        if path:
            p = Path(path)
            if p.exists():
                try:
                    text = p.read_text(encoding="utf-8")
                    for line in text.splitlines():
                        s = line.strip()
                        if not s or s.startswith("#"):
                            continue
                        candidates.append(s)
                except (IOError, UnicodeDecodeError) as e:
                    logger.warning(f"读取昵称文件失败: {e}")
        # fallback defaults if empty
        if not candidates:
            candidates = [
                "晓风残月",
                "代码旅人",
                "产品小白",
                "设计喵",
                "后端工程狮",
                "数据小能手",
                "AI学习者",
                "前端小太阳",
                "运营星海",
                "测试大王",
                "算法菜鸟",
                "UI练习生",
                "需求分析官",
                "云端行者",
                "微服务爱好者",
                "容器搬运工",
                "日志观察员",
                "SQL匠人",
                "接口达人",
                "Bug制造机",
            ]
        self.nicknames = candidates

    def next_nickname(self, group_id: int, idx: int) -> str:
        if not self.nicknames:
            return f"demo_{group_id}_{idx:02d}"
        pos = (group_id + idx) % len(self.nicknames)
        return self.nicknames[pos]


@dataclass
class Settings:
    per_group: int = 20
    prefix: str = "demo"
    domain: str = "demo.invalid"
    password: str = "12345678"
    nicknames_path: Optional[str] = None


async def ensure_user(
    session: AsyncSession,
    *,
    username: str,
    email: str,
    password: str,
    nickname: Optional[str] = None,
    avatar_url: Optional[str] = None,
) -> User:
    """Get or create a user with given identity (idempotent)."""
    res = await session.execute(select(User).where(User.username == username))
    u = res.scalars().first()
    if u:
        return u
    u = User(
        username=username,
        email=email,
        password_hash=get_password_hash(password),
        role=UserRole.user,
        is_active=True,
        nickname=nickname or username,
        avatar_url=avatar_url,
    )
    session.add(u)
    await session.flush()
    logger.debug("创建用户: %s", username)
    return u


async def has_leader(session: AsyncSession, group_id: int) -> bool:
    stmt = select(func.count(CommunityGroupMember.id)).where(
        CommunityGroupMember.group_id == group_id, CommunityGroupMember.role == "leader"
    )
    return bool((await session.execute(stmt)).scalar())


async def ensure_leader_for_group(
    session: AsyncSession, group: CommunityGroup, settings: Settings, nickname_pool: Optional[NicknamePool] = None
) -> None:
    """确保小组存在一位组长，并在缺失时回填 group.owner_* 字段。

    行为：
      - 若已存在 leader，则直接读取该用户；否则创建 demo leader 并建立成员关系
      - 若 group.owner_name/owner_avatar_url 为空，则从 leader 用户回填
    """
    leader_user: Optional[User] = None

    # 尝试获取已存在的 leader 成员
    res = await session.execute(
        select(CommunityGroupMember.user_id)
        .where(CommunityGroupMember.group_id == group.id, CommunityGroupMember.role == "leader")
        .order_by(CommunityGroupMember.joined_at.asc())
        .limit(1)
    )
    row = res.first()

    if row:
        # 读取已存在 leader 对应的用户
        leader_user = (await session.execute(select(User).where(User.id == row[0]))).scalars().first()
    else:
        # 创建 leader 用户并建立关系
        username = f"{settings.prefix}_leader_{group.id}"
        email = f"{username}@{settings.domain}"
        avatar = AVATAR_POOL[group.id % len(AVATAR_POOL)]
        nickname = group.owner_name
        if not nickname:
            if nickname_pool:
                nickname = nickname_pool.next_nickname(group.id, 0)
            else:
                nickname = f"demo_leader_{group.id}"
        leader_user = await ensure_user(
            session,
            username=username,
            email=email,
            password=settings.password,
            nickname=nickname,
            avatar_url=avatar,
        )
        rel = await session.execute(
            select(CommunityGroupMember).where(
                CommunityGroupMember.group_id == group.id, CommunityGroupMember.user_id == leader_user.id
            )
        )
        if not rel.scalars().first():
            session.add(CommunityGroupMember(group_id=group.id, user_id=leader_user.id, role="leader"))
            logger.info("为小组 %s 添加组长: %s", group.title, username)

    # 回填 owner 字段（如缺失）
    if leader_user is not None:
        updated = False
        display_name = leader_user.nickname or leader_user.username
        if not group.owner_name:
            group.owner_name = display_name
            updated = True
        if not group.owner_avatar_url and getattr(leader_user, "avatar_url", None):
            group.owner_avatar_url = leader_user.avatar_url
            updated = True
        if updated:
            logger.info("回填小组 %s 的 owner 信息为: %s", group.title, display_name)

    await session.flush()


async def count_members(session: AsyncSession, group_id: int) -> int:
    stmt = select(func.count(CommunityGroupMember.id)).where(CommunityGroupMember.group_id == group_id)
    return int((await session.execute(stmt)).scalar() or 0)


async def fill_members_for_group(
    session: AsyncSession, group: CommunityGroup, settings: Settings, nickname_pool: NicknamePool
) -> None:
    # Ensure leader first
    await ensure_leader_for_group(session, group, settings, nickname_pool)
    await session.flush()  # Ensure any new leader is committed before counting
    current = await count_members(session, group.id)
    target = max(1, settings.per_group)  # include leader in target
    need = max(0, target - current)
    if need <= 0:
        logger.info("小组 %s 已有成员 %d >= 目标 %d，跳过补齐", group.title, current, target)
        return

    # deterministic usernames per group
    # start index from existing count to avoid collisions; but we ensure uniqueness by probing
    created = 0
    idx = 1
    while created < need:
        username = f"{settings.prefix}_{group.id}_{idx:02d}"
        email = f"{username}@{settings.domain}"
        avatar = AVATAR_POOL[(group.id + idx) % len(AVATAR_POOL)]
        user = await ensure_user(
            session,
            username=username,
            email=email,
            password=settings.password,
            nickname=nickname_pool.next_nickname(group.id, idx),
            avatar_url=avatar,
        )
        # try insert membership as member
        res = await session.execute(
            select(CommunityGroupMember).where(
                CommunityGroupMember.group_id == group.id, CommunityGroupMember.user_id == user.id
            )
        )
        if not res.scalars().first():
            session.add(CommunityGroupMember(group_id=group.id, user_id=user.id, role="member"))
            created += 1
        idx += 1
    logger.info("小组 %s 补充成员 %d 人，现有 %d -> 目标 %d (提交后生效)", group.title, created, current, target)


async def async_main(args: argparse.Namespace) -> None:
    settings = Settings(
        per_group=int(args.per_group),
        prefix=str(args.prefix),
        domain=str(args.domain),
        password=str(args.password),
        nicknames_path=str(args.nicknames_path) if args.nicknames_path else None,
    )

    # instantiate nickname pool for this run
    nickname_pool = NicknamePool(settings.nicknames_path)

    async with async_session_maker() as session:
        # fetch all groups
        res = await session.execute(select(CommunityGroup))
        groups = res.scalars().all()
        if not groups:
            logger.warning("未找到任何小组，请先导入 groups.yaml 或运行种子脚本")
            return

        for g in groups:
            await fill_members_for_group(session, g, settings, nickname_pool)
        await session.commit()

    logger.info("✅ 已为 %d 个小组补齐演示成员", len(groups))


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="为每个学习小组补齐演示成员（真实用户+成员关系）")
    p.add_argument("--per-group", type=int, default=20, help="每个小组的目标演示成员数（包含组长），默认 20")
    p.add_argument("--prefix", type=str, default="demo", help="演示用户的用户名/昵称前缀，默认 demo")
    p.add_argument("--domain", type=str, default="demo.invalid", help="演示用户邮箱域，默认 demo.invalid")
    p.add_argument("--password", type=str, default="12345678", help="演示用户初始密码，默认 12345678")
    p.add_argument(
        "--nicknames-path",
        type=str,
        default=str(ROOT_PATH / "assets" / "nicknames.txt"),
        help="昵称列表文件路径（每行一个昵称），默认 assets/nicknames.txt",
    )
    return p.parse_args()


def main() -> None:
    args = parse_args()
    asyncio.run(async_main(args))


if __name__ == "__main__":  # pragma: no cover
    main()
