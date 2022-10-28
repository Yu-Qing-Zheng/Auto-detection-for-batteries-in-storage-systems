"""
# @Author: ZeKai
# @Date: 2022-03-07
"""

from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy import Column, Integer, DateTime, create_engine, Float, String

engine = create_engine('mysql+pymysql://root:123456@47.92.133.142:3306/data_preprocessing?charset=utf8',
                       pool_size=30,
                       pool_timeout=3,
                       pool_recycle=60)
Base = declarative_base()


def get_session():
    session_maker = sessionmaker(bind=engine)
    session = session_maker()
    return session

class energy_threshold(Base):
    __tablename__ = 'energy_threshold'
    plc_id = Column(Integer, primary_key=True, index=True)
    time = Column(DateTime)
    median_max_forward = Column(Float)
    median_max_reverse = Column(Float)

class diagnose_trigger(Base):
    __tablename__ = 'diagnose_trigger'
    plc_id = Column(Integer, primary_key=True, index=True)
    time = Column(DateTime)
    energy_flag = Column(Integer)

class diagnosed_date(Base):
    __tablename__ = 'diagnosed_date'
    Date = Column(DateTime, primary_key=True, index=True)

class diagnose_results(Base):
    __tablename__ = 'diagnose_results'
    plc_id = Column(Integer, primary_key=True, index=True)
    time = Column(DateTime)
    bat_id = Column(String(255))
    voltage = Column(Float)
    current = Column(Float)
    temperature = Column(Float)
    soc = Column(Float)
    soc_bound = Column(Float)
    soh = Column(Float)
    soh_bound = Column(Float)