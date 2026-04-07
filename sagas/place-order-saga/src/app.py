"""
app.py — Flask application factory for place-order-saga.

Wires together all clients, the saga service, and the Flask blueprint.
"""

import logging
import os

from flask import Flask
from flask_cors import CORS

from clients.error_client import ErrorClient
from clients.inventory_client import InventoryClient
from clients.order_client import OrderClient
from clients.payment_client import PaymentClient
from controller.saga_controller import saga_bp
from service.kafka_publisher import KafkaPublisher
from service.place_order_saga_service import PlaceOrderSagaService
from swagger_docs import register_swagger

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s — %(message)s",
)
logger = logging.getLogger(__name__)


def create_app() -> Flask:
    app = Flask(__name__)
    CORS(app)

    # ------------------------------------------------------------------
    # Clients
    # ------------------------------------------------------------------
    order_client     = OrderClient()
    payment_client   = PaymentClient()
    inventory_client = InventoryClient()
    error_client     = ErrorClient()
    publisher        = KafkaPublisher()

    # ------------------------------------------------------------------
    # Saga service
    # ------------------------------------------------------------------
    saga_service = PlaceOrderSagaService(
        order_client=order_client,
        payment_client=payment_client,
        inventory_client=inventory_client,
        error_client=error_client,
        publisher=publisher,
    )

    # Expose via app.extensions so the controller can retrieve it
    app.extensions["saga_service"] = saga_service

    # ------------------------------------------------------------------
    # Blueprints
    # ------------------------------------------------------------------
    app.register_blueprint(saga_bp)
    register_swagger(app)

    logger.info("place-order-saga ready")
    return app


if __name__ == "__main__":
    app = create_app()
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5003)), debug=False)
