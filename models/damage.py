import enum

from sqlalchemy import Enum, Column, Integer, ForeignKey, DateTime, String, Text
from sqlalchemy.orm import relationship

from models import base
from models.car_event import CarEventFile, CarEventType

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

    @property
    def car_name_plate(self):
        return self.car.car_name_plate()

    @property
    def photos_count(self):
        return CarEventFile.query.filter_by(
            event_type=CarEventType.damage,
            event_id=self.id,
            is_active=True
        ).count()

    @property
    def get_photos(self):
        return CarEventFile.query.filter_by(
            event_type=CarEventType.damage,
            event_id=self.id,
            is_active=True
        ).all()
