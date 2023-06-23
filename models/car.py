import enum
import json
import logging
from calendar import monthrange
from datetime import datetime, timedelta

from sqlalchemy import func, Column, Integer, DateTime, ForeignKey, String, Text, Numeric, Enum, Float, Boolean
from sqlalchemy.orm import relationship

from . import base
from .booking import Booking, ORDER_STATUS_PAID, ORDER_STATUS_NEW, ORDER_STATUS_CHECKIN_PROGRESS, \
    ORDER_STATUS_IN_TRIP, ORDER_STATUS_CHECKOUT_PROGRESS
from .car_event import CarEventType, CarEvent
from .config import S3_CDN_ENDPOINT, S3_ENDPOINT
from .insurance import CarInsurance
from .transaction import Transaction
from .turo_reservation import TuroReservation

CAR_STATUS_PENDING = 0
CAR_STATUS_ACTIVE = 1
CAR_STATUS_INACTIVE = 2
CAR_STATUS_RECALL = 3
CAR_STATUS_DELETED = 10

CAR_OWNER_UNDEFINED = 0
CAR_OWNER_COHOST = 1
CAR_OWNER_PARTNER = 2
CAR_OWNER_FINANCE = 3
CAR_OWNER_CARSAN = 4


class CarPaymentSystemType(enum.Enum):
    fix = 'fix'
    percent = 'percent'


class Car(base):
    __tablename__ = "cars"
    id = Column(Integer, primary_key=True)
    created = Column(DateTime, nullable=False)
    updated = Column(DateTime)
    make_id = Column(Integer, ForeignKey('car_make.id'), nullable=False)
    make = relationship('CarMake')
    model_id = Column(Integer, ForeignKey('car_models.id'), nullable=False)
    model = relationship('CarModel')
    year = Column(String(150), nullable=False)
    description = Column(Text, nullable=True)
    doors = Column(Integer, nullable=True)
    seats = Column(Integer, nullable=True)
    mpg = Column(Integer, nullable=True)
    deposit = Column(Integer, nullable=False, default=500)
    miles_included = Column(Integer, nullable=False)
    unlimited_miles_price = Column(Float, nullable=False)
    power_type = Column(String(150), nullable=True)
    plate = Column(String(150), nullable=False)
    vin = Column(String(150), nullable=True)
    comment = Column(Text, nullable=True)
    # monthly_payment = Column(Numeric(10,2), nullable=True)
    price_day = Column(Numeric(10,2), nullable=True)
    price_day_cache = Column(Numeric(10,2), nullable=True)
    rating = Column(Numeric(10,2), nullable=True)
    turo_url = Column(String(150), nullable=True)
    turo_id = Column(Integer, nullable=True, unique=True)
    platform = Column(String(32), nullable=False)
    # owner = Column(String(150), nullable=False)
    user_id = Column(Integer, nullable=False)
    # user = relationship('User')
    owner_id = Column(Integer, ForeignKey('car_owners.id'), nullable=False)
    owner = relationship('CarOwner')
    manager_id = Column(Integer, ForeignKey('managers.id'), nullable=False)
    manager = relationship('Manager')
    # photo_url = Column(String(150), nullable=True)
    location = Column(String(150), nullable=False)
    registration_link = Column(String(150), nullable=True)
    registration_expire_date = Column(DateTime)
    '''
        0 - pending
        1 - active
        2 - inactive
        3 - recall
        10 - deleted
        '''
    status = Column(Integer, nullable=False, default=0)
    '''
        0 - n/a
        1 - co-host
        2 - partner
        3 - finance
        4 - carsana
    '''
    ownership = Column(Integer, nullable=False, default=0)
    '''
        0 - n/a
        1 - sedan
        2 - coupe
        3 - SUV
        4 - Hatchback 
        5 - Convertible
        6 - Pickup
        7 - Minivan
        8 - Three-wheeler
        10 - other
    '''
    body = Column(Integer, default=0)
    # ownership - finance
    # finance_name = Column(String(150))
    finance_bank_info = Column(Text)
    finance_payment_day = Column(Integer)
    finance_monthly_payment = Column(String(32))
    finance_start_date = Column(DateTime)
    # ownership - partner
    partner_bank_info = Column(Text)
    partner_payment_day = Column(Integer)
    partner_monthly_payment = Column(String(32))
    partner_monthly_earnings = Column(String(32))
    partner_payout_day = Column(Integer)
    partner_start_date = Column(DateTime)
    # ownership - partner
    # cohost_name = Column(String(100))
    cohost_monthly_payment = Column(String(32))
    cohost_monthly_payment_percent = Column(Integer)
    cohost_payment_system_type = Column(Enum(CarPaymentSystemType))
    cohost_payout_day = Column(Integer)
    cohost_start_date = Column(DateTime)
    cohost_checkin = Column(String(150))
    revenue = Column(Integer)
    alias_name = Column(String(250))
    debug = dict()

    def is_self_hosted(self):
        return self.platform == "self"

    @property
    def odometer_list(self):
        return CarEvent.query.filter_by(
            car_id=self.id,
            event_type=CarEventType.odometer
        ).order_by(CarEvent.created.desc()).all()

    @property
    def last_odometer(self) -> int | None:
        last_odometer = CarEvent.query.filter_by(
            car_id=self.id,
            event_type=CarEventType.odometer
        ).order_by(CarEvent.created.desc()).first()
        if not last_odometer:
            return None
        return last_odometer.data_deserialize.get('mileage')

    @property
    def fuel_list(self):
        return CarEvent.query.filter_by(
            car_id=self.id,
            event_type=CarEventType.fuel
        ).order_by(CarEvent.created.desc()).all()


    @property
    def fuel(self):
        return CarEvent.query.filter_by(
            car_id=self.id,
            event_type=CarEventType.fuel
        ).order_by(CarEvent.created.desc()).first().data_deserialize.get('level')

    @property
    def get_statuses(self):
        return CarPaymentSystemType.__members__

    @property
    def allowed_deposits(self):
        return [0, 99, 150, 250, 500, 750, 1000]

    @property
    def fuel_levels(self):
        return {
            0: 'empty',
            12.5: '1/8',
            25: '1/4',
            37.5: '3/8',
            50: '1/2',
            62.5: '5/8',
            75: '3/4',
            87.5: '7/8',
            1: 'full'
        }

    @property
    def extra_miles_price_usd(self):
        return round(self.price() / 100 * 0.75, 2)

    @property
    def extra_miles_price_cents(self):
        return int(self.price() * 0.75)

    @property
    def insurance_link(self):
        return CarInsurance.query.filter_by(car_id=self.id).order_by(CarInsurance.id.desc()).first().url

    @property
    def insurance_expire_date(self):
        return CarInsurance.query.filter_by(car_id=self.id).order_by(CarInsurance.id.desc()).first().expire_date

    @property
    def insurance_expire_days_left(self):
        if not self.insurance_expire_date:
            return None
        delta = self.insurance_expire_date - datetime.utcnow()
        return delta.days

    @property
    def insurance_company(self):
        return CarInsurance.query.filter_by(car_id=self.id).order_by(CarInsurance.id.desc()).first().company


    def registration_expire_days_left(self):
        if not self.registration_expire_date:
            return None
        delta = self.registration_expire_date - datetime.utcnow()
        return delta.days

    @staticmethod
    def fix_turo_ids():
        cars = Car.query.filter(Car.turo_url != None).all()
        for c in cars:
            turo_id = c.turo_url.split('/')[-1]
            c.turo_id = turo_id
            session.commit()

    @staticmethod
    def get_status_list_from_str(status_str):
        if status_str == "pending":
            return [0]
        elif status_str == "active":
            return [1]
        elif status_str == "inactive":
            return [2]
        elif status_str == "recall":
            return [3]
        elif status_str == "deleted":
            return [10]
        else:
            return [0, 1, 2, 3]

    def count_events(self, event_type=None):
        query = CarEvent.query.filter(CarEvent.car_id == self.id)
        if event_type:
            query = query.filter(CarEvent.event_type == event_type)
        return query.count()

            
    def json_dates_booked(self):
        # return json.dumps(self.dates_booked())
        # for the front. expects array with date keys
        dates_booked_dict = self.dates_booked()
        dates_booked = []
        for k in dates_booked_dict.keys():
            dates_booked.append(k)
        return json.dumps(dates_booked)


    def dates_booked_format_adm(self):
        # format [2022,9,10], // october 10
        # from 2022-08-01
        dates_booked_dict = self.dates_booked()
        dates_list = []
        for k in dates_booked_dict.keys():
            date_obj = datetime.strptime(k, '%Y-%m-%d')
            new_date_year = date_obj.strftime('%Y')
            new_date_mon = date_obj.strftime('%-m')
            new_date_mon_corrected_for_js = int(new_date_mon) - 1
            new_date_day = date_obj.strftime('%d')
            dates_list.append(f'[{new_date_year}, {new_date_mon_corrected_for_js}, {new_date_day}],')
        return dates_list

    def is_available_now(self):
        # check for availability of now (today) + 24h
        # self-orders
        order = Booking.query.filter(
            Booking.car_id == self.id,
            Booking.date_checkout >= datetime.utcnow(),
            Booking.date_checkin <= datetime.utcnow() + timedelta(days=1),
            # Booking.status.in_([ORDER_STATUS_PAID, ORDER_STATUS_NEW])
        ).first()
        if order:
            return False

        # check for turo reservations
        # TODO move const to config or enum
        turo_valid_statuses = ['BOOKED']
        turo_reservation = TuroReservation.query.filter(
            TuroReservation.car_id == self.id,
            TuroReservation.date_reservation_end >= datetime.utcnow(),
            TuroReservation.date_reservation_start <= datetime.utcnow() + timedelta(days=1),
            TuroReservation.status_str.in_(turo_valid_statuses)
        ).first()
        if turo_reservation:
            return False
        return True

    def is_available(self, current_date: datetime) -> bool:
        # self-orders
        order = Booking.query.filter(
            Booking.car_id == self.id,
            Booking.date_checkout >= current_date,
            Booking.date_checkin <= current_date + timedelta(days=1),
        ).first()
        if order:
            return False

        # check for turo reservations
        # TODO move const to config or enum
        turo_reservation = TuroReservation.query.filter(
            TuroReservation.car_id == self.id,
            TuroReservation.date_reservation_end >= current_date,
            TuroReservation.date_reservation_start <= current_date + timedelta(days=1),
        ).first()
        if turo_reservation:
            return False
        return True

    def dates_booked_from(self, date_from: datetime) -> list:
        obj_list = []
        orders = Booking.query.filter(
            Booking.car_id == self.id,
            Booking.date_checkout > date_from,
            Booking.status.in_([ORDER_STATUS_PAID, ORDER_STATUS_NEW])
        )
        for o in orders:
            for i in range(0, o.days()):
                day = o.date_checkin + timedelta(days=i)
                obj_list.append(day)

        # extend with dates from turo calendar
        # TODO add turo orders

        obj_list.sort()
        obj_list.reverse()
        return obj_list

    def is_booked_between_dates(self, date_start: datetime, date_end: datetime) -> bool:
        # create date keys for all days between dates
        date_key_list = []
        delta = date_end - date_start
        days_cnt = delta.total_seconds() // 3600 // 24
        days_cnt_full = int(days_cnt) + 1
        date_format = "%Y-%m-%d"
        for i in range(days_cnt_full):
            date_key_obj = date_start + timedelta(days=i)
            date_key_str = date_key_obj.strftime(date_format)
            date_key_list.append(date_key_str)

        # check intersection with booked list for this dates
        is_available = True
        dates_booked = self.dates_booked()
        for date_key in date_key_list:
            if date_key in dates_booked:
                logging.info(f'{date_key=} found in dates booked')
                is_available = False
                break
        return is_available

    def dates_booked(self):
        date_format = "%Y-%m-%d"
        valid_statuses = [ORDER_STATUS_NEW, ORDER_STATUS_PAID, ORDER_STATUS_CHECKIN_PROGRESS, ORDER_STATUS_IN_TRIP, ORDER_STATUS_CHECKOUT_PROGRESS]
        orders = Booking.query.filter(
            Booking.car_id == self.id,
            # Booking.date_checkout >= datetime.utcnow(),
            Booking.status.in_(valid_statuses)
        )
        # format range of dates for json output
        dates_booked = {}
        for o in orders:
            for i in range(0, o.days()):
                day = o.date_checkin + timedelta(days=i)
                date_key = day.strftime(date_format)
                d = dict(
                    date=date_key,
                    source="carsana",
                    order_id=o.id
                )
                # dates_booked.append(d)
                dates_booked[date_key] = d

        # extend with turo reservations
        turo_reservations = TuroReservation.query.filter(TuroReservation.car_id == self.id, TuroReservation.status_str != 'CANCELLED').all()
        for tr in turo_reservations:
            delta = tr.date_reservation_end - tr.date_reservation_start
            delta_days = int(delta.total_seconds() // 3600 // 24)
            full_days = delta_days+1
            for i in range(full_days):
                date_obj = tr.date_reservation_start + timedelta(days=i)
                date_key = date_obj.strftime(date_format)
                if date_key not in dates_booked:
                    d = dict(
                        date=date_key,
                        source="turo",
                        turo_id=tr.turo_id
                    )
                    dates_booked[date_key] = d

        return dates_booked

    def turo_car_id(self):
        if not self.turo_url:
            return ""
        return self.turo_url.split('/')[-1]

    def is_active(self):
        return self.status == 1

    @staticmethod
    def fix_prices():
        cars = Car.query.all()
        for c in cars:
            price = CarPriceHistory.latest_price(c.id)
            if price > 0:
                c.price_day = price
            session.commit()

    @staticmethod
    def count_state(status_list, platform=None, location=None):
        q = Car.query.filter(Car.status.in_(status_list))
        if platform:
            q = q.filter(Car.platform == platform)
        if location:
            q = q.filter(Car.location == location)
        return q.count()

    @staticmethod
    def count_platform(platform, location=None, status_list=None):
        q = Car.query.filter(Car.platform == platform)
        if location:
            q = q.filter(Car.location == location)
        if status_list:
            q = q.filter(Car.status.in_(status_list))
        return q.count()

    @staticmethod
    def count_location(location, platform=None, status_list=None):
        q = Car.query.filter(Car.location == location)
        if platform:
            q = q.filter(Car.platform == platform)
        if status_list:
            q = q.filter(Car.status.in_(status_list))
        return q.count()

    @staticmethod
    def carby_id(car_id):
        return Car.query.filter(Car.id == car_id).first()

    @staticmethod
    def get_cars(status_list, sort, platform=None, location=None):
        q = Car.query.filter(Car.status.in_(status_list))
        if platform:
            q = q.filter(Car.platform == platform)
        if location:
            q = q.filter(Car.location == location)
        if sort == 'abc':
            return q.join(CarMake).join(CarModel).order_by(
                CarMake.name,
                CarModel.name,
                Car.year,
                Car.plate
            ).all()

        return q.order_by(Car.updated.desc()).all()

    @staticmethod
    def get_cars_all():
        data = Car.query.filter(Car.status != 10).all()
        # sort
        data_sorted = []
        data_dict = {}
        for d in data:
            key = d.car_name_plate()
            data_dict[key] = d
        for k in sorted(data_dict.keys()):
            data_sorted.append(data_dict[k])
        return data_sorted

    @staticmethod
    def get_cars_select(state="active"):
        if state == "all":
            return Car.query.filter(Car.status != 10).order_by(Car.updated.desc()).all()
        elif state == "active":
            return Car.query.join(CarModel).join(CarMake).filter(Car.status == 1).order_by(
                CarMake.name,
                CarModel.name,
                Car.year,
                Car.plate
            ).all()
        elif state == "pending":
            return Car.query.filter(Car.status == 0).order_by(Car.updated.desc()).all()
        elif state == "inactive":
            return Car.query.filter(Car.status == 2).order_by(Car.updated.desc()).all()
        elif state == "deleted":
            return Car.query.filter(Car.status == 10).order_by(Car.updated.desc()).all()

    @staticmethod
    def get_cars_active(owner_id=None):
        query = Car.query.filter(Car.status == 1)
        if owner_id:
            query = query.filter(Car.owner_id == owner_id)

        # sort
        query = query.order_by(Car.created.desc())
        return query.all()

    def location_str(self):
        if self.location == "la":
            return "Los Angeles"
        elif self.location == "mi":
            return "Miami"
        else:
            return self.location

    # def tickets(self):
    #     return CarTicket.query.filter(
    #         CarTicket.car_id == self.id,
    #         CarTicket.status != CarTicketStatus.deleted
    #     ).order_by(CarTicket.created.desc()).all()

    # def ticket(self, ticket_id):
    #     return CarTicket.query.filter_by(car_id=self.id, id=ticket_id).first()

    # co-host methods
    def diff_month(self, d1, d2):
        return (d1.year - d2.year) * 12 + d1.month - d2.month

    def earn_all_time(self):
        if self.ownership == CAR_OWNER_COHOST:
            start_date = self.cohost_start_date
            payout_day = self.cohost_payout_day
        elif self.ownership == CAR_OWNER_FINANCE:
            start_date = self.finance_start_date
            payout_day = self.finance_payment_day
        elif self.ownership == CAR_OWNER_PARTNER:
            start_date = self.partner_start_date
            payout_day = self.partner_payout_day
        else:
            return 0

        if not start_date:
            return 0
        today = datetime.utcnow()

        # detect if first mon didnt finish yet
        days_from_start_diff = datetime.now() - start_date
        days_from_start = days_from_start_diff.days


        # TODO
        # if first mon didnt finish
        # if full mon didnt start
        # FIRST MONTH CALC (from start date to the end of the mon)
        # get first month total days
        first_mon_days_count = monthrange(start_date.year, start_date.month)[1]
        if days_from_start <= first_mon_days_count:
            first_mon_days_since_start = days_from_start
            is_first_mon = True
        else:
            first_mon_days_since_start = first_mon_days_count - start_date.day
            is_first_mon = False
        first_mon_earn_per_day = (self.monthly_payment() / first_mon_days_count)
        first_mon_total_earn = first_mon_earn_per_day * first_mon_days_since_start

        # FULL MONTHS CALC
        # get first day of the first full month
        full_months_date_start = start_date + timedelta(days=first_mon_days_since_start)
        # get last day of the last mon
        full_months_date_end = today - timedelta(days=today.day)
        full_months_count = self.diff_month(full_months_date_end, full_months_date_start)
        if full_months_count > 0:
            full_months_total_earn = full_months_count * self.monthly_payment()
        else:
            full_months_total_earn = 0

        if is_first_mon:
            total_earn_since_start = self.earn_this_month()
        else:
            total_earn_since_start = first_mon_total_earn + full_months_total_earn + self.earn_this_month()

        self.debug = dict(
            car=self.car_name_plate(),
            id=self.id,
            today=today.strftime("%d-%m-%Y %H:%M"),
            earned=dict(
                first_month=dict(
                    start_date=start_date.strftime("%d-%m-%Y %H:%M"),
                    payout_day=payout_day,
                    days_in_mon=first_mon_days_count,
                    days_since_start=first_mon_days_since_start,
                    earn_per_day=first_mon_earn_per_day,
                    earned_total=first_mon_total_earn
                ),
                full_month=dict(
                    date_start=full_months_date_start.strftime("%d-%m-%Y %H:%M"),
                    date_end=full_months_date_end.strftime("%d-%m-%Y %H:%M"),
                    count=full_months_count,
                    earn_per_mon=self.monthly_payment(),
                    earned_total=full_months_total_earn,
                ),
            ),
            total_earn=total_earn_since_start
        )
        self.debug_str = ""
        for k,v in self.debug.items():
            self.debug_str += "{}:{}\n".format(k, v)
        return round(total_earn_since_start)

    def earn_this_month(self):
        """
        mon earnings / num of days this mon
        * by current day number (from 1 to 31)
        """

        # calc per day
        today = datetime.utcnow()
        this_mon_days_total_count = monthrange(today.year, today.month)[1]  # from 28 to 31
        this_mon_per_day_earn = (self.monthly_payment() / this_mon_days_total_count)

        # calc from listing day untill today
        if self.ownership != CAR_OWNER_COHOST:
            return 0
        date_start = self.cohost_start_date
        date_end = datetime.now() - timedelta(days=1)
        date_diff = date_end - date_start
        # num_full_days = date_diff.days
        this_mon_full_days = today.day - date_start.day - 1
        if this_mon_full_days > 0:
            this_mon_total_earned = this_mon_per_day_earn * this_mon_full_days
        else:
            this_mon_total_earned = 0
        if not self.debug:
            self.debug = dict()
        if not "earned" in self.debug:
            self.debug["earned"] = dict()
        self.debug["earned"]["current_month"] = dict(
            days_in_this_mon=this_mon_days_total_count,
            day_today=today.day,
            full_days_passed=this_mon_full_days,
            earn_per_day=this_mon_per_day_earn,
            earned_total=this_mon_total_earned,
            date_diff=date_diff,
            date_start=date_start
        )
        # return 0
        # self.debug = []
        return int(float(this_mon_total_earned))

    def last_payment_date(self):
        # if not self.cohost_payout_day:
        #     return 'n/a'
        # get current day of the mon
        today = datetime.utcnow()
        # today is 23
        # cohost is 10
        days_diff = today.day - self.cohost_payout_day
        # diff = 13
        last = today - timedelta(days=days_diff)
        return last

    def next_payment(self):
        if not self.cohost_payout_day:
            return 'n/a'
        # get current day of the mon
        today = datetime.utcnow()
        if today.day > self.cohost_payout_day:
            next_date = today + timedelta(weeks=4)
        else:
            next_date = today
        mon_str = next_date.strftime("%b")
        return "{} {}".format(self.cohost_payout_day, mon_str)

    def transactions(self):
        # return Transaction.query.filter_by(car_id=self.id).order_by(Transaction.tx_date.desc()).all()
        return Transaction.get_car_txs(self.id)

    def upcoming_transactions(self):
        txs_upcoming, txs_upcoming_total = Transaction.get_upcoming(car_id=self.id)
        return txs_upcoming, txs_upcoming_total

    # DEPRECATED
    def total_earnings(self):
        q = Transaction.query.with_entities(func.sum(Transaction.amount).label('total')).filter_by(
            car_id=self.id,
            direction="IN",
            is_deleted=False
        ).all()
        if len(q[0]) == 0:
            return 0
        if not q[0][0]:
            return 0
        return int(q[0][0])

        # TODO move to query with sum
        txs = Transaction.query.filter_by(car_id=self.id, direction="IN", is_deleted=False).all()
        # txs_out = Transaction.query.filter_by(car_id=self.id, direction="OUT").all()
        total_in = 0
        for t in txs:
            total_in += t.amount
        return total_in

    def monthly_payment(self):
        if self.ownership == CAR_OWNER_UNDEFINED:
            return 0
        elif self.ownership == CAR_OWNER_COHOST:
            if self.cohost_payment_system_type == CarPaymentSystemType.percent:
                return 0
            if not self.cohost_monthly_payment:
                return 0
            return int(float(self.cohost_monthly_payment))
        elif self.ownership == CAR_OWNER_PARTNER:
            if self.partner_monthly_payment:
                return int(float(self.partner_monthly_payment))
            return 0
        elif self.ownership == CAR_OWNER_FINANCE:
            if self.finance_monthly_payment:
                return int(float(self.finance_monthly_payment))
            return 0
        elif self.ownership == CAR_OWNER_CARSAN:
            return 0

    def price(self):
        if self.price_day:
            return int(float(self.price_day))

        if self.platform == "turo":
            price = CarPriceHistory.latest_price(self.id)
            if not price:
                return 0
            return price
        elif self.platform == "self" and self.price_day:
            return int(float(self.price_day))
        else:
            return 0

    def body_str(self):
        if self.body == 0:
            return "n/a"
        elif self.body == 1:
            return "Sedan"
        elif self.body == 2:
            return "Coupe"
        elif self.body == 3:
            return "SUV"
        elif self.body == 4:
            return "Hatchback"
        elif self.body == 5:
            return "Convertible"
        elif self.body == 6:
            return "Pickup"
        elif self.body == 7:
            return "Minivan"
        elif self.body == 8:
            return "Three-wheeler"
        elif self.body == 10:
            return "Other"

    def ownership_str(self):
        if self.ownership == CAR_OWNER_UNDEFINED:
            return "n/a"
        elif self.ownership == CAR_OWNER_COHOST:
            return "Co-host"
        elif self.ownership == CAR_OWNER_PARTNER:
            return "Partner"
        elif self.ownership == CAR_OWNER_FINANCE:
            return "Finance"
        elif self.ownership == CAR_OWNER_CARSAN:
            return "Carsana"

    def status_str(self):
        if self.status == 0:
            return "Pending"
        elif self.status == 1:
            return "Active"
        elif self.status == 2:
            return "Inactive"
        elif self.status == 3:
            return "Recall"
        elif self.status == 10:
            return "Deleted"
        else:
            return "Status {}".format(self.status)

    def car_name(self):
        return f'{self.make.name} {self.model.name} {self.year}'

    def car_name_plate(self):
        return f'{self.make.name} {self.model.name} {self.year} {self.plate}'

    def car_name_plate_id(self):
        return f'#{self.id} {self.make.name} {self.model.name} {self.year} {self.plate}'

    def main_photo(self):
        # check for main photo, if not exists - show first
        main_photo = CarPhoto.query.filter_by(car_id=self.id, is_main=True).first()
        if main_photo:
            return main_photo
        return CarPhoto.query.filter_by(car_id=self.id).first()

    # DEPRECATED, use get_url
    def main_photo_url(self):
        main_photo = self.main_photo()
        if not main_photo:
            return None
        return main_photo.get_url_big()

    # DEPRECATED, use get_url
    def photo_tn_url(self):
        main_photo = self.main_photo()
        return main_photo.get_url_tn()

    def photos(self, include_main=True):
        q = CarPhoto.query.filter_by(car_id=self.id, status=1)
        if not include_main:
            q = q.filter_by(is_main=False)
        return q.order_by(CarPhoto.weight.asc()).all()

    def price_day_rounded(self):
        try:
            price = self.price()
            if not price:
                return 0
            return int(price)
        except:
            return 0

    # def update_price(self, price):
    #     """
    #     returns
    #     was_updated (bool), error (str)
    #     """
    #     try:
    #         new_price = int(float(price))
    #         old_price_obj = CarPriceHistory.latest_price_obj(self.id)
    #         if old_price_obj:
    #             old_price = old_price_obj.price
    #             delta = datetime.utcnow() - old_price_obj.created
    #         else:
    #             old_price = 0
    #             delta = datetime.utcnow() - datetime.utcnow()
    #         # print("{}/{}".format(old_price, new_price))
    #         # if prices are the same but 1 day passed - add anyway for statistics
    #
    #         is_old = delta.days > 0
    #         if new_price == old_price and is_old:
    #             logging.info("car {} new price the same but adding anyways ({} sec old)".format(self.id, timedelta.total_seconds()))
    #         if new_price != old_price or is_old:
    #             p = CarPriceHistory(
    #                 created=datetime.utcnow(),
    #                 price=new_price,
    #                 car_id=self.id
    #             )
    #             session.add(p)
    #             # used in catalog for sorting
    #             self.price_day_cache = new_price
    #             self.updated = datetime.utcnow()
    #             session.commit()
    #             # TODO add logs
    #             logging.info('car {} price updated {} -> {}'.format(self.id, old_price, new_price))
    #             return True, None
    #         else:
    #             # TODO remove later, no need, just to reset some cache for now
    #             self.updated = datetime.utcnow()
    #             logging.info("car {} has the same price {}".format(self.id, old_price))
    #             return False, None
    #     except Exception as e:
    #         logging.error(f'update_price error:{e}')
    #         return False, str(e)

    # def update_description(self, description):
    #     if self.description != description:
    #         self.description = description
    #         self.updated = datetime.utcnow()
    #         session.commit()
    #         return True
    #     return False

    @staticmethod
    def helper_format_date_js(date_obj: object) -> object:
        # format to js
        new_date_year = date_obj.strftime('%Y')
        new_date_mon = date_obj.strftime('%-m')
        new_date_mon_corrected_for_js = int(new_date_mon) - 1
        new_date_day = date_obj.strftime('%d')
        return f'[{new_date_year}, {new_date_mon_corrected_for_js}, {new_date_day}]'

    def helper_construct_calendar_dates(self, date_from: datetime) -> dict:
        # date-time
        date_format = "%m/%d/%Y"
        # TODO fix timezone
        # tz = pytz.timezone('America/Los_Angeles')
        # one_day = date_from + timedelta(days=1)
        # two_days = date_from + timedelta(days=2)

        date_from_str = datetime.strftime(date_from, date_format)
        calendar_date_min = Car.helper_format_date_js(date_from)
        calendar_selected_date = datetime.strftime(date_from, date_format)

        # construct min - max date for the js calendar
        dates_booked = self.dates_booked_from(date_from)
        calendar_date_max = None
        nearest_reservation_date_obj = None
        days_available = None
        if len(dates_booked) > 0:
        # if None:
            # nearest_reservation_date_obj = datetime.strptime(dates_booked[0], '%Y-%m-%d')
            # nearest_reservation_date_obj = datetime.strftime(dates_booked[0], '%Y-%m-%d')
            nearest_reservation_date_obj = dates_booked[0]
            # offset 1 day to block calendar
            nearest_offset = dates_booked[0] - timedelta(days=1)
            # check for avaiability at all
            days_available_obj = nearest_offset - date_from
            days_available = days_available_obj.days
            # format to js
            new_date_year = nearest_offset.strftime('%Y')
            new_date_mon = nearest_offset.strftime('%-m')
            new_date_mon_corrected_for_js = int(new_date_mon) - 1
            new_date_day = nearest_offset.strftime('%d')
            calendar_date_max = f'[{new_date_year}, {new_date_mon_corrected_for_js}, {new_date_day}]'

        # construct time range for selector
        time_range = []
        pm = []
        for h in range(8, 12):
            if h < 10:
                h = f'0{h}'

            for m in ["00", "30"]:
                t = f'{h}:{m}'
                time_range.append(f'{t} AM')

        pm.append("12:00 PM")
        pm.append("12:30 PM")
        for h in range(1, 8):
            if h < 10:
                h = f'0{h}'
            for m in ["00", "30"]:
                t = f'{h}:{m}'
                pm.append(f'{t} PM')
        pm.append("08:00 PM")
        time_range.extend(pm)

        return dict(
            date_from=date_from,
            date_from_str=date_from_str,
            calendar_selected_date=calendar_selected_date,
            range=time_range,
            calendar_date_max=calendar_date_max,
            calendar_date_min=calendar_date_min,
            nearest_reservation_date_obj=nearest_reservation_date_obj,
            dates_booked=dates_booked,
            days_available=days_available
        )


class CarMake(base):
    __tablename__ = "car_make"
    id = Column(Integer, primary_key=True)
    name = Column(String(80), nullable=False)

    def __repr__(self):
        return '<CarMake %r>' % self.id


class CarModel(base):
    __tablename__ = "car_models"
    id = Column(Integer, primary_key=True)
    name = Column(String(80), nullable=False)
    make_id = Column(Integer, ForeignKey('car_make.id'), nullable=False)
    make = relationship('CarMake')

    def __repr__(self):
        return '<CarModel %r>' % self.id


class CarOwner(base):
    __tablename__ = "car_owners"
    id = Column(Integer, primary_key=True)
    created = Column(DateTime, nullable=False)
    updated = Column(DateTime)
    name = Column(String(150), nullable=False)
    last_name = Column(String(150))
    phone = Column(String(150), nullable=False)
    email = Column(String(150))
    address = Column(String(150))
    payment_method = Column(String(150))
    driver_license = Column(String(150))
    password = Column(String(150))
    comment = Column(Text)
    manager_id = Column(Integer, ForeignKey('managers.id'))
    manager = relationship('Manager')
    auth_token = Column(String(32), unique=True)
    auth_token_updated = Column(DateTime)

    def fullname(self):
        return "{} {}".format(self.name, self.last_name)

    def cnt_cars(self):
        return Car.query.filter_by(owner_id=self.id).filter(Car.status != 10).count()

    def list_cars(self):
        return Car.query.filter_by(owner_id=self.id).filter(Car.status != 10).order_by(Car.created.desc()).all()

    def list_cars_ids(self):
        cars = self.list_cars()
        list_ids = []
        for c in cars:
            list_ids.append(c.id)
        return list_ids

    def dash_total_earnings(self):
        cars = self.list_cars()
        total = 0
        for c in cars:
            if c.is_active():
                total += c.earn_all_time()
        return total
        # demo_car = Car.query.filter_by(id=18).first()
        # return demo_car.earn_all_time()

    def dash_total_paid(self):
        """
        summ amount of all the transactions with owners cars
        """

        cars_list_ids = self.list_cars_ids()
        #TODO refactor tx to signed int
        total_income = 0
        q = Transaction.query.with_entities(func.sum(Transaction.amount).label('total')).filter(
            Transaction.car_id.in_(cars_list_ids),
            Transaction.direction == "IN",
            Transaction.is_deleted == False
        ).all()
        res = q[0][0]
        if not res:
            total_income = 0
        else:
            total_income = int(res)

        # spendings
        total_spent = 0
        q2 = Transaction.query.with_entities(func.sum(Transaction.amount).label('total')).filter(
            Transaction.car_id.in_(cars_list_ids),
            Transaction.direction == "OUT",
            Transaction.is_deleted == False,
        ).all()
        res = q2[0][0]
        if not res:
            total_spent = 0
        else:
            total_spent = int(res)
        total_balance = total_income - total_spent
        return total_balance


    def earn_this_month(self):
        cars = self.list_cars()
        # return cars[0].earn_this_month()
        total = 0
        for c in cars:
            total += c.earn_this_month()
        return round(total)

    def upcoming_earnings_this_month(self):
        # TODO how much left from listed date to now minus what
        earn_this_month = self.earn_this_month()
        total_monthly = self.total_monthly()
        left = total_monthly - earn_this_month
        return round(left)

    def total_monthly(self):
        total = 0
        cars = self.list_cars()
        for car in cars:
            total += car.monthly_payment()
        return total

    def total_this_mon(self):
        # current_mon
        # TODO fix hack
        cars_ids = self.list_cars_ids()
        cars = Transaction.query.filter(Transaction.car_id.in_(cars_ids)).filter(
            Transaction.created > "2022-01-31",
            Transaction.created < "2022-03-01"
        ).all()
        totals = 0
        for c in cars:
            totals += int(c.amount)
        return totals

    def cnt_transactions(self):
        cars_ids = self.list_cars_ids()
        return Transaction.query.filter(Transaction.car_id.in_(cars_ids)).count()

    def list_transactions(self):
        cars_ids = self.list_cars_ids()
        return Transaction.query.filter(
            Transaction.car_id.in_(cars_ids),
            Transaction.is_deleted == False,
            Transaction.is_visible == True
        ).order_by(Transaction.tx_date.desc()).all()

    def upcoming_transactions(self):
        txs_upcoming, txs_upcoming_total = Transaction.get_upcoming(owner_id=self.id)
        return txs_upcoming, txs_upcoming_total

    # def token_regenerate(self):
    #     try:
    #         from hashlib import md5
    #         str = "{}{}".format(self.phone, datetime.utcnow())
    #         new_token = md5(str.encode()).hexdigest()[:5]
    #         self.auth_token = new_token
    #         self.auth_token_updated = datetime.utcnow()
    #         session.commit()
    #     except Exception as e:
    #         return False, e
    #     return True, None

    def format_phone(self):
        if not self.phone:
            return ""
        try:
            return format(int(self.phone[:-1]), ",").replace(",", "-") + self.phone[-1]
        except:
            return self.phone

    # Flask-Login integation
    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return self.id

    def get_login(self):
        return self.username

    def __repr__(self):
        return '<Owner %r>' % self.id


class CarPhoto(base):
    __tablename__ = "car_photos"
    id = Column(Integer, primary_key=True)
    created = Column(DateTime, nullable=False)
    updated = Column(DateTime)
    status = Column(Integer, nullable=False)
    car_id = Column(Integer, nullable=False)
    # used for ordering inside car gallery
    weight = Column(Integer)
    # main car photos, should be only one per car
    is_main = Column(Boolean, nullable=False)
    # url got from turo parser
    url = Column(String(150), nullable=True)
    # url got from turo parser
    url_tn = Column(String(150), nullable=True)
    size = Column(String(10), nullable=True)
    # uploaded files to s3
    big = Column(String(50), nullable=False)
    tn = Column(String(50), nullable=False)

    @staticmethod
    def list_active(car_id):
        return CarPhoto.query.filter_by(car_id=car_id, status=1).order_by(CarPhoto.weight.asc()).all()

    # TODO refactor this to one method with size
    # sizes example are XL, LG, MD, SM, XS
    # cdn url by default. for parser and tasks use not cdn
    def get_url(self, size="XL", is_blur=False, is_cdn=True):
        # TODO extend model to have diff sizes
        # ternary operator for is_cdn
        if is_cdn:
            endpoint = S3_CDN_ENDPOINT
        else:
            endpoint = S3_ENDPOINT

        dir = f'{endpoint}/_cars/{self.car_id}'
        filename = None
        if size == "XL":
            filename = self.big
        elif size == "LG":
            filename = self.big
        elif size == "MD":
            filename = self.big
        elif size == "SM":
            filename = self.tn
        elif size == "XS":
            filename = self.tn
        else:
            filename = self.big

        # TODO extend model to hold blur version as well
        if is_blur:
            filename = filename.replace(".jpg", "_blur.jpg")
        return f'{dir}/{filename}'


    # DEPRECATED, use get_url
    def get_url_tn(self, is_blur=False):
        url = f'{S3_CDN_ENDPOINT}/_cars/{self.car_id}/{self.tn}'
        if is_blur:
            url = url.replace(".jpg", "_blur.jpg")
        # resize
        resize_prefix = "https://cars.carsan.com/cdn-cgi/image/width=200,quality=50/"
        url = resize_prefix + url
        return url

    # DEPRECATED, use get_url
    def get_url_big(self, is_blur=False):
        if is_blur:
            return f'{S3_CDN_ENDPOINT}/crsns/images/car_blur/{self.car_id}_big.jpg'
        return "{}/_cars/{}/{}".format(S3_CDN_ENDPOINT, self.car_id, self.big)


class CarPriceHistory(base):
    __tablename__ = "car_prices"
    id = Column(Integer, primary_key=True)
    created = Column(DateTime, nullable=False)
    price = Column(Integer, nullable=False)
    car_id = Column(Integer, nullable=False)

    @staticmethod
    def latest_price_obj(car_id):
        return CarPriceHistory.query.filter_by(car_id=car_id).order_by(CarPriceHistory.created.desc()).first()

    @staticmethod
    def latest_price(car_id):
        p = CarPriceHistory.latest_price_obj(car_id)
        if p:
            return p.price
        else:
            return 0
