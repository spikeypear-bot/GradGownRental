# Place Order Saga

Orchestrates the complete checkout flow for the GradGownRental system — from order creation through payment verification and inventory reservation.

## Overview

- **Port**: 5003
- **Tech Stack**: Python, Flask, Kafka
- **Pattern**: Saga Orchestrator (two-phase checkout)
- **Role**: Coordinates Order Service, Payment Service, and Inventory Service to safely complete a rental checkout. Publishes events to trigger downstream notifications and logistics scheduling.

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/health` | Health check |
| `POST` | `/orders/create` | Phase 1: Initialize order and create Stripe PaymentIntent |
| `POST` | `/submit-payment` | Phase 2: Verify payment and finalize the order |

## Saga Flow

### Phase 1 — `POST /orders/create`

Initializes the order and returns payment details to the frontend.

**Request Body**:
```json
{
  "hold_id": "hold-xyz",
  "student_name": "Jane Doe",
  "student_email": "jane@example.com",
  "student_id": "S1234567A",
  "selected_packages": [...],
  "fulfillment_method": "COLLECTION",
  "collection_date": "2024-06-01",
  "return_date": "2024-06-03",
  "total_amount": 15000
}
```

**Steps**:
1. Call **Order Service** `POST /orders` → create order with status `PENDING` → receive `order_id`
2. Call **Payment Service** `POST /checkout` → create Stripe PaymentIntent → receive `client_secret`
3. Return `{order_id, client_secret}` to frontend

**Response** `200 OK`:
```json
{
  "order_id": "f47ac10b-58cc-4372-a567-0e02b2c3d479",
  "client_secret": "pi_xxx_secret_yyy"
}
```

---

### Phase 2 — `POST /submit-payment`

Verifies the completed payment and locks in the reservation.

**Request Body**:
```json
{
  "order_id": "f47ac10b-58cc-4372-a567-0e02b2c3d479",
  "payment_intent_id": "pi_xxx"
}
```

**Steps**:
1. Call **Payment Service** `POST /payments` → verify PaymentIntent is `succeeded` → receive `payment_id`
2. Call **Order Service** `POST /orders/{order_id}/status` → update to `CONFIRMED`
3. Call **Inventory Service** `POST /stock/transition` → `AVAILABLE_TO_RESERVED` (converts soft-hold to hard reservation)
4. Publish `OrderConfirmed` to Kafka → **Notification Service** sends receipt email
5. Publish `OrderPaid` to Kafka → **Logistics Service** schedules delivery/collection in OutSystems
6. Return order summary

**Response** `200 OK`:
```json
{
  "order_id": "f47ac10b-58cc-4372-a567-0e02b2c3d479",
  "payment_id": "pay-456",
  "status": "COMPLETED"
}
```

## Saga State Transitions

```
STARTED
  └─ ORDER_INITIALISED       (order created in Order Service)
       └─ PAYMENT_AUTHORISED (payment verified)
            └─ ORDER_CONFIRMED (order status updated)
                 └─ INVENTORY_TRANSITIONED
                      └─ COMPLETED
```

## Error Handling

If any step fails:
1. The saga logs the error to **Error Service** (`POST /errors`) with the failed step and order ID.
2. The saga aborts and returns an error response to the caller.
3. The order remains in `PENDING` status; no compensating transactions are applied at this stage.

## Kafka Events Published

| Topic | Consumer | Purpose |
|-------|----------|---------|
| `OrderConfirmed` | Notification Service | Send receipt email to student |
| `OrderPaid` | Logistics Service | Schedule delivery/collection in OutSystems |

## Services Called

| Service | Endpoint | Purpose |
|---------|----------|---------|
| Order Service | `POST /orders` | Create order |
| Order Service | `POST /orders/{id}/status` | Update to CONFIRMED |
| Payment Service | `POST /checkout` | Create PaymentIntent |
| Payment Service | `POST /payments` | Verify and record payment |
| Inventory Service | `POST /stock/transition` | Reserve inventory |
| Error Service | `POST /errors` | Log failures |

## Running Locally

```bash
pip install -r requirements.txt
python -m src.app
```

## Docker

```bash
docker compose up place-order-saga
```
