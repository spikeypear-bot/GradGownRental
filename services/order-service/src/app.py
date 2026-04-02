"""
app.py — Flask application factory for order-service.

Wires together:
  • PostgreSQL connection → OrderRepository
  • OrderService + OrderRepository
  • Flask blueprints (OrderController)
"""

import logging
import os

import psycopg2
from flask import Flask
from flask_cors import CORS

from .controller.order_controller import root_bp, order_bp
from .repository.order_repository import OrderRepository
from .service.order_service import OrderService
from .scheduler.order_scheduler import get_scheduler
from .scheduler.kafka_event_publisher import KafkaEventPublisher

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s — %(message)s",
)
logger = logging.getLogger(__name__)


def create_app() -> Flask:
    app = Flask(__name__)
    CORS(app)

    # ------------------------------------------------------------------
    # Database Connection
    # ------------------------------------------------------------------
    try:
        conn = psycopg2.connect(
            host=os.environ.get("DB_HOST", "order-service-db"),
            port=int(os.environ.get("DB_PORT", 5432)),
            dbname=os.environ.get("DB_NAME", "order"),
            user=os.environ.get("DB_USER", "order_user"),
            password=os.environ.get("DB_PASSWORD", "order_pass"),
        )
        conn.autocommit = True  # Enable autocommit to avoid transaction issues
        logger.info("Connected to PostgreSQL database")
    except psycopg2.Error as e:
        logger.critical(f"Failed to connect to database: {e}")
        raise

    # ------------------------------------------------------------------
    # Repository + Service
    # ------------------------------------------------------------------
    repo = OrderRepository(conn)
    service = OrderService(repo)

    # Expose via app.extensions so controllers can access them
    app.extensions["order_repo"] = repo
    app.extensions["order_service"] = service

    # ------------------------------------------------------------------
    # Scheduler (for auto-activation of DELIVERY orders)
    # ------------------------------------------------------------------
    scheduler = get_scheduler()
    publisher = KafkaEventPublisher()
    scheduler.init_app(app, service, publisher=publisher)
    app.extensions["scheduler"] = scheduler

    # ------------------------------------------------------------------
    # Blueprints
    # ------------------------------------------------------------------
    app.register_blueprint(root_bp)
    app.register_blueprint(order_bp)

    logger.info("order-service ready")
    return app


if __name__ == "__main__":
    app = create_app()
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8081)), debug=False)
