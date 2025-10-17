from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Iterable, List, Optional, Tuple, cast
from uuid import uuid4

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logger import logger
from app.models.career import Career
from app.models.extensions import PointTransaction, UserPoints
from app.models.quiz import (
    Option,
    Question,
    QuestionType,
    QuizAnswer,
    QuizSubmission,
    QuizSubmissionStatus,
    UserProfile,
)
from app.models.user import User
from app.repositories.quiz import QuizRepository
from app.schemas.quiz import (
    QuestionSettings,
    QuestionSettingsModel,
    QuizAnswerRequest,
    QuizAnswerResponse,
    QuizClassicScenarioAnswer,
    QuizImagePreferenceAnswer,
    QuizLegacyAllocationAnswer,
    QuizLegacyMetricsAnswer,
    QuizLegacyMultipleChoiceAnswer,
    QuizLegacySingleChoiceAnswer,
    QuizOption,
    QuizProfileRequest,
    QuizProfileResponse,
    QuizQuestion,
    QuizQuestionsResponse,
    QuizRatingAnswer,
    QuizRecommendation,
    QuizReportData,
    QuizReportResponse,
    QuizScoringConfig,
    QuizScoringConfigModel,
    QuizStartResponse,
    QuizSubmitRequest,
    QuizTimeAllocationAnswer,
    QuizValueBalanceAnswer,
    QuizWordChoiceAnswer,
)

SESSION_DURATION_MINUTES = 30
REWARD_POINTS = 50
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

    async def start_quiz(self, user: User, *, slug: Optional[str] = None) -> QuizStartResponse:
        """创建或返回用户的进行中测评会话。

        Args:
            user: 当前登录用户。
            slug: 指定的测评题库标识，若为空则默认选择最新发布的测评。

        Returns:
            QuizStartResponse: 包含会话标识、过期时间与服务器时间。

        Raises:
            HTTPException: 当没有可用测评时返回 404; 当未填写个性化档案时返回 400。
        """
        if slug:
            quiz = await self.repo.get_published_quiz_by_slug(slug)
            if not quiz:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="指定的测评暂未发布")
        else:
            quiz = await self.repo.get_latest_published_quiz()
            if not quiz:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="当前没有可用的测评")

        # 检查用户是否已有进行中的测评
        submission = await self.repo.get_active_submission_by_user(user.id, quiz_id=quiz.id)
        now = datetime.now(timezone.utc)

        if submission:
            expires_at = self._ensure_utc(submission.expires_at)
            if expires_at <= now:
                submission.status = QuizSubmissionStatus.expired
                await self.session.commit()
            else:
                return QuizStartResponse(
                    session_id=submission.session_token,
                    expires_at=expires_at,
                    server_time=now,
                )

        # 检查用户是否已完成个性化档案的填写
        # profile = await self.get_profile(user)
        # if not profile:
        #     raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="请先完成个性化档案的填写")

        # 创建新的测评会话
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
                QuizOption(
                    id=option.id,
                    text=option.content,
                    dimension=option.dimension,
                    image_url=option.image_url,
                )
                for option in sorted(question.options, key=lambda opt: (opt.order, opt.id))
            ]
            selected_option_id = existing_answer.option_id if existing_answer else None
            selected_option_ids = (
                list(existing_answer.option_ids) if existing_answer and existing_answer.option_ids is not None else None
            )
            rating_value = existing_answer.rating_value if existing_answer else None
            metric_values = None
            allocations = None
            if existing_answer and existing_answer.extra_payload:
                raw_values = existing_answer.extra_payload.get("values")
                if isinstance(raw_values, dict):
                    metric_values = {str(key): float(value) for key, value in raw_values.items()}
                raw_allocations = existing_answer.extra_payload.get("allocations")
                if isinstance(raw_allocations, dict):
                    allocations = {str(key): float(value) for key, value in raw_allocations.items()}
            raw_settings: Any = question.settings or {}
            try:
                validated_settings = QuestionSettingsModel.model_validate(raw_settings)
                settings_payload = cast(QuestionSettings, validated_settings.model_dump(exclude_none=True))
            except Exception:
                settings_payload = cast(QuestionSettings, {})
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
                    metric_values=metric_values,
                    allocations=allocations,
                    settings=settings_payload,
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
            question = question_map.get(answer.question_id)
            if question is None:
                raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="题目不存在或已失效")
            question_type = question.question_type

            if isinstance(
                answer,
                (QuizWordChoiceAnswer, QuizImagePreferenceAnswer, QuizLegacyMultipleChoiceAnswer),
            ):
                if isinstance(answer, QuizLegacyMultipleChoiceAnswer):
                    logger.warning("检测到已弃用的答案类型 multiple_choice，请迁移至题目类型字符串")

                option_ids = self._deduplicate_option_ids(answer.option_ids)
                if not option_ids:
                    raise HTTPException(
                        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="多选题需至少选择一个选项"
                    )
                try:
                    settings = QuestionSettingsModel.model_validate(question.settings or {})
                    max_select = settings.max_select
                except Exception as e:
                    raise HTTPException(
                        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=f"题目配置验证失败: {str(e)}"
                    ) from e

                if max_select is not None and len(option_ids) > max_select:
                    raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="超过可选择的最大数量")
                for option_id in option_ids:
                    option = option_map.get(option_id)
                    if not option or option.question_id != answer.question_id:
                        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="存在非法选项")
            elif isinstance(answer, (QuizClassicScenarioAnswer, QuizLegacySingleChoiceAnswer)):
                if isinstance(answer, QuizLegacySingleChoiceAnswer):
                    logger.warning("检测到已弃用的答案类型 single_choice，请迁移至题目类型字符串")

                option = option_map.get(answer.option_id)
                if not option or option.question_id != answer.question_id:
                    raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="存在非法选项")
            elif isinstance(answer, QuizRatingAnswer):
                if answer.rating_value is None:
                    raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="评分题答案无效")
            elif isinstance(answer, (QuizValueBalanceAnswer, QuizLegacyMetricsAnswer)):
                if question_type != QuestionType.value_balance:
                    raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="答案类型与题目不匹配")
                if not answer.values:
                    raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="请完成滑块题的填写")
            elif isinstance(answer, (QuizTimeAllocationAnswer, QuizLegacyAllocationAnswer)):
                if question_type != QuestionType.time_allocation:
                    raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="答案类型与题目不匹配")
                if not answer.allocations:
                    raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="请完成分配题的填写")
            else:
                raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="暂不支持的答案类型")

        await self.repo.clear_answers_for_questions(submission.id, question_ids)

        for answer in request.answers:
            if isinstance(
                answer,
                (QuizWordChoiceAnswer, QuizImagePreferenceAnswer, QuizLegacyMultipleChoiceAnswer),
            ):
                option_ids = self._deduplicate_option_ids(answer.option_ids)
                await self.repo.add_answer(
                    submission_id=submission.id,
                    question_id=answer.question_id,
                    option_id=None,
                    option_ids=option_ids,
                    rating_value=None,
                    response_time=answer.response_time,
                    extra_payload=None,
                )
            elif isinstance(answer, QuizRatingAnswer):
                await self.repo.add_answer(
                    submission_id=submission.id,
                    question_id=answer.question_id,
                    option_id=None,
                    option_ids=None,
                    rating_value=answer.rating_value,
                    response_time=answer.response_time,
                    extra_payload=None,
                )
            elif isinstance(answer, (QuizValueBalanceAnswer, QuizLegacyMetricsAnswer)):
                normalized_values = {str(key): float(value) for key, value in answer.values.items()}
                await self.repo.add_answer(
                    submission_id=submission.id,
                    question_id=answer.question_id,
                    option_id=None,
                    option_ids=None,
                    rating_value=None,
                    response_time=answer.response_time,
                    extra_payload={"values": normalized_values},
                )
            elif isinstance(answer, (QuizTimeAllocationAnswer, QuizLegacyAllocationAnswer)):
                normalized_allocations = {str(key): float(value) for key, value in answer.allocations.items()}
                await self.repo.add_answer(
                    submission_id=submission.id,
                    question_id=answer.question_id,
                    option_id=None,
                    option_ids=None,
                    rating_value=None,
                    response_time=answer.response_time,
                    extra_payload={"allocations": normalized_allocations},
                )
            elif isinstance(answer, (QuizClassicScenarioAnswer, QuizLegacySingleChoiceAnswer)):
                await self.repo.add_answer(
                    submission_id=submission.id,
                    question_id=answer.question_id,
                    option_id=answer.option_id,
                    option_ids=None,
                    rating_value=None,
                    response_time=answer.response_time,
                    extra_payload=None,
                )
            else:
                raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="暂不支持的答案类型")

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

        dimension_scores, component_scores = self._calculate_dimension_scores(answers, submission)
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
            component_scores=component_scores or None,
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

    async def get_report(
        self,
        user: User,
        *,
        session_id: Optional[str] = None,
        slug: Optional[str] = None,
    ) -> QuizReportResponse:
        """获取用户最新的测评报告。

        Args:
            user: 当前登录用户。
            session_id: 可选的测评会话 ID。
            slug: 可选的测评题库标识，用于筛选特定测评。

        Returns:
            QuizReportResponse: 已生成的测评报告。

        Raises:
            HTTPException: 测评未完成、会话不存在或未找到可用报告时抛出。
        """
        submission: Optional[QuizSubmission]
        if session_id:
            submission = await self._get_valid_submission(session_id, user)
            if submission.status != QuizSubmissionStatus.completed or not submission.report:
                raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="测评尚未完成")
            if slug:
                quiz_config = submission.quiz.config or {}
                if isinstance(quiz_config, dict) and quiz_config.get("slug") != slug:
                    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="会话不属于指定测评")
        else:
            submission = await self.repo.get_latest_completed_submission(user.id, slug=slug)
            if not submission:
                detail = "未找到对应测评报告" if slug else "暂无可用的测评报告"
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=detail)
            if not submission.report:
                raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="测评报告数据缺失")

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
        return QuizReportResponse(session_id=submission.session_token, report=report_data)

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
    ) -> Tuple[dict[str, int], dict[str, dict[str, float]]]:
        """根据测评配置计算维度分数及组件得分。"""

        answers_list = list(answers)
        quiz_config = submission.quiz.config
        scoring_config = quiz_config.get("scoring", QuizScoringConfig()) if quiz_config else QuizScoringConfig()
        strategy = scoring_config.get("strategy") if isinstance(scoring_config, dict) else None

        if strategy == "count_based":
            return self._calculate_count_based_scores(answers_list, submission, scoring_config)
        if strategy == "weighted_components":
            return self._calculate_weighted_component_scores(answers_list, submission, scoring_config)

        legacy_scores = self._calculate_legacy_scores(answers_list, submission)
        return legacy_scores, {}

    def _calculate_legacy_scores(
        self,
        answers: Iterable[QuizAnswer],
        submission: QuizSubmission,
    ) -> dict[str, int]:
        """默认的计分方式，按选项维度计数。"""

        option_lookup = self._build_option_lookup(submission)
        score_map: dict[str, int] = {dimension: 0 for dimension in DIMENSION_PRIORITY}
        for answer in answers:
            if answer.option_id is not None:
                option = option_lookup.get(answer.option_id)
                if option and option.dimension:
                    score_map[option.dimension] = score_map.get(option.dimension, 0) + 1
            if answer.option_ids:
                for option_id in answer.option_ids:
                    option = option_lookup.get(option_id)
                    if option and option.dimension:
                        score_map[option.dimension] = score_map.get(option.dimension, 0) + 1
        return score_map

    def _calculate_count_based_scores(
        self,
        answers: Iterable[QuizAnswer],
        submission: QuizSubmission,
        scoring_config: QuizScoringConfig,
    ) -> Tuple[dict[str, int], dict[str, dict[str, float]]]:
        """基于出现次数的计分策略。

        使用 Pydantic 验证配置，简化了类型检查逻辑。
        """
        option_lookup = self._build_option_lookup(submission)
        counts: Dict[str, int] = defaultdict(int)
        dimension_max_occurrences: Dict[str, int] = defaultdict(int)

        # 统计各维度出现次数
        for answer in answers:
            if answer.option_id is not None:
                option = option_lookup.get(answer.option_id)
                if option and option.dimension:
                    counts[option.dimension] += 1
            if answer.option_ids:
                for option_id in answer.option_ids:
                    option = option_lookup.get(option_id)
                    if option and option.dimension:
                        counts[option.dimension] += 1

        # 动态计算各维度的理论最大出现次数（按题目中是否包含该维度统计）
        quiz_questions = submission.quiz.questions or []
        for question in quiz_questions:
            if not question.options:
                continue
            dims_in_question = {opt.dimension for opt in question.options if opt.dimension}
            for dim in dims_in_question:
                dimension_max_occurrences[dim] += 1

        # 使用 Pydantic 验证配置
        try:
            validated_config = QuizScoringConfigModel.model_validate(scoring_config or {})
            dimension_formulas = validated_config.dimension_formulas or {}
        except Exception:
            dimension_formulas = {}

        component_scores: dict[str, dict[str, float]] = {"classic_scenario": {}}
        final_scores: dict[str, int] = {}

        # 根据配置计算各维度得分
        for dimension, formula_cfg in dimension_formulas.items():
            raw_count = counts.get(dimension, 0)
            computed_max = dimension_max_occurrences.get(dimension, raw_count)
            max_occurrences_val = formula_cfg.max_occurrences or computed_max
            max_occurrences_val = max(max_occurrences_val, 1)
            clamped_count = min(raw_count, max_occurrences_val)

            # 计算得分（避免执行外部表达式，固定为百分制算法）
            score_value = (clamped_count / max_occurrences_val) * 100

            score_value = max(0.0, min(100.0, score_value))
            component_scores["classic_scenario"][dimension] = round(score_value, 2)
            final_scores[dimension] = int(round(score_value))

        # 处理未配置公式的维度
        for dimension, count in counts.items():
            if dimension not in final_scores:
                max_occurs = dimension_max_occurrences.get(dimension, count)
                max_occurs = max(max_occurs, 1)
                clamped_count = min(count, max_occurs)
                score_value = (clamped_count / max_occurs) * 100
                component_scores["classic_scenario"][dimension] = round(score_value, 2)
                final_scores[dimension] = int(round(score_value))

        # 确保所有标准维度都有值
        for dimension in DIMENSION_PRIORITY:
            final_scores.setdefault(dimension, 0)
            component_scores["classic_scenario"].setdefault(dimension, 0.0)

        return final_scores, component_scores

    def _calculate_weighted_component_scores(
        self,
        answers: Iterable[QuizAnswer],
        submission: QuizSubmission,
        scoring_config: QuizScoringConfig,
    ) -> Tuple[dict[str, int], dict[str, dict[str, float]]]:
        """按题型权重聚合的计分策略。

        该方法协调各个子步骤完成加权计分：
        1. 计算各题型的理论最高分
        2. 累计用户实际得分
        3. 归一化为百分制
        4. 应用权重聚合
        """
        question_map = {question.id: question for question in submission.quiz.questions}
        option_lookup = self._build_option_lookup(submission)

        # 步骤 1: 计算理论最高分
        component_possible = self._calculate_possible_scores(submission.quiz.questions)

        # 步骤 2: 累计实际得分
        component_raw = self._accumulate_actual_scores(answers, question_map, option_lookup)

        # 步骤 3: 归一化为百分制
        component_scores = self._normalize_to_percentage(component_raw, component_possible)

        # 步骤 4: 应用权重聚合
        dimension_scores = self._apply_weights(component_scores, scoring_config)

        return dimension_scores, component_scores

    def _calculate_possible_scores(
        self,
        questions: Iterable[Question],
    ) -> Dict[str, Dict[str, float]]:
        """计算各题型各维度的理论最高分。

        Args:
            questions: 测评的所有题目列表

        Returns:
            嵌套字典 {题型: {维度: 最高分}}
        """
        component_possible: Dict[str, Dict[str, float]] = defaultdict(lambda: defaultdict(float))

        for question in questions:
            component = question.question_type.value

            # 使用 Pydantic 验证和解析配置
            try:
                settings = QuestionSettingsModel.model_validate(question.settings or {})
            except Exception:
                settings = QuestionSettingsModel.model_validate({})

            if question.question_type in {
                QuestionType.classic_scenario,
                QuestionType.image_preference,
                QuestionType.word_choice,
            }:
                # 选择题型：计算每个维度的最高可得分
                max_select = self._get_max_select(question, settings)
                per_dimension_scores: Dict[str, list[float]] = defaultdict(list)

                for option in question.options:
                    if option.dimension:
                        per_dimension_scores[option.dimension].append(float(option.score or 0) or 1.0)

                for dimension, scores in per_dimension_scores.items():
                    scores.sort(reverse=True)
                    limit = min(max_select, len(scores))
                    component_possible[component][dimension] += sum(scores[:limit])

            elif question.question_type == QuestionType.value_balance:
                # 价值观天平：最高分为滑块最大值
                max_value = settings.scale.max_value if settings.scale else 100.0
                if settings.dimensions:
                    for entry in settings.dimensions:
                        component_possible[component][entry.dimension] += max_value

            elif question.question_type == QuestionType.time_allocation:
                # 时间分配：最高分为总可分配时间
                max_hours = settings.max_hours or 0.0
                if settings.activities:
                    for activity in settings.activities:
                        if activity.dimension and max_hours > 0:
                            component_possible[component][activity.dimension] += max_hours

        return component_possible

    def _get_max_select(self, question: Question, settings: QuestionSettingsModel) -> int:
        """获取题目的最大可选数量。"""
        if question.question_type == QuestionType.word_choice:
            return settings.max_select or len(question.options)
        return 1

    def _accumulate_actual_scores(
        self,
        answers: Iterable[QuizAnswer],
        question_map: Dict[int, Question],
        option_lookup: Dict[int, Option],
    ) -> Dict[str, Dict[str, float]]:
        """累计用户实际得分。

        Args:
            answers: 用户提交的答案列表
            question_map: 题目ID到题目对象的映射
            option_lookup: 选项ID到选项对象的映射

        Returns:
            嵌套字典 {题型: {维度: 实际得分}}
        """
        component_raw: Dict[str, Dict[str, float]] = defaultdict(lambda: defaultdict(float))

        for answer in answers:
            question = question_map.get(answer.question_id)
            if not question:
                continue
            component = question.question_type.value

            # 处理单选答案
            if answer.option_id is not None:
                option = option_lookup.get(answer.option_id)
                if option and option.dimension:
                    component_raw[component][option.dimension] += float(option.score or 0) or 1.0

            # 处理多选答案
            if answer.option_ids:
                for option_id in answer.option_ids:
                    option = option_lookup.get(option_id)
                    if option and option.dimension:
                        component_raw[component][option.dimension] += float(option.score or 0) or 1.0

            # 处理扩展答案（价值观天平、时间分配）
            if answer.extra_payload and isinstance(answer.extra_payload, dict):
                try:
                    settings = QuestionSettingsModel.model_validate(question.settings or {})
                except Exception:
                    settings = QuestionSettingsModel.model_validate({})

                if question.question_type == QuestionType.value_balance:
                    self._accumulate_value_balance_score(answer, component, component_raw, settings)
                elif question.question_type == QuestionType.time_allocation:
                    self._accumulate_time_allocation_score(answer, component, component_raw, settings)

        return component_raw

    def _accumulate_value_balance_score(
        self,
        answer: QuizAnswer,
        component: str,
        component_raw: Dict[str, Dict[str, float]],
        settings: QuestionSettingsModel,
    ) -> None:
        """累计价值观天平题的得分。"""
        if not answer.extra_payload:
            return
        values = answer.extra_payload.get("values")
        if not isinstance(values, dict) or not settings.dimensions:
            return

        for key, value in values.items():
            dimension = self._resolve_dimension_from_validated_settings(key, settings.dimensions)
            if dimension:
                try:
                    component_raw[component][dimension] += float(value)
                except (TypeError, ValueError):
                    continue

    def _accumulate_time_allocation_score(
        self,
        answer: QuizAnswer,
        component: str,
        component_raw: Dict[str, Dict[str, float]],
        settings: QuestionSettingsModel,
    ) -> None:
        """累计时间分配题的得分。"""
        if not answer.extra_payload:
            return
        allocations = answer.extra_payload.get("allocations")
        if not isinstance(allocations, dict) or not settings.activities:
            return

        for key, value in allocations.items():
            dimension = self._resolve_dimension_from_validated_settings(key, settings.activities)
            if dimension:
                try:
                    component_raw[component][dimension] += float(value)
                except (TypeError, ValueError):
                    continue

    def _resolve_dimension_from_validated_settings(
        self,
        key: str,
        entries: Optional[List],
    ) -> Optional[str]:
        """从已验证的设置中解析维度代码。

        Args:
            key: 用户提交的键值
            entries: 维度或活动条目列表

        Returns:
            对应的维度代码，如果找不到返回 None
        """
        if not entries:
            return None

        key_str = str(key)
        for entry in entries:
            if not hasattr(entry, "dimension"):
                continue
            dimension = entry.dimension
            if not dimension:
                continue
            # 尝试匹配维度、标签等字段
            candidates = {
                str(dimension),
                str(getattr(entry, "label", "")),
            }
            if key_str in candidates:
                return dimension

        # 如果没有匹配，检查是否是有效的维度代码
        if key_str in DIMENSION_PRIORITY:
            return key_str
        return None

    def _normalize_to_percentage(
        self,
        component_raw: Dict[str, Dict[str, float]],
        component_possible: Dict[str, Dict[str, float]],
    ) -> dict[str, dict[str, float]]:
        """将原始得分归一化为百分制。

        Args:
            component_raw: 实际得分
            component_possible: 理论最高分

        Returns:
            归一化后的百分制得分
        """
        component_scores: dict[str, dict[str, float]] = {}

        for component, dim_scores in component_raw.items():
            comp_result: dict[str, float] = {}
            possible_map = component_possible.get(component, {})

            for dimension, raw_value in dim_scores.items():
                possible = possible_map.get(dimension, 0.0)
                if possible > 0:
                    percentage = (raw_value / possible) * 100
                else:
                    percentage = raw_value
                comp_result[dimension] = round(max(0.0, min(100.0, percentage)), 2)

            # 确保所有可能的维度都有值（未答题的维度为0）
            for dimension, possible in possible_map.items():
                comp_result.setdefault(dimension, 0.0)

            component_scores[component] = comp_result

        # 确保所有题型都有完整的维度映射
        for component_name, possible_map in component_possible.items():
            if component_name not in component_scores:
                component_scores[component_name] = {}
            existing_scores = component_scores[component_name]
            for dimension in possible_map.keys():
                existing_scores.setdefault(dimension, 0.0)

        return component_scores

    def _apply_weights(
        self,
        component_scores: dict[str, dict[str, float]],
        scoring_config: QuizScoringConfig,
    ) -> dict[str, int]:
        """应用权重聚合各题型得分。

        Args:
            component_scores: 各题型的百分制得分
            scoring_config: 计分配置（包含权重信息）

        Returns:
            最终的维度得分（整数）
        """
        # 使用 Pydantic 验证配置
        try:
            validated_config = QuizScoringConfigModel.model_validate(scoring_config or {})
            weights_cfg = validated_config.weights or {}
        except Exception:
            weights_cfg = {}

        # 提取权重
        weights: dict[str, float] = {}
        for component in component_scores.keys():
            weight_value = weights_cfg.get(component, 0.0)
            weights[component] = float(weight_value) if isinstance(weight_value, (int, float)) else 0.0

        total_weight = sum(weight for weight in weights.values() if weight > 0)

        # 如果没有配置权重，使用均匀权重
        if total_weight <= 0:
            uniform_weight = 1.0 if component_scores else 0.0
            weights = {component: uniform_weight for component in component_scores.keys()}
            total_weight = uniform_weight * len(component_scores)

        # 计算加权平均
        dimension_scores: dict[str, int] = {}
        for dimension in DIMENSION_PRIORITY:
            weighted_sum = 0.0
            for component, comp_scores in component_scores.items():
                weight = weights.get(component, 0.0)
                if weight <= 0:
                    continue
                weighted_sum += comp_scores.get(dimension, 0.0) * weight

            if total_weight > 0:
                value = weighted_sum / total_weight
            else:
                value = 0.0
            dimension_scores[dimension] = int(round(max(0.0, min(100.0, value))))

        # 确保所有维度都有值
        for scores in component_scores.values():
            for dimension, score in scores.items():
                dimension_scores.setdefault(dimension, int(round(score)))

        return dimension_scores

    @staticmethod
    def _build_option_lookup(submission: QuizSubmission) -> dict[int, Option]:
        """生成选项快速索引。"""

        lookup: dict[int, Option] = {}
        for question in submission.quiz.questions:
            for option in question.options:
                lookup[option.id] = option
        return lookup

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

    async def save_profile(self, request: QuizProfileRequest, user: User) -> QuizProfileResponse:
        """保存或更新用户个性化档案。

        Args:
            request: 档案数据。
            user: 当前登录用户。

        Returns:
            QuizProfileResponse: 完整的档案信息。

        Raises:
            HTTPException: 验证失败时抛出。
        """
        # 验证职业阶段选项
        valid_stages = {"高中生", "大学生", "职场新人", "资深宇航员", "星际指挥官"}
        if request.career_stage not in valid_stages:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
                detail=f"职业阶段无效，仅支持：{', '.join(valid_stages)}",
            )

        # 验证短期目标非空
        if not request.short_term_goals or all(not goal.strip() for goal in request.short_term_goals):
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
                detail="短期目标不能为空",
            )

        # 查找或创建档案
        result = await self.session.execute(select(UserProfile).where(UserProfile.user_id == user.id))
        profile = result.scalars().first()

        if profile:
            # 更新现有档案
            profile.career_stage = request.career_stage
            profile.major = request.major.strip()
            profile.career_confusion = request.career_confusion.strip()
            profile.short_term_goals = [goal.strip() for goal in request.short_term_goals if goal.strip()]
        else:
            # 创建新档案
            profile = UserProfile(
                user_id=user.id,
                career_stage=request.career_stage,
                major=request.major.strip(),
                career_confusion=request.career_confusion.strip(),
                short_term_goals=[goal.strip() for goal in request.short_term_goals if goal.strip()],
            )
            self.session.add(profile)

        await self.session.commit()
        await self.session.refresh(profile)

        return QuizProfileResponse(
            career_stage=profile.career_stage,
            major=profile.major,
            career_confusion=profile.career_confusion,
            short_term_goals=profile.short_term_goals,
            created_at=profile.created_at,
            updated_at=profile.updated_at,
        )

    async def get_profile(self, user: User) -> Optional[QuizProfileResponse]:
        """获取用户个性化档案。

        Args:
            user: 当前登录用户。

        Returns:
            QuizProfileResponse: 档案信息，不存在时返回 None。
        """
        result = await self.session.execute(select(UserProfile).where(UserProfile.user_id == user.id))
        profile = result.scalars().first()

        if not profile:
            return None

        return QuizProfileResponse(
            career_stage=profile.career_stage,
            major=profile.major,
            career_confusion=profile.career_confusion,
            short_term_goals=profile.short_term_goals,
            created_at=profile.created_at,
            updated_at=profile.updated_at,
        )

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
