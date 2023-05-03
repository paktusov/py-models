from datetime import datetime

from sqlalchemy import Column, Integer, DateTime, String, Text, ForeignKey
from sqlalchemy.orm import relationship

from models import base


class Settings(base):
    __tablename__ = 'settings'
    id = Column(Integer, primary_key=True)
    created = Column(DateTime, nullable=False)
    updated = Column(DateTime, nullable=False)
    key = Column(String(128), unique=True, nullable=False)
    value = Column(Text, nullable=False)
    manager_id = Column(Integer, ForeignKey('managers.id'), nullable=False)
    manager = relationship('Manager')

    @staticmethod
    def get_item(key):
        item = Settings.query.filter_by(key=key).first()
        if not item:
            return None
        return item

    @staticmethod
    def get_value(key):
        item = Settings.query.filter_by(key=key).first()
        if not item:
            return None
        return item.value

    @staticmethod
    def is_true(key):
        item = Settings.query.filter_by(key=key).first()
        if not item:
            return False
        return item.value == '1'

    # @staticmethod
    # def save(key, value):
    #     try:
    #         item = Settings.query.filter_by(key=key).first()
    #         if not item:
    #             raise Exception('item_not_found')
    #         item.value = value
    #         item.updated = datetime.utcnow()
    #         session.commit()
    #         return True, None
    #     except Exception as e:
    #         return False, str(e)
