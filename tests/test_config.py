from app.core.config import Settings
import pytest
from pydantic import ValidationError

def _make_settings(expiration_minutes: int) -> Settings:
    return Settings(
        _env_file=None, # type: ignore
        DATABASE_URL="postgresql://test:password@localhost/test_db",
        JWT_SECRET_KEY="test-only-secret",
        JWT_ALGORITHM="HS256",
        ACCESS_TOKEN_EXPIRE_MINUTES=expiration_minutes,
    )



def test_positive_access_token_expiration_is_accepted():
    setting = _make_settings(30)
    assert setting.ACCESS_TOKEN_EXPIRE_MINUTES == 30

def test_negative_access_token_expiration_is_rejected():
    with pytest.raises(ValidationError):
        _make_settings(-1)

def test_zero_access_token_expiration_is_rejected():
    with pytest.raises(ValidationError):
        _make_settings(0)