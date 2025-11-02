from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.deps.sql import get_db

router = APIRouter()


@router.get(
    "",
    summary="职业伙伴列表（预留）",
    description="占位接口：后续支持伙伴列表/搜索/关注等功能。",
)
async def list_partners(
    db: Annotated[AsyncSession, Depends(get_db)],
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
):
    return {"items": [], "pagination": {"page": page, "page_size": page_size, "total": 0}}
