from sqlalchemy import Column, Integer, String, create_engine, DateTime, text
from sqlalchemy.orm import declarative_base, sessionmaker
from datetime import datetime


engine = create_engine('sqlite:///my_database.db')
Base = declarative_base()


class CallOrder(Base):
    __tablename__ = 'call_orders'

    id = Column(Integer, primary_key=True)
    date = Column(String)
    user_name = Column(String)
    phone_number = Column(String)

class Car(Base):
    __tablename__ = 'cars'

    id = Column(Integer, primary_key=True)
    photo = Column(String)
    car_brand = Column(String)
    year = Column(String)
    transmission = Column(String)
    air_cold = Column(String)


Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
session = Session()


