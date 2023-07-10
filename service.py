import random

from sqlalchemy import create_engine, Column, Integer, Boolean, String, ForeignKey
from sqlalchemy import create_engine, Column, Integer, Boolean, String, ForeignKey
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import scoped_session, declarative_base, sessionmaker

from strings import *

HOST = "localhost"
PASSWORD = "postgres"
DATABASE = "backup_rasulovgi_17_01_2023"

host = HOST
password = PASSWORD
database = DATABASE

engine = create_engine(f"postgresql+psycopg2://postgres:{password}@{host}/{database}")
session = scoped_session(sessionmaker(bind=engine))
Base = declarative_base()
Base.query = session.query_property()


class Subscriber(Base):
    __tablename__ = 'subscriber'

    id = Column(String, primary_key=True)

    contact = Column(String)
    first = Column(String)
    last = Column(String)
    birthday = Column(String)
    gender = Column(String)

    username = Column(String)
    admin = Column(Boolean, default=False)
    percentage = Column(String)


class Purchases(Base):
    __tablename__ = 'purchase'

    id = Column(Integer, primary_key=True)
    assigned_subscriber = Column(String, ForeignKey("subscriber.id"))
    quantity = Column(Integer)
    total_sum = Column(Integer)
    date = Column(String)


class CardDetails(Base):
    __tablename__ = 'card'

    id = Column(Integer, primary_key=True, autoincrement=True)
    assigned_subscriber = Column(String, ForeignKey("subscriber.id"))
    holder = Column(String)
    issued = Column(String)
    name = Column(String)


Base.metadata.create_all(bind=engine)


def register_subscriber(message, contact, first, last, birthday, gender):
    username = message.from_user.username if message.from_user.username else None
    user = Subscriber(
        id=message.from_user.id,
        username=username,
        contact=contact,
        first=first,
        last=last,
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


def register_card_details(message, holder, issued, name):
    card_details = CardDetails(
        assigned_subscriber=message.from_user.id,
        holder=holder,
        issued=issued,
        name=name
    )

    session.add(card_details)

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
    result = ''
    for user in users:
        result += f'{lastName}: {user.last}\n{firstName}: {user.first}\n{phoneNumber}: {user.contact}\n-------\n'
    return result


def return_all_users():
    return session.query(Subscriber).all()


def return_card_details(user_id):
    return session.query(CardDetails).filter(CardDetails.assigned_subscriber == user_id).first()


def broadcast(message, last_name, first_name, gender):
    if gender == male:
        return f'Дорогой {last_name} {first_name} есть новости для вас.\n{message.replace("broadcast", "🆘")}'
    elif gender == female:
        return f'Дорогая {last_name} {first_name} есть новости для вас.\n{message.replace("broadcast", "🆘")}'
    else:
        return f'Дорогой/ая {last_name} {first_name} есть новости для вас.\n{message.replace("broadcast", "🆘")}'



def select_purchases(user_id):
    purchases = session.query(Purchases).filter(Purchases.assigned_subscriber == user_id).all()
    result = ''

    if len(purchases) == 0:
        return f'{emptyBag}'
    for purchase in purchases:
        result += f'{purchaseNo}: {purchase.id}\n{quantity}: {purchase.quantity}\n{price}: {purchase.total_sum} UZS\n{date}: {purchase.date}\n---\n'
    return result


def select_loyalty(user_id):
    purchases = session.query(Purchases).filter(Purchases.assigned_subscriber == user_id).all()
    result = ''

    if len(purchases) == 0:
        return f'{emptyBag}'
    total_sum = 0
    cash_back = 1
    subscriber = session.query(Subscriber).filter(Subscriber.id == user_id).first()
    for purchase in purchases:
        total_sum += purchase.total_sum
        if purchase.assigned_subscriber == subscriber.id:
            cash_back = total_sum * int(subscriber.percentage) / 100
    result += f'{loyalty} \n\n{totalSum}: {total_sum} UZS\n{cashBack}: {cash_back}'
    return result
