import json
from app.modules.payments import service
from fastapi import Request, HTTPException, status, Depends
from fastapi.concurrency import run_in_threadpool
from sqlalchemy.orm import Session
from app.database.dependencies import get_db
from app.modules.payments import provider
from fastapi import APIRouter

router = APIRouter(
    prefix="/webhooks",
    tags=["Webhooks"],
)


@router.post("/razorpay",status_code=status.HTTP_204_NO_CONTENT)
async def razorpay_webhook(request: Request, db: Session = Depends(get_db)) -> None:
    raw_body = await request.body()
    signature = request.headers.get("X-Razorpay-Signature")

    if not signature or not provider.verify_webhook_signature(raw_body=raw_body, signature=signature):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid webhook signature"
        )

    try:
        event = json.loads(raw_body)

    except (json.JSONDecodeError, UnicodeDecodeError) as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid webhook JSON"
        ) from exc

    if not isinstance(event, dict):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Webhook body must be a JSON object",
        )

    if event.get("event") != "payment.captured":
        return

    try:
        payment_entity = event["payload"]["payment"]["entity"]
        provider_order_id = payment_entity["order_id"]
        amount = payment_entity["amount"]
        currency = payment_entity["currency"]
        payment_status = payment_entity["status"]

    except (KeyError, TypeError) as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid payment webhook payload",
            ) from exc

    if not isinstance(provider_order_id, str) or not provider_order_id.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Missing Razorpay order ID"
        )
    if (
        type(amount) is not int
        or amount <= 0
        or not isinstance(currency, str)
        or not currency.strip()
        or not isinstance(payment_status, str)
        or not payment_status.strip()
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid payment webhook fields",
        )
        
    await run_in_threadpool(
        service.complete_payment_from_webhook,
        db,
        provider_order_id=provider_order_id,
        amount_minor=amount,
        currency=currency,
        payment_status=payment_status,
    )