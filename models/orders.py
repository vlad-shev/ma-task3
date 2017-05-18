from models.base import Base, open_base
from sqlalchemy import Column, ForeignKey, Integer, String, DateTime
from datetime import datetime


class Order(Base):
    __tablename__ = 'orders'

    order_id = Column(Integer(), primary_key=True, autoincrement=True)
    user_id = Column(Integer(), ForeignKey('users.user_id'))
    username = Column(String(50))
    menu = Column(String())
    address = Column(String(70))
    phone = Column(Integer())
    created_on = Column(DateTime(timezone=True), default=datetime.utcnow())

    @staticmethod
    def get_order(user_id):
        session = open_base()
        for order in session.query(Order):
            if order.user_id == user_id:
                return order


def __init__(self, order_id, user_id, username, menu, address, phone, created_on):
    self.order_id = order_id
    self.user_id = user_id
    self.username = username
    self.menu = menu
    self.address = address
    self.phone = phone
    self.created_on = created_on
