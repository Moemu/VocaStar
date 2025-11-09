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
    WrongbookItem,
    WrongbookListResponse,
)
from app.schemas.user import UserProfileSummary, UserSetProfileRequest
from app.services.achievement_service import AchievementService

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
            # 只保留 unique_advantage；若为空则回退到基于 code 的分析文案
            ua = payload.get("unique_advantage")
            if not ua:
                ua = _analysis_for_code(code)
            holland = HollandPortrait(
                report_id=report.id,  # 关联的测评报告ID
                code=code,
                dimension_scores=dim_scores,
                unique_advantage=ua,
            )
            # 推荐结果可直接使用测评时生成的推荐
            recs = payload.get("recommendations") or []
            score_map = {}
            if getattr(report, "career_recommendations", None):
                for item in report.career_recommendations:
                    score_map[item.career_id] = int(item.score)
            for item in recs:
                # item: { profession_id, name, description }
                career_id = item.get("profession_id")
                name = item.get("name")
                ms = score_map.get(career_id, 0) if isinstance(career_id, int) else 0
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
        # 成就：探索进度更新后触发
        await AchievementService(self.session).evaluate_and_award(user.id, events=["exploration"])

    async def list_explorations(self, user: User, *, limit: int = 4) -> ExplorationListResponse:
        """列出探索进度，并填充不足 limit 的其余推荐位为“未开始”。

        逻辑：
        1. 查询用户已存在的探索记录并构造进度。
        2. 若记录数 < limit，则从职业表中补充尚未探索的职业，直到达到 limit 或无更多可补。
        3. 未开始的条目 explored_blocks=0, progress_percent=0, updated_at=None。
        """
        limit = max(1, min(20, limit))  # 安全上限，避免一次性返回过大
        rows = await self.repo.list_explorations(user.id)
        records: list[ExplorationRecord] = []
        explored_ids: set[int] = set()
        for progress, career in rows:
            explored = max(0, min(4, progress.explored_blocks))
            percent = int(explored / 4 * 100) if explored else 0
            explored_ids.add(progress.career_id)
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

        # 若不足 limit，补全未探索职业
        if len(records) < limit:
            # 直接拉取部分职业表（按 ID 升序）补位
            from sqlalchemy import select

            from app.models.career import Career

            need = limit - len(records)
            stmt = (
                select(Career)
                .where(~Career.id.in_(explored_ids) if explored_ids else True)
                .order_by(Career.id.asc())
                .limit(need)
            )
            res = await self.session.execute(stmt)
            for c in res.scalars().all():
                records.append(
                    ExplorationRecord(
                        career_id=c.id,
                        career_name=c.name,
                        explored_blocks=0,
                        total_blocks=4,
                        progress_percent=0,
                        updated_at=None,
                    )
                )

        # 截断到 limit（如果用户已有记录超过 limit）
        return ExplorationListResponse(items=records[:limit])

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

    # ---- Wrongbook ----
    async def list_wrongbook(self, user: User) -> WrongbookListResponse:
        rows = await self.repo.list_wrongbook(user.id)
        items: list[WrongbookItem] = []
        for r in rows:
            items.append(
                WrongbookItem(
                    script_title=r.script_title,
                    scene_title=r.scene_title,
                    selected_option_text=r.selected_option_text or "",
                    correct_option_text=r.correct_option_text,
                    analysis=r.analysis or "",
                    occurred_at=r.created_at,
                )
            )
        return WrongbookListResponse(items=items)
