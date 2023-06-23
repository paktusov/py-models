import enum

from sqlalchemy import Enum, Column, Integer, DateTime, ForeignKey, String
from sqlalchemy.orm import relationship

from models import base


class FuelSource(enum.Enum):
    reservation = "reservation"


class FuelSourceType(enum.Enum):
    checkin = 'checkin'
    checkout = 'checkout'


class CarFuel(base):
    __tablename__ = "car_fuel"
    id = Column(Integer, primary_key=True)
    created = Column(DateTime, nullable=False)
    updated = Column(DateTime)
    car_id = Column(Integer, ForeignKey('cars.id'), nullable=False)
    car = relationship('Car')
    source = Column(Enum(FuelSource), nullable=False)
    source_uuid = Column(String(64))
    fuel_level = Column(Integer, nullable=False, comment='Fuel level in percent')
    source_type = Column(Enum(FuelSourceType))
