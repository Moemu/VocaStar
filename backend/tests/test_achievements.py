from __future__ import annotations

from datetime import datetime, timedelta

import pytest
from sqlalchemy import select

from app.models.extensions import (
    ExplorationProgress,
    PointTransaction,
    UserAchievement,
    UserPoints,
)
from app.models.partners import CommunityPartner


@pytest.mark.asyncio
async def test_first_exploration_award(student_client, database, test_user, sample_careers):
    # 前置：确保成就配置存在（若种子已执行则忽略）
    await student_client.get("/api/profile/achievements")

    # 1) 未满进度不授予
    database.add(ExplorationProgress(user_id=test_user.id, career_id=sample_careers[0].id, explored_blocks=3))
    await database.commit()

    resp0 = await student_client.post(
        "/api/profile/explorations",
        json={"items": [{"career_id": sample_careers[0].id, "explored_blocks": 3}]},
    )
    assert resp0.status_code == 200

    rows0 = (
        (await database.execute(select(UserAchievement).where(UserAchievement.user_id == test_user.id))).scalars().all()
    )
    assert len(rows0) == 0

    # 2) 满进度后授予
    resp = await student_client.post(
        "/api/profile/explorations",
        json={"items": [{"career_id": sample_careers[0].id, "explored_blocks": 4}]},
    )
    assert resp.status_code == 200

    rows = (
        (await database.execute(select(UserAchievement).where(UserAchievement.user_id == test_user.id))).scalars().all()
    )
    assert len(rows) == 1


@pytest.mark.asyncio
async def test_partner_bind_award(student_client, database, test_user):
    await student_client.get("/api/profile/achievements")

    # 插入 3 个伙伴并绑定
    for i in range(3):
        p = CommunityPartner(name=f"p{i}", profession="dev")
        database.add(p)
        await database.flush()
        await database.refresh(p)
        res = await student_client.post(f"/api/community/partners/{p.id}/bind")
        assert res.status_code == 200

    rows = (
        (await database.execute(select(UserAchievement).where(UserAchievement.user_id == test_user.id))).scalars().all()
    )
    assert len(rows) >= 1


@pytest.mark.asyncio
async def test_signin_streak_award(student_client, database, test_user):
    await student_client.get("/api/profile/achievements")

    # 构造用户积分账户并插入最近 6 天签到（今天不含）
    up = UserPoints(user_id=test_user.id, points=0)
    database.add(up)
    await database.flush()
    base = datetime.utcnow().replace(hour=9, minute=0, second=0, microsecond=0)
    for d in range(1, 7):
        database.add(
            PointTransaction(user_points_id=up.id, amount=50, reason="每日签到", created_at=base - timedelta(days=d))
        )
    await database.commit()

    # 触发当天签到（通过首页）
    res = await student_client.get("/api/home/summary")
    assert res.status_code == 200

    rows = (
        (await database.execute(select(UserAchievement).where(UserAchievement.user_id == test_user.id))).scalars().all()
    )
    assert len(rows) >= 1
