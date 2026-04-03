"""
Order model — represents a gown rental order for a student.
Persisted to PostgreSQL via the repository layer.
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Optional


class OrderStatus(str, Enum):
    """
    Order lifecycle:
    PENDING → CONFIRMED → ACTIVE → RETURNED_DAMAGED → COMPLETED

    PENDING: Checkout initialized, awaiting successful payment completion
    CONFIRMED: Payment processed, order ready for pickup/delivery
    ACTIVE: Rental handover completed and item is now rented out
    RETURNED: Legacy clean-return state retained for backward compatibility
    RETURNED_DAMAGED: Return processed with damage workflow still in progress
    COMPLETED: Return workflow finished and stock moved back to available
    """
    PENDING = "PENDING"
    CONFIRMED = "CONFIRMED"
    ACTIVE = "ACTIVE"
    RETURNED = "RETURNED"
    RETURNED_DAMAGED = "RETURNED_DAMAGED"
    COMPLETED = "COMPLETED"


@dataclass
class Order:
    # --- Identity ---
    order_id: str
    
    # --- Student contact info (for notifications) ---
    student_name: str
    email: str
    phone: str
    
    # --- Package & selected items ---
    # package_id: which graduation package (e.g., NUS Engineering)
    # selected_items: list of {modelId, qty} dicts
    # model_id encodes both STYLE and SIZE (e.g., "0100020" = M Blue Gown)
    package_id: int
    selected_items: list                    # e.g., [{modelId: "0000024", qty: 1}, ...]
    
    # --- Rental dates ---
    rental_start_date: str                  # ISO format: "2026-05-15"
    rental_end_date: str
    
    # --- Pricing ---
    total_amount: float
    fulfillment_method: str                 # 'COLLECTION' | 'DELIVERY'
    
    # --- Fulfillment fees (with defaults) ---
    deposit: float = 0.0                        # Total deposit from all selected items
    # Note: delivery_fee ($5 for DELIVERY) is calculated by frontend and included in total_amount
    
    # --- Order state ---
    status: OrderStatus = OrderStatus.PENDING

    # --- Status timestamps ---
    confirmed_at: Optional[datetime] = None
    activated_at: Optional[datetime] = None
    returned_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    
    # --- Audit ---
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    
    # --- Saga context (reference only) ---
    hold_id: Optional[str] = None
    payment_id: Optional[str] = None
    
    # --- Damage tracking ---
    damaged: Optional[bool] = None
    damaged_items: list = field(default_factory=list)  # List of {modelId, qty} dicts
    
    # --- Database ID ---
    id: Optional[int] = None

    def to_dict(self) -> dict:
        """Convert Order to dictionary for JSON serialization."""
        return {
            "id": self.id,
            "order_id": self.order_id,
            "student_name": self.student_name,
            "email": self.email,
            "phone": self.phone,
            "package_id": self.package_id,
            "selected_items": self.selected_items,
            "rental_start_date": self.rental_start_date,
            "rental_end_date": self.rental_end_date,
            "total_amount": self.total_amount,
            "deposit": self.deposit,
            "fulfillment_method": self.fulfillment_method,
            "status": self.status.value,
            "confirmed_at": self.confirmed_at.isoformat() if isinstance(self.confirmed_at, datetime) else self.confirmed_at,
            "activated_at": self.activated_at.isoformat() if self.activated_at else None,
            "returned_at": self.returned_at.isoformat() if self.returned_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "created_at": self.created_at.isoformat() if isinstance(self.created_at, datetime) else self.created_at,
            "updated_at": self.updated_at.isoformat() if isinstance(self.updated_at, datetime) else self.updated_at,
            "hold_id": self.hold_id,
            "payment_id": self.payment_id,
            "damaged": self.damaged,
            "damaged_items": self.damaged_items,
        }
