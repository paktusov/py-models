import enum
import json
from functools import cached_property

from sqlalchemy import Enum, Column, Integer, DateTime, String, Text

from models import base


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


class UserPayment(base):
    __tablename__ = "user_payments"
    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    created = Column(DateTime, nullable=False)
    uuid = Column(String(255), nullable=False)
    payment_type = Column(Enum(UserPaymentType), nullable=False)
    user_uuid = Column(String(64))
    reservation_uuid = Column(String(64))
    amount = Column(String(12))
    status = Column(Enum(UserPaymentStatus), nullable=False)
    data = Column(Text)
    raw = Column(Text)
    reference = Column(String(255))
    card_number = Column(String(16))

    @cached_property
    def data_deserialize(self):
        if not self.data:
            return {}
        return sorted(json.loads(self.data).items())
