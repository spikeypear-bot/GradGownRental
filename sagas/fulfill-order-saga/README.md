# Fulfill Order Saga

Orchestrates the order fulfillment (handover) workflow for the GradGownRental system — activating the order, syncing logistics tracking, and transitioning inventory to rented.

## Overview

- **Port**: 5005
- **Tech Stack**: Python, Flask, Kafka
- **Pattern**: Saga Orchestrator
- **Role**: Coordinates Order Service, Logistics Service, and Inventory Service when a gown is physically handed over to a student. Publishes an event to notify the student via email.

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/health` | Health check |
| `POST` | `/fulfillment/activate` | Activate handover for a confirmed order |

## Saga Flow

### `POST /fulfillment/activate`

Called by staff or an admin system when a gown is handed over (collection) or delivered.

**Request Body**:
```json
{
  "order_id": "f47ac10b-58cc-4372-a567-0e02b2c3d479",
  "selected_packages": [...],
  "chosen_date": "2024-06-01",
  "tracking_status": "COLLECTED"
}
```

**Steps**:
1. Fetch full order from **Order Service** `GET /orders/{order_id}`
2. Call **Order Service** `POST /orders/{order_id}/activate` → update status to `ACTIVE`
3. Call **Logistics Service** `PUT /logistics/{shipment_id}/status` → sync tracking status (`COLLECTED` or `DELIVERED`)
4. Call **Inventory Service** `POST /stock/transition` → `RESERVED_TO_RENTED`
5. Publish `OrderActivated` to Kafka → **Notification Service** sends handover instructions email
6. Return confirmation

**Response** `200 OK`:
```json
{
  "order_id": "f47ac10b-58cc-4372-a567-0e02b2c3d479",
  "status": "COMPLETED"
}
```

## Saga State Transitions

```
STARTED
  └─ ORDER_ACTIVATED         (order status set to ACTIVE)
       └─ LOGISTICS_UPDATED  (tracking status synced in OutSystems)
            └─ INVENTORY_UPDATED (inventory: RESERVED → RENTED)
                 └─ COMPLETED
```

## Error Handling

If any step fails:
1. Log to **Error Service** (`POST /errors`) with saga name, step, and order ID.
2. Abort and return an error response.

## Kafka Events Published

| Topic | Consumer | Purpose |
|-------|----------|---------|
| `OrderActivated` | Notification Service | Send handover instructions to student |

## Services Called

| Service | Endpoint | Purpose |
|---------|----------|---------|
| Order Service | `GET /orders/{id}` | Fetch order details |
| Order Service | `POST /orders/{id}/activate` | Set status to ACTIVE |
| Logistics Service | `PUT /logistics/{shipment_id}/status` | Sync tracking status |
| Inventory Service | `POST /stock/transition` | Transition RESERVED → RENTED |
| Error Service | `POST /errors` | Log failures |

## Tracking Status Values

| Value | Meaning |
|-------|---------|
| `COLLECTED` | Student collected gown in person |
| `DELIVERED` | Gown delivered to student's address |

## Running Locally

```bash
pip install -r requirements.txt
python -m src.app
```

## Docker

```bash
docker compose up fulfill-order-saga
```
