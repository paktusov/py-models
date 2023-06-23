import enum

from sqlalchemy import Enum

from app.db import db


class ParserCarPriceStatus(enum.Enum):
    UNKNOWN = "unknown"
    STARTED = 'started'
    SUCCESS = 'success'
    ERROR = 'error'


class ParserCarPrice(db.Model):
    __tablename__ = "parser_car_prices"
    id = db.Column(db.Integer, primary_key=True)
    created = db.Column(db.DateTime, nullable=False)
    updated = db.Column(db.DateTime, nullable=False)
    price_usd = db.Column(db.Integer, nullable=False)
    status = db.Column(Enum(ParserCarPriceStatus), nullable=False)
    # old_price_usd = db.Column(db.Integer, nullable=False)
    car_id = db.Column(db.Integer, db.ForeignKey('cars.id'), nullable=False)
    car = db.relationship('Car')
    raw = db.Column(db.Text)
    error = db.Column(db.Text)
