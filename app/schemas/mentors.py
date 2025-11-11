from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.community import Pagination


class DomainItem(BaseModel):
    slug: str = Field(..., description="领域标识，如 frontend/backend/data")
    name: str = Field(..., description="领域名称")
    count: int = Field(0, ge=0, description="该领域下导师数量")


class DomainListResponse(BaseModel):
    items: list[DomainItem] = Field(default_factory=list, description="导师领域列表")


class MentorItem(BaseModel):
    """导师卡片数据。"""

    id: int = Field(..., description="导师 ID")
    name: str = Field(..., description="导师姓名/展示名")
    avatar_url: str | None = Field(None, description="头像 URL")
    profession: str = Field(..., description="所属/擅长职业")
    company: str | None = Field(None, description="在职企业")
    fee_per_hour: int = Field(0, ge=0, description="咨询费用（每小时）")
    rating: float = Field(0, ge=0, le=5, description="星级评分，满分 5 分")
    rating_count: int = Field(0, ge=0, description="评分数量")
    tech_stack: list[str] = Field(default_factory=list, description="技能标签列表")
    domains: list[str] = Field(default_factory=list, description="所属领域标识列表")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "id": 1,
                "name": "Alice",
                "avatar_url": "/static/avatars/alice.png",
                "profession": "前端开发",
                "company": "Awesome Inc.",
                "fee_per_hour": 299,
                "rating": 4.8,
                "rating_count": 152,
                "tech_stack": ["react", "typescript", "vite"],
                "domains": ["frontend", "devops"],
            }
        }
    )


class MentorListResponse(BaseModel):
    items: list[MentorItem]
    pagination: Pagination


class MentorRequestCreate(BaseModel):
    type: str = Field(..., pattern="^(question|consult)$", description="申请类型：question|consult")
    # message: str = Field(..., min_length=1, max_length=1000, description="问题/需求描述")
    # preferred_time: Optional[str] = Field(None, description="期望沟通时间（自由文本/ISO）")
    # duration_min: Optional[int] = Field(None, ge=15, le=180, description="咨询时长（分钟），仅 consult 可选")


class MentorRequestItem(BaseModel):
    id: int
    status: str = Field(..., description="pending/accepted/rejected/cancelled")


class MyMentorItem(BaseModel):
    """我的职业导师列表项：只展示基本公开信息。"""

    id: int = Field(..., description="导师ID")
    name: str = Field(..., description="导师姓名/展示名")
    avatar_url: str | None = Field(None, description="头像URL")
    profession: str = Field(..., description="导师职业/职能")
    company: str | None = Field(None, description="所在公司")
    rating: float = Field(0, ge=0, le=5, description="评分 0-5")


class MyMentorListResponse(BaseModel):
    items: list[MyMentorItem] = Field(default_factory=list, description="已申请（视为我的）导师列表")
