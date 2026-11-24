from datetime import datetime, timezone
from unittest.mock import MagicMock, call
from uuid import uuid4
from app.modules.payments.models import PaymentStatusEnum
from pydantic import SecretStr

from app.core.config import settings


def test_reconcile_payment_uses_matching_captured_attempt(monkeypatch):

    attempts = [
        {"order_id": "order_demo", "status": "failed"},
        {"order_id": "order_other", "status": "captured"},
        {
            "order_id": "order_demo",
            "status": "captured",
            "amount": 25000,
            "currency": "INR",
        },
    ]


    monkeypatch.setattr(
        settings, "CELERY_BROKER_URL", SecretStr("redis://localhost:6379/1")
    )

    from app.core import celery_app as worker

    monkeypatch.setattr(
        worker.provider, "list_order_payments", MagicMock(return_value=attempts),
    )

    fake_db = MagicMock()
    session_factory = MagicMock()
    session_factory.return_value.__enter__.return_value = fake_db

    monkeypatch.setattr(worker, "SessionLocal", session_factory)

    complete_payment = MagicMock(return_value=PaymentStatusEnum.COMPLETED)
    monkeypatch.setattr(
        worker.payment_service, "complete_payment_from_webhook", complete_payment
    )




    result = worker.reconcile_payment.run("order_demo")

    complete_payment.assert_called_once_with(
        fake_db,
        provider_order_id="order_demo",
        amount_minor=25000,
        currency="INR",
        payment_status="captured",
    )

    assert result == PaymentStatusEnum.COMPLETED.value

def test_reconcile_payment_skips_when_no_matching_capture(monkeypatch):

    attempts = [
        {"order_id": "order_demo", "status": "failed"},
        {"order_id": "order_other", "status": "captured"},
    ]


    monkeypatch.setattr(
        settings, "CELERY_BROKER_URL", SecretStr("redis://localhost:6379/1")
    )

    from app.core import celery_app as worker

    monkeypatch.setattr(
        worker.provider, "list_order_payments", MagicMock(return_value=attempts),
    )

    session_factory = MagicMock()

    monkeypatch.setattr(worker, "SessionLocal", session_factory)

    complete_payment = MagicMock()
    monkeypatch.setattr(
        worker.payment_service, "complete_payment_from_webhook", complete_payment
    )





    result = worker.reconcile_payment.run("order_demo")

    assert result == "no_capture"


    session_factory.assert_not_called()
    complete_payment.assert_not_called()


def test_enqueue_pending_payments_advances_cursor(monkeypatch):

    monkeypatch.setattr(
        settings, "CELERY_BROKER_URL", SecretStr("redis://localhost:6379/1")
    )

    from app.core import celery_app as worker

    fake_db = MagicMock()
    session_factory = MagicMock()
    session_factory.return_value.__enter__.return_value = fake_db

    monkeypatch.setattr(worker, "SessionLocal", session_factory)

    created_at = datetime.now(timezone.utc)
    payment_a_id = uuid4()
    payment_b_id = uuid4()

    list_batches = MagicMock(side_effect=[
        [(created_at, payment_a_id,"order_a")],
        [(created_at, payment_b_id,"order_b")],
        [],
    ])

    monkeypatch.setattr(
    worker.payment_repository,
    "list_pending_provider_order_ids",
    list_batches,
)
    enqueue = MagicMock()

    monkeypatch.setattr(worker.reconcile_payment, "delay", enqueue)


    assert worker.enqueue_pending_payments.run() == 2
    assert enqueue.call_args_list == [call("order_a"), call("order_b")]
    assert list_batches.call_args_list == [
        call(fake_db, limit=50, after=None),
        call(fake_db, limit=50, after=(created_at, payment_a_id)),
        call(fake_db, limit=50, after=(created_at, payment_b_id)),
    ]


    