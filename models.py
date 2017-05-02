from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base

engine = create_engine('sqlite:///SQLAlchemy_telegram_db.db', convert_unicode=True, echo=False)
Base = declarative_base()
Base.metadata.reflect(engine)


class Users(Base):
    __table__ = Base.metadata.tables['users']


class Orders(Base):
    __table__ = Base.metadata.tables['buy']
