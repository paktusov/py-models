from app.db import db


class Proxy(db.Model):
    __tablename__ = 'proxies'
    id = db.Column(db.Integer, primary_key=True)
    created = db.Column(db.DateTime, nullable=False)
    address = db.Column(db.String(64), unique=True, nullable=False)
    headers = db.Column(db.Text)
    port = db.Column(db.Integer, nullable=False)
    status = db.Column(db.Integer, default=0, nullable=False)
    """
    0 - disabled, not working
    1 - working
    6 - error
    """
