from sqlalchemy import Column, ForeignKey, Integer, String, create_engine, DateTime, text
from sqlalchemy.orm import declarative_base, sessionmaker
from datetime import datetime
from sqlalchemy.orm import relationship

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
    price_from = Column(Integer)

    tariff = relationship("Tariff",
                          uselist=False, 
                          back_populates="car")

class Tariff(Base):
    __tablename__ = 'car_tariffs'

    id = Column(Integer,
                primary_key=True)
    car_id = Column(Integer,
                    ForeignKey('cars.id'),
                    nullable=False)
    price_1 = Column(Integer)
    deposit = Column(Integer)

    car = relationship("Car", back_populates="tariff")


Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
session = Session()


