import enum

from sqlalchemy import Enum

from app.db import db
from app.models.car_event import CarEventFile, CarEventType

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


class CarDamage(db.Model):
    __tablename__ = "car_damages"
    id = db.Column(db.Integer, primary_key=True)
    car_id = db.Column(db.Integer, db.ForeignKey('cars.id'), nullable=False)
    car = db.relationship('Car')
    created = db.Column(db.DateTime, nullable=False)
    status = db.Column(db.Enum(CarDamageStatus), nullable=False)
    damage_part = db.Column(db.String(255), nullable=False)
    reservation_id = db.Column(db.String(64), nullable=True)
    reservation_type = db.Column(db.String(50), nullable=True)
    manager_id = db.Column(db.Integer, db.ForeignKey('managers.id'), nullable=False)
    manager = db.relationship('Manager')
    comment = db.Column(db.Text, nullable=True)
    claim_id = db.Column(db.Integer, nullable=True)

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
