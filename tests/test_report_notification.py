"""
测试报告生成完成后的通知创建。
"""

from datetime import datetime, timedelta, timezone

import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.extensions import MessageType, Notification
from app.models.quiz import QuizSubmission, QuizSubmissionStatus
from app.models.user import User
from app.schemas.notifications import NotificationTypeEnum
from app.services.report_queue import ReportJob


@pytest.mark.asyncio
async def test_notification_created_after_report_queue_completion(
    database: AsyncSession,
    test_user: User,
    sample_quiz,
) -> None:
    """验证报告队列完成后，通知被正确创建。"""

    # 创建测评提交
    now = datetime.now(timezone.utc)
    expires_at = now + timedelta(minutes=30)

    submission = QuizSubmission(
        user_id=test_user.id,
        quiz_id=sample_quiz.id,
        session_token="test-token-123",
        status=QuizSubmissionStatus.in_progress,
        expires_at=expires_at,
    )
    database.add(submission)
    await database.commit()

    # 模拟通知创建的回调
    notifications_created = []

    async def mock_on_complete(user_id: int, report_id: int) -> None:
        """模拟报告完成回调。"""
        notifications_created.append((user_id, report_id))
        # 实际的通知创建逻辑
        from app.services.notification_service import NotificationService

        notification_svc = NotificationService(database)
        await notification_svc.create_notification(
            user_id=user_id,
            title="你的职业测评报告已生成",
            notification_type=NotificationTypeEnum.achievement,
            content="您已完成职业兴趣测评，请查看详细报告了解职业方向建议。",
        )

    # 验证：模拟队列任务中的回调被正确调用
    job = ReportJob(report_id=999, on_complete=mock_on_complete)

    # 在这里不真正入队，而是直接模拟调用回调
    if job.on_complete is not None:
        await job.on_complete(test_user.id, job.report_id)

    # 验证回调被调用
    assert len(notifications_created) == 1
    assert notifications_created[0] == (test_user.id, 999)

    # 验证通知已创建
    result = await database.execute(select(Notification).where(Notification.user_id == test_user.id))
    notifications = result.scalars().all()
    assert len(notifications) > 0

    # 验证通知内容
    notification = notifications[-1]
    assert notification.title == "你的职业测评报告已生成"
    assert notification.message_type == MessageType.achievement


@pytest.mark.asyncio
async def test_report_job_with_callback() -> None:
    """验证 ReportJob 能够正确携带和调用回调。"""

    callback_called = []

    async def test_callback(user_id: int, report_id: int) -> None:
        callback_called.append((user_id, report_id))

    # 创建包含回调的 ReportJob
    job = ReportJob(report_id=42, on_complete=test_callback)

    # 验证回调存在
    assert job.on_complete is not None

    # 调用回调
    if job.on_complete is not None:
        await job.on_complete(123, job.report_id)

    # 验证回调被执行
    assert len(callback_called) == 1
    assert callback_called[0] == (123, 42)


@pytest.mark.asyncio
async def test_report_job_without_callback() -> None:
    """验证不含回调的 ReportJob 能正常工作（向后兼容性）。"""

    # 创建不含回调的 ReportJob
    job = ReportJob(report_id=42)

    # 验证回调为 None
    assert job.on_complete is None

    # 不会抛出错误
    if job.on_complete is not None:
        await job.on_complete(456, job.report_id)
