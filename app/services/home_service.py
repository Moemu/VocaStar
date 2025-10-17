from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Iterable, List, Optional

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logger import logger
from app.models.career import Career, CareerGalaxy, CareerRecommendation
from app.models.extensions import PointTransaction, UserPoints
from app.models.quiz import QuizReport, QuizSubmission, QuizSubmissionStatus
from app.models.user import User
from app.schemas.home import (
    AbilityScore,
    CareerRecommendationItem,
    HomeSummaryResponse,
    PersonalOverview,
    PlanetProgress,
    PointEntry,
    TodayPointsSummary,
)
from app.schemas.quiz import QuizReportData
from app.services.quiz_service import DIMENSION_LABELS

_REFRESH_REASON = "适合探索者"
_SIGN_IN_REASON = "每日签到"
_SIGN_IN_POINTS = 50


class HomeService:
    """首页聚合信息服务。"""

    def _get_today_naive_range(self) -> tuple[datetime, datetime]:
        """获取当天起止的 naive datetime（无时区信息）。"""
        now = datetime.now(timezone.utc)
        start_of_day = now.replace(hour=0, minute=0, second=0, microsecond=0)
        end_of_day = start_of_day + timedelta(days=1)
        start_naive = start_of_day.replace(tzinfo=None)
        end_naive = end_of_day.replace(tzinfo=None)
        return start_naive, end_naive

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_home_summary(self, user: User, *, limit: int = 3) -> HomeSummaryResponse:
        """生成首页聚合信息。"""
        report, report_payload = await self._get_latest_report(user.id)

        planet_progress = await self._get_planet_progress(user)
        ability_scores = self._build_ability_scores(report_payload)
        await self._ensure_daily_sign_in(user)
        today_points = await self._get_today_points(user)
        recommendations = await self._get_recommendations(report, limit=limit)

        personal = PersonalOverview(
            planet_progress=planet_progress,
            ability_scores=ability_scores,
            today_points=today_points,
        )

        return HomeSummaryResponse(personal=personal, recommendations=recommendations)

    async def _get_planet_progress(self, user: User) -> PlanetProgress:
        """统计职业星球探索进度。当前全部默认解锁。"""
        total_stmt = select(func.count(Career.id))
        total_planets = (await self.session.execute(total_stmt)).scalar() or 0
        # TODO: 待接入真正的解锁逻辑，这里直接认为全部解锁
        return PlanetProgress(unlocked=total_planets, total=total_planets)

    async def _get_latest_report(self, user_id: int) -> tuple[Optional[QuizReport], Optional[QuizReportData]]:
        """获取用户最近一次完成的测评报告。"""
        stmt = (
            select(QuizReport)
            .join(QuizSubmission, QuizReport.submission_id == QuizSubmission.id)
            .where(QuizSubmission.user_id == user_id, QuizSubmission.status == QuizSubmissionStatus.completed)
            .order_by(QuizSubmission.completed_at.desc(), QuizReport.created_at.desc())
            .limit(1)
        )
        report = (await self.session.execute(stmt)).scalars().first()
        if not report:
            return None, None
        try:
            payload = QuizReportData.model_validate(report.result_json)
        except Exception as exc:  # pragma: no cover - 数据异常时记录方便排查
            logger.exception("解析 QuizReport JSON 失败 user_id=%s report_id=%s", user_id, report.id)
            logger.error("原始 JSON 内容: %s", report.result_json)
            logger.error("异常信息: %s", exc)
            payload = None
        return report, payload

    def _build_ability_scores(self, payload: Optional[QuizReportData]) -> List[AbilityScore]:
        if payload is None:
            return []
        dimension_scores = payload.dimension_scores or {}
        ability_items = [
            AbilityScore(
                code=code,
                name=DIMENSION_LABELS.get(code, code),
                score=float(score),
            )
            for code, score in dimension_scores.items()
        ]
        ability_items.sort(key=lambda item: item.score, reverse=True)
        return ability_items

    async def _ensure_daily_sign_in(self, user: User) -> None:
        """确保用户当日完成签到并获得积分。"""
        start_naive, end_naive = self._get_today_naive_range()

        exists_stmt = (
            select(PointTransaction.id)
            .join(UserPoints, PointTransaction.user_points_id == UserPoints.id)
            .where(
                UserPoints.user_id == user.id,
                PointTransaction.reason == _SIGN_IN_REASON,
                PointTransaction.created_at >= start_naive,
                PointTransaction.created_at < end_naive,
            )
            .limit(1)
        )
        already_signed_in = (await self.session.execute(exists_stmt)).scalar() is not None
        if already_signed_in:
            return

        user_points_stmt = select(UserPoints).where(UserPoints.user_id == user.id)
        user_points = (await self.session.execute(user_points_stmt)).scalars().first()
        if not user_points:
            user_points = UserPoints(user_id=user.id, points=0)
            self.session.add(user_points)
            await self.session.flush()

        user_points.points += _SIGN_IN_POINTS
        transaction = PointTransaction(
            user_points_id=user_points.id,
            amount=_SIGN_IN_POINTS,
            reason=_SIGN_IN_REASON,
        )
        self.session.add(transaction)
        logger.info("用户 %s 完成每日签到，奖励积分 %s", user.id, _SIGN_IN_POINTS)
        await self.session.commit()

    async def _get_today_points(self, user: User) -> TodayPointsSummary:
        """统计用户当日的积分情况。"""
        start_naive, end_naive = self._get_today_naive_range()

        base_query = (
            select(PointTransaction)
            .join(UserPoints, PointTransaction.user_points_id == UserPoints.id)
            .where(
                UserPoints.user_id == user.id,
                PointTransaction.created_at >= start_naive,
                PointTransaction.created_at < end_naive,
            )
            .order_by(PointTransaction.created_at.asc())
        )
        result = await self.session.execute(base_query)
        transactions = result.scalars().all()

        total = int(sum(txn.amount for txn in transactions))

        def _has_reason(keyword: str) -> bool:
            return any(txn.reason == keyword for txn in transactions)

        entries = [
            PointEntry(task="每日签到", status="已完成" if _has_reason(_SIGN_IN_REASON) else "未完成"),
            PointEntry(
                task="职业测评",
                status="已完成" if _has_reason("完成职业兴趣测评") else "未完成",
            ),
        ]
        return TodayPointsSummary(total=total, entries=entries)

    async def _get_recommendations(self, report: Optional[QuizReport], *, limit: int) -> List[CareerRecommendationItem]:
        counts_subquery = self._build_explorer_count_subquery()
        recommendations: List[CareerRecommendationItem] = []
        exclude_ids: set[int] = set()

        if report:
            recommendations = await self._fetch_report_recommendations(
                report_id=report.id,
                limit=limit,
                counts_subquery=counts_subquery,
            )
            exclude_ids = {item.career_id for item in recommendations}

        if len(recommendations) < limit:
            extra = await self._fetch_general_recommendations(
                limit=limit - len(recommendations),
                counts_subquery=counts_subquery,
                exclude_ids=exclude_ids,
            )
            recommendations.extend(extra)

        return recommendations

    def _build_explorer_count_subquery(self):
        return (
            select(
                CareerRecommendation.career_id.label("career_id"),
                func.count(func.distinct(QuizSubmission.user_id)).label("explorer_count"),
            )
            .join(QuizReport, CareerRecommendation.report_id == QuizReport.id)
            .join(QuizSubmission, QuizReport.submission_id == QuizSubmission.id)
            .group_by(CareerRecommendation.career_id)
            .subquery()
        )

    async def _fetch_report_recommendations(
        self,
        *,
        report_id: int,
        limit: int,
        counts_subquery,
    ) -> List[CareerRecommendationItem]:
        stmt = (
            select(
                Career,
                CareerGalaxy.name.label("galaxy_name"),
                func.coalesce(counts_subquery.c.explorer_count, 0).label("explorer_count"),
            )
            .join(Career, CareerRecommendation.career_id == Career.id)
            .join(CareerGalaxy, Career.galaxy_id == CareerGalaxy.id, isouter=True)
            .outerjoin(counts_subquery, counts_subquery.c.career_id == Career.id)
            .where(CareerRecommendation.report_id == report_id)
            .order_by(CareerRecommendation.score.desc(), Career.id)
            .limit(limit)
        )
        rows = (await self.session.execute(stmt)).all()
        return [
            self._build_recommendation_item(career, galaxy_name, explorer_count)
            for career, galaxy_name, explorer_count in rows
        ]

    async def _fetch_general_recommendations(
        self,
        *,
        limit: int,
        counts_subquery,
        exclude_ids: Iterable[int],
    ) -> List[CareerRecommendationItem]:
        if limit <= 0:
            return []
        stmt = (
            select(
                Career,
                CareerGalaxy.name.label("galaxy_name"),
                func.coalesce(counts_subquery.c.explorer_count, 0).label("explorer_count"),
            )
            .join(CareerGalaxy, Career.galaxy_id == CareerGalaxy.id, isouter=True)
            .outerjoin(counts_subquery, counts_subquery.c.career_id == Career.id)
            .order_by(func.random())
            .limit(limit)
        )
        exclude_ids = list(exclude_ids)
        if exclude_ids:
            stmt = stmt.where(~Career.id.in_(exclude_ids))
        rows = (await self.session.execute(stmt)).all()
        return [
            self._build_recommendation_item(career, galaxy_name, explorer_count)
            for career, galaxy_name, explorer_count in rows
        ]

    def _build_recommendation_item(
        self,
        career: Career,
        galaxy_name: Optional[str],
        explorer_count: Optional[int],
    ) -> CareerRecommendationItem:
        return CareerRecommendationItem(
            career_id=career.id,
            name=career.name,
            galaxy_name=galaxy_name,
            image_url=career.cover or career.planet_image_url,
            description=career.description,
            reason=_REFRESH_REASON,
            explorer_count=int(explorer_count or 0),
        )
