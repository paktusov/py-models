import json
from datetime import datetime

from flask_login import current_user
from sqlalchemy import Column, Integer, DateTime, String, Text, ForeignKey
from sqlalchemy.orm import relationship

from models import base


class FleetLog(base):
    __tablename__ = "fleet_logs"
    id = Column(Integer, primary_key=True)
    created = Column(DateTime)
    item = Column(String(128))
    action = Column(String(128))
    target = Column(String(128))
    data = Column(Text)
    manager_id = Column(Integer, ForeignKey('managers.id'), nullable=True)
    manager = relationship('Manager')

    @staticmethod
    # def log(item, target):
    #     try:
    #         item = FleetLog(
    #             created=datetime.utcnow(),
    #             item=item,
    #             action="",
    #             target=target,
    #             manager_id=current_user.id
    #         )
    #         session.add(item)
    #         session.commit()
    #         return True
    #     except Exception as e:
    #         return False

    @staticmethod
    def create_log(item: str, target: str, action: str, data: any):
        log = FleetLog(
            created=datetime.utcnow(),
            item=item,
            action=action,
            target=target,
            data=json.dumps(data)
        )
        if current_user and current_user.is_authenticated:
            log.manager_id = current_user.id
        return log

    def __repr__(self):
        return '<FleetLog %r>' % self.id
