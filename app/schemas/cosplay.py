from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class CosplayAbilityDescriptor(BaseModel):
    code: str = Field(..., description="能力维度编码，例如 T/S/P/Q")
    name: str = Field(..., description="能力维度名称")
    description: Optional[str] = Field(None, description="能力维度说明")


class CosplayOptionDefinition(BaseModel):
    id: str = Field(..., description="选项ID")
    text: str = Field(..., description="选项展示文本")
    description: Optional[str] = Field(None, description="补充说明，前端可用于悬浮提示")
    effects: dict[str, int] = Field(..., description="能力维度的加减分(以单位步长计)")
    feedback: str = Field(..., description="选择该选项后的即时反馈")


class CosplaySceneDefinition(BaseModel):
    id: str = Field(..., description="场景ID")
    title: str = Field(..., description="场景标题")
    narrative: str = Field(..., description="场景叙事文本")
    options: list[CosplayOptionDefinition] = Field(..., description="可选项列表")


class CosplayEvaluationRule(BaseModel):
    key: str = Field(..., description="维度组合标识，如 T+Q 或 balanced")
    route: str = Field(..., description="职业发展路线名称")
    summary: str = Field(..., description="总体评价摘要")
    advice: str = Field(..., description="发展建议")


class CosplayScriptContent(BaseModel):
    summary: str = Field(..., description="剧本简介或导语")
    setting: Optional[str] = Field(None, description="核心设定或背景")
    base_score: int = Field(50, description="能力维度初始分值")
    point_step: int = Field(10, description="每个单位调整对应的分值")
    abilities: list[CosplayAbilityDescriptor] = Field(..., description="能力维度定义列表")
    scenes: list[CosplaySceneDefinition] = Field(..., description="剧本场景顺序")
    evaluation_rules: list[CosplayEvaluationRule] = Field(..., description="结算评价规则集合")


class CosplayOptionView(BaseModel):
    id: str = Field(..., description="选项ID")
    text: str = Field(..., description="选项展示文案")
    description: Optional[str] = Field(None, description="可选的补充说明")


class CosplaySceneView(BaseModel):
    id: str = Field(..., description="场景ID")
    title: str = Field(..., description="场景标题")
    narrative: str = Field(..., description="场景描述文本")
    options: list[CosplayOptionView] = Field(..., description="可供选择的选项列表")


class CosplayHistoryRecord(BaseModel):
    scene_id: str = Field(..., description="所属场景ID")
    scene_title: str = Field(..., description="所属场景标题")
    option_id: str = Field(..., description="选择的选项ID")
    option_text: str = Field(..., description="选择的选项文案")
    feedback: str = Field(..., description="即时反馈文案")
    delta: dict[str, int] = Field(..., description="各能力维度的分值变化")
    scores_after: dict[str, int] = Field(..., description="选择后各维度分数")
    occurred_at: datetime = Field(..., description="选择发生时间(UTC)")


class CosplayReportPayload(BaseModel):
    scores: dict[str, int] = Field(..., description="会话结束时的能力维度得分")
    highlight_dimensions: list[str] = Field(..., description="表现突出的维度编码")
    ranked_dimensions: list[str] = Field(..., description="按得分排序的维度编码")
    route_key: str = Field(..., description="命中的评价规则标识")
    route_name: str = Field(..., description="对应的职业发展路线名称")
    summary: str = Field(..., description="最终评价摘要")
    advice: str = Field(..., description="发展建议文案")
    ability_labels: dict[str, str] = Field(..., description="能力编码到展示名称的映射")
    ability_descriptions: dict[str, str] = Field(..., description="能力编码到说明的映射")
    history: list[CosplayHistoryRecord] = Field(..., description="完整的选择历史记录")


class CosplaySessionState(BaseModel):
    session_id: int = Field(..., description="会话ID")
    script_id: int = Field(..., description="剧本ID")
    script_title: str = Field(..., description="剧本标题")
    setting: Optional[str] = Field(None, description="剧本背景设定")
    progress: int = Field(..., ge=0, le=100, description="当前完成进度(百分比)")
    completed: bool = Field(..., description="会话是否已完成")
    current_scene_index: int = Field(..., description="下一待完成场景的索引位置")
    total_scenes: int = Field(..., description="剧本总场景数")
    scores: dict[str, int] = Field(..., description="当前能力维度得分")
    abilities: list[CosplayAbilityDescriptor] = Field(..., description="剧本包含的能力维度配置")
    current_scene: Optional[CosplaySceneView] = Field(None, description="当前待选择的场景信息")
    history: list[CosplayHistoryRecord] = Field(..., description="已完成的场景历史记录")
    report: Optional[CosplayReportPayload] = Field(None, description="若已完成则包含的最终报告")


class CosplayScriptSummary(BaseModel):
    id: int = Field(..., description="剧本ID")
    title: str = Field(..., description="剧本名称")
    summary: str = Field(..., description="剧本简介")
    setting: Optional[str] = Field(None, description="剧本设定")
    total_scenes: int = Field(..., description="场景数量")
    updated_at: datetime = Field(..., description="最近更新时间")


class CosplayScriptDetail(BaseModel):
    id: int = Field(..., description="剧本ID")
    title: str = Field(..., description="剧本名称")
    summary: str = Field(..., description="剧本简介")
    setting: Optional[str] = Field(None, description="剧本设定")
    abilities: list[CosplayAbilityDescriptor] = Field(..., description="能力维度配置")
    total_scenes: int = Field(..., description="场景数量")
    updated_at: datetime = Field(..., description="最近更新时间")


class CosplayChoiceRequest(BaseModel):
    option_id: str = Field(..., description="用户在当前场景中选择的选项ID")


class CosplaySessionResumeRequest(BaseModel):
    resume: bool = Field(False, description="是否复用已有未完成会话")


class CosplaySessionListResponse(BaseModel):
    scripts: list[CosplayScriptSummary] = Field(..., description="可用剧本列表")


class CosplaySessionStateResponse(BaseModel):
    state: CosplaySessionState = Field(..., description="当前会话状态数据")


class CosplayScriptDetailResponse(BaseModel):
    script: CosplayScriptDetail = Field(..., description="剧本详情数据")
