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
from service.return_order_saga_service import ReturnOrderSagaService

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s — %(message)s",
)
logger = logging.getLogger(__name__)


def create_app() -> Flask:
    app = Flask(__name__)
    CORS(app)

    order_client = OrderClient()
    inventory_client = InventoryClient()
    payment_client = PaymentClient()
    error_client = ErrorClient()
    publisher = KafkaPublisher()

    saga_service = ReturnOrderSagaService(
        order_client=order_client,
        inventory_client=inventory_client,
        payment_client=payment_client,
        error_client=error_client,
        publisher=publisher,
    )

    app.extensions["saga_service"] = saga_service
    app.extensions["order_client"] = order_client

    app.register_blueprint(saga_bp)
    logger.info("return-order-saga ready")
    return app


app = create_app()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5005)), debug=False)
