import enum

from sqlalchemy import Column, Integer, DateTime, String, Boolean

from models import base


class MangerRole(enum.Enum):
    undefined = 0
    manager = 1
    fleet = 2
    admin = 777


class Manager(base):
    __tablename__ = "managers"
    id = Column(Integer, primary_key=True)
    created = Column(DateTime, nullable=False)
    updated = Column(DateTime, nullable=True)
    name = Column(String(80))
    email = Column(String(120), unique=True)
    pwd_hashed = Column(String(60))
    role = Column(String(120))
    # role = Column(Enum(MangerRole), nullable=False)
    is_active_status = Column(Boolean, default=True)

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
