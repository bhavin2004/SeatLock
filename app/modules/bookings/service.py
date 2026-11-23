from datetime import datetime, timedelta, timezone
from uuid import UUID
from app.modules.shows import repository as show_repository
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.modules.bookings.models import Booking
from app.modules.bookings.schemas import BookingCreate,BookingResponse
from app.modules.seats import repository as seat_repository
from app.modules.bookings import repository as booking_repository
from app.modules.bookings.models import BookingStatusEnum


def create_booking(
    db: Session,
    *,
    user_id: UUID,
    data: BookingCreate,
) -> BookingResponse:
    try:
            
        show = show_repository.get_by_id_for_update(db,data.show_id)
        if show is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Show does not Exist"
            )

        if show.starts_at <= datetime.now(timezone.utc):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Show has already started"
            )

        seats = seat_repository.list_by_ids_for_screen(
            db,
            screen_id=show.screen_id,
            seat_ids=data.seat_ids
        )

        found_ids = {seat.id for seat in seats}

        if not set(data.seat_ids).issubset(found_ids):
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
                detail="One or more seat IDs are invalid for this show"
            )

        unavailable_seat_ids = booking_repository.list_unavailable_seat_ids(
            db,
            show_id=show.id,
            seat_ids=data.seat_ids,
            now=datetime.now(timezone.utc)
        )

        if unavailable_seat_ids:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="One or more requested seats are unavailable"
            )

        booking = Booking(
            user_id=user_id,
            show_id=show.id,
            status=BookingStatusEnum.PENDING_PAYMENT,
            expires_at=datetime.now(timezone.utc) + timedelta(minutes=10)
        )

        booking_repository.add_booking_with_seats(
            db,
            booking=booking,
            seat_ids=data.seat_ids
        )

        response = BookingResponse(
            id=booking.id,
            show_id=booking.show_id,
            seat_ids=data.seat_ids,
            status=booking.status,
            expires_at=booking.expires_at
        )

        db.commit()


    except Exception :
        db.rollback()
        raise

    return response


def get_booking_details(
    db: Session, *, booking_id: UUID, user_id: UUID
) -> BookingResponse:
    booking = booking_repository.get_booking_for_user(
        db,
        booking_id=booking_id,
        user_id=user_id
    )

    if booking is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Booking does not exist"
        )

    seat_ids = booking_repository.list_seat_ids_for_booking(
        db,
        booking_id=booking.id
    )

    response = BookingResponse(
        id=booking.id,
        show_id=booking.show_id,
        seat_ids=seat_ids,
        status=booking.status,
        expires_at=booking.expires_at
    )

    return response

def cancel_booking(db: Session, *, booking_id: UUID, user_id: UUID) -> None:
    try:
        booking = booking_repository.get_booking_for_user_for_update(
            db,
            booking_id=booking_id,
            user_id=user_id
        )

        if booking is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Booking does not exist"
            )

        if (
            booking.status != BookingStatusEnum.PENDING_PAYMENT
            or booking.expires_at <= datetime.now(timezone.utc)
        ):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Booking cannot be cancelled"
            )
        booking.status = BookingStatusEnum.CANCELLED
        db.commit()
    except Exception:
        db.rollback()
        raise


def confirm_booking(db: Session, *, booking_id: UUID, user_id: UUID) -> None:
    try:
        booking = booking_repository.get_booking_for_user(
            db,
            booking_id=booking_id,
            user_id=user_id
        )


        if booking is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Booking does not exist"
            )
        
        show_repository.get_by_id_for_update(db, booking.show_id)

        booking = booking_repository.get_booking_for_user_for_update(
            db,
            booking_id=booking_id,
            user_id=user_id
        )

        if booking is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Booking does not exist"
            )


        if (
            booking.status != BookingStatusEnum.PENDING_PAYMENT
            or booking.expires_at <= datetime.now(timezone.utc)
        ):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Booking cannot be confirmed"
            )
        booking.status = BookingStatusEnum.CONFIRMED
        db.commit()
    except Exception:
        db.rollback()
        raise
