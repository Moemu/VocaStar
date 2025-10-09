from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class CareerSummary(BaseModel):
    id: int = Field(..., description="职业主键ID")
    name: str = Field(..., description="职业名称")
    description: Optional[str] = Field(None, description="职业简介")
    holland_dimensions: Optional[list[str]] = Field(
        None,
        description="匹配的霍兰德维度列表，例如 ['R','I','A']",
    )
    planet_image_url: Optional[str] = Field(None, description="职业星球展示图地址")
    related_courses: Optional[list[str]] = Field(None, description="推荐学习的课程列表")
    core_competency_model: Optional[dict[str, float]] = Field(
        None,
        description="核心胜任力模型分布，键为能力项，值为评分",
    )
    knowledge_background: Optional[dict[str, str]] = Field(
        None,
        description="知识背景补充说明，例如行业及专业知识要求",
    )


class CareerDetail(CareerSummary):
    work_contents: Optional[list[str]] = Field(None, description="主要工作内容描述列表")
    career_outlook: Optional[str] = Field(None, description="职业发展前景说明")
    development_path: Optional[list[str]] = Field(None, description="职业发展路径阶段列表")
    required_skills: Optional[list[str]] = Field(None, description="岗位要求技能列表")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="最近更新时间")


class CareerListResponse(BaseModel):
    total: int = Field(..., description="符合条件的职业总数")
    items: list[CareerSummary] = Field(..., description="当前页职业列表")


class CareerFeaturedResponse(BaseModel):
    items: list[CareerSummary] = Field(..., description="推荐职业列表")
