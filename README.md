# CineBook / SeatLock

CineBook (also called SeatLock in the current workspace) is a FastAPI backend for a movie-ticket booking service. It is being built as a learning project, with production engineering practices as a goal.

## Current implementation

- User registration, login, and current-user profile endpoints.
- Argon2 password hashing and JWT access-token authentication.
- CUSTOMER and ADMIN roles; movie changes require ADMIN access.
- Movie creation, listing, detail, update, publish, and archive endpoints.
- Public movie reads return published movies only.
- Admin APIs for theaters, screens, seats, and shows, plus public upcoming shows and seat availability.
- Authenticated bookings with expiring seat holds, cancellation, and PostgreSQL row locking to prevent double booking.
- Razorpay Test Mode checkout, payment verification, and signed webhook handling. Captured payments that cannot confirm a booking are marked for review.
- Redis login rate limiting by IP and email and scheduled payment reconciliation with Celery.
- SQLAlchemy models and Alembic migrations for the booking and payment flow.

## Requirements

- Python 3.11 or newer.
- [uv](https://docs.astral.sh/uv/) for dependency and environment management.
- A PostgreSQL database for running migrations and using the API.

## Local setup

From the project root, install the project and development dependencies:

```powershell
uv sync --dev
```

Create a local environment file from the example:

```powershell
Copy-Item .env.example .env
```

Edit `.env` and set `DATABASE_URL` to the PostgreSQL database you intend to use. Replace the JWT secret placeholder with a randomly generated secret. Keep `.env` private; it is ignored by Git.

The example configuration includes:

| Variable | Purpose |
| --- | --- |
| `DATABASE_URL` | SQLAlchemy connection URL for PostgreSQL. |
| `APP_NAME` | Application name shown by FastAPI. |
| `APP_ENV` | Environment label, such as `development`. |
| `DEBUG` | Enables or disables FastAPI debug mode. Keep this `false` outside local development. |
| `JWT_SECRET_KEY` | Secret used to sign access tokens. Use a unique, random value and do not commit it. |
| `JWT_ALGORITHM` | JWT signing algorithm; the current example uses `HS256`. |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Access-token lifetime in minutes. |

## Database migrations

Apply the Alembic migrations to the database selected by `DATABASE_URL`:

```powershell
uv run alembic upgrade head
```

This changes the target database schema. Confirm that `.env` points to the intended development database before running it. Do not use a production database for local development or tests.

## Run the API

Start the local development server:

```powershell
uv run uvicorn app.main:app --reload
```

Useful local endpoints:

- API health: `http://127.0.0.1:8000/api/v1/health`
- Interactive API documentation: `http://127.0.0.1:8000/docs`

The API currently uses the `/api/v1` prefix. Movie and authentication routes are listed in the interactive API documentation.

## Run tests

Run the tests that do not require a live PostgreSQL connection:

```powershell
uv run python -m pytest --ignore=tests/test_booking_concurrency.py -v
```

The API tests use dependency overrides and mocks for database-backed movie operations.

### PostgreSQL concurrency test

Set `TEST_DATABASE_URL` in your local `.env` to a dedicated PostgreSQL database named `cinebook_test`. Keep `DATABASE_URL` pointed at your development database. From the project root, apply the Alembic migrations to the test database using this process-local override:

```powershell
@'
from alembic import command
from alembic.config import Config
from sqlalchemy.engine import make_url

from app.core.config import settings

if settings.TEST_DATABASE_URL is None:
    raise SystemExit("Set TEST_DATABASE_URL first")

test_url = settings.TEST_DATABASE_URL.get_secret_value()
target = make_url(test_url)
if (
    target.get_backend_name() != "postgresql"
    or target.database != "cinebook_test"
    or target.database == make_url(settings.DATABASE_URL).database
):
    raise SystemExit("Expected a separate PostgreSQL database named cinebook_test")

settings.DATABASE_URL = test_url
command.upgrade(Config("alembic.ini"), "head")
'@ | uv run python -
```

Run the concurrency test:

```powershell
uv run python -m pytest tests/test_booking_concurrency.py -v
```

Two customers attempt to hold the same seat for the same show using separate database sessions. The show row lock keeps the availability check and booking write in one transaction. The test checks that one booking succeeds, the other raises `409 Conflict`, and exactly one booking-seat row is committed. The test deletes the records created during that run.

## Razorpay Test Mode demo

Use a development database and set `APP_ENV=development`, `RAZORPAY_KEY_ID`, and `RAZORPAY_KEY_SECRET` in your local `.env`. Use a Razorpay Test Mode key pair. Keep the key secret in `.env`.

1. In Swagger, sign in as an admin and set up a published movie, a theater with a screen and a seat, and a future show. Sign in as a customer to run the booking flow.
2. Find an available seat with `GET /api/v1/shows/{show_id}/seats`, then hold it with `POST /api/v1/bookings` by passing `show_id` and `seat_ids`.
3. Call `POST /api/v1/bookings/{booking_id}/payments` while the hold is active. In `razorpay-test.html`, set `key` to the Test Key ID, set `order_id` to the returned `provider_order_id`, and set the `/verify` URL using the returned `booking_id` and payment `id`.
4. Open the [local checkout page](http://127.0.0.1:8000/dev/checkout), click **Pay**, and complete the Test Mode payment. When prompted, paste the booking owner's access token. The page should display **Booking confirmed**. Confirm `confirmed` through `GET /api/v1/bookings/{booking_id}` and `completed` through `GET /api/v1/bookings/{booking_id}/payments/{payment_id}`.

To demo failure and retry, start with a fresh hold and order. In Test Mode Netbanking, choose **Failure** on the mock bank page. Razorpay records a failed attempt and CineBook keeps the booking at `pending_payment` and the local payment at `pending`. Retry on the same order while the hold is active. After successful verification, the payment becomes `completed` and the booking becomes `confirmed`.

## Redis login rate limiting

Start Redis with Docker Desktop and confirm it responds:

```powershell
docker network create cinebook-net
docker run -d --name cinebook-redis --network cinebook-net -p 127.0.0.1:6379:6379 redis:7-alpine
docker exec cinebook-redis redis-cli PING
```

If the Redis container already exists, start it with `docker start cinebook-redis` and make sure it is connected to `cinebook-net`.

Add `REDIS_URL=redis://127.0.0.1:6379/0` to your local `.env`, then restart the API. Each IP gets five login requests per 60-second window. Each normalized email gets ten requests that pass the IP check in its own 60-second window. A blocked request receives `429 Too Many Requests` and a `Retry-After` header. The email counter follows the account identifier across IP changes.

To demo the IP limit, send six login requests with invalid credentials from a fresh IP counter within one minute. The first five return `401`; the sixth returns `429`. The unit tests also check the email limit without requiring Redis.

## Celery payment reconciliation demo

Set `CELERY_BROKER_URL=redis://127.0.0.1:6379/1` in your local `.env`. Use a development database and the same Razorpay Test Mode keys as the API. Build and start the worker and a single Beat scheduler from the project root:

```powershell
docker build -f Dockerfile.worker -t cinebook-worker .

docker run -d --rm --name cinebook-worker --network cinebook-net `
  --env-file .env `
  -e "CELERY_BROKER_URL=redis://cinebook-redis:6379/1" cinebook-worker

docker run -d --rm --name cinebook-beat --network cinebook-net `
  --env-file .env `
  -e "CELERY_BROKER_URL=redis://cinebook-redis:6379/1" cinebook-worker `
  /app/.venv/bin/celery -A app.core.celery_app:celery_app beat `
  --loglevel=INFO --schedule=/tmp/celerybeat-schedule
```

Beat sends a scan task every 60 seconds. The worker reads pending orders in batches and queues a reconciliation task for each order. Each task looks for a matching captured payment in Razorpay and uses the existing payment completion flow.

1. Create a fresh seat hold and Razorpay test order using the checkout demo above.
2. Complete the test payment, then cancel the CineBook token prompt so the browser skips verification. Use a local setup where the Razorpay webhook cannot reach CineBook so Beat is the only confirmation path.
3. Check `docker logs --tail 30 cinebook-worker` after the next scan. While the hold is active, expect `completed`, then confirm the booking is `confirmed` and the payment is `completed` using the GET endpoints in the checkout demo. If the hold has expired by the time the worker processes the capture, expect `review_required` and no new booking confirmation. `no_capture` means the worker did not find a matching captured payment.

Stop scheduled scans when the demo is finished with `docker stop cinebook-beat cinebook-worker`.

## Project status

Latest full test run: **44 passed in 9.77 seconds**, including the PostgreSQL concurrency test.

The Razorpay Test Mode success and failure/retry flows were verified against the API. The same-seat PostgreSQL concurrency test also passed. Use [`PRODUCTION_CHECKLIST.md`](PRODUCTION_CHECKLIST.md) to track launch work such as reconciliation, staging, monitoring, and backups.
