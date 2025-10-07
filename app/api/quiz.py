from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.deps.auth import get_current_user
from app.deps.sql import get_db
from app.models.user import User
from app.schemas.quiz import (
    QuizAnswerRequest,
    QuizAnswerResponse,
    QuizQuestionsResponse,
    QuizReportResponse,
    QuizStartResponse,
    QuizSubmitRequest,
)
from app.services.quiz_service import QuizService

router = APIRouter()


@router.post("/start", response_model=QuizStartResponse)
async def start_quiz(
    slug: str | None = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> QuizStartResponse:
    service = QuizService(db)
    return await service.start_quiz(current_user, slug=slug)


@router.get("/questions", response_model=QuizQuestionsResponse)
async def get_questions(
    session_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> QuizQuestionsResponse:
    service = QuizService(db)
    return await service.get_questions(session_id, current_user)


@router.post("/answer", response_model=QuizAnswerResponse)
async def answer_questions(
    request: QuizAnswerRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> QuizAnswerResponse:
    service = QuizService(db)
    return await service.answer_questions(request, current_user)


@router.post("/submit", response_model=QuizReportResponse)
async def submit_quiz(
    request: QuizSubmitRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> QuizReportResponse:
    service = QuizService(db)
    return await service.submit_quiz(request, current_user)


@router.get("/report", response_model=QuizReportResponse)
async def get_report(
    session_id: str | None = None,
    slug: str | None = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> QuizReportResponse:
    service = QuizService(db)
    return await service.get_report(current_user, session_id=session_id, slug=slug)
