from pwdlib import PasswordHash
from datetime import datetime,timedelta,timezone
import jwt
from app.core.config import settings
from fastapi import HTTPException,status

password_hash = PasswordHash.recommended()

def hash_password(password: str) -> str:
    return password_hash.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return password_hash.verify(plain_password,hashed_password)


def create_access_token(user_id: str) -> str:
    current_time = datetime.now(timezone.utc)
    expiration_time = current_time+timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    payload = {
        "sub" : user_id,
        "iat" : current_time,
        "exp" : expiration_time,
        "type" : "access"

    }

    return jwt.encode(
        payload=payload,
        key=settings.JWT_SECRET_KEY.get_secret_value(),
        algorithm=settings.JWT_ALGORITHM
    )

def decode_access_token(token: str) -> dict:
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY.get_secret_value(),
            algorithms=[settings.JWT_ALGORITHM],
            options={
                "require": ["sub", "iat", "exp", "type"]
            }
        )
        if payload["type"] != "access":
           raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired token",
                headers={"WWW-Authenticate": "Bearer"}
            )
        return payload
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"}
            )

