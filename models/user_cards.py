from app.db import db


class UserCard(db.Model):
    __tablename__ = "user_cards"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True, nullable=False)
    uuid = db.Column(db.String(36), nullable=False)
    user_id = db.Column(db.Integer, nullable=False)
    created = db.Column(db.DateTime, nullable=False)
    token_id = db.Column(db.String(255))
    consumer_id = db.Column(db.String(255))
    card_number = db.Column(db.String(255))
    card_type_name = db.Column(db.String(255))
    card_type_code = db.Column(db.String(3))
    card_issuer = db.Column(db.String(255))
    card_scheme = db.Column(db.String(255))
    card_account_type = db.Column(db.String(255))
    card_expiration_date = db.Column(db.DateTime, nullable=False)
    card_expiration_date_str = db.Column(db.String(255))
    billing_first_name = db.Column(db.String(255))
    billing_last_name = db.Column(db.String(255))
    billing_address = db.Column(db.String(255))
    billing_city = db.Column(db.String(255))
    billing_zip = db.Column(db.String(255))
    billing_state = db.Column(db.String(255))
    billing_country = db.Column(db.String(255))
    billing_email = db.Column(db.String(255))
    billing_phone = db.Column(db.String(255))
