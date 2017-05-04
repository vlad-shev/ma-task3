from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine

engine = create_engine('sqlite:///SQLAlchemy_telegram_v5.db', convert_unicode=True, echo=False,
                       connect_args={'check_same_thread': False})
Base = declarative_base()
Base.metadata.reflect(engine)


class Users(Base):
    __table__ = Base.metadata.tables['user']


class Orders(Base):
    __table__ = Base.metadata.tables['buy']
