"""
NotificationService — orchestrates message composition, adapter dispatch, and persistence.

Covers:
  • Scenario 2a: pickup_reminder / return_reminder (triggered by Kafka consumer)
  • Scenario 2b: OrderConfirmed / OrderActivated / ReturnProcessed (event-driven)
"""

import logging
from datetime import datetime

from adapters.twilio_adapter import TwilioAdapter
from adapters.sendgrid_adapter import SendGridAdapter
from model.notification_log import (
    NotificationChannel,
    NotificationEvent,
    NotificationLog,
    NotificationStatus,
)
from repository.notification_repository import NotificationRepository

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Message templates
# ---------------------------------------------------------------------------
# Each event maps to: (sms_body, email_subject, email_html)
# Placeholders are filled in by the service before dispatch.

_SMS_TEMPLATES: dict[NotificationEvent, str] = {
    NotificationEvent.CONFIRMATION: "Hi {name}, your GradGown order #{order_id} is confirmed! "
                                    "Collection/delivery is on {date}.",
    NotificationEvent.COLLECTION:   "Reminder: Your GradGown collection for order #{order_id} is "
                                    "scheduled for {date}. Please be available.",
    NotificationEvent.RETURN:       "Reminder: Your GradGown return for order #{order_id} is due on "
                                    "{return_date}. Please prepare the gown.",
    NotificationEvent.DEPOSIT:      "Hi {name}, return for order #{order_id} is complete. "
                                    "{deposit_summary}",
}

_EMAIL_TEMPLATES: dict[NotificationEvent, tuple[str, str]] = {
    # (subject, html_body)
    NotificationEvent.CONFIRMATION: (
        "Your GradGown Order #{order_id} is Confirmed!",
        "<h2>Order Confirmed</h2><p>Hi {name},</p>"
        "<p>Your order <strong>#{order_id}</strong> has been confirmed.</p>"
        "<p>Fulfillment method: <strong>{fulfillment_method}</strong><br>"
        "Date: <strong>{date}</strong></p>"
        "<p>Total charged: <strong>${amount}</strong></p>"
        "<p>Thank you for choosing GradGown Rental!</p>",
    ),
    NotificationEvent.COLLECTION: (
        "Reminder: Collection Scheduled for Order #{order_id}",
        "<h2>Collection Reminder</h2><p>Hi {name},</p>"
        "<p>Your gown collection for order <strong>#{order_id}</strong> is scheduled on "
        "<strong>{date}</strong>.</p>"
        "<p>Please bring your order details when collecting.</p>"
        "<h3>Gown Care Instructions</h3>"
        "<ul><li>Store in a cool, dry place.</li>"
        "<li>Do not machine wash — dry clean only.</li>"
        "<li>Return on or before <strong>{return_date}</strong>.</li></ul>",
    ),
    NotificationEvent.DEPOSIT: (
        "Return Complete — Deposit Update for Order #{order_id}",
        "<h2>Return Processed</h2><p>Hi {name},</p>"
        "<p>Your return for order <strong>#{order_id}</strong> has been processed.</p>"
        "<p>{deposit_summary}</p>"
        "<p>Original deposit: <strong>${original_deposit}</strong><br>"
        "Damage deduction: <strong>${damage_fee}</strong><br>"
        "Refund amount: <strong>${refund_amount}</strong><br>"
        "Expected arrival: 5–7 business days.</p>"
        "<p>Thank you for using GradGown Rental!</p>",
    ),
    NotificationEvent.RETURN: (
        "Reminder: GradGown Return Due Soon — Order #{order_id}",
        "<h2>Return Reminder</h2><p>Hi {name},</p>"
        "<p>This is a reminder that your gown return for order "
        "<strong>#{order_id}</strong> is due on <strong>{return_date}</strong>. "
        "Please ensure the gown is clean and packed.</p>",
    ),
}


class NotificationService:
    def __init__(
        self,
        twilio: TwilioAdapter,
        sendgrid: SendGridAdapter,
        repo: NotificationRepository,
    ):
        self._twilio = twilio
        self._sendgrid = sendgrid
        self._repo = repo

    # ------------------------------------------------------------------
    # Public entry points (called by Kafka consumers)
    # ------------------------------------------------------------------

    def handle_order_confirmed(self, payload: dict) -> None:
        """Scenario 2b — fires after OrderConfirmed event."""
        ctx = {
            "order_id": payload["order_id"],
            "name": payload.get("student_name", "Student"),
            "date": payload.get("fulfillment_date", "TBD"),
            "fulfillment_method": payload.get("fulfillment_method", "N/A"),
            "amount": payload.get("total_amount", "0.00"),
            "return_date": payload.get("return_date", "TBD"),
        }
        self._dispatch(
            event=NotificationEvent.CONFIRMATION,
            order_id=ctx["order_id"],
            phone=payload.get("phone"),
            email=payload.get("email"),
            ctx=ctx,
        )

    def handle_order_activated(self, payload: dict) -> None:
        """Order activation does not emit one of the required four email stages."""
        ctx = {
            "order_id": payload["order_id"],
            "name": payload.get("student_name", "Student"),
            "return_date": payload.get("return_date", "TBD"),
        }
        logger.info("Skipping OrderActivated notification for 4-stage lifecycle | order_id=%s", ctx["order_id"])

    def handle_return_processed(self, payload: dict) -> None:
        """Scenario 2b — fires after ReturnProcessed event."""
        has_damage = bool(payload.get("has_damage"))
        damage_fee = payload.get("damage_fee", "0.00")
        refundable_amount = payload.get("refund_amount", "0.00")
        original_deposit = payload.get("original_deposit", "0.00")

        if has_damage:
            deposit_summary = (
                f"A damage deduction of ${damage_fee} was applied. "
                f"Your refundable deposit is ${refundable_amount}."
            )
        else:
            deposit_summary = f"Your full deposit refund of ${refundable_amount} is being processed."

        ctx = {
            "order_id": payload["order_id"],
            "name": payload.get("student_name", "Student"),
            "refund_amount": refundable_amount,
            "original_deposit": original_deposit,
            "damage_fee": damage_fee,
            "deposit_summary": deposit_summary,
        }
        self._dispatch(
            event=NotificationEvent.DEPOSIT,
            order_id=ctx["order_id"],
            phone=payload.get("phone"),
            email=payload.get("email"),
            ctx=ctx,
        )

    def handle_pickup_reminder(self, payload: dict) -> None:
        """Scenario 2a — scheduled pickup/collection reminder."""
        ctx = {
            "order_id": payload["order_id"],
            "name": payload.get("student_name", "Student"),
            "date": payload.get("fulfillment_date", "tomorrow"),
            "return_date": payload.get("return_date", "TBD"),
        }
        self._dispatch(
            event=NotificationEvent.COLLECTION,
            order_id=ctx["order_id"],
            phone=payload.get("phone"),
            email=payload.get("email"),
            ctx=ctx,
        )

    def handle_return_reminder(self, payload: dict) -> None:
        """Scenario 2a — scheduled return reminder."""
        ctx = {
            "order_id": payload["order_id"],
            "name": payload.get("student_name", "Student"),
            "return_date": payload.get("return_date", "tomorrow"),
        }
        self._dispatch(
            event=NotificationEvent.RETURN,
            order_id=ctx["order_id"],
            phone=payload.get("phone"),
            email=payload.get("email"),
            ctx=ctx,
        )

    # ------------------------------------------------------------------
    # Internal dispatch
    # ------------------------------------------------------------------

    def _dispatch(
        self,
        event: NotificationEvent,
        order_id: str,
        ctx: dict,
        phone: str | None,
        email: str | None,
    ) -> None:
        """Send SMS (Twilio) and email (SendGrid) for a given event."""
        if phone:
            self._send_sms(event, order_id, phone, ctx)
        if email:
            self._send_email(event, order_id, email, ctx)

    def _send_sms(
        self,
        event: NotificationEvent,
        order_id: str,
        phone: str,
        ctx: dict,
    ) -> None:
        body = _SMS_TEMPLATES[event].format(**ctx)
        log = NotificationLog(
            order_id=order_id,
            event_type=event,
            channel=NotificationChannel.SMS,
            recipient=phone,
            message_body=body,
            created_at=datetime.utcnow(),
        )
        log = self._repo.save(log)

        result = self._twilio.send_sms(to=phone, body=body)
        status = NotificationStatus.SENT if result["success"] else NotificationStatus.FAILED
        self._repo.update_status(
            log.id,
            status=status,
            external_id=result.get("external_id"),
            error_message=result.get("error"),
        )
        logger.info("SMS %s | event=%s | order=%s", status.value, event.value, order_id)

    def _send_email(
        self,
        event: NotificationEvent,
        order_id: str,
        email: str,
        ctx: dict,
    ) -> None:
        subject_tpl, html_tpl = _EMAIL_TEMPLATES[event]
        subject = subject_tpl.format(**ctx)
        html = html_tpl.format(**ctx)

        log = NotificationLog(
            order_id=order_id,
            event_type=event,
            channel=NotificationChannel.EMAIL,
            recipient=email,
            message_body=subject,
            created_at=datetime.utcnow(),
        )
        log = self._repo.save(log)

        result = self._sendgrid.send_email(to=email, subject=subject, html_content=html)
        status = NotificationStatus.SENT if result["success"] else NotificationStatus.FAILED
        self._repo.update_status(
            log.id,
            status=status,
            external_id=result.get("external_id"),
            error_message=result.get("error"),
        )
        logger.info("Email %s | event=%s | order=%s", status.value, event.value, order_id)
