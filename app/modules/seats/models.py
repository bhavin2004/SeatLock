import enum

from app.database.base import Base
import uuid
from sqlalchemy import CheckConstraint, Enum, Integer, Uuid,String,ForeignKey,UniqueConstraint
from sqlalchemy.orm import Mapped,mapped_column


class SeatTypeEnum(enum.Enum):
    REGULAR = "REGULAR"
    PREMIUM = "PREMIUM"
    

class Seat(Base):

    __tablename__ = "seats"
    
    __table_args__ = (
        UniqueConstraint(
            "screen_id",
            "row_label",
            "seat_number",
            name="uq_seats_screen_row_number"
        ),
        CheckConstraint(
            "seat_number > 0",
            name="ck_seats_seat_number_positive"
        )
    )
    id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        primary_key=True,
        default=uuid.uuid4
    )

    screen_id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        ForeignKey("screens.id"),
        nullable=False,
    )

    row_label: Mapped[str] = mapped_column(
        String(10),
        nullable=False
    )

    seat_number: Mapped[int] = mapped_column(
        Integer,
        nullable=False
    )

    seat_type: Mapped[SeatTypeEnum] = mapped_column(
        Enum(
            SeatTypeEnum,
            name="seat_type",
            values_callable=lambda x: [e.value for e in x]
            ),
        nullable=False
    )
