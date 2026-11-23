
from app.modules.bookings import service as booking_service
from app.modules.bookings.models import BookingStatusEnum
import pytest
from fastapi import HTTPException, status

from datetime import datetime, timedelta, timezone
from unittest.mock import MagicMock
from uuid import uuid4


def test_cancelled_booking_cannot_be_confirmed(monkeypatch):

    fake_db = MagicMock()

    fake_booking = MagicMock()
    fake_booking.status = BookingStatusEnum.CANCELLED
    fake_booking.expires_at = datetime.now(timezone.utc) + timedelta(minutes=10)

    monkeypatch.setattr(
        booking_service.booking_repository,
        "get_booking_for_user",
        MagicMock(return_value=fake_booking),
    )
    monkeypatch.setattr(
        booking_service.booking_repository,
        "get_booking_for_user_for_update",
        MagicMock(return_value=fake_booking),
    )

    fake_booking.show_id = uuid4()

    monkeypatch.setattr(
        booking_service.show_repository,
        "get_by_id_for_update",
        MagicMock(),
    )

    with pytest.raises(HTTPException) as exc_info:
        booking_service.confirm_booking(
            fake_db,
            booking_id=uuid4(),
            user_id=uuid4(),
        )

    assert exc_info.value.status_code == status.HTTP_409_CONFLICT
    assert fake_booking.status == BookingStatusEnum.CANCELLED
    fake_db.commit.assert_not_called()
    fake_db.rollback.assert_called_once()

def test_active_booking_can_be_confirmed(monkeypatch):

    fake_db = MagicMock()

    fake_booking = MagicMock()
    fake_booking.status = BookingStatusEnum.PENDING_PAYMENT
    fake_booking.expires_at = datetime.now(timezone.utc) + timedelta(minutes=10)

    monkeypatch.setattr(
        booking_service.booking_repository,
        "get_booking_for_user",
        MagicMock(return_value=fake_booking),
    )
    monkeypatch.setattr(
        booking_service.booking_repository,
        "get_booking_for_user_for_update",
        MagicMock(return_value=fake_booking),
    )

    fake_booking.show_id = uuid4()

    monkeypatch.setattr(
        booking_service.show_repository,
        "get_by_id_for_update",
        MagicMock(),
    )

    booking_service.confirm_booking(
        fake_db,
        booking_id=uuid4(),
        user_id=uuid4(),
    )

    assert fake_booking.status == BookingStatusEnum.CONFIRMED
    fake_db.commit.assert_called_once()
    fake_db.rollback.assert_not_called()


def test_expired_booking_cannot_be_confirmed(monkeypatch):
    fake_db = MagicMock()

    fake_booking = MagicMock()
    fake_booking.status = BookingStatusEnum.PENDING_PAYMENT
    fake_booking.expires_at = datetime.now(timezone.utc) - timedelta(minutes=10)

    monkeypatch.setattr(
        booking_service.booking_repository,
        "get_booking_for_user",
        MagicMock(return_value=fake_booking),
    )
    monkeypatch.setattr(
        booking_service.booking_repository,
        "get_booking_for_user_for_update",
        MagicMock(return_value=fake_booking),
    )

    fake_booking.show_id = uuid4()

    monkeypatch.setattr(
        booking_service.show_repository,
        "get_by_id_for_update",
        MagicMock(),
    )

    with pytest.raises(HTTPException) as exc_info:
        booking_service.confirm_booking(
            fake_db,
            booking_id=uuid4(),
            user_id=uuid4(),
        )

    assert exc_info.value.status_code == status.HTTP_409_CONFLICT
    assert fake_booking.status == BookingStatusEnum.PENDING_PAYMENT
    fake_db.commit.assert_not_called()
    fake_db.rollback.assert_called_once()


def test_missing_booking_cannot_be_confirmed(monkeypatch):
    fake_db = MagicMock()

    monkeypatch.setattr(
        booking_service.booking_repository,
        "get_booking_for_user",
        MagicMock(return_value=None),
    )

    show_lock = MagicMock()
    monkeypatch.setattr(
        booking_service.show_repository,
        "get_by_id_for_update",
        show_lock,
    )

    with pytest.raises(HTTPException) as exc_info:
        booking_service.confirm_booking(
            fake_db,
            booking_id=uuid4(),
            user_id=uuid4(),
        )

    assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND
    fake_db.commit.assert_not_called()
    fake_db.rollback.assert_called_once()
    show_lock.assert_not_called()