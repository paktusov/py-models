import enum

from sqlalchemy import Enum, Column, Integer, DateTime, String, Text

from . import base


class UserPaymentPaypalType(enum.Enum):
    reservation = "reservation"
    deposit = "deposit"


class UserPaymentPaypalStatus(enum.Enum):
    created = "created"
    approved = "approved"
    success = "success"
    failed = "failed"
    unknown = "unknown"


class UserPaymentPaypal(base):
    __tablename__ = "user_payments_paypal"
    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    created = Column(DateTime, nullable=False)
    uuid = Column(String(255), nullable=False)
    payment_type = Column(Enum(UserPaymentPaypalType), nullable=False)
    user_uuid = Column(String(64))
    reservation_uuid = Column(String(64))
    status = Column(Enum(UserPaymentPaypalStatus), nullable=False)
    reference = Column(String(255))
    amount = Column(String(10))
    raw = Column(Text)
