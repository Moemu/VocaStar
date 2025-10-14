from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.deps.auth import get_current_user_optional
from app.deps.sql import get_db
from app.models.user import User
from app.schemas.career import (
    CareerDetail,
    CareerExploreResponse,
    CareerListResponse,
    CareerSummary,
)
from app.services.career_service import CareerService

router = APIRouter()


def get_service(db: AsyncSession) -> CareerService:
    return CareerService(db)


# pragma: no cover
def _parse_int_param(
    name: str,
    raw_value: Optional[str],
    *,
    default: int,
    min_value: int,
    max_value: Optional[int] = None,
) -> int:
    if raw_value is None or raw_value == "":
        return default
    try:
        value = int(raw_value)
    except (TypeError, ValueError):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"参数 {name} 必须是整数",
        ) from None

    if value < min_value:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"参数 {name} 不能小于 {min_value}",
        )
    if max_value is not None and value > max_value:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"参数 {name} 不能大于 {max_value}",
        )
    return value


# pragma: no cover
def _parse_optional_int_param(
    name: str,
    raw_value: Optional[str],
    *,
    min_value: int,
    max_value: Optional[int] = None,
) -> Optional[int]:
    if raw_value is None or raw_value == "":
        return None
    try:
        value = int(raw_value)
    except (TypeError, ValueError):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"参数 {name} 必须是整数",
        ) from None
    if value < min_value:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"参数 {name} 不能小于 {min_value}",
        )
    if max_value is not None and value > max_value:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"参数 {name} 不能大于 {max_value}",
        )
    return value


# pragma: no cover
def _parse_bool_param(name: str, raw_value: Optional[str]) -> bool:
    if raw_value is None or raw_value == "":
        return False
    normalized = raw_value.strip().lower()
    if normalized in {"1", "true", "yes", "on"}:
        return True
    if normalized in {"0", "false", "no", "off"}:
        return False
    raise HTTPException(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        detail=f"参数 {name} 只能是 true/false",
    )


@router.get("/", response_model=CareerListResponse, summary="分页获取职业列表")
async def list_careers(
    dimension: Optional[str] = Query(None, description="按霍兰德维度过滤，例如 R/I/A/S/E/C"),
    keyword: Optional[str] = Query(None, description="按名称或简介模糊搜索"),
    limit: Optional[str] = Query(None, description="返回条数，默认 20，范围 1-50"),
    offset: Optional[str] = Query(None, description="偏移量，用于分页，默认 0"),
    db: AsyncSession = Depends(get_db),
) -> CareerListResponse:
    limit_value = _parse_int_param("limit", limit, default=20, min_value=1, max_value=50)
    offset_value = _parse_int_param("offset", offset, default=0, min_value=0)

    service = get_service(db)
    return await service.list_careers(dimension=dimension, keyword=keyword, limit=limit_value, offset=offset_value)


@router.get("/featured", response_model=list[CareerSummary], summary="获取推荐职业列表")
async def featured_careers(
    limit: Optional[str] = Query(None, description="返回推荐数量"),
    dimension: Optional[str] = Query(None, description="可选维度过滤"),
    db: AsyncSession = Depends(get_db),
) -> list[CareerSummary]:
    limit_value = _parse_int_param("limit", limit, default=6, min_value=1, max_value=20)

    service = get_service(db)
    return await service.list_featured_careers(limit=limit_value, dimension=dimension)


@router.get("/exploration", response_model=CareerExploreResponse, summary="职业星球探索数据")
async def explore_career_galaxies(
    category: Optional[str] = Query(None, description="职业分类编码或名称"),
    salary_avg: Optional[str] = Query(None, description="薪资均值"),
    recommended: Optional[str] = Query(None, description="是否根据最新测评结果推荐"),
    db: AsyncSession = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional),
) -> CareerExploreResponse:
    salary_avg_value = _parse_optional_int_param("salary_avg", salary_avg, min_value=0)
    recommended_flag = _parse_bool_param("recommended", recommended)

    service = get_service(db)
    return await service.explore_careers(
        category=category,
        salary_avg=salary_avg_value,
        recommended=recommended_flag,
        current_user=current_user,
    )


@router.get("/{career_id}", response_model=CareerDetail, summary="根据 ID 获取职业详情")
async def get_career_detail(
    career_id: int,
    db: AsyncSession = Depends(get_db),
) -> CareerDetail:
    service = get_service(db)
    return await service.get_career_detail(career_id)
