from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy import Column, Integer, DateTime, create_engine, Float, String

engine = create_engine('mysql+pymysql://root:tmrdatapreprocessing@47.92.133.142:3306/data_preprocessing?charset=utf8',
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
    max_forward = Column(Float)
    max_reverse = Column(Float)

class diagnose_trigger(Base):
    __tablename__ = 'diagnose_trigger'
    plc_id = Column(Integer, primary_key=True, index=True)
    time = Column(DateTime)
    energy_flag = Column(Integer)

class diagnosed_date(Base):
    __tablename__ = 'diagnosed_date'
    Date = Column(DateTime, primary_key=True, index=True)

class sox_calculation(Base):
    __tablename__ = 'sox_calculation'
    ind = Column(Integer, primary_key=True, index=True)
    plc_id = Column(Integer)
    bat_id = Column(String(16))
    time = Column(DateTime)
    voltage = Column(Float)
    current = Column(Float)
    temperature = Column(Float)
    soc = Column(Float)
    soc_bound = Column(Float)
    soh = Column(Float)
    soh_bound = Column(Float)

class diff_sox(Base):
    __tablename__ = 'diff_sox'
    ind = Column(Integer, primary_key=True, index=True)
    plc_id = Column(Integer)
    bat_id = Column(String(16))
    time = Column(DateTime)
    voltage = Column(Float)
    soc = Column(Float)
    soc_bound = Column(Float)
    soh = Column(Float)
    soh_bound = Column(Float)
    voltage_bench = Column(Float)
    soc_bench = Column(Float)
    soc_bound_bench = Column(Float)
    soh_bench = Column(Float)
    soh_bound_bench = Column(Float)
    diff_soc = Column(Float)
    diff_soc_bound = Column(Float)
    diff_soh = Column(Float)
    diff_soh_bound = Column(Float)

class final_conclusions(Base):
    __tablename__ = 'final_conclusions'
    ind = Column(Integer, primary_key=True, index=True)
    plc_id = Column(Integer)
    bat_id = Column(String(16))
    dsoc = Column(Float)
    dsoh = Column(Float)