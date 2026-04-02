import os
import requests

INVENTORY_SERVICE_URL = os.environ.get("INVENTORY_SERVICE_URL", "http://inventory-service:8080")
_TIMEOUT = 10


class InventoryClient:
    def transition(self, transition: str, items: list) -> dict:
        url = f"{INVENTORY_SERVICE_URL}/api/inventory/stock/transition"
        payload = {
            "transition": transition,
            "items": items,
        }
        resp = requests.put(url, json=payload, timeout=_TIMEOUT)
        resp.raise_for_status()
        return resp.json()

    def request_maintenance(self, payload: dict) -> dict:
        url = f"{INVENTORY_SERVICE_URL}/api/inventory/maintenance/request"
        resp = requests.put(url, json=payload, timeout=_TIMEOUT)
        resp.raise_for_status()
        return resp.json()
