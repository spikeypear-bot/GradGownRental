"""
PaymentClient — HTTP client for the Payment Service.

Endpoints:
  POST /payments → authorise transaction, returns {payment_id}
"""

import logging
import os

import requests

logger = logging.getLogger(__name__)

PAYMENT_SERVICE_URL = os.environ.get("PAYMENT_SERVICE_URL", "http://payment-service:3000")
_TIMEOUT = 15  # seconds — slightly longer to account for Stripe round-trip


class PaymentClient:

    def create_checkout_intent(self, amount: str) -> dict:
        """
        POST /api/payment/checkout — create a Stripe PaymentIntent and return client_secret.

        Returns: {"client_secret": str}
        """
        url = f"{PAYMENT_SERVICE_URL}/api/payment/checkout"
        try:
            resp = requests.post(url, json={"amount": float(amount)}, timeout=_TIMEOUT)
            resp.raise_for_status()
            return resp.json()
        except requests.RequestException as exc:
            logger.error("PaymentClient.create_checkout_intent failed: %s", exc)
            raise

    def authorise_payment(self, order_id: str, total_amount: str, payment_details: dict) -> dict:
        """
        POST /payments — charge the student via the Payment Service → Stripe Adapter.

        Returns: {"payment_id": str}
        """
        url = f"{PAYMENT_SERVICE_URL}/api/payment/payments"
        payload = {
            "order_id": order_id,
            "total_amount": total_amount,
            "payment_details": payment_details,
        }
        try:
            resp = requests.post(url, json=payload, timeout=_TIMEOUT)
            resp.raise_for_status()
            return resp.json()
        except requests.RequestException as exc:
            logger.error("PaymentClient.authorise_payment failed: %s", exc)
            raise
