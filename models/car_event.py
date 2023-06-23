import enum
import json

from sqlalchemy import Enum

from app.db import db


class CarEventType(enum.Enum):
    unknown = "unknown"
    service = "service"
    inspection = "inspection"
    damage = "damage"
    odometer = "odometer"
    fuel = "fuel"


class CarEvent(db.Model):
    """
    car events created by fleet managers
    types:
    inspection
    service
    damage
    """
    __tablename__ = "car_events"
    id = db.Column(db.Integer, primary_key=True)
    created = db.Column(db.DateTime, nullable=False)
    event_type = db.Column(Enum(CarEventType), nullable=False)
    car_id = db.Column(db.Integer, db.ForeignKey('cars.id'), nullable=False)
    car = db.relationship('Car')
    # common data storage for all event types
    data = db.Column(db.JSON, nullable=False)
    manager_id = db.Column(db.Integer, db.ForeignKey('managers.id'), nullable=False)
    manager = db.relationship('Manager')

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


class CarEventFile(db.Model):
    __tablename__ = "car_event_files"
    id = db.Column(db.Integer, primary_key=True)
    created = db.Column(db.DateTime, nullable=False)
    file_type = db.Column(Enum(CarEventFileType), nullable=False)
    url = db.Column(db.String(150), nullable=False)
    event_id = db.Column(db.Integer, nullable=False)
    event_type = db.Column(Enum(CarEventType), nullable=False)
    file_func = db.Column(Enum(CarEventFileFunc), nullable=False)
    is_active = db.Column(db.Boolean, nullable=True, default=True)


class CarEventClaimType(enum.Enum):
    unknown = 0
    turo = 1
    direct = 2
    self = 3 # carsan


class CarEventClaim(db.Model):
    """
    car claim event created by fleet managers
    """
    __tablename__ = "car_event_claims"
    id = db.Column(db.Integer, primary_key=True)
    created = db.Column(db.DateTime, nullable=False)
    claim_type = db.Column(Enum(CarEventClaimType), nullable=False)
    car_id = db.Column(db.Integer, db.ForeignKey('cars.id'), nullable=False)
    car = db.relationship('Car')
    reservation_id = db.Column(db.Integer, db.ForeignKey('bookings.id'), nullable=True)
    reservation = db.relationship('Booking')
    claim_number = db.Column(db.String(50), nullable=False)
    cash_repair_price_usd = db.Column(db.Numeric(10, 2), nullable=False)
    estimate_amount_usd = db.Column(db.Numeric(10, 2), nullable=False)
    estimate_photo_url = db.Column(db.String(150), nullable=False)
    supplement_amount_usd = db.Column(db.Numeric(10, 2), nullable=False)
    supplement_photo_url = db.Column(db.String(150), nullable=False)
    supplement2_amount_usd = db.Column(db.Numeric(10, 2), nullable=False)
    supplement2_photo_url = db.Column(db.String(150), nullable=False)
    repair_price_usd = db.Column(db.Numeric(10, 2), nullable=False)
    last_showup_date = db.Column(db.DateTime, nullable=False)
    comment = db.Column(db.Text)
    manager_id = db.Column(db.Integer, db.ForeignKey('managers.id'), nullable=False)
    manager = db.relationship('Manager')
