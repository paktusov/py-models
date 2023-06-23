import enum

from app.db import db


class PromoCodeStatus(enum.Enum):
    active = "active"
    inactive = "inactive"
    deleted = "deleted"


class PromoCode(db.Model):
    __tablename__ = "promo_codes"
    id = db.Column(db.Integer, primary_key=True)
    created = db.Column(db.DateTime, nullable=False)
    updated = db.Column(db.DateTime)
    name = db.Column(db.String(50), nullable=False)
    discount = db.Column(db.Integer, nullable=False)
    status = db.Column(db.Enum(PromoCodeStatus), nullable=False)
    description = db.Column(db.Text)
