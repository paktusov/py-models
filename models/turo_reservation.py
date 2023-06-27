import enum
import json
import math
from functools import cached_property

from sqlalchemy import Enum, Column, Integer, DateTime, String, ForeignKey, Boolean, Text
from sqlalchemy.orm import relationship

from . import base


# TODO refactor turo stuff into separate file
class TuroChat(base):
    __tablename__ = "turo_chat"
    id = Column(Integer, primary_key=True)
    created = Column(DateTime, nullable=False)
    posted = Column(DateTime, nullable=False)
    author = Column(Integer, nullable=False)
    text = Column(String(150), nullable=False)
    booking_id = Column(Integer, nullable=True)


class TuroReceiptType(enum.Enum):
    undefined = 0
    expense = 1
    income = 2


class TuroReceipt(base):
    __tablename__ = "turo_receipts"
    id = Column(Integer, primary_key=True)
    created = Column(DateTime, nullable=False)
    receipt_type = Column(Enum(TuroReceiptType), nullable=False)
    amount_cents = Column(Integer, nullable=False)
    label = Column(String(150), nullable=False)
    description = Column(String(150), nullable=True)
    reservation_id = Column(Integer, nullable=False)

    def amount_usd(self):
        return self.amount_cents / 100.0

    def type_expence(self):
        return TuroReceiptType.expense

    def type_income(self):
        return TuroReceiptType.income


class TuroDriver(base):
    __tablename__ = "turo_drivers"
    id = Column(Integer, primary_key=True)
    created = Column(DateTime, nullable=False)
    updated = Column(DateTime)
    first_name = Column(String(150), nullable=False)
    last_name = Column(String(150), nullable=False)
    photo_url = Column(String(150), nullable=True)
    email = Column(String(128), nullable=True)
    phone = Column(String(32), nullable=True)
    approval_status = Column(String(150), nullable=True)
    turo_driver_id = Column(Integer, nullable=False)
    url = Column(String(150), nullable=True)

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


class TuroReservation(base):
    __tablename__ = "turo_reservations"
    id = Column(Integer, primary_key=True)
    created = Column(DateTime, nullable=False)
    updated = Column(DateTime)
    turo_id = Column(Integer, nullable=False, unique=True)
    car_id = Column(Integer, ForeignKey('cars.id'), nullable=False)
    # car_id = Column(Integer, nullable=False)
    car = relationship('Car')
    # status = Column(Enum(TuroReservationStatus), nullable=False)
    # COMPLETED, CANCELLED | BOOKED
    status_str = Column(String(32), nullable=False)
    # drivers
    driver_main_id = Column(Integer, ForeignKey('turo_drivers.id'), nullable=False)
    # driver_main_id = Column(Integer, nullable=False)
    driver_main = relationship('TuroDriver')
    # driver_additional_id = Column(Integer, ForeignKey('turo_drivers.id'), nullable=True)
    # driver_additional = relationship('TuroDriver')
    # dates
    date_reservation_end = Column(DateTime)
    date_reservation_start = Column(DateTime)
    date_turo_created = Column(DateTime)
    date_trip_end = Column(DateTime)
    date_trip_start = Column(DateTime)
    # odometer
    check_in_mi = Column(Integer)
    check_out_mi = Column(Integer)
    distance_limit_mi = Column(Integer)
    distance_mi = Column(Integer)
    excess_distance_mi = Column(Integer)
    is_unlimited_mi = Column(Boolean)
    latest_odometer_mi = Column(Integer)
    city = Column(String(12))
    raw_json = Column(Text)

    @staticmethod
    def get_turo_reservations_select():
        return TuroReservation.query.order_by(TuroReservation.id.desc()).all()

    # def receipts(self):
    #     return TuroReceipt.query\
    #         .filter_by(reservation_id=self.turo_id)\
    #         .order_by(TuroReceipt.receipt_type.desc())\
    #         .all()

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
        return self.calc_days(start=self.date_reservation_start, finish=self.date_reservation_end)

    @property
    def data_deserialize(self):
        return json.loads(self.raw_json)

    @property
    def delivered(self):
        return not self.data_deserialize['location']['addressLines'][0] == '129 East Washington Boulevard'

    @cached_property
    def information(self):
        return f"#{self.turo_id} Car: {self.car.car_name_plate()} Client: {self.driver_main.fullname()}"
