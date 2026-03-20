"""
InventoryClient — HTTP client for the Inventory Service (Spring Boot, port 8080).

This service is already merged to main, so all methods are fully implemented.

Endpoints used by the saga (per scenario spec):
  PUT  /inventory/stock/transition   → move items between qty buckets
"""

import logging
import os

import requests

logger = logging.getLogger(__name__)

INVENTORY_SERVICE_URL = os.environ.get("INVENTORY_SERVICE_URL", "http://inventory-service:8080")
_TIMEOUT = 10  # seconds


class InventoryClient:

    def transition_stock(self, hold_id: str, from_bucket: str, to_bucket: str) -> dict:
        """
        PUT /inventory/stock/transition

        Moves items associated with hold_id from one qty bucket to another.
        Used by the saga to move from available_qty -> reserved_qty after payment.

        :param hold_id:     The hold ID returned during soft-hold (step 4 of scenario 1)
        :param from_bucket: Source bucket, e.g. "available_qty"
        :param to_bucket:   Destination bucket, e.g. "reserved_qty"
        :return:            {"success": True, "updated_items": [...]}
        """
        url = f"{INVENTORY_SERVICE_URL}/inventory/stock/transition"
        payload = {
            "hold_id": hold_id,
            "from_bucket": from_bucket,
            "to_bucket": to_bucket,
        }
        try:
            resp = requests.put(url, json=payload, timeout=_TIMEOUT)
            resp.raise_for_status()
            return resp.json()
        except requests.RequestException as exc:
            logger.error(
                "InventoryClient.transition_stock failed | hold_id=%s | %s",
                hold_id,
                exc,
            )
            raise
