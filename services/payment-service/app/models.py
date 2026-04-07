import enum
import uuid

# from flask import current_app as app
from app import db
from sqlalchemy import Numeric, Enum

class PaymentStatus(enum.Enum):
    """Model for payment status"""
    PENDING = "PENDING"
    SUCCESS = "SUCCESS"
    FAILURE = "FAILED"
    CANCELLED = "CANCELLED"
    REFUNDED = "REFUNDED"

class Payment(db.Model):
    """Model for payment transactions"""
    __tablename__ = "payments"

    # Payment ID on creation of database table
    payment_id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()), index=True)

    # Client Secret created by StripeClient (used for payment)
    client_secret = db.Column(db.String(255), nullable=True, unique=True, index=True)

    order_id = db.Column(db.String(36), nullable=False, unique=True, index=True)
    amount = db.Column(Numeric(10, 2), nullable=False)

    status = db.Column(db.Enum(PaymentStatus, name='payment_status_enum', create_type=False),
                      nullable=False,
                      default=PaymentStatus.PENDING,
                      index=True)


    created_at = db.Column(db.DateTime, nullable=False, default=db.func.now())
    updated_at = db.Column(db.DateTime, nullable=False, default=db.func.now(), onupdate=db.func.now())

    def to_dict(self):
        """Convert the model to a dictionary"""
        return {
            'paymentId': self.payment_id,
            'clientSecret': self.client_secret,
            'orderId': self.order_id,
            'amount': float(self.amount),
            'status': self.status.value,
            'createdAt': self.created_at.isoformat(),
            'updatedAt': self.updated_at.isoformat()
        }
