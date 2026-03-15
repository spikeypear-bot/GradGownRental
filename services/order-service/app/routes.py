from flask import Blueprint, jsonify, request
from app import db
from app.models import OrderRecord
import uuid
from datetime import date

bp = Blueprint('order', __name__, url_prefix='/api/orders')  # ← THIS LINE MISSING

@bp.route('', methods=['GET'])  # ← Add this before POST
def list_orders():
    orders = OrderRecord.query.all()
    return jsonify([order.to_dict() for order in orders])


@bp.route('', methods=['POST'])
def create_order():
    data = request.json
    order = OrderRecord(
        order_id=str(uuid.uuid4()),
        email=data['email'],
        phone=data['phone'],
        name=data['name'],
        start_date=date.fromisoformat(data['start_date']),
        return_date=date.fromisoformat(data['return_date']),
        deposit=float(data['deposit']),
        rental_fee=float(data['rental_fee']),
        delivery=data.get('delivery', False)
    )
    db.session.add(order)
    db.session.commit()
    return jsonify(order.to_dict()), 201

@bp.route('/<order_id>', methods=['GET'])
def get_order(order_id):
    order = OrderRecord.query.get_or_404(order_id)
    return jsonify(order.to_dict())
