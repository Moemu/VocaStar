"""通知 API 数据模型"""

from __future__ import annotations

from datetime import datetime
from enum import Enum

from pydantic import BaseModel, ConfigDict, Field


class NotificationTypeEnum(str, Enum):
    """通知类型枚举，与 MessageType 对应"""

    system = "system"  # 系统通知
    activity = "activity"  # 活动提醒
    achievement = "achievement"  # 成就通知


class NotificationItem(BaseModel):
    """通知列表项"""

    id: int = Field(..., description="通知 ID")
    title: str = Field(..., description="通知标题")
    type: NotificationTypeEnum = Field(..., description="通知类型")
    timestamp: datetime = Field(..., description="通知时间")
    is_read: bool = Field(False, description="是否已读")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "id": 1,
                "title": "你的职业测评报告已生成",
                "type": "achievement",
                "timestamp": "2025-09-25T10:30:00Z",
                "is_read": False,
            }
        }
    )


class NotificationListResponse(BaseModel):
    """通知列表响应"""

    items: list[NotificationItem] = Field(default_factory=list, description="通知列表")
    total: int = Field(0, ge=0, description="总数")
    unread_count: int = Field(0, ge=0, description="未读数")


class NotificationReadRequest(BaseModel):
    """标记通知已读请求"""

    is_read: bool = Field(True, description="标记为已读（true）或未读（false）")


class MarkAllReadRequest(BaseModel):
    """批量标记已读请求"""

    mark_all: bool = Field(True, description="是否标记全部为已读")
