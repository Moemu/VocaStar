from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.deps.auth import get_current_user
from app.deps.sql import get_db
from app.models.extensions import FavoriteItemType
from app.models.user import User
from app.schemas.profile_center import (  # 新增：成就查询响应将动态构造，不需要预定义复杂模型，这里后续可加 Pydantic Schema
    AchievementItem,
    AchievementListResponse,
    AddFavoriteRequest,
    DashboardResponse,
    ExplorationListResponse,
    ExplorationUpsertRequest,
    FavoriteListResponse,
    WrongbookListResponse,
)
from app.schemas.user import UserProfileSummary, UserSetProfileRequest
from app.services.profile_center_service import ProfileCenterService

router = APIRouter()


def get_service(db: AsyncSession) -> ProfileCenterService:
    return ProfileCenterService(db)


# ------- 个人资料 -------


@router.get("/me", response_model=UserProfileSummary)
async def get_my_profile(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> UserProfileSummary:
    svc = get_service(db)
    return await svc.get_profile(current_user)


@router.post("/me")
async def set_my_profile(
    request: UserSetProfileRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict[str, str]:
    svc = get_service(db)
    await svc.set_profile(current_user, request)
    return {"msg": "ok"}


# ------- 数据看板 -------


@router.get("/dashboard", response_model=DashboardResponse)
async def get_my_dashboard(
    db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)
) -> DashboardResponse:
    svc = get_service(db)
    return await svc.get_dashboard(current_user)


# ------- 探索足迹 -------


@router.post("/explorations")
async def upsert_explorations(
    request: ExplorationUpsertRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict[str, str]:
    svc = get_service(db)
    await svc.upsert_explorations(current_user, request.items)
    return {"msg": "ok"}


@router.get("/explorations", response_model=ExplorationListResponse)
async def list_explorations(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    limit: int = Query(4, ge=1, le=20, description="返回的最大探索项数量，默认4，范围1-20"),
) -> ExplorationListResponse:
    svc = get_service(db)
    return await svc.list_explorations(current_user, limit=limit)


# ------- 成就 -------


@router.get("/achievements", response_model=AchievementListResponse)
async def list_achievements(
    db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)
) -> AchievementListResponse:
    from app.services.achievement_service import AchievementService

    svc = AchievementService(db)
    items = await svc.list_with_progress(current_user.id)
    return AchievementListResponse(items=[AchievementItem(**it) for it in items])


# ------- 收藏夹 -------


@router.post("/favorites")
async def add_favorite(
    request: AddFavoriteRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict[str, str]:
    svc = get_service(db)
    item_type = FavoriteItemType(request.item_type)
    await svc.add_favorite(current_user, item_type, request.item_id)
    return {"msg": "ok"}


@router.get("/favorites", response_model=FavoriteListResponse)
async def list_favorites(
    db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)
) -> FavoriteListResponse:
    svc = get_service(db)
    return await svc.list_favorites(current_user)


# ------- 错题本 -------


@router.get("/wrongbook", response_model=WrongbookListResponse)
async def list_wrongbook(
    db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)
) -> WrongbookListResponse:
    svc = get_service(db)
    return await svc.list_wrongbook(current_user)
