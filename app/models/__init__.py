# Import all models to ensure they are registered with SQLAlchemy

# 用户相关
# 职业星球
from app.models.career import (
    Career,
    CareerRecommendation,
    CareerTag,
    CareerTagRelation,
)

# Cosplay剧本
from app.models.cosplay import (
    CosplayReport,
    CosplayScript,
    CosplaySession,
    SessionState,
)

# 用户中心扩展功能
from app.models.extensions import (
    Achievement,
    Feedback,
    FeedbackStatus,
    FeedbackType,
    MessageType,
    Notification,
    PointTransaction,
    ReportBookmark,
    UserAchievement,
    UserPoints,
)
from app.models.profile import UserProfile

# 测评系统
from app.models.quiz import (
    Option,
    Question,
    QuestionType,
    Quiz,
    QuizAnswer,
    QuizReport,
    QuizSubmission,
)
from app.models.user import User, UserRole

__all__ = [
    # 用户相关
    "User",
    "UserRole",
    "UserProfile",
    # 测评系统
    "Quiz",
    "Question",
    "QuestionType",
    "Option",
    "QuizSubmission",
    "QuizAnswer",
    "QuizReport",
    # 职业星球
    "Career",
    "CareerTag",
    "CareerTagRelation",
    "CareerRecommendation",
    # Cosplay剧本
    "CosplayScript",
    "CosplaySession",
    "SessionState",
    "CosplayReport",
    # 用户中心扩展功能
    "ReportBookmark",
    "Notification",
    "MessageType",
    "UserPoints",
    "PointTransaction",
    "UserAchievement",
    "Achievement",
    "Feedback",
    "FeedbackStatus",
    "FeedbackType",
]
