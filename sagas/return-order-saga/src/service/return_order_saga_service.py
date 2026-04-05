import logging

from model.return_order_context import ReturnOrderContext, SagaStatus

logger = logging.getLogger(__name__)
SAGA_NAME = "return-order-saga"


class ReturnOrderSagaService:
    def __init__(self, order_client, inventory_client, payment_client, error_client, publisher):
        self._orders = order_client
        self._inventory = inventory_client
        self._payments = payment_client
        self._errors = error_client
        self._publisher = publisher

    def process_return(self, context: ReturnOrderContext) -> dict:
        try:
            # Ensure all items have chosenDate for inventory transitions
            def ensure_chosen_date(items):
                for item in items or []:
                    if "chosenDate" not in item or not item.get("chosenDate"):
                        item["chosenDate"] = context.chosen_date
                return items or []

            # Step 1 - Mark order as RETURNED (items physically returned to system)
            self._orders.update_status(context.order_id, "RETURNED")
            context.status = SagaStatus.ORDER_UPDATED

            # Step 2 - Move all items to RENTED_TO_WASH initially (will be reassessed in Check Damage)
            selected_packages = ensure_chosen_date(context.selected_packages)
            self._inventory.transition("RENTED_TO_WASH", selected_packages)
            context.status = SagaStatus.MAINTENANCE_REQUESTED

            # Step 3 - Store initial damage info (actual refund will be processed after maintenance complete)
            context.metadata["damage_report"] = context.damage_report or ""
            context.metadata["damage_images_count"] = len(context.damage_images or [])
            context.metadata["has_damage"] = False  # Will be updated during assessment

            # Step 4 - Publish return event (damage assessment will happen in Check Damage workflow)
            self._publisher.publish_return_processed({
                "order_id": context.order_id,
                "student_name": context.student_name,
                "phone": context.phone,
                "email": context.email,
                "refund_amount": "pending",  # Amount will be determined after damage assessment and maintenance
            })

            return context.to_return_summary()
            context.metadata["damage_images_count"] = 0
            context.metadata["has_damage"] = False

            return context.to_return_summary()
        except Exception as exc:
            context.status = SagaStatus.FAILED
            context.error = str(exc)
            logger.error("[%s] failed | order_id=%s | error=%s", SAGA_NAME, context.order_id, exc)
            self._errors.log_error(SAGA_NAME, "process_return", context.order_id, str(exc))
            raise

    def assess_damage(self, context: ReturnOrderContext) -> dict:
        """
        Called from Check Damage page when staff assesses damage for returned items.
        Updates order status and inventory transitions based on damage findings.
        PROCESSES REFUND based on actual damage determined.
        
        Automatic progression:
        - Damaged items: RENTED_TO_DAMAGED → DAMAGED_TO_REPAIR (1 day) → REPAIR_TO_WASH (3 days) → WASH_TO_AVAILABLE
        - Clean items: Already in RENTED_TO_WASH → WASH_TO_AVAILABLE (3 days)
        """
        try:
            has_damage = bool(
                context.damaged_components
                or context.damage_report.strip()
                or context.damage_images
            )

            def ensure_chosen_date(items):
                for item in items or []:
                    if "chosenDate" not in item or not item.get("chosenDate"):
                        item["chosenDate"] = context.chosen_date
                return items or []

            damaged_packages = ensure_chosen_date(context.damaged_packages)
            clean_packages = ensure_chosen_date(context.clean_packages)

            # Transition items based on damage assessment
            if has_damage and damaged_packages:
                # Damaged items enter repair workflow
                self._inventory.transition("RENTED_TO_DAMAGED", damaged_packages)
                self._inventory.transition("DAMAGED_TO_REPAIR", damaged_packages)
                # Update order status to reflect damage needing repair
                self._orders.update_status(context.order_id, "RETURNED_DAMAGED")
                # Store which items are damaged in the order record
                self._orders.set_damaged_items(context.order_id, damaged_packages)
                context.status = SagaStatus.MAINTENANCE_REQUESTED
            
            # Clean items already in RENTED_TO_WASH, will auto-complete after 3 days
            # No additional action needed here
            
            # PROCESS REFUND NOW - based on actual damage assessment
            # Refund amount = Original deposit - damage charges
            if context.payment_id:
                context.refundable_amount = max(0.0, context.original_deposit - context.damage_fee)
                refund = self._payments.refund(context.order_id, context.payment_id, context.refundable_amount)
                context.refund_id = refund.get("refund_id")
                context.status = SagaStatus.REFUNDED
                logger.info(f"[{SAGA_NAME}] Refund processed for order {context.order_id}: ${context.refundable_amount:.2f} (Deposit: ${context.original_deposit:.2f}, Damage fee: ${context.damage_fee:.2f})")
            
            context.metadata["damage_report"] = context.damage_report
            context.metadata["damage_images_count"] = len(context.damage_images)
            context.metadata["has_damage"] = has_damage

            return context.to_return_summary()
        except Exception as exc:
            context.status = SagaStatus.FAILED
            context.error = str(exc)
            logger.error("[%s] assess_damage failed | order_id=%s | error=%s", SAGA_NAME, context.order_id, exc)
            self._errors.log_error(SAGA_NAME, "assess_damage", context.order_id, str(exc))
            raise

    def transition_to_wash(self, context: ReturnOrderContext) -> dict:
        """
        Transition items from repair to wash (after repair is complete).
        This is typically called automatically or manually from repair queue.
        """
        try:
            def ensure_chosen_date(items):
                for item in items or []:
                    if "chosenDate" not in item or not item.get("chosenDate"):
                        item["chosenDate"] = context.chosen_date
                return items or []

            selected_packages = ensure_chosen_date(context.selected_packages)
            # Transition from repair to wash
            self._inventory.transition("REPAIR_TO_WASH", selected_packages)
            context.status = SagaStatus.MAINTENANCE_REQUESTED
            return context.to_return_summary()
        except Exception as exc:
            context.status = SagaStatus.FAILED
            context.error = str(exc)
            logger.error("[%s] transition_to_wash failed | order_id=%s | error=%s", SAGA_NAME, context.order_id, exc)
            self._errors.log_error(SAGA_NAME, "transition_to_wash", context.order_id, str(exc))
            raise

    def maintenance_complete(self, context: ReturnOrderContext) -> dict:
        """
        Complete maintenance workflow (washing/repair done, items ready for inventory).
        Items transition to available inventory.
        
        NOTE: Refund was already processed during assess_damage() based on damage found.
        """
        try:
            def ensure_chosen_date(items):
                for item in items or []:
                    if "chosenDate" not in item or not item.get("chosenDate"):
                        item["chosenDate"] = context.chosen_date
                return items or []

            selected_packages = ensure_chosen_date(context.selected_packages)
            # Transition items to available inventory
            self._inventory.transition("WASH_TO_AVAILABLE", selected_packages)
            
            # Update order status to COMPLETED
            self._orders.update_status(context.order_id, "COMPLETED")
            context.status = SagaStatus.COMPLETED
            
            logger.info(f"[{SAGA_NAME}] Maintenance complete for order {context.order_id} - items now available")
            return context.to_return_summary()
        except Exception as exc:
            context.status = SagaStatus.FAILED
            context.error = str(exc)
            logger.error("[%s] maintenance_complete failed | order_id=%s | error=%s", SAGA_NAME, context.order_id, exc)
            self._errors.log_error(SAGA_NAME, "maintenance_complete", context.order_id, str(exc))
            raise

    """
    NOTE: Maintenance transitions (REPAIR_TO_WASH, WASH_TO_AVAILABLE) are handled automatically
    based on elapsed time windows:
    - DAMAGED_TO_REPAIR: 1 day window
    - REPAIR_TO_WASH + WASH_TO_AVAILABLE: 3 day window for washing
    
    Backup inventory is automatically allocated during maintenance periods
    to ensure rental availability is maintained.
    
    The Repair and Laundry tabs provide read-only dashboard views of items
    in each stage, auto-refreshing every 30 seconds to show progress.
    """
