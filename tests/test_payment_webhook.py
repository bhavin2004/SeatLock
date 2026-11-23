import asyncio
import hashlib
import hmac
import json
from unittest.mock import AsyncMock, MagicMock

from fastapi import HTTPException
import pytest
from app.modules.payments import router as webhook_router
from pydantic import SecretStr


def test_captured_webhook_calls_payment_service(monkeypatch):
    event = {
        "event": "payment.captured",
        "payload": {
            "payment": {
                "entity": {
                    "order_id": "order_test_123",
                    "amount": 25000,
                    "currency": "INR",
                    "status": "captured",
                }
            }
        },
    }

    secret = "test_webhook_secret"
    monkeypatch.setattr(
        "app.modules.payments.provider.settings.RAZORPAY_WEBHOOK_SECRET",
        SecretStr(secret)
    )

    raw_body = json.dumps(event).encode("utf-8")
    signature = hmac.new(
        secret.encode("utf-8"),
        raw_body,
        hashlib.sha256
    ).hexdigest()

    request = MagicMock()
    request.body = AsyncMock(return_value=raw_body)
    request.headers = {"X-Razorpay-Signature": signature}
    fake_db = MagicMock()

    complete_payment = MagicMock()

    monkeypatch.setattr(
        webhook_router.service,
        "complete_payment_from_webhook",
        complete_payment
    )

    asyncio.run(webhook_router.razorpay_webhook(request, db=fake_db))

    complete_payment.assert_called_once_with(
        fake_db,
        provider_order_id="order_test_123",
        amount_minor=25000,
        currency="INR",
        payment_status="captured"
    )




def test_webhook_rejects_invalid_signature(monkeypatch):
    event = {
            "event": "payment.captured",
            "payload": {
                "payment": {
                    "entity": {
                        "order_id": "order_test_123",
                        "amount": 25000,
                        "currency": "INR",
                        "status": "captured",
                    }
                }
            },
        }
    
    secret = "test_webhook_secret"
    monkeypatch.setattr(
        "app.modules.payments.provider.settings.RAZORPAY_WEBHOOK_SECRET",
        SecretStr(secret)
    )

    raw_body = json.dumps(event).encode("utf-8")
    

    request = MagicMock()
    request.body = AsyncMock(return_value=raw_body)
    request.headers = {"X-Razorpay-Signature":  "invalid-signature"}
    fake_db = MagicMock()

    complete_payment = MagicMock()

    monkeypatch.setattr(
        webhook_router.service,
        "complete_payment_from_webhook",
        complete_payment
    )

    with pytest.raises(HTTPException) as exc_info:
        asyncio.run(webhook_router.razorpay_webhook(request, db=fake_db))

    assert exc_info.value.status_code == 400
    complete_payment.assert_not_called()


def test_captured_webhook_rejects_missing_order_id(monkeypatch):
    event = {
        "event": "payment.captured",
        "payload": {
            "payment": {
                "entity": {
                    "amount": 25000,
                    "currency": "INR",
                    "status": "captured",
                }
            }
        },
    }

    secret = "test_webhook_secret"
    monkeypatch.setattr(
        "app.modules.payments.provider.settings.RAZORPAY_WEBHOOK_SECRET",
        SecretStr(secret)
    )

    raw_body = json.dumps(event).encode("utf-8")
    signature = hmac.new(
        secret.encode("utf-8"),
        raw_body,
        hashlib.sha256
    ).hexdigest()

    request = MagicMock()
    request.body = AsyncMock(return_value=raw_body)
    request.headers = {"X-Razorpay-Signature": signature}
    fake_db = MagicMock()

    complete_payment = MagicMock()

    monkeypatch.setattr(
        webhook_router.service,
        "complete_payment_from_webhook",
        complete_payment
    )

    with pytest.raises(HTTPException) as exc_info:
        asyncio.run(webhook_router.razorpay_webhook(request, db=fake_db))

    assert exc_info.value.status_code == 400
    assert exc_info.value.detail == "Invalid payment webhook payload"
    complete_payment.assert_not_called()

