"""
InventoryClient — HTTP client for the Inventory Service (Spring Boot, port 8080).

This service is already merged to main, so all methods are fully implemented.

Endpoints used by the saga:
  PUT /api/inventory/stock/transition → move available stock into reserved stock
"""

import logging
import os

import requests

logger = logging.getLogger(__name__)

INVENTORY_SERVICE_URL = os.environ.get("INVENTORY_SERVICE_URL", "http://inventory-service:8080")
_TIMEOUT = 10  # seconds


class InventoryClient:

    def reserve_items(self, hold_id: str, items: list) -> dict:
        """
        PUT /api/inventory/stock/transition

        Reserves items associated with hold_id after successful payment.

        :param hold_id: soft-hold ID returned from /softlock
        :param items: list of {modelId, qty, chosenDate}
        """
        url = f"{INVENTORY_SERVICE_URL}/api/inventory/stock/transition"
        payload = {
            "transition": "AVAILABLE_TO_RESERVED",
            "holdId": hold_id,
            "items": items,
        }
        try:
            resp = requests.put(url, json=payload, timeout=_TIMEOUT)
            resp.raise_for_status()
            return resp.json()
        except requests.RequestException as exc:
            logger.error(
                "InventoryClient.reserve_items failed | hold_id=%s | %s",
                hold_id,
                exc,
            )
            raise
