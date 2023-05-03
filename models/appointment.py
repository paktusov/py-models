import enum

from sqlalchemy import Enum, Column, Integer, DateTime, ForeignKey, String, Text
from sqlalchemy.orm import synonym, relationship

from config import HOST_URL_ADM
from models import base


class CohostStatus(enum.Enum):
    new = 'new'
    canceled = 'canceled'
    expired = 'expired'
    finished = 'finished'


class City(enum.Enum):
    la = 'la'
    miami = 'miami'


class CohostAppointment(base):
    __tablename__ = "cohost_appointments"
    id = Column(Integer, primary_key=True)
    created = Column(DateTime, nullable=False)
    status = Column(Enum(CohostStatus), default=CohostStatus.new, nullable=False)
    car_details = Column(Integer, ForeignKey('car_models.id'), nullable=False)
    city = Column(Enum(City), nullable=False)
    mode = Column(String(50), nullable=False)
    owner_id = Column(Integer, ForeignKey('car_owners.id'), nullable=False)
    owner = relationship('CarOwner')
    appointment_date = Column(String(50), nullable=False)
    event_time = synonym("appointment_date")
    comment = Column(Text)
    updated = Column(DateTime)

    @property
    def get_statuses(self):
        return CohostStatus.__members__

    @property
    def car_info(self):
        return f'{self.model.make.name} {self.model.name} {self.year}'

    @property
    def car_model(self):
        return f'{self.model.name}'

    @property
    def car_make(self):
        return f'{self.model.make.name}'

    def get_url(self):
        return f'{HOST_URL_ADM}/appointment/{self.id}'
