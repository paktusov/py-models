import enum

from sqlalchemy import Column, Integer, DateTime, String, Enum, Text

from . import base


class PromoCodeStatus(enum.Enum):
    active = "active"
    inactive = "inactive"
    deleted = "deleted"


class PromoCode(base):
    __tablename__ = "promo_codes"
    id = Column(Integer, primary_key=True)
    created = Column(DateTime, nullable=False)
    updated = Column(DateTime)
    name = Column(String(50), nullable=False)
    discount = Column(Integer, nullable=False)
    status = Column(Enum(PromoCodeStatus), nullable=False)
    description = Column(Text)
