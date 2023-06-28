import enum
from datetime import datetime

from sqlalchemy import Enum, Column, Integer, DateTime, ForeignKey, String, Text
from sqlalchemy.orm import relationship

from . import base
# this import fixes celery error about Car not being defined as a key
from .car import Car


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


class CarTicket(base):
    __tablename__ = "car_tickets"
    id = Column(Integer, primary_key=True)
    created = Column(DateTime, nullable=False)
    updated = Column(DateTime)
    car_id = Column(Integer, ForeignKey('cars.id'), nullable=False)
    car = relationship('Car')
    status = Column(Enum(CarTicketStatus), nullable=False, default=CarTicketStatus.new)
    ticket_type = Column(Enum(CarTicketType), nullable=False)
    ocr_id = Column(Integer, nullable=True)
    ocr_ref = Column(String(32), nullable=True)
    ocr_date = Column(DateTime, nullable=True)
    ocr_due_date = Column(DateTime, nullable=True)
    ocr_subtotal = Column(Integer, nullable=True)
    ocr_total = Column(Integer, nullable=True)
    ocr_vendor_name = Column(String(32), nullable=True)
    ocr_vendor_phone = Column(String(32), nullable=True)
    ocr_vendor_address = Column(String(128), nullable=True)
    ocr_vendor_logo = Column(String(128), nullable=True)
    comment = Column(Text)
    manager_id = Column(Integer, ForeignKey('managers.id'), nullable=True)
    manager = relationship('Manager')
    reservation_type = Column(Text, nullable=True)
    reservation_id = Column(String(128), nullable=True)
    amount_paid = Column(Integer, nullable=True)
    amount_refunded = Column(Integer, nullable=True)
    violation_date = Column(DateTime, nullable=True)
    ocr_status = Column(Enum(CarTicketOCRStatus), nullable=True)

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


class CarTicketPhoto(base):
    __tablename__ = "car_ticket_photos"
    id = Column(Integer, primary_key=True)
    created = Column(DateTime, nullable=False)
    updated = Column(DateTime)
    url = Column(String(150), nullable=False)
    url_preview = Column(String(150))
    ticket_id = Column(Integer, ForeignKey('car_tickets.id'), nullable=False)
    ticket = relationship('CarTicket')
    ocr_id = Column(Integer, ForeignKey('car_ticket_photo_ocr.id'), nullable=True)
    ocr = relationship('CarTicketPhotoOCR')


class CarTicketPhotoOCRStatus(enum.Enum):
    success = "success"
    error = "error"


class CarTicketPhotoOCR(base):
    __tablename__ = "car_ticket_photo_ocr"
    id = Column(Integer, primary_key=True)
    created = Column(DateTime, nullable=False)
    status = Column(Enum(CarTicketPhotoOCRStatus), nullable=False)
    date = Column(DateTime, nullable=False)
    due_date = Column(DateTime, nullable=False)
    reference_number = Column(String(255), nullable=False)
    document_reference_number = Column(String(255), nullable=False)
    ocrid = Column(Integer, nullable=False)
    subtotal = Column(Integer, nullable=True)
    total = Column(Integer, nullable=True)
    vendor_logo = Column(String(255), nullable=True)
    vendor_name = Column(String(255), nullable=True)
    vendor_phone = Column(String(32), nullable=True)
    vendor_address = Column(String(255), nullable=True)
    # vendor_type = Column(String(32), nullable=True)
    url_preview = Column(String(255), nullable=True)
    error = Column(String(255), nullable=True)
    raw_result = Column(String(255), nullable=False)
