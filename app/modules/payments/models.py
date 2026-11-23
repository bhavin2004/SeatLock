from datetime import datetime
import enum

from app.database.base import Base
import uuid
from sqlalchemy import DateTime, Enum, Integer, CheckConstraint, String, UniqueConstraint, Uuid,ForeignKey, func
from sqlalchemy.orm import Mapped,mapped_column

class PaymentStatusEnum(enum.Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"
    REVIEW_REQUIRED = "review_required"


class Payment(Base):

    __tablename__ = "payments"

    __table_args__ = (
        CheckConstraint("amount_minor > 0", name="ck_payments_amount_minor_positive"),
        UniqueConstraint("provider_order_id", name="uq_payments_provider_order_id"),
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

    amount_minor: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    currency: Mapped[str] = mapped_column(
        String(3),
        nullable=False,
    )

    payment_status: Mapped[PaymentStatusEnum] = mapped_column(
        Enum(PaymentStatusEnum,
              name="payment_status_enum",
              values_callable=lambda x: [e.value for e in x]),
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    provider_order_id: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
        unique=True,
    )
    