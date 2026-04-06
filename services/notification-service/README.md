# notification-service

Microservice responsible for all student-facing notifications in the GradGown Rental platform.

Consumes events from Kafka and dispatches SMS (Twilio) and email (SendGrid) via an Anti-Corruption Layer that shields internal logic from third-party SDK changes.

---

## Table of Contents

- [Responsibilities](#responsibilities)
- [Architecture](#architecture)
- [Project Structure](#project-structure)
- [Environment Variables](#environment-variables)
- [pyproject.toml — What It Does](#pyprojecttoml--what-it-does)
- [Running with Docker Compose](#running-with-docker-compose)
- [Testing the Service](#testing-the-service)
- [Kafka Events Reference](#kafka-events-reference)
- [API Endpoints](#api-endpoints)
- [Database Schema](#database-schema)

---

## Responsibilities

Covers two notification scenarios from the spec:

**Scenario 2a — Scheduled Reminders** (triggered by Order Service scheduled job)
- `pickup_reminder` → SMS + email reminder 24 hours before collection/delivery
- `return_reminder` → SMS + email reminder 24 hours before return due date

**Scenario 2b — Post-Action Notifications** (event-driven via Kafka)
- `OrderConfirmed` → "Order Receipt" email + "Order Confirmed" SMS
- `OrderActivated` → "Gown Care & Return Instructions" email + "Collection Complete" SMS
- `ReturnProcessed` → "Refund Receipt" email + "Return Complete" SMS

---

## Architecture

```
Kafka Topics
    │
    ├── OrderConfirmed  ──┐
    ├── OrderActivated  ──┤
    ├── ReturnProcessed ──┼──► NotificationConsumer
    ├── pickup_reminder ──┤         │
    └── return_reminder ──┘         ▼
                               NotificationService
                              /                   \
                    TwilioAdapter            SendGridAdapter
                   (Anti-Corruption)        (Anti-Corruption)
                          │                        │
                     Twilio API              SendGrid API
                     (SMS)                   (Email)
                          \                        /
                           NotificationRepository
                                    │
                               PostgreSQL
                           (notification_logs)
```

The service has **no synchronous dependencies on other microservices** — it only reads from Kafka. If it goes down, Kafka retains all messages and replays them on restart (`auto_offset_reset="earliest"`), guaranteeing no student ever misses a notification.

---

## Project Structure

```
notification-service/
├── Dockerfile
├── requirements.txt
├── pyproject.toml
├── db/
│   └── init.sql                    ← creates notification_logs table on first boot
└── src/
    ├── app.py                      ← Flask factory; wires everything together
    ├── model/
    │   └── notification_log.py     ← NotificationLog dataclass + enums
    ├── repository/
    │   └── notification_repository.py  ← all SQL isolated here
    ├── service/
    │   └── notification_service.py ← core logic; composes adapters + repo
    ├── adapters/
    │   ├── twilio_adapter.py       ← Anti-Corruption Layer for Twilio SMS
    │   └── sendgrid_adapter.py     ← Anti-Corruption Layer for SendGrid email
    ├── consumer/
    │   └── notification_consumer.py ← Kafka consumer (background daemon thread)
    └── controller/
        └── notification_controller.py  ← Flask blueprint: /health, /notifications/<order_id>
```

**Why this layering?**

| Layer | Responsibility |
|---|---|
| `model/` | Pure data — no logic, no I/O |
| `repository/` | All SQL in one place — swap DB engine without touching service logic |
| `service/` | Business logic — knows nothing about HTTP or Kafka |
| `adapters/` | Third-party isolation — Twilio/SendGrid API changes never leak inward |
| `consumer/` | Kafka wiring — routes topic events to service methods |
| `controller/` | HTTP wiring — thin, no business logic |

---

## Environment Variables

Add these to your `.env` file at the project root (copy from `.env.example`):

```env
# PostgreSQL — notification-service database
DB_HOST=notification-service-db
DB_PORT=5432
DB_NAME=notification
DB_USER=notification_user
DB_PASSWORD=notification_pass

# Kafka
KAFKA_BOOTSTRAP_SERVERS=kafka:29092

# Twilio (SMS)
TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
TWILIO_AUTH_TOKEN=your_auth_token_here
TWILIO_FROM_NUMBER=+1234567890

# SendGrid (email)
SENDGRID_API_KEY=SG.xxxxxxxxxxxxxxxxxxxxxxxx
SENDGRID_FROM_EMAIL=noreply@yourdomain.com
```

> **Where to get credentials**
> - Twilio: https://console.twilio.com → Account Info panel
> - SendGrid: https://app.sendgrid.com → Settings → API Keys

---

## pyproject.toml — What It Does

```toml
[project]
name = "notification-service"
version = "0.1.0"
requires-python = ">=3.13"
dependencies = []           # ← needs to be filled in (see below)
```

`pyproject.toml` is the **modern Python project manifest**. It tells `uv` (the package manager this repo uses) what the service is and what it depends on.

The repo root `pyproject.toml` declares a **uv workspace** with all services as members. This means running `uv sync` from the project root installs dependencies for every service in one shot.

**The `dependencies = []` field is currently empty — you need to fill it in:**

```toml
[project]
name = "notification-service"
version = "0.1.0"
description = "Kafka-driven notification microservice for GradGown Rental"
readme = "README.md"
requires-python = ">=3.13"
dependencies = [
    "flask>=3.1.3",
    "flask-cors>=6.0.2",
    "gunicorn>=25.1.0",
    "psycopg2-binary>=2.9.9",
    "kafka-python>=2.3.0",
    "twilio>=9.0.0",
    "sendgrid>=6.11.0",
    "requests>=2.32.0",
]
```

Once filled in, the `Dockerfile` can use `uv` instead of `pip` to stay consistent with the rest of the repo. 

---

## Running with Docker Compose

### 1. Fill in your `.env`

```bash
cp .env.example .env
# then edit .env and add the Twilio + SendGrid credentials above
```

### 2. Add the service blocks to `docker-compose.yml`

Paste the contents of `docker-compose.additions.yml` into your existing `docker-compose.yml`:
- Add the `notification-service` and `notification-service-db` service blocks under `services:`
- Add `notification-data:` under the top-level `volumes:` block

### 3. Start only the notification-service stack

To spin up just the notification-service and its dependencies (Kafka + Postgres) without starting every other service:

```bash
docker compose up --build notification-service notification-service-db kafka
```

To run it in the background:

```bash
docker compose up --build -d notification-service notification-service-db kafka
```

### 4. Start the full stack

```bash
docker compose up --build
```

### 5. Check it's running

```bash
# Health check
curl http://localhost:5001/health

# Expected response:
# {"service": "notification-service", "status": "ok"}
```

### 6. View logs

```bash
docker compose logs -f notification-service
```

---

## Testing the Service

Since the notification-service is purely event-driven, testing means publishing a fake Kafka message and checking that the right SMS/email is sent (or that the log table is written to if you're not ready to hit real Twilio/SendGrid).

### Option A — Publish a test Kafka event manually

Use the Kafka CLI inside the running container:

```bash
# Open a shell on the Kafka container
docker exec -it kafka bash

# Publish a fake OrderConfirmed event
/opt/kafka/bin/kafka-console-producer.sh \
  --bootstrap-server localhost:9092 \
  --topic OrderConfirmed
```

Then paste this JSON and press Enter:

```json
{"order_id": "TEST-001", "student_name": "Jia Qian", "phone": "+6588756213", "email": "wanjiaqian613@gmail.com", "fulfillment_method": "COLLECTION", "fulfillment_date": "2025-11-10", "return_date": "2025-11-14", "total_amount": "125.00"}
```

Then check the notification logs:

```bash
curl http://localhost:5001/notifications/TEST-001
```

Expected response — two log entries (one SMS, one EMAIL), both with `"status": "SENT"`.

### Option B — Publish both DEPOSIT outcomes quickly (full refund + damage deduction)

Use the helper script in this repo:

```bash
cd services/notification-service
python src/scripts/publish_return_processed_test_events.py \
  --email eichawzin123@gmail.com \
  --phone +6581234567
```

The script publishes **two** `ReturnProcessed` events:
- full-refund case (`has_damage=false`)
- damage-deduction case (`has_damage=true`)

Then verify each generated order id via:

```bash
curl http://localhost:5001/notifications/<GENERATED_ORDER_ID>
```

### Option B — Query the database directly

```bash
# Open a psql shell on the notification database
docker exec -it notification-service-db psql -U notification_user -d notification

# Check what's been logged
SELECT id, order_id, event_type, channel, status, external_id, created_at
FROM notification_logs
ORDER BY created_at DESC
LIMIT 20;
```

### Checking the consumer is connected to Kafka

```bash
docker compose logs notification-service | grep "NotificationConsumer started"
# Should show: NotificationConsumer started | topics=[...]

# Or list all consumer groups from Kafka
docker exec -it kafka /opt/kafka/bin/kafka-consumer-groups.sh \
  --bootstrap-server localhost:9092 \
  --list
# Should show: notification-service-group
```

---

## Kafka Events Reference

All events are JSON, published by upstream services. The notification-service consumes these topics:

### `OrderConfirmed` (published by Place an Order Saga)
```json
{
  "order_id": "ORD-001",
  "student_name": "Jia Qian",
  "phone": "+6588756213",
  "email": "wanjiaqian613@gmail.com",
  "fulfillment_method": "COLLECTION",
  "fulfillment_date": "2025-11-10",
  "return_date": "2025-11-14",
  "total_amount": "125.00"
}
```
→ Sends: Order Receipt email + Order Confirmed SMS

### `OrderActivated` (published by Fulfill an Order Saga)
```json
{
  "order_id": "ORD-001",
  "student_name": "Jia Qian",
  "phone": "+6588756213",
  "email": "wanjiaqian613@gmail.com",
  "return_date": "2025-11-14"
}
```
→ Sends: Gown Care & Return Instructions email + Collection Complete SMS

### `ReturnProcessed` (published by Return an Order Saga)
```json
{
  "order_id": "ORD-001",
  "student_name": "Jia Qian",
  "phone": "+6588756213",
  "email": "wanjiaqian613@gmail.com",
  "refund_amount": "100.00"
}
```
→ Sends: Refund Receipt email + Return Complete SMS

### `pickup_reminder` (published by Order Service scheduled job)
```json
{
  "order_id": "ORD-001",
  "student_name": "Jia Qian",
  "phone": "+6588756213",
  "email": "wanjiaqian613@gmail.com"
}
```
→ Sends: Collection/Delivery reminder SMS + email

### `return_reminder` (published by Order Service scheduled job)
```json
{
  "order_id": "ORD-001",
  "student_name": "Jia Qian",
  "phone": "+6588756213",
  "email": "wanjiaqian613@gmail.com"
}
```
→ Sends: Return due reminder SMS + email

---

## API Endpoints

The service exposes two HTTP endpoints — mainly for health checks and support tooling:

| Method | Path | Description |
|---|---|---|
| `GET` | `/health` | Liveness probe — returns `{"status": "ok"}` |
| `GET` | `/notifications/<order_id>` | Returns all notification log entries for an order |

These are accessed through Kong in production. For local testing, call `http://localhost:5001` directly.

---

## Database Schema

```sql
CREATE TABLE notification_logs (
    id              SERIAL          PRIMARY KEY,
    order_id        VARCHAR(64)     NOT NULL,
    event_type      VARCHAR(32)     NOT NULL,   -- e.g. 'OrderConfirmed'
    channel         VARCHAR(8)      NOT NULL,   -- 'SMS' or 'EMAIL'
    recipient       VARCHAR(255)    NOT NULL,   -- phone number or email address
    message_body    TEXT            NOT NULL,
    status          VARCHAR(10)     NOT NULL DEFAULT 'PENDING',
    external_id     VARCHAR(128),               -- Twilio SID or SendGrid message ID
    error_message   TEXT,
    created_at      TIMESTAMPTZ     NOT NULL DEFAULT NOW()
);
```

`status` transitions: `PENDING` → `SENT` on success, `PENDING` → `FAILED` on adapter error. Failed rows retain the `error_message` so you can diagnose and manually retry if needed.