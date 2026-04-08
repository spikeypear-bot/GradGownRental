from datetime import datetime, timezone
from app import db


class ErrorLog(db.Model):
    __tablename__ = "error_logs"

    id = db.Column(db.Integer, primary_key=True)
    saga_name = db.Column(db.String(255), nullable=False)
    step = db.Column(db.String(255), nullable=False)
    error_message = db.Column(db.Text, nullable=False)
    order_id = db.Column(db.String(255), nullable=True)
    status_code = db.Column(db.Integer, nullable=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
