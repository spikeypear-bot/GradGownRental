# Order Service

Manages the full lifecycle of gown rental orders in the GradGownRental system.

## Overview

- **Port**: 8081
- **Tech Stack**: Python, Flask, PostgreSQL, APScheduler
- **Database**: `order`
- **Role**: Creates orders, tracks status through the rental lifecycle, validates business rules, and publishes reminder events via Kafka.

## Order Lifecycle

```
PENDING
  └─ CONFIRMED         (payment processed by Place-Order-Saga)
       └─ ACTIVE       (gown handed over by Fulfill-Order-Saga)
            ├─ RETURNED          (returned, no damage)
            └─ RETURNED_DAMAGED  (returned with damage)
                 └─ COMPLETED    (maintenance done by Return-Order-Saga)
```

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/health` | Health check |
| `POST` | `/orders` | Create a new order |
| `GET` | `/orders/<order_id>` | Fetch an order by ID |
| `GET` | `/orders/by-email/<email>` | Fetch all orders for a student |
| `GET` | `/orders/status/<status>` | Fetch all orders with a given status |
| `POST` | `/orders/<order_id>/status` | Update order status |
| `POST` | `/orders/<order_id>/activate` | Activate order (handover to student) |
| `POST` | `/orders/<order_id>/return` | Mark order as returned |
| `POST` | `/orders/<order_id>/complete` | Complete order (after maintenance) |

### POST `/orders`

Creates a new order. Orders start as `PENDING` in the full checkout flow; the saga later confirms them after payment.

**Request Body**:
```json
{
  "order_id": "f47ac10b-58cc-4372-a567-0e02b2c3d479",
  "student_name": "Alice Chen",
  "email": "alice@example.com",
  "phone": "+65-1234-5678",
  "package_id": 5,
  "selected_items": [
    {"modelId": "0000024", "qty": 1},
    {"modelId": "0000002", "qty": 1},
    {"modelId": "0100020", "qty": 1}
  ],
  "rental_start_date": "2026-05-15",
  "rental_end_date": "2026-05-18",
  "total_amount": 75.00,
  "deposit": 75.00,
  "fulfillment_method": "DELIVERY"
}
```

**Response** `201 Created`: Full order object with `"status": "CONFIRMED"`.

### POST `/orders/<order_id>/return`

Marks a gown as returned. Validates that any reported damage does not exceed selected quantities.

**Request Body**:
```json
{
  "damaged_items": [
    {"modelId": "0100020", "qty": 1}
  ]
}
```

## Business Rules

### Fulfillment Method

| Method | Rule |
|--------|------|
| `DELIVERY` | `rental_start_date` must be at least 24 hours in the future. Same-day delivery is rejected. Auto-activated at 6 AM on `rental_start_date` by a scheduler job. |
| `COLLECTION` | No time restriction. Enables same-day walk-in pickups. Must be manually activated by staff via `/activate`. |

### Damage Validation

When returning with damaged items:
- Each `modelId` in `damaged_items` must exist in the order's `selected_items`.
- Damaged `qty` cannot exceed selected `qty` for that model.

```
Order has hat: 1, damage: hat: 1  → Valid
Order has gown: 2, damage: gown: 1 → Valid
Order has hat: 1, damage: hat: 2  → Invalid (exceeds selected qty)
Order has gown: 1, damage: jacket: 1 → Invalid (not in order)
```

## Reminder Scheduler

A background APScheduler job publishes Kafka events to notify students of upcoming deadlines:

| Kafka Topic | Trigger |
|-------------|---------|
| `pickup_reminder` | Student's collection/delivery date is approaching |
| `return_reminder` | Return deadline is approaching |

These events are consumed by the **Notification Service** to send reminder emails and SMS.

## Database Schema (Orders Table)

| Column | Type | Description |
|--------|------|-------------|
| `order_id` | VARCHAR UNIQUE | Unique order identifier |
| `student_name` | VARCHAR | Student's full name |
| `email` | VARCHAR | Student's email |
| `phone` | VARCHAR | Student's phone |
| `package_id` | INT | Graduation package ID |
| `selected_items` | JSONB | Items and quantities selected |
| `rental_start_date` | DATE | Rental start date |
| `rental_end_date` | DATE | Rental end date |
| `total_amount` | DECIMAL | Total charged (includes $5 delivery fee if applicable) |
| `deposit` | DECIMAL | Total deposit from selected items |
| `fulfillment_method` | VARCHAR | `COLLECTION` or `DELIVERY` |
| `status` | VARCHAR | Current lifecycle status |
| `damaged` | BOOLEAN | Whether any items were damaged |
| `damaged_items` | JSONB | Damaged items with model IDs and quantities |
| `hold_id` | VARCHAR | Reference to Inventory Service hold |
| `payment_id` | VARCHAR | Reference to Payment Service |

## Environment Variables

```bash
DB_HOST=localhost
DB_PORT=5432
DB_NAME=order
DB_USER=order_user
DB_PASSWORD=order_pass
KAFKA_BOOTSTRAP_SERVERS=kafka:29092
```

## Running Locally

```bash
pip install -r requirements.txt
python main.py
```

Service available at `http://localhost:8081`.

## Docker

```bash
docker compose up order-service
```
