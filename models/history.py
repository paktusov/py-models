from app.db import db


class History(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    link = db.Column(db.String(80))
    name = db.Column(db.String(80))
    car = db.Column(db.String(120))
    dates = db.Column(db.String(120))
    notes = db.Column(db.String(120))
    hash = db.Column(db.String(120), unique=True)

    def __repr__(self):
        return '<History %r>' % self.id
