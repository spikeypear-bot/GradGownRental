import os
import requests

PAYMENT_SERVICE_URL = os.environ.get("PAYMENT_SERVICE_URL", "http://payment-service:3000")
_TIMEOUT = 15


class PaymentClient:
    def refund(self, order_id: str, payment_id: str, refundable_amount: float) -> dict:
        url = f"{PAYMENT_SERVICE_URL}/payments/refunds"
        payload = {
            "order_id": order_id,
            "payment_id": payment_id,
            "refundable_amount": f"{refundable_amount:.2f}",
        }
        resp = requests.post(url, json=payload, timeout=_TIMEOUT)
        resp.raise_for_status()
        return resp.json()
