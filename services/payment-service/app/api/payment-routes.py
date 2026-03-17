from flask import app
from stripe import StripeClient
import dotenv
import os

dotenv.load_dotenv()

STRIPE_SECRET_KEY  = os.getenv("STRIPE_SECRET_KEY")
stripe_client = StripeClient(STRIPE_SECRET_KEY)

@app.route('/checkout/<order_id>/', methods=["POST"])
def create_payment_intent(self, parameter_list):
    """
    docstring
    """
    try:
        checkout_session = stripe_client.v1.checkout.sessions.create_async()
    except Exception as e:
        pass
