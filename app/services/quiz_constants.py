from __future__ import annotations

SESSION_DURATION_MINUTES = 30
REWARD_POINTS = 50
DIMENSION_PRIORITY = ["R", "I", "A", "S", "E", "C"]
DIMENSION_LABELS = {
    "R": "现实型 R",
    "I": "研究型 I",
    "A": "艺术型 A",
    "S": "社会型 S",
    "E": "企业型 E",
    "C": "常规型 C",
}
MAX_RECOMMENDATIONS = 3

DIMENSION_ADVANTAGE_KEYWORDS = {
    "R": "动手实践",
    "I": "深入钻研",
    "A": "创意表达",
    "S": "沟通协作",
    "E": "目标驱动",
    "C": "秩序条理",
}

DIMENSION_ADVANTAGE_BENEFITS = {
    "R": "把想法快速落地并验证成效",
    "I": "找出问题的底层规律并提供洞见",
    "A": "为团队带来新颖视角和体验",
    "S": "帮助不同人群快速建立信任",
    "E": "调动资源推动团队达成目标",
    "C": "打造稳定可靠的流程标准",
}
