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

    def transition(self, transition: str, items: list, extra_payload: dict | None = None) -> dict:
        url = f"{INVENTORY_SERVICE_URL}/api/inventory/stock/transition"
        payload = {
            "transition": transition,
            "items": items,
        }
        if extra_payload:
            payload.update(extra_payload)
        resp = requests.put(url, json=payload, timeout=_TIMEOUT)
        return self._unwrap_or_raise(resp)

    def request_maintenance(self, payload: dict) -> dict:
        url = f"{INVENTORY_SERVICE_URL}/api/inventory/maintenance/request"
        resp = requests.put(url, json=payload, timeout=_TIMEOUT)
        return self._unwrap_or_raise(resp)
