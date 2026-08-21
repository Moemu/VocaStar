from pathlib import Path
from uuid import uuid4

from httpx import AsyncClient
from sqlalchemy.dialects import sqlite
from sqlalchemy.sql import column

from app.core.config import config
from app.models.user import User
from app.repositories.user import UserRepository
from app.services.auth_service import get_password_hash


async def test_reset_password(student_client: AsyncClient, test_user: User):
    # Test with correct old password
    response = await student_client.post(
        "/api/user/resetpw",
        json={"old_password": "123456", "new_password": "newpassword"},
    )

    assert response.status_code == 200


async def test_upload_avatar(student_client: AsyncClient, test_user: User, user_repo: UserRepository):
    avatar_bytes = b"fake-image-content"
    response = await student_client.post(
        "/api/user/avatar",
        files={"file": ("avatar.png", avatar_bytes, "image/png")},
    )

    assert response.status_code == 200

    data = response.json()
    assert data["avatar_url"].startswith(config.avatar_url_prefix)

    filename = Path(data["avatar_url"]).name
    avatar_path = config.avatar_dir / filename
    assert avatar_path.is_file()
    assert avatar_path.read_bytes() == avatar_bytes

    # 数据库中的头像地址应更新
    updated_user = await user_repo.get_by_username(test_user.username)
    assert updated_user
    assert updated_user.avatar_url == data["avatar_url"]

    # 清理测试头像文件
    avatar_path.unlink(missing_ok=True)


async def test_set_profile(student_client: AsyncClient, test_user: User, user_repo: UserRepository):
    # 获取旧数据
    old_user = await user_repo.get_by_username(test_user.username)
    assert old_user

    new_nickname = "Updated Nick"
    new_email = f"{test_user.username}_{uuid4().hex[:6]}@example.com"

    response = await student_client.post(
        "/api/user/profile",
        json={
            "nickname": new_nickname,
            "email": new_email,
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert data.get("msg") == "个人资料更新成功"

    # 验证数据库更新
    updated = await user_repo.get_by_username(test_user.username)
    assert updated
    assert updated.nickname == new_nickname
    assert updated.email == new_email
    # 未修改的字段保持 (如 avatar_url 仍与之前一致)
    assert updated.avatar_url == old_user.avatar_url


async def test_get_current_user_info(student_client: AsyncClient, test_user: User):
    response = await student_client.get("/api/user/profile")
    assert response.status_code == 200
    payload = response.json()
    assert payload["username"] == test_user.username
    assert payload["role"] == test_user.role.value


async def test_user_repository_addition_and_delete(user_repo: UserRepository):
    prefix = f"order_{uuid4().hex[:6]}"

    first_order = await user_repo.get_addition_order(prefix)
    assert first_order == 1

    password_hash = get_password_hash("TempPass123")
    user = await user_repo.create_user(
        username=f"{prefix}_user",
        password_hash=password_hash,
        email=f"{prefix}@example.com",
    )
    assert user is not None

    second_order = await user_repo.get_addition_order(prefix)
    assert second_order == 2

    await user_repo.delete_user(user)

    final_order = await user_repo.get_addition_order(prefix)
    assert final_order == 1
    deleted = await user_repo.get_by_username(f"{prefix}_user")
    assert deleted is None


async def test_user_repository_term_filter_generates_sql(user_repo: UserRepository):
    expr = user_repo._term_filter(column("payload"), "2024-S1")
    compiled = expr.compile(dialect=sqlite.dialect(), compile_kwargs={"literal_binds": True})
    sql_text = str(compiled)
    assert "json_extract" in sql_text
    assert "$.term" in sql_text
    assert "2024-S1" in sql_text
