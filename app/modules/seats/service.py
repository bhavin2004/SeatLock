from uuid import UUID
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.modules.seats.models import Seat
from app.modules.seats.schemas import SeatCreate
from app.modules.seats import repository as seat_repository
from app.modules.screens import repository as screen_repository

def create_seat(db: Session, *, screen_id: UUID, data: SeatCreate) -> Seat:

    screen = screen_repository.get_by_id(db, screen_id=screen_id)
    if screen is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Screen does not exist"
        )

    seat = Seat(
        screen_id=screen_id,
        row_label=data.row_label,
        seat_number=data.seat_number,
        seat_type=data.seat_type
    )

    try:
        seat_repository.add_seat(db, seat=seat)
        db.commit()
    except Exception:
        db.rollback()
        raise

    return seat