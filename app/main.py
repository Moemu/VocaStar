from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import auth, user
from app.core.config import config
from app.core.logger import logger
from app.core.sql import close_db, load_db

logger.info("初始化 Server...")


# 启动/关闭事件
@asynccontextmanager
async def lifespan(app: FastAPI):
    await load_db()
    yield
    logger.info("正在退出...")
    await close_db()  # type:ignore
    logger.info("已安全退出")


app = FastAPI(title=config.title, version=config.version, lifespan=lifespan)

# 配置 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # 允许的前端源
    allow_credentials=True,
    allow_methods=["*"],  # 允许所有 HTTP 方法
    allow_headers=["*"],  # 允许所有请求头
)

# 注册 API 路由
app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(user.router, prefix="/api/user", tags=["user"])

if __name__ == "__main__":
    import uvicorn

    logger.info(f"服务器地址: http://{config.host}:{config.port}")
    logger.info(f"FastAPI 文档地址: http://{config.host}:{config.port}/docs")
    uvicorn.run(app, host=config.host, port=config.port)
