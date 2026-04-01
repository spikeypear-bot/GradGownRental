import json
import logging
import os
import threading
from datetime import datetime, timezone

from flask import Flask, jsonify, request
from flask_cors import CORS
from kafka import KafkaConsumer

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s — %(message)s",
)
logger = logging.getLogger("logistics-service")


class LogisticsState:
    def __init__(self):
        self.shipments = {}


def create_app() -> Flask:
    app = Flask(__name__)
    CORS(app)
    state = LogisticsState()
    app.extensions["state"] = state

    @app.get("/health")
    def health():
        return jsonify({"status": "ok", "service": "logistics-service"}), 200

    @app.post("/logistics/events/order-paid")
    def order_paid_event():
        payload = request.get_json() or {}
        order_id = payload.get("order_id")
        if not order_id:
            return jsonify({"error": "Missing order_id"}), 400

        state.shipments[order_id] = {
            "shipment_id": payload.get("shipment_id") or order_id,
            "order_id": order_id,
            "fulfillment_method": payload.get("fulfillment_method", "COLLECTION"),
            "tracking_status": "SCHEDULED",
            "scheduled_datetime": payload.get("scheduled_datetime") or datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat(),
        }
        return jsonify(state.shipments[order_id]), 201

    @app.put("/logistics/<string:shipment_id>/status")
    def update_status(shipment_id: str):
        body = request.get_json() or {}
        tracking_status = body.get("tracking_status")
        if tracking_status not in {"COLLECTED", "DELIVERED", "SCHEDULED"}:
            return jsonify({"error": "tracking_status must be one of SCHEDULED/COLLECTED/DELIVERED"}), 400

        # Find by shipment_id or order_id for flexibility.
        shipment = state.shipments.get(shipment_id)
        if shipment is None:
            for _, record in state.shipments.items():
                if record.get("shipment_id") == shipment_id:
                    shipment = record
                    break

        if shipment is None:
            # Auto-create if upstream did not pre-register via OrderPaid.
            shipment = {
                "shipment_id": shipment_id,
                "order_id": body.get("order_id", shipment_id),
                "fulfillment_method": body.get("fulfillment_method", "COLLECTION"),
                "tracking_status": "SCHEDULED",
                "scheduled_datetime": body.get("scheduled_datetime") or datetime.now(timezone.utc).isoformat(),
            }
            state.shipments[shipment["order_id"]] = shipment

        shipment["tracking_status"] = tracking_status
        shipment["updated_at"] = datetime.now(timezone.utc).isoformat()
        return jsonify(shipment), 200

    @app.get("/logistics/<string:shipment_id>")
    def get_status(shipment_id: str):
        shipment = state.shipments.get(shipment_id)
        if shipment is None:
            for _, record in state.shipments.items():
                if record.get("shipment_id") == shipment_id:
                    shipment = record
                    break
        if shipment is None:
            return jsonify({"error": "Shipment not found"}), 404
        return jsonify(shipment), 200

    _start_order_paid_consumer(state)
    return app


def _start_order_paid_consumer(state: LogisticsState) -> None:
    bootstrap = os.environ.get("KAFKA_BOOTSTRAP_SERVERS", "kafka:29092")

    def loop():
        consumer = KafkaConsumer(
            "OrderPaid",
            bootstrap_servers=bootstrap,
            group_id="logistics-service-group",
            auto_offset_reset="earliest",
            enable_auto_commit=True,
            value_deserializer=lambda v: json.loads(v.decode("utf-8")) if v else None,
        )
        logger.info("Kafka consumer started | topic=OrderPaid")
        for message in consumer:
            payload = message.value or {}
            order_id = payload.get("order_id")
            if not order_id:
                continue
            state.shipments[order_id] = {
                "shipment_id": payload.get("shipment_id") or order_id,
                "order_id": order_id,
                "fulfillment_method": payload.get("fulfillment_method", "COLLECTION"),
                "tracking_status": "SCHEDULED",
                "scheduled_datetime": payload.get("fulfillment_date") or datetime.now(timezone.utc).isoformat(),
                "updated_at": datetime.now(timezone.utc).isoformat(),
            }
            logger.info("OrderPaid consumed | order_id=%s", order_id)

    t = threading.Thread(target=loop, daemon=True, name="order-paid-consumer")
    t.start()


app = create_app()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5004)), debug=False)
