import dotenv
import logging
import os

from stripe import StripeClient

dotenv.load_dotenv()

STRIPE_SECRET_KEY  = os.getenv("STRIPE_SECRET_KEY")
stripe_client = StripeClient(STRIPE_SECRET_KEY)


