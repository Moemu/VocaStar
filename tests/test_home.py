from __future__ import annotations

import pytest
from sqlalchemy import select

from app.models.extensions import PointTransaction, UserPoints
from app.services.home_service import _SIGN_IN_POINTS, _SIGN_IN_REASON


@pytest.mark.asyncio
async def test_home_summary_triggers_daily_sign_in(student_client, database, test_user):
    first_response = await student_client.get("/api/home/summary")
    assert first_response.status_code == 200

    payload = first_response.json()
    today_points = payload["personal"]["today_points"]
    assert today_points["total"] == _SIGN_IN_POINTS

    sign_in_entry = next((entry for entry in today_points["entries"] if entry["task"] == _SIGN_IN_REASON), None)
    assert sign_in_entry is not None
    assert sign_in_entry["status"] == "已完成"

    user_points_stmt = select(UserPoints).where(UserPoints.user_id == test_user.id)
    user_points = (await database.execute(user_points_stmt)).scalars().first()
    assert user_points is not None
    assert user_points.points == _SIGN_IN_POINTS

    tx_stmt = select(PointTransaction).where(PointTransaction.user_points_id == user_points.id)
    transactions = (await database.execute(tx_stmt)).scalars().all()
    assert len(transactions) == 1
    assert transactions[0].reason == _SIGN_IN_REASON

    second_response = await student_client.get("/api/home/summary")
    assert second_response.status_code == 200

    second_payload = second_response.json()
    second_today_points = second_payload["personal"]["today_points"]
    assert second_today_points["total"] == _SIGN_IN_POINTS

    sign_in_entry_second = next(
        (entry for entry in second_today_points["entries"] if entry["task"] == _SIGN_IN_REASON),
        None,
    )
    assert sign_in_entry_second is not None
    assert sign_in_entry_second["status"] == "已完成"

    transactions_after = (await database.execute(tx_stmt)).scalars().all()
    assert len(transactions_after) == 1
