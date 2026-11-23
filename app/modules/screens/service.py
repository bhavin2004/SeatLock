from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.modules.screens.models import Screen
from app.modules.screens.schemas import ScreenCreate
from app.modules.screens import repository as screen_repository
from app.modules.theaters import repository as theater_repository

def create_screen(db: Session, *, data: ScreenCreate) -> Screen:
    if theater_repository.get_by_id(db, theater_id=data.theater_id) is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Theater does not exist"
        )
    screen = Screen(
        name=data.name,
        theater_id=data.theater_id
    )
    try:
        screen_repository.add_screen(db, screen=screen)
        db.commit()
    except Exception:
        db.rollback()
        raise

    return screen
    