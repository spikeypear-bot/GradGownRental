import json
import logging
import os

from kafka import KafkaProducer

logger = logging.getLogger(__name__)


class KafkaPublisher:
    def __init__(self):
        self._producer = KafkaProducer(
            bootstrap_servers=os.environ.get("KAFKA_BOOTSTRAP_SERVERS", "kafka:29092"),
            value_serializer=lambda v: json.dumps(v).encode("utf-8"),
        )

    def publish_return_processed(self, payload: dict) -> None:
        future = self._producer.send("ReturnProcessed", payload)
        meta = future.get(timeout=10)
        logger.info("Published ReturnProcessed | partition=%s | offset=%s", meta.partition, meta.offset)
