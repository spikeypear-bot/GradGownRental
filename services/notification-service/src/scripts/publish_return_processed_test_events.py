"""Publish test ReturnProcessed events for DEPOSIT email-stage validation.

Usage example:
  python src/scripts/publish_return_processed_test_events.py \
    --email eichawzin123@gmail.com
"""

from __future__ import annotations

import argparse
import json
import os
from datetime import datetime, timezone

from kafka import KafkaProducer


def _build_payloads(order_prefix: str, email: str) -> list[dict]:
    ts = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")
    base = {
        "student_name": "Email Stage Test",
        "email": email,
        "processed_at": datetime.now(timezone.utc).isoformat(),
    }

    full_refund = {
        **base,
        "order_id": f"{order_prefix}-FULL-{ts}",
        "refund_amount": "40.00",
        "original_deposit": "40.00",
        "damage_fee": "0.00",
        "has_damage": False,
    }

    damaged_refund = {
        **base,
        "order_id": f"{order_prefix}-DMG-{ts}",
        "refund_amount": "25.00",
        "original_deposit": "40.00",
        "damage_fee": "15.00",
        "has_damage": True,
    }

    return [full_refund, damaged_refund]


def main() -> None:
    parser = argparse.ArgumentParser(description="Publish ReturnProcessed test events")
    parser.add_argument("--email", required=True, help="Recipient email for notification test")
    parser.add_argument(
        "--order-prefix",
        default="TESTRET",
        help="Prefix used to generate synthetic order IDs",
    )
    parser.add_argument(
        "--bootstrap",
        default=os.environ.get("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092"),
        help="Kafka bootstrap servers",
    )
    args = parser.parse_args()

    producer = KafkaProducer(
        bootstrap_servers=args.bootstrap,
        value_serializer=lambda v: json.dumps(v).encode("utf-8"),
        acks="all",
        retries=3,
    )

    payloads = _build_payloads(args.order_prefix, args.email)
    for payload in payloads:
        future = producer.send("ReturnProcessed", payload)
        meta = future.get(timeout=10)
        print(
            f"Published ReturnProcessed | order_id={payload['order_id']} "
            f"| partition={meta.partition} | offset={meta.offset}"
        )

    producer.flush()
    producer.close()

    print("\nDone. Check notification logs via /notifications/<order_id> for both generated order IDs.")


if __name__ == "__main__":
    main()
