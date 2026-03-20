"""
SendGridAdapter — Anti-Corruption Layer for SendGrid Email API.

Shields internal domain logic from SendGrid SDK changes.
Transforms vendor-specific responses into a standardised internal dict.
"""

import os
import logging
from typing import Optional

from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from python_http_client.exceptions import HTTPError

logger = logging.getLogger(__name__)


class SendGridAdapter:
    """
    Wraps the SendGrid Python SDK.
    All SendGrid-specific concepts stay inside this class.
    Callers receive a plain dict: {"success": bool, "external_id": str|None, "error": str|None}
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        from_email: Optional[str] = None,
        from_name: str = "GradGown Rental",
    ):
        self._api_key = api_key or os.environ["SENDGRID_API_KEY"]
        self._from_email = from_email or os.environ["SENDGRID_FROM_EMAIL"]
        self._from_name = from_name
        self._client = SendGridAPIClient(self._api_key)

    def send_email(self, to: str, subject: str, html_content: str) -> dict:
        """
        Send a transactional email via SendGrid.

        :param to:           Recipient email address
        :param subject:      Email subject line
        :param html_content: HTML body of the email
        :return:             {"success": True,  "external_id": "<X-Message-Id>", "error": None}
                             {"success": False, "external_id": None,             "error": "<reason>"}
        """
        message = Mail(
            from_email=(self._from_email, self._from_name),
            to_emails=to,
            subject=subject,
            html_content=html_content,
        )
        try:
            response = self._client.send(message)
            # SendGrid returns the message ID in the response headers
            external_id = response.headers.get("X-Message-Id")
            logger.info(
                "SendGrid email sent | message_id=%s | to=%s | status=%s",
                external_id,
                to,
                response.status_code,
            )
            return {"success": True, "external_id": external_id, "error": None}

        except HTTPError as exc:
            logger.error("SendGrid HTTP error | to=%s | status=%s | body=%s", to, exc.status_code, exc.body)
            return {"success": False, "external_id": None, "error": str(exc.body)}

        except Exception as exc:  # noqa: BLE001
            logger.exception("Unexpected SendGrid error | to=%s", to)
            return {"success": False, "external_id": None, "error": str(exc)}
