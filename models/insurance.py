from datetime import datetime as dt

from sqlalchemy import Column, Integer, DateTime, ForeignKey, String, Date
from sqlalchemy.orm import relationship

from models import base


class CarInsurance(base):
    __tablename__ = "car_insurances"
    id = Column(Integer, primary_key=True)
    created = Column(DateTime, default=dt.utcnow, nullable=False)
    car_id = Column(Integer, ForeignKey("cars.id"), nullable=False)
    car = relationship("Car")
    company = Column(String(150), nullable=False)
    expire_date = Column(Date, nullable=False)
    url = Column(String(150))
    manager_id = Column(Integer, ForeignKey("managers.id"), nullable=False)
    manager = relationship("Manager")

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
