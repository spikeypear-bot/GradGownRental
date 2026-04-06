"""
SagaController — Flask blueprint exposing the two saga endpoints.

Routes:
  POST /orders/create     — Create the order and return checkout details
  POST /submit-payment    — Verify payment, finalise the order, publish events
  GET  /health            — liveness probe
"""

from flask import Blueprint, jsonify, request, current_app

from model.place_order_context import PlaceOrderContext

saga_bp = Blueprint("saga", __name__)


@saga_bp.get("/health")
def health():
    return jsonify({"status": "ok", "service": "place-order-saga"}), 200


@saga_bp.post("/orders/create")
def create_order():
    """
    Initialise checkout and create the pending order.

    Expected JSON body:
    {
        "hold_id": "...",
        "selected_packages": [...],
        "fulfillment_method": "COLLECTION" | "DELIVERY",
        "student_name": "...",
        "phone": "+65...",
        "email": "student@example.com",
        "fulfillment_date": "2025-11-10",
        "return_date": "2025-11-14",
        "total_amount": "125.00"
    }
    """
    body = request.get_json(force=True)

    # Validate required fields
    required = ["hold_id", "selected_packages", "fulfillment_method",
                "student_name", "phone", "email", "fulfillment_date",
                "return_date", "total_amount"]
    missing = [f for f in required if f not in body]
    if missing:
        return jsonify({"error": f"Missing required fields: {missing}"}), 400

    context = PlaceOrderContext(
        hold_id=body["hold_id"],
        selected_packages=body["selected_packages"],
        fulfillment_method=body["fulfillment_method"],
        # payment_details not needed yet — provided in Phase 2
        payment_details={},
        student_name=body["student_name"],
        phone=body["phone"],
        email=body["email"],
        fulfillment_date=body["fulfillment_date"],
        return_date=body["return_date"],
        total_amount=body["total_amount"],
        package_id=int(body.get("package_id", 0)),
    )

    saga = current_app.extensions["saga_service"]
    try:
        result = saga.create_order(context)
        return jsonify(result), 201
    except Exception as exc:
        return jsonify({"error": str(exc), "step": "create_order"}), 500


@saga_bp.post("/submit-payment")
def submit_payment():
    """
    Finalise checkout after the frontend confirms payment.

    Expected JSON body:
    {
        "order_id": "...",
        "hold_id": "...",
        "selected_packages": [...],
        "fulfillment_method": "COLLECTION" | "DELIVERY",
        "payment_details": { ... },
        "student_name": "...",
        "phone": "+65...",
        "email": "student@example.com",
        "fulfillment_date": "2025-11-10",
        "return_date": "2025-11-14",
        "total_amount": "125.00"
    }
    """
    body = request.get_json(force=True)

    required = ["order_id", "hold_id", "payment_details", "total_amount",
                "student_name", "phone", "email", "fulfillment_method",
                "fulfillment_date", "return_date", "selected_packages"]
    missing = [f for f in required if f not in body]
    if missing:
        return jsonify({"error": f"Missing required fields: {missing}"}), 400

    context = PlaceOrderContext(
        hold_id=body["hold_id"],
        selected_packages=body["selected_packages"],
        fulfillment_method=body["fulfillment_method"],
        payment_details=body["payment_details"],
        student_name=body["student_name"],
        phone=body["phone"],
        email=body["email"],
        fulfillment_date=body["fulfillment_date"],
        return_date=body["return_date"],
        total_amount=body["total_amount"],
        package_id=int(body.get("package_id", 0)),
    )
    # order_id already exists from Phase 1
    context.order_id = body["order_id"]

    saga = current_app.extensions["saga_service"]
    try:
        result = saga.submit_payment(context)
        return jsonify(result), 200
    except Exception as exc:
        return jsonify({"error": str(exc), "step": "submit_payment"}), 500
