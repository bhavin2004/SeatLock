from datetime import datetime
import enum

from app.database.base import Base
import uuid
from sqlalchemy import DateTime, Enum, UniqueConstraint, Uuid,ForeignKey
from sqlalchemy.orm import Mapped,mapped_column


class BookingStatusEnum(enum.Enum):
    PENDING_PAYMENT = "pending_payment"
    CONFIRMED = "confirmed"
    CANCELLED = "cancelled"
    EXPIRED = "expired"

class Booking(Base):

    __tablename__ = "bookings"
    
    
    id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        primary_key=True,
        default=uuid.uuid4
    )

    user_id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        ForeignKey("users.id"),
        nullable=False,
    )

    show_id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        ForeignKey("shows.id"),
        nullable=False
    )

    status: Mapped[BookingStatusEnum] = mapped_column(
        Enum(
            BookingStatusEnum,
            name="booking_status_enum",
            values_callable=lambda x: [e.value for e in x]
        ),
        nullable=False
    )

    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False
    )


class BookingSeat(Base):

    __tablename__ = "booking_seats"

    __table_args__ = (
        UniqueConstraint(
            "booking_id",
            "seat_id",
            name="uq_booking_seat"
        ),
    )
    id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        primary_key=True,
        default=uuid.uuid4
    )

    booking_id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        ForeignKey("bookings.id"),
        nullable=False,
    )

    seat_id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        ForeignKey("seats.id"),
        nullable=False
    )
