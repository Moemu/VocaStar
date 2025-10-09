from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.deps.sql import get_db
from app.schemas.career import CareerDetail, CareerListResponse, CareerSummary
from app.services.career_service import CareerService

router = APIRouter()


def get_service(db: AsyncSession) -> CareerService:
    return CareerService(db)


@router.get("/", response_model=CareerListResponse, summary="分页获取职业列表")
async def list_careers(
    dimension: Optional[str] = Query(None, description="按霍兰德维度过滤，例如 R/I/A/S/E/C"),
    keyword: Optional[str] = Query(None, description="按名称或简介模糊搜索"),
    limit: int = Query(20, ge=1, le=50, description="返回条数，默认 20"),
    offset: int = Query(0, ge=0, description="偏移量，用于分页"),
    db: AsyncSession = Depends(get_db),
) -> CareerListResponse:
    service = get_service(db)
    return await service.list_careers(dimension=dimension, keyword=keyword, limit=limit, offset=offset)


@router.get("/featured", response_model=list[CareerSummary], summary="获取推荐职业列表")
async def featured_careers(
    limit: int = Query(6, ge=1, le=20, description="返回推荐数量"),
    dimension: Optional[str] = Query(None, description="可选维度过滤"),
    db: AsyncSession = Depends(get_db),
) -> list[CareerSummary]:
    service = get_service(db)
    return await service.list_featured_careers(limit=limit, dimension=dimension)


@router.get("/{career_id}", response_model=CareerDetail, summary="根据 ID 获取职业详情")
async def get_career_detail(
    career_id: int,
    db: AsyncSession = Depends(get_db),
) -> CareerDetail:
    service = get_service(db)
    return await service.get_career_detail(career_id)
