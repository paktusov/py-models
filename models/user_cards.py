from sqlalchemy import Column, Integer, String, DateTime

from . import base


class UserCard(base):
    __tablename__ = "user_cards"

    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    uuid = Column(String(36), nullable=False)
    user_id = Column(Integer, nullable=False)
    created = Column(DateTime, nullable=False)
    token_id = Column(String(255))
    consumer_id = Column(String(255))
    card_number = Column(String(255))
    card_type_name = Column(String(255))
    card_type_code = Column(String(3))
    card_issuer = Column(String(255))
    card_scheme = Column(String(255))
    card_account_type = Column(String(255))
    card_expiration_date = Column(DateTime, nullable=False)
    card_expiration_date_str = Column(String(255))
    billing_first_name = Column(String(255))
    billing_last_name = Column(String(255))
    billing_address = Column(String(255))
    billing_city = Column(String(255))
    billing_zip = Column(String(255))
    billing_state = Column(String(255))
    billing_country = Column(String(255))
    billing_email = Column(String(255))
    billing_phone = Column(String(255))
