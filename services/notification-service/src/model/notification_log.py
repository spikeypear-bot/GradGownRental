"""
NotificationLog model — represents a record of every notification sent or attempted.
Persisted to PostgreSQL via the repository layer.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional


class NotificationChannel(str, Enum):
    SMS = "SMS"
    EMAIL = "EMAIL"


class NotificationStatus(str, Enum):
    SENT = "SENT"
    FAILED = "FAILED"
    PENDING = "PENDING"


class NotificationEvent(str, Enum):
    # Canonical 4-stage labels (requested lifecycle)
    CONFIRMATION = "CONFIRMATION"
    COLLECTION = "COLLECTION"
    RETURN = "RETURN"
    DEPOSIT = "DEPOSIT"

    # Backward-compatible aliases currently used by topics/events
    PICKUP_REMINDER = "pickup_reminder"
    RETURN_REMINDER = "return_reminder"
    ORDER_CONFIRMED = "OrderConfirmed"
    ORDER_ACTIVATED = "OrderActivated"
    RETURN_PROCESSED = "ReturnProcessed"


@dataclass
class NotificationLog:
    order_id: str
    event_type: NotificationEvent
    channel: NotificationChannel
    recipient: str          # recipient email address
    message_body: str
    status: NotificationStatus = NotificationStatus.PENDING
    external_id: Optional[str] = None   # SendGrid message ID
    error_message: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    id: Optional[int] = None            # set after DB insert

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "order_id": self.order_id,
            "event_type": self.event_type.value,
            "channel": self.channel.value,
            "recipient": self.recipient,
            "message_body": self.message_body,
            "status": self.status.value,
            "external_id": self.external_id,
            "error_message": self.error_message,
            "created_at": self.created_at.isoformat(),
        }
