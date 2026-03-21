"""
ErrorClient — HTTP client for the Error Service.

Called by the saga on any synchronous step failure (E1 in scenario spec).

Endpoint:
  POST /errors  → log a failure event with context
"""

import logging
import os

import requests

logger = logging.getLogger(__name__)

ERROR_SERVICE_URL = os.environ.get("ERROR_SERVICE_URL", "http://error-service:5002")
_TIMEOUT = 5  # short — error logging must never block the failure path


class ErrorClient:

    def log_error(self, saga: str, step: str, order_id: str | None, detail: str) -> None:
        """
        POST /errors

        Fire-and-forget style — we log locally if the error service itself
        is unavailable, so no cascading failures.

        :param saga:     Saga name, e.g. "place-order-saga"
        :param step:     Step that failed, e.g. "authorise_payment"
        :param order_id: Associated order ID (may be None if failure is pre-order)
        :param detail:   Human-readable error description / exception message
        """
        url = f"{ERROR_SERVICE_URL}/errors"
        payload = {
            "saga": saga,
            "step": step,
            "order_id": order_id,
            "detail": detail,
        }
        try:
            resp = requests.post(url, json=payload, timeout=_TIMEOUT)
            resp.raise_for_status()
            logger.info("Error logged to error-service | step=%s | order_id=%s", step, order_id)
        except requests.RequestException as exc:
            # Never let error-service failure mask the original error
            logger.error(
                "Could not reach error-service | step=%s | order_id=%s | reason=%s",
                step, order_id, exc,
            )
