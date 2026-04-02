import os
import requests

LOGISTICS_SERVICE_URL = os.environ.get("LOGISTICS_SERVICE_URL", "http://logistics-service:5004")
_TIMEOUT = 10


class LogisticsClient:
    def update_status(self, shipment_id: str, tracking_status: str, order_id: str) -> dict:
        url = f"{LOGISTICS_SERVICE_URL}/logistics/{shipment_id}/status"
        payload = {
            "tracking_status": tracking_status,
            "order_id": order_id,
        }
        resp = requests.put(url, json=payload, timeout=_TIMEOUT)
        resp.raise_for_status()
        return resp.json()
