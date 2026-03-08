from app import db
from datetime import datetime
import uuid

class OrderRecord(db.Model):
    order_id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))  # UUID
    email = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.Integer)  # Note: Use String for intl formats later
    name = db.Column(db.String(100), nullable=False)
    order_status = db.Column(db.String(20), default='CONFIRMED')  # CONFIRMED, ACTIVE, CANCELLED, RETURNED
    start_date = db.Column(db.Date, nullable=False)
    return_date = db.Column(db.Date, nullable=False)
    returned = db.Column(db.Boolean, default=False)
    delivery = db.Column(db.Boolean, default=False)
    deposit = db.Column(db.Numeric(10,2), nullable=False)  # 50% deposit
    rental_fee = db.Column(db.Numeric(10,2), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    damaged = db.Column(db.Boolean, default=False)
    
    def to_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}
