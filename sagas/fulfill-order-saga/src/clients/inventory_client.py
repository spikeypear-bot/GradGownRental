import os
import requests

INVENTORY_SERVICE_URL = os.environ.get("INVENTORY_SERVICE_URL", "http://inventory-service:8080")
_TIMEOUT = 10


class InventoryClient:
    def transition_reserved_to_rented(self, items: list) -> dict:
        url = f"{INVENTORY_SERVICE_URL}/api/inventory/stock/transition"
        payload = {
            "transition": "RESERVED_TO_RENTED",
            "items": items,
        }
        resp = requests.put(url, json=payload, timeout=_TIMEOUT)
        resp.raise_for_status()
        return resp.json()
