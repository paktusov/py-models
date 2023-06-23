import enum

from sqlalchemy import Enum

from app.db import db


class FuelSource(enum.Enum):
    reservation = "reservation"


class FuelSourceType(enum.Enum):
    checkin = 'checkin'
    checkout = 'checkout'


class CarFuel(db.Model):
    __tablename__ = "car_fuel"
    id = db.Column(db.Integer, primary_key=True)
    created = db.Column(db.DateTime, nullable=False)
    # updated = db.Column(db.DateTime)
    car_id = db.Column(db.Integer, db.ForeignKey('cars.id'), nullable=False)
    car = db.relationship('Car')
    source = db.Column(Enum(FuelSource), nullable=False)
    source_uuid = db.Column(db.String(64))
    fuel_level = db.Column(db.Integer, nullable=False, comment='Fuel level in percent')
    source_type = db.Column(Enum(FuelSourceType))
