from flask import Blueprint, jsonify, request
import requests
import logging
from app import db
from app.models import ErrorLog
from config import Config

logger = logging.getLogger('main')

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

    logger.error(f"[{saga_name}] {step} failed | order_id={order_id} | {error_message}")

    entry = ErrorLog(
        saga_name=saga_name,
        step=step,
        error_message=error_message,
        order_id=order_id,
        status_code=status_code,
    )
    db.session.add(entry)
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

    return jsonify({'status': 'logged'}), 201