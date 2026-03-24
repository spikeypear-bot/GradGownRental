# Error Service

A lightweight microservice responsible for logging failures that occur during saga orchestration in the GradGownRental system. It receives error reports from sagas via HTTP, persists them to a PostgreSQL database, and triggers a notification alert.

---

## Tech Stack

- Python 3.12
- Flask
- Flask-SQLAlchemy
- PostgreSQL
- psycopg2

---

## Endpoints

### POST /errors
Logs a new error from a saga.

**Request Body:**
```json
{
  "saga_name": "PlaceAnOrderSaga",
  "step": "Step 10 - POST /payments",
  "order_id": "abc-123",
  "error_message": "Payment service timeout",
  "status_code": 504
}
```

**Response (201):**
```json
{
  "error_id": "uuid-here",
  "status": "logged"
}
```

### GET /errors
Returns all logged errors, sorted by most recent.

**Response (200):**
```json
[
  {
    "error_id": "...",
    "saga_name": "...",
    "step": "...",
    "order_id": "...",
    "error_message": "...",
    "status_code": 504,
    "created_at": "..."
  }
]
```

### GET /errors/<error_id>
Returns a specific error log by ID.

**Response (200):**
```json
{
  "error_id": "...",
  "saga_name": "...",
  "step": "...",
  "order_id": "...",
  "error_message": "...",
  "status_code": 504,
  "created_at": "..."
}
```

---

## How Other Services Call This
import requests

requests.post("http://localhost:5006/errors", json={
    "saga_name": "PlaceAnOrderSaga",
    "step": "Step 10 - POST /payments",
    "order_id": order_id,
    "error_message": str(e),
    "status_code": 500
})