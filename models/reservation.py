import enum

from sqlalchemy import Enum, Column, Integer, DateTime, String, ForeignKey, Boolean, Text
import math

from sqlalchemy.orm import relationship

from models import base
from models.booking import OrderPhoto


class ReservationStatus(enum.Enum):
    new = 'new'
    paid = 'paid'
    canceled = 'canceled'
    expired = 'expired'
    complete = 'complete'
    undefined = 'undefined'


class ReservationInsuranceType(enum.Enum):
    minimal = 'minimal'
    standard = 'standard'


class ReservationDeliveryType(enum.Enum):
    pickup = 'pickup'
    delivery = 'delivery'


class ReservationMileageType(enum.Enum):
    limited = 'limited'
    unlimited = 'unlimited'


class Reservation(base):
    __tablename__ = "reservations"
    id = Column(Integer, primary_key=True)
    created_at = Column(DateTime, nullable=False)
    updated_at = Column(DateTime)
    uuid = Column(String(130), nullable=False)
    status = Column(Enum(ReservationStatus), default=ReservationStatus.new, nullable=False)
    driver_id = Column(Integer, ForeignKey('drivers.id'), nullable=False)
    driver = relationship('Driver')
    car_id = Column(Integer, ForeignKey('cars.id'), nullable=False)
    car = relationship('Car')
    date_checkin = Column(DateTime, nullable=False)
    date_checkout = Column(DateTime, nullable=False)
    in_trip = Column(Boolean(), nullable=False)
    insurance_type = Column(Enum(ReservationInsuranceType), nullable=False)
    insurance_price = Column(Integer, nullable=False)
    delivery_type = Column(Enum(ReservationDeliveryType), nullable=False)
    delivery_price = Column(Integer, nullable=False)
    delivery_address = Column(Text)
    deposit_amount = Column(Integer, nullable=False)
    deposit_paid = Column(Boolean(), nullable=False)
    mileage_type = Column(Enum(ReservationMileageType), nullable=False)
    mileage_unlimited_price = Column(Integer, nullable=False)
    mileage_limited_included = Column(Integer, nullable=False)
    mileage_limited_price = Column(Integer, nullable=False)
    promo_code = Column(String(32))
    promo_code_discount = Column(Integer)
    car_price = Column(Integer, nullable=False)
    trip_fee_price = Column(Integer)

    @staticmethod
    def calc_days(start, finish) -> int:
        delta = finish - start
        seconds = delta.total_seconds()
        days = seconds / 3600 / 24
        days = math.ceil(days)
        if days < 1:
            days = 1
        return days

    def odometers(self) -> (int, int):
        car_odometers = self.car.odometer_list
        checkin_odometer, checkout_odometer = 0, 0
        for odometer in car_odometers:
            data = odometer.data_deserialize
            if data.get('id') != self.id:
                continue

            if data.get('type') == 'checkin':
                checkin_odometer = data.get('mileage')
                break
            elif data.get('type') == 'checkout':
                checkout_odometer = data.get('mileage')

        return checkin_odometer, checkout_odometer

    def fuels(self) -> (int, int):
        car_fuels = self.car.fuel_list
        checkin_fuel, checkout_fuel = 0, 0
        for fuel in car_fuels:
            data = fuel.data_deserialize
            if data.get('id') != self.id:
                continue

            if data.get('type') == 'checkin':
                checkin_fuel = data.get('level')
                break
            elif data.get('type') == 'checkout':
                checkout_fuel = data.get('level')

        return checkin_fuel, checkout_fuel

    def days(self) -> int:
        return self.calc_days(start=self.date_checkin, finish=self.date_checkout)

    def get_photos(self, photo_type=None):
        order_photo_query = OrderPhoto.query.filter(OrderPhoto.order_id == self.id, OrderPhoto.status == 1)
        if photo_type:
            order_photo_query = order_photo_query.filter(OrderPhoto.photo_type == photo_type)
        return order_photo_query.order_by(OrderPhoto.created.desc()).all()

    def count_photos(self, photo_type):
        return OrderPhoto.query.filter(
            OrderPhoto.order_id == self.id,
            OrderPhoto.status == 1,
            OrderPhoto.photo_type == photo_type).count()

    def insurance_price_total(self) -> int:
        return self.days() * self.insurance_price

    def car_price_total(self) -> int:
        return self.days() * self.car_price

    def trip_fee_price(self):
        if self.days() == 1:
            percents = 0.1
        elif 2 <= self.days() <= 3:
            percents = 0.075
        elif 4 <= self.days() <= 7:
            percents = 0.05
        elif 8 <= self.days() <= 30:
            percents = 0.04
        elif self.days() > 30:
            percents = 0.025
        else:
            return 0

        return int(self.car_price * percents)

    def trip_fee_price_total(self) -> int:
        return self.days() * self.trip_fee_price()

    def car_price_discount_total(self) -> int:
        if 2 <= self.days() <= 3:
            percents = 0.05
        elif 4 <= self.days() <= 7:
            percents = 0.1
        elif 8 <= self.days() <= 30:
            percents = 0.2
        elif self.days() > 30:
            percents = 0.3
        else:
            return 0

        return int(percents * self.car_price * self.days())

    def mileage_unlimited_price_total(self) -> int:
        return self.mileage_unlimited_price * self.days()

    def total_price(self) -> int:
        total_price = self.car_price_total() + self.trip_fee_price_total() \
                      + self.insurance_price_total() - self.car_price_discount_total()
        if self.mileage_type.name == "unlimited":
            total_price += self.mileage_unlimited_price_total()
        if self.delivery_type.name == "delivery":
            total_price += self.delivery_price
        return total_price




