import enum

from sqlalchemy.orm import synonym

from app.config import HOST_URL_ADM
from app.db import db


class CohostStatus(enum.Enum):
    new = 'new'
    canceled = 'canceled'
    expired = 'expired'
    finished = 'finished'


class City(enum.Enum):
    la = 'la'
    miami = 'miami'


class CohostAppointment(db.Model):
    __tablename__ = "cohost_appointments"
    id = db.Column(db.Integer, primary_key=True)
    created = db.Column(db.DateTime, nullable=False)
    status = db.Column(db.Enum(CohostStatus), default=CohostStatus.new, nullable=False)
    car_details = db.Column(db.Integer, db.ForeignKey('car_models.id'), nullable=False)
    city = db.Column(db.Enum(City), nullable=False)
    mode = db.Column(db.String(50), nullable=False)
    owner_id = db.Column(db.Integer, db.ForeignKey('car_owners.id'), nullable=False)
    owner = db.relationship('CarOwner')
    appointment_date = db.Column(db.String(50), nullable=False)
    event_time = synonym("appointment_date")
    comment = db.Column(db.Text)
    updated = db.Column(db.DateTime)

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
