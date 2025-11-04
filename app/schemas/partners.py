from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.community import Pagination


class SkillStat(BaseModel):
    """热门技能标签统计。"""

    skill: str = Field(..., description="技能标签（小写规范化，如 react、sql）")
    count: int = Field(..., ge=0, description="拥有该技能的伙伴数量")


class PartnerItem(BaseModel):
    """伙伴列表项（完整信息）。

    场景：通用搜索/列表页使用。包含学习进度与技术栈。
    """

    id: int = Field(..., description="伙伴 ID")
    name: str = Field(..., description="伙伴姓名/展示名")
    avatar_url: str | None = Field(None, description="头像 URL，可为空")
    profession: str = Field(..., description="职业/岗位，如 前端开发、数据分析师")
    learning_progress: int = Field(0, ge=0, le=100, description="学习进度百分比（0-100）")
    tech_stack: list[str] = Field(default_factory=list, description="技能标签列表（去重、小写）")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "id": 101,
                "name": "小明",
                "avatar_url": "/static/avatars/u101.png",
                "profession": "后端开发",
                "learning_progress": 75,
                "tech_stack": ["python", "fastapi", "postgresql"],
            }
        }
    )


class PartnerRecommendItem(BaseModel):
    """推荐伙伴项（隐藏学习进度）。

    场景：推荐列表中展示。包含技术栈但不包含学习进度。
    """

    id: int = Field(..., description="伙伴 ID")
    name: str = Field(..., description="伙伴姓名/展示名")
    avatar_url: str | None = Field(None, description="头像 URL，可为空")
    profession: str = Field(..., description="职业/岗位")
    tech_stack: list[str] = Field(default_factory=list, description="技能标签列表")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "id": 102,
                "name": "Ada",
                "avatar_url": "/static/avatars/u102.png",
                "profession": "数据分析师",
                "tech_stack": ["sql", "pandas", "tableau"],
            }
        }
    )


class PartnerMyItem(BaseModel):
    """我的伙伴项（隐藏技术栈）。

    场景：我的伙伴列表。包含学习进度，但不返回技术栈。
    """

    id: int = Field(..., description="伙伴 ID")
    name: str = Field(..., description="伙伴姓名/展示名")
    avatar_url: str | None = Field(None, description="头像 URL，可为空")
    profession: str = Field(..., description="职业/岗位")
    learning_progress: int = Field(0, ge=0, le=100, description="学习进度百分比（0-100）")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "id": 103,
                "name": "橘子老师",
                "avatar_url": "/static/avatars/u103.png",
                "profession": "产品经理",
                "learning_progress": 40,
            }
        }
    )


class PartnerListResponse(BaseModel):
    """伙伴搜索/列表响应。"""

    items: list[PartnerItem] = Field(..., description="伙伴列表（完整信息）")
    pagination: Pagination = Field(..., description="分页信息")


class PartnerRecommendListResponse(BaseModel):
    """推荐伙伴响应。"""

    items: list[PartnerRecommendItem] = Field(..., description="推荐伙伴列表（隐藏学习进度）")


class PartnerMyListResponse(BaseModel):
    """我的伙伴响应（隐藏技术栈）。"""

    items: list[PartnerMyItem] = Field(..., description="我的伙伴列表（隐藏技术栈）")
    pagination: Pagination = Field(..., description="分页信息")


class BindState(BaseModel):
    """绑定状态返回。"""

    bound: bool = Field(..., description="绑定后 true，解绑后 false（幂等）")
