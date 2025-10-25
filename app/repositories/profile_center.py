from __future__ import annotations

from typing import Optional, Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.career import Career, CareerRecommendation
from app.models.extensions import (
    ExplorationProgress,
    Favorite,
    FavoriteItemType,
    UserPoints,
)
from app.models.quiz import QuizReport, QuizSubmission, QuizSubmissionStatus
from app.models.user import User


class ProfileCenterRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    # --- User, Points, Extra ---
    async def get_user(self, user_id: int) -> Optional[User]:
        stmt = select(User).where(User.id == user_id).options(selectinload(User.user_points))
        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def get_or_create_points(self, user_id: int) -> UserPoints:
        stmt = select(UserPoints).where(UserPoints.user_id == user_id)
        result = await self.session.execute(stmt)
        points = result.scalars().first()
        if points:
            return points
        points = UserPoints(user_id=user_id, points=0)
        self.session.add(points)
        await self.session.flush()
        await self.session.refresh(points)
        return points

    # User.bio 直接存入 users 表，不再使用独立的 UserExtra 表

    # --- Holland via latest quiz report ---
    async def get_latest_quiz_report(self, user_id: int) -> Optional[QuizReport]:
        order_key = QuizSubmission.completed_at
        stmt = (
            select(QuizSubmission)
            .where(QuizSubmission.user_id == user_id, QuizSubmission.status == QuizSubmissionStatus.completed)
            .order_by(order_key.desc(), QuizSubmission.id.desc())
            .limit(1)
            .options(
                selectinload(QuizSubmission.report)
                .selectinload(QuizReport.career_recommendations)
                .selectinload(CareerRecommendation.career)
            )
        )
        result = await self.session.execute(stmt)
        submission = result.scalars().first()
        if submission and submission.report:
            return submission.report
        return None

    # --- Exploration ---
    async def upsert_explorations(self, user_id: int, items: Sequence[tuple[int, int]]) -> None:
        if not items:
            return
        # Load existing
        career_ids = tuple({cid for cid, _ in items})
        stmt = select(ExplorationProgress).where(
            ExplorationProgress.user_id == user_id, ExplorationProgress.career_id.in_(career_ids)
        )
        result = await self.session.execute(stmt)
        existing = {row.career_id: row for row in result.scalars().all()}

        for career_id, explored in items:
            explored_clamped = max(0, min(4, int(explored)))
            rec = existing.get(career_id)
            if rec:
                # 不回退进度：只保留较大值
                rec.explored_blocks = max(rec.explored_blocks, explored_clamped)
            else:
                self.session.add(
                    ExplorationProgress(user_id=user_id, career_id=career_id, explored_blocks=explored_clamped)
                )

    async def list_explorations(self, user_id: int) -> list[tuple[ExplorationProgress, Optional[Career]]]:
        stmt = select(ExplorationProgress).where(ExplorationProgress.user_id == user_id)
        result = await self.session.execute(stmt)
        progresses = list(result.scalars().all())
        # Attach career names
        if not progresses:
            return []
        career_ids = [p.career_id for p in progresses]
        stmt2 = select(Career).where(Career.id.in_(tuple(set(career_ids))))
        result2 = await self.session.execute(stmt2)
        career_map = {c.id: c for c in result2.scalars().all()}
        return [(p, career_map.get(p.career_id)) for p in progresses]

    # --- Favorites ---
    async def add_favorite(self, user_id: int, item_type: FavoriteItemType, item_id: int) -> Favorite:
        stmt = select(Favorite).where(
            Favorite.user_id == user_id, Favorite.item_type == item_type, Favorite.item_id == item_id
        )
        result = await self.session.execute(stmt)
        fav = result.scalars().first()
        if fav:
            return fav
        fav = Favorite(user_id=user_id, item_type=item_type, item_id=item_id)
        self.session.add(fav)
        await self.session.flush()
        await self.session.refresh(fav)
        return fav

    async def list_favorites(self, user_id: int) -> list[tuple[Favorite, Optional[Career]]]:
        stmt = select(Favorite).where(Favorite.user_id == user_id).order_by(Favorite.created_at.desc())
        result = await self.session.execute(stmt)
        favs = list(result.scalars().all())
        if not favs:
            return []
        career_ids = [f.item_id for f in favs if f.item_type == FavoriteItemType.career]
        career_map: dict[int, Career] = {}
        if career_ids:
            result2 = await self.session.execute(select(Career).where(Career.id.in_(tuple(set(career_ids)))))
            career_map = {c.id: c for c in result2.scalars().all()}
        return [(f, (career_map.get(f.item_id) if f.item_type == FavoriteItemType.career else None)) for f in favs]
