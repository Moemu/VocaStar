from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, Path, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.deps.auth import get_current_user
from app.deps.sql import get_db
from app.models.user import User
from app.schemas.mentors import (
    DomainListResponse,
    MentorListResponse,
    MentorRequestCreate,
    MentorRequestItem,
    MyMentorListResponse,
)
from app.services.mentor_service import MentorService

router = APIRouter()


@router.get(
    "/domains",
    summary="导师领域列表",
    response_model=DomainListResponse,
)
async def list_domains(db: Annotated[AsyncSession, Depends(get_db)]):
    service = MentorService(db)
    return await service.list_domains()


@router.get(
    "/search",
    summary="搜索职业导师",
    response_model=MentorListResponse,
)
async def search_mentors(
    db: Annotated[AsyncSession, Depends(get_db)],
    q: str | None = Query(None, description="关键词（姓名/职业），模糊匹配"),
    skill: str | None = Query(None, description="技能标签（精确）"),
    domain: str | None = Query(None, description="领域标识（slug），如 frontend/backend"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
):
    service = MentorService(db)
    return await service.search(q=q, skill=skill, domain=domain, page=page, page_size=page_size)


@router.post(
    "/{mentor_id:int}/request",
    summary="创建导师提问/咨询申请",
    response_model=MentorRequestItem,
)
async def create_request(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
    payload: MentorRequestCreate,
    mentor_id: int = Path(..., ge=1),
):
    service = MentorService(db)
    return await service.create_request(current_user=current_user, mentor_id=mentor_id, payload=payload)


@router.get(
    "/my",
    summary="我的职业导师（曾申请过的导师）",
    response_model=MyMentorListResponse,
)
async def my_mentors(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    service = MentorService(db)
    return await service.my_mentors(current_user=current_user)
