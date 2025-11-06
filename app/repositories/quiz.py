from __future__ import annotations

from datetime import datetime
from typing import Iterable, Optional, Sequence

from sqlalchemy import delete, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.career import Career, CareerRecommendation
from app.models.quiz import (
    Option,
    Question,
    Quiz,
    QuizAnswer,
    QuizReport,
    QuizSubmission,
    QuizSubmissionStatus,
)


class QuizRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_latest_published_quiz(self) -> Optional[Quiz]:
        stmt = select(Quiz).where(Quiz.is_published.is_(True)).order_by(Quiz.created_at.desc()).limit(1)
        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def get_published_quiz_by_slug(self, slug: str) -> Optional[Quiz]:
        """Fetch a published quiz by its config.slug using a JSON filter.

        This avoids loading all published quizzes into Python and improves
        performance once the table grows.
        """
        if not slug:
            return None

        stmt = (
            select(Quiz)
            .where(Quiz.is_published.is_(True))
            .where(Quiz.config.isnot(None))
            .where(Quiz.config["slug"].as_string() == slug)
            .limit(1)
        )
        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def get_submission_by_token(self, token: str) -> Optional[QuizSubmission]:
        stmt = (
            select(QuizSubmission)
            .where(QuizSubmission.session_token == token)
            .options(
                selectinload(QuizSubmission.quiz).selectinload(Quiz.questions).selectinload(Question.options),
                selectinload(QuizSubmission.answers),
                selectinload(QuizSubmission.report)
                .selectinload(QuizReport.career_recommendations)
                .selectinload(CareerRecommendation.career),
            )
        )
        result = await self.session.execute(stmt)
        return result.scalars().unique().first()

    async def get_latest_completed_submission(
        self,
        user_id: int,
        *,
        slug: Optional[str] = None,
    ) -> Optional[QuizSubmission]:
        order_key = func.coalesce(QuizSubmission.completed_at, QuizSubmission.started_at)
        stmt = (
            select(QuizSubmission)
            .join(Quiz, Quiz.id == QuizSubmission.quiz_id)
            .where(
                QuizSubmission.user_id == user_id,
                QuizSubmission.status == QuizSubmissionStatus.completed,
            )
            .options(
                selectinload(QuizSubmission.quiz).selectinload(Quiz.questions).selectinload(Question.options),
                selectinload(QuizSubmission.answers),
                selectinload(QuizSubmission.report)
                .selectinload(QuizReport.career_recommendations)
                .selectinload(CareerRecommendation.career),
            )
            .order_by(order_key.desc(), QuizSubmission.id.desc())
            .limit(1)
        )

        if slug:
            stmt = stmt.where(Quiz.config["slug"].as_string() == slug)

        result = await self.session.execute(stmt)
        return result.scalars().unique().first()

    async def get_active_submission_by_user(
        self, user_id: int, *, quiz_id: Optional[int] = None
    ) -> Optional[QuizSubmission]:
        stmt = (
            select(QuizSubmission)
            .where(
                QuizSubmission.user_id == user_id,
                QuizSubmission.status == QuizSubmissionStatus.in_progress,
            )
            .order_by(QuizSubmission.started_at.desc())
            .limit(1)
        )
        if quiz_id is not None:
            stmt = stmt.where(QuizSubmission.quiz_id == quiz_id)
        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def create_submission(
        self,
        *,
        user_id: int,
        quiz_id: int,
        session_token: str,
        expires_at: datetime,
    ) -> QuizSubmission:
        submission = QuizSubmission(
            user_id=user_id,
            quiz_id=quiz_id,
            session_token=session_token,
            expires_at=expires_at,
        )
        self.session.add(submission)
        await self.session.flush()
        await self.session.refresh(submission)
        return submission

    async def list_questions_with_options(self, quiz_id: int) -> list[Question]:
        stmt = (
            select(Question)
            .where(Question.quiz_id == quiz_id)
            .order_by(Question.order.asc(), Question.id.asc())
            .options(selectinload(Question.options).selectinload(Option.answers))
        )
        result = await self.session.execute(stmt)
        return result.scalars().unique().all()  # type:ignore

    async def clear_answers_for_questions(self, submission_id: int, question_ids: Iterable[int]) -> None:
        if not question_ids:
            return
        unique_ids = tuple(set(question_ids))
        stmt = delete(QuizAnswer).where(
            QuizAnswer.submission_id == submission_id,
            QuizAnswer.question_id.in_(unique_ids),
        )
        await self.session.execute(stmt)

    async def add_answer(
        self,
        *,
        submission_id: int,
        question_id: int,
        option_id: Optional[int],
        option_ids: Optional[Sequence[int]],
        rating_value: Optional[float],
        response_time: Optional[int],
        extra_payload: Optional[dict],
    ) -> QuizAnswer:
        answer = QuizAnswer(
            submission_id=submission_id,
            question_id=question_id,
            option_id=option_id,
            option_ids=list(option_ids) if option_ids is not None else None,
            rating_value=rating_value,
            response_time=response_time,
            extra_payload=extra_payload,
        )
        self.session.add(answer)
        return answer

    async def list_careers_for_dimensions(self) -> list[Career]:
        stmt = select(Career)
        result = await self.session.execute(stmt)
        return list(result.scalars().unique().all())

    async def create_report(self, submission_id: int, result_json: dict) -> QuizReport:
        report = QuizReport(submission_id=submission_id, result_json=result_json)
        self.session.add(report)
        await self.session.flush()
        await self.session.refresh(report)
        return report

    async def create_career_recommendations(
        self,
        *,
        report_id: int,
        items: Sequence[tuple[int, float, str]],
    ) -> list[CareerRecommendation]:
        if not items:
            return []
        recommendations = [
            CareerRecommendation(report_id=report_id, career_id=career_id, score=score, match_reason=reason)
            for career_id, score, reason in items
        ]
        self.session.add_all(recommendations)
        await self.session.flush()
        for recommendation in recommendations:
            await self.session.refresh(recommendation)
        return recommendations

    async def list_questions_map(self, quiz_id: int) -> dict[int, Question]:
        questions = await self.list_questions_with_options(quiz_id)
        return {question.id: question for question in questions}

    async def list_options_map(self, question_ids: Iterable[int]) -> dict[int, Option]:
        unique_ids = tuple(set(question_ids))
        if not unique_ids:
            return {}
        stmt = select(Option).where(Option.question_id.in_(unique_ids))
        result = await self.session.execute(stmt)
        return {option.id: option for option in result.scalars().all()}
