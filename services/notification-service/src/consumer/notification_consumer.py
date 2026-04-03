"""
NotificationConsumer — Kafka consumer that routes incoming events to NotificationService.

Topics consumed:
  • OrderConfirmed     → handle_order_confirmed   (Scenario 2b)
  • OrderActivated     → handle_order_activated   (Scenario 2b)
  • ReturnProcessed    → handle_return_processed  (Scenario 2b)
  • pickup_reminder    → handle_pickup_reminder   (Scenario 2a)
  • return_reminder    → handle_return_reminder   (Scenario 2a)

If the Notification Service is temporarily down, Kafka retains messages and
replays them on restart — guaranteeing no student misses their notification.
"""

import json
import logging
import os
import threading

from kafka import KafkaConsumer
from kafka.errors import KafkaError

from service.notification_service import NotificationService

logger = logging.getLogger(__name__)

TOPICS = [
    "OrderConfirmed",
    "OrderActivated",
    "ReturnProcessed",
    "pickup_reminder",
    "return_reminder",
]

_HANDLER_MAP = {
    "OrderConfirmed":  "handle_order_confirmed",
    "OrderActivated":  "handle_order_activated",
    "ReturnProcessed": "handle_return_processed",
    "pickup_reminder": "handle_pickup_reminder",
    "return_reminder": "handle_return_reminder",
}


def _safe_json_deserializer(value: bytes | None) -> dict | None:
    """Decode Kafka message JSON without crashing the consumer thread."""
    if not value:
        return None

    try:
        return json.loads(value.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError):
        logger.warning("Skipping malformed Kafka message: %r", value[:200])
        return None


class NotificationConsumer:
    def __init__(self, notification_service: NotificationService):
        self._service = notification_service
        self._consumer = KafkaConsumer(
            *TOPICS,
            bootstrap_servers=os.environ.get("KAFKA_BOOTSTRAP_SERVERS", "kafka:29092"),
            group_id="notification-service-group",
            auto_offset_reset="earliest",       # replay missed messages on restart
            enable_auto_commit=True,
            value_deserializer=_safe_json_deserializer,
        )
        self._thread: threading.Thread | None = None

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    def start(self) -> None:
        """Start consuming in a background daemon thread."""
        self._thread = threading.Thread(target=self._consume_loop, daemon=True, name="kafka-consumer")
        self._thread.start()
        logger.info("NotificationConsumer started | topics=%s", TOPICS)

    def stop(self) -> None:
        self._consumer.close()
        logger.info("NotificationConsumer stopped")

    # ------------------------------------------------------------------
    # Consumer loop
    # ------------------------------------------------------------------

    def _consume_loop(self) -> None:
        try:
            for message in self._consumer:
                self._handle(message)
        except KafkaError as exc:
            logger.exception("Kafka consumer error: %s", exc)

    def _handle(self, message) -> None:
        if message.value is None:
            logger.warning("Received empty message on topic=%s, skipping", message.topic)
            return
        topic: str = message.topic
        payload: dict = message.value

        logger.info("Received Kafka event | topic=%s | payload=%s", topic, payload)

        handler_name = _HANDLER_MAP.get(topic)
        if handler_name is None:
            logger.warning("No handler registered for topic: %s", topic)
            return

        handler = getattr(self._service, handler_name, None)
        if handler is None:
            logger.error("Handler method missing on NotificationService: %s", handler_name)
            return

        try:
            handler(payload)
        except Exception as exc:  # noqa: BLE001
            # Log and continue — never let one bad message crash the consumer loop.
            logger.exception(
                "Failed to handle event | topic=%s | order_id=%s | error=%s",
                topic,
                payload.get("order_id"),
                exc,
            )
