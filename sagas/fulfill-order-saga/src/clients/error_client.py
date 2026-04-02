import os
import requests

ERROR_SERVICE_URL = os.environ.get("ERROR_SERVICE_URL", "http://error-service:5002")
_TIMEOUT = 5


class ErrorClient:
    def log_error(self, saga: str, step: str, order_id: str, detail: str) -> None:
        url = f"{ERROR_SERVICE_URL}/errors"
        requests.post(url, json={
            "saga": saga,
            "step": step,
            "order_id": order_id,
            "detail": detail,
        }, timeout=_TIMEOUT)
