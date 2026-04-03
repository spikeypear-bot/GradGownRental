"""
OrderController — Flask blueprint exposing HTTP endpoints for order operations.

Routes:
  GET  /health                           — liveness probe
  POST /orders                           — create new order
  GET  /orders/<order_id>                — fetch order details
  GET  /orders/by-email/<email>          — fetch all orders for a student
  POST /orders/<order_id>/activate       — activate order (COLLECTION only; manual staff action)
  POST /orders/<order_id>/return         — mark gown as returned
  POST /orders/<order_id>/complete       — complete order (refund processed)
  GET  /orders/status/<status>           — fetch orders by status

Activation Logic:
  • COLLECTION (Pickup): Staff manually calls POST /activate when student picks up
  • DELIVERY: Auto-activated on rental_start_date via scheduled job (no manual action needed)
"""

import logging
from flask import Blueprint, request, jsonify, current_app

logger = logging.getLogger(__name__)

root_bp = Blueprint("root", __name__)
order_bp = Blueprint("orders", __name__, url_prefix="/orders")


@root_bp.get("/health")
def health():
    """Liveness probe for Docker/orchestration."""
    return jsonify({"status": "ok", "service": "order-service"}), 200


@order_bp.post("")
def create_order():
    """Create a new order."""
    data = request.get_json() or {}
    service = current_app.extensions["order_service"]
    
    # Validate required fields
    required = [
        "student_name", "email", "phone",
        "selected_items", "rental_start_date",
        "rental_end_date", "total_amount", "fulfillment_method"
    ]
    missing = [f for f in required if f not in data]
    if missing:
        return jsonify({"error": f"Missing required fields: {missing}"}), 400
    
    try:
        order = service.create_order(
            order_id=data.get("order_id"),
            student_name=data["student_name"],
            email=data["email"],
            phone=data["phone"],
            package_id=int(data.get("package_id", 0)),
            selected_items=data["selected_items"],
            rental_start_date=data["rental_start_date"],
            rental_end_date=data["rental_end_date"],
            total_amount=float(data["total_amount"]),
            fulfillment_method=data["fulfillment_method"],
            deposit=float(data.get("deposit", 0.0)),
            hold_id=data.get("hold_id"),
            payment_id=data.get("payment_id"),
            status=data.get("status", "PENDING"),
        )
        return jsonify(order.to_dict()), 201
    except ValueError as e:
        logger.error(f"Validation error creating order: {e}")
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        logger.error(f"Error creating order: {e}")
        return jsonify({"error": "Internal server error"}), 500


@order_bp.put("/<string:order_id>/status")
def update_order_status(order_id: str):
    """Update lifecycle status for an existing order."""
    service = current_app.extensions["order_service"]
    data = request.get_json() or {}

    status = data.get("status") or data.get("order_status")
    if not status:
        return jsonify({"error": "Missing required field: status"}), 400

    try:
        order = service.update_order_status(
            order_id=order_id,
            status=status,
            payment_id=data.get("payment_id"),
        )
        return jsonify(order.to_dict()), 200
    except ValueError as e:
        message = str(e)
        if message.startswith("Invalid status:"):
            return jsonify({"error": message}), 400
        return jsonify({"error": message}), 404
    except Exception as e:
        logger.error(f"Error updating order status: {e}")
        return jsonify({"error": "Internal server error"}), 500


@order_bp.get("/<string:order_id>")
def get_order(order_id: str):
    """Fetch a single order by order_id."""
    service = current_app.extensions["order_service"]
    
    try:
        order = service.get_order(order_id)
        return jsonify(order.to_dict()), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 404
    except Exception as e:
        logger.error(f"Error fetching order: {e}")
        return jsonify({"error": "Internal server error"}), 500


@order_bp.get("/by-email/<string:email>")
def get_student_orders(email: str):
    """Fetch all orders for a student."""
    service = current_app.extensions["order_service"]
    
    try:
        orders = service.get_student_orders(email)
        return jsonify([order.to_dict() for order in orders]), 200
    except Exception as e:
        logger.error(f"Error fetching student orders: {e}")
        return jsonify({"error": "Internal server error"}), 500


@order_bp.post("/<string:order_id>/activate")
def activate_order(order_id: str):
    """
    Activate order (rental period started).
    
    Used for COLLECTION fulfillment only. Staff calls this endpoint when the student
    picks up the gown from the store.
    
    For DELIVERY orders, activation happens automatically on rental_start_date
    via a scheduled job (no manual action needed).
    """
    service = current_app.extensions["order_service"]
    
    try:
        order = service.activate_order(order_id)
        return jsonify(order.to_dict()), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        logger.error(f"Error activating order: {e}")
        return jsonify({"error": "Internal server error"}), 500



@order_bp.post("/<string:order_id>/return")
def return_order(order_id: str):
    """
    Mark order as returned (gown received back).
    
    Request body:
      damaged_items: list of dicts indicating damage (can be empty if no damage)
        Example: [
          {"modelId": "0100020", "qty": 1},
          {"modelId": "0000002", "qty": 1}
        ]
    """
    service = current_app.extensions["order_service"]
    
    try:
        data = request.get_json() or {}
        damaged_items = data.get("damaged_items", [])
        
        order = service.process_return(order_id, damaged_items=damaged_items)
        return jsonify(order.to_dict()), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        logger.error(f"Error returning order: {e}")
        return jsonify({"error": "Internal server error"}), 500


@order_bp.get("/status/<string:status>")
def get_orders_by_status(status: str):
    """Fetch all orders with a given status."""
    service = current_app.extensions["order_service"]
    
    try:
        # Validate status is valid
        from ..model.order import OrderStatus
        order_status = OrderStatus[status.upper()]
        orders = service.get_orders_by_status(order_status)
        return jsonify([order.to_dict() for order in orders]), 200
    except KeyError:
        return jsonify({"error": f"Invalid status: {status}"}), 400
    except Exception as e:
        logger.error(f"Error fetching orders by status: {e}")
        return jsonify({"error": "Internal server error"}), 500
