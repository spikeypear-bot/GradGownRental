"""
PaymentClient — HTTP client for the Payment Service.

TODO: Replace stub implementations with real HTTP calls once the
      payment-service branch merges to main.

Expected endpoints (per scenario spec):
  POST /payments         → authorise transaction, returns {payment_id}
"""

import logging
import os

import requests

logger = logging.getLogger(__name__)

PAYMENT_SERVICE_URL = os.environ.get("PAYMENT_SERVICE_URL", "http://payment-service:3000")
_TIMEOUT = 15  # seconds — slightly longer to account for Stripe round-trip


class PaymentClient:

    def authorise_payment(self, order_id: str, total_amount: str, payment_details: dict) -> dict:
        """
        POST /payments — charge the student via the Payment Service → Stripe Adapter.

        Returns: {"payment_id": str}

        TODO: Uncomment the real implementation below once payment-service is merged.
        """
        # --- STUB (remove when payment-service is live) ---
        logger.warning("[STUB] PaymentClient.authorise_payment called — returning mock payment_id")
        return {"payment_id": "STUB-PAY-001"}

        # --- REAL IMPLEMENTATION (uncomment when ready) ---
        # url = f"{PAYMENT_SERVICE_URL}/payments"
        # payload = {
        #     "order_id": order_id,
        #     "total_amount": total_amount,
        #     "payment_details": payment_details,
        # }
        # try:
        #     resp = requests.post(url, json=payload, timeout=_TIMEOUT)
        #     resp.raise_for_status()
        #     return resp.json()
        # except requests.RequestException as exc:
        #     logger.error("PaymentClient.authorise_payment failed: %s", exc)
        #     raise
