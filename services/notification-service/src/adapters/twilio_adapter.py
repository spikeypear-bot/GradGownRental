"""
TwilioAdapter — Anti-Corruption Layer for Twilio SMS API.

Shields internal domain logic from Twilio SDK changes.
Transforms vendor-specific responses into a standardised internal dict.
"""

import os
import logging
from typing import Optional

from twilio.rest import Client
from twilio.base.exceptions import TwilioRestException

logger = logging.getLogger(__name__)


class TwilioAdapter:
    """
    Wraps the Twilio REST client.
    All Twilio-specific concepts (MessageInstance, SID, etc.) stay inside this class.
    Callers receive a plain dict: {"success": bool, "external_id": str, "error": str|None}
    """

    def __init__(
        self,
        account_sid: Optional[str] = None,
        auth_token: Optional[str] = None,
        from_number: Optional[str] = None,
    ):
        self._account_sid = account_sid or os.environ["TWILIO_ACCOUNT_SID"]
        self._auth_token = auth_token or os.environ["TWILIO_AUTH_TOKEN"]
        self._from_number = from_number or os.environ["TWILIO_FROM_NUMBER"]
        self._client = Client(self._account_sid, self._auth_token)

    def send_sms(self, to: str, body: str) -> dict:
        """
        Send an SMS via Twilio.

        :param to:   E.164 recipient phone number, e.g. "+6591234567"
        :param body: SMS body text (max ~1600 chars)
        :return:     {"success": True,  "external_id": "<MessageSID>", "error": None}
                     {"success": False, "external_id": None,           "error": "<reason>"}
        """
        try:
            message = self._client.messages.create(
                body=body,
                from_=self._from_number,
                to=to,
            )
            logger.info("Twilio SMS sent | SID=%s | to=%s", message.sid, to)
            return {"success": True, "external_id": message.sid, "error": None}

        except TwilioRestException as exc:
            logger.error("Twilio SMS failed | to=%s | code=%s | msg=%s", to, exc.code, exc.msg)
            return {"success": False, "external_id": None, "error": str(exc.msg)}

        except Exception as exc:  # noqa: BLE001
            logger.exception("Unexpected Twilio error | to=%s", to)
            return {"success": False, "external_id": None, "error": str(exc)}
