from datetime import datetime, timezone
from uuid import UUID
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.modules.shows.models import Show
from app.modules.shows import repository as show_repository
from app.modules.seats import repository as seat_repository
from app.modules.shows.schemas import ShowCreate, ShowSeatResponse
from app.modules.bookings import repository as bookings_repository
from app.modules.movies import repository as movie_repository
from app.modules.screens import repository as screen_repository


def list_upcoming_shows(db: Session, *, limit: int, offset: int) -> list[Show]:
    now = datetime.now(timezone.utc)
    return show_repository.list_upcoming_shows(db, now=now, limit=limit, offset=offset)

def list_show_seats(db: Session, *, show_id: UUID) -> list[ShowSeatResponse]:
    response = []

    show = show_repository.get_by_id(db, show_id)
    if show is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Show does not exist"
        )
    seats = seat_repository.list_by_screen(db, screen_id=show.screen_id)


    unavailable_seat_ids = bookings_repository.list_unavailable_seat_ids(
        db,
        show_id=show.id,
        seat_ids=[seat.id for seat in seats],
        now=datetime.now(timezone.utc),
    )

    for seat in seats:
        response.append(
            ShowSeatResponse(
                id=seat.id,
                row_label=seat.row_label,
                seat_number=seat.seat_number,
                seat_type=seat.seat_type,
                is_available=seat.id not in unavailable_seat_ids
            )
        )
    
    return response

def create_show(db: Session, *, data: ShowCreate) -> Show:
    if data.starts_at <= datetime.now(timezone.utc):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="Show start time must be in the future."
        )
    movie = movie_repository.get_movie_by_id(db, data.movie_id)
    if movie is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Movie not found."
        )

    screen = screen_repository.get_by_id(db, data.screen_id)
    if screen is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Screen does not exist"
        )
    
    show = Show(
        movie_id=data.movie_id,
        screen_id=data.screen_id,
        starts_at=data.starts_at
    )

    try:
        show_repository.add_show(db, show=show)
        db.commit()
    except Exception:
        db.rollback()
        raise

    return show
