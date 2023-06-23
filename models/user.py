import enum

from sqlalchemy import Enum

from app.db import db
from app.models.car import Car
from app.models.driver import DriverVerification, DriverVerificationStatus
from app.models.reservation import Reservation


class UserVerification(enum.Enum):
    verified_level1 = "approved"
    not_verified = "not approved"


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True, nullable=False)
    created = db.Column(db.DateTime, nullable=False)
    updated = db.Column(db.DateTime, nullable=True)
    phone = db.Column(db.String(64), nullable=False)
    email = db.Column(db.String(64), nullable=True)
    address = db.Column(db.String(250), nullable=True)
    driver_license_number = db.Column(db.String(64), nullable=True)
    name = db.Column(db.String(50), nullable=True)
    uuid = db.Column(db.String(64), nullable=False)
    auth_token = db.Column(db.String(256), nullable=False)
    verification = db.Column(Enum(UserVerification), default="not_verified", nullable=False)
    status = db.Column(db.Enum("active", "inactive"), default="active", nullable=False)

    # def __init__(self, phone, uuid, auth_token):
    #     self.phone = phone
    #     self.uuid = uuid
    #     self.auth_token = auth_token

    def cnt_cars(self):
        # count all the cars that are not deleted
        return Car.query.filter_by(user_id=self.id).filter(Car.status != 10).count()

    def cnt_trips(self):
        return Reservation.query.filter(Reservation.user_id == self.id).count()

    def list_cars(self):
        return Car.query.filter_by(user_id=self.id).filter(Car.status != 10).order_by(Car.created.desc()).all()

    def list_cars_ids(self):
        cars = self.list_cars()
        list_ids = []
        for c in cars:
            list_ids.append(c.id)
        return list_ids

    @property
    def pending(self):
        pending = DriverVerification.query.filter(
            DriverVerification.user_id == self.id,
            DriverVerification.status == DriverVerificationStatus.pending,
        ).order_by(DriverVerification.created_at.desc()).first()
        if pending:
            return True
        return False

    def fullname(self):
        if self.name:
            return f'{self.name}'
        return '-'

    def full_description(self):
        description = [self.phone]
        if self.name:
            description.append(self.name)
        if self.email:
            description.append(self.email)
        return " - ".join(description)

