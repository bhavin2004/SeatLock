from unittest.mock import MagicMock
import pytest
from fastapi import HTTPException
from app.modules.auth.schemas import UserLogin
from pydantic import SecretStr

from app.modules.auth import router as auth_router

def test_login_rejects_when_email_limit_is_exceeded(monkeypatch):
    monkeypatch.setattr(
        auth_router.settings, "REDIS_URL", SecretStr("redis://localhost:6379/0")
    )
    monkeypatch.setattr(
        auth_router, "count_login_request", MagicMock(return_value=(1, 60))
    )
    monkeypatch.setattr(
        auth_router, "count_login_request_by_email", MagicMock(return_value=(11, 35))
    )

    authenticate_user = MagicMock()
    monkeypatch.setattr(auth_router.service, "authenticate_user", authenticate_user)

    request = MagicMock()
    request.client.host = "127.0.0.1"
    data = UserLogin(email="test@example.com", password="test-password")

    with pytest.raises(HTTPException) as exc_info:
        auth_router.user_login(data, request, db=MagicMock())

    assert exc_info.value.status_code == 429
    assert exc_info.value.headers == {"Retry-After": "35"}
    authenticate_user.assert_not_called()


def test_login_rejects_when_ip_limit_is_exceeded(monkeypatch):
    monkeypatch.setattr(
        auth_router.settings, "REDIS_URL", SecretStr("redis://localhost:6379/0")
    )
    monkeypatch.setattr(
        auth_router, "count_login_request", MagicMock(return_value=(6, 42))
    )
    email_counter = MagicMock()
    monkeypatch.setattr(auth_router, "count_login_request_by_email", email_counter)

    authenticate_user = MagicMock()
    monkeypatch.setattr(auth_router.service, "authenticate_user", authenticate_user)

    request = MagicMock()
    request.client.host = "127.0.0.1"
    data = UserLogin(email="test@example.com", password="test-password")

    with pytest.raises(HTTPException) as exc_info:
        auth_router.user_login(data, request, db=MagicMock())

    assert exc_info.value.status_code == 429
    assert exc_info.value.headers == {"Retry-After": "42"}
    authenticate_user.assert_not_called()
    email_counter.assert_not_called()

