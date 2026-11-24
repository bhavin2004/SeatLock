 # Register ORM tables before the worker runs tasks.
from celery import Celery
from app.modules.payments import provider
from app.core.config import settings
from datetime import datetime
from uuid import UUID
from app.database.session import SessionLocal
from app.modules.payments import service as payment_service
from app.modules.payments import repository as payment_repository
from app.modules.auth.models import User
from app.modules.bookings.models import Booking, BookingSeat
from app.modules.movies.models import Movie
from app.modules.payments.models import Payment
from app.modules.screens.models import Screen
from app.modules.seats.models import Seat
from app.modules.shows.models import Show
from app.modules.theaters.models import Theater

broker_url = settings.CELERY_BROKER_URL

if broker_url is None:
    raise RuntimeError("CELERY_BROKER_URL is not configured")

celery_app = Celery(
    "cinebook",
    broker=broker_url.get_secret_value(),
)

celery_app.conf.beat_schedule = {
    "scan-pending-payments-every-minute": {
        "task": "app.core.celery_app.enqueue_pending_payments",
        "schedule": 60.0,
    }
}


@celery_app.task
def add(x: int, y: int) -> int:
    return x + y

@celery_app.task
def reconcile_payment(provider_order_id: str) -> str:
    attempts = provider.list_order_payments(
        provider_order_id=provider_order_id
    )

    for attempt in attempts:
        if (
            attempt.get("status") == "captured"
            and attempt.get("order_id") == provider_order_id
        ):
            with SessionLocal() as db:
                outcome = payment_service.complete_payment_from_webhook(
                    db,
                    provider_order_id=provider_order_id,
                    amount_minor=attempt["amount"],
                    currency=attempt["currency"],
                    payment_status=attempt["status"]
                )

            return outcome.value if outcome is not None else "payment_not_found"
    return "no_capture"

@celery_app.task
def enqueue_pending_payments() -> int:

    after: tuple[datetime, UUID] | None = None
    queued = 0

    while True:
        with SessionLocal() as db:
            batch = payment_repository.list_pending_provider_order_ids(
                db, limit=50, after=after)

        if not batch:
            return queued

        for _,_, order_id in batch:
            reconcile_payment.delay(order_id)
            queued += 1

        last_created_at, last_payment_id, _ = batch[-1]
        after = (last_created_at, last_payment_id)
        