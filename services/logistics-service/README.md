# Kafka wrapper in (Scenario 1)
POST /logistics/events/order-paid

## Expected request body structure
{
  "order_id": "string",
  "fulfillment_method": "DELIVERY or PICKUP",
  "scheduled_datetime": "YYYY-MM-DDTHH:MM:SS"
}


# Fulfill an Order Saga (Scenario 3)
PUT /logistics/{shipment_id}/status

## Expected request body structure
{
  "tracking_status": "COLLECTED or DELIVERED"
}
