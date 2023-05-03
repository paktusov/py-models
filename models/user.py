from sqlalchemy import Column, Integer, String, Boolean

from models import base


class User(base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    email = Column(String(128), unique=True, nullable=False)
    active = Column(Boolean(), default=True, nullable=False)

    def __init__(self, email):
        self.email = email
