import enum

from sqlalchemy import Column, Integer, DateTime, Enum, Text, ForeignKey
from sqlalchemy.orm import relationship

from . import base
from .booking import Booking
from .damage import CarDamage
from .turo_reservation import TuroReservation


class CarClaimStatus(enum.Enum):
    progress = "progress"
    resolved = "resolved"
    declined = "declined"
    canceled = "canceled"


class CarClaim(base):
    __tablename__ = "car_claims"
    id = Column(Integer, primary_key=True)
    created = Column(DateTime, nullable=False)
    updated = Column(DateTime, nullable=False)
    status = Column(Enum(CarClaimStatus), nullable=False)
    reservation_type = Column(Text, nullable=True)
    reservation_id = Column(Text, nullable=True)
    car_id = Column(Integer, ForeignKey('cars.id'), nullable=False)
    car = relationship('Car')
    manager_id = Column(Integer, ForeignKey('managers.id'), nullable=False)
    manager = relationship('Manager')
    comment = Column(Text, nullable=True)
    body_shop_name = Column(Text, nullable=True)
    estimate_usd = Column(Integer, nullable=True)  # cents
    deductible_usd = Column(Integer, nullable=True)  # cents
    etc_supplement = Column(Text, nullable=True)
    etc_guest_deductible = Column(Integer, nullable=True)  # cents
    total_amount_usd = Column(Integer, nullable=True)  # cents
    etc_iaa = Column(Text, nullable=True)
    etc_account_balance = Column(Text, nullable=True)  # cents
    repair_cost_usd = Column(Integer, nullable=True)  # cents
    etc_main = Column(Text, nullable=True)

    @property
    def car_name_plate(self):
        return self.car.car_name_plate()

    @property
    def source(self):
        return self.car.platform

    @property
    def driver(self):
        if not self.reservation_type:
            return '-'
        elif self.reservation_type == "turo":
            reservation = TuroReservation.query.filter(TuroReservation.turo_id == self.reservation_id).first()
            return f'{reservation.driver_main.fullname()} {reservation.driver_main.phone} {reservation.driver_main.email}'
        else:
            reservation = Booking.query.filter(Booking.id == self.reservation_id).first()
            return f'{reservation.client_name} {reservation.client_phone} {reservation.client_email}'

    @property
    def damages_list(self):
        return CarDamage.query.filter(CarDamage.claim_id == self.id).all()

    @property
    def host(self):
        return self.car.owner.fullname()
