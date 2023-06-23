import enum
import math
from datetime import datetime

# from dateutil.tz import tz
from sqlalchemy import or_, Enum, Column, Integer, DateTime, String, ForeignKey, Boolean, Text, Numeric
from sqlalchemy.orm import relationship

from . import base
from .fleet_log import FleetLog
from .manager import Manager

ORDER_STATUS_NEW = 0
ORDER_STATUS_PAID = 1
ORDER_STATUS_CHECKIN_PROGRESS = 2
ORDER_STATUS_IN_TRIP = 3
ORDER_STATUS_CHECKOUT_PROGRESS = 4
ORDER_STATUS_COMPLETE = 5
ORDER_STATUS_CANCELED = 6
ORDER_STATUS_EXPIRED = 7
ORDER_STATUS_ISSUE_DAMAGE = 10


class BookingType(enum.Enum):
    undefined = 0
    normal = 1
    service = 2


# TODO rename booking to reservation
class BookingInsuranceType(enum.Enum):
    undefined = 0
    minimum = 1
    standard = 2
    none = 3


# TODO move from str to enum status
class BookingStatus(enum.Enum):
    new = 0
    paid = 1
    check_in_progress = 2
    in_trip = 3
    checkout_in_progress = 4
    complete = 5
    refunded = 6
    issue_damage = 10


class OrderPhoto(base):
    __tablename__ = "order_photos"
    id = Column(Integer, primary_key=True)
    created = Column(DateTime, nullable=False)
    updated = Column(DateTime)
    status = Column(Integer, default=1, nullable=False)
    '''
    1 - visible
    0 - hidden
    '''
    photo_type = Column(String(30), nullable=False)
    '''
    driver
    checkin
    checkout
    '''
    order_id = Column(Integer, ForeignKey('reservations.id'), nullable=False)
    manager_id = Column(Integer, ForeignKey('managers.id'), nullable=False)
    manager = relationship('Manager')
    url = Column(String(150), nullable=False)

    def __repr__(self):
        return '<OrderPhoto %r>' % self.id


class Booking(base):
    __tablename__ = "bookings"
    id = Column(Integer, primary_key=True)
    created = Column(DateTime)
    updated = Column(DateTime)
    status = Column(Integer, nullable=False, default=0)
    '''
    ORDER_STATUS_NEW = 0
    ORDER_STATUS_PAID = 1
    ORDER_STATUS_CHECKIN_PROGRESS = 2
    ORDER_STATUS_IN_TRIP = 3
    ORDER_STATUS_CHECKOUT_PROGRESS = 4
    ORDER_STATUS_COMPLETE = 5
    ORDER_STATUS_ISSUE_DAMAGE = 10
    '''
    date_checkin = Column(DateTime, nullable=False)
    date_checkout = Column(DateTime, nullable=False)
    trip = Column(String(120))
    img = Column(String(120))
    address = Column(String(120))
    link = Column(String(120))
    client_name = Column(String(120), nullable=False)
    client_phone = Column(String(120), nullable=False)
    client_email = Column(String(120), nullable=False)
    location_parking = Column(String(120), nullable=False)
    location_delivery = Column(String(120))
    location_dropoff = Column(String(120))
    delivery_price = Column(Integer, default=0)
    unlimited_mileage = Column(Boolean(), default=False)
    full_insurance = Column(Boolean(), default=False)
    insurance_type = Column(Enum(BookingInsuranceType), nullable=False)
    hash = Column(String(64), unique=True)
    # order_ref = Column(String(32), unique=True)
    odometer_start = Column(Integer)
    odometer_end = Column(Integer)
    fuel_start = Column(Integer)
    fuel_end = Column(Integer)
    deposit_usd = Column(Integer, nullable=False)
    promo_code = Column(String(32), nullable=True)
    promo_code_discount = Column(Integer, nullable=True)
    is_deposit_paid = Column(Boolean(), default=False)
    is_deposit_refunded = Column(Boolean(), default=False)
    trip_fee_day_cents = Column(Integer)
    trip_fee_total_cents = Column(Integer)
    source = Column(String(80))
    comment = Column(Text)
    note_fleet = Column(Text)
    manager_id = Column(Integer, nullable=False)
    car_id = Column(Integer, ForeignKey('cars.id'), nullable=False)
    car = relationship('Car')
    parent_reservation_id = Column(Integer, nullable=True)
    over_mileage = Column(Integer, nullable=True)
    reimbursements_mileage_usd = Column(Integer, nullable=True)
    excessive_fuel = Column(Integer, nullable=True)
    reimbursements_fuel_usd = Column(Integer, nullable=True)
    is_smoking = Column(Boolean(), nullable=True)

    @staticmethod
    def get_bookings_select():
        return Booking.query.filter(Booking.status != "6").order_by(Booking.id.desc()).all()

    @property
    def information(self):
        return f"#{self.id} Car: {self.car.car_name_plate()} Client: {self.client_name}"

    @staticmethod
    def status_name(status):
        """
        ORDER_STATUS_NEW = 0
        ORDER_STATUS_PAID = 1
        ORDER_STATUS_CHECKIN_PROGRESS = 2
        ORDER_STATUS_IN_TRIP = 3
        ORDER_STATUS_CHECKOUT_PROGRESS = 4
        ORDER_STATUS_COMPLETE = 5
        ORDER_STATUS_CANCELED = 6
        ORDER_STATUS_EXPIRED = 7
        ORDER_STATUS_ISSUE_DAMAGE = 10
        """

        if status == ORDER_STATUS_NEW:
            return "Waiting for payment"
        elif status == ORDER_STATUS_PAID:
            return "Paid"
        elif status == ORDER_STATUS_CHECKIN_PROGRESS:
            return "Check-In"
        elif status == ORDER_STATUS_IN_TRIP:
            return "In trip"
        elif status == ORDER_STATUS_CHECKOUT_PROGRESS:
            return "Check-Out"
        elif status == ORDER_STATUS_COMPLETE:
            return "Completed"
        elif status == ORDER_STATUS_CANCELED:
            return "Canceled"
        elif status == ORDER_STATUS_EXPIRED:
            return "Expired"
        elif status == ORDER_STATUS_ISSUE_DAMAGE:
            return "Issue"

    @property
    def reimbursements(self):
        return self.over_mileage or self.excessive_fuel or self.is_smoking

    @property
    def delivered(self):
        return self.location_delivery and 'Carsana' not in str(self.location_delivery)

    # @staticmethod
    # def create_from_turo(vars):
    #     random_hash = hashlib.md5(str(random.getrandbits(128)).encode()).hexdigest()
    #     status = ORDER_STATUS_NEW
    #     reservation = Booking(
    #         created=datetime.utcnow(),
    #         status=status,
    #         location_delivery=pr.location_delivery,
    #         location_dropoff=pr.location_dropoff,
    #         source='turo',
    #         date_checkin=date_checkin,
    #         date_checkout=date_checkout,
    #         car_id=pr.car_id,
    #         full_insurance=pr.full_insurance,
    #         unlimited_mileage=pr.unlimited_mileage,
    #         deposit_usd=0,
    #         hash=random_hash,
    #         delivery_price=0,
    #         comment='automatic order from turo'
    #     )
    #     session.add(reservation)
    #     session.commit()

    def last_comment(self):
        return FleetLog.query.filter_by(target=self.id, item="reservation", action="comment").order_by(FleetLog.created.desc()).first()

    # def last_comment_formatted(self):
    #     c = self.last_comment()
    #     if not c:
    #         return ''
    #     to_zone = tz.gettz('america/los_angeles')
    #     local = c.created.replace(tzinfo=tz.gettz('UTC'))
    #     converted = local.astimezone(to_zone)
    #     created = converted.strftime('%m/%d-%Y %H:%M')
    #     return f'{created} {c.manager.fullname()}: {c.data}'

    # def expire_seconds_left(self):
    #     delta = datetime.utcnow() - self.created
    #     seconds_passed = delta.total_seconds()
    #     seconds_duration = ORDER_LIMIT_EXPIRE_MIN * 60
    #     seconds_left = seconds_duration - seconds_passed
    #     seconds_left = int(float(seconds_left))
    #     if seconds_left < 0:
    #         seconds_left = 0
    #     return seconds_left

    def get_manager(self):
        if not self.manager_id:
            return None
        return Manager.query.filter_by(id=self.manager_id).first()

    def is_cancelation_free(self):
        """
        check if paid order is legible for free cancelation
        """
        # check for 24h after payment
        if self.status != ORDER_STATUS_PAID:
            return True
        delta = datetime.utcnow() - self.created
        h_passed = delta.total_seconds() / 60 / 24
        if h_passed < 25:
            return True
        return False

    def is_extended(self):
        return self.parent_reservation_id

    def get_extended_from(self):
        return Booking.query.filter_by(id=self.parent_reservation_id).first()

    def get_extended_to(self):
        return Booking.query.filter_by(parent_reservation_id=self.id).first()

    # def set_as_paid(self):
    #     try:
    #         self.status = ORDER_STATUS_PAID
    #         self.updated = datetime.utcnow()
    #         # TODO add tx id
    #         session.commit()
    #         return True, None
    #     except Exception as e:
    #         return False, str(e)

    # def set_deposit_as_paid(self):
    #     try:
    #         self.is_deposit_paid = True
    #         self.updated = datetime.utcnow()
    #         # TODO add tx id
    #         session.commit()
    #         return True, None
    #     except Exception as e:
    #         return False, str(e)

    def hash_short(self):
        return self.hash[:5]

    def is_payable(self):
        return self.status == ORDER_STATUS_NEW

    def is_paid(self):
        return self.status == ORDER_STATUS_PAID

    def insurance_type_str(self):
        if self.insurance_type == BookingInsuranceType.minimum:
            return "Minimum"
        elif self.insurance_type == BookingInsuranceType.standard:
            return "Standard"
        elif self.insurance_type == BookingInsuranceType.none:
            return "None"
        else:
            return "N/A"

    def status_str(self):
        return Booking.status_name(self.status)

    def describe(self):
        return "Res #{ID}\nHash:{HASH}\nCar: {CAR}\nFrom {DATETIME_FROM}\nTo {DATETIME_TO}\nTotal: ${TOTAL_USD}\nStatus:{STATUS}".format(
            ID=self.id,
            HASH=self.hash,
            CAR=self.car.car_name(),
            DATETIME_FROM=self.date_checkin,
            DATETIME_TO=self.date_checkout,
            TOTAL_USD=self.amount_final_before_deposit_usd(),
            STATUS=self.status_str()
        )

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
        return Booking.calc_days(start=self.date_checkin, finish=self.date_checkout)

    def insurance_price_day_usd(self):
        days = self.days()
        car_price_day = self.car.price()
        insurance_type_percents = 0
        if self.insurance_type == BookingInsuranceType.minimum:
            if days == 1:
                insurance_type_percents = 30
            else:
                insurance_type_percents = 18
        elif self.insurance_type == BookingInsuranceType.standard:
            if days == 1:
                insurance_type_percents = 50
            else:
                insurance_type_percents = 25
        day_price_cents = round(car_price_day / 100 * insurance_type_percents * 100)
        day_price_usd = day_price_cents / 100
        return day_price_usd

    def amount_total_insurance_usd(self):
        amount_day_usd = self.insurance_price_day_usd()
        days = self.days()
        total_cents = round(amount_day_usd * days * 100)
        total_usd = total_cents / 100
        return total_usd

    def price_trip_fee_day_usd(self):
        if self.trip_fee_day_cents and self.trip_fee_day_cents > 0:
            return self.trip_fee_day_cents / 100
        return 0

    def amount_total_trip_fee_usd(self):
        if self.trip_fee_total_cents and self.trip_fee_total_cents > 0:
            return self.trip_fee_total_cents / 100
        return 0

    # rent before discount
    def amount_rent_total_usd(self):
        amount_day_usd = self.car.price()
        amount_total_usd = amount_day_usd * self.days()
        return amount_total_usd

    def amount_total_after_discount_usd(self):
        discount_usd = self.discount_usd()
        amount_day_usd = self.car.price()
        amount_total_usd = amount_day_usd * self.days()
        if discount_usd:
            amount_total_usd -= discount_usd
        return amount_total_usd

    def amount_total_after_discount_promo_usd(self):
        amount_total_usd = self.amount_total_after_discount_usd()
        discount_promo_usd = self.discount_promo_usd()
        amount_total_usd -= discount_promo_usd
        return amount_total_usd

    def amount_final_before_deposit_usd(self):
        amount_total_usd = self.amount_total_after_discount_promo_usd()
        if self.unlimited_mileage:
            amount_total_usd += self.unlimited_mileage_total_usd()
        if self.delivery_price:
            amount_total_usd += self.delivery_price
        # add insurance
        amount_total_usd += self.amount_total_insurance_usd()
        # add trip fee
        amount_total_usd += self.amount_total_trip_fee_usd()
        # round up cents
        amount_total_cents = round(amount_total_usd * 100)
        amount_total_usd = amount_total_cents / 100
        return amount_total_usd

    def amount_final_refund_usd(self):
        amount_usd = self.amount_final_before_deposit_usd()
        if self.deposit_usd and self.is_deposit_paid:
            amount_usd += self.deposit_usd
        return amount_usd

    def amount_final_refund_with_deposit_usd(self):
        amount_usd = self.amount_final_before_deposit_usd()
        amount_usd += self.deposit_usd
        return amount_usd

    def discount_name(self):
        return self.discount_usd(only_name=True)

    def discount_usd(self, only_name=False):
        percent_off = None
        coupon_name = None
        days_cnt = self.days()
        amount_total_cents = self.amount_rent_total_usd() * 100
        if days_cnt >= 30:
            percent_off = 20
            coupon_name = "30+ days discount, 20%"
        elif days_cnt >= 7:
            percent_off = 10
            coupon_name = "7+ days discount, 10%"
        elif days_cnt >= 3:
            percent_off = 5
            coupon_name = "3+ days discount, 5%"
        if percent_off:
            discount_amount_usd_cents = int(amount_total_cents / 100.0 * percent_off)
            discount_amount_usd = discount_amount_usd_cents/100.0
            if only_name:
                return coupon_name
            return discount_amount_usd
        return None

    def discount_promo_usd(self):
        if self.promo_code_discount and self.promo_code_discount > 0:
            amount_total_usd = self.amount_total_after_discount_usd()
            return amount_total_usd / 100 * self.promo_code_discount
        return 0

    def unlimited_milage_day_usd(self):
        return float(self.car.unlimited_miles_price)

    def unlimited_mileage_total_usd(self):
        price_usd = self.unlimited_milage_day_usd()
        days = self.days()
        return price_usd * days

    def mileage_included(self):
        miles_included = self.car.miles_included
        days = self.days()
        return miles_included * days

    # def get_photos(self, photo_type=None):
    #     if photo_type:
    #         return OrderPhoto.query.filter(
    #             OrderPhoto.order_id == self.id,
    #             OrderPhoto.status == 1,
    #             OrderPhoto.photo_type == photo_type).order_by(OrderPhoto.created.desc()).all()
    #     return OrderPhoto.query.filter(
    #         OrderPhoto.order_id == self.id,
    #         OrderPhoto.status == 1,
    #         ).order_by(OrderPhoto.created.desc()).all()

    # def count_photos(self, photo_type):
    #     return OrderPhoto.query.filter(
    #         OrderPhoto.order_id == self.id,
    #         OrderPhoto.status == 1,
    #         OrderPhoto.photo_type == photo_type).count()

    def is_photos_deletable(self):
        if self.status in [ORDER_STATUS_CANCELED, ORDER_STATUS_COMPLETE]:
            return False
        return True

    def refund_days_left(self):
        # count days from order completion until refund is possible
        days_from_complete = datetime.utcnow() - self.date_checkout
        # TODO - make it configurable
        days_left = 14 - days_from_complete.days
        return days_left

    def refund_amount_usd(self):
        amount = 0
        if self.status == ORDER_STATUS_CANCELED:
            amount += self.amount_final_before_deposit_usd()
            if self.is_deposit_paid:
                amount += self.deposit_usd
        elif self.status == ORDER_STATUS_COMPLETE:
            if self.is_deposit_paid:
                amount += self.deposit_usd
        return amount

    @staticmethod
    def refund_notifications_count():
        # TODO this is slow, need to cache
        data = Booking.query.filter(
            Booking.status.in_([ORDER_STATUS_CANCELED, ORDER_STATUS_COMPLETE]),
            Booking.deposit_usd > 0,
            Booking.is_deposit_paid == True,
        ).filter(
            or_(
                Booking.is_deposit_refunded == False,
                Booking.is_deposit_refunded == None,
            )
        ).all()
        count = 0
        for d in data:
            if d.refund_days_left() <= 0:
                count += 1
        return count

    # TODO fix with relative object column
    # def car_name(self):
    #     from app.models.car import Car
    #     car = Car.query.filter(Car.id == self.car_id).first()
    #     return f'{car.model.make.name} {car.model.name} {car.year}'

    def __repr__(self):
        return '<Booking %r>' % self.id


class BookingTransactionType(enum.Enum):
    system = 0
    manual = 1


class BookingTransaction(base):
    __tablename__ = "booking_transactions"
    id = Column(Integer, primary_key=True)
    created = Column(DateTime, nullable=False)
    amount_cents = Column(Numeric(10, 2), nullable=False)
    label = Column(String(32), nullable=False)
    tx_type = Column(Enum(BookingTransactionType), nullable=False)
    direction = Column(String(5), nullable=False)
    comment = Column(String(150))
    hash = Column(String(64), nullable=False, unique=True, index=True)
    manager_id = Column(Integer, ForeignKey('managers.id'))
    manager = relationship('Manager')
    reservation_id = Column(Integer, ForeignKey('bookings.id'), nullable=False, index=True)
    invoice_url = Column(String(150))
    raw = Column(Text)


class BookingPhotoType(enum.Enum):
    undefined = 0
    check_in_self = 1
    check_out_self = 2
    check_in_driver = 3
    check_out_driver = 4


class BookingPhoto(base):
    __tablename__ = "booking_photos"
    id = Column(Integer, primary_key=True)
    created = Column(DateTime, nullable=False)
    photo_type = Column(String(30), nullable=False)
    '''
    driver
    checkinx
    checkout
    '''
    url = Column(String(150), nullable=False)
    booking_id = Column(Integer, nullable=False)
    manager_id = Column(Integer, ForeignKey('managers.id'), nullable=False)
    manager = relationship('Manager')
