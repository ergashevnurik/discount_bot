import psycopg2
import os
from sqlalchemy import create_engine, Column, Integer, Boolean, String
from sqlalchemy.orm import scoped_session, declarative_base, sessionmaker
from sqlalchemy.exc import PendingRollbackError, IntegrityError
from strings import *

HOST = "localhost"
PASSWORD = "postgres"
DATABASE = "rasulovgi"

host = HOST
password = PASSWORD
database = DATABASE

engine = create_engine(f"postgresql+psycopg2://postgres:{password}@{host}/{database}")
session = scoped_session(sessionmaker(bind=engine))
Base = declarative_base()
Base.query = session.query_property()


class Subscriber(Base):
    __tablename__ = 'subscriber'

    id = Column(Integer, primary_key=True)

    contact = Column(String)
    firstName = Column(String)
    lastName = Column(String)
    birthday = Column(String)
    gender = Column(String)

    username = Column(String)
    admin = Column(Boolean, default=False)


Base.metadata.create_all(bind=engine)


def register_subscriber(message, contact, first_name, last_name, birthday, gender):
    username = message.from_user.username if message.from_user.username else None
    user = Subscriber(
        id=int(message.from_user.id),
        username=username,
        contact=contact,
        firstName=first_name,
        lastName=last_name,
        birthday=birthday,
        gender=gender
    )

    session.add(user)

    try:
        session.commit()
        return True
    except IntegrityError:
        session.rollback()  # откатываем session.add(user)
        return False


def select_user(user_id):
    user = session.query(Subscriber).filter(Subscriber.id == user_id).first()
    return user


def select_all_users():
    users = session.query(Subscriber).all()
    for user in users:
        return f'{lastName}: {user.lastName}\n{firstName}: {user.firstName}\n{phoneNumber}: {user.contact}\n-------'


def broadcast(message):
    users = session.query(Subscriber).all()
    for user in users:
        return f'Dear {user.name} there is news for you.\n{message.replace("broadcast", "🆘")}'
