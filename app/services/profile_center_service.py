from __future__ import annotations

from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.extensions import FavoriteItemType
from app.models.user import User
from app.repositories.profile_center import ProfileCenterRepository
from app.repositories.quiz import QuizRepository
from app.schemas.profile_center import (
    DashboardRecommendation,
    DashboardResponse,
    ExplorationItem,
    ExplorationListResponse,
    ExplorationRecord,
    FavoriteListResponse,
    FavoriteRecord,
    HollandPortrait,
)
from app.schemas.user import UserProfileSummary, UserSetProfileRequest

HOLLAND_DESCRIPTIONS = {
    "R": "现实型：动手实践，坚韧可靠",
    "I": "研究型：分析思考，逻辑严谨",
    "A": "艺术型：创意表达，审美驱动",
    "S": "社会型：沟通协作，乐于助人",
    "E": "企业型：目标导向，影响驱动",
    "C": "常规型：秩序条理，执行稳健",
}


def _analysis_for_code(code: str) -> str:
    letters = [ch for ch in (code or "") if ch.isalpha()]
    if not letters:
        return "还没有测评记录，去做一次兴趣测评吧～"
    top = "、".join(HOLLAND_DESCRIPTIONS.get(letter, letter) for letter in letters[:3])
    # 组装一段自然语言说明
    return f"你的兴趣画像倾向于：{top}。这表明你更适合发挥这些优势的工作环境，建议在职业探索中优先关注与这些特质高度相关的岗位。"


class ProfileCenterService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.repo = ProfileCenterRepository(session)
        self.quiz_repo = QuizRepository(session)

    # ---- Profile ----
    async def get_profile(self, user: User) -> UserProfileSummary:
        db_user = await self.repo.get_user(user.id)
        points = await self.repo.get_or_create_points(user.id)
        return UserProfileSummary(
            avatar_url=db_user.avatar_url if db_user else None,
            nickname=db_user.nickname if db_user else None,
            description=(db_user.bio if db_user else None),
            total_points=points.points if points else 0,
        )

    async def set_profile(self, user: User, request: UserSetProfileRequest) -> None:
        # 头像/昵称复用既有 user 表字段，描述使用 UserExtra.bio
        db_user = await self.repo.get_user(user.id)
        if db_user:
            if request.avatar_url is not None:
                db_user.avatar_url = request.avatar_url
            if request.nickname is not None:
                db_user.nickname = request.nickname
            if request.description is not None:
                db_user.bio = request.description
        await self.session.commit()

    # ---- Dashboard ----
    async def get_dashboard(self, user: User) -> DashboardResponse:
        # 读取最近一次完成的测评报告
        report = await self.repo.get_latest_quiz_report(user.id)
        holland: Optional[HollandPortrait] = None
        recommendations: list[DashboardRecommendation] = []
        if report and isinstance(report.result_json, dict):
            payload = report.result_json
            code = payload.get("holland_code") or ""
            dim_scores = payload.get("dimension_scores") or {}
            holland = HollandPortrait(code=code, dimension_scores=dim_scores, analysis=_analysis_for_code(code))
            # 推荐结果可直接使用测评时生成的推荐
            recs = payload.get("recommendations") or []
            for item in recs:
                # item: { profession_id, name, match_score, reason }
                career_id = item.get("profession_id")
                name = item.get("name")
                ms = int(item.get("match_score")) if item.get("match_score") is not None else 0
                if isinstance(career_id, int):
                    recommendations.append(
                        DashboardRecommendation(career_id=career_id, name=name or "", match_score=ms)
                    )
        return DashboardResponse(holland=holland, recommendations=recommendations)

    # ---- Exploration ----
    async def upsert_explorations(self, user: User, items: list[ExplorationItem]) -> None:
        pairs = [(it.career_id, it.explored_blocks) for it in items]
        await self.repo.upsert_explorations(user.id, pairs)
        await self.session.commit()

    async def list_explorations(self, user: User) -> ExplorationListResponse:
        rows = await self.repo.list_explorations(user.id)
        records: list[ExplorationRecord] = []
        for progress, career in rows:
            explored = max(0, min(4, progress.explored_blocks))
            percent = int(explored / 4 * 100) if explored else 0
            records.append(
                ExplorationRecord(
                    career_id=progress.career_id,
                    career_name=(career.name if career else None),
                    explored_blocks=explored,
                    total_blocks=4,
                    progress_percent=percent,
                    updated_at=progress.updated_at,
                )
            )
        return ExplorationListResponse(items=records)

    # ---- Favorites ----
    async def add_favorite(self, user: User, item_type: FavoriteItemType, item_id: int) -> None:
        await self.repo.add_favorite(user.id, item_type, item_id)
        await self.session.commit()

    async def list_favorites(self, user: User) -> FavoriteListResponse:
        rows = await self.repo.list_favorites(user.id)
        items: list[FavoriteRecord] = []
        for fav, career in rows:
            name = None
            if fav.item_type == FavoriteItemType.career and career:
                name = career.name
            items.append(
                FavoriteRecord(
                    item_type=fav.item_type.value,  # type: ignore[arg-type]
                    item_id=fav.item_id,
                    name=name,
                    favorited_at=fav.created_at,
                )
            )
        return FavoriteListResponse(items=items)

    # ---- Wrongbook (placeholder) ----
    # 目前返回空数组，后续接入 Cosplay 错题计算逻辑
