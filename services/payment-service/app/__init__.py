import dotenv
import logging
import os

from flask import Flask
from flask_cors import CORS
from stripe import StripeClient, AuthenticationError

dotenv.load_dotenv()

logging.basicConfig(level=logging.INFO,
                    # filename="./logs/payment-service.log",
                    encoding='utf-8',
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("payment-service")

def create_app():
    app = Flask(__name__)

    CORS(app)

    app.config.from_mapping(
        STRIPE_SECRET_KEY = os.getenv("STRIPE_SECRET_KEY"),
    )

    if not app.config.get("STRIPE_SECRET_KEY"):
        logger.critical("STRIPE_SECRET_KEY is not configured!")

    try:
        stripe_client = StripeClient(app.config.get("STRIPE_SECRET_KEY"))
        logger.info("Stripe client configured with API key")


        logger.info("Flask server successfully initialised")

    except AuthenticationError as e:
        logger.critical(e)

    return app



