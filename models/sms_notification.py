from datetime import datetime

from app.db import db


SMS_NOTIFICATION_LIMIT_SEC = 120
SMS_NOTIFICATION_STATUS_NEW = 0
SMS_NOTIFICATION_STATUS_LOCK = 1
SMS_NOTIFICATION_STATUS_SENT = 2
SMS_NOTIFICATION_STATUS_DELIVERED = 3
SMS_NOTIFICATION_STATUS_UNDELIVERED = 4
SMS_NOTIFICATION_STATUS_ERROR = 5
SMS_NOTIFICATION_STATUS_EXPIRED = 6
SMS_NOTIFICATION_STATUS_CANCELED = 7

SMS_TEXT_OWNER_ACCESS = "Hello! Here is your access link to Carsan\n\nhttps://cohost.carsan.com/a/{token}"


class SmsNotification(db.Model):
    __tablename__ = 'sms_notifications'
    id = db.Column(db.Integer, primary_key=True)
    created = db.Column(db.DateTime, nullable=False)
    updated = db.Column(db.DateTime)
    body = db.Column(db.String(256), nullable=False)
    sid = db.Column(db.String(64), unique=True)
    recipient = db.Column(db.String(32), nullable=False)
    lifetime_min = db.Column(db.Integer, default=60)
    """
    0 - new, not sent
    1 - locked for sending
    2 - sent
    3 - delivered
    4 - undelivered
    5 - error
    6 - expired
    7 - experimental, testing, do not send
    """
    status = db.Column(db.Integer, default=0)
    error = db.Column(db.String(128))

    @staticmethod
    def create(to, text):
        try:
            sms = SmsNotification(
                created=datetime.utcnow(),
                recipient=to,
                body=text
            )
            db.session.add(sms)
            db.session.commit()
            return sms.id, None
        except Exception as e:
            return None, str(e)

    def expire_in(self):
        td = datetime.utcnow() - self.created
        min_passed = td.total_seconds() / 60
        expire_in_min = self.lifetime_min - min_passed
        return int(expire_in_min)

    def is_ready_to_sent(self):
        return self.status < 2
