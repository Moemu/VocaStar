from datetime import datetime
from typing import Annotated, Dict, List, Literal, NotRequired, Optional, Union

from pydantic import BaseModel, ConfigDict, Field
from typing_extensions import TypedDict


class QuizScoringFormulaConfigModel(BaseModel):
    """计分公式配置的验证模型"""

    max_occurrences: Optional[int] = None
    expression: Optional[str] = None

    model_config = ConfigDict(extra="allow")


class QuizScoringConfigModel(BaseModel):
    """计分策略配置的验证模型"""

    strategy: Optional[str] = None
    dimension_formulas: Optional[Dict[str, QuizScoringFormulaConfigModel]] = None
    weights: Optional[Dict[str, float]] = None
    notes: Optional[str] = None

    model_config = ConfigDict(extra="allow")


class QuizConfigModel(BaseModel):
    """测评配置的验证模型"""

    slug: Optional[str] = None
    scoring: Optional[QuizScoringConfigModel] = None

    model_config = ConfigDict(extra="allow")


class QuestionScaleConfigModel(BaseModel):
    """题目量表配置的验证模型"""

    min_value: float = 0.0
    max_value: float = 100.0
    step: float = 1.0

    model_config = ConfigDict(extra="allow")


class QuestionDimensionEntryModel(BaseModel):
    """维度条目的验证模型"""

    label: str
    dimension: str

    model_config = ConfigDict(extra="allow")


class QuestionActivityEntryModel(BaseModel):
    """活动条目的验证模型"""

    label: str
    description: str = ""
    dimension: str

    model_config = ConfigDict(extra="allow")


class QuestionSettingsModel(BaseModel):
    """题目设置的验证模型"""

    response_time_limit: Optional[int] = None
    max_select: Optional[int] = None
    scale: Optional[QuestionScaleConfigModel] = None
    dimensions: Optional[List[QuestionDimensionEntryModel]] = None
    max_hours: Optional[float] = None
    activities: Optional[List[QuestionActivityEntryModel]] = None
    notes: Optional[str] = None

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


class QuizSingleChoiceAnswer(QuizAnswerBase):
    """单选题答案。"""

    type: Literal["single_choice"] = Field("single_choice", description="答案类型-单选")
    option_id: int = Field(..., description="被选中的单选选项ID")


class QuizMultipleChoiceAnswer(QuizAnswerBase):
    """多选题答案。"""

    type: Literal["multiple_choice"] = Field("multiple_choice", description="答案类型-多选")
    option_ids: List[int] = Field(..., min_length=1, description="被选中的多选选项ID列表")


class QuizRatingAnswer(QuizAnswerBase):
    """评分题答案。"""

    type: Literal["rating"] = Field("rating", description="答案类型-评分")
    rating_value: float = Field(..., description="用户给出的评分值")


class QuizMetricsAnswer(QuizAnswerBase):
    """多维滑块题答案。"""

    type: Literal["metrics"] = Field("metrics", description="答案类型-多维滑块")
    values: Dict[str, float] = Field(..., description="各维度的评分百分比映射")


class QuizAllocationAnswer(QuizAnswerBase):
    """资源/时间分配题答案。"""

    type: Literal["allocation"] = Field("allocation", description="答案类型-资源分配")
    allocations: Dict[str, float] = Field(..., description="各维度分配的数量 (小时数等)")


QuizAnswerItem = Annotated[
    Union[
        QuizSingleChoiceAnswer,
        QuizMultipleChoiceAnswer,
        QuizRatingAnswer,
        QuizMetricsAnswer,
        QuizAllocationAnswer,
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
