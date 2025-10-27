from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class _FlexibleModel(BaseModel):
    model_config = ConfigDict(extra="allow")


class CareerOverview(_FlexibleModel):
    description: Optional[str] = Field(None, description="职业简介文本")
    work_contents: list[str] = Field(default_factory=list, description="主要工作内容列表")
    career_outlook: Optional[str] = Field(None, description="职业发展前景")
    development_path: list[str] = Field(default_factory=list, description="职业发展/晋升路径阶段")


class KnowledgeBackground(_FlexibleModel):
    education_requirements: Optional[str] = Field(None, description="学历要求")
    industry_knowledge: Optional[str] = Field(None, description="行业知识背景")
    professional_knowledge: Optional[str] = Field(None, description="专业知识要求")
    professional_requirements: list[str] = Field(default_factory=list, description="相关专业/资格列表")


class CompetencyRequirements(_FlexibleModel):
    core_competency_model: Optional[dict[str, float]] = Field(None, description="核心胜任力模型分布")
    knowledge_background: Optional[KnowledgeBackground] = Field(None, description="知识背景要求")


class SalaryAndDistribution(_FlexibleModel):
    salary_level: dict[str, int] = Field(default_factory=dict, description="薪资等级映射")
    distribution_of_popular_cities: dict[str, int] = Field(default_factory=dict, description="热门城市分布")


class SkillEnhancementStage(_FlexibleModel):
    name: Optional[str] = Field(None, description="阶段名称")
    description: Optional[str] = Field(None, description="阶段描述")
    tags: list[str] = Field(default_factory=list, description="阶段涉及的知识点标签")


class SkillMap(_FlexibleModel):
    skills_snapshot: list[str] = Field(default_factory=list, description="技能摘要")
    related_courses: list[str] = Field(default_factory=list, description="推荐课程")
    important_but_not_offered_courses: list[str] = Field(default_factory=list, description="重要但未提供的课程")
    skill_enhancement_path: list[SkillEnhancementStage] = Field(default_factory=list, description="技能提升路径")


class CareerSummary(BaseModel):
    id: int = Field(..., description="职业主键ID")
    name: str = Field(..., description="职业名称")
    description: Optional[str] = Field(None, description="职业简介")
    holland_dimensions: Optional[list[str]] = Field(
        None,
        description="匹配的霍兰德维度列表，例如 ['R','I','A']",
    )
    planet_image_url: Optional[str] = Field(None, description="职业星球展示图地址")
    career_header_image: Optional[str] = Field(None, description="职业详情头图")
    overview: Optional[CareerOverview] = Field(None, description="职业总览信息")
    competency_requirements: Optional[CompetencyRequirements] = Field(None, description="胜任力与知识背景")
    salary_and_distribution: Optional[SalaryAndDistribution] = Field(None, description="薪资与地域分布")
    skill_map: Optional[SkillMap] = Field(None, description="技能图谱")
    skills_snapshot: Optional[list[str]] = Field(None, description="简短的技能要求列表")
    related_courses: Optional[list[str]] = Field(None, description="推荐学习的课程列表")
    galaxy_id: Optional[int] = Field(None, description="所属星系编码")
    galaxy_name: Optional[str] = Field(None, description="所属星系名称")
    category: Optional[str] = Field(None, description="职业分类显示名称")
    salary_min: Optional[int] = Field(None, description="薪资范围下限")
    salary_max: Optional[int] = Field(None, description="薪资范围上限")


class CareerDetail(CareerSummary):
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="最近更新时间")
    galaxy_description: Optional[str] = Field(None, description="所属星系简介")
    galaxy_cover_image_url: Optional[str] = Field(None, description="所属星系封面图")
    cosplay_script_id: Optional[int] = Field(None, description="关联的Cosplay剧本ID")


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
    career_header_image: Optional[str] = Field(None, description="职业详情头图")
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
