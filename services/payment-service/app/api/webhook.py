from app import db
from app.models import Payment, PaymentStatus
from flask import abort, Blueprint, jsonify, current_app, request
from werkzeug.exceptions import HTTPException

import logging
import stripe

logger = logging.getLogger("payment").getChild("webhook")
# logger.setLevel("DEBUG")

webhook = Blueprint("webhook", __name__)

# Handle exceptions
@webhook.errorhandler(HTTPException)
def handle_http_exceptions(e: HTTPException):

    logger.debug(e)

    return jsonify(code=e.code, error=e.description), e.code

@webhook.errorhandler(Exception)
def handle_exceptions(e: Exception):

    logger.error(e)

    return jsonify(code=500, error='Internal Service Error'), 500

@webhook.route("/webhook", methods=['POST'])
def handle_webhook():
    payload = request.get_data()
    sig_header = request.headers.get('STRIPE_SIGNATURE')
    event = None

    # logger.debug(payload)
    # logger.debug(sig_header)

    try:
        endpoint_secret = current_app.config.get("STRIPE_ENDPOINT_SECRET")

        event = stripe.Webhook.construct_event(
        payload, sig_header, endpoint_secret
        )
        logger.debug(event)

    except ValueError as e:
        # invalid payload
        abort(400, description="Invalid Payload")

    except stripe.error.SignatureVerificationError as e:
        # invalid signature
        abort(400, description="Invalid Signature")

    intent = event.data.object

    if event.type == "payment_intent.succeeded":
        # Payment succeeded
        handle_payment_succeeded(intent)
        # logger.info(f"Succeeded:  {intent["id"]}")


    elif event.type == "payment_intent.payment_failed":
        # Payment failed
        handle_payment_failed(intent)
        # error_message = intent["last_payment_error"]["message"] if intent.get('last_payment_error') else None
        # logger.info("Failed: ", {intent["id"]}), error_message

    return jsonify({"Received": True}), 200

def handle_payment_succeeded(intent):
    id = intent.id

    logger.info(f"Payment {id} succeeded")
    return

def handle_payment_failed(intent):
    id = intent.id

    logger.info(f"Payment {id} failed")
    return
