import os
import requests

INVENTORY_SERVICE_URL = os.environ.get("INVENTORY_SERVICE_URL", "http://inventory-service:8080")
_TIMEOUT = 10


class InventoryClient:
    @staticmethod
    def _unwrap_or_raise(resp: requests.Response) -> dict:
        try:
            payload = resp.json()
        except ValueError:
            payload = None

        if not resp.ok:
            detail = None
            if isinstance(payload, dict):
                detail = payload.get("msg") or payload.get("message") or payload.get("error")
            detail = detail or resp.text or f"HTTP {resp.status_code}"
            raise requests.HTTPError(
                f"Inventory transition failed ({resp.status_code}): {detail}",
                response=resp,
            )

        if isinstance(payload, dict) and payload.get("status") != 200:
            raise RuntimeError(payload.get("msg") or "Inventory transition failed")
        return payload

    def transition_reserved_to_rented(self, items: list) -> dict:
        url = f"{INVENTORY_SERVICE_URL}/api/inventory/stock/transition"
        payload = {
            "transition": "RESERVED_TO_RENTED",
            "items": items,
        }
        resp = requests.put(url, json=payload, timeout=_TIMEOUT)
        return self._unwrap_or_raise(resp)
