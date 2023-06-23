import enum
import random
from datetime import datetime, timedelta

from sqlalchemy import Enum

from app.db import db


class Transaction(db.Model):
    __tablename__ = "transactions"
    id = db.Column(db.Integer, primary_key=True)
    tx_date = db.Column(db.DateTime, nullable=False)
    created = db.Column(db.DateTime, nullable=False)
    updated = db.Column(db.DateTime, nullable=True)
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    tx_type = db.Column(db.String(10), nullable=False)
    comment = db.Column(db.String(150))
    manager_id = db.Column(db.Integer, db.ForeignKey('managers.id'))
    manager = db.relationship('Manager')
    car_id = db.Column(db.Integer, db.ForeignKey('cars.id'), nullable=False)
    car = db.relationship('Car')
    direction = db.Column(db.String(5), nullable=False)
    is_visible = db.Column(db.Boolean, nullable=False, default=False)
    invoice_url = db.Column(db.String(150))
    hash = db.Column(db.String(64), nullable=False, unique=True, index=True)
    is_deleted = db.Column(db.Boolean, nullable=False, default=False)

    def transaction_date_fmt(self):
        return self.tx_date.strftime("%b %m. %Y")

    @staticmethod
    def get_car_txs(car_id):
        return Transaction.query.filter_by(car_id=car_id, is_deleted=False).order_by(Transaction.tx_date.desc()).all()

    @staticmethod
    def get_upcoming(owner_id=None, car_id=None):
        from app.models.car import Car
        '''
        returns tuple (list of trasactions, total_summ)
        '''
        if car_id:
            car = Car.get_by_id(car_id)
            active_cars = [car]
        else:
            active_cars = Car.get_cars_active(owner_id=owner_id)
        txs = []
        total = 0
        for car in active_cars:
            if car.cohost_monthly_payment:
                mon_payment = int(car.cohost_monthly_payment)
            else:
                mon_payment = 123
            day_payment = round(mon_payment/30, 2)
            next_midnight = (datetime.utcnow() + timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
            tx = Transaction(
                created=next_midnight,
                tx_type="UPCOMING",
                direction="IN",
                amount=day_payment,
                car_id=car.id,
                car=Car.get_by_id(car.id),
                comment="car rent 1 day",
                hash=random.getrandbits(128)
            )
            txs.append(tx)
            total += day_payment
        total = round(total, 2)
        return txs, total

    def get_hash_short(self):
        return str(self.hash)[:6]

    def __repr__(self):
        return '<Transaction %r>' % self.id


class Category(enum.Enum):
    debit = "debit"
    credit = "credit"


class Source(enum.Enum):
    gateway = "gateway"
    manager = "manager"


class Target(enum.Enum):
    user = "user"
    reservation = "reservation"
    car = "car"


class TxType(enum.Enum):
    deposit = "deposit"
    payment = "payment"


class TransactionV1(db.Model):
    __tablename__ = "transactions_v1"
    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(db.String(36), nullable=False)
    created = db.Column(db.DateTime, nullable=False)
    tx_type = db.Column(Enum(TxType), nullable=False)
    source = db.Column(Enum(Source), nullable=False)
    source_uuid = db.Column(db.String(64))
    target = db.Column(Enum(Target))
    target_uuid = db.Column(db.String(64), nullable=False)
    amount = db.Column(db.Integer, nullable=False)
    category = db.Column(Enum(Category), nullable=False)
    description = db.Column(db.Text)
