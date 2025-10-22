from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class CosplayAbilityDescriptor(BaseModel):
    code: str = Field(..., description="能力维度编码，例如 T/S/P/Q")
    name: str = Field(..., description="能力维度名称")
    description: Optional[str] = Field(None, description="能力维度说明")


class CosplayOptionDefinition(BaseModel):
    """Cosplay 剧本中单个选项的定义"""

    id: str = Field(..., description="选项的唯一标识符")
    text: str = Field(..., description="向用户展示的选项文本")
    outcome: str = Field(..., description="选择该选项后触发的剧情结果文本")
    effects: dict[str, int] = Field(
        default_factory=dict, description="对各项能力分值的影响, key为能力编码, value为影响点数"
    )


class CosplayOptionView(BaseModel):
    """向用户呈现的选项视图，不包含选择结果"""

    id: str = Field(..., description="选项的唯一标识符")
    text: str = Field(..., description="向用户展示的选项文本")


class CosplaySceneDefinition(BaseModel):
    """Cosplay 剧本中单个场景的定义"""

    id: str = Field(..., description="场景的唯一标识符")
    title: str = Field(..., description="场景标题")
    text: str = Field(..., description="场景的描述性文本")
    options: list[CosplayOptionDefinition] = Field(..., description="该场景的所有可选选项定义")
    is_end: bool = Field(False, description="是否为结束场景")


class CosplaySceneView(BaseModel):
    """向用户呈现的场景视图"""

    id: str = Field(..., description="场景的唯一标识符")
    title: str = Field(..., description="场景标题")
    text: str = Field(..., description="场景的描述性文本")
    options: list[CosplayOptionView] = Field(..., description="提供给用户的选项")
    is_end: bool = Field(False, description="是否为结束场景")


class CosplayEvaluationRule(BaseModel):
    """Cosplay 报告的最终评价规则"""

    summary: str = Field(..., description="根据最终得分给出的总结性评价")
    advice: str = Field(..., description="根据最终得分给出的发展建议")
    thresholds: dict[str, int] = Field(..., description="触发此评价所需的各项能力最低分值")


class CosplayScriptContent(BaseModel):
    """Cosplay 剧本的完整内容定义"""

    initial_scores: dict[str, int] = Field(..., description="各项能力的初始分值")
    scenes: dict[str, CosplaySceneDefinition] = Field(..., description="剧本的所有场景定义, key为场景ID")
    evaluations: list[CosplayEvaluationRule] = Field(..., description="最终报告的评价规则列表")
    abilities: list[CosplayAbilityDescriptor] = Field(..., description="剧本涉及的能力维度定义")
    summary: str = Field(..., description="剧本的整体摘要")
    setting: str | None = Field(None, description="剧本的背景设定")
    base_score: int | None = Field(None, description="计算分数变化时的基础分, 默认为50")
    point_step: int | None = Field(None, description="每个效果点数对应的实际分数变化, 默认为10")


class CosplayChoiceResponse(BaseModel):
    """用户做出选择后的响应体"""

    outcome: str = Field(..., description="选择该选项后触发的剧情结果文本")
    score_changes: dict[str, int] = Field(..., description="本次选择带来的分数变化")
    current_scores: dict[str, int] = Field(..., description="更新后的总分")
    next_scene: "CosplaySessionState" = Field(..., description="包含下一个场景信息的会话状态")


class CosplayHistoryRecord(BaseModel):
    """Cosplay 会话中的单次选择历史记录"""

    scene_id: str = Field(..., description="所选场景的ID")
    choice_id: str = Field(..., description="所做选择的ID")


class CosplayReportPayload(BaseModel):
    """Cosplay 报告的详细内容"""

    final_scores: dict[str, int] = Field(..., description="最终的各项能力得分")
    summary: str = Field(..., description="最终评价摘要")
    advice: str = Field(..., description="发展建议文案")
    ability_labels: dict[str, str] = Field(..., description="能力编码到展示名称的映射")
    ability_descriptions: dict[str, str] = Field(..., description="能力编码到说明的映射")
    history: list[CosplayHistoryRecord] = Field(..., description="完整的选择历史记录")


class CosplaySessionState(BaseModel):
    """Cosplay 会话的完整状态"""

    session_id: int = Field(..., description="会话ID")
    script_id: int = Field(..., description="剧本ID")
    script_title: str = Field(..., description="剧本标题")
    setting: str | None = Field(None, description="剧本背景设定")
    progress: int = Field(..., ge=0, le=100, description="当前完成进度(百分比)")
    completed: bool = Field(..., description="会话是否已完成")
    current_scene_index: int = Field(..., description="下一待完成场景的索引位置")
    total_scenes: int = Field(..., description="剧本总场景数")
    scores: dict[str, int] = Field(..., description="当前能力维度得分")
    abilities: list[CosplayAbilityDescriptor] = Field(..., description="剧本包含的能力维度配置")
    current_scene: CosplaySceneView | None = Field(None, description="当前待选择的场景信息")
    history: list[CosplayHistoryRecord] = Field(..., description="已完成的场景历史记录")
    report: CosplayReportPayload | None = Field(None, description="若已完成则包含的最终报告")


class CosplayScriptSummary(BaseModel):
    """Cosplay 剧本的摘要信息"""

    id: int = Field(..., description="剧本ID")
    title: str = Field(..., description="剧本名称")
    summary: str = Field(..., description="剧本摘要")
    setting: str | None = Field(None, description="剧本背景设定")
    total_scenes: int = Field(..., description="总场景数")
    updated_at: datetime = Field(..., description="最后更新时间")


class CosplayScriptDetail(CosplayScriptSummary):
    """Cosplay 剧本的详细信息"""

    abilities: list[CosplayAbilityDescriptor] = Field(..., description="剧本包含的能力维度定义")


class CosplaySessionListResponse(BaseModel):
    """可用 Cosplay 剧本列表的响应体"""

    scripts: list[CosplayScriptSummary]


class CosplayScriptDetailResponse(BaseModel):
    """单个 Cosplay 剧本详情的响应体"""

    script: CosplayScriptDetail


class CosplaySessionStateResponse(BaseModel):
    """Cosplay 会话状态的响应体"""

    state: CosplaySessionState


class CosplaySessionResumeRequest(BaseModel):
    """开始或恢复 Cosplay 会话的请求体"""

    resume: bool = Field(True, description="是否尝试恢复上一次未完成的会话")


class CosplayChoiceRequest(BaseModel):
    """用户在场景中做出选择的请求体"""

    option_id: str = Field(..., description="用户选择的选项ID")
