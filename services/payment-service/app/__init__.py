from flask import Flask
from stripe import StripeClient
import dotenv
import os

dotenv.load_dotenv()

def create_app():
    STRIPE_API_KEY  = os.getenv("STRIPE_API_KEY")

    app = Flask(__name__)

    stripe_client = StripeClient(STRIPE_API_KEY)

    return app

print(STRIPE_API_KEY)


