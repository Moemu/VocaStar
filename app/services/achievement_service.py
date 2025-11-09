from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Iterable

from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.cosplay import CosplaySession, SessionState
from app.models.extensions import (
    Achievement,
    ExplorationProgress,
    PointTransaction,
    UserAchievement,
)
from app.models.partners import UserPartnerBinding

# 与首页签到逻辑保持一致的 reason 常量（保持硬编码以避免循环导入）
_SIGN_IN_REASON = "每日签到"


class AchievementCodes:
    """成就代码常量集合。

    说明：采用大写+下划线的稳定常量，便于前端做图标/文案映射。
    """

    FIRST_EXPLORATION = "FIRST_EXPLORATION"  # 第一次完成 1 个职业星球（满探索）
    COSPLAY_3_COMPLETED = "COSPLAY_3_COMPLETED"  # 完成 3 次职业体验
    SIGNIN_7_STREAK = "SIGNIN_7_STREAK"  # 连续签到 7 天
    PARTNER_3_BOUND = "PARTNER_3_BOUND"  # 绑定 3 个职业伙伴


@dataclass
class RuleDef:
    """成就规则定义。

    Attributes:
        code: 成就代码，对应 Achievement.code。
        condition_type: 条件类型，用于 _current_progress 选择计算策略。
        threshold: 触发阈值，到达即授予；<=0 表示不授予（保护）。
    """

    code: str
    condition_type: str
    threshold: int


RULES: list[RuleDef] = [
    # 满探索 1 个职业（explored_blocks >= 4 的职业数量 >= 1）
    RuleDef(AchievementCodes.FIRST_EXPLORATION, "first_full_exploration", 1),
    # 完成 3 次 Cosplay 体验（CosplaySession.state == completed 的数量）
    RuleDef(AchievementCodes.COSPLAY_3_COMPLETED, "cosplay_completed_count", 3),
    # 连续签到 7 天（从今日起按天回溯计算连续天数）
    RuleDef(AchievementCodes.SIGNIN_7_STREAK, "consecutive_sign_in_days", 7),
    # 绑定 3 个职业伙伴（UserPartnerBinding 计数）
    RuleDef(AchievementCodes.PARTNER_3_BOUND, "partner_bindings_count", 3),
]


class AchievementService:
    """成就评估与授予服务。

    目标：
    - 幂等种子：首次访问自动补齐基础成就（seed_minimal）。
    - 事件驱动评估：evaluate_and_award 只评估与事件相关的规则，减少无关查询。
    - 统一进度口：_current_progress 集中处理各类 condition_type 的进度计算。
    - 前端友好：list_with_progress 返回进度、百分比、达成标记与时间。
    """

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def seed_minimal(self) -> None:
        """插入四个基础成就（幂等）。

        若表中已存在相同 code 的记录，将跳过插入。用于测试初始化与首次运行自动补全。
        """
        existing_stmt = select(Achievement.code)
        existing_codes = {c for c, in (await self.session.execute(existing_stmt)).all()}
        for r in RULES:
            if r.code in existing_codes:
                continue
            ach = Achievement(
                code=r.code,
                name=self._default_name(r.code),
                description=self._default_desc(r.code),
                points=self._default_points(r.code),
                condition_type=r.condition_type,
                threshold=r.threshold,
            )
            self.session.add(ach)
        await self.session.commit()

    def _default_name(self, code: str) -> str:
        return {
            AchievementCodes.FIRST_EXPLORATION: "初次探索",
            AchievementCodes.COSPLAY_3_COMPLETED: "职业新秀",
            AchievementCodes.SIGNIN_7_STREAK: "学习达人",
            AchievementCodes.PARTNER_3_BOUND: "社交之星",
        }.get(code, code)

    def _default_desc(self, code: str) -> str:
        return {
            AchievementCodes.FIRST_EXPLORATION: "完成第一个职业星球的探索",
            AchievementCodes.COSPLAY_3_COMPLETED: "完成3次职业体验",
            AchievementCodes.SIGNIN_7_STREAK: "连续打卡7天",
            AchievementCodes.PARTNER_3_BOUND: "绑定3个职业伙伴",
        }.get(code, code)

    def _default_points(self, code: str) -> int:
        return {
            AchievementCodes.FIRST_EXPLORATION: 50,
            AchievementCodes.COSPLAY_3_COMPLETED: 80,
            AchievementCodes.SIGNIN_7_STREAK: 100,
            AchievementCodes.PARTNER_3_BOUND: 60,
        }.get(code, 0)

    async def evaluate_and_award(self, user_id: int, *, events: Iterable[str]) -> list[str]:
        """根据事件集合评估相关成就并授予，返回新授予的成就代码列表。

        参数:
            user_id: 目标用户ID。
            events: 本次触发的事件集合，用于筛选需要评估的 condition_type。
                    可选值：exploration | cosplay_completed | sign_in | partner_bind。

        返回:
            list[str]: 新授予的成就代码列表；若无授予或无匹配事件则为空。
        """
        event_set = set(events)
        stmt = select(Achievement)
        achievements = (await self.session.execute(stmt)).scalars().all()
        # 若不存在任何成就定义，自动种子（测试/首次运行友好）
        if not achievements:
            await self.seed_minimal()
            achievements = (await self.session.execute(stmt)).scalars().all()
        if not achievements:
            return []
        owned_stmt = select(UserAchievement.achievement_id).where(UserAchievement.user_id == user_id)
        owned_ids = {aid for aid, in (await self.session.execute(owned_stmt)).all()}

        # 将高层事件映射为具体 condition_type 集合，便于最小化进度计算范围
        event_map = {
            "exploration": {"first_full_exploration"},
            "cosplay_completed": {"cosplay_completed_count"},
            "sign_in": {"consecutive_sign_in_days"},
            "partner_bind": {"partner_bindings_count"},
        }
        active_condition_types = set()
        for e in event_set:
            active_condition_types.update(event_map.get(e, set()))
        if not active_condition_types:
            return []

        newly_awarded: list[str] = []
        for ach in achievements:
            if ach.id in owned_ids:
                continue
            if ach.condition_type not in active_condition_types:
                continue
            progress = await self._current_progress(user_id, ach.condition_type)
            threshold = ach.threshold or 0
            if progress >= threshold and threshold > 0:
                ua = UserAchievement(user_id=user_id, achievement_id=ach.id)
                self.session.add(ua)
                newly_awarded.append(ach.code)
        if newly_awarded:
            await self.session.commit()
        return newly_awarded

    async def _current_progress(self, user_id: int, condition_type: str) -> int:
        """根据 condition_type 计算用户当前的进度值。

        支持的 condition_type：
            - first_full_exploration: 满探索职业数量（explored_blocks >= 4）
            - cosplay_completed_count: 已完成 Cosplay 会话数量
            - consecutive_sign_in_days: 截止今天的连续签到天数（回溯统计）
            - partner_bindings_count: 绑定的伙伴数量

        未识别的类型返回 0。
        """
        if condition_type == "first_full_exploration":
            stmt = (
                select(func.count())
                .select_from(ExplorationProgress)
                .where(and_(ExplorationProgress.user_id == user_id, ExplorationProgress.explored_blocks >= 4))
            )
            return int((await self.session.execute(stmt)).scalar() or 0)
        if condition_type == "cosplay_completed_count":
            stmt = (
                select(func.count())
                .select_from(CosplaySession)
                .where(and_(CosplaySession.user_id == user_id, CosplaySession.state == SessionState.completed))
            )
            return int((await self.session.execute(stmt)).scalar() or 0)
        if condition_type == "consecutive_sign_in_days":
            # 简化查询：直接按 user_points -> user_id 过滤
            from app.models.extensions import UserPoints

            now = datetime.utcnow().date()
            start_date = now - timedelta(days=14)
            stmt = (
                select(PointTransaction.created_at)
                .join(UserPoints, PointTransaction.user_points_id == UserPoints.id)
                .where(UserPoints.user_id == user_id)
                .where(PointTransaction.reason == _SIGN_IN_REASON)
                .where(PointTransaction.created_at >= datetime.combine(start_date, datetime.min.time()))
                .where(PointTransaction.created_at <= datetime.combine(now, datetime.max.time()))
            )
            rows = [dt for dt, in (await self.session.execute(stmt)).all()]
            day_set = {dt.date() for dt in rows}
            streak = 0
            cur = now
            while cur in day_set:
                streak += 1
                cur = cur - timedelta(days=1)
            return streak
        if condition_type == "partner_bindings_count":
            stmt = select(func.count()).select_from(UserPartnerBinding).where(UserPartnerBinding.user_id == user_id)
            return int((await self.session.execute(stmt)).scalar() or 0)
        return 0

    async def list_with_progress(self, user_id: int) -> list[dict]:
        """列出所有成就及该用户的达成进度。

        返回的每个元素字段：code, name, description, points, progress, threshold,
        progress_percent(0-100), achieved(bool), achieved_at(datetime|None)。
        当无成就定义时会自动触发 seed_minimal。
        """
        stmt = select(Achievement)
        achievements = (await self.session.execute(stmt)).scalars().all()
        if not achievements:
            await self.seed_minimal()
            achievements = (await self.session.execute(stmt)).scalars().all()
        owned_stmt = select(UserAchievement).where(UserAchievement.user_id == user_id)
        owned = {ua.achievement_id: ua for ua in (await self.session.execute(owned_stmt)).scalars().all()}
        result: list[dict] = []
        for ach in achievements:
            progress = await self._current_progress(user_id, ach.condition_type or "")
            threshold = ach.threshold or 0
            # 进度百分比按 0-100 钳制，避免大于100时触发响应模型校验错误
            if threshold > 0:
                percent = int(progress / threshold * 100)
                if percent > 100:
                    percent = 100
                if percent < 0:
                    percent = 0
            else:
                percent = 0
            ua = owned.get(ach.id)
            result.append(
                {
                    "code": ach.code,
                    "name": ach.name,
                    "description": ach.description,
                    "points": ach.points,
                    "progress": progress,
                    "threshold": threshold,
                    "progress_percent": percent,
                    "achieved": ua is not None,
                    "achieved_at": ua.achieved_at if ua else None,
                }
            )
        return result
