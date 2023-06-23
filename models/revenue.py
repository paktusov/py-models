import enum

from sqlalchemy import Enum

from app.db import db


class ReservationType(enum.Enum):
    self = "self"
    turo = "turo"


class CarRevenue(db.Model):
    __tablename__ = "car_revenues"
    id = db.Column(db.Integer, primary_key=True)
    created = db.Column(db.DateTime, nullable=False)
    date_stat = db.Column(db.DateTime, nullable=False)
    car_id = db.Column(db.Integer, db.ForeignKey('cars.id'), nullable=False)
    car = db.relationship('Car')
    price_day = db.Column(db.Integer, nullable=True)
    price_day_turo = db.Column(db.Integer, nullable=True)
    day_in_trip = db.Column(db.Boolean(), nullable=False)
    revenue = db.Column(db.Integer, nullable=True)
    revenue_plan = db.Column(db.Integer, nullable=True)
    rate = db.Column(db.Integer, nullable=True)
    final_data = db.Column(db.Boolean(), nullable=False)
    reservation_type = db.Column(Enum(ReservationType), nullable=False)
