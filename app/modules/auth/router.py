from fastapi import APIRouter
from fastapi import Depends, status
from sqlalchemy.orm import Session
from app.modules.auth.models import User
from app.database.dependencies import get_db
from app.modules.auth.dependencies import get_current_user,require_admin
from app.modules.auth.schemas import UserRegister, UserResponse, UserLogin, TokenResponse
from app.modules.auth import service
from app.core.security import create_access_token


router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED
)
def user_register(user: UserRegister,db: Session = Depends(get_db)) -> User:
    return service.register_user(db,user)


@router.post(
    "/login",
    response_model=TokenResponse,
    status_code=200
)
def user_login(data: UserLogin, db: Session = Depends(get_db)) -> TokenResponse:
    user = service.authenticate_user(db,data)
    token = create_access_token(str(user.id))
    return TokenResponse(access_token=token)


@router.get("/me",response_model=UserResponse)
def get_my_profile(current_user: User = Depends(get_current_user)) -> User:
    return current_user