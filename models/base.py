from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

engine = create_engine('sqlite:///ma-task.sqlite', connect_args={'check_same_thread':False})
Base = declarative_base()


def open_base():
    from models.users import User
    from models.orders import Order
    Base.metadata.create_all(engine)
    Base.metadata.bind = engine
    DBSession = sessionmaker(bind=engine)
    session = DBSession()
    return session
