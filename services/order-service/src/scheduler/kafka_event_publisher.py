"""
KafkaEventPublisher — emits order reminder events for notification-service.

Published topics:
  • pickup_reminder
  • return_reminder
"""

import json
import logging
import os

from kafka import KafkaProducer

logger = logging.getLogger(__name__)


class KafkaEventPublisher:
    def __init__(self):
        bootstrap = os.environ.get("KAFKA_BOOTSTRAP_SERVERS", "kafka:29092")
        self._producer = KafkaProducer(
            bootstrap_servers=bootstrap,
            value_serializer=lambda v: json.dumps(v).encode("utf-8"),
        )
        logger.info("KafkaEventPublisher initialised | bootstrap=%s", bootstrap)

    def publish_order_paid(self, payload: dict) -> None:
        self._publish("OrderPaid", payload)

    def publish_pickup_reminder(self, payload: dict) -> None:
        self._publish("pickup_reminder", payload)

    def publish_return_reminder(self, payload: dict) -> None:
        self._publish("return_reminder", payload)

    def _publish(self, topic: str, payload: dict) -> None:
        future = self._producer.send(topic, payload)
        meta = future.get(timeout=10)
        logger.info(
            "Published reminder event | topic=%s | partition=%s | offset=%s | order_id=%s",
            topic,
            meta.partition,
            meta.offset,
            payload.get("order_id"),
        )

    def close(self) -> None:
        try:
            self._producer.flush(timeout=5)
            self._producer.close()
        except Exception:
            logger.exception("Failed to close KafkaEventPublisher cleanly")
