from flask import Blueprint, current_app, jsonify, request

from model.fulfill_order_context import FulfillOrderContext

saga_bp = Blueprint("fulfill_saga", __name__)


@saga_bp.get("/health")
def health():
    return jsonify({"status": "ok", "service": "fulfill-order-saga"}), 200


@saga_bp.post("/fulfillment/activate")
def activate_fulfillment():
    """
    Scenario 3 entrypoint.
    Expected fields:
    - order_id
    Optional:
    - shipment_id
    - tracking_status (COLLECTED|DELIVERED)
    - selected_packages: [{modelId, qty, chosenDate}]
    """
    body = request.get_json(force=True) or {}
    if "order_id" not in body:
        return jsonify({"error": "Missing required fields: ['order_id']"}), 400

    order_id = body["order_id"]
    saga = current_app.extensions["saga_service"]
    order_client = current_app.extensions["order_client"]

    try:
        order = order_client.get_order(order_id)
        selected_items = body.get("selected_packages") or [
            {
                "modelId": item.get("modelId"),
                "qty": item.get("qty", 1),
                "chosenDate": body.get("chosen_date") or order.get("rental_start_date"),
            }
            for item in (order.get("selected_items") or [])
        ]

        ctx = FulfillOrderContext(
            order_id=order_id,
            shipment_id=body.get("shipment_id") or order_id,
            tracking_status=body.get("tracking_status") or (
                "DELIVERED" if order.get("fulfillment_method") == "DELIVERY" else "COLLECTED"
            ),
            selected_packages=selected_items,
            chosen_date=body.get("chosen_date") or order.get("rental_start_date"),
            student_name=order.get("student_name", "Student"),
            phone=order.get("phone", ""),
            email=order.get("email", ""),
            return_date=order.get("rental_end_date", ""),
        )

        result = saga.activate_handover(ctx)
        return jsonify(result), 200
    except Exception as exc:
        return jsonify({"error": str(exc), "step": "activate_fulfillment"}), 500
