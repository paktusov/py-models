from datetime import datetime as dt

from app.db import db


class CarInsurance(db.Model):
    __tablename__ = "car_insurances"
    id = db.Column(db.Integer, primary_key=True)
    created = db.Column(db.DateTime, default=dt.utcnow, nullable=False)
    car_id = db.Column(db.Integer, db.ForeignKey("cars.id"), nullable=False)
    car = db.relationship("Car")
    company = db.Column(db.String(150), nullable=False)
    expire_date = db.Column(db.Date, nullable=False)
    url = db.Column(db.String(150))
    manager_id = db.Column(db.Integer, db.ForeignKey("managers.id"), nullable=False)
    manager = db.relationship("Manager")

    @property
    def car_name_plate(self):
        return self.car.car_name_plate()

    @property
    def expire_days_left(self):
        if not self.expire_date:
            return None
        delta = self.expire_date - dt.utcnow()
        return delta.days

    @property
    def car_status(self):
        return self.car.status
