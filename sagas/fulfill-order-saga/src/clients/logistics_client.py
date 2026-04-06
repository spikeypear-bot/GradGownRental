import os
import requests

LOGISTICS_SERVICE_URL = os.environ.get("LOGISTICS_SERVICE_URL", "http://logistics-service:5004")
_TIMEOUT = 10


class LogisticsClient:
    def get_shipment_id_by_order(self, order_id: str) -> str | None:
        url = f"{LOGISTICS_SERVICE_URL}/logistics/order/{order_id}/shipment-id"
        resp = requests.get(url, timeout=_TIMEOUT)
        if resp.status_code == 404:
            return None
        resp.raise_for_status()
        payload = resp.json() if resp.content else {}
        shipment_id = payload.get("shipment_id")
        if shipment_id is None:
            return None
        return str(shipment_id)

    def update_status(self, shipment_id: str, tracking_status: str, order_id: str) -> dict:
        url = f"{LOGISTICS_SERVICE_URL}/logistics/{shipment_id}/status"
        payload = {
            "tracking_status": tracking_status,
            "order_id": order_id,
        }
        resp = requests.put(url, json=payload, timeout=_TIMEOUT)
        resp.raise_for_status()
        return resp.json()
