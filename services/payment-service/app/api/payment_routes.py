from flask_migrate import current
from sqlalchemy import insert

from app import db
from app.models import Payment, PaymentStatus
from flask import Blueprint, abort, jsonify, current_app, request
from werkzeug.exceptions import HTTPException

import logging

logger = logging.getLogger("payment").getChild("api")
# logger.setLevel("DEBUG")

api = Blueprint("api", __name__)

# Handle exceptions
@api.errorhandler(HTTPException)
def handle_http_exceptions(e: HTTPException):

    logger.debug(e)

    return jsonify(code=e.code, error=e.description), e.code

@api.errorhandler(Exception)
def handle_exceptions(e: Exception):

    logger.error(e)

    return jsonify(code=500, error='Internal Service Error'), 500


@api.route('/checkout', methods=["POST"])
def create_payment_intent():
    """
    Create payment intent after order created
    Order information passed from Make Order Saga
    Returns client's payment intent to Make Order Saga
    """

    data = request.get_json()
    logger.info(data)

    amount_cents = data["amount"] * 100 # Stripe takes amounts in cents...
    stripe_client = current_app.stripe_client
    intent = stripe_client.v1.payment_intents.create({"amount": amount_cents, "currency": "sgd"})

    logger.debug(intent.client_secret)
    return jsonify({"code" :200,
                    "client_secret": intent.client_secret
                    }), 200

@api.route('/test', methods=["GET"])
def test():
    """Test endpoint
    """
    payments = Payment.query.all()

    try:
        stmt = Payment(
            client_secret="ac",
            order_id="aac",
            amount=2.51,
            )
        db.session.add(stmt)
        db.session.commit()

    except Exception as e:
        db.session.rollback()

    payments = Payment.query.all()
    if len(payments) != 0:
        result = [ payment.to_dict()
                  for payment in payments ]

        return jsonify({"payments": result}), 200

    else:
        abort(400)
