from datetime import datetime

from sqlalchemy import Column, Integer, DateTime, String

from . import base

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


class SmsNotification(base):
    __tablename__ = 'sms_notifications'
    id = Column(Integer, primary_key=True)
    created = Column(DateTime, nullable=False)
    updated = Column(DateTime)
    body = Column(String(256), nullable=False)
    sid = Column(String(64), unique=True)
    recipient = Column(String(32), nullable=False)
    lifetime_min = Column(Integer, default=60)
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
    status = Column(Integer, default=0)
    error = Column(String(128))

    def expire_in(self):
        td = datetime.utcnow() - self.created
        min_passed = td.total_seconds() / 60
        expire_in_min = self.lifetime_min - min_passed
        return int(expire_in_min)

    def is_ready_to_sent(self):
        return self.status < 2
