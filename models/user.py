from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
from sqlalchemy import DateTime

Base = declarative_base()


class User(Base):
    __tablename__ = 'users'
    user_id = Column(Integer, primary_key=True)  # User id from telegram
    username = Column(String(15))
    email = Column(String(255))
    phone = Column(String(20))
    google_token = Column(String())
    created_on = Column(DateTime(), default=datetime.now)
    updated_on = Column(DateTime(), default=datetime.now, onupdate=datetime.now)


def __init__(self, user_id, username, email, phone, google_token, created_on, updated_on):
    self.user_id = user_id
    self.username = username
    self.email = email
    self.phone = phone
    self.google_token = google_token
    self.created_on = created_on
    self.updated_on = updated_on
