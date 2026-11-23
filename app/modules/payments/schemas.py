from uuid import UUID
from pydantic import BaseModel, ConfigDict
from datetime import datetime
from app.modules.payments.models import PaymentStatusEnum


class PaymentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    booking_id: UUID
    amount_minor: int
    currency: str
    payment_status: PaymentStatusEnum
    created_at: datetime
    provider_order_id: str | None = None


class PaymentVerifyRequest(BaseModel):
    razorpay_payment_id: str
    razorpay_order_id: str
    razorpay_signature: str