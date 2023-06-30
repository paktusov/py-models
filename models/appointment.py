import enum

from sqlalchemy import Column, Integer, DateTime, Enum, String, ForeignKey, Text
from sqlalchemy.orm import synonym, relationship

from . import base


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

    def get_url(self, url):
        return f'{url}/appointment/{self.id}'


class CohostV2Status(enum.Enum):
    new = 'new'
    confirmed = 'confirmed'
    cancelled = 'cancelled'
    expired = 'expired'
    complete = 'complete'


class CohostV2Type(enum.Enum):
    appointment = 'appointment'
    call = 'call'


class CohostV2Location(enum.Enum):
    la = 'la'
    miami = 'miami'


class CohostAppointmentV2(base):
    __tablename__ = "cohost_appointments_v2"
    id = Column(Integer, primary_key=True)
    uuid = Column(String(64), nullable=False)
    created = Column(DateTime, nullable=False)
    updated = Column(DateTime, nullable=False)
    status = Column(Enum(CohostV2Status), nullable=False)
    name = Column(String(255), nullable=False)
    scheduled_date = Column(DateTime, nullable=False)
    event_time = synonym("scheduled_date")
    type = Column(Enum(CohostV2Type), nullable=False)
    location = Column(Enum(CohostV2Location), nullable=False)
    notes = Column(Text)
    car_details = Column(String(255), nullable=False)
    car_make_id = Column(Integer)
    car_model_id = Column(Integer)
    car_year = Column(String(4))
    user_id = Column(Integer, ForeignKey('users.id'))
    user = relationship('User')

