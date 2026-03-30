"""
OrderClient — HTTP client for the Order Service.

Endpoints:
  POST /orders              → initialise order record, returns order payload
  PUT  /orders/{id}/status  → update order_status
"""

import logging
import os

import requests

logger = logging.getLogger(__name__)

ORDER_SERVICE_URL = os.environ.get("ORDER_SERVICE_URL", "http://order-service:8081")
_TIMEOUT = 10  # seconds


class OrderClient:

    def create_order(
        self,
        *,
        student_name: str,
        email: str,
        phone: str,
        package_id: int,
        selected_items: list,
        rental_start_date: str,
        rental_end_date: str,
        total_amount: str,
        fulfillment_method: str,
        hold_id: str,
        deposit: float = 0.0,
    ) -> dict:
        """
        POST /orders — initialise a new order record in PENDING state.
        """
        url = f"{ORDER_SERVICE_URL}/orders"
        payload = {
            "student_name": student_name,
            "email": email,
            "phone": phone,
            "package_id": package_id,
            "selected_items": selected_items,
            "rental_start_date": rental_start_date,
            "rental_end_date": rental_end_date,
            "total_amount": total_amount,
            "fulfillment_method": fulfillment_method,
            "deposit": deposit,
            "hold_id": hold_id,
            "status": "PENDING",
        }
        try:
            resp = requests.post(url, json=payload, timeout=_TIMEOUT)
            resp.raise_for_status()
            return resp.json()
        except requests.RequestException as exc:
            logger.error("OrderClient.create_order failed: %s", exc)
            raise

    def update_status(self, order_id: str, status: str, payment_id: str | None = None) -> None:
        """
        PUT /orders/{order_id}/status — update the order's status field.
        """
        url = f"{ORDER_SERVICE_URL}/orders/{order_id}/status"
        payload = {"status": status}
        if payment_id:
            payload["payment_id"] = payment_id
        try:
            resp = requests.put(url, json=payload, timeout=_TIMEOUT)
            resp.raise_for_status()
        except requests.RequestException as exc:
            logger.error("OrderClient.update_status failed: %s", exc)
            raise
