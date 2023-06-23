import enum

from sqlalchemy import Enum

from app.db import db


class MangerRole(enum.Enum):
    undefined = 0
    manager = 1
    fleet = 2
    admin = 777


class Manager(db.Model):
    __tablename__ = "managers"
    id = db.Column(db.Integer, primary_key=True)
    created = db.Column(db.DateTime, nullable=False)
    updated = db.Column(db.DateTime, nullable=True)
    name = db.Column(db.String(80))
    email = db.Column(db.String(120), unique=True)
    pwd_hashed = db.Column(db.String(60))
    role = db.Column(db.String(120))
    # role = db.Column(Enum(MangerRole), nullable=False)
    is_active_status = db.Column(db.Boolean, default=True)

    def is_manager(self):
        return self.role in ["manager", "admin"]

    def is_admin(self):
        return self.role == "admin"

    def fullname(self):
        return "{}".format(self.name)

    # Flask-Login integration
    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return self.id

    def get_login(self):
        return self.username

    def __repr__(self):
        return '<Manager %r>' % self.id
