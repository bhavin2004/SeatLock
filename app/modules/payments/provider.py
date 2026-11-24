import razorpay
from uuid import UUID
from app.core.config import settings
from typing import Any
import hashlib
import hmac

def create_order(*, payment_id: UUID, amount_minor: int, currency: str) -> str:
    client = _get_razorpay_client()
    order = client.order.create(
        data={
            "amount": amount_minor,
            "currency": currency,
            "receipt": payment_id.hex,
        },
    )
    return order["id"]


def _get_razorpay_client() -> Any:
    key_id = settings.RAZORPAY_KEY_ID
    key_secret = settings.RAZORPAY_KEY_SECRET

    if not key_id or key_secret is None:
        raise RuntimeError("Razorpay API keys are not configured")

    return razorpay.Client(auth=(key_id, key_secret.get_secret_value()))

def verify_payment_signature(
        *, 
        razorpay_payment_id: str, 
        provider_order_id: str,
        razorpay_signature: str
) -> None:
    client = _get_razorpay_client()
    client.utility.verify_payment_signature({
        "razorpay_payment_id": razorpay_payment_id,
        "razorpay_order_id": provider_order_id,
        "razorpay_signature": razorpay_signature
    })

def fetch_payment(*, razorpay_payment_id: str) -> dict:
    client = _get_razorpay_client()
    return client.payment.fetch(razorpay_payment_id)


def verify_webhook_signature(*, raw_body: bytes, signature: str) -> bool:
    secret = settings.RAZORPAY_WEBHOOK_SECRET
    if secret is None:
        raise RuntimeError("Razorpay webhook secret is not configured")

    expected = hmac.new(
        secret.get_secret_value().encode("utf-8"),
        raw_body,
        hashlib.sha256
    ).hexdigest()

    return hmac.compare_digest(expected, signature)

def list_order_payments(*, provider_order_id: str) -> list[dict]:
    client = _get_razorpay_client()
    payments = client.order.payments(provider_order_id)
    return payments["items"]