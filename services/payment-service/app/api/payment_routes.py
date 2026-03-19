from termios import ECHOE

from sqlalchemy import insert

from app import db
from app.models import Payment, PaymentStatus
from flask import Blueprint, jsonify, current_app

import logging

logger = logging.getLogger("payment-service")
api = Blueprint("api", __name__)


# Clicking make payment on site creates Payment Intent using order information
# TODO replace order id with payment class
@api.route('/checkout', methods=["POST"])
def create_payment_intent():
    """
    Create payment intent
    """
    try:
        stripe_client = current_app.stripe_client
        intent = stripe_client.v1.payment_intents.create({"amount": 10099, "currency": "sgd"})

        logger.debug(intent.client_secret)
        return jsonify({"code" :200,
                        "client_secret": intent.client_secret
                        }), 200

    except Exception as e:
        logger.error(e)

    return jsonify({"code": 500,
                    "message" : "Internal Server Error"
                    }), 500

@api.route('/test', methods=["GET"])
def test():
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
        return {"failed"}, 400
