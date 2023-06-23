import enum

from sqlalchemy import Enum, Column, Integer, DateTime, String

from . import base


class UserVerification(enum.Enum):
    verified_level1 = "approved"
    not_verified = "not approved"


class User(base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    created = Column(DateTime, nullable=False)
    updated = Column(DateTime, nullable=True)
    phone = Column(String(64), nullable=False)
    email = Column(String(64), nullable=True)
    address = Column(String(250), nullable=True)
    driver_license_number = Column(String(64), nullable=True)
    name = Column(String(50), nullable=True)
    uuid = Column(String(64), nullable=False)
    auth_token = Column(String(256), nullable=False)
    verification = Column(Enum(UserVerification), default="not_verified", nullable=False)
    status = Column(Enum("active", "inactive"), default="active", nullable=False)

    # def __init__(self, phone, uuid, auth_token):
    #     self.phone = phone
    #     self.uuid = uuid
    #     self.auth_token = auth_token

    # def cnt_cars(self):
    #     # count all the cars that are not deleted
    #     return Car.query.filter_by(user_id=self.id).filter(Car.status != 10).count()

    # def cnt_trips(self):
    #     return Reservation.query.filter(Reservation.user_id == self.id).count()

    # def list_cars(self):
    #     return Car.query.filter_by(user_id=self.id).filter(Car.status != 10).order_by(Car.created.desc()).all()

    def list_cars_ids(self):
        cars = self.list_cars()
        list_ids = []
        for c in cars:
            list_ids.append(c.id)
        return list_ids

    # @property
    # def pending(self):
    #     pending = DriverVerification.query.filter(
    #         DriverVerification.user_id == self.id,
    #         DriverVerification.status == DriverVerificationStatus.pending,
    #     ).order_by(DriverVerification.created_at.desc()).first()
    #     if pending:
    #         return True
    #     return False

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
