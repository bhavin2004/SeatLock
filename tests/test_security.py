from datetime import datetime, timedelta, timezone

from app.core.security import hash_password,verify_password
import jwt
from fastapi import HTTPException
import pytest
import uuid
from app.core.config import settings
from app.core.security import create_access_token,decode_access_token

sample_password = "CineBook@123"

hashed_password = hash_password(sample_password)

def test_hashed_password():
    assert verify_password(sample_password,hashed_password)

def test_wrong_password():
    assert verify_password("WrongPassword123",hashed_password) == False

def test_unique_salts():
    hash1 = hash_password(sample_password)
    hash2 = hash_password(sample_password)

    assert hash1 != hash2

def test_create_access_token():
    user_id = uuid.uuid4()
    jwt_token = create_access_token(str(user_id))
    assert jwt_token
    assert isinstance(jwt_token, str)

    decode_jwt_token = jwt.decode(
        jwt_token,
        settings.JWT_SECRET_KEY.get_secret_value(),
        algorithms=[settings.JWT_ALGORITHM]
    )

    assert decode_jwt_token["sub"] == str(user_id)
    assert decode_jwt_token["type"] == "access"
    assert decode_jwt_token["iat"] and decode_jwt_token["exp"] and decode_jwt_token["exp"]>decode_jwt_token["iat"]


def test_decode_access_token():
    user_id = uuid.uuid4()
    jwt_token = create_access_token(str(user_id))
    

    payload = decode_access_token(jwt_token)

    assert payload["sub"] == str(user_id)
    assert payload["type"] == "access"


def test_invalid_access_token():
    with pytest.raises(HTTPException) as exc_info:
        decode_access_token("invalid.jwt.token")

    assert exc_info.value.status_code == 401


def test_expired_access_token():
    user_id = uuid.uuid4()
    past_time = datetime.now(timezone.utc) - timedelta(hours=2)
    payload = {
            "sub" : str(user_id),
            "iat" : past_time,
            "exp" : past_time + timedelta(hours=1),
            "type" : "access"
    
        }

    token = jwt.encode(
        payload,
        settings.JWT_SECRET_KEY.get_secret_value(),
        settings.JWT_ALGORITHM
    )

    with pytest.raises(HTTPException) as exc_info:
        decode_access_token(token)

    assert exc_info.value.status_code == 401

def test_decode_uses_configured_algorithm(monkeypatch):
    monkeypatch.setattr(settings, "JWT_ALGORITHM", "HS384")
    user_id = uuid.uuid4()

    token = create_access_token(str(user_id))
    payload = decode_access_token(token)

    assert payload["sub"] == str(user_id)

