from dataclasses import dataclass, field
from enum import Enum
from typing import Optional

COMPONENT_DAMAGE_RATES = {
    "gown": 0.60,
    "hood": 0.25,
    "mortarboard": 0.15,
}


class SagaStatus(str, Enum):
    STARTED = "STARTED"
    ORDER_UPDATED = "ORDER_UPDATED"
    INVENTORY_DAMAGED = "INVENTORY_DAMAGED"
    REFUNDED = "REFUNDED"
    MAINTENANCE_REQUESTED = "MAINTENANCE_REQUESTED"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


@dataclass
class ReturnOrderContext:
    order_id: str
    payment_id: str
    selected_packages: list
    chosen_date: str

    student_name: str = "Student"
    phone: str = ""
    email: str = ""
    original_deposit: float = 0.0
    damage_fee: float = 0.0
    refundable_amount: float = 0.0
    damaged_components: list = field(default_factory=list)
    damage_report: str = ""
    damage_images: list = field(default_factory=list)

    refund_id: Optional[str] = None
    status: SagaStatus = SagaStatus.STARTED
    error: Optional[str] = None
    metadata: dict = field(default_factory=dict)

    def to_return_summary(self) -> dict:
        return {
            "order_id": self.order_id,
            "refund_id": self.refund_id,
            "damage_fee": f"{self.damage_fee:.2f}",
            "original_deposit": f"{self.original_deposit:.2f}",
            "refundable_amount": f"{self.refundable_amount:.2f}",
            "damaged_components": self.damaged_components,
            "status": self.status.value,
        }
