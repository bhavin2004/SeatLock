import hashlib
import hmac
from app.modules.payments import provider

from pydantic import SecretStr


def test_verify_webhook_signature_rejects_modified_body(monkeypatch):

    monkeypatch.setattr(
        "app.modules.payments.provider.settings.RAZORPAY_WEBHOOK_SECRET",
        SecretStr("test_webhook_secret")
    )

    raw_body = b'{"amount":25000}'

    modified_body = b'{"amount":50000}'

    signature = hmac.new(
        b"test_webhook_secret",
        raw_body,
        hashlib.sha256
    ).hexdigest()


    assert provider.verify_webhook_signature(raw_body=raw_body, signature=signature)
    assert not provider.verify_webhook_signature(raw_body=modified_body, signature=signature)


