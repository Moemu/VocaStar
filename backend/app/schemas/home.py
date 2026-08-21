from typing import List, Optional

from pydantic import BaseModel, Field


class PlanetProgress(BaseModel):
    """职业星球探索进度。"""

    unlocked: int = Field(..., description="已解锁的职业星球数量")
    total: int = Field(..., description="职业星球总数")


class AbilityScore(BaseModel):
    """用户能力维度得分。"""

    code: str = Field(..., description="能力编码，例如 R/I/A/S/E/C")
    name: str = Field(..., description="能力名称")
    score: float = Field(..., description="能力得分")


class PointEntry(BaseModel):
    """积分任务完成情况。"""

    task: str = Field(..., description="积分任务名称")
    status: str = Field(..., description="积分任务的完成状态，例如 已完成/未完成")


class TodayPointsSummary(BaseModel):
    """当天积分汇总。"""

    total: int = Field(..., description="今天累计获得的积分")
    entries: List[PointEntry] = Field(default_factory=list, description="积分任务完成情况列表")


class PersonalOverview(BaseModel):
    """个人信息概览。"""

    planet_progress: PlanetProgress = Field(..., description="职业星球探索进度")
    ability_scores: List[AbilityScore] = Field(default_factory=list, description="用户能力得分")
    today_points: TodayPointsSummary = Field(..., description="今天的积分情况")


class CareerRecommendationItem(BaseModel):
    """首页职业推荐卡片信息。"""

    career_id: int = Field(..., description="职业 ID")
    name: str = Field(..., description="职业名称")
    galaxy_name: Optional[str] = Field(None, description="所属职业星系名称")
    image_url: Optional[str] = Field(None, description="职业描述图 URL")
    description: Optional[str] = Field(None, description="职业简介")
    reason: str = Field(..., description="推荐理由")
    explorer_count: int = Field(..., description="探索该职业的人数")


class HomeSummaryResponse(BaseModel):
    """首页聚合接口响应体。"""

    personal: PersonalOverview = Field(..., description="个人信息概览")
    recommendations: List[CareerRecommendationItem] = Field(default_factory=list, description="首页职业推荐列表")
