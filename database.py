from sqlalchemy import Column, Integer, String, create_engine, DateTime, text
from sqlalchemy.orm import declarative_base, sessionmaker


engine = create_engine('sqlite:///my_database.db')
Base = declarative_base()

class CallOrder(Base):
    __tablename__ = 'call_orders'

    id = Column(Integer, primary_key=True)
    date = Column(DateTime, server_default=text('CURRENT_TIMESTAMP'))
    user_name = Column(String)
    phone_number = Column(String)

Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
session = Session()


