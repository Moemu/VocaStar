from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.deps.auth import get_current_user
from app.deps.sql import get_db
from app.models.extensions import FavoriteItemType
from app.models.user import User
from app.schemas.profile_center import (
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
    db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)
) -> ExplorationListResponse:
    svc = get_service(db)
    return await svc.list_explorations(current_user)


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
