from uuid import UUID

from sqlalchemy.orm import Session
from app.modules.theaters.models import Theater

def add_theater(db: Session, *, theater: Theater) -> Theater:
    db.add(theater)
    db.flush()
    return theater

def get_by_id(db: Session, theater_id: UUID) -> Theater | None:
    return db.get(Theater, theater_id)