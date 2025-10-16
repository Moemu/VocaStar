from datetime import datetime
from typing import Annotated, Dict, List, Literal, NotRequired, Optional, Union

from pydantic import BaseModel, ConfigDict, Field
from typing_extensions import TypedDict


class QuizScoringFormulaConfigModel(BaseModel):
    """计分公式配置的验证模型"""

    max_occurrences: Optional[int] = Field(
        None,
        description="维度出现次数的上限，用于限定计数型题目的最大计分次数",
    )
    expression: Optional[str] = Field(
        None,
        description="自定义计分表达式（若启用），使用安全公式语法描述各维度的计算方式",
    )

    model_config = ConfigDict(extra="allow")


class QuizScoringConfigModel(BaseModel):
    """计分策略配置的验证模型"""

    strategy: Optional[str] = Field(
        None,
        description="计分策略标识，例如 count_based、weighted_components 等",
    )
    dimension_formulas: Optional[Dict[str, QuizScoringFormulaConfigModel]] = Field(
        None,
        description="按维度划分的公式配置，键为维度代码，值为对应的计分公式",
    )
    weights: Optional[Dict[str, float]] = Field(
        None,
        description="题型或组件的权重配置，取值范围通常在 0-1 之间",
    )
    notes: Optional[str] = Field(
        None,
        description="计分策略的补充说明，例如算法备注或业务提示",
    )

    model_config = ConfigDict(extra="allow")


class QuizConfigModel(BaseModel):
    """测评配置的验证模型"""

    slug: Optional[str] = Field(
        None,
        description="题库的唯一标识，便于前后端按别名检索测评",
    )
    scoring: Optional[QuizScoringConfigModel] = Field(
        None,
        description="测评整体的计分配置，包含策略、权重与公式说明",
    )

    model_config = ConfigDict(extra="allow")


class QuestionScaleConfigModel(BaseModel):
    """题目量表配置的验证模型"""

    min_value: float = Field(0.0, description="量表允许的最小取值，例如 0")
    max_value: float = Field(100.0, description="量表允许的最大取值，例如 100")
    step: float = Field(1.0, description="滑块或量表的步进值，用于控制精度")

    model_config = ConfigDict(extra="allow")


class QuestionDimensionEntryModel(BaseModel):
    """维度条目的验证模型"""

    label: str = Field(..., description="显示给用户的维度名称或标签")
    dimension: str = Field(..., description="对应的霍兰德维度代码，例如 R/I/A/S/E/C")

    model_config = ConfigDict(extra="allow")


class QuestionActivityEntryModel(BaseModel):
    """活动条目的验证模型"""

    label: str = Field(..., description="活动名称或标题，用于呈现给用户")
    description: str = Field("", description="活动的补充说明或示例描述")
    dimension: str = Field(..., description="活动关联的霍兰德维度代码")

    model_config = ConfigDict(extra="allow")


class QuestionSettingsModel(BaseModel):
    """题目设置的验证模型"""

    response_time_limit: Optional[int] = Field(
        None,
        description="题目的作答时间限制（秒），为空表示不限制",
    )
    max_select: Optional[int] = Field(
        None,
        description="多选题允许选择的最大选项数量",
    )
    scale: Optional[QuestionScaleConfigModel] = Field(
        None,
        description="量表题的取值范围与步进设置",
    )
    dimensions: Optional[List[QuestionDimensionEntryModel]] = Field(
        None,
        description="量表题或词汇题涉及的维度列表，用于映射用户输入",
    )
    max_hours: Optional[float] = Field(
        None,
        description="时间分配题可分配的总时长（小时），为空表示未设限制",
    )
    activities: Optional[List[QuestionActivityEntryModel]] = Field(
        None,
        description="时间分配题的活动列表，与维度一一对应",
    )
    notes: Optional[str] = Field(
        None,
        description="题目配置的补充说明或出题备注",
    )

    model_config = ConfigDict(extra="allow")


# ============================================================================
# TypedDict Definitions (保留用于类型提示)
# ============================================================================


class QuizScoringFormulaConfig(TypedDict, total=False):
    max_occurrences: int
    expression: str


class QuizScoringConfig(TypedDict, total=False):
    strategy: str
    dimension_formulas: dict[str, QuizScoringFormulaConfig]
    weights: dict[str, float]
    notes: str


class QuizConfig(TypedDict, total=False):
    slug: str
    scoring: QuizScoringConfig


class QuestionScaleConfig(TypedDict, total=False):
    min_value: float
    max_value: float
    step: float


class QuestionDimensionEntry(TypedDict):
    label: str
    dimension: str


class QuestionActivityEntry(TypedDict):
    label: str
    description: str
    dimension: str


class QuestionSettings(TypedDict, total=False):
    response_time_limit: int
    max_select: int
    scale: QuestionScaleConfig
    dimensions: List[QuestionDimensionEntry]
    max_hours: float
    activities: List[QuestionActivityEntry]
    notes: str


class AnswerExtraPayload(TypedDict, total=False):
    values: dict[str, float]
    allocations: dict[str, float]


class QuizRecommendationPayload(TypedDict):
    profession_id: int
    name: str
    match_score: int
    reason: str


class QuizReportPayload(TypedDict):
    holland_code: str
    dimension_scores: dict[str, int]
    recommendations: List[QuizRecommendationPayload]
    reward_points: int
    component_scores: NotRequired[dict[str, dict[str, float]]]


class QuizStartResponse(BaseModel):
    session_id: str = Field(..., description="测评会话ID")
    expires_at: datetime = Field(..., description="会话过期时间")
    server_time: datetime = Field(..., description="服务器当前时间(UTC)")


class QuizOption(BaseModel):
    """测评题目的单个选项。"""

    id: int = Field(..., description="选项ID")
    text: str = Field(..., description="选项内容")
    dimension: Optional[str] = Field(None, description="对应的霍兰德维度，可为空")
    image_url: Optional[str] = Field(None, description="选项图片 URL，可为空")

    model_config = ConfigDict(from_attributes=True)


class QuizQuestion(BaseModel):
    """测评题目信息及用户作答数据。"""

    question_id: int = Field(..., description="题目ID")
    type: str = Field(..., description="题目类型标识")
    title: Optional[str] = Field(None, description="题目标题，可选")
    content: str = Field(..., description="题目内容/描述")
    options: List[QuizOption] = Field(..., description="题目可选项列表")
    selected_option_id: Optional[int] = Field(None, description="用户当前选中的单选选项ID")
    selected_option_ids: Optional[List[int]] = Field(None, description="用户当前选中的多选选项ID列表")
    rating_value: Optional[float] = Field(None, description="用户当前填写的打分值")
    metric_values: Optional[Dict[str, float]] = Field(None, description="多维滑块/评分题当前值映射")
    allocations: Optional[Dict[str, float]] = Field(None, description="时间/资源分配题当前值映射")
    settings: QuestionSettings = Field(default_factory=QuestionSettings, description="题目额外配置")

    model_config = ConfigDict(from_attributes=True)


class QuizQuestionsResponse(BaseModel):
    """获取题目接口的响应体。"""

    session_id: str = Field(..., description="测评会话ID")
    questions: List[QuizQuestion] = Field(..., description="本次测评包含的题目列表")
    server_time: datetime = Field(..., description="服务器当前时间(UTC)")


class QuizAnswerBase(BaseModel):
    """作答请求公共字段。"""

    question_id: int = Field(..., description="题目ID")
    response_time: Optional[int] = Field(None, ge=0, description="答题耗时(秒)")


class _SingleOptionAnswer(QuizAnswerBase):
    """单选题答案公共字段。"""

    option_id: int = Field(..., description="被选中的选项ID")


class _MultiOptionAnswer(QuizAnswerBase):
    """多选题答案公共字段。"""

    option_ids: List[int] = Field(..., min_length=1, description="被选中的选项ID列表")


class QuizClassicScenarioAnswer(_SingleOptionAnswer):
    """经典情景题答案（单选）。"""

    type: Literal["classic_scenario"] = Field("classic_scenario", description="题目类型-经典情景（单选）")


class QuizWordChoiceAnswer(_MultiOptionAnswer):
    """词汇选择题答案（多选）。"""

    type: Literal["word_choice"] = Field("word_choice", description="题目类型-词汇多选")


class QuizImagePreferenceAnswer(_MultiOptionAnswer):
    """图片偏好题答案（多选）。"""

    type: Literal["image_preference"] = Field("image_preference", description="题目类型-图片偏好多选")


class QuizRatingAnswer(QuizAnswerBase):
    """评分题答案。"""

    type: Literal["rating"] = Field("rating", description="题目类型-评分题")
    rating_value: float = Field(..., description="用户给出的评分值")


class QuizValueBalanceAnswer(QuizAnswerBase):
    """价值平衡题答案（滑块）。"""

    type: Literal["value_balance"] = Field("value_balance", description="题目类型-价值平衡滑块题")
    values: Dict[str, float] = Field(..., description="各维度的评分百分比映射")


class QuizTimeAllocationAnswer(QuizAnswerBase):
    """资源/时间分配题答案。"""

    type: Literal["time_allocation"] = Field("time_allocation", description="题目类型-时间/资源分配题")
    allocations: Dict[str, float] = Field(..., description="各维度分配的数量 (小时数等)")


class QuizLegacySingleChoiceAnswer(_SingleOptionAnswer):
    """兼容旧版字段的单选题答案。"""

    type: Literal["single_choice"] = Field(
        "single_choice",
        description="[兼容] 旧版答案类型-单选，请尽快迁移至 classic_scenario",
    )


class QuizLegacyMultipleChoiceAnswer(_MultiOptionAnswer):
    """兼容旧版字段的多选题答案。"""

    type: Literal["multiple_choice"] = Field(
        "multiple_choice",
        description="[兼容] 旧版答案类型-多选，请尽快迁移至具体题目类型",
    )


class QuizLegacyMetricsAnswer(QuizAnswerBase):
    """兼容旧版字段的多维滑块题答案。"""

    type: Literal["metrics"] = Field("metrics", description="[兼容] 旧版答案类型-多维滑块")
    values: Dict[str, float] = Field(..., description="各维度的评分百分比映射")


class QuizLegacyAllocationAnswer(QuizAnswerBase):
    """兼容旧版字段的资源分配题答案。"""

    type: Literal["allocation"] = Field("allocation", description="[兼容] 旧版答案类型-资源分配")
    allocations: Dict[str, float] = Field(..., description="各维度分配的数量 (小时数等)")


QuizAnswerItem = Annotated[
    Union[
        QuizClassicScenarioAnswer,
        QuizWordChoiceAnswer,
        QuizImagePreferenceAnswer,
        QuizRatingAnswer,
        QuizValueBalanceAnswer,
        QuizTimeAllocationAnswer,
        QuizLegacySingleChoiceAnswer,
        QuizLegacyMultipleChoiceAnswer,
        QuizLegacyMetricsAnswer,
        QuizLegacyAllocationAnswer,
    ],
    Field(discriminator="type"),
]


class QuizAnswerRequest(BaseModel):
    """保存答题记录的请求体。"""

    session_id: str = Field(..., description="测评会话ID")
    answers: List[QuizAnswerItem] = Field(..., description="本次提交的题目答案列表")


class QuizAnswerResponse(BaseModel):
    """保存答题后的通用响应。"""

    msg: str = Field(..., description="提示信息")


class QuizProfileRequest(BaseModel):
    """提交/更新用户个性化档案的请求体。"""

    career_stage: str = Field(
        ...,
        description="职业阶段：高中生/大学生/职场新人/资深宇航员/星际指挥官",
    )
    major: str = Field(..., description="专业方向", min_length=1, max_length=200)
    career_confusion: str = Field(..., description="职业困惑", min_length=1)
    short_term_goals: List[str] = Field(
        ...,
        description="短期目标列表",
        min_length=1,
    )


class QuizProfileResponse(BaseModel):
    """用户个性化档案响应体。"""

    career_stage: str = Field(..., description="职业阶段")
    major: str = Field(..., description="专业方向")
    career_confusion: str = Field(..., description="职业困惑")
    short_term_goals: List[str] = Field(..., description="短期目标列表")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")


class QuizSubmitRequest(BaseModel):
    """提交测评的请求体。"""

    session_id: str = Field(..., description="测评会话ID")


class QuizRecommendation(BaseModel):
    """测评匹配的职业推荐。"""

    profession_id: int = Field(..., description="匹配的职业ID (对应 careers 表)")
    name: str = Field(..., description="职业名称")
    match_score: int = Field(..., description="与用户匹配度(0-100)")
    reason: str = Field(..., description="推荐理由摘要")


class QuizReportData(BaseModel):
    """测评结果详细数据。"""

    holland_code: str = Field(..., description="霍兰德兴趣代码")
    dimension_scores: dict[str, int] = Field(..., description="各维度得分映射")
    recommendations: List[QuizRecommendation] = Field(..., description="系统推荐的职业列表")
    reward_points: int = Field(..., description="完成测评获得的积分")
    component_scores: Optional[Dict[str, Dict[str, float]]] = Field(
        None,
        description="按题型拆分的各维度得分 (百分制)",
    )


class QuizReportResponse(BaseModel):
    """查询测评报告的响应体。"""

    session_id: str = Field(..., description="测评会话ID")
    report: QuizReportData = Field(..., description="测评报告详情")
