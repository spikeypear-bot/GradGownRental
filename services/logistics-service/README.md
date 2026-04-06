BASE_URL = https://personal-fssbnhif.outsystemscloud.com/Logistics/rest/Logistics
(use this followed by the endpoint url)

# Kafka ingress

`logistics-service` consumes `OrderPaid` from Kafka and forwards it to OutSystems:

Kafka `OrderPaid` -> OutSystems `POST /logistics/events/order-paid`

## Expected Kafka payload
{
  "order_id": "string",
  "fulfillment_method": "DELIVERY or COLLECTION",
  "fulfillment_date": "YYYY-MM-DD or YYYY-MM-DDTHH:MM:SS"
}

OutSystems is the source of truth for shipment reads. The local `_ORDER_SHIPMENT_CACHE` is only used as a fallback helper if an OutSystems lookup fails.

# Shipment reads

## Get full shipment by order ID
GET /logistics/order/{order_id}

Returns the OutSystems shipment payload for an order, including fields such as:
- `shipment_id`
- `order_id`
- `fulfillment_method`
- `tracking_status`
- `scheduled_datetime`
- `created_at`

## Get shipment ID by order ID
GET /logistics/order/{order_id}/shipment-id

Returns a small lookup payload with the resolved shipment ID. The response also indicates whether the ID came from `outsystems` or the local fallback `cache`.


# Fulfill Order Saga proxy (Scenario 3)
PUT /logistics/{shipment_id}/status

This local HTTP endpoint remains only as a thin proxy for `fulfill-order-saga`.

## Expected request body
{
  "tracking_status": "COLLECTED or DELIVERED"
}
