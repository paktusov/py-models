import random
from datetime import datetime, timedelta

from sqlalchemy import Integer, Column, DateTime, Numeric, String, ForeignKey, Boolean
from sqlalchemy.orm import relationship

from models import base


class Transaction(base):
    __tablename__ = "transactions"
    id = Column(Integer, primary_key=True)
    created = Column(DateTime, nullable=False)
    updated = Column(DateTime, nullable=True)
    tx_date = Column(DateTime, nullable=False)
    amount = Column(Numeric(10, 2), nullable=False)
    tx_type = Column(String(10), nullable=False)
    direction = Column(String(5), nullable=False)
    comment = Column(String(150))
    hash = Column(String(64), nullable=False, unique=True, index=True)
    manager_id = Column(Integer, ForeignKey('managers.id'))
    manager = relationship('Manager')
    car_id = Column(Integer, ForeignKey('cars.id'), nullable=False)
    car = relationship('Car')
    is_visible = Column(Boolean, nullable=False, default=False)
    is_deleted = Column(Boolean, nullable=False, default=False)
    invoice_url = Column(String(150))

    def transaction_date_fmt(self):
        return self.tx_date.strftime("%b %m. %Y")

    @staticmethod
    def get_car_txs(car_id):
        return Transaction.query.filter_by(car_id=car_id, is_deleted=False).order_by(Transaction.tx_date.desc()).all()

    @staticmethod
    def get_upcoming(owner_id=None, car_id=None):
        from models.car import Car
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
