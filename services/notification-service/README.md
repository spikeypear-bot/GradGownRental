# Notification Service

Sends email notifications to students and logs all outgoing notifications for the GradGownRental system.

## Overview

- **Port**: 5001
- **Tech Stack**: Python, Flask, PostgreSQL, SendGrid (email), Kafka
- **Database**: `notification`
- **Role**: Consumes Kafka events from sagas and the order scheduler, dispatches transactional emails via SendGrid, and persists notification logs for auditing and the order tracking UI.

The service has **no synchronous dependencies on other microservices** — it only reads from Kafka. If it goes down, Kafka retains all messages and replays them on restart (`auto_offset_reset="earliest"`), guaranteeing no student misses a notification.

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
                                        │
                                 SendGridAdapter
                               (Anti-Corruption)
                                        │
                                  SendGrid API
                                    (Email)
                                        │
                           NotificationRepository
                                    │
                               PostgreSQL
                           (notification_logs)
```

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/health` | Health check — returns `{"status": "ok"}` |
| `GET` | `/notifications/<order_id>` | Fetch all notification logs for an order |

## Kafka Events Consumed

| Topic | Producer | Notifications Sent |
|-------|----------|--------------------|
| `OrderConfirmed` | Place-Order-Saga | Order Receipt email |
| `OrderActivated` | Fulfill-Order-Saga | Gown Care & Return Instructions email |
| `ReturnProcessed` | Return-Order-Saga | Refund Receipt email |
| `pickup_reminder` | Order-Service scheduler | Collection/Delivery reminder email |
| `return_reminder` | Order-Service scheduler | Return due reminder email |

### Kafka Event Payloads

**`OrderConfirmed`**:
```json
{
  "order_id": "f47ac10b-58cc-4372-a567-0e02b2c3d479",
  "student_name": "Jia Qian",
  "email": "student@example.com",
  "fulfillment_method": "COLLECTION",
  "fulfillment_date": "2025-11-10",
  "return_date": "2025-11-14",
  "total_amount": "125.00"
}
```

**`OrderActivated`**:
```json
{
  "order_id": "f47ac10b-58cc-4372-a567-0e02b2c3d479",
  "student_name": "Jia Qian",
  "email": "student@example.com",
  "return_date": "2025-11-14"
}
```

**`ReturnProcessed`**:
```json
{
  "order_id": "f47ac10b-58cc-4372-a567-0e02b2c3d479",
  "student_name": "Jia Qian",
  "email": "student@example.com",
  "refund_amount": "100.00"
}
```

**`pickup_reminder` / `return_reminder`**:
```json
{
  "order_id": "f47ac10b-58cc-4372-a567-0e02b2c3d479",
  "student_name": "Jia Qian",
  "email": "student@example.com"
}
```

## Database Schema

```sql
CREATE TABLE notification_logs (
    id              SERIAL          PRIMARY KEY,
    order_id        VARCHAR(64)     NOT NULL,
    event_type      VARCHAR(32)     NOT NULL,   -- e.g. 'OrderConfirmed'
    channel         VARCHAR(8)      NOT NULL,   -- 'EMAIL'
    recipient       VARCHAR(255)    NOT NULL,   -- email address
    message_body    TEXT            NOT NULL,
    status          VARCHAR(10)     NOT NULL DEFAULT 'PENDING',
    external_id     VARCHAR(128),               -- SendGrid message ID
    error_message   TEXT,
    created_at      TIMESTAMPTZ     NOT NULL DEFAULT NOW()
);
```

`status` transitions: `PENDING` → `SENT` on success, `PENDING` → `FAILED` on adapter error.

## Environment Variables

```env
# PostgreSQL
DB_HOST=notification-service-db
DB_PORT=5432
DB_NAME=notification
DB_USER=notification_user
DB_PASSWORD=notification_pass

# Kafka
KAFKA_BOOTSTRAP_SERVERS=kafka:29092

# SendGrid (email)
SENDGRID_API_KEY=SG.xxxxxxxxxxxxxxxxxxxxxxxx
SENDGRID_FROM_EMAIL=noreply@yourdomain.com
```

## Running Locally

```bash
pip install -r requirements.txt
python -m src.app
```

## Docker

```bash
# Start notification-service and its dependencies only
docker compose up --build notification-service notification-service-db kafka

# Full stack
docker compose up --build
```

## Testing

### Publish a test Kafka event manually

```bash
docker exec -it kafka bash
/opt/kafka/bin/kafka-console-producer.sh \
  --bootstrap-server localhost:9092 \
  --topic OrderConfirmed
```

Paste and press Enter:
```json
{"order_id": "f47ac10b-58cc-4372-a567-0e02b2c3d479", "student_name": "Jia Qian", "email": "student@example.com", "fulfillment_method": "COLLECTION", "fulfillment_date": "2025-11-10", "return_date": "2025-11-14", "total_amount": "125.00"}
```

Then check logs:
```bash
curl http://localhost:5001/notifications/f47ac10b-58cc-4372-a567-0e02b2c3d479
```

Expected response — one log entry with `"status": "SENT"`.

### Query the database directly

```bash
docker exec -it notification-service-db psql -U notification_user -d notification
```

```sql
SELECT id, order_id, event_type, channel, status, external_id, created_at
FROM notification_logs
ORDER BY created_at DESC
LIMIT 20;
```

### Verify Kafka consumer is connected

```bash
docker compose logs notification-service | grep "NotificationConsumer started"
```

## Project Structure

```
notification-service/
├── src/
│   ├── app.py                        ← Flask factory; wires everything together
│   ├── model/notification_log.py     ← NotificationLog dataclass + enums
│   ├── repository/                   ← All SQL isolated here
│   ├── service/notification_service.py ← Core logic; composes adapters + repo
│   ├── adapters/
│   │   └── sendgrid_adapter.py       ← Anti-Corruption Layer for SendGrid email
│   ├── consumer/notification_consumer.py ← Kafka consumer (background daemon thread)
│   └── controller/                   ← Flask blueprint: /health, /notifications
└── db/init.sql                       ← Creates notification_logs table on first boot
```
