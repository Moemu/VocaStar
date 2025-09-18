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

    username: str = Field(..., description="用户名")
    """用户名"""
    realname: str = Field(..., description="真实姓名")
    """真实姓名"""
    email: str = Field(..., description="广金邮箱", pattern=r"^[a-zA-Z0-9._%+-]+@m\.gduf\.edu\.cn$")
    """广金邮箱"""
    password: str = Field(..., min_length=6, description="密码，至少六位")
    """密码"""
    role: Optional[str] = Field("student", description="用户角色，默认为 student")
    """用户角色"""
