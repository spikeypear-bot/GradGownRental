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
    format="%(asctime)s [%(levelname)s] %(name)s - %(message)s",
)
logger = logging.getLogger("logistics-service")

_ORDER_SHIPMENT_CACHE: dict[str, int] = {}

_OS_BASE = os.environ.get(
    "OUTSYSTEMS_BASE_URL",
    "https://personal-fssbnhif.outsystemscloud.com/Logistics/rest/Logistics",
).rstrip("/")
_ERR_BASE = os.environ.get("ERROR_SERVICE_URL", "http://error-service:5002").rstrip("/")


def _safe_kafka_json_deserialize(value: bytes | None) -> dict | None:
    if not value:
        return None
    try:
        decoded = value.decode("utf-8")
        payload = json.loads(decoded)
        return payload if isinstance(payload, dict) else None
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        logger.warning("Skipping malformed Kafka message: %s", exc)
        return None


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


def _os_request(method: str, path: str, *, json_body: dict | None = None) -> requests.Response:
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


def _normalize_scheduled_datetime(raw_value: str | None) -> str:
    if not raw_value:
        return datetime.now(timezone.utc).isoformat()
    if "T" in raw_value:
        return raw_value
    try:
        parsed_date = datetime.fromisoformat(raw_value).date()
        return datetime.combine(parsed_date, datetime.min.time(), tzinfo=timezone.utc).isoformat()
    except ValueError:
        logger.warning("Invalid fulfillment_date=%s; using current UTC timestamp", raw_value)
        return datetime.now(timezone.utc).isoformat()


def _normalize_created_at(raw_value: str | None) -> str:
    if not raw_value:
        return datetime.now(timezone.utc).isoformat()
    return raw_value


def _resolve_shipment_id(payload: dict, order_id: str) -> int:
    shipment_id = payload.get("shipment_id")
    if isinstance(shipment_id, int):
        return shipment_id

    if isinstance(shipment_id, str) and shipment_id.isdigit():
        return int(shipment_id)

    # Deterministic fallback int64 when upstream payload doesn't include shipment_id.
    return abs(hash(order_id)) % 9_000_000_000_000_000 + 1_000_000_000_000_000


def _cache_order_shipment(order_id: str, shipment_id: int | str | None) -> None:
    if not order_id:
        return
    try:
        if shipment_id is None:
            return
        resolved = int(shipment_id)
    except (TypeError, ValueError):
        logger.warning("Skipping cache for non-numeric shipment_id=%s order_id=%s", shipment_id, order_id)
        return
    _ORDER_SHIPMENT_CACHE[order_id] = resolved


def _lookup_shipment_id(order_id: str) -> int | None:
    return _ORDER_SHIPMENT_CACHE.get(order_id)


def notify_order_paid(
    order_id: str,
    fulfillment_method: str,
    scheduled_datetime: str,
    shipment_id: int,
    created_at: str,
) -> dict:
    resp = _os_request(
        "POST",
        "/logistics/events/order-paid",
        json_body={
            "order_id": order_id,
            "fulfillment_method": fulfillment_method,
            "scheduled_datetime": scheduled_datetime,
            "shipment_id": shipment_id,
            "created_at": created_at,
        },
    )
    try:
        return resp.json() if resp.content else {}
    except ValueError:
        return {}


def notify_status_update(shipment_id: int, tracking_status: str) -> requests.Response:
    return _os_request(
        "PUT",
        f"/logistics/{shipment_id}/status",
        json_body={"tracking_status": tracking_status},
    )


def get_shipment(identifier: str | int) -> requests.Response:
    return _os_request("GET", f"/logistics/{identifier}")


def _extract_shipment_id(payload: dict) -> int | None:
    if not isinstance(payload, dict):
        return None

    raw_shipment_id = payload.get("shipment_id")
    if raw_shipment_id is None and isinstance(payload.get("data"), dict):
        raw_shipment_id = payload["data"].get("shipment_id")

    try:
        return int(raw_shipment_id) if raw_shipment_id is not None else None
    except (TypeError, ValueError):
        return None


def lookup_shipment_id_by_order(order_id: str) -> int | None:
    try:
        resp = get_shipment(order_id)
        payload = resp.json() if resp.content else {}
        shipment_id = _extract_shipment_id(payload)
        if shipment_id is not None:
            _cache_order_shipment(order_id, shipment_id)
        return shipment_id
    except requests.HTTPError as exc:
        status_code = getattr(exc.response, "status_code", None)
        if status_code == 404:
            return None
        raise


def create_app() -> Flask:
    app = Flask(__name__)
    CORS(app)

    @app.get("/health")
    def health():
        return jsonify({"status": "ok", "service": "logistics-service"}), 200

    @app.put("/logistics/<string:shipment_id>/status")
    def update_status(shipment_id: str):
        body = request.get_json() or {}
        tracking_status = body.get("tracking_status")
        if tracking_status not in {"COLLECTED", "DELIVERED", "SCHEDULED"}:
            return jsonify({"error": "tracking_status must be one of SCHEDULED/COLLECTED/DELIVERED"}), 400

        try:
            os_shipment_id = int(shipment_id)
        except (TypeError, ValueError):
            return jsonify({"error": "shipment_id must be a valid int64"}), 400

        try:
            resp = notify_status_update(os_shipment_id, tracking_status)
            payload = resp.json() if resp.content else {"updated": True}
            return jsonify(payload), resp.status_code
        except Exception as exc:
            _report_error(
                saga="order-fulfillment",
                step="notify-outsystems-status-update",
                detail=str(exc),
                order_id=body.get("order_id"),
            )
            return jsonify({"error": "Failed to update OutSystems shipment status"}), 502

    @app.get("/logistics/<string:shipment_id>")
    def get_shipment_status(shipment_id: str):
        try:
            resp = get_shipment(shipment_id)
            payload = resp.json() if resp.content else {}
            return jsonify(payload), resp.status_code
        except Exception as exc:
            _report_error(
                saga="order-fulfillment",
                step="get-outsystems-shipment",
                detail=str(exc),
            )
            return jsonify({"error": "Failed to fetch OutSystems shipment"}), 502

    @app.get("/logistics/order/<string:order_id>/shipment-id")
    def get_shipment_id_for_order(order_id: str):
        shipment_id = _lookup_shipment_id(order_id)
        if shipment_id is None:
            try:
                shipment_id = lookup_shipment_id_by_order(order_id)
            except Exception as exc:
                _report_error(
                    saga="order-fulfillment",
                    step="lookup-shipment-by-order",
                    detail=str(exc),
                    order_id=order_id,
                )
                return jsonify({"error": "Failed to resolve shipment_id from OutSystems"}), 502

        if shipment_id is None:
            return jsonify({"error": "shipment_id not found for order_id"}), 404
        return jsonify({"order_id": order_id, "shipment_id": shipment_id}), 200

    register_swagger(app)
    _start_order_paid_consumer()
    return app


def _start_order_paid_consumer() -> None:
    bootstrap = os.environ.get("KAFKA_BOOTSTRAP_SERVERS", "kafka:29092")

    def loop():
        consumer = KafkaConsumer(
            "OrderPaid",
            bootstrap_servers=bootstrap,
            group_id="logistics-service-group",
            auto_offset_reset="earliest",
            enable_auto_commit=True,
            value_deserializer=_safe_kafka_json_deserialize,
        )
        logger.info("Kafka consumer started | topic=OrderPaid")
        for message in consumer:
            payload = message.value or {}
            order_id = payload.get("order_id")
            if not order_id:
                logger.warning("Skipping OrderPaid event with missing order_id")
                continue

            scheduled_datetime = _normalize_scheduled_datetime(
                payload.get("scheduled_datetime") or payload.get("fulfillment_date")
            )
            created_at = _normalize_created_at(payload.get("created_at"))
            fulfillment_method = payload.get("fulfillment_method", "COLLECTION")
            shipment_id = _resolve_shipment_id(payload, order_id)
            logger.info("OrderPaid consumed | order_id=%s", order_id)

            try:
                os_result = notify_order_paid(
                    order_id=order_id,
                    fulfillment_method=fulfillment_method,
                    scheduled_datetime=scheduled_datetime,
                    shipment_id=shipment_id,
                    created_at=created_at,
                )
                _cache_order_shipment(order_id, os_result.get("shipment_id") or shipment_id)
                logger.info(
                    "OutSystems notified for OrderPaid | order_id=%s | requested_shipment_id=%s | outsystems_shipment_id=%s",
                    order_id,
                    shipment_id,
                    os_result.get("shipment_id"),
                )
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
