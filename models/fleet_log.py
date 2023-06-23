import json
from datetime import datetime

from flask_login import current_user

from app.db import db


class FleetLog(db.Model):
    __tablename__ = "fleet_logs"
    id = db.Column(db.Integer, primary_key=True)
    created = db.Column(db.DateTime)
    item = db.Column(db.String(128))
    action = db.Column(db.String(128))
    target = db.Column(db.String(128))
    data = db.Column(db.Text)
    manager_id = db.Column(db.Integer, db.ForeignKey('managers.id'), nullable=True)
    manager = db.relationship('Manager')

    @staticmethod
    def log(item, target):
        try:
            item = FleetLog(
                created=datetime.utcnow(),
                item=item,
                action="",
                target=target,
                manager_id=current_user.id
            )
            db.session.add(item)
            db.session.commit()
            return True
        except Exception as e:
            return False

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
