from datetime import datetime
from typing import Annotated, List, Literal, Optional, Union

from pydantic import BaseModel, Field


class QuizStartResponse(BaseModel):
    session_id: str = Field(..., description="测评会话ID")
    expires_at: datetime = Field(..., description="会话过期时间")
    server_time: datetime = Field(..., description="服务器当前时间(UTC)")


class QuizOption(BaseModel):
    """测评题目的单个选项。"""

    id: int = Field(..., description="选项ID")
    text: str = Field(..., description="选项内容")
    dimension: Optional[str] = Field(None, description="对应的霍兰德维度，可为空")

    class Config:
        from_attributes = True


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

    class Config:
        from_attributes = True


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


QuizAnswerItem = Annotated[
    Union[QuizSingleChoiceAnswer, QuizMultipleChoiceAnswer, QuizRatingAnswer],
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


class QuizReportResponse(BaseModel):
    """查询测评报告的响应体。"""

    session_id: str = Field(..., description="测评会话ID")
    report: QuizReportData = Field(..., description="测评报告详情")
