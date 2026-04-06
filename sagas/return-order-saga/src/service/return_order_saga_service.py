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
            has_damage = bool(
                context.damaged_components
                or context.damage_report.strip()
                or context.damage_images
            )

            # Step 2
            self._orders.update_status(
                context.order_id,
                "RETURNED_DAMAGED" if has_damage else "RETURNED",
            )
            context.status = SagaStatus.ORDER_UPDATED

            # Step 3
            if has_damage and context.damaged_packages:
                self._inventory.transition("RENTED_TO_DAMAGED", context.damaged_packages)
            if context.clean_packages:
                self._inventory.transition("RENTED_TO_WASH", context.clean_packages)
            if not has_damage and not context.clean_packages:
                self._inventory.transition("RENTED_TO_WASH", context.selected_packages)
            context.status = SagaStatus.INVENTORY_DAMAGED if has_damage else SagaStatus.MAINTENANCE_REQUESTED

            # Step 4
            context.refundable_amount = max(0.0, context.original_deposit - context.damage_fee)

            # Step 5/6/7
            refund = self._payments.refund(context.order_id, context.payment_id, context.refundable_amount)
            context.refund_id = refund.get("refund_id")
            context.status = SagaStatus.REFUNDED

            # Step 8
            self._publisher.publish_return_processed({
                "order_id": context.order_id,
                "student_name": context.student_name,
                "phone": context.phone,
                "email": context.email,
                "refund_amount": f"{context.refundable_amount:.2f}",
                "original_deposit": f"{context.original_deposit:.2f}",
                "damage_fee": f"{context.damage_fee:.2f}",
                "has_damage": has_damage,
            })

            # Step 9
            if has_damage:
                self._inventory.transition("DAMAGED_TO_REPAIR", context.damaged_packages or context.selected_packages)
                context.status = SagaStatus.MAINTENANCE_REQUESTED
            context.metadata["damage_report"] = context.damage_report
            context.metadata["damage_images_count"] = len(context.damage_images)
            context.metadata["has_damage"] = has_damage

            return context.to_return_summary()
        except Exception as exc:
            context.status = SagaStatus.FAILED
            context.error = str(exc)
            logger.error("[%s] failed | order_id=%s | error=%s", SAGA_NAME, context.order_id, exc)
            self._errors.log_error(SAGA_NAME, "process_return", context.order_id, str(exc))
            raise

    def transition_to_wash(self, context: ReturnOrderContext) -> dict:
        try:
            self._inventory.transition("REPAIR_TO_WASH", context.selected_packages)
            return {
                "order_id": context.order_id,
                "status": "REPAIR_TO_WASH_COMPLETED",
            }
        except Exception as exc:
            self._errors.log_error(SAGA_NAME, "transition_to_wash", context.order_id, str(exc))
            raise

    def maintenance_complete(self, context: ReturnOrderContext) -> dict:
        try:
            self._inventory.transition("WASH_TO_AVAILABLE", context.selected_packages)
            if context.complete_order:
                self._orders.update_status(context.order_id, "COMPLETED")
                context.status = SagaStatus.COMPLETED
            else:
                context.status = SagaStatus.MAINTENANCE_REQUESTED
            return context.to_return_summary()
        except Exception as exc:
            self._errors.log_error(SAGA_NAME, "maintenance_complete", context.order_id, str(exc))
            raise
