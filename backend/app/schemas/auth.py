from dataclasses import asdict, dataclass, field
from typing import Optional
from uuid import uuid4

from pydantic import BaseModel, Field


class Token(BaseModel):
    """
    jwt 密钥实体
    """

    access_token: str
    token_type: str


@dataclass
class Payload:
    """
    jwt Payload
    """

    sub: str
    """用户名"""
    exp: Optional[int] = None
    """过期时间"""
    jti: str = field(default_factory=lambda: uuid4().hex)
    """JWT ID"""

    def to_json(self):
        return asdict(self)


class RegisterRequest(BaseModel):
    """
    注册请求体
    """

    username: str = Field(..., description="用户名", examples=["Muika", "Moemu"])
    """用户名"""
    nickname: str = Field(..., description="昵称", examples=["沐妮卡", "萌沐"])
    """昵称"""
    email: str = Field(
        ...,
        description="邮箱",
        pattern=r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$",
        examples=["user@example.com"],
    )
    """邮箱"""
    password: str = Field(..., min_length=6, description="密码，至少六位(明文)")
    """密码"""
    role: str = Field(default="user", description="用户角色，默认为 user", examples=["user", "admin"])
    """用户角色"""
