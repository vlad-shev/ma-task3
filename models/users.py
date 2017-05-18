from models.base import Base, open_base
from sqlalchemy import Column, Integer, String
from sqlalchemy_utils import JSONType


class User(Base):
    __tablename__ = 'users'

    user_id = Column(Integer(), primary_key=True, autoincrement=True)
    telegram_id = Column(Integer())
    username = Column(String())
    google_token = Column(JSONType())
    email = Column(String())
    phone = Column(Integer())

    @staticmethod
    def get_user(telegram_id):
        session = open_base()
        for user in session.query(User):
            if user.telegram_id == telegram_id:
                return user


def __init__(self, user_id, telegram_id, username, google_token, email, phone):
    self.user_id = user_id
    self.telegram_id = telegram_id
    self.username = username
    self.google_token = google_token
    self.email = email
    self.phone = phone
