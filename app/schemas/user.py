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
        examples=["user@example.com"],
    )
    """邮箱"""
    avatar_url: Optional[str] = Field(
        None,
        description="头像URL",
        pattern=r"^(https?://).+",
        examples=["https://example.com/avatar.png"],
    )
    """头像URL"""
