from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.api import auth, career, cosplay, quiz, user
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
app.mount("/static", StaticFiles(directory=str(config.static_dir)), name="static")

# 配置 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=config.cors_allow_origins,
    allow_credentials=config.cors_allow_credentials,
    allow_methods=config.cors_allow_methods,
    allow_headers=config.cors_allow_headers,
)

# 注册 API 路由
app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(user.router, prefix="/api/user", tags=["user"])
app.include_router(quiz.router, prefix="/api/quiz", tags=["quiz"])
app.include_router(career.router, prefix="/api/career", tags=["career"])
app.include_router(cosplay.router, prefix="/api/cosplay", tags=["cosplay"])

if __name__ == "__main__":
    import uvicorn

    logger.info(f"服务器地址: http://{config.host}:{config.port}")
    logger.info(f"FastAPI 文档地址: http://{config.host}:{config.port}/docs")
    logger.info(f"OpenAPI JSON 地址: http://{config.host}:{config.port}/openapi.json")
    uvicorn.run(app, host=config.host, port=config.port)
