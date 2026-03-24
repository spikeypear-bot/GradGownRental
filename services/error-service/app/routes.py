from flask import Blueprint, jsonify, request
import requests
from app import db
from app.models import ErrorLog
from config import Config

bp = Blueprint('error', __name__, url_prefix='/errors')

@bp.route('', methods=['POST'])
def log_error():
    data = request.json

    # Validate required fields
    if not data.get('saga_name') or not data.get('error_message') or not data.get('step'):
        return jsonify({'error': 'saga_name, step and error_message are required'}), 400

    # Save to DB
    error = ErrorLog(
        saga_name     = data['saga_name'],
        step          = data['step'],
        order_id      = data.get('order_id'),
        error_message = data['error_message'],
        status_code   = data.get('status_code')
    )
    db.session.add(error)
    db.session.commit()

    # Trigger notification
    try:
        requests.post(
            f"{Config.NOTIFICATION_SERVICE_URL}/notifications/error",
            json={
                'order_id': data.get('order_id'),
                'saga_name': data['saga_name'],
                'error_message': data['error_message']
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