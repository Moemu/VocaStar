"""通知业务服务层"""

from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.extensions import MessageType, Notification
from app.models.user import User
from app.repositories.notifications import NotificationsRepository
from app.schemas.notifications import (
    NotificationItem,
    NotificationListResponse,
    NotificationTypeEnum,
)


class NotificationService:
    """通知服务层"""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.repo = NotificationsRepository(session)

    async def list_notifications(
        self,
        *,
        current_user: User,
        limit: int = 20,
        offset: int = 0,
        unread_only: bool = False,
    ) -> NotificationListResponse:
        """获取用户的通知列表

        参数:
            current_user: 当前用户
            limit: 返回的最大通知数（默认 20）
            offset: 分页偏移量（默认 0）
            unread_only: 仅返回未读通知（默认 False）

        返回:
            NotificationListResponse 包含通知列表、总数、未读数
        """
        notifications, total = await self.repo.list_notifications(
            user_id=current_user.id,
            limit=limit,
            offset=offset,
            unread_only=unread_only,
        )
        unread_count = await self.repo.get_unread_count(current_user.id)

        items = [
            NotificationItem(
                id=n.id,
                title=n.title,
                type=NotificationTypeEnum(n.message_type.value),
                timestamp=n.created_at,
                is_read=n.is_read,
            )
            for n in notifications
        ]
        return NotificationListResponse(items=items, total=total, unread_count=unread_count)

    async def mark_as_read(self, *, current_user: User, notification_id: int) -> bool:
        """标记通知为已读"""
        return await self.repo.mark_as_read(notification_id, current_user.id)

    async def mark_as_unread(self, *, current_user: User, notification_id: int) -> bool:
        """标记通知为未读"""
        return await self.repo.mark_as_unread(notification_id, current_user.id)

    async def mark_all_as_read(self, *, current_user: User) -> int:
        """标记所有通知为已读

        返回:
            int: 标记为已读的通知数量
        """
        return await self.repo.mark_all_as_read(current_user.id)

    async def delete_notification(self, *, current_user: User, notification_id: int) -> bool:
        """删除单个通知"""
        return await self.repo.delete_notification(notification_id, current_user.id)

    async def delete_all_read(self, *, current_user: User) -> int:
        """删除所有已读通知

        返回:
            int: 删除的通知数量
        """
        return await self.repo.delete_all_read(current_user.id)

    async def create_notification(
        self,
        *,
        user_id: int,
        title: str,
        notification_type: NotificationTypeEnum,
        content: str = "",
    ) -> Notification:
        """创建一条通知

        参数:
            user_id: 接收通知的用户 ID
            title: 通知标题
            notification_type: 通知类型
            content: 通知内容（可选）
        """
        return await self.repo.create_notification(
            user_id=user_id,
            title=title,
            message_type=MessageType(notification_type.value),
            content=content,
        )
