"""
NotificationService — orchestrates message composition, adapter dispatch, and persistence.

Covers:
  • Reminder events: pickup_reminder / delivery_reminder / return_reminder
  • Order events: OrderConfirmed / OrderActivated / ReturnProcessed
"""

import logging
import os
import threading
import uuid
from datetime import datetime

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
# Each event maps to: (email_subject, email_html)
# Placeholders are filled in by the service before dispatch.

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
    NotificationEvent.ORDER_ACTIVATED: (
        "{activation_subject} for Order #{order_id}",
        "<h2>{activation_heading}</h2><p>Hi {name},</p>"
        "<p>{activation_message}</p>"
        "<p>{completion_label}: <strong>{fulfillment_date}</strong><br>"
        "Return date: <strong>{return_date}</strong></p>"
        "<h3>Gown Care &amp; Return Instructions</h3>"
        "<ul><li>Store in a cool, dry place.</li>"
        "<li>Do not wash the gown.</li>"
        "<li>Handle the gown gently and avoid dragging it on the floor.</li>"
        "<li>Return the full set on or before <strong>{return_date}</strong>.</li></ul>"
        "<p>Thank you for renting with GradGown Rental.</p>",
    ),
    NotificationEvent.COLLECTION: (
        "Reminder: Collection Scheduled for Order #{order_id}",
        "<h2>Collection Reminder</h2><p>Hi {name},</p>"
        "<p>Your gown collection for order <strong>#{order_id}</strong> is scheduled on "
        "<strong>{date}</strong>.</p>"
        "<p>Please bring your order details when collecting.</p>",
    ),
    NotificationEvent.DELIVERY: (
        "Reminder: Delivery Scheduled for Order #{order_id}",
        "<h2>Delivery Reminder</h2><p>Hi {name},</p>"
        "<p>Your gown delivery for order <strong>#{order_id}</strong> is scheduled on "
        "<strong>{date}</strong>.</p>"
        "<p>Please ensure someone is available to receive the full set.</p>",
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
        sendgrid: SendGridAdapter,
        repo: NotificationRepository,
    ):
        self._sendgrid = sendgrid
        self._repo = repo
        self._demo_mode = self._read_bool_env(
            "NOTIFICATION_DEMO_MODE",
            fallback=os.environ.get("VITE_DEMO_MODE"),
        )
        self._demo_reminder_delay_seconds = self._read_int_env(
            "NOTIFICATION_DEMO_REMINDER_DELAY_SECONDS",
            default=60,
        )

    # ------------------------------------------------------------------
    # Public entry points (called by Kafka consumers)
    # ------------------------------------------------------------------

    def handle_order_confirmed(self, payload: dict) -> None:
        """Handle order confirmation notifications."""
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
            email=payload.get("email"),
            ctx=ctx,
        )

    def handle_order_activated(self, payload: dict) -> None:
        """Handle collection/delivery completion notifications."""
        fulfillment_method = str(payload.get("fulfillment_method", "COLLECTION")).upper()
        is_delivery = fulfillment_method == "DELIVERY"
        ctx = {
            "order_id": payload["order_id"],
            "name": payload.get("student_name", "Student"),
            "activation_subject": "Delivery Completed" if is_delivery else "Collection Completed",
            "activation_heading": "Delivery Completed" if is_delivery else "Collection Completed",
            "activation_message": (
                f"Your order <strong>#{payload['order_id']}</strong> has been delivered successfully."
                if is_delivery else
                f"Your order <strong>#{payload['order_id']}</strong> has been collected successfully."
            ),
            "completion_label": "Delivered on" if is_delivery else "Collected on",
            "fulfillment_date": payload.get("fulfillment_date", "Today"),
            "return_date": payload.get("return_date", "TBD"),
        }
        self._dispatch(
            event=NotificationEvent.ORDER_ACTIVATED,
            order_id=ctx["order_id"],
            email=payload.get("email"),
            ctx=ctx,
        )
        self._schedule_demo_return_reminder_if_needed(
            order_id=ctx["order_id"],
            email=payload.get("email"),
            name=ctx["name"],
            return_date=ctx["return_date"],
        )

    def handle_return_processed(self, payload: dict) -> None:
        """Handle return completion notifications."""
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
            email=payload.get("email"),
            ctx=ctx,
        )

    def handle_pickup_reminder(self, payload: dict) -> None:
        """Handle scheduled pickup reminders."""
        ctx = {
            "order_id": payload["order_id"],
            "name": payload.get("student_name", "Student"),
            "date": payload.get("fulfillment_date", "tomorrow"),
            "return_date": payload.get("return_date", "TBD"),
        }
        self._dispatch(
            event=NotificationEvent.COLLECTION,
            order_id=ctx["order_id"],
            email=payload.get("email"),
            ctx=ctx,
        )

    def handle_delivery_reminder(self, payload: dict) -> None:
        """Handle scheduled delivery reminders."""
        ctx = {
            "order_id": payload["order_id"],
            "name": payload.get("student_name", "Student"),
            "date": payload.get("fulfillment_date", "tomorrow"),
            "return_date": payload.get("return_date", "TBD"),
        }
        self._dispatch(
            event=NotificationEvent.DELIVERY,
            order_id=ctx["order_id"],
            email=payload.get("email"),
            ctx=ctx,
        )

    def handle_return_reminder(self, payload: dict) -> None:
        """Handle scheduled return reminders."""
        ctx = {
            "order_id": payload["order_id"],
            "name": payload.get("student_name", "Student"),
            "return_date": payload.get("return_date", "tomorrow"),
        }
        self._dispatch(
            event=NotificationEvent.RETURN,
            order_id=ctx["order_id"],
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
        email: str | None,
    ) -> None:
        """Send email notifications for a given event."""
        if email:
            if self._should_delay_reminder_for_demo(event):
                self._schedule_email(event, order_id, email, ctx)
                return
            self._send_email(event, order_id, email, ctx)

    def _should_delay_reminder_for_demo(self, event: NotificationEvent) -> bool:
        return self._demo_mode and event in {
            NotificationEvent.COLLECTION,
            NotificationEvent.DELIVERY,
            NotificationEvent.RETURN,
        }

    def _schedule_email(
        self,
        event: NotificationEvent,
        order_id: str,
        email: str,
        ctx: dict,
    ) -> None:
        delay_seconds = max(self._demo_reminder_delay_seconds, 0)
        if delay_seconds == 0:
            self._send_email(event, order_id, email, ctx)
            return

        timer = threading.Timer(
            delay_seconds,
            self._send_email,
            args=(event, order_id, email, ctx),
        )
        timer.daemon = True
        timer.start()
        logger.info(
            "Scheduled demo reminder email | event=%s | order=%s | delay_seconds=%s",
            event.value,
            order_id,
            delay_seconds,
        )

    def _schedule_demo_return_reminder_if_needed(
        self,
        order_id: str,
        email: str | None,
        name: str,
        return_date: str,
    ) -> None:
        if not self._demo_mode or not email:
            return
        self._schedule_email(
            event=NotificationEvent.RETURN,
            order_id=order_id,
            email=email,
            ctx={
                "order_id": order_id,
                "name": name,
                "return_date": return_date or "tomorrow",
            },
        )

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
        result = self._simulate_demo_success_if_needed(event, order_id, result)
        status = NotificationStatus.SENT if result["success"] else NotificationStatus.FAILED
        self._repo.update_status(
            log.id,
            status=status,
            external_id=result.get("external_id"),
            error_message=result.get("error"),
        )
        logger.info("Email %s | event=%s | order=%s", status.value, event.value, order_id)

    @staticmethod
    def _read_bool_env(name: str, fallback: str | None = None) -> bool:
        raw = os.environ.get(name, fallback or "")
        return str(raw).strip().lower() in {"1", "true", "yes", "on"}

    @staticmethod
    def _read_int_env(name: str, default: int) -> int:
        raw = os.environ.get(name)
        if raw is None:
            return default
        try:
            return int(raw)
        except ValueError:
            logger.warning("Invalid integer env for %s: %s. Using default=%s", name, raw, default)
            return default

    def _simulate_demo_success_if_needed(
        self,
        event: NotificationEvent,
        order_id: str,
        result: dict,
    ) -> dict:
        if result.get("success") or not self._demo_mode:
            return result

        error_text = str(result.get("error") or "").lower()
        quota_limited = (
            "maximum credits exceeded" in error_text or
            "exceeded your messaging limits" in error_text
        )
        if not quota_limited:
            return result

        simulated = {
            "success": True,
            "external_id": f"demo-simulated-{uuid.uuid4()}",
            "error": f"Simulated success in demo mode after provider limit: {result.get('error')}",
        }
        logger.warning(
            "Simulating email success in demo mode | event=%s | order=%s | provider_error=%s",
            event.value,
            order_id,
            result.get("error"),
        )
        return simulated
