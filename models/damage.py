import enum

from sqlalchemy import Enum, Column, Integer, ForeignKey, DateTime, String, Text
from sqlalchemy.orm import relationship

from . import base

BODY_PARTS = [
    'Front bumper',
    'Back bumper',
    'Fender front driver',
    'Fender front passenger',
    'Fender back driver',
    'Fender back passenger',
    'Door front driver',
    'Door front passenger',
    'Door back driver',
    'Door back passenger',
    'Door back',
    'Threshold driver',
    'Threshold passenger',
    'Undercarriage',
    'Mechanical',
    'Glass',
    'Tires',
    'Rims',
    'Interior',
    'Roof'
    ]


class CarDamageStatus(enum.Enum):
    new = "new"
    preexisted = "preexisted"
    fixed = "fixed"
    canceled = "canceled"


class CarDamage(base):
    __tablename__ = "car_damages"
    id = Column(Integer, primary_key=True)
    car_id = Column(Integer, ForeignKey('cars.id'), nullable=False)
    car = relationship('Car')
    created = Column(DateTime, nullable=False)
    status = Column(Enum(CarDamageStatus), nullable=False)
    damage_part = Column(String(255), nullable=False)
    reservation_id = Column(String(64), nullable=True)
    reservation_type = Column(String(50), nullable=True)
    manager_id = Column(Integer, ForeignKey('managers.id'), nullable=False)
    manager = relationship('Manager')
    comment = Column(Text, nullable=True)
    claim_id = Column(Integer, nullable=True)
