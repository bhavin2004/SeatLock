# CineBook / SeatLock Production Readiness Checklist

**Last updated:** 21 November 2026  
**Purpose:** Track the work from the current learning project to a reliable movie-ticket booking service. A checked item means the capability exists and has evidence; it does not by itself mean the whole system is production-ready.

## Current progress

- [x] FastAPI application with `/api/v1` routing and a health endpoint.
- [x] SQLAlchemy and Alembic foundations, with `User` and `Movie` models and initial migrations.
- [x] Registration, login, current-user endpoint, Argon2 password hashing, JWT access tokens, and CUSTOMER/ADMIN authorization.
- [x] Movie create, list, detail, update, publish, and archive endpoints.
- [x] Public movie reads are limited to published movies; admin-only movie changes are protected.
- [x] API/security tests cover the current health, JWT, authorization, and movie-list pagination behavior.
- [x] Last reported full test run: **23 passed** on 21 November 2026. The API tests use dependency overrides and service mocks, not Neon writes.

## 1. Project setup and configuration

- [x] Document local setup, environment variables, migrations, running the server, and tests in `README.md`.
- [x] Complete `.env.example` with every required setting, including `JWT_ALGORITHM` and `ACCESS_TOKEN_EXPIRE_MINUTES`.
- [ ] Validate configuration at startup: strong production JWT secret, supported algorithm, positive token lifetime, and safe production debug settings.
  - [x] Require `ACCESS_TOKEN_EXPIRE_MINUTES` to be greater than zero; the focused config tests passed (3 tests, 21 November 2026).
  - [ ] Restrict `JWT_ALGORITHM` to a supported value (deferred).
  - [ ] Reject short JWT secrets in production (implemented; tests pending).
  - [ ] Prevent `DEBUG=true` in production (implemented; tests pending).
- [x] Decide and document the supported Python version and one reproducible install/test workflow in `README.md`.

## 2. Database and test safety

- [ ] Create a dedicated PostgreSQL test database or local disposable PostgreSQL service; never point automated tests at Neon development data.
- [ ] Add repository and transaction tests against PostgreSQL for uniqueness, constraints, rollback behavior, and query results.
- [ ] Verify a fresh Alembic upgrade creates the expected schema and test downgrade/upgrade behavior where safe.
- [ ] Add a CI check that model metadata and migrations do not drift.
- [ ] Document how developers create, migrate, seed, and reset each environment without risking production data.

## 3. Authentication and account security

- [ ] Add isolated API tests for registration, duplicate email, login success/failure, disabled accounts, and `/auth/me`.
- [ ] Define a safe ADMIN provisioning process that does not require manual production SQL edits.
- [ ] Add rate limits and abuse protection for registration and login.
- [ ] Define password reset and account recovery flows.
- [ ] Decide whether refresh tokens, logout/revocation, and multiple-device session management are required; implement and test the chosen behavior.
- [ ] Review token claims, expiration, key rotation, secret storage, and authorization behavior before deployment.

## 4. Movie catalog quality

- [ ] Add tests for invalid upper pagination bounds, published-only list/detail behavior, and missing movie IDs.
- [ ] Add tests for update null/empty input handling and publish/archive state conflicts.
- [ ] Decide whether archived movies can be edited or republished and enforce the policy consistently.
- [ ] Add catalog search/filter/sort only when product requirements define the supported fields and ordering.

## 5. Theater, screen, seat, and show catalog

- [ ] Add Theater and Screen models, schemas, repositories, services, migrations, and admin APIs.
  - [x] Define the Theater ORM model and import it into Alembic metadata.
  - [x] Generate and review the Theater migration.
  - [x] Apply the Theater migration to the intended development database (user-reported complete).
  - [x] Define the Screen ORM model with a Theater foreign key and per-theater unique name.
  - [x] Generate and review the Screen migration.
  - [x] Apply the Screen migration to the intended development database (user-reported complete).
  - [x] Define the Seat ORM model with a Screen foreign key, seat type, positive number, and per-screen position uniqueness.
  - [x] Generate and review the Seat migration.
  - [ ] Apply the Seat migration to the intended development database.
- [ ] Add Seat layouts and seat types tied to a Screen; enforce unique seat identifiers within a screen.
- [ ] Add Show models linking a Movie, Screen, show time, and price rules; keep show time on the Show.
- [ ] Validate show scheduling, time zones, screen conflicts, and movie availability.
- [ ] Add public APIs to browse theaters, screens/seats, and showtimes, with pagination and appropriate indexes.
- [ ] Add isolated PostgreSQL tests for relationships, uniqueness, and scheduling constraints.

## 6. Booking and seat reservation

- [ ] Define booking states and support group bookings with multiple seats.
- [ ] Store seat occupancy per show and booking; do not rely on a permanent `is_booked` flag on Seat.
- [ ] Implement temporary seat holds with expiration and safe release of expired holds.
- [ ] Extend holds during an active payment attempt according to the chosen timeout policy.
- [ ] Prevent two customers from reserving the same `(show_id, seat_id)` using PostgreSQL constraints and transaction-safe locking/version checks.
- [ ] Make booking creation and seat reservation atomic so partial failures do not strand seats.
- [ ] Add idempotency for booking requests and clear behavior for retries, cancellation, and hold expiration.
- [ ] Add PostgreSQL integration and concurrency tests for competing customers, expired holds, payment delays, and rollback.

## 7. Payments and booking completion

- [ ] Add a separate Payment record with amount/currency snapshots, provider reference, status, attempts, and timestamps.
- [ ] Define payment success, failure, retry, timeout, cancellation, and refund state transitions.
- [ ] Verify provider webhooks, signatures, idempotency, and replay handling.
- [ ] Ensure payment callbacks cannot confirm a booking whose hold expired or whose seats were reassigned.
- [ ] Add sandbox-provider integration tests and reconciliation for uncertain or delayed payment outcomes.
- [ ] Never store raw card data; use a payment provider’s tokenized/hosted payment flow.

## 8. Production operations and security

- [ ] Add automated CI for dependency sync, tests, linting, and migration checks.
- [ ] Separate development, staging, and production configuration and credentials.
- [ ] Deploy behind HTTPS with restricted database/network access and least-privilege credentials.
- [ ] Add structured logs with request IDs; exclude passwords, tokens, payment data, and unnecessary personal data.
- [ ] Add readiness checks for database/dependencies, health monitoring, metrics, error reporting, and actionable alerts.
- [ ] Configure database connection limits, timeouts, pool behavior, and graceful shutdown for the chosen host/load.
- [ ] Set up automated database backups and perform a restore drill.
- [ ] Add API rate limits, request-size limits, CORS policy if browser clients need it, and security-header policy at the appropriate layer.
- [ ] Establish deployment/migration rollback steps, incident contacts, and a short operations runbook.
- [ ] Load-test browsing and concurrent booking paths; fix measured bottlenecks before launch.
- [ ] Complete a security review of authentication, authorization, input validation, dependencies, secrets, and payment integration.

## 9. Launch gate

- [ ] All CI checks pass from a clean checkout.
- [ ] Staging deployment, migrations, booking flow, payment sandbox flow, and rollback have been exercised.
- [ ] Production secrets, backups, alerts, support process, and incident runbook are verified.
- [ ] No automated test or staging workflow can write to production or the Neon development database.
- [ ] Product owner signs off on booking, cancellation, refund, seat-hold, and payment policies.
