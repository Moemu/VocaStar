from __future__ import annotations

from fastapi import APIRouter, Body, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.deps.auth import get_current_user
from app.deps.sql import get_db
from app.models.user import User
from app.schemas.cosplay import (
    CosplayChoiceRequest,
    CosplayReportPayload,
    CosplayScriptDetailResponse,
    CosplaySessionListResponse,
    CosplaySessionResumeRequest,
    CosplaySessionStateResponse,
)
from app.services.cosplay_service import CosplayService

router = APIRouter()


def get_service(db: AsyncSession) -> CosplayService:
    """基于当前数据库会话构造 Cosplay 服务。"""
    return CosplayService(db)


@router.get("/scripts", response_model=CosplaySessionListResponse, summary="列出可用的 Cosplay 剧本")
async def list_cosplay_scripts(db: AsyncSession = Depends(get_db)) -> CosplaySessionListResponse:
    """列出所有可用的 Cosplay 剧本概要信息。"""
    service = get_service(db)
    return await service.list_scripts()


@router.get(
    "/scripts/{script_id}",
    response_model=CosplayScriptDetailResponse,
    summary="获取指定 Cosplay 剧本详情",
)
async def get_cosplay_script_detail(script_id: int, db: AsyncSession = Depends(get_db)) -> CosplayScriptDetailResponse:
    """根据剧本 ID 获取详细内容与场景信息。"""
    service = get_service(db)
    return await service.get_script_detail(script_id)


@router.post(
    "/scripts/{script_id}/sessions",
    response_model=CosplaySessionStateResponse,
    summary="创建或恢复 Cosplay 会话",
)
async def create_or_resume_cosplay_session(
    script_id: int,
    request: CosplaySessionResumeRequest | None = Body(default=None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> CosplaySessionStateResponse:
    """为当前用户创建新的 Cosplay 会话或恢复已存在的会话。"""
    service = get_service(db)
    return await service.start_session(script_id=script_id, user=current_user, request=request)


@router.get(
    "/sessions/{session_id}",
    response_model=CosplaySessionStateResponse,
    summary="获取 Cosplay 会话当前状态",
)
async def get_cosplay_session_state(
    session_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> CosplaySessionStateResponse:
    """查询指定 Cosplay 会话的最新状态。"""
    service = get_service(db)
    return await service.get_session_state(session_id=session_id, user=current_user)


@router.post(
    "/sessions/{session_id}/choice",
    response_model=CosplaySessionStateResponse,
    summary="在当前场景中选择一个选项",
)
async def submit_cosplay_choice(
    session_id: int,
    request: CosplayChoiceRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> CosplaySessionStateResponse:
    """在指定会话的当前场景中提交用户的选项选择。"""
    service = get_service(db)
    return await service.choose_option(session_id=session_id, user=current_user, request=request)


@router.get(
    "/sessions/{session_id}/report",
    response_model=CosplayReportPayload,
    summary="获取 Cosplay 会话最终报告",
)
async def get_cosplay_report(
    session_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> CosplayReportPayload:
    """获取已经完成的 Cosplay 会话的总结报告。"""
    service = get_service(db)
    return await service.get_report(session_id=session_id, user=current_user)
