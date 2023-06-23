import enum

from sqlalchemy import Enum

from app.db import db


class DriverApprovedToDrive(enum.Enum):
    approved = "approved"
    not_approved = "not approved"


class Driver(db.Model):
    __tablename__ = "drivers"
    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, nullable=False)
    updated_at = db.Column(db.DateTime)
    phone = db.Column(db.String(150), unique=True, nullable=False)
    email = db.Column(db.String(128), nullable=True)
    uuid = db.Column(db.String(64), nullable=False)
    auth_token_refresh = db.Column(db.String(256), nullable=True)
    approved_to_drive = db.Column(Enum(DriverApprovedToDrive), nullable=False)
    name = db.Column(db.String(50), nullable=True)

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


class DriverVerification(db.Model):
    __tablename__ = "driver_verifications"
    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, nullable=False)
    updated_at = db.Column(db.DateTime)
    status = db.Column(db.Enum(DriverVerificationStatus), nullable=False)
    name = db.Column(db.String(128), nullable=True)
    email = db.Column(db.String(150), nullable=True)
    photo_selfie = db.Column(db.String(128), nullable=False)
    photo_license = db.Column(db.String(128), nullable=False)
    photo_license_back = db.Column(db.String(128), nullable=False)
    decline_comment = db.Column(db.Text)
    driver_id = db.Column(db.Integer, db.ForeignKey('drivers.id'), nullable=False)
    driver = db.relationship('Driver')
    manager_id = db.Column(db.Integer, db.ForeignKey('managers.id'))
    manager = db.relationship('Manager')
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    user = db.relationship('User')
