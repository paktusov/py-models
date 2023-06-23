import enum

from sqlalchemy import Enum, Column, Integer, DateTime, ForeignKey, String
from sqlalchemy.orm import relationship

from models import base


class OdometerSource(enum.Enum):
    reservation = "reservation"


class OdometerSourceType(enum.Enum):
    checkin = 'checkin'
    checkout = 'checkout'


class CarOdometer(base):
    __tablename__ = "car_odometer"
    id = Column(Integer, primary_key=True)
    created = Column(DateTime, nullable=False)
    # updated = Column(DateTime)
    car_id = Column(Integer, ForeignKey('cars.id'), nullable=False)
    car = relationship('Car')
    source = Column(Enum(OdometerSource), nullable=False)
    source_uuid = Column(String(64))
    odometer = Column(Integer, nullable=False)
    source_type = Column(Enum(OdometerSourceType))
