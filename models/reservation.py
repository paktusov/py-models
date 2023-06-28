import enum
from datetime import datetime
from functools import cached_property

from sqlalchemy import Enum, Column, Integer, DateTime, String, ForeignKey, Boolean, Text
import math

from sqlalchemy.orm import relationship

from . import base


class ReservationStatus(enum.Enum):
    new = 'new'
    paid = 'paid'
    in_trip = 'in trip'
    expired = 'expired'
    complete = 'complete'
    canceled = 'canceled'
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
    # driver = relationship('Driver')
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    user = relationship('User')
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
    deposit_refunded = Column(Boolean(), nullable=False)
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

    # def odometers(self) -> (int | None, int | None):
    #     car_odometer_checkin = CarOdometer.query.filter(
    #         CarOdometer.car_id == self.car.id,
    #         CarOdometer.source_uuid == self.uuid,
    #         CarOdometer.source_type == OdometerSourceType.checkin
    #     ).first()
    #
    #     if car_odometer_checkin:
    #         car_odometer_checkout = CarOdometer.query.filter(
    #             CarOdometer.car_id == self.car.id,
    #             CarOdometer.source_uuid == self.uuid,
    #             CarOdometer.source_type == OdometerSourceType.checkout
    #         ).first()
    #
    #         return getattr(car_odometer_checkin, 'odometer', None), getattr(car_odometer_checkout, 'odometer', None)

    def odometers_old(self) -> (int | None, int | None):
        checkin_odometer, checkout_odometer = None, None
        car_odometers = self.car.odometer_list
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

    # def fuels(self) -> (int | None, int | None):
    #     car_fuel_level_checkin = CarFuel.query.filter(
    #         CarFuel.car_id == self.car.id,
    #         CarFuel.source_uuid == self.uuid,
    #         CarFuel.source_type == FuelSourceType.checkin
    #     ).first()
    #
    #     car_fuel_level_checkout = CarFuel.query.filter(
    #         CarFuel.car_id == self.car.id,
    #         CarFuel.source_uuid == self.uuid,
    #         CarFuel.source_type == FuelSourceType.checkout
    #     ).first()
    #
    #     return getattr(car_fuel_level_checkin, 'fuel_level', None), getattr(car_fuel_level_checkout, 'odometer', None)

    def fuels_old(self) -> (int | None, int | None):
        checkin_fuel, checkout_fuel = None, None
        car_fuels = self.car.fuel_list
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

    # def get_photos(self, photo_type=None):
    #     order_photo_query = OrderPhoto.query.filter(OrderPhoto.order_id == self.id, OrderPhoto.status == 1)
    #     if photo_type:
    #         order_photo_query = order_photo_query.filter(OrderPhoto.photo_type == photo_type)
    #     return order_photo_query.order_by(OrderPhoto.created.desc()).all()

    # def count_photos(self, photo_type):
    #     return OrderPhoto.query.filter(
    #         OrderPhoto.order_id == self.id,
    #         OrderPhoto.status == 1,
    #         OrderPhoto.photo_type == photo_type).count()

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
        if 3 <= self.days() <= 6:
            percents = 0.2
        elif 7 <= self.days() <= 29:
            percents = 0.22
        elif self.days() >= 30:
            percents = 0.3
        else:
            return 0

        return int(percents * self.car_price * self.days())

    def mileage_unlimited_price_total(self) -> int:
        return self.mileage_unlimited_price * self.days()

    def total_promo_code_discount(self):
        if not self.promo_code_discount:
            return 0
        return self.car_price_total() * (self.promo_code_discount / 100)

    def total_price(self) -> int:
        total_price = self.car_price_total() + self.trip_fee_price_total() - self.total_promo_code_discount() \
                      + self.insurance_price_total() - self.car_price_discount_total()
        if self.mileage_type.name == "unlimited":
            total_price += self.mileage_unlimited_price_total()
        if self.delivery_type.name == "delivery":
            total_price += self.delivery_price
        return total_price

    def refund_days_left(self):
        if self.status == ReservationStatus.canceled:
            days_to_return = 7
            return days_to_return - (datetime.utcnow() - self.updated_at).days
        elif self.status == ReservationStatus.complete:
            days_to_return = 14
            return days_to_return - (datetime.utcnow() - self.date_checkout).days

    def refund_amount_usd(self):
        amount = 0
        if self.status == ReservationStatus.canceled:
            amount += self.total_price()
        if self.deposit_paid:
            amount += self.deposit_amount
        return amount

    def is_photos_deletable(self):
        if self.status in [ReservationStatus.canceled, ReservationStatus.complete]:
            return False
        return True

    @cached_property
    def information(self):
        information = f"#{self.uuid[:4]} Car: {self.car.car_name_plate()}"
        if self.user and self.user.name:
            information += f" Client: {self.user.name}"
        return information
