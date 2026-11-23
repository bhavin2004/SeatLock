from uuid import UUID
from sqlalchemy.orm import Session
from app.modules.screens.models import Screen

def get_by_id(db: Session, screen_id: UUID) -> Screen | None:
    return db.get(Screen, screen_id)

def add_screen(db: Session, *, screen: Screen) -> Screen:
    db.add(screen)
    db.flush()
    return screen