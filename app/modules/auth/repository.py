import uuid

from sqlalchemy.orm import Session
from app.modules.auth.models import User
from sqlalchemy import select

def get_user_by_email(db:Session , email: str) -> User | None:
    stmt = select(User).filter(User.email == email)

    return db.scalar(statement=stmt)

def create_user(db: Session, user: User) -> User:
    db.add(user)
    db.flush()
    return user


def get_user_by_id(db: Session, user_id: uuid.UUID) -> User | None:
    stmt = select(User).filter(User.id == user_id)
    
    return db.scalar(statement=stmt)