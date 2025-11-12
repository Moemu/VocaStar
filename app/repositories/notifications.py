"""通知数据访问层"""

from __future__ import annotations

from typing import Optional

from sqlalchemy import and_, desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.extensions import MessageType, Notification


class NotificationsRepository:
    """通知数据访问层"""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def list_notifications(
        self,
        *,
        user_id: int,
        limit: int = 20,
        offset: int = 0,
        unread_only: bool = False,
    ) -> tuple[list[Notification], int]:
        """列出用户的通知。

        返回 (通知列表, 总数)
        """
        stmt = select(Notification).where(Notification.user_id == user_id)
        if unread_only:
            stmt = stmt.where(Notification.is_read.is_(False))

        # 获取总数
        count_stmt = stmt.with_only_columns(func.count()).order_by(None)
        total = int((await self.session.execute(count_stmt)).scalar() or 0)

        # 获取分页结果，按创建时间倒序
        stmt = stmt.order_by(desc(Notification.created_at)).offset(offset).limit(limit)
        notifications = list((await self.session.execute(stmt)).scalars().all())
        return notifications, total

    async def get_unread_count(self, user_id: int) -> int:
        """获取用户未读通知数"""
        stmt = (
            select(func.count())
            .select_from(Notification)
            .where(and_(Notification.user_id == user_id, Notification.is_read.is_(False)))
        )
        return int((await self.session.execute(stmt)).scalar() or 0)

    async def get_by_id(self, notification_id: int, user_id: int) -> Optional[Notification]:
        """根据 ID 获取通知（需验证所有权）"""
        stmt = select(Notification).where(and_(Notification.id == notification_id, Notification.user_id == user_id))
        return (await self.session.execute(stmt)).scalar_one_or_none()

    async def mark_as_read(self, notification_id: int, user_id: int) -> bool:
        """标记单个通知为已读。返回是否成功"""
        notification = await self.get_by_id(notification_id, user_id)
        if not notification:
            return False
        if not notification.is_read:
            notification.is_read = True
            await self.session.flush()
        await self.session.commit()
        return True

    async def mark_as_unread(self, notification_id: int, user_id: int) -> bool:
        """标记单个通知为未读。返回是否成功"""
        notification = await self.get_by_id(notification_id, user_id)
        if not notification:
            return False
        if notification.is_read:
            notification.is_read = False
            await self.session.flush()
        await self.session.commit()
        return True

    async def mark_all_as_read(self, user_id: int) -> int:
        """标记所有通知为已读。返回更新的数量"""
        stmt = select(Notification).where(and_(Notification.user_id == user_id, Notification.is_read.is_(False)))
        notifications = list((await self.session.execute(stmt)).scalars().all())
        for n in notifications:
            n.is_read = True
        if notifications:
            await self.session.flush()
            await self.session.commit()
        return len(notifications)

    async def delete_notification(self, notification_id: int, user_id: int) -> bool:
        """删除单个通知。返回是否成功"""
        notification = await self.get_by_id(notification_id, user_id)
        if not notification:
            return False
        await self.session.delete(notification)
        await self.session.commit()
        return True

    async def delete_all_read(self, user_id: int) -> int:
        """删除所有已读通知。返回删除的数量"""
        stmt = select(Notification).where(and_(Notification.user_id == user_id, Notification.is_read.is_(True)))
        notifications = list((await self.session.execute(stmt)).scalars().all())
        for n in notifications:
            await self.session.delete(n)
        if notifications:
            await self.session.commit()
        return len(notifications)

    async def create_notification(
        self,
        *,
        user_id: int,
        title: str,
        message_type: MessageType,
        content: str = "",
    ) -> Notification:
        """创建一条通知"""
        notification = Notification(
            user_id=user_id,
            title=title,
            message_type=message_type,
            content=content,
            is_read=False,
        )
        self.session.add(notification)
        await self.session.flush()
        await self.session.commit()
        return notification
