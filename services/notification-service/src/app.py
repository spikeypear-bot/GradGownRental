"""
app.py — Flask application factory for notification-service.

Wires together:
  • PostgreSQL connection → NotificationRepository
  • TwilioAdapter + SendGridAdapter → NotificationService
  • NotificationConsumer (Kafka) — started as a background thread
  • Flask blueprints (NotificationController)
"""

import logging
import os

import psycopg2
from flask import Flask
from flask_cors import CORS

from adapters.sendgrid_adapter import SendGridAdapter
from adapters.twilio_adapter import TwilioAdapter
from consumer.notification_consumer import NotificationConsumer
from controller.notification_controller import root_bp, notification_bp
from repository.notification_repository import NotificationRepository
from service.notification_service import NotificationService

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s — %(message)s",
)
logger = logging.getLogger(__name__)


def create_app() -> Flask:
    app = Flask(__name__)
    CORS(app)

    # ------------------------------------------------------------------
    # Database
    # ------------------------------------------------------------------
    conn = psycopg2.connect(
        host=os.environ.get("DB_HOST", "notification-service-db"),
        port=int(os.environ.get("DB_PORT", 5432)),
        dbname=os.environ.get("DB_NAME", "notification"),
        user=os.environ.get("DB_USER", "notification_user"),
        password=os.environ.get("DB_PASSWORD", "notification_pass"),
    )

    # ------------------------------------------------------------------
    # Adapters (Anti-Corruption Layer)
    # ------------------------------------------------------------------
    twilio = TwilioAdapter()
    sendgrid = SendGridAdapter()

    # ------------------------------------------------------------------
    # Service + Repository
    # ------------------------------------------------------------------
    repo = NotificationRepository(conn)
    service = NotificationService(twilio=twilio, sendgrid=sendgrid, repo=repo)

    # Expose repo via app.extensions so controllers can access it
    app.extensions["notification_repo"] = repo

    # ------------------------------------------------------------------
    # Kafka consumer (background thread)
    # ------------------------------------------------------------------
    consumer = NotificationConsumer(service)
    consumer.start()

    # ------------------------------------------------------------------
    # Blueprints
    # ------------------------------------------------------------------
    app.register_blueprint(root_bp)
    app.register_blueprint(notification_bp)

    logger.info("notification-service ready")
    return app


if __name__ == "__main__":
    app = create_app()
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5001)), debug=False)