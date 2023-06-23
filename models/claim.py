import enum

from app.db import db
from app.models.booking import Booking
from app.models.damage import CarDamage
from app.models.turo_reservation import TuroReservation


class CarClaimStatus(enum.Enum):
    progress = "progress"
    resolved = "resolved"
    declined = "declined"
    canceled = "canceled"


class CarClaim(db.Model):
    __tablename__ = "car_claims"
    id = db.Column(db.Integer, primary_key=True)
    created = db.Column(db.DateTime, nullable=False)
    updated = db.Column(db.DateTime, nullable=False)
    status = db.Column(db.Enum(CarClaimStatus), nullable=False)
    reservation_type = db.Column(db.Text, nullable=True)
    reservation_id = db.Column(db.Text, nullable=True)
    car_id = db.Column(db.Integer, db.ForeignKey('cars.id'), nullable=False)
    car = db.relationship('Car')
    manager_id = db.Column(db.Integer, db.ForeignKey('managers.id'), nullable=False)
    manager = db.relationship('Manager')
    comment = db.Column(db.Text, nullable=True)
    body_shop_name = db.Column(db.Text, nullable=True)
    estimate_usd = db.Column(db.Integer, nullable=True)  # cents
    deductible_usd = db.Column(db.Integer, nullable=True)  # cents
    etc_supplement = db.Column(db.Text, nullable=True)
    etc_guest_deductible = db.Column(db.Integer, nullable=True)  # cents
    total_amount_usd = db.Column(db.Integer, nullable=True)  # cents
    etc_iaa = db.Column(db.Text, nullable=True)
    etc_account_balance = db.Column(db.Text, nullable=True)  # cents
    repair_cost_usd = db.Column(db.Integer, nullable=True)  # cents
    etc_main = db.Column(db.Text, nullable=True)

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
