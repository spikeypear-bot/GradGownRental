import logging
import os

from flask import Flask
from flask_cors import CORS

from clients.error_client import ErrorClient
from clients.inventory_client import InventoryClient
from clients.logistics_client import LogisticsClient
from clients.order_client import OrderClient
from controller.saga_controller import saga_bp
from service.fulfill_order_saga_service import FulfillOrderSagaService
from service.kafka_publisher import KafkaPublisher

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
    logistics_client = LogisticsClient()
    error_client = ErrorClient()
    publisher = KafkaPublisher()

    saga_service = FulfillOrderSagaService(
        order_client=order_client,
        inventory_client=inventory_client,
        logistics_client=logistics_client,
        error_client=error_client,
        publisher=publisher,
    )

    app.extensions["saga_service"] = saga_service
    app.extensions["order_client"] = order_client

    app.register_blueprint(saga_bp)
    logger.info("fulfill-order-saga ready")
    return app


app = create_app()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5004)), debug=False)
