from uuid import UUID
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.modules.seats.models import Seat


def list_by_ids_for_screen(db: Session, *,screen_id: UUID, seat_ids: list[UUID]):
    stmt = select(Seat).where(
        Seat.screen_id == screen_id,
        Seat.id.in_(seat_ids)
    )
    return list(db.scalars(stmt))

def list_by_screen(db: Session, *, screen_id: UUID) -> list[Seat]:
    stmt = select(Seat).where(Seat.screen_id == screen_id).order_by(Seat.row_label,Seat.seat_number)
    return list(db.scalars(stmt)) 


def add_seat(db: Session, *, seat: Seat) -> Seat:
    db.add(seat)
    db.flush()
    return seat