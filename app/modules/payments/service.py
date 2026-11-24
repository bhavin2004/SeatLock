from datetime import datetime, timezone
from uuid import UUID
from fastapi import HTTPException,status
from sqlalchemy.orm import Session
from app.modules.bookings import repository as booking_repository
from app.modules.bookings.models import BookingStatusEnum
from app.modules.payments.models import Payment,PaymentStatusEnum
from app.modules.payments import repository as payment_repository
from app.modules.payments.schemas import PaymentVerifyRequest
from app.modules.shows import repository as show_repository
from app.modules.payments import provider
from razorpay.errors import SignatureVerificationError

PRICE_PER_SEAT_MINOR  = 25_000

def create_payment_attempt(db: Session, *, booking_id: UUID, user_id: UUID) -> tuple[Payment, bool]:
    try:
        booking = booking_repository.get_booking_for_user_for_update(db, booking_id=booking_id, user_id=user_id)
        if booking is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Booking not found"
            )

        if booking.status != BookingStatusEnum.PENDING_PAYMENT or booking.expires_at <= datetime.now(timezone.utc):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Booking is not eligible for payment attempt"
            )

        existing_payment = payment_repository.get_pending_payment_for_booking(db, booking_id=booking.id)
        if existing_payment is not None:
            if existing_payment.provider_order_id is None:
                existing_payment.provider_order_id = provider.create_order(
                    payment_id=existing_payment.id,
                    amount_minor=existing_payment.amount_minor,
                    currency=existing_payment.currency
                )
            db.commit()
            return existing_payment, False

        seat_ids = booking_repository.list_seat_ids_for_booking(db,booking_id=booking.id)
        if not seat_ids:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Booking has no seats"
            ) 

        amount_minor = len(seat_ids) * PRICE_PER_SEAT_MINOR 

        payment_attempt = Payment(
            booking_id=booking.id,
            amount_minor=amount_minor,
            payment_status=PaymentStatusEnum.PENDING,
            currency="INR",
        )

        payment_repository.add_payment(db, payment=payment_attempt)
        payment_attempt.provider_order_id = provider.create_order(
            payment_id=payment_attempt.id,
            amount_minor=payment_attempt.amount_minor,
            currency=payment_attempt.currency
        )
        
        db.commit()


    except Exception:
        db.rollback()
        raise 

    return payment_attempt, True

def complete_payment(db: Session, *, payment_id: UUID, user_id: UUID) -> PaymentStatusEnum:
    try:
        payment = payment_repository.get_payment_by_id(db, payment_id=payment_id)

        if payment is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Payment not found"
            )

        booking = booking_repository.get_booking_for_user(db, booking_id=payment.booking_id, user_id=user_id)

        if booking is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Booking not found"
            )
        show = show_repository.get_by_id_for_update(db, show_id=booking.show_id)

        if show is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Show not found"
            )

        booking = booking_repository.get_booking_for_user_for_update(db, booking_id=payment.booking_id, user_id=user_id)

        if booking is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Booking not found"
            )
        payment = payment_repository.get_payment_by_id_for_update(db, payment_id=payment_id)

        if payment is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Payment not found"
            )

        if booking.status == BookingStatusEnum.CONFIRMED and payment.payment_status == PaymentStatusEnum.COMPLETED:
            db.rollback()
            return PaymentStatusEnum.COMPLETED

        if payment.payment_status == PaymentStatusEnum.REVIEW_REQUIRED:
            db.rollback()
            return PaymentStatusEnum.REVIEW_REQUIRED
        
        if payment.payment_status != PaymentStatusEnum.PENDING:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Payment is not pending"
            )

        now = datetime.now(timezone.utc)

        if booking.status in (
            BookingStatusEnum.CANCELLED,
            BookingStatusEnum.EXPIRED,
            BookingStatusEnum.CONFIRMED) or (
            booking.status == BookingStatusEnum.PENDING_PAYMENT
            and booking.expires_at <= now
        ):
            payment.payment_status = PaymentStatusEnum.REVIEW_REQUIRED
            db.commit()
            return PaymentStatusEnum.REVIEW_REQUIRED

        if booking.status != BookingStatusEnum.PENDING_PAYMENT:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Booking is not eligible for payment completion",
            )
        
        
        payment.payment_status = PaymentStatusEnum.COMPLETED
        booking.status = BookingStatusEnum.CONFIRMED
        db.commit()

    except Exception:
        db.rollback()
        raise
    return PaymentStatusEnum.COMPLETED

def get_payment_details(
    db: Session, *, booking_id: UUID, payment_id: UUID, user_id: UUID
) -> Payment:
    booking = booking_repository.get_booking_for_user(db, booking_id=booking_id, user_id=user_id)
    if booking is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Booking not found"
        )
    payment = payment_repository.get_payment_for_booking(db, booking_id=booking_id, payment_id=payment_id)
    if payment is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Payment not found"
        )
    return payment

def verify_checkout_payment(db: Session, *, payment_id: UUID, booking_id: UUID, user_id: UUID, data: PaymentVerifyRequest) -> PaymentStatusEnum:
    try:
        
        payment =  get_payment_details(db, booking_id=booking_id, payment_id=payment_id, user_id=user_id)

        provider_order_id = payment.provider_order_id
        if provider_order_id is None or provider_order_id != data.razorpay_order_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Razorpay order does not match this payment",
            )

        provider.verify_payment_signature(
            razorpay_payment_id=data.razorpay_payment_id,
            provider_order_id=provider_order_id,
            razorpay_signature=data.razorpay_signature,
        )
        remote_payment = provider.fetch_payment(
                            razorpay_payment_id=data.razorpay_payment_id,
                        )

        if (
            remote_payment.get("order_id") != provider_order_id 
            or remote_payment.get("amount") != payment.amount_minor
            or remote_payment.get("currency") != payment.currency
        ):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Razorpay payment details do not match this payment",
            )

        if remote_payment.get("status") != "captured":
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Razorpay payment has not been captured",
            )
    except SignatureVerificationError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid Razorpay payment signature",
        ) from exc
    except Exception:
        db.rollback()
        raise

    return complete_payment(
        db,
        payment_id=payment_id,
        user_id=user_id
    )


def complete_payment_from_webhook(
        db: Session,
        *, 
        provider_order_id: str,
        amount_minor: int,
        currency: str,
        payment_status: str,
) -> PaymentStatusEnum | None:
    payment = payment_repository.get_payment_by_provider_order_id(db, provider_order_id=provider_order_id)
    if payment is None:
        return

    if(
        payment_status != "captured"
        or payment.amount_minor != amount_minor
        or payment.currency != currency
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Webhook payment details do not match this payment",
        )

    booking = booking_repository.get_booking_by_id(db, booking_id=payment.booking_id)

    if booking is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Booking not found"
        )

    return complete_payment(
        db,
        payment_id=payment.id,
        user_id=booking.user_id
    )
    


     