from app.modules.auth import repository
from sqlalchemy.orm import Session
from fastapi import HTTPException,status
from app.modules.auth.schemas import UserRegister,UserLogin
from app.modules.auth.models import User
from sqlalchemy.exc import IntegrityError
from app.core.security import hash_password,verify_password


def register_user(db: Session, data: UserRegister)-> User:
    try:
        email = data.email.lower().strip()
        if repository.get_user_by_email(db,email):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Email already registered"
            )
        user = User(
            email=email,
            password_hash = hash_password(data.password)
        )
        user = repository.create_user(db,user)
        db.commit()
        db.refresh(user)
        return user

    except IntegrityError:
            db.rollback()
            raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Email already registered"
                ) 
    except Exception:
        db.rollback()
        raise


def authenticate_user(db: Session, data: UserLogin) -> User:
    email = data.email.lower().strip()
    user = repository.get_user_by_email(db, email)
    if user is None or not verify_password(data.password,user.password_hash):
         raise HTTPException(
              status_code=status.HTTP_401_UNAUTHORIZED,
              detail="Invalid email or password"
         )
    if not user.is_active:
         raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is disabled"
        )

    return user