from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest
from fastapi import HTTPException
from starlette.requests import Request

import app.deps.auth as auth_deps
from app.models.user import UserRole


@pytest.mark.asyncio
async def test_get_current_user_optional_without_token(database):
    request = Request({"type": "http", "method": "GET", "headers": []})
    redis = AsyncMock()
    result = await auth_deps.get_current_user_optional(request, database, redis)
    assert result is None


@pytest.mark.asyncio
async def test_get_current_user_optional_returns_none_for_invalid_token(database, monkeypatch):
    request = Request(
        {
            "type": "http",
            "method": "GET",
            "headers": [(b"authorization", b"Bearer invalid")],
        }
    )
    redis = AsyncMock()

    async def fake_resolve(**_kwargs):
        raise HTTPException(status_code=401, detail="invalid")

    monkeypatch.setattr(auth_deps, "_resolve_user_from_token", fake_resolve)
    result = await auth_deps.get_current_user_optional(request, database, redis)
    assert result is None


@pytest.mark.asyncio
async def test_get_current_user_optional_success(database, monkeypatch):
    request = Request(
        {
            "type": "http",
            "method": "GET",
            "headers": [(b"authorization", b"Bearer valid")],
        }
    )
    redis = AsyncMock()
    user_obj = SimpleNamespace(username="demo")

    async def fake_resolve(**kwargs):
        assert kwargs["token"] == "valid"
        return user_obj

    monkeypatch.setattr(auth_deps, "_resolve_user_from_token", fake_resolve)
    result = await auth_deps.get_current_user_optional(request, database, redis)
    assert result is user_obj


@pytest.mark.asyncio
async def test_check_and_get_current_role_allows_matching_role(database, monkeypatch):
    redis = AsyncMock()
    wrapper = auth_deps.check_and_get_current_role(UserRole.admin)
    user_obj = SimpleNamespace(role=UserRole.admin)

    async def fake_resolve(**kwargs):
        assert kwargs["token"] == "ok"
        return user_obj

    monkeypatch.setattr(auth_deps, "_resolve_user_from_token", fake_resolve)
    result = await wrapper(database, "ok", redis)
    assert result is user_obj


@pytest.mark.asyncio
async def test_check_and_get_current_role_rejects_mismatch(database, monkeypatch):
    redis = AsyncMock()
    wrapper = auth_deps.check_and_get_current_role(UserRole.admin)

    async def fake_resolve(**_kwargs):
        return SimpleNamespace(role=UserRole.user)

    monkeypatch.setattr(auth_deps, "_resolve_user_from_token", fake_resolve)
    with pytest.raises(HTTPException) as exc:
        await wrapper(database, "bad", redis)
    assert exc.value.status_code == 403
