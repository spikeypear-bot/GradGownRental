from dataclasses import dataclass
from enum import Enum
from typing import Optional


class SagaStatus(str, Enum):
    STARTED = "STARTED"
    ORDER_ACTIVATED = "ORDER_ACTIVATED"
    LOGISTICS_UPDATED = "LOGISTICS_UPDATED"
    INVENTORY_UPDATED = "INVENTORY_UPDATED"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


@dataclass
class FulfillOrderContext:
    order_id: str
    shipment_id: Optional[str]
    tracking_status: str
    selected_packages: list
    chosen_date: str
    fulfillment_method: str = "COLLECTION"

    student_name: str = "Student"
    phone: str = ""
    email: str = ""
    fulfillment_date: str = ""
    return_date: str = ""

    status: SagaStatus = SagaStatus.STARTED
    error: Optional[str] = None

    def to_confirmation(self) -> dict:
        return {
            "order_id": self.order_id,
            "order_status": "ACTIVE",
            "handover_timestamp": self.chosen_date,
            "updated_inventory_levels": "reserved_to_rented",
            "tracking_status": self.tracking_status,
            "status": self.status.value,
        }
