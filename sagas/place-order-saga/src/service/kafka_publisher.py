"""
KafkaPublisher — thin wrapper around KafkaProducer for the saga.

Events published by the checkout flow:
  • OrderPaid       → consumed by Logistics Service
  • OrderConfirmed  → consumed by Notification Service
"""

import json
import logging
import os

from kafka import KafkaProducer
from kafka.errors import KafkaError

logger = logging.getLogger(__name__)


class KafkaPublisher:

    def __init__(self):
        self._producer = KafkaProducer(
            bootstrap_servers=os.environ.get("KAFKA_BOOTSTRAP_SERVERS", "kafka:29092"),
            value_serializer=lambda v: json.dumps(v).encode("utf-8"),
            acks="all",         # wait for full ISR acknowledgement
            retries=3,
        )

    def publish_order_paid(self, context) -> None:
        """
        Publish OrderPaid event.
        Consumed by: Logistics Service (reserves collection slot / assigns driver).
        """
        payload = {
            "order_id": context.order_id,
            "payment_id": context.payment_id,
            "fulfillment_method": context.fulfillment_method,
            "fulfillment_date": context.fulfillment_date,
        }
        self._publish("OrderPaid", payload)

    def publish_order_confirmed(self, context) -> None:
        """
        Publish OrderConfirmed event.
        Consumed by: Notification Service (sends receipt email).
        """
        payload = {
            "order_id": context.order_id,
            "payment_id": context.payment_id,
            "student_name": context.student_name,
            "phone": context.phone,
            "email": context.email,
            "fulfillment_method": context.fulfillment_method,
            "fulfillment_date": context.fulfillment_date,
            "return_date": context.return_date,
            "total_amount": context.total_amount,
        }
        self._publish("OrderConfirmed", payload)

    def _publish(self, topic: str, payload: dict) -> None:
        try:
            future = self._producer.send(topic, value=payload)
            self._producer.flush()
            record = future.get(timeout=10)
            logger.info(
                "Published to Kafka | topic=%s | partition=%s | offset=%s",
                topic, record.partition, record.offset,
            )
        except KafkaError as exc:
            logger.error("Failed to publish to Kafka | topic=%s | error=%s", topic, exc)
            raise

    def close(self) -> None:
        self._producer.close()
