"""
OrderClient — HTTP client for the Order Service.

TODO: Replace stub implementations with real HTTP calls once the
      order-service branch merges to main.

Expected endpoints (per scenario spec):
  POST /orders           → initialise order record, returns {order_id, order_status}
  PUT  /orders/{id}/status → update order_status
"""

import logging
import os

import requests

logger = logging.getLogger(__name__)

ORDER_SERVICE_URL = os.environ.get("ORDER_SERVICE_URL", "http://order-service:8081")
_TIMEOUT = 10  # seconds


class OrderClient:

    def create_order(self, hold_id: str, selected_packages: list, fulfillment_method: str, total_deposit: float = 0.0) -> dict:
        """
        POST /orders — initialise a new order record.
        
        :param hold_id: inventory hold ID
        :param selected_packages: list of selected items with deposits
        :param fulfillment_method: 'COLLECTION' or 'DELIVERY'
        :param total_deposit: sum of deposits from all selected items
        
        Returns: {"order_id": str, "order_status": "PENDING"}

        TODO: Uncomment the real implementation below once order-service is merged.
        """
        # --- STUB (remove when order-service is live) ---
        logger.warning("[STUB] OrderClient.create_order called — returning mock order_id")
        return {"order_id": "STUB-ORDER-001", "order_status": "PENDING"}

        # --- REAL IMPLEMENTATION (uncomment when ready) ---
        # url = f"{ORDER_SERVICE_URL}/orders"
        # payload = {
        #     "hold_id": hold_id,
        #     "selected_packages": selected_packages,
        #     "fulfillment_method": fulfillment_method,
        #     "deposit": total_deposit,
        # }
        # try:
        #     resp = requests.post(url, json=payload, timeout=_TIMEOUT)
        #     resp.raise_for_status()
        #     return resp.json()
        # except requests.RequestException as exc:
        #     logger.error("OrderClient.create_order failed: %s", exc)
        #     raise

    def update_status(self, order_id: str, status: str) -> None:
        """
        PUT /orders/{order_id}/status — update the order's status field.

        TODO: Uncomment the real implementation below once order-service is merged.
        """
        # --- STUB (remove when order-service is live) ---
        logger.warning("[STUB] OrderClient.update_status called | order_id=%s status=%s", order_id, status)
        return

        # --- REAL IMPLEMENTATION (uncomment when ready) ---
        # url = f"{ORDER_SERVICE_URL}/orders/{order_id}/status"
        # try:
        #     resp = requests.put(url, json={"status": status}, timeout=_TIMEOUT)
        #     resp.raise_for_status()
        # except requests.RequestException as exc:
        #     logger.error("OrderClient.update_status failed: %s", exc)
        #     raise
