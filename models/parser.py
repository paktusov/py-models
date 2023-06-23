import enum

from sqlalchemy import Enum, Column, Integer, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship

from models import base


class ParserCarPriceStatus(enum.Enum):
    UNKNOWN = "unknown"
    STARTED = 'started'
    SUCCESS = 'success'
    ERROR = 'error'


class ParserCarPrice(base):
    __tablename__ = "parser_car_prices"
    id = Column(Integer, primary_key=True)
    created = Column(DateTime, nullable=False)
    updated = Column(DateTime, nullable=False)
    price_usd = Column(Integer, nullable=False)
    status = Column(Enum(ParserCarPriceStatus), nullable=False)
    # old_price_usd = Column(Integer, nullable=False)
    car_id = Column(Integer, ForeignKey('cars.id'), nullable=False)
    car = relationship('Car')
    raw = Column(Text)
    error = Column(Text)
