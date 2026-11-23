

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.modules.payments.models import Payment, PaymentStatusEnum


def add_payment(db: Session, *, payment: Payment) -> None:
    db.add(payment)
    db.flush()
    return 

def get_payment_by_id(db: Session, *, payment_id: UUID) -> Payment | None:
    return db.get(Payment, payment_id) 

def get_payment_by_id_for_update(db: Session, *, payment_id: UUID) -> Payment | None:
    stmt = select(Payment).where(Payment.id == payment_id).with_for_update().execution_options(populate_existing=True)
    return db.scalar(stmt)

def get_payment_for_booking(db: Session, *, booking_id: UUID, payment_id: UUID) -> Payment | None:
    stmt = select(Payment).where(Payment.booking_id == booking_id, Payment.id == payment_id)
    return db.scalar(stmt)

def get_pending_payment_for_booking(db: Session, *, booking_id: UUID) -> Payment | None:
    stmt = select(Payment).where(Payment.booking_id == booking_id, Payment.payment_status == PaymentStatusEnum.PENDING).order_by(Payment.created_at.desc(),Payment.id.desc()).limit(1)
    return db.scalar(stmt)

def get_payment_by_provider_order_id(
    db: Session, *, provider_order_id: str
) -> Payment | None:
    stmt = select(Payment).where(Payment.provider_order_id == provider_order_id)
    return db.scalar(stmt)