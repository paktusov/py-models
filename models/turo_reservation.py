import enum
import json
import math
from functools import cached_property

from sqlalchemy import Enum

from app.db import db
from app.models.booking import Booking


# TODO refactor turo stuff into separate file
class TuroChat(db.Model):
    __tablename__ = "turo_chat"
    id = db.Column(db.Integer, primary_key=True)
    created = db.Column(db.DateTime, nullable=False)
    posted = db.Column(db.DateTime, nullable=False)
    author = db.Column(db.Integer, nullable=False)
    text = db.Column(db.String(150), nullable=False)
    booking_id = db.Column(db.Integer, nullable=True)


class TuroReceiptType(enum.Enum):
    undefined = 0
    expense = 1
    income = 2


class TuroReceipt(db.Model):
    __tablename__ = "turo_receipts"
    id = db.Column(db.Integer, primary_key=True)
    created = db.Column(db.DateTime, nullable=False)
    receipt_type = db.Column(Enum(TuroReceiptType), nullable=False)
    amount_cents = db.Column(db.Integer, nullable=False)
    label = db.Column(db.String(150), nullable=False)
    description = db.Column(db.String(150), nullable=True)
    reservation_id = db.Column(db.Integer, nullable=False)

    def amount_usd(self):
        return self.amount_cents / 100.0

    def type_expence(self):
        return TuroReceiptType.expense

    def type_income(self):
        return TuroReceiptType.income


class TuroDriver(db.Model):
    __tablename__ = "turo_drivers"
    id = db.Column(db.Integer, primary_key=True)
    created = db.Column(db.DateTime, nullable=False)
    updated = db.Column(db.DateTime)
    first_name = db.Column(db.String(150), nullable=False)
    last_name = db.Column(db.String(150), nullable=False)
    photo_url = db.Column(db.String(150), nullable=True)
    email = db.Column(db.String(128), nullable=True)
    phone = db.Column(db.String(32), nullable=True)
    approval_status = db.Column(db.String(150), nullable=True)
    turo_driver_id = db.Column(db.Integer, nullable=False)
    url = db.Column(db.String(150), nullable=True)

    def fullname(self):
        return f'{self.first_name.capitalize()} {self.last_name.capitalize()}'

    def photo_tn_url(self):
        if not self.photo_url:
            return ''
        return self.photo_url.replace('.jpg', '.84x84.jpg')

    def __repr__(self):
        return f'{self.fullname()} driver_id:{self.driver_id} turo:{self.url} phone:{self.phone} status:{self.approval_status}'


class TuroReservationStatus(enum.Enum):
    undefined = 0
    upcoming = 1
    in_trip = 2
    completed = 3


class TuroReservation(db.Model):
    __tablename__ = "turo_reservations"
    id = db.Column(db.Integer, primary_key=True)
    created = db.Column(db.DateTime, nullable=False)
    updated = db.Column(db.DateTime)
    turo_id = db.Column(db.Integer, nullable=False, unique=True)
    car_id = db.Column(db.Integer, db.ForeignKey('cars.id'), nullable=False)
    # car_id = db.Column(db.Integer, nullable=False)
    car = db.relationship('Car')
    # status = db.Column(Enum(TuroReservationStatus), nullable=False)
    # COMPLETED, CANCELLED | BOOKED
    status_str = db.Column(db.String(32), nullable=False)
    # drivers
    driver_main_id = db.Column(db.Integer, db.ForeignKey('turo_drivers.id'), nullable=False)
    # driver_main_id = db.Column(db.Integer, nullable=False)
    driver_main = db.relationship('TuroDriver')
    # driver_additional_id = db.Column(db.Integer, db.ForeignKey('turo_drivers.id'), nullable=True)
    # driver_additional = db.relationship('TuroDriver')
    # dates
    date_reservation_end = db.Column(db.DateTime)
    date_reservation_start = db.Column(db.DateTime)
    date_turo_created = db.Column(db.DateTime)
    date_trip_end = db.Column(db.DateTime)
    date_trip_start = db.Column(db.DateTime)
    # odometer
    check_in_mi = db.Column(db.Integer)
    check_out_mi = db.Column(db.Integer)
    distance_limit_mi = db.Column(db.Integer)
    distance_mi = db.Column(db.Integer)
    excess_distance_mi = db.Column(db.Integer)
    is_unlimited_mi = db.Column(db.Boolean)
    latest_odometer_mi = db.Column(db.Integer)
    city = db.Column(db.String(12))
    raw_json = db.Column(db.Text)

    @staticmethod
    def get_turo_reservations_select():
        return TuroReservation.query.order_by(TuroReservation.id.desc()).all()

    def receipts(self):
        return TuroReceipt.query\
            .filter_by(reservation_id=self.turo_id)\
            .order_by(TuroReceipt.receipt_type.desc())\
            .all()

    def receipts_you_earned_usd(self):
        receipt = TuroReceipt.query.filter(
            TuroReceipt.reservation_id == self.turo_id,
            TuroReceipt.label == "You earned"
        ).order_by(TuroReceipt.receipt_type.desc()).first()
        if receipt:
            return receipt.amount_usd()
        return 0

    @staticmethod
    def calc_days(start, finish):
        delta = finish - start
        seconds = delta.total_seconds()
        days = seconds/3600/24
        days = math.ceil(days)
        if days < 1:
            days = 1
        return days

    def days(self):
        return Booking.calc_days(start=self.date_reservation_start, finish=self.date_reservation_end)

    @property
    def data_deserialize(self):
        return json.loads(self.raw_json)

    @property
    def delivered(self):
        return not self.data_deserialize['location']['addressLines'][0] == '129 East Washington Boulevard'

    @cached_property
    def information(self):
        return f"#{self.turo_id} Car: {self.car.car_name_plate()} Client: {self.driver_main.fullname()}"
