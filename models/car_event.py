import enum
import json

from sqlalchemy import Enum, Column, Integer, DateTime, ForeignKey, JSON, String, Boolean, Numeric, Text
from sqlalchemy.orm import relationship

from . import base


class CarEventType(enum.Enum):
    unknown = "unknown"
    service = "service"
    inspection = "inspection"
    damage = "damage"
    odometer = "odometer"
    fuel = "fuel"
    checkin = "check in"
    checkout = "check out"


# noinspection PyInterpreter
class CarEvent(base):
    """
    car events created by fleet managers
    types:
    inspection
    service
    damage
    """
    __tablename__ = "car_events"
    id = Column(Integer, primary_key=True)
    created = Column(DateTime, nullable=False)
    event_type = Column(Enum(CarEventType), nullable=False)
    car_id = Column(Integer, ForeignKey('cars.id'), nullable=False)
    car = relationship('Car')
    # common data storage for all event types
    data = Column(JSON, nullable=False)
    manager_id = Column(Integer, ForeignKey('managers.id'), nullable=False)
    manager = relationship('Manager')

    @property
    def car_name_plate(self):
        return self.car.car_name_plate()

    @property
    def data_deserialize(self):
        return json.loads(self.data)

    @staticmethod
    def list_form_body_parts():
        return [
            'Front bumper',
            'Back bumper',
            'Fender front driver',
            'Fender front passenger',
            'Fender back driver',
            'Fender back passenger',
            'Door front driver',
            'Door front passenger',
            'Door back driver',
            'Door back passenger',
            'Door back',
            'Threshold driver',
            'Threshold passenger',
            'Undercarriage',
            'Mechanical',
            'Glass',
            'Tires',
            'Rims',
            'Interior',
            'Roof'
        ]

    @staticmethod
    def list_form_mechanical_checks():
        return [
            'Engine start',
            'Central lock',
            'Power windows',
            'Horn',
            'Heater / AC',
            # 'AT/MT operation',
            'Wipers',
            'Steering',
            'Light - Interior',
            'Light - Turn',
            'Light - Reverse',
            'Light - Tail',
            'Light - Emergency',
            'Oil level'
        ]

    @staticmethod
    def list_form_service_type():
        return [
            'Oil',
            'Battery',
            'Tires',
            'Rims',
            'Brakes',
            'Glass',
            'Engine',
            'Transmission',
            'Suspension',
            'Filters',
            'Other'
        ]

    def photos_count(self):
        return CarEventFile.query.filter_by(event_id=self.id).count()

    def comment_short(self):
        # cached_prop is a weird func,
        # spend a lot of time to figure out how to fix 'dict is not callable' error
        # jdata = self.data_enc()
        jdata = json.loads(self.data)
        if jdata and 'comment' in jdata:
            return f"{jdata.get('comment')[:10]}..."
        return ''

    def files(self):
        return CarEventFile.query.filter_by(event_id=self.id).order_by(CarEventFile.id.desc()).all()


class CarEventFileType(enum.Enum):
    unknown = "unknown"
    image = "image"
    document = "document"


class CarEventFileFunc(enum.Enum):
    unknown = "unknown"
    photo = 'photo'
    receipt = 'receipt'


class CarEventFile(base):
    __tablename__ = "car_event_files"
    id = Column(Integer, primary_key=True)
    created = Column(DateTime, nullable=False)
    file_type = Column(Enum(CarEventFileType), nullable=False)
    url = Column(String(150), nullable=False)
    event_id = Column(Integer, nullable=False)
    event_type = Column(Enum(CarEventType), nullable=False)
    file_func = Column(Enum(CarEventFileFunc), nullable=False)
    is_active = Column(Boolean, nullable=True, default=True)


class CarEventClaimType(enum.Enum):
    unknown = 0
    turo = 1
    direct = 2
    self = 3 # carsan


class CarEventClaim(base):
    """
    car claim event created by fleet managers
    """
    __tablename__ = "car_event_claims"
    id = Column(Integer, primary_key=True)
    created = Column(DateTime, nullable=False)
    claim_type = Column(Enum(CarEventClaimType), nullable=False)
    car_id = Column(Integer, ForeignKey('cars.id'), nullable=False)
    car = relationship('Car')
    reservation_id = Column(Integer, ForeignKey('bookings.id'), nullable=True)
    reservation = relationship('Booking')
    claim_number = Column(String(50), nullable=False)
    cash_repair_price_usd = Column(Numeric(10, 2), nullable=False)
    estimate_amount_usd = Column(Numeric(10, 2), nullable=False)
    estimate_photo_url = Column(String(150), nullable=False)
    supplement_amount_usd = Column(Numeric(10, 2), nullable=False)
    supplement_photo_url = Column(String(150), nullable=False)
    supplement2_amount_usd = Column(Numeric(10, 2), nullable=False)
    supplement2_photo_url = Column(String(150), nullable=False)
    repair_price_usd = Column(Numeric(10, 2), nullable=False)
    last_showup_date = Column(DateTime, nullable=False)
    comment = Column(Text)
    manager_id = Column(Integer, ForeignKey('managers.id'), nullable=False)
    manager = relationship('Manager')
