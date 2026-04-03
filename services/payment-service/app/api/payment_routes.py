from app import db
from app.models import Payment, PaymentStatus
from flask import Blueprint, abort, jsonify, current_app, request
from werkzeug.exceptions import HTTPException

from decimal import Decimal
import logging

logger = logging.getLogger("payment").getChild("api")
# logger.setLevel("DEBUG")

api = Blueprint("api", __name__)


@api.route('/health', methods=["GET"])
def health():
    return jsonify({"status": "ok", "service": "payment-service"}), 200

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

    amount_cents = int(Decimal(str(data["amount"])) * 100) # Stripe takes amounts in cents...
    stripe_client = current_app.stripe_client
    intent = stripe_client.v1.payment_intents.create({"amount": amount_cents, "currency": "sgd"})

    logger.debug(intent.client_secret)
    return jsonify({"code" :200,
                    "client_secret": intent.client_secret
                    }), 200


@api.route('/payments', methods=["POST"])
def authorise_payment():
    """
    Saga-facing endpoint.
    Creates a successful payment record synchronously and returns payment_id.
    """
    data = request.get_json() or {}
    required = ["order_id", "total_amount"]
    missing = [f for f in required if f not in data]
    if missing:
        return jsonify({"error": f"Missing required fields: {missing}"}), 400

    order_id = data["order_id"]
    total_amount = Decimal(str(data["total_amount"]))
    payment_details = data.get("payment_details", {})
    amount_cents = int(total_amount * 100)

    existing = Payment.query.filter_by(order_id=order_id).first()
    if existing:
        return jsonify({
            "payment_id": existing.payment_id,
            "status": existing.status.value,
            "idempotent": True,
        }), 200

    stripe_client = current_app.stripe_client
    intent = None

    # Path A: frontend already confirmed a PaymentIntent via Stripe.js
    payment_intent_id = payment_details.get("payment_intent_id")
    if payment_intent_id:
        try:
            intent = stripe_client.v1.payment_intents.retrieve(payment_intent_id)
        except Exception as e:
            logger.error(f"Stripe intent retrieval failed for order {order_id}: {e}")
            return jsonify({"error": f"Payment verification failed: {str(e)}"}), 402
    else:
        # Path B: server-side sandbox shortcut (fallback)
        # Use Stripe test payment methods such as:
        #   pm_card_visa            -> success
        #   pm_card_chargeDeclined  -> declined
        payment_method_id = payment_details.get("test_payment_method_id", "pm_card_visa")

        try:
            intent = stripe_client.v1.payment_intents.create({
                "amount": amount_cents,
                "currency": "sgd",
                "confirm": True,
                "payment_method": payment_method_id,
                "automatic_payment_methods": {
                    "enabled": True,
                    "allow_redirects": "never",
                },
                "description": f"GradGown order {order_id}",
                "metadata": {"order_id": order_id},
            })
        except Exception as e:
            logger.error(f"Stripe payment failed for order {order_id}: {e}")
            return jsonify({"error": f"Payment authorisation failed: {str(e)}"}), 402

    intent_status = getattr(intent, "status", None) or intent.get("status")
    if intent_status != "succeeded":
        logger.error(f"Stripe payment not successful for order {order_id}: status={intent_status}")
        return jsonify({
            "error": f"Payment not successful (status={intent_status})",
            "stripe_status": intent_status,
        }), 402

    payment = Payment(
        order_id=order_id,
        amount=total_amount,
        status=PaymentStatus.SUCCESS,
        client_secret=getattr(intent, "client_secret", None) or intent.get("client_secret"),
    )
    db.session.add(payment)
    db.session.commit()

    return jsonify({
        "payment_id": payment.payment_id,
        "status": payment.status.value,
        "stripe_payment_intent_id": getattr(intent, "id", None) or intent.get("id"),
    }), 201


@api.route('/payments/refunds', methods=["POST"])
def refund_payment():
    """
    Scenario 4 refund endpoint.

    Expected JSON:
    {
      "order_id": "...",
      "payment_id": "...",
      "refundable_amount": "10.00"
    }
    """
    data = request.get_json() or {}
    required = ["order_id", "payment_id", "refundable_amount"]
    missing = [f for f in required if f not in data]
    if missing:
        return jsonify({"error": f"Missing required fields: {missing}"}), 400

    order_id = data["order_id"]
    payment_id = data["payment_id"]
    refundable_amount = Decimal(str(data["refundable_amount"]))
    if refundable_amount < 0:
        return jsonify({"error": "refundable_amount must be >= 0"}), 400

    if refundable_amount == 0:
        return jsonify({
            "refund_id": None,
            "status": "NO_REFUND",
            "refunded_amount": "0.00",
        }), 200

    payment = Payment.query.filter_by(payment_id=payment_id, order_id=order_id).first()
    if not payment:
        # Seeded/demo orders in local environments may carry placeholder payment ids
        # such as "pay-004" without a real payment-service record. Surface a clear
        # simulated refund response so the orchestration flow remains testable.
        if str(payment_id).startswith("pay-"):
            logger.warning(
                "Using simulated refund for demo payment | order_id=%s | payment_id=%s | refundable_amount=%s",
                order_id,
                payment_id,
                refundable_amount,
            )
            return jsonify({
                "refund_id": f"manual-{payment_id}",
                "status": "SIMULATED_REFUND",
                "refunded_amount": f"{refundable_amount:.2f}",
            }), 202

        return jsonify({"error": "Payment record not found for order_id/payment_id"}), 404

    # We store client_secret. PaymentIntent id can be extracted from it:
    # e.g. pi_123_secret_abc -> pi_123
    if not payment.client_secret or "_secret_" not in payment.client_secret:
        return jsonify({"error": "Stored payment record does not contain refundable Stripe reference"}), 400

    payment_intent_id = payment.client_secret.split("_secret_")[0]
    amount_cents = int(refundable_amount * 100)

    try:
        stripe_client = current_app.stripe_client
        refund = stripe_client.v1.refunds.create({
            "payment_intent": payment_intent_id,
            "amount": amount_cents,
            "metadata": {"order_id": order_id, "payment_id": payment_id},
        })
    except Exception as e:
        logger.error(f"Refund failed for order {order_id}: {e}")
        return jsonify({"error": f"Refund authorisation failed: {str(e)}"}), 402

    return jsonify({
        "refund_id": getattr(refund, "id", None) or refund.get("id"),
        "status": getattr(refund, "status", None) or refund.get("status"),
        "refunded_amount": f"{refundable_amount:.2f}",
    }), 201

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
