import time
from typing import Annotated

import jwt
from fastapi import APIRouter, Depends, HTTPException, status
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import config
from app.core.logger import logger
from app.core.redis import get_redis_client
from app.deps.auth import get_current_user, get_db, oauth2_scheme
from app.models.user import User
from app.repositories.user import UserRepository
from app.schemas.user import (
    UserResetPasswordRequest,
    UserSetProfileRequest,
)
from app.services.auth_service import (
    authenticate_user,
    get_password_hash,
)
from app.services.token_blacklist import add_token_to_blacklist

router = APIRouter()


@router.post("/resetpw", tags=["user"])
async def reset_password(
    form_data: UserResetPasswordRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    redis: Annotated[Redis, Depends(get_redis_client)],
    db: Annotated[AsyncSession, Depends(get_db)],
    token: str = Depends(oauth2_scheme),
):
    logger.info(f"用户 {current_user.username} 请求重置密码")

    # 获取用户
    user_repo = UserRepository(db)
    user = await user_repo.get_by_username(current_user.username)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    # 验证旧密码
    user = await authenticate_user(user_repo, current_user.username, form_data.old_password)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    # 修改密码
    hashed_password = get_password_hash(form_data.new_password)
    await user_repo.change_password(user, hashed_password)

    # 将当前 token 加入黑名单
    payload = jwt.decode(token, config.secret_key, algorithms=config.algorithm)
    jti = payload.get("jti")
    exp = payload.get("exp")
    now = int(time.time())
    ttl = exp - now

    logger.debug(f"将 jti {jti[-5:]} 加入到 redis 黑名单中...")
    await add_token_to_blacklist(redis, jti, ttl)

    logger.info(f"用户 {current_user.username} 登出成功，jti 已禁用")
    return {"msg": "密码重置成功，请使用新密码登录"}


@router.post("/set_profile", tags=["user"])
async def set_profile(
    form_data: UserSetProfileRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    logger.info(f"用户 {current_user.username} 请求更新个人资料")

    # 获取用户
    user_repo = UserRepository(db)
    user = await user_repo.get_by_username(current_user.username)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    # 更新资料
    await user_repo.edit_info(
        user,
        nickname=form_data.nickname,
        email=form_data.email,
        avatar_url=form_data.avatar_url,
    )

    logger.info(f"用户 {current_user.username} 个人资料更新成功")
    return {"msg": "个人资料更新成功"}
