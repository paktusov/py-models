import enum
from datetime import datetime

from sqlalchemy import Enum

from app.db import db
# this import fixes celery error about Car not being defined as a key
from app.models.car import Car


class CarTicketStatus(enum.Enum):
    new = 'new'
    in_progress = 'in progress'
    paid = 'paid'
    resolved = 'resolved'
    lost = 'lost'
    declined = 'declined'
    deleted = 'deleted'
    other = 'other'


class CarTicketType(enum.Enum):
    redlight = "red light"
    speeding = "speeding"
    parking = "parking"
    tolls = "tolls"
    other = "other"


class CarTicketOCRStatus(enum.Enum):
    pending = "pending"
    success = "success"
    error = "error"


class CarTicket(db.Model):
    __tablename__ = "car_tickets"
    id = db.Column(db.Integer, primary_key=True)
    created = db.Column(db.DateTime, nullable=False)
    updated = db.Column(db.DateTime)
    car_id = db.Column(db.Integer, db.ForeignKey('cars.id'), nullable=False)
    car = db.relationship('Car')
    status = db.Column(Enum(CarTicketStatus), nullable=False, default=CarTicketStatus.new)
    ticket_type = db.Column(Enum(CarTicketType), nullable=False)
    ocr_id = db.Column(db.Integer, nullable=True)
    ocr_ref = db.Column(db.String(32), nullable=True)
    ocr_date = db.Column(db.DateTime, nullable=True)
    ocr_due_date = db.Column(db.DateTime, nullable=True)
    ocr_subtotal = db.Column(db.Integer, nullable=True)
    ocr_total = db.Column(db.Integer, nullable=True)
    ocr_vendor_name = db.Column(db.String(32), nullable=True)
    ocr_vendor_phone = db.Column(db.String(32), nullable=True)
    ocr_vendor_address = db.Column(db.String(128), nullable=True)
    ocr_vendor_logo = db.Column(db.String(128), nullable=True)
    comment = db.Column(db.Text)
    manager_id = db.Column(db.Integer, db.ForeignKey('managers.id'), nullable=True)
    manager = db.relationship('Manager')
    reservation_type = db.Column(db.Text, nullable=True)
    reservation_id = db.Column(db.Integer, nullable=True)
    amount_paid = db.Column(db.Integer, nullable=True)
    amount_refunded = db.Column(db.Integer, nullable=True)
    violation_date = db.Column(db.DateTime, nullable=True)
    ocr_status = db.Column(Enum(CarTicketOCRStatus), nullable=True)

    @staticmethod
    def enum_type():
        return CarTicketType

    @staticmethod
    def enum_status():
        return CarTicketStatus

    def type_str(self):
        if self.ticket_type == CarTicketType.redlight:
            return "Red lights"
        elif self.ticket_type == CarTicketType.speeding:
            return "Speeding"
        elif self.ticket_type == CarTicketType.parking:
            return "Parking"
        elif self.ticket_type == CarTicketType.tolls:
            return "Tolls"
        elif self.ticket_type == CarTicketType.other:
            return "Other"

    def status_str(self):
        if self.status == CarTicketStatus.new:
            return "New"
        elif self.status == CarTicketStatus.resolved:
            return "Resolved"
        elif self.status == CarTicketStatus.declined:
            return "Declined"
        elif self.ticket_type == CarTicketStatus.other:
            return "Other"

    @staticmethod
    def status_from_str(status):
        if status == "new":
            return CarTicketStatus.new
        elif status == "resolved":
            return CarTicketStatus.resolved
        elif status == "declined":
            return CarTicketStatus.declined
        else:
            return None

    def get_comment(self):
        if not self.comment or self.comment == "None":
            return ""
        else:
            return self.comment

    def format_date(self):
        if not self.created:
            return '-'
        return datetime.strftime(self.created, "%d %b %Y")

    def photos(self):
        return CarTicketPhoto.query.filter_by(ticket_id=self.id).all()


class CarTicketPhoto(db.Model):
    __tablename__ = "car_ticket_photos"
    id = db.Column(db.Integer, primary_key=True)
    created = db.Column(db.DateTime, nullable=False)
    updated = db.Column(db.DateTime)
    url = db.Column(db.String(150), nullable=False)
    url_preview = db.Column(db.String(150))
    ticket_id = db.Column(db.Integer, db.ForeignKey('car_tickets.id'), nullable=False)
    ticket = db.relationship('CarTicket')
    ocr_id = db.Column(db.Integer, db.ForeignKey('car_ticket_photo_ocr.id'), nullable=True)
    ocr = db.relationship('CarTicketPhotoOCR')


class CarTicketPhotoOCRStatus(enum.Enum):
    success = "success"
    error = "error"


class CarTicketPhotoOCR(db.Model):
    __tablename__ = "car_ticket_photo_ocr"
    id = db.Column(db.Integer, primary_key=True)
    created = db.Column(db.DateTime, nullable=False)
    status = db.Column(Enum(CarTicketPhotoOCRStatus), nullable=False)
    date = db.Column(db.DateTime, nullable=False)
    due_date = db.Column(db.DateTime, nullable=False)
    reference_number = db.Column(db.String(255), nullable=False)
    document_reference_number = db.Column(db.String(255), nullable=False)
    ocrid = db.Column(db.Integer, nullable=False)
    subtotal = db.Column(db.Integer, nullable=True)
    total = db.Column(db.Integer, nullable=True)
    vendor_logo = db.Column(db.String(255), nullable=True)
    vendor_name = db.Column(db.String(255), nullable=True)
    vendor_phone = db.Column(db.String(32), nullable=True)
    vendor_address = db.Column(db.String(255), nullable=True)
    # vendor_type = db.Column(db.String(32), nullable=True)
    url_preview = db.Column(db.String(255), nullable=True)
    error = db.Column(db.String(255), nullable=True)
    raw_result = db.Column(db.String(255), nullable=False)
