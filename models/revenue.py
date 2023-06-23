import enum

from sqlalchemy import Enum, Column, Integer, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship

from models import base


class ReservationType(enum.Enum):
    self = "self"
    turo = "turo"


class CarRevenue(base):
    __tablename__ = "car_revenues"
    id = Column(Integer, primary_key=True)
    created = Column(DateTime, nullable=False)
    date_stat = Column(DateTime, nullable=False)
    car_id = Column(Integer, ForeignKey('cars.id'), nullable=False)
    car = relationship('Car')
    price_day = Column(Integer, nullable=True)
    price_day_turo = Column(Integer, nullable=True)
    day_in_trip = Column(Boolean(), nullable=False)
    revenue = Column(Integer, nullable=True)
    revenue_plan = Column(Integer, nullable=True)
    rate = Column(Integer, nullable=True)
    final_data = Column(Boolean(), nullable=False)
    reservation_type = Column(Enum(ReservationType), nullable=False)
