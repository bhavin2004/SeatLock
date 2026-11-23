from datetime import datetime
import uuid

from pydantic import BaseModel, EmailStr, Field,ConfigDict

from app.modules.auth.models import UserRole

class UserRegister(BaseModel):
    email: EmailStr
    password: str = Field(max_length=128,min_length=8)


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    email: EmailStr
    role: UserRole
    is_active: bool
    created_at: datetime

class UserLogin(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str 
    token_type: str = "bearer"

