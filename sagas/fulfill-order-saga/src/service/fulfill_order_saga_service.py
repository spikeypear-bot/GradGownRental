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
            self._sync_logistics_tracking(context)

            # Step 4
            self._inventory.transition_reserved_to_rented(context.selected_packages)
            context.status = SagaStatus.INVENTORY_UPDATED

            # Step 6
            self._publisher.publish_order_activated({
                "order_id": context.order_id,
                "student_name": context.student_name,
                "phone": context.phone,
                "email": context.email,
                "fulfillment_method": context.fulfillment_method,
                "fulfillment_date": context.fulfillment_date or context.chosen_date,
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

    def _sync_logistics_tracking(self, context: FulfillOrderContext) -> None:
        shipment_id = context.shipment_id
        if not shipment_id:
            shipment_id = self._logistics.get_shipment_id_by_order(context.order_id)

        if not shipment_id:
            logger.warning(
                "[%s] logistics sync skipped | order_id=%s | reason=shipment_id_unavailable",
                SAGA_NAME,
                context.order_id,
            )
            return

        try:
            self._logistics.update_status(shipment_id, context.tracking_status, context.order_id)
            context.shipment_id = shipment_id
            context.status = SagaStatus.LOGISTICS_UPDATED
        except Exception as exc:
            logger.warning(
                "[%s] logistics update skipped | order_id=%s | shipment_id=%s | error=%s",
                SAGA_NAME,
                context.order_id,
                shipment_id,
                exc,
            )
