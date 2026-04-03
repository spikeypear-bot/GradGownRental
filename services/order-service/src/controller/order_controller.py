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
import uuid

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
        "student_name", "email",
        "selected_items", "rental_start_date",
        "rental_end_date", "total_amount", "fulfillment_method"
    ]
    missing = [f for f in required if f not in data]
    if missing:
        return jsonify({"error": f"Missing required fields: {missing}"}), 400
    
    try:
        order = service.create_order(
            order_id=data.get("order_id") or str(uuid.uuid4()),
            student_name=data["student_name"],
            email=data["email"],
            phone=data.get("phone", ""),
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


@root_bp.post("/debug/trigger-reminders")
def trigger_reminders_debug():
    """DEBUG ONLY: Manually trigger the reminder job."""
    scheduler = current_app.extensions.get("scheduler")
    if not scheduler:
        return jsonify({"error": "Scheduler not available"}), 500
    
    try:
        scheduler._publish_reminders_job()
        return jsonify({"status": "success", "message": "Reminder job triggered manually"}), 200
    except Exception as e:
        logger.error(f"Error triggering reminders: {e}", exc_info=True)
        return jsonify({"error": str(e)}), 500


@root_bp.post("/debug/create-test-orders")
def create_test_orders_debug():
    """
    DEBUG ONLY: Create two test orders for testing reminders TODAY:
    - Order 1: COLLECTION, pickup TODAY (for PICKUP_REMINDER)
    - Order 2: COLLECTION, return TODAY (for RETURN_REMINDER - activated yesterday)
    """
    import json
    import urllib.request
    from datetime import datetime, timedelta
    
    today = datetime.now().date()
    tomorrow = today + timedelta(days=1)
    yesterday = today - timedelta(days=1)
    
    try:
        # First, try to create soft holds via inventory API
        hold_id_1 = "manual-hold-1"
        hold_id_2 = "manual-hold-2"
        
        try:
            hold_payload = [
                {"modelId": "0000024", "qty": 1, "chosenDate": today.isoformat()},
            ]
            
            req = urllib.request.Request(
                "http://inventory-service:8080/api/inventory/soft-hold",
                data=json.dumps(hold_payload).encode('utf-8'),
                headers={"Content-Type": "application/json"},
                method="POST"
            )
            
            with urllib.request.urlopen(req, timeout=10) as response:
                hold_data = json.loads(response.read().decode('utf-8')).get("data", {})
                hold_id_1 = hold_data.get("holdId", "manual-hold-1")
                hold_id_2 = hold_data.get("holdId", "manual-hold-2")
        except Exception as e:
            logger.warning(f"Could not create soft hold via API: {e}, using manual IDs")
        
        service = current_app.extensions.get("order_service")
        if not service:
            return jsonify({"error": "Order service not available"}), 500
        
        # Create Order 1: Pickup reminder (COLLECTION, pickup TODAY)
        order1 = service.create_order(
            order_id=None,  # auto-generate
            student_name="Ei Chaw Zin",
            email="eichawzin123@gmail.com",
            phone="",
            package_id=1,
            selected_items=[{"modelId": "0000024", "qty": 1}],
            rental_start_date=today.isoformat(),
            rental_end_date=tomorrow.isoformat(),
            total_amount=50.00,
            fulfillment_method="COLLECTION",
            hold_id=hold_id_1,
            status="CONFIRMED"  # confirmed, waiting to be picked up today
        )
        
        # Create Order 2: Return reminder (COLLECTION, return TODAY)
        # Create as CONFIRMED, then activate to set activated_at to yesterday
        order2 = service.create_order(
            order_id=None,  # auto-generate
            student_name="Ei Chaw Zin",
            email="eichawzin123@gmail.com",
            phone="",
            package_id=1,
            selected_items=[{"modelId": "0000024", "qty": 1}],
            rental_start_date=yesterday.isoformat(),
            rental_end_date=today.isoformat(),
            total_amount=55.00,
            fulfillment_method="COLLECTION",
            hold_id=hold_id_2,
            status="CONFIRMED"  # Create as CONFIRMED so it can be activated
        )
        
        # Auto-activate order 2 so it becomes ACTIVE (pretend it was activated yesterday)
        service.activate_order(order2.order_id)
        
        return jsonify({
            "status": "success",
            "message": "Test orders created successfully - reminders should send immediately",
            "next_step": "Run POST /debug/trigger-reminders NOW to send reminder emails immediately to eichawzin123@gmail.com",
            "orders": [
                {
                    "order_id": order1.order_id,
                    "type": "PICKUP_REMINDER",
                    "student_email": order1.email,
                    "rental_start_date": str(order1.rental_start_date),
                    "status": order1.status,
                    "notes": "Pickup is TODAY - reminder ready to send"
                },
                {
                    "order_id": order2.order_id,
                    "type": "RETURN_REMINDER",
                    "student_email": order2.email,
                    "rental_end_date": str(order2.rental_end_date),
                    "status": "ACTIVE",
                    "notes": "Return is TODAY - reminder ready to send"
                }
            ]
        }), 201
        
    except Exception as e:
        logger.error(f"Error creating test orders: {e}", exc_info=True)
        return jsonify({"error": str(e)}), 500
