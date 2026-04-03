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
# Email templates for notifications
# Placeholders are filled in by the service before dispatch.

_EMAIL_TEMPLATES: dict[NotificationEvent, tuple[str, str]] = {
    # (subject, html_body)
    NotificationEvent.ORDER_CONFIRMED: (
        "Your GradGown Order #{order_id} is Confirmed!",
        "<h2>Order Confirmed</h2><p>Hi {name},</p>"
        "<p>Your order <strong>#{order_id}</strong> has been confirmed.</p>"
        "<p>Fulfillment method: <strong>{fulfillment_method}</strong><br>"
        "Date: <strong>{date}</strong></p>"
        "<p>Total charged: <strong>${amount}</strong></p>"
        "<p>Thank you for choosing GradGown Rental!</p>",
    ),
    NotificationEvent.RETURN_PROCESSED: (
        "Return Complete — Refund Issued for Order #{order_id}",
        "<h2>Return Processed</h2><p>Hi {name},</p>"
        "<p>Your return for order <strong>#{order_id}</strong> has been processed.</p>"
        "<p>Refund amount: <strong>${refund_amount}</strong><br>"
        "Expected arrival: 5–7 business days.</p>"
        "<p>Thank you for using GradGown Rental!</p>",
    ),
    NotificationEvent.RETURN_REMINDER: (
        "Reminder: GradGown Return Due Tomorrow — Order #{order_id}",
        "<h2>Return Reminder</h2><p>Hi {name},</p>"
        "<p>This is a reminder that your gown return for order "
        "<strong>#{order_id}</strong> is due <strong>tomorrow</strong>. "
        "Please ensure the gown is clean and packed.</p>",
    ),
    NotificationEvent.PICKUP_REMINDER: (
        "Reminder: GradGown Pickup Tomorrow — Order #{order_id}",
        "<h2>Pickup Reminder</h2><p>Hi {name},</p>"
        "<p>This is a reminder that your gown collection for order "
        "<strong>#{order_id}</strong> is scheduled for <strong>tomorrow</strong>. "
        "Please be available to pick up your gown.</p>",
    ),
}

_EVENT_CHANNELS: dict[NotificationEvent, set[NotificationChannel]] = {
    NotificationEvent.ORDER_CONFIRMED: {NotificationChannel.EMAIL},
    NotificationEvent.RETURN_PROCESSED: {NotificationChannel.EMAIL},
    NotificationEvent.RETURN_REMINDER: {NotificationChannel.EMAIL},
    NotificationEvent.PICKUP_REMINDER: {NotificationChannel.EMAIL},
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
        }
        self._dispatch(
            event=NotificationEvent.ORDER_CONFIRMED,
            order_id=ctx["order_id"],
            phone=payload.get("phone"),
            email=payload.get("email"),
            ctx=ctx,
        )

    def handle_order_activated(self, payload: dict) -> None:
        """Scenario 2b — fires after OrderActivated event."""
        ctx = {
            "order_id": payload["order_id"],
            "name": payload.get("student_name", "Student"),
            "return_date": payload.get("return_date", "TBD"),
        }
        self._dispatch(
            event=NotificationEvent.ORDER_ACTIVATED,
            order_id=ctx["order_id"],
            phone=payload.get("phone"),
            email=payload.get("email"),
            ctx=ctx,
        )

    def handle_return_processed(self, payload: dict) -> None:
        """Scenario 2b — fires after ReturnProcessed event."""
        ctx = {
            "order_id": payload["order_id"],
            "name": payload.get("student_name", "Student"),
            "refund_amount": payload.get("refund_amount", "0.00"),
        }
        self._dispatch(
            event=NotificationEvent.RETURN_PROCESSED,
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
        }
        self._dispatch(
            event=NotificationEvent.PICKUP_REMINDER,
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
        }
        self._dispatch(
            event=NotificationEvent.RETURN_REMINDER,
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
        """Send the configured notification channels for a given event."""
        channels = _EVENT_CHANNELS[event]
        if email and NotificationChannel.EMAIL in channels:
            self._send_email(event, order_id, email, ctx)

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
