# Logistics Service

Bridges the GradGownRental system with OutSystems for shipment tracking and delivery management.

## Overview

- **Port**: 5004
- **Tech Stack**: Python, Flask, Kafka
- **Database**: None (stateless — OutSystems is the source of truth)
- **Role**: Thin proxy adapter between internal sagas and the OutSystems logistics platform. Handles shipment creation on payment, status updates during fulfillment, and shipment lookups.

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/health` | Health check |
| `GET` | `/logistics/order/<order_id>` | Get full shipment data by order ID |
| `GET` | `/logistics/order/<order_id>/shipment-id` | Look up shipment ID by order ID |
| `GET` | `/logistics/<shipment_id>` | Get shipment details by shipment ID |
| `PUT` | `/logistics/<shipment_id>/status` | Update shipment tracking status (Fulfill-Order-Saga proxy) |

### GET `/logistics/order/<order_id>`

Returns the OutSystems shipment payload for an order, including:
- `shipment_id`
- `order_id`
- `fulfillment_method`
- `tracking_status`
- `scheduled_datetime`
- `created_at`

### GET `/logistics/order/<order_id>/shipment-id`

Returns a small lookup payload with the resolved shipment ID, and indicates whether the ID came from `outsystems` or the local fallback `cache`.

### PUT `/logistics/<shipment_id>/status`

Thin proxy for **Fulfill-Order-Saga**. Updates the tracking status in OutSystems.

**Request Body**:
```json
{
  "tracking_status": "COLLECTED"
}
```

Valid statuses: `SCHEDULED`, `COLLECTED`, `DELIVERED`

## Kafka Events Consumed

| Topic | Producer | Action |
|-------|----------|--------|
| `OrderPaid` | Place-Order-Saga | Forwards order to OutSystems to create/schedule a shipment |

### Expected `OrderPaid` Payload

```json
{
  "order_id": "f47ac10b-58cc-4372-a567-0e02b2c3d479",
  "fulfillment_method": "DELIVERY",
  "fulfillment_date": "2026-05-15"
}
```

On receiving this event, the service calls OutSystems `POST /logistics/events/order-paid` to register the shipment.

## OutSystems Integration

- **Base URL**: `https://personal-fssbnhif.outsystemscloud.com/Logistics/rest/Logistics`
- The service acts as a lightweight HTTP proxy; all persistent shipment data lives in OutSystems.
- An in-memory cache (`_ORDER_SHIPMENT_CACHE`) provides a fallback if an OutSystems lookup fails. The cache is cleared on restart.

## Environment Variables

| Variable | Description |
|----------|-------------|
| `OUTSYSTEMS_BASE_URL` | Base URL for the OutSystems Logistics REST API |
| `OUTSYSTEMS_API_KEY` | API key for OutSystems authentication |
| `KAFKA_BOOTSTRAP_SERVERS` | Kafka broker address |

## Running Locally

```bash
pip install -r requirements.txt
python main.py
```

## Docker

```bash
docker compose up logistics-service
```

## Notes

- Only `DELIVERY` orders involve active shipment tracking in OutSystems. `COLLECTION` orders are registered to allow staff confirmation tracking.
- OutSystems is the source of truth for shipment reads. The local cache is only used as a fallback helper if an OutSystems lookup fails.
