#!/usr/bin/env python3
"""
Test script to publish pickup_reminder events to Kafka for testing.
"""

import json
import os
from kafka import KafkaProducer

# Configure Kafka
KAFKA_BOOTSTRAP_SERVERS = os.environ.get("KAFKA_BOOTSTRAP_SERVERS", "kafka:29092")

# Create producer
producer = KafkaProducer(
    bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
    value_serializer=lambda v: json.dumps(v).encode("utf-8"),
)

# Test pickup_reminder event
pickup_reminder_event = {
    "order_id": "ORDER-TEST-001",
    "student_name": "Test Student",
    "email": "test@example.com",
    "fulfillment_date": "2026-04-06",
    "return_date": "2026-04-08",
    "fulfillment_method": "COLLECTION",
}

print("Publishing pickup_reminder event...")
future = producer.send("pickup_reminder", pickup_reminder_event)
metadata = future.get(timeout=10)
print(f"✓ Published to partition {metadata.partition}, offset {metadata.offset}")

# Test return_reminder event
return_reminder_event = {
    "order_id": "ORDER-TEST-002",
    "student_name": "Another Test Student",
    "email": "another@example.com",
    "return_date": "2026-04-08",
}

print("Publishing return_reminder event...")
future = producer.send("return_reminder", return_reminder_event)
metadata = future.get(timeout=10)
print(f"✓ Published to partition {metadata.partition}, offset {metadata.offset}")

producer.flush(timeout=5)
producer.close()
print("\nEvents published successfully!")
