# Error Service

Centralized error logging service for capturing saga and service failures across the GradGownRental system.

## Overview

- **Port**: 5002
- **Tech Stack**: Python, Flask, Flask-SQLAlchemy, PostgreSQL, psycopg2
- **Role**: Receives error reports from sagas when a distributed transaction step fails; provides a unified log for debugging.

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/health` | Health check |
| `POST` | `/errors` | Log an error event |
| `GET` | `/errors` | Retrieve all error logs (most recent first) |
| `GET` | `/errors/<error_id>` | Retrieve a specific error log by ID |

### POST `/errors`

Log an error from a saga or service.

**Request Body**:
```json
{
  "saga_name": "PlaceAnOrderSaga",
  "step": "Step 10 - POST /payments",
  "order_id": "f47ac10b-58cc-4372-a567-0e02b2c3d479",
  "error_message": "Payment service timeout",
  "status_code": 504
}
```

**Response** `201 Created`:
```json
{
  "error_id": "uuid-here",
  "status": "logged"
}
```

### GET `/errors`

Returns all logged errors, sorted by most recent.

### GET `/errors/<error_id>`

Returns a specific error log by ID.

## How Sagas Call This Service

```python
import requests

requests.post("http://error-service:5002/errors", json={
    "saga_name": "PlaceAnOrderSaga",
    "step": "Step 10 - POST /payments",
    "order_id": order_id,
    "error_message": str(e),
    "status_code": 500
})
```

All three sagas call this endpoint as part of their failure handling before aborting a transaction.

## Environment Variables

| Variable | Description |
|----------|-------------|
| `DB_HOST` | PostgreSQL host |
| `DB_NAME` | Database name |
| `DB_USER` | Database user |
| `DB_PASSWORD` | Database password |

## Running Locally

```bash
pip install -r requirements.txt
python main.py
```

## Docker

```bash
docker compose up error-service
```
