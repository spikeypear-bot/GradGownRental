from app import db
from datetime import datetime
import uuid

class ErrorLog(db.Model):
    __tablename__ = 'error_log'

    error_id     = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    saga_name    = db.Column(db.String(100), nullable=False)   # e.g. "PlaceAnOrderSaga"
    step         = db.Column(db.String(100), nullable=False)   # e.g. "Step 10 - POST /payments"
    order_id     = db.Column(db.String(100), nullable=True)    # the affected order if available
    error_message= db.Column(db.Text, nullable=False)          # what went wrong
    status_code  = db.Column(db.Integer, nullable=True)        # HTTP status code that caused the failure
    created_at   = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {c.name: str(getattr(self, c.name)) for c in self.__table__.columns}