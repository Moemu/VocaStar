from pathlib import Path
from typing import Literal

from dotenv import load_dotenv
from pydantic_settings import BaseSettings

load_dotenv()


BASE_DIR = Path(__file__).resolve().parent.parent


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

    # CORS 配置
    cors_allow_origins: list[str] = ["*"] if env == "dev" else []
    """允许跨域的源列表，开发环境下允许所有来源"""
    cors_allow_methods: list[str] = ["*"]
    """允许的 HTTP 方法"""
    cors_allow_headers: list[str] = ["*"]
    """允许的 HTTP 头"""
    cors_allow_credentials: bool = True
    """是否允许携带凭证（如 Cookies）"""

    # jwt 配置
    secret_key: str = "82ec285b5f0670c852c2e16d9776c5d17bd89a5f1dc09cdab5374a8a9ec7aa11"
    """32 位 hex 密钥，可以通过类似于 openssl rand -hex 32 的命令获得"""
    algorithm: str = "HS256"
    """jwt 签名算法"""
    expire_minutes: int = 1440
    """密钥过期时间"""

    # JWXT 配置
    jwxt_encryption_key: str = "EWE1wl__6LIkWY1zNl5RS_ipky_bbYOf_8r5Tf4-e6E="
    """JWXT密码加密密钥，建议使用32字节的随机字符串"""
    jwxt_sync_interval_days: int = 90
    """JWXT自动同步间隔天数，默认90天（一学期）"""
    jwxt_api_timeout: int = 30
    """JWXT外部API请求超时时间（秒）"""

    # 数据库配置
    db_url: str = "sqlite+aiosqlite:///./database.db"
    """orm 数据库连接字符串"""

    # Redis 配置
    redis_host: str = "localhost"
    """Redis 主机地址"""
    redis_port: int = 6379
    """Redis 端口号"""

    # 静态资源与上传配置
    static_dir: Path = BASE_DIR / "static"
    """静态资源根目录"""
    avatar_subdir: str = "avatars"
    """头像文件子目录"""
    avatar_url_prefix: str = "/static/avatars"
    """头像访问 URL 前缀"""
    max_avatar_size: int = 2 * 1024 * 1024
    """头像文件大小限制，默认 2MB"""

    # LLM 配置
    llm_api_base_url: str = ""
    """OpenAI 兼容接口的基础地址，例如 http://localhost:11434/v1"""
    llm_api_key: str = ""
    """调用 LLM 服务所需的 API Key，若为空则视为未启用"""
    llm_default_model: str = "gpt-4o-mini"
    """默认使用的模型名称，可根据部署环境调整"""
    llm_request_timeout: float = 30.0
    """调用 LLM 服务的超时时间（秒）"""

    @property
    def avatar_dir(self) -> Path:
        """头像实际存储路径"""
        return self.static_dir / self.avatar_subdir


config = Config()
config.static_dir.mkdir(parents=True, exist_ok=True)
config.avatar_dir.mkdir(parents=True, exist_ok=True)
