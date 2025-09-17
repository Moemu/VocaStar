from typing import Literal

from dotenv import load_dotenv
from pydantic_settings import BaseSettings

load_dotenv()


class Config(BaseSettings):
    env: Literal["dev", "prod"] = "dev"
    """当前环境，dev 开发环境，prod 生产环境"""
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR"] = "DEBUG" if env == "dev" else "INFO"
    """日志等级"""

    # FastAPI 配置
    title: str = "FinancialCareerCommunity API"
    """API 服务标题"""
    version: str = "0.1.0"
    """API 服务版本"""
    host: str = "127.0.0.1"
    """API 本地回环地址(IP地址)"""
    port: int = 8080
    """API 服务端口"""

    # jwt 配置
    secret_key: str = "82ec285b5f0670c852c2e16d9776c5d17bd89a5f1dc09cdab5374a8a9ec7aa11"
    """32 位 hex 密钥，可以通过类似于 openssl rand -hex 32 的命令获得"""
    algorithm: str = "HS256"
    """jwt 签名算法"""
    expire_minutes: int = 60
    """密钥过期时间"""

    # 数据库配置
    db_url: str = "aiosqlite+sqlite:///./database.db"
    """orm 数据库连接字符串"""


config = Config()
