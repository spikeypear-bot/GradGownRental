import os
import requests

ORDER_SERVICE_URL = os.environ.get("ORDER_SERVICE_URL", "http://order-service:8081")
_TIMEOUT = 10


class OrderClient:
    def update_status(self, order_id: str, status: str) -> dict:
        url = f"{ORDER_SERVICE_URL}/orders/{order_id}/status"
        resp = requests.put(url, json={"status": status}, timeout=_TIMEOUT)
        resp.raise_for_status()
        return resp.json()

    def set_damaged_items(self, order_id: str, damaged_items: list) -> dict:
        """Update the damaged_items field on an order"""
        url = f"{ORDER_SERVICE_URL}/orders/{order_id}/damage"
        resp = requests.put(url, json={"damaged_items": damaged_items}, timeout=_TIMEOUT)
        resp.raise_for_status()
        return resp.json()

    def get_order(self, order_id: str) -> dict:
        url = f"{ORDER_SERVICE_URL}/orders/{order_id}"
        resp = requests.get(url, timeout=_TIMEOUT)
        resp.raise_for_status()
        return resp.json()
