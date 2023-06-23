from datetime import datetime

from app.db import db


class Settings(db.Model):
    __tablename__ = 'settings'
    id = db.Column(db.Integer, primary_key=True)
    created = db.Column(db.DateTime, nullable=False)
    updated = db.Column(db.DateTime, nullable=False)
    key = db.Column(db.String(128), unique=True, nullable=False)
    name = db.Column(db.String(64))
    value = db.Column(db.Text, nullable=False)
    manager_id = db.Column(db.Integer, db.ForeignKey('managers.id'), nullable=False)
    manager = db.relationship('Manager')

    @staticmethod
    def get_item(key):
        item = Settings.query.filter_by(name=key).first()
        if not item:
            return None
        return item

    @staticmethod
    def get_value(key):
        item = Settings.query.filter_by(name=key).first()
        if not item:
            return None
        return item.value

    @staticmethod
    def is_true(key):
        item = Settings.query.filter_by(name=key).first()
        if not item:
            return False
        return item.value == '1'

    @staticmethod
    def save(key, value):
        try:
            item = Settings.query.filter_by(name=key).first()
            if not item:
                raise Exception('item_not_found')
            item.value = value
            item.updated = datetime.utcnow()
            db.session.commit()
            return True, None
        except Exception as e:
            return False, str(e)
