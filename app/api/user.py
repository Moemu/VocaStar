import mimetypes
import time
from pathlib import Path
from typing import Annotated
from uuid import uuid4

import jwt
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import config
from app.core.logger import logger
from app.core.redis import get_redis_client
from app.deps.auth import get_current_user, get_db, oauth2_scheme
from app.models.user import User
from app.repositories.user import UserRepository
from app.schemas.user import (
    UserInfoResponse,
    UserResetPasswordRequest,
    UserSetProfileRequest,
)
from app.services.auth_service import (
    authenticate_user,
    get_password_hash,
)
from app.services.token_blacklist import add_token_to_blacklist

router = APIRouter()


ALLOWED_AVATAR_CONTENT_TYPES = {
    "image/jpeg",
    "image/png",
    "image/gif",
    "image/webp",
}

ALLOWED_AVATAR_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".webp"}

CONTENT_TYPE_EXTENSION_MAP = {
    "image/jpeg": ".jpg",
    "image/png": ".png",
    "image/gif": ".gif",
    "image/webp": ".webp",
}


@router.post("/resetpw", tags=["user"])
async def reset_password(
    form_data: UserResetPasswordRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    redis: Annotated[Redis, Depends(get_redis_client)],
    db: Annotated[AsyncSession, Depends(get_db)],
    token: str = Depends(oauth2_scheme),
) -> dict[str, str]:
    """校验旧密码后更新用户密码，并使当前令牌失效。"""
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


@router.post("/profile", tags=["user"])
async def set_profile(
    form_data: UserSetProfileRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> dict[str, str]:
    """更新当前用户的昵称、邮箱和头像地址。"""
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


@router.post("/avatar", tags=["user"])
async def upload_avatar(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
    file: UploadFile = File(...),
) -> dict[str, str]:
    """校验头像文件并保存至本地后更新用户头像地址。"""
    logger.info(f"用户 {current_user.username} 请求上传头像")

    user_repo = UserRepository(db)
    user = await user_repo.get_by_username(current_user.username)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    if not file.filename:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="文件名不能为空")

    content_type = file.content_type or mimetypes.guess_type(file.filename)[0]
    if not content_type or content_type not in ALLOWED_AVATAR_CONTENT_TYPES:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="不支持的头像文件类型")

    avatar_bytes = await file.read()
    if not avatar_bytes:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="上传头像文件为空")

    if len(avatar_bytes) > config.max_avatar_size:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="头像文件大小超出限制")

    extension = Path(file.filename).suffix.lower()
    if extension not in ALLOWED_AVATAR_EXTENSIONS:
        extension = CONTENT_TYPE_EXTENSION_MAP.get(content_type, extension)

    if extension not in ALLOWED_AVATAR_EXTENSIONS:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="不支持的头像文件扩展名")

    new_filename = f"{current_user.id}_{int(time.time())}_{uuid4().hex}{extension}"
    new_filepath = config.avatar_dir / new_filename

    try:
        with new_filepath.open("wb") as f:
            f.write(avatar_bytes)
    except OSError as exc:
        logger.exception("写入头像文件失败: %s", exc)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="保存头像失败")

    avatar_url = f"{config.avatar_url_prefix}/{new_filename}"
    old_avatar_url = user.avatar_url

    success = await user_repo.edit_info(user, avatar_url=avatar_url)
    if not success:
        new_filepath.unlink(missing_ok=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="更新头像失败")

    if old_avatar_url and old_avatar_url.startswith(config.avatar_url_prefix):
        relative_path = old_avatar_url.removeprefix(config.avatar_url_prefix).lstrip("/\\")
        old_filepath = (config.avatar_dir / relative_path).resolve()
        avatar_dir_resolved = config.avatar_dir.resolve()
        try:
            # Ensure the old file is within the avatar directory to prevent path traversal
            if (
                old_filepath.is_file()
                and old_filepath != new_filepath
                and str(old_filepath).startswith(str(avatar_dir_resolved))
            ):
                old_filepath.unlink()
        except OSError as exc:
            logger.warning("删除旧头像文件失败: %s", exc)

    logger.info(f"用户 {current_user.username} 上传头像成功")
    return {
        "msg": "头像上传成功",
        "avatar_url": avatar_url,
    }


@router.get("/profile", response_model=UserInfoResponse, tags=["user"])
async def get_current_user_info(current_user: Annotated[User, Depends(get_current_user)]):
    """获取当前登录用户信息"""
    return current_user
