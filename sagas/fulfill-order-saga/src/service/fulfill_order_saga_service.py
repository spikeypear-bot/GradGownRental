import logging

from model.fulfill_order_context import FulfillOrderContext, SagaStatus

logger = logging.getLogger(__name__)
SAGA_NAME = "fulfill-order-saga"


class FulfillOrderSagaService:
    def __init__(self, order_client, inventory_client, logistics_client, error_client, publisher):
        self._orders = order_client
        self._inventory = inventory_client
        self._logistics = logistics_client
        self._errors = error_client
        self._publisher = publisher

    def activate_handover(self, context: FulfillOrderContext) -> dict:
        try:
            # Step 2
            self._orders.update_status(context.order_id, "ACTIVE")
            context.status = SagaStatus.ORDER_ACTIVATED

            # Step 3
            self._logistics.update_status(context.shipment_id, context.tracking_status, context.order_id)
            context.status = SagaStatus.LOGISTICS_UPDATED

            # Step 4
            self._inventory.transition_reserved_to_rented(context.selected_packages)
            context.status = SagaStatus.INVENTORY_UPDATED

            # Step 6
            self._publisher.publish_order_activated({
                "order_id": context.order_id,
                "student_name": context.student_name,
                "phone": context.phone,
                "email": context.email,
                "return_date": context.return_date,
            })

            context.status = SagaStatus.COMPLETED
            return context.to_confirmation()
        except Exception as exc:
            context.status = SagaStatus.FAILED
            context.error = str(exc)
            logger.error("[%s] failed | order_id=%s | error=%s", SAGA_NAME, context.order_id, exc)
            self._errors.log_error(SAGA_NAME, "activate_handover", context.order_id, str(exc))
            raise
