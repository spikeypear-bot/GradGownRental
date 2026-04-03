from flask import Blueprint, current_app, jsonify, request

from model.return_order_context import COMPONENT_DAMAGE_RATES, ReturnOrderContext

saga_bp = Blueprint("return_saga", __name__)


@saga_bp.get("/health")
def health():
    return jsonify({"status": "ok", "service": "return-order-saga"}), 200


def _default_items(order: dict, body: dict) -> list:
    if body.get("selected_packages"):
        return body["selected_packages"]
    return [
        {
            "modelId": item.get("modelId"),
            "qty": item.get("qty", 1),
            "chosenDate": body.get("chosen_date") or order.get("rental_start_date"),
        }
        for item in (order.get("selected_items") or [])
    ]


def _normalize_components(raw_components: list) -> list:
    valid_components = []
    for component in raw_components or []:
        normalized = str(component).strip().lower()
        if normalized in COMPONENT_DAMAGE_RATES and normalized not in valid_components:
            valid_components.append(normalized)
    return valid_components


def _calculate_damage_fee(original_deposit: float, damaged_components: list) -> float:
    deduction_rate = sum(COMPONENT_DAMAGE_RATES[component] for component in damaged_components)
    return round(original_deposit * deduction_rate, 2)


@saga_bp.post("/returns/process")
def process_return():
    body = request.get_json(force=True) or {}
    required = ["order_id"]
    missing = [f for f in required if f not in body]
    if missing:
        return jsonify({"error": f"Missing required fields: {missing}"}), 400

    order_client = current_app.extensions["order_client"]
    saga = current_app.extensions["saga_service"]

    try:
        order = order_client.get_order(body["order_id"])
        items = _default_items(order, body)
        original_deposit = float(order.get("deposit") or 0.0)
        damaged_components = _normalize_components(body.get("damaged_components", []))
        damage_fee = body.get("damage_fee")
        if damage_fee is None:
            damage_fee = _calculate_damage_fee(original_deposit, damaged_components)
        else:
            damage_fee = float(damage_fee)
        payment_id = body.get("payment_id") or order.get("payment_id")
        if not payment_id:
            return jsonify({"error": "payment_id missing and not found on order"}), 400

        ctx = ReturnOrderContext(
            order_id=order["order_id"],
            payment_id=payment_id,
            selected_packages=items,
            chosen_date=body.get("chosen_date") or order.get("rental_start_date"),
            student_name=order.get("student_name", "Student"),
            phone=order.get("phone", ""),
            email=order.get("email", ""),
            original_deposit=original_deposit,
            damage_fee=damage_fee,
            damaged_components=damaged_components,
            damage_report=body.get("damage_report", ""),
            damage_images=body.get("damage_images", []),
        )
        result = saga.process_return(ctx)
        return jsonify(result), 200
    except Exception as exc:
        return jsonify({"error": str(exc), "step": "process_return"}), 500


@saga_bp.put("/returns/transition-to-wash")
def transition_to_wash():
    body = request.get_json(force=True) or {}
    if "order_id" not in body:
        return jsonify({"error": "Missing required fields: ['order_id']"}), 400

    order_client = current_app.extensions["order_client"]
    saga = current_app.extensions["saga_service"]

    try:
        order = order_client.get_order(body["order_id"])
        items = _default_items(order, body)

        ctx = ReturnOrderContext(
            order_id=order["order_id"],
            payment_id=order.get("payment_id") or "",
            selected_packages=items,
            chosen_date=body.get("chosen_date") or order.get("rental_start_date"),
        )
        result = saga.transition_to_wash(ctx)
        return jsonify(result), 200
    except Exception as exc:
        return jsonify({"error": str(exc), "step": "transition_to_wash"}), 500


@saga_bp.put("/returns/maintenance-complete")
def maintenance_complete():
    body = request.get_json(force=True) or {}
    if "order_id" not in body:
        return jsonify({"error": "Missing required fields: ['order_id']"}), 400

    order_client = current_app.extensions["order_client"]
    saga = current_app.extensions["saga_service"]

    try:
        order = order_client.get_order(body["order_id"])
        items = _default_items(order, body)

        ctx = ReturnOrderContext(
            order_id=order["order_id"],
            payment_id=order.get("payment_id") or "",
            selected_packages=items,
            chosen_date=body.get("chosen_date") or order.get("rental_start_date"),
            original_deposit=float(order.get("deposit") or 0.0),
        )
        result = saga.maintenance_complete(ctx)
        return jsonify(result), 200
    except Exception as exc:
        return jsonify({"error": str(exc), "step": "maintenance_complete"}), 500
