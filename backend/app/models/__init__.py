# Import all models to ensure they are registered with SQLAlchemy

# 用户相关
# 职业星球
from app.models.career import (
    Career,
    CareerGalaxy,
    CareerRecommendation,
)
from app.models.community import (
    CommunityCategory,
    CommunityCommentLike,
    CommunityGroup,
    CommunityGroupLike,
    CommunityGroupMember,
    CommunityPost,
    CommunityPostAttachment,
    CommunityPostComment,
    CommunityPostLike,
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
from app.models.mentors import (
    CommunityMentor,
    CommunityMentorSkill,
    MentorDomain,
    MentorDomainMap,
    MentorRequest,
)
from app.models.partners import (
    CommunityPartner,
    CommunityPartnerSkill,
    UserPartnerBinding,
)

# 测评系统
from app.models.quiz import (
    Option,
    Question,
    QuestionType,
    Quiz,
    QuizAnswer,
    QuizReport,
    QuizSubmission,
    UserProfile,
)
from app.models.user import User, UserRole

__all__ = [
    # 用户相关
    "User",
    "UserRole",
    # 测评系统
    "Quiz",
    "Question",
    "QuestionType",
    "Option",
    "QuizSubmission",
    "UserProfile",
    "QuizAnswer",
    "QuizReport",
    # 职业星球
    "Career",
    "CareerGalaxy",
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
    # 社区模块
    "CommunityCategory",
    "CommunityGroup",
    "CommunityGroupMember",
    "CommunityGroupLike",
    "CommunityPost",
    "CommunityPostAttachment",
    "CommunityPostLike",
    "CommunityPostComment",
    "CommunityCommentLike",
    # 社区：职业伙伴
    "CommunityPartner",
    "CommunityPartnerSkill",
    "UserPartnerBinding",
    # 社区：职业导师
    "CommunityMentor",
    "CommunityMentorSkill",
    "MentorDomain",
    "MentorDomainMap",
    "MentorRequest",
]
