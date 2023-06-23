from sqlalchemy import Column, Integer, String

from models import base


class History(base):
    id = Column(Integer, primary_key=True)
    link = Column(String(80))
    name = Column(String(80))
    car = Column(String(120))
    dates = Column(String(120))
    notes = Column(String(120))
    hash = Column(String(120), unique=True)

    def __repr__(self):
        return '<History %r>' % self.id
