import enum
import json
from functools import cached_property

from sqlalchemy import Enum

from app.db import db


class UserPaymentType(enum.Enum):
    reservation = "reservation"
    deposit = "deposit"
    token = "token"
    unknown = "unknown"
    sale = "sale"
    auth = "auth"
    sale_token = "sale token"
    auth_token = "auth token"


class UserPaymentStatus(enum.Enum):
    created = "created"
    accepted = "accepted"
    review = "review"
    decline = "decline"
    error = "error"
    cancel = "cancel"
    unknown = "unknown"


class UserPayment(db.Model):
    __tablename__ = "user_payments"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, nullable=False)
    created = db.Column(db.DateTime, nullable=False)
    uuid = db.Column(db.String(255), nullable=False)
    payment_type = db.Column(Enum(UserPaymentType), nullable=False)
    user_uuid = db.Column(db.String(64))
    reservation_uuid = db.Column(db.String(64))
    amount = db.Column(db.String(12))
    status = db.Column(Enum(UserPaymentStatus), nullable=False)
    data = db.Column(db.Text)
    raw = db.Column(db.Text)
    reference = db.Column(db.String(255))
    card_number = db.Column(db.String(16))

    @cached_property
    def data_deserialize(self):
        if not self.data:
            return {}
        return sorted(json.loads(self.data).items())
