# Return Order Saga

Orchestrates the gown return workflow for the GradGownRental system — handling damage assessment, refund processing, and the full maintenance lifecycle back to available stock.

## Overview

- **Port**: 5006
- **Tech Stack**: Python, Flask, Kafka
- **Pattern**: Saga Orchestrator (multi-step, with maintenance continuation endpoints)
- **Role**: Coordinates Order Service, Inventory Service, and Payment Service when a student returns a gown. Manages both clean returns and damage workflows. Publishes a return summary event for email notification.

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/health` | Health check |
| `POST` | `/returns/process` | Process a gown return with optional damage assessment |
| `POST` | `/returns/<order_id>/transition-wash` | Mark repair as complete; move items to wash |
| `POST` | `/returns/<order_id>/maintenance-complete` | Mark wash as complete; return items to available stock |

## Saga Flow

### `POST /returns/process`

The primary return endpoint, called when a gown is physically returned.

**Request Body**:
```json
{
  "order_id": "f47ac10b-58cc-4372-a567-0e02b2c3d479",
  "payment_id": "pay-456",
  "selected_packages": [...],
  "damaged_packages": [...],
  "damage_components": ["gown", "hood"],
  "damage_report": "Tear on gown sleeve",
  "damage_images": ["https://..."],
  "damage_fee": 3000,
  "original_deposit": 15000
}
```

**Steps**:
1. Partition items into `damaged_packages` and `clean_packages`
2. Call **Order Service** → update status to `RETURNED_DAMAGED` (if damage) or `RETURNED` (if clean)
3. Call **Inventory Service**:
   - Damaged items: `RENTED_TO_DAMAGED`
   - Clean items: `RENTED_TO_WASH`
4. Calculate `refundable_amount = original_deposit - damage_fee`
5. Call **Payment Service** `POST /refunds` → process refund → receive `refund_id`
6. If damage: call **Inventory Service** → `DAMAGED_TO_REPAIR`
7. Publish `ReturnProcessed` to Kafka → **Notification Service** sends refund summary email
8. Return summary

**Response** `200 OK`:
```json
{
  "order_id": "f47ac10b-58cc-4372-a567-0e02b2c3d479",
  "refund_id": "re_xxx",
  "refundable_amount": 12000,
  "status": "COMPLETED"
}
```

---

### `POST /returns/<order_id>/transition-wash`

Called by staff when repair work is finished. Moves items from `REPAIR` to `WASH`.

**Steps**:
1. Call **Inventory Service** → `REPAIR_TO_WASH`

---

### `POST /returns/<order_id>/maintenance-complete`

Called by staff when laundering is finished. Returns items to available stock and closes the order.

**Steps**:
1. Call **Inventory Service** → `WASH_TO_AVAILABLE`
2. Call **Order Service** → update status to `COMPLETED`

## Damage Components

Valid values for `damage_components`:

| Value | Description |
|-------|-------------|
| `gown` | Main graduation gown |
| `hood` | Faculty hood |
| `mortarboard` | Mortarboard cap |

## Inventory State Machine (Return Path)

```
RENTED
  ├─ WASH              (clean return)
  │    └─ AVAILABLE    (maintenance-complete)
  └─ DAMAGED           (damaged return)
       └─ REPAIR
            └─ WASH
                 └─ AVAILABLE
```

## Order Status Transitions

| Step | Order Status |
|------|-------------|
| Return received (no damage) | `RETURNED` |
| Return received (with damage) | `RETURNED_DAMAGED` |
| Maintenance complete | `COMPLETED` |

## Error Handling

If any step fails:
1. Log to **Error Service** (`POST /errors`) with saga name, step, and order ID.
2. Abort and return an error response.

## Kafka Events Published

| Topic | Consumer | Purpose |
|-------|----------|---------|
| `ReturnProcessed` | Notification Service | Send refund and damage summary to student |

## Services Called

| Service | Endpoint | Purpose |
|---------|----------|---------|
| Order Service | `POST /orders/{id}/return` | Set status to RETURNED / RETURNED_DAMAGED |
| Order Service | `POST /orders/{id}/complete` | Set status to COMPLETED |
| Inventory Service | `POST /stock/transition` | Manage all stock state transitions |
| Payment Service | `POST /refunds` | Process partial/full refund |
| Error Service | `POST /errors` | Log failures |

## Running Locally

```bash
pip install -r requirements.txt
python -m src.app
```

## Docker

```bash
docker compose up return-order-saga
```
