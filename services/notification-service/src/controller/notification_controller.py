"""
NotificationController — Flask blueprint exposing HTTP endpoints.

Routes:
  GET  /health                              — liveness probe for Kong / Docker
  GET  /notifications/<order_id>            — fetch all notification logs for an order
"""

from flask import Blueprint, jsonify, current_app

root_bp = Blueprint("root", __name__)
notification_bp = Blueprint("notifications", __name__, url_prefix="/notifications")


@root_bp.get("/health")
def health():
    return jsonify({"status": "ok", "service": "notification-service"}), 200


@notification_bp.get("/<string:order_id>")
def get_notifications_by_order(order_id: str):
    """
    Returns all notification logs for a given order_id.
    Useful for support staff to verify that a student was notified.
    """
    repo = current_app.extensions["notification_repo"]
    logs = repo.find_by_order_id(order_id)
    return jsonify([log.to_dict() for log in logs]), 200
