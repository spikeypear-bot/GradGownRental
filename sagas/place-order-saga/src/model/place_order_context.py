"""
PlaceOrderContext — immutable-ish context object threaded through every saga step.

Populated incrementally as each step succeeds.
The saga service reads/writes this object; it is never persisted directly —
individual downstream services own their own records.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


class SagaStatus(str, Enum):
    STARTED = "STARTED"
    ORDER_INITIALISED = "ORDER_INITIALISED"
    PAYMENT_AUTHORISED = "PAYMENT_AUTHORISED"
    ORDER_CONFIRMED = "ORDER_CONFIRMED"
    INVENTORY_TRANSITIONED = "INVENTORY_TRANSITIONED"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


@dataclass
class PlaceOrderContext:
    # --- Inputs (provided by caller) ---
    hold_id: str                    # soft-hold ID from Inventory Service
    selected_packages: list         # list of package dicts from soft-hold (includes deposit info)
    fulfillment_method: str         # 'COLLECTION' | 'DELIVERY'
    payment_details: dict           # passed straight through to Payment Service

    # Student contact info — needed by Notification Service via Kafka
    student_name: str
    phone: str
    email: str
    fulfillment_date: str           # ISO date string
    return_date: str                # ISO date string
    total_amount: str               # string, e.g. "125.00" (rental + delivery, NOT including deposit)
    total_deposit: str = "0.00"     # string, sum of deposits from all selected items
    package_id: int = 0

    # --- Outputs (populated during saga execution) ---
    order_id: Optional[str] = None
    payment_id: Optional[str] = None
    status: SagaStatus = SagaStatus.STARTED
    error: Optional[str] = None

    def to_order_summary(self) -> dict:
        return {
            "order_id": self.order_id,
            "payment_id": self.payment_id,
            "fulfillment_method": self.fulfillment_method,
            "status": self.status.value,
        }
