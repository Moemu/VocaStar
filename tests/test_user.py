from pathlib import Path

from httpx import AsyncClient

from app.core.config import config
from app.models.user import User
from app.repositories.user import UserRepository


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

    response = await student_client.post(
        "/api/auth/login",
        data={"username": test_user.username, "password": "newpassword"},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )

    assert response.status_code == 200
