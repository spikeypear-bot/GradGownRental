from stripe import StripeClient
import dotenv
import os

dotenv.load_dotenv()

STRIPE_API_KEY  = os.getenv("STRIPE_API_KEY")
stripe_client = StripeClient(STRIPE_API_KEY)

