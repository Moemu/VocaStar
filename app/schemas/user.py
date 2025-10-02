from typing import Optional

from pydantic import BaseModel, Field


class UserResetPasswordRequest(BaseModel):
    """
    用户重置密码请求体
    """

    old_password: str = Field(..., min_length=6, description="旧密码，至少六位(明文)")
    """旧密码"""
    new_password: str = Field(..., min_length=6, description="新密码，至少六位(明文)")
    """新密码"""


class UserSetProfileRequest(BaseModel):
    """
    用户设置个人资料请求体
    """

    nickname: Optional[str] = Field(None, description="昵称", examples=["沐妮卡", "萌沐"])
    """昵称"""
    email: Optional[str] = Field(
        None,
        description="邮箱",
        pattern=r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$",
        examples=["user@example.com", "test@gduf.edu.cn"],
    )
    """邮箱"""
    college: Optional[str] = Field(None, description="学院", examples=["计算机与信息工程学院", "经济与贸易学院"])
    """学院"""
    major: Optional[str] = Field(None, description="专业", examples=["计算机科学与技术", "国际经济与贸易"])
    """专业"""
    grade: Optional[int] = Field(None, description="年级", examples=[2023, 2024])
    """年级"""
