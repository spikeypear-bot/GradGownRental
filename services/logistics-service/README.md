BASE_URL = https://personal-fssbnhif.outsystemscloud.com/Logistics/rest/Logistics
(use this followed by the endpoint url)

# Kafka ingress

`logistics-service` consumes `OrderPaid` from Kafka and forwards it to OutSystems:

Kafka `OrderPaid` -> OutSystems `POST /logistics/events/order-paid`

## Expected Kafka payload
{
  "order_id": "string",
  "fulfillment_method": "DELIVERY or PICKUP",
  "fulfillment_date": "YYYY-MM-DD or YYYY-MM-DDTHH:MM:SS"
}


# Fulfill Order Saga proxy (Scenario 3)
PUT /logistics/{shipment_id}/status

This local HTTP endpoint remains only as a thin proxy for `fulfill-order-saga`.

## Expected request body
{
  "tracking_status": "COLLECTED or DELIVERED"
}
