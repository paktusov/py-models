from sqlalchemy import Column, Integer, DateTime, String, Text

from models import base


class Proxy(base):
    __tablename__ = 'proxies'
    id = Column(Integer, primary_key=True)
    created = Column(DateTime, nullable=False)
    address = Column(String(64), unique=True, nullable=False)
    headers = Column(Text)
    port = Column(Integer, nullable=False)
    status = Column(Integer, default=0, nullable=False)
    """
    0 - disabled, not working
    1 - working
    6 - error
    """

    def test(self):
        return self.address
