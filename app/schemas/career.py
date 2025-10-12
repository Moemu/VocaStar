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
    galaxy_id: Optional[int] = Field(None, description="所属星系编码")
    galaxy_name: Optional[str] = Field(None, description="所属星系名称")
    category: Optional[str] = Field(None, description="职业分类显示名称")
    salary_min: Optional[int] = Field(None, description="薪资范围下限")
    salary_max: Optional[int] = Field(None, description="薪资范围上限")
    skills_snapshot: Optional[list[str]] = Field(None, description="简短的技能要求列表")


class CareerDetail(CareerSummary):
    work_contents: Optional[list[str]] = Field(None, description="主要工作内容描述列表")
    career_outlook: Optional[str] = Field(None, description="职业发展前景说明")
    development_path: Optional[list[str]] = Field(None, description="职业发展路径阶段列表")
    required_skills: Optional[list[str]] = Field(None, description="岗位要求技能列表")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="最近更新时间")
    galaxy_description: Optional[str] = Field(None, description="所属星系简介")
    galaxy_cover_image_url: Optional[str] = Field(None, description="所属星系封面图")


class CareerListResponse(BaseModel):
    total: int = Field(..., description="符合条件的职业总数")
    items: list[CareerSummary] = Field(..., description="当前页职业列表")


class CareerFeaturedResponse(BaseModel):
    items: list[CareerSummary] = Field(..., description="推荐职业列表")


class CareerExplorePlanet(BaseModel):
    id: int = Field(..., description="职业主键ID")
    name: str = Field(..., description="职业名称")
    description: Optional[str] = Field(None, description="职业简介")
    planet_image_url: Optional[str] = Field(None, description="职业星球展示图地址")
    holland_dimensions: Optional[list[str]] = Field(None, description="关联的霍兰德维度")
    salary_min: Optional[int] = Field(None, description="薪资范围下限")
    salary_max: Optional[int] = Field(None, description="薪资范围上限")
    skills_snapshot: Optional[list[str]] = Field(None, description="技能亮点列表")


class CareerExploreGalaxy(BaseModel):
    id: int = Field(..., description="星系ID")
    name: str = Field(..., description="星系名称")
    category: str = Field(..., description="职业分类编码")
    description: Optional[str] = Field(None, description="星系简介")
    cover_image_url: Optional[str] = Field(None, description="星系封面图")
    planets: list[CareerExplorePlanet] = Field(..., description="星系下的职业星球列表")


class CareerExploreSalaryRange(BaseModel):
    min: Optional[int] = Field(None, description="全局薪资下限")
    max: Optional[int] = Field(None, description="全局薪资上限")


class CareerExploreFilters(BaseModel):
    categories: list[str] = Field(default_factory=list, description="可选职业分类列表")
    salary: Optional[CareerExploreSalaryRange] = Field(None, description="薪资筛选范围")


class CareerExploreResponse(BaseModel):
    galaxies: list[CareerExploreGalaxy] = Field(default_factory=list, description="探索星系及其职业星球列表")
    filters: CareerExploreFilters = Field(
        default_factory=lambda: CareerExploreFilters(categories=[], salary=None),
        description="用于前端展示的筛选信息",
    )
