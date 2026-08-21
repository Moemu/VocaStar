from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.deps.auth import get_current_user
from app.deps.sql import get_db
from app.models.user import User
from app.schemas.home import HomeSummaryResponse
from app.services.home_service import HomeService

router = APIRouter()


@router.get("/summary", response_model=HomeSummaryResponse, summary="首页聚合信息")
async def get_home_summary(
    limit: int = Query(3, ge=1, le=10, description="返回的职业推荐数量"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> HomeSummaryResponse:
    service = HomeService(db)
    return await service.get_home_summary(current_user, limit=limit)
