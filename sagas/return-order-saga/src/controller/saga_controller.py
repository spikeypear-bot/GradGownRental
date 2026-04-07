from flask import Blueprint, current_app, jsonify, request

from model.return_order_context import VALID_COMPONENTS, ReturnOrderContext

saga_bp = Blueprint("return_saga", __name__)


@saga_bp.get("/health")
def health():
    return jsonify({"status": "ok", "service": "return-order-saga"}), 200


def _default_items(order: dict, body: dict) -> list:
    selected_packages = body.get("selected_packages") or []
    fallback_date = body.get("chosen_date") or order.get("rental_start_date")

    def _normalize_item(item: dict) -> dict:
        return {
            **item,
            "modelId": item.get("modelId"),
            "qty": item.get("qty", 1),
            "chosenDate": item.get("chosenDate") or fallback_date,
        }

    if body.get("selected_packages"):
        return [_normalize_item(item) for item in selected_packages]
    return [_normalize_item(item) for item in (order.get("selected_items") or [])]


def _normalize_components(raw_components: list) -> list:
    valid_components = []
    for component in raw_components or []:
        normalized = str(component).strip().lower()
        if normalized in VALID_COMPONENTS and normalized not in valid_components:
            valid_components.append(normalized)
    return valid_components


def _item_component_key(item: dict) -> str | None:
    raw = str(
        item.get("itemType")
        or item.get("item_type")
        or item.get("itemName")
        or item.get("item_name")
        or ""
    ).strip().lower()

    if "gown" in raw:
        return "gown"
    if "hood" in raw:
        return "hood"
    if "hat" in raw or "mortarboard" in raw or "cap" in raw:
        return "mortarboard"
    return None


def _partition_items_by_damage(items: list, damaged_components: list) -> tuple[list, list]:
    if not damaged_components:
        return [], items

    damaged = []
    clean = []
    for item in items:
        component_key = _item_component_key(item)
        if component_key and component_key in damaged_components:
            damaged.append(item)
        else:
            clean.append(item)
    return damaged, clean


def _parse_complete_order_flag(raw_value) -> bool:
    if raw_value is None:
        return True
    if isinstance(raw_value, bool):
        return raw_value
    return str(raw_value).strip().lower() not in {"false", "0", "no"}


def _compute_deposit_from_items(items: list) -> float:
    total = 0.0
    for item in items or []:
        if not isinstance(item, dict):
            continue
        qty = item.get("qty", 1)
        try:
            qty = float(qty)
        except (TypeError, ValueError):
            qty = 1.0
        deposit_value = (
            item.get("deposit")
            or item.get("depositFee")
            or item.get("totalDeposit")
            or 0
        )
        try:
            total += float(deposit_value) * qty
        except (TypeError, ValueError):
            continue
    return round(total, 2)


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
        original_deposit = _compute_deposit_from_items(items) or float(order.get("deposit") or 0.0)
        damaged_components = _normalize_components(body.get("damaged_components", []))
        damaged_packages, clean_packages = _partition_items_by_damage(items, damaged_components)
        damage_fee = body.get("damage_fee")
        if damage_fee is None:
            damage_fee = _compute_deposit_from_items(damaged_packages)
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
            damaged_packages=damaged_packages,
            clean_packages=clean_packages,
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
            original_deposit=_compute_deposit_from_items(items) or float(order.get("deposit") or 0.0),
            complete_order=_parse_complete_order_flag(body.get("complete_order")),
        )
        result = saga.maintenance_complete(ctx)
        return jsonify(result), 200
    except Exception as exc:
        return jsonify({"error": str(exc), "step": "maintenance_complete"}), 500
