"""
PlaceOrderSagaService — orchestrates the full "Place an Order" saga.

Scenario 1 steps (from spec):
  5.  Receive POST /orders/create from Gown Rental UI
  6.  POST /orders        → Order Service    (initialise record)         [STUB until merged]
  7.  Receive order_id, status=PENDING
  8.  Return order_id to UI
  9.  Receive POST /submit-payment (order_id, payment_details)
  10. POST /payments      → Payment Service  (authorise transaction)     [STUB until merged]
  11-12. Stripe via Payment Service adapter, returns payment_id
  13. PUT /orders/{id}/status → Order Service  (CONFIRMED)               [STUB until merged]
  14. PUT /inventory/stock/transition → Inventory Service (available -> reserved)
  15. Return order_summary to UI
  16. Publish OrderPaid + OrderConfirmed to Kafka
  E1. On any failure → POST /errors → Error Service

The two-phase split (create_order / submit_payment) matches the UI flow:
the frontend first gets an order_id to anchor the session, then submits payment.
"""

import logging

from clients.error_client import ErrorClient
from clients.inventory_client import InventoryClient
from clients.order_client import OrderClient
from clients.payment_client import PaymentClient
from model.place_order_context import PlaceOrderContext, SagaStatus
from service.kafka_publisher import KafkaPublisher

logger = logging.getLogger(__name__)

SAGA_NAME = "place-order-saga"


class PlaceOrderSagaService:

    def __init__(
        self,
        order_client: OrderClient,
        payment_client: PaymentClient,
        inventory_client: InventoryClient,
        error_client: ErrorClient,
        publisher: KafkaPublisher,
    ):
        self._orders = order_client
        self._payments = payment_client
        self._inventory = inventory_client
        self._errors = error_client
        self._publisher = publisher

    # ------------------------------------------------------------------
    # Phase 1 — Scenario step 5-8
    # Called by: POST /orders/create
    # Returns:   {"order_id": str}  (links frontend session to backend tx)
    # ------------------------------------------------------------------

    def create_order(self, context: PlaceOrderContext) -> dict:
        """
        Initialise an order record via Order Service and return the order_id to the UI.
        The student then enters payment details before Phase 2 is triggered.
        """
        step = "create_order"
        try:
            logger.info("[%s] Phase 1 started | hold_id=%s", SAGA_NAME, context.hold_id)

            # Step 6 — POST /orders (Order Service)
            result = self._orders.create_order(
                hold_id=context.hold_id,
                selected_packages=context.selected_packages,
                fulfillment_method=context.fulfillment_method,
            )
            context.order_id = result["order_id"]
            context.status = SagaStatus.ORDER_INITIALISED

            logger.info("[%s] Order initialised | order_id=%s", SAGA_NAME, context.order_id)
            # Step 8 — return order_id to UI
            return {"order_id": context.order_id}

        except Exception as exc:
            self._handle_failure(context, step, exc)
            raise

    # ------------------------------------------------------------------
    # Phase 2 — Scenario steps 9-16
    # Called by: POST /submit-payment
    # Returns:   order_summary dict
    # ------------------------------------------------------------------

    def submit_payment(self, context: PlaceOrderContext) -> dict:
        """
        Execute the financial commitment and finalise the order.

        Compensation logic:
          - If payment fails  → order stays PENDING (no charge, no inventory change)
          - If inventory transition fails after a successful payment → log error;
            a manual reconciliation job should handle this edge case. In a full
            implementation you would issue a refund here as the compensating transaction.
        """
        try:
            logger.info("[%s] Phase 2 started | order_id=%s", SAGA_NAME, context.order_id)

            # Step 10 — POST /payments (Payment Service)
            self._step_authorise_payment(context)

            # Step 13 — PUT /orders/{id}/status → CONFIRMED (Order Service)
            self._step_confirm_order(context)

            # Step 14 — PUT /inventory/stock/transition (Inventory Service)
            self._step_transition_inventory(context)

            # Step 16 — Publish OrderPaid + OrderConfirmed to Kafka
            self._step_publish_events(context)

            context.status = SagaStatus.COMPLETED
            logger.info("[%s] Saga completed | order_id=%s", SAGA_NAME, context.order_id)

            # Step 15 — return order_summary to UI
            return context.to_order_summary()

        except Exception as exc:
            # E1 — already logged inside each _step_* helper; re-raise to controller
            raise

    # ------------------------------------------------------------------
    # Individual saga steps — each logs to Error Service on failure
    # ------------------------------------------------------------------

    def _step_authorise_payment(self, context: PlaceOrderContext) -> None:
        step = "authorise_payment"
        try:
            result = self._payments.authorise_payment(
                order_id=context.order_id,
                total_amount=context.total_amount,
                payment_details=context.payment_details,
            )
            context.payment_id = result["payment_id"]
            context.status = SagaStatus.PAYMENT_AUTHORISED
            logger.info("[%s] Payment authorised | payment_id=%s", SAGA_NAME, context.payment_id)
        except Exception as exc:
            self._handle_failure(context, step, exc)
            raise

    def _step_confirm_order(self, context: PlaceOrderContext) -> None:
        step = "confirm_order"
        try:
            self._orders.update_status(context.order_id, "CONFIRMED")
            context.status = SagaStatus.ORDER_CONFIRMED
            logger.info("[%s] Order confirmed | order_id=%s", SAGA_NAME, context.order_id)
        except Exception as exc:
            self._handle_failure(context, step, exc)
            raise

    def _step_transition_inventory(self, context: PlaceOrderContext) -> None:
        step = "transition_inventory"
        try:
            self._inventory.transition_stock(
                hold_id=context.hold_id,
                from_bucket="available_qty",
                to_bucket="reserved_qty",
            )
            context.status = SagaStatus.INVENTORY_TRANSITIONED
            logger.info("[%s] Inventory transitioned | hold_id=%s", SAGA_NAME, context.hold_id)
        except Exception as exc:
            self._handle_failure(context, step, exc)
            raise

    def _step_publish_events(self, context: PlaceOrderContext) -> None:
        step = "publish_kafka_events"
        try:
            self._publisher.publish_order_paid(context)
            self._publisher.publish_order_confirmed(context)
        except Exception as exc:
            self._handle_failure(context, step, exc)
            raise

    # ------------------------------------------------------------------
    # Error handling — E1
    # ------------------------------------------------------------------

    def _handle_failure(self, context: PlaceOrderContext, step: str, exc: Exception) -> None:
        context.status = SagaStatus.FAILED
        context.error = str(exc)
        logger.error("[%s] Step failed | step=%s | order_id=%s | error=%s",
                     SAGA_NAME, step, context.order_id, exc)
        self._errors.log_error(
            saga=SAGA_NAME,
            step=step,
            order_id=context.order_id,
            detail=str(exc),
        )
