import json
import logging
import os
import threading
from datetime import datetime, timezone

import requests
from flask import Flask, jsonify, request
from flask_cors import CORS
from kafka import KafkaConsumer

try:
    from .swagger_docs import register_swagger
except ImportError:
    from swagger_docs import register_swagger

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s — %(message)s",
)
logger = logging.getLogger("logistics-service")

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
_OS_BASE = os.environ.get(
    "OUTSYSTEMS_BASE_URL",
    "https://personal-fssbnhif.outsystemscloud.com/Logistics/rest/Logistics",
).rstrip("/")

_ERR_BASE = os.environ.get("ERROR_SERVICE_URL", "http://error-service:5005").rstrip("/")

# ---------------------------------------------------------------------------
# Error-service client
# ---------------------------------------------------------------------------

def _report_error(saga: str, step: str, detail: str, order_id: str | None = None) -> None:
    payload = {"saga": saga, "step": step, "detail": detail}
    if order_id:
        payload["order_id"] = order_id
    try:
        resp = requests.post(f"{_ERR_BASE}/errors", json=payload, timeout=5)
        resp.raise_for_status()
        logger.info("Error reported to error-service | saga=%s step=%s", saga, step)
    except requests.RequestException as exc:
        logger.error("Failed to reach error-service: %s", exc)


# ---------------------------------------------------------------------------
# OutSystems client
# ---------------------------------------------------------------------------

def _os_request(method: str, path: str, *, json_body: dict) -> requests.Response:
    url = f"{_OS_BASE}{path}"
    resp = requests.request(
        method,
        url,
        json=json_body,
        timeout=10,
        headers={"Content-Type": "application/json"},
    )
    resp.raise_for_status()
    return resp


def notify_order_paid(order_id: str, fulfillment_method: str, scheduled_datetime: str) -> None:
    _os_request(
        "POST",
        "/logistics/events/order-paid",
        json_body={
            "order_id": order_id,
            "fulfillment_method": fulfillment_method,
            "scheduled_datetime": scheduled_datetime,
        },
    )


def notify_status_update(shipment_id: int, tracking_status: str) -> None:
    _os_request(
        "PUT",
        f"/logistics/{shipment_id}/status",
        json_body={"tracking_status": tracking_status},
    )


# ---------------------------------------------------------------------------
# App
# ---------------------------------------------------------------------------

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

        scheduled_datetime = payload.get("scheduled_datetime") or datetime.now(timezone.utc).isoformat()
        fulfillment_method = payload.get("fulfillment_method", "COLLECTION")

        state.shipments[order_id] = {
            "shipment_id": payload.get("shipment_id") or order_id,
            "order_id": order_id,
            "fulfillment_method": fulfillment_method,
            "tracking_status": "SCHEDULED",
            "scheduled_datetime": scheduled_datetime,
            "updated_at": datetime.now(timezone.utc).isoformat(),
        }

        try:
            notify_order_paid(order_id, fulfillment_method, scheduled_datetime)
        except Exception as exc:
            _report_error(
                saga="order-fulfillment",
                step="notify-outsystems-order-paid",
                detail=str(exc),
                order_id=order_id,
            )

        return jsonify(state.shipments[order_id]), 201

    @app.put("/logistics/<string:shipment_id>/status")
    def update_status(shipment_id: str):
        body = request.get_json() or {}
        tracking_status = body.get("tracking_status")
        if tracking_status not in {"COLLECTED", "DELIVERED", "SCHEDULED"}:
            return jsonify({"error": "tracking_status must be one of SCHEDULED/COLLECTED/DELIVERED"}), 400

        shipment = state.shipments.get(shipment_id)
        if shipment is None:
            for _, record in state.shipments.items():
                if record.get("shipment_id") == shipment_id:
                    shipment = record
                    break

        if shipment is None:
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

        try:
            os_shipment_id = int(shipment["shipment_id"])
            notify_status_update(os_shipment_id, tracking_status)
        except (ValueError, TypeError):
            logger.warning("shipment_id=%s is not a valid int64 — skipping OutSystems status update", shipment["shipment_id"])
        except Exception as exc:
            _report_error(
                saga="order-fulfillment",
                step="notify-outsystems-status-update",
                detail=str(exc),
                order_id=shipment.get("order_id"),
            )

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

    register_swagger(app)
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

            scheduled_datetime = payload.get("fulfillment_date") or datetime.now(timezone.utc).isoformat()
            fulfillment_method = payload.get("fulfillment_method", "COLLECTION")

            state.shipments[order_id] = {
                "shipment_id": payload.get("shipment_id") or order_id,
                "order_id": order_id,
                "fulfillment_method": fulfillment_method,
                "tracking_status": "SCHEDULED",
                "scheduled_datetime": scheduled_datetime,
                "updated_at": datetime.now(timezone.utc).isoformat(),
            }
            logger.info("OrderPaid consumed | order_id=%s", order_id)

            try:
                notify_order_paid(order_id, fulfillment_method, scheduled_datetime)
            except Exception as exc:
                _report_error(
                    saga="order-fulfillment",
                    step="notify-outsystems-order-paid",
                    detail=str(exc),
                    order_id=order_id,
                )

    t = threading.Thread(target=loop, daemon=True, name="order-paid-consumer")
    t.start()


app = create_app()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5004)), debug=False)