from datetime import datetime
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.modules.shows.models import Show

def get_by_id(db: Session, show_id: UUID) -> Show | None:
    return db.get(Show, show_id)

def get_by_id_for_update(db: Session, show_id: UUID) -> Show | None:
    stmt = select(Show).where(Show.id == show_id).with_for_update()
    return db.scalar(stmt)

def list_upcoming_shows(db: Session, *, now: datetime, limit: int, offset: int) -> list[Show]:
    stmt = select(Show).where(Show.starts_at > now).order_by(Show.starts_at, Show.id).offset(offset).limit(limit)

    return list(db.scalars(stmt))

def add_show(db: Session, *, show: Show) -> Show:
    db.add(show)
    db.flush()
    return show