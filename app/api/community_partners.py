from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, Path, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.deps.auth import get_current_user, get_current_user_optional
from app.deps.sql import get_db
from app.models.user import User
from app.schemas.partners import (
    BindState,
    PartnerListResponse,
    PartnerMyListResponse,
    PartnerRecommendListResponse,
    SkillStat,
)
from app.services.partner_service import PartnerService

router = APIRouter()


@router.get(
    "/search",
    summary="搜索职业伙伴",
    response_model=PartnerListResponse,
)
async def search_partners(
    db: Annotated[AsyncSession, Depends(get_db)],
    q: str | None = Query(None, description="关键词（姓名/职业），模糊匹配"),
    skill: str | None = Query(None, description="技能标签（精确匹配）"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
):
    service = PartnerService(db)
    return await service.search(q=q, skill=skill, page=page, page_size=page_size)


@router.get(
    "/hot-skills",
    summary="热门技能标签",
    response_model=list[SkillStat],
)
async def get_hot_skills(
    db: Annotated[AsyncSession, Depends(get_db)],
    limit: int = Query(20, ge=1, le=100),
):
    service = PartnerService(db)
    return await service.hot_skills(limit=limit)


@router.get(
    "/recommended",
    summary="推荐伙伴（隐藏学习进度）",
    response_model=PartnerRecommendListResponse,
)
async def recommended_partners(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User | None, Depends(get_current_user_optional)],
    limit: int = Query(6, ge=1, le=50),
    skill: str | None = Query(None, description="可选技能过滤"),
):
    service = PartnerService(db)
    return await service.recommended(current_user=current_user, limit=limit, skill=skill)


@router.post(
    "/{partner_id:int}/bind",
    summary="绑定职业伙伴",
    response_model=BindState,
)
async def bind_partner(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
    partner_id: int = Path(..., ge=1),
):
    service = PartnerService(db)
    return await service.bind(current_user=current_user, partner_id=partner_id)


@router.delete(
    "/{partner_id:int}/bind",
    summary="解绑职业伙伴",
    response_model=BindState,
)
async def unbind_partner(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
    partner_id: int = Path(..., ge=1),
):
    service = PartnerService(db)
    return await service.unbind(current_user=current_user, partner_id=partner_id)


@router.get(
    "/my",
    summary="我的伙伴（隐藏技术栈）",
    response_model=PartnerMyListResponse,
)
async def my_partners(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
):
    service = PartnerService(db)
    return await service.my_partners(current_user=current_user, page=page, page_size=page_size)
