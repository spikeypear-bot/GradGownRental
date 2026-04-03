from flask import Blueprint, jsonify, request
import requests
from app import db
from app.models import ErrorLog
from config import Config

bp = Blueprint('error', __name__, url_prefix='/errors')

@bp.route('', methods=['POST'])
def log_error():
    data = request.json or {}

    saga_name = data.get('saga_name') or data.get('saga')
    step = data.get('step')
    error_message = data.get('error_message') or data.get('detail')
    order_id = data.get('order_id')
    status_code = data.get('status_code')

    # Validate required fields
    if not saga_name or not error_message or not step:
        return jsonify({'error': 'saga_name/saga, step and error_message/detail are required'}), 400

    # Save to DB
    error = ErrorLog(
        saga_name=saga_name,
        step=step,
        order_id=order_id,
        error_message=error_message,
        status_code=status_code
    )
    db.session.add(error)
    db.session.commit()

    # Trigger notification
    try:
        requests.post(
            f"{Config.NOTIFICATION_SERVICE_URL}/notifications/error",
            json={
                'order_id': order_id,
                'saga_name': saga_name,
                'error_message': error_message
            },
            timeout=3
        )
    except Exception:
        pass  # Don't fail error logging if notification is down

    return jsonify({'error_id': error.error_id, 'status': 'logged'}), 201


@bp.route('', methods=['GET'])
def get_errors():
    errors = ErrorLog.query.order_by(ErrorLog.created_at.desc()).all()
    return jsonify([e.to_dict() for e in errors]), 200


@bp.route('/<error_id>', methods=['GET'])
def get_error(error_id):
    error = ErrorLog.query.get_or_404(error_id)
    return jsonify(error.to_dict()), 200