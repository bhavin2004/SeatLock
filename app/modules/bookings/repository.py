from datetime import datetime
from uuid import UUID

from sqlalchemy import select,and_,or_
from sqlalchemy.orm import Session

from app.modules.bookings.models import Booking, BookingSeat
from app.modules.bookings.models import BookingStatusEnum

def list_unavailable_seat_ids(
    db: Session,
    *,
    show_id: UUID,
    seat_ids: list[UUID],
    now: datetime,
) -> set[UUID]:
    stmt = select(BookingSeat.seat_id).join(
        Booking,
        BookingSeat.booking_id == Booking.id,   
    ).where(
        Booking.show_id == show_id,
        BookingSeat.seat_id.in_(seat_ids),
        or_(
            Booking.status == BookingStatusEnum.CONFIRMED,
            and_(
                Booking.status == BookingStatusEnum.PENDING_PAYMENT,
                Booking.expires_at > now,
            ),
        ),
    )

    return set(db.scalars(stmt))


def add_booking_with_seats(
    db: Session,
    *,
    booking: Booking,
    seat_ids: list[UUID],
) -> None:
    db.add(booking)
    db.flush()

    booking_seats = [
        BookingSeat(booking_id=booking.id, seat_id=seat_id)
        for seat_id in seat_ids
    ]
    db.add_all(booking_seats)
    db.flush()


def get_booking_for_user(db: Session, *, booking_id: UUID, user_id: UUID) -> Booking | None:
    stmt = select(Booking).where(
        Booking.id == booking_id,
        Booking.user_id == user_id,
    )
    return db.scalar(stmt)

def list_seat_ids_for_booking(db: Session, *, booking_id: UUID) -> list[UUID]:
    stmt = select(BookingSeat.seat_id).where(
        BookingSeat.booking_id == booking_id
    )
    return list(db.scalars(stmt))

def get_booking_for_user_for_update(db: Session, *, booking_id: UUID, user_id: UUID) -> Booking | None:
    stmt = select(Booking).where(
        Booking.id == booking_id,
        Booking.user_id == user_id,
    ).with_for_update().execution_options(populate_existing=True)
    return db.scalar(stmt)


def get_booking_by_id(db: Session, *, booking_id: UUID) -> Booking | None:
    return db.get(Booking, booking_id)
