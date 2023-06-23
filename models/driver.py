import enum

from sqlalchemy import Enum, Column, Integer, DateTime, String, Text, ForeignKey
from sqlalchemy.orm import relationship

from . import base


class DriverApprovedToDrive(enum.Enum):
    approved = "approved"
    not_approved = "not approved"


class Driver(base):
    __tablename__ = "drivers"
    id = Column(Integer, primary_key=True)
    created_at = Column(DateTime, nullable=False)
    updated_at = Column(DateTime)
    phone = Column(String(150), unique=True, nullable=False)
    email = Column(String(128), nullable=True)
    uuid = Column(String(64), nullable=False)
    auth_token_refresh = Column(String(256), nullable=True)
    approved_to_drive = Column(Enum(DriverApprovedToDrive), nullable=False)
    name = Column(String(50), nullable=True)

    @property
    def pending(self):
        pending = DriverVerification.query.filter(
            DriverVerification.driver_id == self.id,
            DriverVerification.status == DriverVerificationStatus.pending,
        ).order_by(DriverVerification.created_at.desc()).first()
        if pending:
            return True
        return False

    def fullname(self):
        if self.name:
            return f'{self.name}'
        return '-'

    def full_description(self):
        description = [self.phone]
        if self.name:
            description.append(self.name)
        if self.email:
            description.append(self.email)
        return " - ".join(description)

    @staticmethod
    def get_by_phone(phone):
        return Driver.query.filter_by(phone=phone).first()


class DriverVerificationStatus(enum.Enum):
    approved = "approved"
    pending = "pending"
    declined = "declined"


class DriverVerification(base):
    __tablename__ = "driver_verifications"
    id = Column(Integer, primary_key=True)
    created_at = Column(DateTime, nullable=False)
    updated_at = Column(DateTime)
    status = Column(Enum(DriverVerificationStatus), nullable=False)
    name = Column(String(128), nullable=True)
    email = Column(String(150), nullable=True)
    photo_selfie = Column(String(128), nullable=False)
    photo_license = Column(String(128), nullable=False)
    photo_license_back = Column(String(128), nullable=False)
    decline_comment = Column(Text)
    driver_id = Column(Integer, ForeignKey('drivers.id'), nullable=False)
    driver = relationship('Driver')
    manager_id = Column(Integer, ForeignKey('managers.id'))
    manager = relationship('Manager')
    user_id = Column(Integer, ForeignKey('users.id'))
    user = relationship('User')
