"""
OrderService — orchestrates order creation, state transitions, and business logic.
"""

import logging
import uuid
from datetime import date

from ..model.order import Order, OrderStatus
from ..repository.order_repository import OrderRepository

logger = logging.getLogger(__name__)


class OrderService:
    def __init__(self, repo: OrderRepository):
        self._repo = repo

    # ------------------------------------------------------------------
    # Order Lifecycle
    # ------------------------------------------------------------------

    def create_order(
        self,
        order_id: str | None,
        student_name: str,
        email: str,
        phone: str,
        package_id: int,
        selected_items: list,
        rental_start_date: str,
        rental_end_date: str,
        total_amount: float,
        fulfillment_method: str,
        deposit: float = 0.0,
        hold_id: str = None,
        payment_id: str = None,
        status: str = "PENDING",
    ) -> Order:
        """
        Create a new order in the requested initial state (default: PENDING).
        
        :param order_id: unique order identifier (generated if omitted)
        :param student_name: student's full name
        :param email: student's email
        :param phone: student's phone number
        :param package_id: which graduation package was selected
        :param selected_items: list of {modelId, qty} dicts
        :param rental_start_date: ISO date string
        :param rental_end_date: ISO date string
        :param total_amount: final charged amount
        :param fulfillment_method: 'COLLECTION' | 'DELIVERY'
        :param deposit: total deposit from all selected items
        :param hold_id: soft-hold ID from Inventory (optional)
        :param payment_id: payment ID from Payment Service (optional)
        :param status: initial order status string
        
        :raises ValueError: if DELIVERY is chosen with rental_start_date < 24 hours away
        """
        if not order_id:
            order_id = str(uuid.uuid4())

        try:
            initial_status = OrderStatus[status.upper()]
        except KeyError as exc:
            raise ValueError(f"Invalid status: {status}") from exc

        normalized_fulfillment_method = str(fulfillment_method or "").upper()
        if normalized_fulfillment_method not in {"COLLECTION", "DELIVERY"}:
            raise ValueError(
                "fulfillment_method must be either 'COLLECTION' or 'DELIVERY'"
            )

        # Validate: DELIVERY orders must be at least next-day.
        # Frontend sends a date-only string (YYYY-MM-DD), so compare dates directly
        # instead of mixing naive datetimes with timezone-aware timestamps.
        if normalized_fulfillment_method == "DELIVERY":
            try:
                rental_start = date.fromisoformat(str(rental_start_date))
            except ValueError as exc:
                raise ValueError("rental_start_date must be a valid ISO date (YYYY-MM-DD)") from exc

            if rental_start <= date.today():
                raise ValueError(
                    "DELIVERY orders require rental_start_date to be after today. "
                    "For same-day rentals, please use COLLECTION fulfillment method."
                )
        
        # Note: total_amount already includes delivery fee if applicable (calculated by frontend)
        
        order = Order(
            order_id=order_id,
            student_name=student_name,
            email=email,
            phone=phone,
            package_id=package_id,
            selected_items=selected_items,
            rental_start_date=rental_start_date,
            rental_end_date=rental_end_date,
            total_amount=total_amount,
            deposit=deposit,
            fulfillment_method=normalized_fulfillment_method,
            status=initial_status,
            hold_id=hold_id,
            payment_id=payment_id,
        )
        saved = self._repo.save(order)
        logger.info(f"Order {order_id} created in {initial_status.value} state")
        return saved

    def update_order_status(self, order_id: str, status: str, payment_id: str | None = None) -> Order:
        """Update an order's lifecycle status and optionally attach payment_id."""
        order = self._repo.find_by_order_id(order_id)
        if not order:
            raise ValueError(f"Order {order_id} not found")

        try:
            new_status = OrderStatus[status.upper()]
        except KeyError as exc:
            raise ValueError(f"Invalid status: {status}") from exc
        self._repo.update_status(order_id, new_status)
        if payment_id:
            self._repo.update_payment_id(order_id, payment_id)
        logger.info("Order %s updated to %s", order_id, new_status.value)
        return self._repo.find_by_order_id(order_id)

    def activate_order(self, order_id: str) -> Order:
        """
        Mark order as ACTIVE (rental period started).
        
        Used for COLLECTION fulfillment: staff manually activates when student picks up.
        For DELIVERY, activation is automatic via activate_orders_for_today().
        """
        order = self._repo.find_by_order_id(order_id)
        if not order:
            raise ValueError(f"Order {order_id} not found")
        
        if order.status != OrderStatus.CONFIRMED:
            raise ValueError(f"Cannot activate order in {order.status} state")
        
        self._repo.update_status(order_id, OrderStatus.ACTIVE)
        logger.info(f"Order {order_id} activated (rental period started)")
        
        return self._repo.find_by_order_id(order_id)

    def process_return(self, order_id: str, damaged_items: list = None) -> Order:
        """
        Mark order as returned after physical handback.
        
        Validates that damaged items are a subset of selected items with valid quantities.
        Stores damaged items for inventory tracking.

        This direct service method should not close the order immediately. The order
        only becomes COMPLETED once the downstream maintenance flow confirms the
        return is fully resolved.
        
        :param order_id: order identifier
        :param damaged_items: list of dicts indicating which items are damaged
                            e.g., [{"modelId": "0100020", "qty": 1}, {"modelId": "0000002", "qty": 1}]
        :raises ValueError: if damaged items exceed selected items or have invalid data
        """
        order = self._repo.find_by_order_id(order_id)
        if not order:
            raise ValueError(f"Order {order_id} not found")
        if order.status != OrderStatus.ACTIVE:
            raise ValueError(f"Cannot return order in {order.status} state")
        
        # Validate damaged items
        self._validate_damaged_items(order.selected_items, damaged_items or [])
        
        # Determine if items are damaged
        damaged = bool(damaged_items and len(damaged_items) > 0)
        next_status = OrderStatus.RETURNED_DAMAGED if damaged else OrderStatus.RETURNED
        
        # Update status and damage flag
        self._repo.update_status(order_id, next_status)
        self._repo.set_damage(order_id, damaged, damaged_items=damaged_items or [])
        logger.info(
            "Order %s marked as %s (damaged=%s, items=%s)",
            order_id,
            next_status.value,
            damaged,
            damaged_items,
        )
        
        return self._repo.find_by_order_id(order_id)
    
    def _validate_damaged_items(self, selected_items: list, damaged_items: list) -> None:
        """
        Validate that damaged items are a subset of selected items with valid quantities.
        
        :param selected_items: list of selected items [{"modelId": "...", "qty": ...}, ...]
        :param damaged_items: list of damaged items to validate
        :raises ValueError: if validation fails
        """
        if not damaged_items or len(damaged_items) == 0:
            # Empty list is valid (no damage)
            return
        
        # Build a map of modelId -> qty for selected items
        selected_map = {}
        if isinstance(selected_items, list):
            # Handle list format: [{"modelId": "...", "qty": ...}, ...]
            for item in selected_items:
                if isinstance(item, dict):
                    model_id = item.get("modelId")
                    qty = item.get("qty", 0)
                    if model_id:
                        selected_map[model_id] = qty
        elif isinstance(selected_items, dict):
            # Handle dict format: {"modelId1": qty1, "modelId2": qty2, ...}
            selected_map = selected_items
        
        # Validate each damaged item
        for damaged_item in damaged_items:
            if not isinstance(damaged_item, dict):
                raise ValueError(f"Invalid damaged item format: {damaged_item}. Must be a dict with 'modelId' and 'qty'")
            
            model_id = damaged_item.get("modelId")
            damaged_qty = damaged_item.get("qty", 0)
            
            if not model_id:
                raise ValueError("Damaged item missing 'modelId' field")
            if not isinstance(damaged_qty, (int, float)) or damaged_qty <= 0:
                raise ValueError(f"Damaged item has invalid qty: {damaged_qty}. Must be a positive number")
            
            if model_id not in selected_map:
                raise ValueError(f"Damaged item with modelId '{model_id}' was not part of this order")
            
            selected_qty = selected_map[model_id]
            if damaged_qty > selected_qty:
                raise ValueError(
                    f"Damaged qty ({damaged_qty}) for modelId '{model_id}' exceeds selected qty ({selected_qty})"
                )

    def get_order(self, order_id: str) -> Order:
        """Fetch a single order."""
        order = self._repo.find_by_order_id(order_id)
        if not order:
            raise ValueError(f"Order {order_id} not found")
        return order

    def get_student_orders(self, email: str) -> list:
        """Fetch all orders for a student."""
        return self._repo.find_by_email(email)

    def get_orders_by_status(self, status: OrderStatus) -> list:
        """Fetch all orders with a given status."""
        return self._repo.find_by_status(status)

    def get_orders_by_rental_date(self, date_str: str) -> list:
        """Fetch all orders renting on a specific date."""
        return self._repo.find_by_rental_start_date(date_str)

    def get_orders_by_return_date(self, date_str: str) -> list:
        """Fetch all orders returning on a specific date."""
        return self._repo.find_by_rental_end_date(date_str)

    # ------------------------------------------------------------------
    # Auto-activation (for scheduled jobs or background tasks)
    # ------------------------------------------------------------------

    def activate_orders_for_today(self) -> list:
        """
        Auto-activate all DELIVERY orders whose rental_start_date is TODAY.
        Called by a scheduled job (e.g., daily cron at midnight or 6 AM).
        
        COLLECTION orders are NOT auto-activated — staff must manually call
        POST /orders/<order_id>/activate when student picks up.
        
        DELIVERY orders are assumed to always arrive on-time, so we auto-activate
        on the rental_start_date.
        """
        today = date.today().isoformat()
        orders = self._repo.find_by_rental_start_date(today)
        
        activated = []
        for order in orders:
            # Only auto-activate DELIVERY orders
            if order.status == OrderStatus.CONFIRMED and order.fulfillment_method == "DELIVERY":
                try:
                    updated = self.activate_order(order.order_id)
                    activated.append(updated)
                    logger.info(f"Auto-activated DELIVERY order {order.order_id} for today")
                except ValueError as e:
                    logger.error(f"Failed to auto-activate {order.order_id}: {e}")
        
        return activated
