import enum

from sqlalchemy import Enum

from app.db import db


class OdometerSource(enum.Enum):
    reservation = "reservation"


class OdometerSourceType(enum.Enum):
    checkin = 'checkin'
    checkout = 'checkout'


class CarOdometer(db.Model):
    __tablename__ = "car_odometer"
    id = db.Column(db.Integer, primary_key=True)
    created = db.Column(db.DateTime, nullable=False)
    # updated = db.Column(db.DateTime)
    car_id = db.Column(db.Integer, db.ForeignKey('cars.id'), nullable=False)
    car = db.relationship('Car')
    source = db.Column(Enum(OdometerSource), nullable=False)
    source_uuid = db.Column(db.String(64))
    odometer = db.Column(db.Integer, nullable=False)
    source_type = db.Column(Enum(OdometerSourceType))
