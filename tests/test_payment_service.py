from datetime import datetime, timedelta, timezone
from unittest.mock import MagicMock
from uuid import uuid4

from fastapi import HTTPException,status
import pytest
from app.modules.payments import service as payment_service
from app.modules.bookings.models import BookingStatusEnum
from app.modules.payments.models import PaymentStatusEnum


def test_complete_payment_confirms_active_booking(monkeypatch):
    fake_db = MagicMock()
    fake_booking = MagicMock()
    fake_booking.id = uuid4()
    fake_booking.show_id = uuid4()
    fake_booking.status = BookingStatusEnum.PENDING_PAYMENT
    fake_booking.expires_at = datetime.now(timezone.utc) + timedelta(minutes=10)

    fake_payment = MagicMock()
    fake_payment.payment_status = PaymentStatusEnum.PENDING
    fake_payment.booking_id = fake_booking.id

    monkeypatch.setattr(
        payment_service.payment_repository,
        "get_payment_by_id",
        MagicMock(return_value=fake_payment),
    )

    monkeypatch.setattr(
        payment_service.booking_repository,
        "get_booking_for_user_for_update",
        MagicMock(return_value=fake_booking),
    )

    monkeypatch.setattr(
        payment_service.booking_repository,
        "get_booking_for_user",
        MagicMock(return_value=fake_booking),
    )

    monkeypatch.setattr(
        payment_service.show_repository,
        "get_by_id_for_update",
        MagicMock(),
    )

    monkeypatch.setattr(
        payment_service.payment_repository,
        "get_payment_by_id_for_update",
        MagicMock(return_value=fake_payment),
    )

    result = payment_service.complete_payment(
        db=fake_db,
        payment_id=uuid4(),
        user_id=uuid4(),
    )

    assert result == PaymentStatusEnum.COMPLETED
    assert fake_payment.payment_status == PaymentStatusEnum.COMPLETED
    assert fake_booking.status == BookingStatusEnum.CONFIRMED
    fake_db.commit.assert_called_once()
    fake_db.rollback.assert_not_called()

def test_complete_payment_ignores_duplicate_success(monkeypatch):
    fake_db = MagicMock()
    fake_booking = MagicMock()
    fake_booking.id = uuid4()
    fake_booking.show_id = uuid4()
    fake_booking.status = BookingStatusEnum.CONFIRMED
    fake_booking.expires_at = datetime.now(timezone.utc) + timedelta(minutes=10)

    fake_payment = MagicMock()
    fake_payment.payment_status = PaymentStatusEnum.COMPLETED
    fake_payment.booking_id = fake_booking.id

    monkeypatch.setattr(
        payment_service.payment_repository,
        "get_payment_by_id",
        MagicMock(return_value=fake_payment),
    )

    monkeypatch.setattr(
        payment_service.booking_repository,
        "get_booking_for_user_for_update",
        MagicMock(return_value=fake_booking),
    )

    monkeypatch.setattr(
        payment_service.booking_repository,
        "get_booking_for_user",
        MagicMock(return_value=fake_booking),
    )

    monkeypatch.setattr(
        payment_service.show_repository,
        "get_by_id_for_update",
        MagicMock(),
    )

    monkeypatch.setattr(
        payment_service.payment_repository,
        "get_payment_by_id_for_update",
        MagicMock(return_value=fake_payment),
    )

    payment_service.complete_payment(
        db=fake_db,
        payment_id=uuid4(),
        user_id=uuid4(),
    )

    assert fake_payment.payment_status == PaymentStatusEnum.COMPLETED
    assert fake_booking.status == BookingStatusEnum.CONFIRMED
    fake_db.commit.assert_not_called()
    fake_db.rollback.assert_called_once()

def test_complete_payment_marks_expired_booking_for_review(monkeypatch):
    fake_db = MagicMock()
    fake_booking = MagicMock()
    fake_booking.id = uuid4()
    fake_booking.show_id = uuid4()
    fake_booking.status = BookingStatusEnum.PENDING_PAYMENT
    fake_booking.expires_at = datetime.now(timezone.utc) - timedelta(minutes=1)

    fake_payment = MagicMock()
    fake_payment.payment_status = PaymentStatusEnum.PENDING
    fake_payment.booking_id = fake_booking.id

    monkeypatch.setattr(
        payment_service.payment_repository,
        "get_payment_by_id",
        MagicMock(return_value=fake_payment),
    )

    monkeypatch.setattr(
        payment_service.booking_repository,
        "get_booking_for_user_for_update",
        MagicMock(return_value=fake_booking),
    )

    monkeypatch.setattr(
        payment_service.booking_repository,
        "get_booking_for_user",
        MagicMock(return_value=fake_booking),
    )

    monkeypatch.setattr(
        payment_service.show_repository,
        "get_by_id_for_update",
        MagicMock(),
    )

    monkeypatch.setattr(
        payment_service.payment_repository,
        "get_payment_by_id_for_update",
        MagicMock(return_value=fake_payment),
    )

    result = payment_service.complete_payment(
        db=fake_db,
        payment_id=uuid4(),
        user_id=uuid4(),
    )

    assert result == PaymentStatusEnum.REVIEW_REQUIRED
    assert fake_payment.payment_status == PaymentStatusEnum.REVIEW_REQUIRED
    assert fake_booking.status == BookingStatusEnum.PENDING_PAYMENT
    fake_db.commit.assert_called_once()
    fake_db.rollback.assert_not_called()


def test_create_payment_attempt_reuses_pending_payment(monkeypatch):
    fake_db = MagicMock()
    fake_booking = MagicMock()
    fake_booking.id = uuid4()
    fake_booking.status = BookingStatusEnum.PENDING_PAYMENT
    fake_booking.expires_at = datetime.now(timezone.utc) + timedelta(minutes=10)

    fake_payment = MagicMock()
    fake_payment.payment_status = PaymentStatusEnum.PENDING
    fake_payment.booking_id = fake_booking.id
    fake_payment.provider_order_id = "dev_order_existing"

    monkeypatch.setattr(
        payment_service.booking_repository,
        "get_booking_for_user_for_update",
        MagicMock(return_value=fake_booking),
    )

    monkeypatch.setattr(
        payment_service.payment_repository,
        "get_pending_payment_for_booking",
        MagicMock(return_value=fake_payment),
    )

    add_payment = MagicMock()
    monkeypatch.setattr(payment_service.payment_repository, "add_payment", add_payment)

    create_order = MagicMock(return_value="dev_order_backfilled")
    monkeypatch.setattr(payment_service.provider, "create_order", create_order)
    
    result, created = payment_service.create_payment_attempt(
        db=fake_db,
        booking_id=fake_booking.id,
        user_id=uuid4(),
    )


    assert result is fake_payment
    assert created is False
    create_order.assert_not_called()
    add_payment.assert_not_called()
    fake_db.commit.assert_called_once()
    fake_db.rollback.assert_not_called()

def test_create_payment_attempt_adds_missing_provider_order_id(monkeypatch):
    fake_db = MagicMock()
    fake_booking = MagicMock()
    fake_booking.id = uuid4()
    fake_booking.status = BookingStatusEnum.PENDING_PAYMENT
    fake_booking.expires_at = datetime.now(timezone.utc) + timedelta(minutes=10)

    fake_payment = MagicMock()
    fake_payment.payment_status = PaymentStatusEnum.PENDING
    fake_payment.booking_id = fake_booking.id
    fake_payment.provider_order_id = None

    monkeypatch.setattr(
        payment_service.booking_repository,
        "get_booking_for_user_for_update",
        MagicMock(return_value=fake_booking),
    )

    monkeypatch.setattr(
        payment_service.payment_repository,
        "get_pending_payment_for_booking",
        MagicMock(return_value=fake_payment),
    )

    add_payment = MagicMock()
    monkeypatch.setattr(payment_service.payment_repository, "add_payment", add_payment)

    create_order = MagicMock(return_value="dev_order_backfilled")
    monkeypatch.setattr(payment_service.provider, "create_order", create_order)
    result , created = payment_service.create_payment_attempt(
        db=fake_db,
        booking_id=fake_booking.id,
        user_id=uuid4(),
    )


    assert result is fake_payment
    assert created is False
    assert fake_payment.provider_order_id == "dev_order_backfilled"
    create_order.assert_called_once()
    add_payment.assert_not_called()
    fake_db.commit.assert_called_once()
    fake_db.rollback.assert_not_called()

def test_webhook_rejects_mismatched_amount(monkeypatch):
     
    fake_db = MagicMock()
    fake_payment = MagicMock(amount_minor=25000, currency="INR")

    monkeypatch.setattr(
        payment_service.payment_repository,
        "get_payment_by_provider_order_id",
        MagicMock(return_value=fake_payment),
    )

    complete_payment = MagicMock()
    monkeypatch.setattr(
        payment_service,
        "complete_payment",
        complete_payment
    )

    with pytest.raises(HTTPException) as exc_info:
        payment_service.complete_payment_from_webhook(
            db=fake_db,
            provider_order_id="order_test_123",
            amount_minor=20000,
            currency="INR",
            payment_status="captured"
        )

    assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST
    assert exc_info.value.detail == "Webhook payment details do not match this payment"
    complete_payment.assert_not_called()

def test_webhook_completes_matching_payment(monkeypatch):
     
    fake_db = MagicMock()
    fake_payment = MagicMock(amount_minor=25000, currency="INR",id=uuid4(), booking_id=uuid4())
    fake_booking = MagicMock(user_id=uuid4())

    monkeypatch.setattr(
        payment_service.payment_repository,
        "get_payment_by_provider_order_id",
        MagicMock(return_value=fake_payment),
    )

    monkeypatch.setattr(
        payment_service.booking_repository,
        "get_booking_by_id",
        MagicMock(return_value=fake_booking),
    )

    complete_payment = MagicMock()
    monkeypatch.setattr(
        payment_service,
        "complete_payment",
        complete_payment
    )

    payment_service.complete_payment_from_webhook(
            db=fake_db,
            provider_order_id="order_test_123",
            amount_minor=25000,
            currency="INR",
            payment_status="captured"
        )

    complete_payment.assert_called_once_with(
        fake_db,
        payment_id=fake_payment.id,
        user_id=fake_booking.user_id
    )

    


def test_complete_payment_ignores_duplicate_webhook_for_review_required_payment(
    monkeypatch,
):
    fake_db = MagicMock()
    user_id = uuid4()

    fake_booking = MagicMock(
        id=uuid4(),
        show_id=uuid4(),
        status=BookingStatusEnum.PENDING_PAYMENT,
        expires_at=datetime.now(timezone.utc) - timedelta(minutes=1),
    )
    fake_payment = MagicMock(
        id=uuid4(),
        booking_id=fake_booking.id,
        payment_status=PaymentStatusEnum.REVIEW_REQUIRED,
    )

    monkeypatch.setattr(
        payment_service.payment_repository,
        "get_payment_by_id",
        MagicMock(return_value=fake_payment),
    )
    monkeypatch.setattr(
        payment_service.booking_repository,
        "get_booking_for_user",
        MagicMock(return_value=fake_booking),
    )
    monkeypatch.setattr(
        payment_service.show_repository,
        "get_by_id_for_update",
        MagicMock(return_value=object()),
    )
    monkeypatch.setattr(
        payment_service.booking_repository,
        "get_booking_for_user_for_update",
        MagicMock(return_value=fake_booking),
    )
    monkeypatch.setattr(
        payment_service.payment_repository,
        "get_payment_by_id_for_update",
        MagicMock(return_value=fake_payment),
    )

    result = payment_service.complete_payment(
        db=fake_db,
        payment_id=fake_payment.id,
        user_id=user_id,
    )

    assert fake_payment.payment_status == PaymentStatusEnum.REVIEW_REQUIRED
    assert fake_booking.status == BookingStatusEnum.PENDING_PAYMENT
    assert result == PaymentStatusEnum.REVIEW_REQUIRED
    fake_db.commit.assert_not_called()
    fake_db.rollback.assert_called_once()

def test_complete_payment_marks_second_attempt_for_review(
    monkeypatch,
):
    fake_db = MagicMock()
    fake_booking = MagicMock()
    fake_booking.id = uuid4()
    fake_booking.show_id = uuid4()
    fake_booking.status = BookingStatusEnum.CONFIRMED
    fake_booking.expires_at = datetime.now(timezone.utc) + timedelta(minutes=10)

    fake_payment = MagicMock()
    fake_payment.payment_status = PaymentStatusEnum.PENDING
    fake_payment.booking_id = fake_booking.id

    monkeypatch.setattr(
        payment_service.payment_repository,
        "get_payment_by_id",
        MagicMock(return_value=fake_payment),
    )

    monkeypatch.setattr(
        payment_service.booking_repository,
        "get_booking_for_user_for_update",
        MagicMock(return_value=fake_booking),
    )

    monkeypatch.setattr(
        payment_service.booking_repository,
        "get_booking_for_user",
        MagicMock(return_value=fake_booking),
    )

    monkeypatch.setattr(
        payment_service.show_repository,
        "get_by_id_for_update",
        MagicMock(),
    )

    monkeypatch.setattr(
        payment_service.payment_repository,
        "get_payment_by_id_for_update",
        MagicMock(return_value=fake_payment),
    )

    result = payment_service.complete_payment(
        db=fake_db,
        payment_id=uuid4(),
        user_id=uuid4(),
    )    

    assert fake_payment.payment_status == PaymentStatusEnum.REVIEW_REQUIRED
    assert fake_booking.status == BookingStatusEnum.CONFIRMED
    assert result == PaymentStatusEnum.REVIEW_REQUIRED
    fake_db.commit.assert_called_once()
    fake_db.rollback.assert_not_called()


def test_complete_payment_marks_second_attempt_for_review(
    monkeypatch,
):
    fake_db = MagicMock()
    fake_booking = MagicMock()
    fake_booking.id = uuid4()
    fake_booking.show_id = uuid4()
    fake_booking.status = BookingStatusEnum.CONFIRMED
    fake_booking.expires_at = datetime.now(timezone.utc) + timedelta(minutes=10)

    fake_payment = MagicMock()
    fake_payment.payment_status = PaymentStatusEnum.PENDING
    fake_payment.booking_id = fake_booking.id

    monkeypatch.setattr(
        payment_service.payment_repository,
        "get_payment_by_id",
        MagicMock(return_value=fake_payment),
    )

    monkeypatch.setattr(
        payment_service.booking_repository,
        "get_booking_for_user_for_update",
        MagicMock(return_value=fake_booking),
    )

    monkeypatch.setattr(
        payment_service.booking_repository,
        "get_booking_for_user",
        MagicMock(return_value=fake_booking),
    )

    monkeypatch.setattr(
        payment_service.show_repository,
        "get_by_id_for_update",
        MagicMock(),
    )

    monkeypatch.setattr(
        payment_service.payment_repository,
        "get_payment_by_id_for_update",
        MagicMock(return_value=fake_payment),
    )

    result = payment_service.complete_payment(
        db=fake_db,
        payment_id=uuid4(),
        user_id=uuid4(),
    )    

    assert fake_payment.payment_status == PaymentStatusEnum.REVIEW_REQUIRED
    assert fake_booking.status == BookingStatusEnum.CONFIRMED
    assert result == PaymentStatusEnum.REVIEW_REQUIRED
    fake_db.commit.assert_called_once()
    fake_db.rollback.assert_not_called()
