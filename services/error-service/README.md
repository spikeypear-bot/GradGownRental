# Error Service

**Saga Pattern Error Handler** — Centralizes failure logging and compensation triggering for distributed transactions in GradGownRental microservices. Demonstrates fault isolation and loose coupling.

---

## Purpose

When a saga step fails (e.g. Payment service timeout), this service:
1. **Logs the failure** → `docker logs error-service` for real-time observability
2. **Triggers notifications** → Compensation via Notification Service
3. **Returns 201 logged** → Saga continues recovery without blocking

**Proves microservices fault tolerance: one service failure doesn't cascade.**

---

## Tech Stack

- Python 3.12
- Flask
- Gunicorn (production server)
- `requests` (notification forwarding)

**Stateless & lightweight — no database dependency.**

---

## Endpoints

### `POST /errors`
**Receives saga failures, logs them, triggers compensation.**

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
  "status": "logged"
}
```

**Console Output:**
[ERROR] main — [PlaceAnOrderSaga] Step 10 failed | order_id=abc-123 | Payment service timeout


---

## Architecture Flow
Saga Step 10 (Payment) Error
↓ POST /errors
┌─────────────┐
│ error-service│ ← docker logs error-service
└──────┬──────┘
↓ POST /notifications/error
┌─────────────┐
│ notification│ ← triggers compensating transaction
│ service │
└─────────────┘

---

## How Other Services Call It

```python
import requests

try:
    requests.post("http://error-service:5002/errors", json={
        "saga_name": "PlaceAnOrderSaga",
        "step": f"Step 10 - POST /payments",
        "order_id": order_id,
        "error_message": str(e),
        "status_code": getattr(e, 'status_code', 500)
    }, timeout=2)
except:
    pass  # Don't block saga recovery
```

---

## Verification

```bash
# Watch logs in real-time
docker logs -f error-service

# Trigger test error (from any saga)
curl -X POST http://localhost:5002/errors \
  -H "Content-Type: application/json" \
  -d '{"saga_name":"TestSaga","step":"Test","error_message":"Test error"}'
```

**Expected:** Log entry appears immediately.

---

## Docker Compose

```yaml
error-service:
  build: ./services/error-service
  ports:
    - "5002:5002"
  environment:
    NOTIFICATION_SERVICE_URL: "http://notification-service:5005"
  networks:
    - app-network
```

---

## Production Considerations

- **Observability**: Add ELK stack (Elasticsearch + Kibana) for log aggregation
- **Persistence**: PostgreSQL + Grafana for historical analysis
- **Alerting**: Prometheus + Alertmanager for critical failure thresholds
- **Circuit Breaker**: Add resilience4j to prevent notification cascade failures

**Current implementation prioritizes Saga pattern proof over full production monitoring.**

---

## Why This Design?

1. **Fault Isolation**: Payment service down → saga still logs/recovers
2. **Loose Coupling**: HTTP contract only — no shared DB
3. **Demo Reliability**: Single container, no DB setup issues
4. **Saga Pattern Compliance**: Centralized failure coordination

**Validates microservices theory: independent failure handling via service mesh.**