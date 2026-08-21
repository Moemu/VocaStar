"""通知 API 路由"""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Path, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.deps.auth import get_current_user
from app.deps.sql import get_db
from app.models.user import User
from app.schemas.notifications import (
    NotificationListResponse,
    NotificationReadRequest,
)
from app.services.notification_service import NotificationService

router = APIRouter()


@router.get(
    "",
    summary="获取通知列表",
    response_model=NotificationListResponse,
    tags=["通知"],
)
async def list_notifications(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
    limit: int = Query(20, ge=1, le=100, description="返回通知数量（默认20，最多100）"),
    offset_raw: str | None = Query(
        None,
        description="分页偏移量（默认0）。允许空值，如 offset 将视为 0。",
    ),
    unread_only_raw: str | None = Query(
        None,
        description="仅返回未读通知。允许空值（例如 &unread_only），此时视为 True。",
    ),
) -> NotificationListResponse:
    """获取当前用户的通知列表

    为兼容某些前端在构造查询字符串时传入空值（例如 `?offset&unread_only`），
    这里对 offset 与 unread_only 进行宽松解析：
    - offset 为空或非法时回退为 0
    - unread_only 为空时视为 True；支持 true/1/yes/on 等真值解析
    """

    # 宽松解析 offset
    def _parse_offset(value: str | None, default: int = 0) -> int:
        if value is None:
            return default
        s = value.strip()
        if not s:
            return default
        try:
            num = int(s)
            return max(0, num)
        except ValueError:
            return default

    # 宽松解析布尔参数：空值/presence 视为 True
    def _parse_bool(value: str | None, default: bool = False) -> bool:
        if value is None:
            return default
        s = value.strip().lower()
        if s == "":
            return True  # presence-only
        truthy = {"1", "true", "yes", "on", "y", "t"}
        falsy = {"0", "false", "no", "off", "n", "f"}
        if s in truthy:
            return True
        if s in falsy:
            return False
        return default

    offset = _parse_offset(offset_raw, default=0)
    unread_only = _parse_bool(unread_only_raw, default=False)

    service = NotificationService(db)
    return await service.list_notifications(
        current_user=current_user,
        limit=limit,
        offset=offset,
        unread_only=unread_only,
    )


@router.post(
    "/{notification_id:int}/read",
    summary="标记通知为已读或未读",
    tags=["通知"],
)
async def mark_notification_read(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
    notification_id: int = Path(..., ge=1, description="通知ID"),
    payload: NotificationReadRequest | None = None,
) -> dict[str, str]:
    """标记单个通知为已读或未读

    如果 payload 为空，默认标记为已读
    """
    if payload is None:
        payload = NotificationReadRequest(is_read=True)

    service = NotificationService(db)
    if payload.is_read:
        success = await service.mark_as_read(current_user=current_user, notification_id=notification_id)
    else:
        success = await service.mark_as_unread(current_user=current_user, notification_id=notification_id)

    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="通知不存在")
    return {"msg": "ok"}


@router.post(
    "/mark-all-read",
    summary="标记所有通知为已读",
    tags=["通知"],
)
async def mark_all_read(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> dict[str, int]:
    """标记当前用户的所有通知为已读"""
    service = NotificationService(db)
    count = await service.mark_all_as_read(current_user=current_user)
    return {"count": count}


@router.delete(
    "/{notification_id:int}",
    summary="删除单个通知",
    tags=["通知"],
)
async def delete_notification(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
    notification_id: int = Path(..., ge=1, description="通知ID"),
) -> dict[str, str]:
    """删除单个通知"""
    service = NotificationService(db)
    success = await service.delete_notification(current_user=current_user, notification_id=notification_id)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="通知不存在")
    return {"msg": "ok"}


@router.delete(
    "/delete-all-read",
    summary="删除所有已读通知",
    tags=["通知"],
)
async def delete_all_read(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> dict[str, int]:
    """删除当前用户的所有已读通知"""
    service = NotificationService(db)
    count = await service.delete_all_read(current_user=current_user)
    return {"count": count}
