# Payment Service

Handles payment processing and refunds via Stripe for the GradGownRental system.

## Overview

- **Port**: 3000
- **Tech Stack**: Python, Flask, PostgreSQL, Stripe
- **Database**: `payment`
- **Role**: Creates Stripe PaymentIntents, verifies payment completion, and processes refunds.

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/api/payment/health` | Health check |
| `POST` | `/api/payment/checkout` | Create a Stripe PaymentIntent |
| `POST` | `/api/payment/payments` | Authorize payment (verify intent & record in DB) |
| `POST` | `/api/payment/refunds` | Process a refund |
| `GET` | `/api/payment/payments/<order_id>` | Fetch payment record for an order |

### POST `/api/payment/checkout`

Creates a Stripe PaymentIntent for the given amount.

**Request Body**:
```json
{
  "amount": 15000,
  "currency": "sgd",
  "order_id": "f47ac10b-58cc-4372-a567-0e02b2c3d479"
}
```

**Response** `200 OK`:
```json
{
  "client_secret": "pi_xxx_secret_yyy"
}
```

### POST `/api/payment/payments`

Verifies a completed PaymentIntent and records the payment in the database.

**Request Body**:
```json
{
  "order_id": "f47ac10b-58cc-4372-a567-0e02b2c3d479",
  "payment_intent_id": "pi_xxx"
}
```

**Response** `200 OK`:
```json
{
  "payment_id": "pay-456",
  "status": "SUCCEEDED"
}
```

### POST `/api/payment/refunds`

Processes a refund for a previously succeeded payment.

**Request Body**:
```json
{
  "payment_id": "pay-456",
  "amount": 12000
}
```

**Response** `200 OK`:
```json
{
  "refund_id": "re_xxx",
  "status": "REFUNDED"
}
```

## Payment Flow

1. **Place-Order-Saga** calls `POST /checkout` → receives `client_secret`.
2. Frontend uses `client_secret` to collect card details via Stripe.js and confirm the payment.
3. **Place-Order-Saga** calls `POST /payments` with the resulting `payment_intent_id` to verify and record the payment.
4. On order return, **Return-Order-Saga** calls `POST /refunds` to issue a partial or full refund.

## Payment Status

| Status | Description |
|--------|-------------|
| `SUCCEEDED` | Payment captured successfully |
| `REFUNDED` | Full or partial refund issued |

## Environment Variables

| Variable | Description |
|----------|-------------|
| `STRIPE_SECRET_KEY` | Stripe secret API key |
| `DB_HOST` | PostgreSQL host |
| `DB_NAME` | Database name (`payment`) |
| `DB_USER` | Database user |
| `DB_PASSWORD` | Database password |

## Running Locally

```bash
pip install -r requirements.txt
python run.py
```

## Docker

```bash
docker compose up payment-service
```
