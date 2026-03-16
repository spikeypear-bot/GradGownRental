from flask import app
from stripe import StripeClient
import dotenv
import os

dotenv.load_dotenv()

STRIPE_API_KEY  = os.getenv("STRIPE_API_KEY")
stripe_client = StripeClient(STRIPE_API_KEY)

@app.route('/checkout/<order_id>/', methods=["POST"])
def create_payment_intent(self, parameter_list):
    """
    docstring
    """
    try:
        checkout_session = stripe_client.v1.checkout.sessions.create_async()
    except Exception as e:
        pass
