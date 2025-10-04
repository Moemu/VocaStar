from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Iterable
from uuid import uuid4

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.career import Career
from app.models.extensions import PointTransaction, UserPoints
from app.models.quiz import Option, QuizAnswer, QuizSubmission, QuizSubmissionStatus
from app.models.user import User
from app.repositories.quiz import QuizRepository
from app.schemas.quiz import (
    QuizAnswerRequest,
    QuizAnswerResponse,
    QuizMultipleChoiceAnswer,
    QuizOption,
    QuizQuestion,
    QuizQuestionsResponse,
    QuizRatingAnswer,
    QuizRecommendation,
    QuizReportData,
    QuizReportResponse,
    QuizStartResponse,
    QuizSubmitRequest,
)

SESSION_DURATION_MINUTES = 30
REWARD_POINTS = 80
DIMENSION_PRIORITY = ["R", "I", "A", "S", "E", "C"]
DIMENSION_LABELS = {
    "R": "现实型 R",
    "I": "研究型 I",
    "A": "艺术型 A",
    "S": "社会型 S",
    "E": "企业型 E",
    "C": "常规型 C",
}
MAX_RECOMMENDATIONS = 6


@dataclass(frozen=True)
class RecommendationResult:
    """封装职业推荐的内部结构。"""

    career: Career
    match_score: int
    raw_score: float
    contributing_dimensions: list[str]
    reason: str


class QuizService:
    def __init__(self, session: AsyncSession) -> None:
        """初始化测评服务。

        Args:
            session: SQLAlchemy 异步会话。
        """
        self.session = session
        self.repo = QuizRepository(session)

    async def start_quiz(self, user: User) -> QuizStartResponse:
        """创建或返回用户的进行中测评会话。

        Args:
            user: 当前登录用户。

        Returns:
            QuizStartResponse: 包含会话标识、过期时间与服务器时间。

        Raises:
            HTTPException: 当没有可用测评时返回 404。
        """
        quiz = await self.repo.get_latest_published_quiz()
        if not quiz:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="当前没有可用的测评")

        submission = await self.repo.get_active_submission_by_user(user.id)
        now = datetime.now(timezone.utc)

        if submission:
            if submission.expires_at <= now:
                submission.status = QuizSubmissionStatus.expired
                await self.session.commit()
            else:
                return QuizStartResponse(
                    session_id=submission.session_token,
                    expires_at=self._ensure_utc(submission.expires_at),
                    server_time=now,
                )

        session_token = uuid4().hex
        expires_at = now + timedelta(minutes=SESSION_DURATION_MINUTES)
        submission = await self.repo.create_submission(
            user_id=user.id,
            quiz_id=quiz.id,
            session_token=session_token,
            expires_at=expires_at,
        )
        await self.session.commit()
        return QuizStartResponse(
            session_id=submission.session_token,
            expires_at=self._ensure_utc(submission.expires_at),
            server_time=now,
        )

    async def get_questions(self, session_id: str, user: User) -> QuizQuestionsResponse:
        """返回测评题目及已作答情况。

        Args:
            session_id: 测评会话 ID。
            user: 当前登录用户。

        Returns:
            QuizQuestionsResponse: 包含题目、选项、已选答案及服务器时间。

        Raises:
            HTTPException: 会话不存在、已过期或不属于当前用户时抛出。
        """
        submission = await self._get_valid_submission(session_id, user)
        questions = await self.repo.list_questions_with_options(submission.quiz_id)
        answers_map = {answer.question_id: answer for answer in submission.answers}
        payload: list[QuizQuestion] = []
        for question in questions:
            existing_answer = answers_map.get(question.id)
            options = [
                QuizOption(id=option.id, text=option.content, dimension=option.dimension)
                for option in sorted(question.options, key=lambda opt: (opt.order, opt.id))
            ]
            selected_option_id = existing_answer.option_id if existing_answer else None
            selected_option_ids = (
                list(existing_answer.option_ids) if existing_answer and existing_answer.option_ids is not None else None
            )
            rating_value = existing_answer.rating_value if existing_answer else None
            payload.append(
                QuizQuestion(
                    question_id=question.id,
                    type=question.question_type.value,
                    title=question.title,
                    content=question.content,
                    options=options,
                    selected_option_id=selected_option_id,
                    selected_option_ids=selected_option_ids,
                    rating_value=rating_value,
                )
            )
        return QuizQuestionsResponse(
            session_id=session_id,
            questions=payload,
            server_time=datetime.now(timezone.utc),
        )

    async def answer_questions(self, request: QuizAnswerRequest, user: User) -> QuizAnswerResponse:
        """保存用户对题目的作答。

        Args:
            request: 包含会话 ID 与答案列表的请求体。
            user: 当前登录用户。

        Returns:
            QuizAnswerResponse: 保存成功后的提示信息。

        Raises:
            HTTPException: 当会话无效、题目或选项非法、状态不允许提交时。
        """
        submission = await self._get_valid_submission(request.session_id, user)
        if submission.status != QuizSubmissionStatus.in_progress:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="测评已结束，请重新开始")

        question_ids = [item.question_id for item in request.answers]
        question_map = await self.repo.list_questions_map(submission.quiz_id)
        missing_questions = [qid for qid in question_ids if qid not in question_map]
        if missing_questions:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="存在非法题目")

        option_map = await self.repo.list_options_map(question_ids)
        for answer in request.answers:
            if isinstance(answer, QuizMultipleChoiceAnswer):
                option_ids = self._deduplicate_option_ids(answer.option_ids)
                if not option_ids:
                    raise HTTPException(
                        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="多选题需至少选择一个选项"
                    )
                for option_id in option_ids:
                    option = option_map.get(option_id)
                    if not option or option.question_id != answer.question_id:
                        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="存在非法选项")
            elif answer.type == "single_choice":
                option = option_map.get(answer.option_id)
                if not option or option.question_id != answer.question_id:
                    raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="存在非法选项")
            elif isinstance(answer, QuizRatingAnswer):
                pass

        await self.repo.clear_answers_for_questions(submission.id, question_ids)

        for answer in request.answers:
            if isinstance(answer, QuizMultipleChoiceAnswer):
                option_ids = self._deduplicate_option_ids(answer.option_ids)
                await self.repo.add_answer(
                    submission_id=submission.id,
                    question_id=answer.question_id,
                    option_id=None,
                    option_ids=option_ids,
                    rating_value=None,
                    response_time=answer.response_time,
                )
            elif isinstance(answer, QuizRatingAnswer):
                await self.repo.add_answer(
                    submission_id=submission.id,
                    question_id=answer.question_id,
                    option_id=None,
                    option_ids=None,
                    rating_value=answer.rating_value,
                    response_time=answer.response_time,
                )
            else:
                await self.repo.add_answer(
                    submission_id=submission.id,
                    question_id=answer.question_id,
                    option_id=answer.option_id,
                    option_ids=None,
                    rating_value=None,
                    response_time=answer.response_time,
                )

        await self.session.commit()
        return QuizAnswerResponse(msg="答题已保存")

    async def submit_quiz(self, request: QuizSubmitRequest, user: User) -> QuizReportResponse:
        """提交测评并生成报告。

        Args:
            request: 包含会话 ID 的提交请求。
            user: 当前登录用户。

        Returns:
            QuizReportResponse: 测评报告及奖励信息。

        Raises:
            HTTPException: 会话状态异常、未作答或报告生成失败时抛出。
        """
        submission = await self._get_valid_submission(request.session_id, user)
        if submission.status == QuizSubmissionStatus.completed:
            if submission.report is None:
                raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="报告生成异常")
            report_data = QuizReportData.model_validate(submission.report.result_json)
            return QuizReportResponse(session_id=request.session_id, report=report_data)
        if submission.status != QuizSubmissionStatus.in_progress:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="测评已提交")

        answers = submission.answers
        if not answers:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="请先完成答题")

        dimension_scores = self._calculate_dimension_scores(answers, submission)
        holland_code = self._calculate_holland_code(dimension_scores)
        recommendation_results = await self._generate_recommendations(dimension_scores)
        recommendation_payload = [
            QuizRecommendation(
                profession_id=result.career.id,
                name=result.career.name,
                match_score=result.match_score,
                reason=result.reason,
            )
            for result in recommendation_results
        ]

        report_data = QuizReportData(
            holland_code=holland_code,
            dimension_scores=dimension_scores,
            recommendations=recommendation_payload,
            reward_points=REWARD_POINTS,
        )

        report = await self.repo.create_report(submission.id, report_data.model_dump())
        await self.repo.create_career_recommendations(
            report_id=report.id,
            items=[(result.career.id, float(result.match_score), result.reason) for result in recommendation_results],
        )
        submission.status = QuizSubmissionStatus.completed
        submission.completed_at = datetime.now(timezone.utc)
        await self._award_points(user.id, REWARD_POINTS, reason="完成职业兴趣测评")
        await self.session.commit()

        return QuizReportResponse(
            session_id=request.session_id,
            report=report_data,
        )

    async def get_report(self, session_id: str, user: User) -> QuizReportResponse:
        """获取指定会话的测评报告。

        Args:
            session_id: 测评会话 ID。
            user: 当前登录用户。

        Returns:
            QuizReportResponse: 已生成的测评报告。

        Raises:
            HTTPException: 会话未完成或不存在时抛出。
        """
        submission = await self._get_valid_submission(session_id, user)
        if submission.status != QuizSubmissionStatus.completed or not submission.report:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="测评尚未完成")

        report = submission.report
        payload = report.result_json
        report_data = QuizReportData.model_validate(payload)
        if report.career_recommendations:
            sorted_records = sorted(
                report.career_recommendations,
                key=lambda item: (-item.score, item.career_id),
            )
            payload_lookup = {
                entry.get("profession_id"): entry.get("name")
                for entry in payload.get("recommendations", [])
                if isinstance(entry, dict)
            }
            recommendations = []
            for record in sorted_records:
                name = (record.career.name if record.career else payload_lookup.get(record.career_id)) or "职业推荐"
                recommendations.append(
                    QuizRecommendation(
                        profession_id=record.career_id,
                        name=name,
                        match_score=int(record.score),
                        reason=record.match_reason or "",
                    )
                )
            report_data = report_data.model_copy(update={"recommendations": recommendations})
        return QuizReportResponse(session_id=session_id, report=report_data)

    async def _get_valid_submission(self, session_id: str, user: User) -> QuizSubmission:
        """校验并返回有效的测评会话。"""
        submission = await self.repo.get_submission_by_token(session_id)
        if not submission or submission.user_id != user.id:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="会话不存在")

        now = datetime.now(timezone.utc)
        expires_at = self._ensure_utc(submission.expires_at)
        if expires_at <= now and submission.status == QuizSubmissionStatus.in_progress:
            submission.status = QuizSubmissionStatus.expired
            await self.session.commit()
            raise HTTPException(status_code=status.HTTP_410_GONE, detail="测评会话已过期")

        return submission

    @staticmethod
    def _ensure_utc(dt: datetime) -> datetime:
        """确保时间为 UTC 时区。"""
        if dt.tzinfo is None:
            return dt.replace(tzinfo=timezone.utc)
        return dt.astimezone(timezone.utc)

    def _calculate_dimension_scores(
        self,
        answers: Iterable[QuizAnswer],
        submission: QuizSubmission,
    ) -> dict[str, int]:
        """根据答案累计各维度分值。"""
        score_map: dict[str, int] = {dimension: 0 for dimension in DIMENSION_PRIORITY}
        option_lookup: dict[int, Option] = {}
        for question in submission.quiz.questions:
            for option in question.options:
                option_lookup[option.id] = option

        for answer in answers:
            if answer.option_id is not None:
                option = option_lookup.get(answer.option_id)
                if option and option.dimension:
                    score_map.setdefault(option.dimension, 0)
                    score_map[option.dimension] += option.score
            if answer.option_ids:
                for option_id in answer.option_ids:
                    option = option_lookup.get(option_id)
                    if option and option.dimension:
                        score_map.setdefault(option.dimension, 0)
                        score_map[option.dimension] += option.score

        return score_map

    def _calculate_holland_code(self, scores: dict[str, int]) -> str:
        """依据维度分值生成霍兰德代码。"""
        sorted_items = sorted(
            scores.items(),
            key=lambda item: (-item[1], DIMENSION_PRIORITY.index(item[0]) if item[0] in DIMENSION_PRIORITY else 99),
        )
        top_three = [item[0] for item in sorted_items if item[1] > 0][:3]
        return "".join(top_three)

    async def _generate_recommendations(self, scores: dict[str, int]) -> list[RecommendationResult]:
        """根据维度得分生成职业推荐列表并返回带原始信息的结构。"""
        if not scores:
            return []

        careers = await self.repo.list_careers_for_dimensions()
        if not careers:
            return []

        candidates: list[tuple[Career, list[str], float, str]] = []
        for career in careers:
            dimensions = career.holland_dimensions or []
            contributing_dimensions = [dim for dim in dimensions if dim in scores and scores[dim] > 0]
            if not contributing_dimensions:
                continue

            contributing_dimensions.sort(
                key=lambda dim: (
                    -scores.get(dim, 0),
                    DIMENSION_PRIORITY.index(dim) if dim in DIMENSION_PRIORITY else 99,
                )
            )
            raw_score = float(sum(scores.get(dim, 0) for dim in contributing_dimensions))
            if raw_score <= 0:
                continue

            reason = self._build_match_reason(career, contributing_dimensions, scores)
            candidates.append((career, contributing_dimensions, raw_score, reason))

        if not candidates:
            return []

        max_raw_score = max(candidate[2] for candidate in candidates)
        sorted_candidates = sorted(
            candidates,
            key=lambda item: (
                -item[2],
                DIMENSION_PRIORITY.index(item[1][0]) if item[1] and item[1][0] in DIMENSION_PRIORITY else 99,
                item[0].id,
            ),
        )

        results: list[RecommendationResult] = []
        for career, dims, raw_score, reason in sorted_candidates[:MAX_RECOMMENDATIONS]:
            match_score = int(raw_score / max_raw_score * 100) if max_raw_score else 0
            results.append(
                RecommendationResult(
                    career=career,
                    match_score=match_score,
                    raw_score=raw_score,
                    contributing_dimensions=dims,
                    reason=reason,
                )
            )
        return results

    def _build_match_reason(
        self,
        career: Career,
        contributing_dimensions: list[str],
        scores: dict[str, int],
    ) -> str:
        """根据贡献维度与职业描述生成推荐理由。"""
        dimension_scores = "、".join(
            f"{self._format_dimension_label(dim)}({scores.get(dim, 0)})" for dim in contributing_dimensions
        )
        summary_source = career.description or career.career_outlook or "适合发挥您的兴趣优势"
        summary = summary_source.strip()
        if not summary:
            summary = "适合发挥您的兴趣优势"
        if summary[-1] not in "。.!！?:？":
            summary = f"{summary}。"
        return f"您在 {dimension_scores} 维度表现出色，{summary}"

    def _format_dimension_label(self, dimension: str) -> str:
        """将维度代码转成更易理解的标签。"""
        return DIMENSION_LABELS.get(dimension, dimension)

    async def _award_points(self, user_id: int, points: int, *, reason: str) -> None:
        """为用户增加积分并记录积分流水。"""
        if points <= 0:
            return
        user_points = await self.session.execute(select(UserPoints).where(UserPoints.user_id == user_id))
        user_points_instance = user_points.scalars().first()
        if not user_points_instance:
            user_points_instance = UserPoints(user_id=user_id, points=0)
            self.session.add(user_points_instance)
            await self.session.flush()
        user_points_instance.points += points
        transaction = PointTransaction(user_points_id=user_points_instance.id, amount=points, reason=reason)
        self.session.add(transaction)

    @staticmethod
    def _deduplicate_option_ids(option_ids: Iterable[int]) -> list[int]:
        """去重选项 ID 列表并保持顺序。"""
        return list(dict.fromkeys(option_ids))
