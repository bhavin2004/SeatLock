from fastapi import APIRouter, Request, HTTPException, status
from app.core.config import settings
from app.core.rate_limit import count_login_request, count_login_request_by_email
from fastapi import Depends, status
from sqlalchemy.orm import Session
from app.modules.auth.models import User
from app.database.dependencies import get_db
from app.modules.auth.dependencies import get_current_user
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
def user_login(data: UserLogin, request: Request,  db: Session = Depends(get_db), ) -> TokenResponse:

    if settings.REDIS_URL is not None:

        
        ip = request.client.host if request.client else "unknown"
        count, ttl = count_login_request(ip)

        if count > 5:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Too many login attempts. Try again later.",
                headers={"Retry-After": str(max(ttl, 1))},
            )

        email_count, email_ttl = count_login_request_by_email(data.email)

        if email_count > 10:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Too many login attempts. Try again later.",
                headers={"Retry-After": str(max(email_ttl, 1))},
            )
            
    user = service.authenticate_user(db,data)
    token = create_access_token(str(user.id))
    return TokenResponse(access_token=token)


@router.get("/me",response_model=UserResponse)
def get_my_profile(current_user: User = Depends(get_current_user)) -> User:
    return current_user