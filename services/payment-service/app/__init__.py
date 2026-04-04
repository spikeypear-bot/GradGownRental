from flask import Flask
from flask_cors import CORS
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from stripe import StripeClient, AuthenticationError

import dotenv
import logging
import os

dotenv.load_dotenv()

logging.basicConfig(level=logging.INFO,
                    encoding='utf-8',
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("payment")

db = SQLAlchemy()
migrate = Migrate()

def create_app():
    app = Flask(__name__)

    CORS(app)

    app.config.from_mapping(
        KAFKA_BOOTSTRAP_SERVERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS"),
        STRIPE_SECRET_KEY = os.getenv("STRIPE_SECRET_KEY"),
        STRIPE_ENDPOINT_SECRET = os.getenv("STRIPE_ENDPOINT_SECRET"),
        SQLALCHEMY_DATABASE_URI = os.getenv("PAYMENT_DATABASE_URL", "postgresql+psycopg://payment_user:payment_pass@payment-service-db:5432/payment")
    )

    # DB Setup/Startup
    db.init_app(app)
    migrate.init_app(app, db)

    with app.app_context():
        from app.models import Payment # Import is used for db creation, DO NOT remove
        db.create_all()

    # Stripe Client Setup
    if not app.config.get("STRIPE_SECRET_KEY"):
        logger.critical("STRIPE_SECRET_KEY is not configured!")

    try:
        app.stripe_client = StripeClient(app.config.get("STRIPE_SECRET_KEY"))
        logger.info("Stripe client configured with API key")

    except AuthenticationError as e:
        logger.critical(e)

    # Stripe Webhook Confirmation
    if not app.config.get("STRIPE_ENDPOINT_SECRET"):
        logger.critical("STRIPE_ENDPOINT_SECRET is not configured!")


    # Kafka Startup
    if not app.config.get("KAFKA_BOOTSTRAP_SERVERS"):
        logger.critical("KAFKA_BOOTSTRAP_SERVERS is not configured!")

    try:
        with app.app_context():
            from app.service.kafka_service import KafkaService
            app.kafka_client = KafkaService(app.config.get("KAFKA_BOOTSTRAP_SERVERS"))

    except Exception as e:
        logger.critical(e)

    # Routing
    from app.api.payment_routes import api as payment_api_blueprint
    app.register_blueprint(payment_api_blueprint)

    from app.api.webhook import webhook as webhook_blueprint
    app.register_blueprint(webhook_blueprint)

    from app.swagger_docs import register_swagger
    register_swagger(app)

    logger.info("Flask server initialised")
    return app
