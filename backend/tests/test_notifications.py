"""测试通知系统集成"""

import pytest
from sqlalchemy import select

from app.models.extensions import Notification
from app.schemas.notifications import NotificationTypeEnum
from app.services.achievement_service import AchievementCodes, AchievementService
from app.services.notification_service import NotificationService


@pytest.mark.asyncio
async def test_notification_on_achievement_unlock(database, test_user):
    """测试成就解锁时是否创建通知"""
    # 前置：确保成就存在
    svc = AchievementService(database)
    await svc.seed_minimal()

    # 初始状态：无通知
    stmt = select(Notification).where(Notification.user_id == test_user.id)
    notifications_before = (await database.execute(stmt)).scalars().all()
    assert len(notifications_before) == 0

    # 触发成就授予（模拟伙伴绑定）
    from app.models.partners import CommunityPartner, UserPartnerBinding

    # 创建 3 个伙伴并绑定
    for i in range(3):
        partner = CommunityPartner(name=f"partner_{i}", profession="dev")
        database.add(partner)
        await database.flush()

        binding = UserPartnerBinding(user_id=test_user.id, partner_id=partner.id)
        database.add(binding)
        await database.flush()

    await database.commit()

    # 触发成就评估（应该解锁 PARTNER_3_BOUND）
    newly_awarded = await svc.evaluate_and_award(test_user.id, events=["partner_bind"])

    # 验证成就被授予
    assert AchievementCodes.PARTNER_3_BOUND in newly_awarded

    # 验证通知被创建
    notifications_after = (await database.execute(stmt)).scalars().all()
    assert len(notifications_after) > 0

    # 验证通知内容
    notification = notifications_after[0]
    assert "解锁成就" in notification.title
    assert "社交之星" in notification.title
    assert notification.message_type.value == "achievement"
    assert not notification.is_read


@pytest.mark.asyncio
async def test_notification_list_with_unread_count(database, test_user):
    """测试通知列表与未读计数"""
    notification_svc = NotificationService(database)

    # 创建 3 条通知
    for i in range(3):
        await notification_svc.create_notification(
            user_id=test_user.id,
            title=f"测试通知 {i+1}",
            notification_type=NotificationTypeEnum.system,
            content=f"这是测试内容 {i+1}",
        )

    # 获取通知列表
    response = await notification_svc.list_notifications(current_user=test_user)

    assert response.total == 3
    assert response.unread_count == 3
    assert len(response.items) == 3

    # 标记第一条为已读
    await notification_svc.mark_as_read(current_user=test_user, notification_id=response.items[0].id)

    # 重新获取列表
    response2 = await notification_svc.list_notifications(current_user=test_user)
    assert response2.unread_count == 2

    # 仅返回未读
    response3 = await notification_svc.list_notifications(current_user=test_user, unread_only=True)
    assert len(response3.items) == 2


@pytest.mark.asyncio
async def test_mark_all_read(database, test_user):
    """测试批量标记为已读"""
    notification_svc = NotificationService(database)

    # 创建 5 条通知
    for i in range(5):
        await notification_svc.create_notification(
            user_id=test_user.id,
            title=f"通知 {i+1}",
            notification_type=NotificationTypeEnum.activity,
        )

    # 标记全部已读
    count = await notification_svc.mark_all_as_read(current_user=test_user)
    assert count == 5

    # 验证未读数为 0
    response = await notification_svc.list_notifications(current_user=test_user)
    assert response.unread_count == 0


@pytest.mark.asyncio
async def test_notifications_api_blank_query_params(student_client, test_user, database):
    """测试 /api/notifications 在出现空查询参数 (&offset&unread_only) 时仍可正常返回。

    期望：
    - offset 为空 => 视为 0
    - unread_only 空存在 => 视为 True
    """
    from app.schemas.notifications import NotificationTypeEnum
    from app.services.notification_service import NotificationService

    svc = NotificationService(database)
    # 创建 3 条通知，其中 1 条标记为已读，剩余 2 条未读
    n1 = await svc.create_notification(user_id=test_user.id, title="A", notification_type=NotificationTypeEnum.system)
    n2 = await svc.create_notification(user_id=test_user.id, title="B", notification_type=NotificationTypeEnum.system)
    n3 = await svc.create_notification(user_id=test_user.id, title="C", notification_type=NotificationTypeEnum.system)
    await svc.mark_as_read(current_user=test_user, notification_id=n1.id)

    # 通过 API 访问（传入空参数）
    resp = await student_client.get("/api/notifications?limit=5&offset&unread_only")
    assert resp.status_code == 200, resp.text
    data = resp.json()
    # 仅返回未读（应为 2 条）
    assert data["total"] >= 2
    assert data["unread_count"] == 2
    returned_ids = {item["id"] for item in data["items"]}
    assert n2.id in returned_ids and n3.id in returned_ids
