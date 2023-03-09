from sqlalchemy import Column, Integer, String, create_engine, DateTime, text
from sqlalchemy.orm import declarative_base, sessionmaker
from datetime import datetime


engine = create_engine('sqlite:///my_database.db')
Base = declarative_base()
current_time = datetime.now()


class CallOrder(Base):
    __tablename__ = 'call_orders'

    id = Column(Integer, primary_key=True)
    date = Column(DateTime, server_default=current_time.strftime('%Y-%m-%d %H:%M'))
    user_name = Column(String)
    phone_number = Column(String)

Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
session = Session()


