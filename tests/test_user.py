from httpx import AsyncClient

from app.models.user import User


async def test_reset_password(student_client: AsyncClient, test_user: User):
    # Test with correct old password
    response = await student_client.post(
        "/api/user/resetpw",
        json={"old_password": "123456", "new_password": "newpassword"},
    )

    assert response.status_code == 200
    # Check that the response contains a token
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert isinstance(data["access_token"], str)
    assert len(data["access_token"]) > 0

    response = await student_client.post(
        "/api/auth/login",
        data={"username": test_user.username, "password": "newpassword"},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )

    assert response.status_code == 200
