from sqlalchemy import Column, Integer, DateTime, String, Text, ForeignKey
from sqlalchemy.orm import relationship

from models import base


class Settings(base):
    __tablename__ = 'settings'
    id = Column(Integer, primary_key=True)
    created = Column(DateTime, nullable=False)
    updated = Column(DateTime, nullable=False)
    key = Column(String(128), unique=True, nullable=False)
    name = Column(String(64))
    value = Column(Text, nullable=False)
    manager_id = Column(Integer, ForeignKey('managers.id'), nullable=False)
    manager = relationship('Manager')
