from __future__ import annotations

from datetime import datetime
from typing import Literal, Optional

from pydantic import BaseModel, Field

# -------- 数据看板 --------


class HollandPortrait(BaseModel):
    code: str = Field(..., description="霍兰德三字母代码，如 ASE")
    dimension_scores: dict[str, int] = Field(..., description="各维度分数 R/I/A/S/E/C")
    analysis: str = Field(..., description="个性化分析文案")


class DashboardRecommendation(BaseModel):
    career_id: int = Field(..., description="推荐职业ID")
    name: str = Field(..., description="职业名称")
    match_score: int = Field(..., description="匹配度 0-100")


class DashboardResponse(BaseModel):
    holland: Optional[HollandPortrait] = Field(None, description="职业兴趣画像，可能为空(未测评)")
    recommendations: list[DashboardRecommendation] = Field(default_factory=list, description="推荐职业")


# -------- 探索足迹 --------


class ExplorationItem(BaseModel):
    career_id: int = Field(..., description="职业ID")
    explored_blocks: int = Field(..., ge=0, le=4, description="已探索区块数(0-4)")


class ExplorationUpsertRequest(BaseModel):
    items: list[ExplorationItem] = Field(..., description="探索进度上报列表")


class ExplorationRecord(BaseModel):
    career_id: int = Field(..., description="职业ID")
    career_name: str | None = Field(None, description="职业名称")
    explored_blocks: int = Field(..., description="已探索区块数")
    total_blocks: int = Field(4, description="区块总数(固定为4)")
    progress_percent: int = Field(..., description="进度百分比(0-100)")
    updated_at: datetime = Field(..., description="最近更新时间")


class ExplorationListResponse(BaseModel):
    items: list[ExplorationRecord] = Field(..., description="探索进度记录列表")


# -------- 错题本占位 --------


class WrongbookItem(BaseModel):
    script_title: str = Field(..., description="剧本标题")
    scene_title: str = Field(..., description="场景标题")
    correct_option_text: str = Field(..., description="正确选项文本")
    analysis: str = Field(..., description="解析说明")
    occurred_at: datetime = Field(..., description="发生时间")


class WrongbookListResponse(BaseModel):
    items: list[WrongbookItem] = Field(..., description="错题记录列表")


# -------- 收藏夹 --------

FavoriteType = Literal["career"]


class AddFavoriteRequest(BaseModel):
    item_type: FavoriteType = Field(..., description="收藏对象类型，目前仅支持 career")
    item_id: int = Field(..., description="收藏对象ID，例如职业ID")


class FavoriteRecord(BaseModel):
    item_type: FavoriteType = Field(..., description="收藏对象类型")
    item_id: int = Field(..., description="收藏对象ID")
    name: str | None = Field(None, description="对象名称")
    favorited_at: datetime = Field(..., description="收藏时间")


class FavoriteListResponse(BaseModel):
    items: list[FavoriteRecord] = Field(..., description="收藏记录列表")
