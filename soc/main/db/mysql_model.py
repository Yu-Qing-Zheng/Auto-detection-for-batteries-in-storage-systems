"""
# @Author: ZeKai
# @Date: 2022-03-07
"""

from sqlalchemy.orm import declarative_base, relationship, sessionmaker
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, FetchedValue, create_engine, Float

engine = create_engine('mysql+pymysql://root:Tmr84937686!@47.92.252.35:3307/dems_Prime_test?charset=utf8',
                       pool_size=30,
                       pool_timeout=3,
                       pool_recycle=60)
Base = declarative_base()


def get_session():
    session_maker = sessionmaker(bind=engine)
    session = session_maker()
    return session


class AppGroup(Base):
    __tablename__ = 'app_group'

    app_group_id = Column(Integer, primary_key=True)
    app_group_name = Column(String(255), nullable=False, unique=True, server_default=FetchedValue())


class Device(Base):
    __tablename__ = 'device'

    device_id = Column(Integer, primary_key=True)
    name = Column(String(45), nullable=False, unique=True)
    status = Column(Integer, nullable=False, server_default=FetchedValue())
    create_time = Column(DateTime, nullable=False, server_default=FetchedValue())
    last_update_time = Column(DateTime, nullable=False, server_default=FetchedValue())
    device_sn = Column(String(45), nullable=False, server_default=FetchedValue())
    run_mode = Column(String(45), nullable=False)
    locked_status = Column(Integer, server_default=FetchedValue())
    error_status = Column(Integer, server_default=FetchedValue())


class Ipc(Base):
    __tablename__ = 'ipc'

    ipc_id = Column(Integer, primary_key=True)
    ipc_sn = Column(String(255), nullable=False)
    need_sync = Column(Integer, nullable=False, server_default=FetchedValue())
    mac = Column(String(31), server_default=FetchedValue())
    project_id = Column(ForeignKey(u'project.project_id'), index=True)
    last_update_time = Column(DateTime, nullable=False, server_default=FetchedValue())
    collect_log = Column(Integer, nullable=False, server_default=FetchedValue())

    project = relationship(u'Project', primaryjoin='Ipc.project_id == Project.project_id', backref=u'ipcs')


class Plc(Base):
    __tablename__ = 'plc'

    plc_id = Column(Integer, primary_key=True, index=True)
    transformer_id = Column(ForeignKey(u'transformer.transformer_id'), nullable=False, index=True)
    template_id = Column(Integer, nullable=False)
    name = Column(String(31), nullable=False, server_default=FetchedValue())
    create_time = Column(DateTime, nullable=False, server_default=FetchedValue())
    device_id = Column(ForeignKey(u'device.device_id'), index=True)
    slave_id = Column(Integer)

    device = relationship(u'Device', primaryjoin='Plc.device_id == Device.device_id', backref=u'plcs')
    transformer = relationship(u'Transformer', primaryjoin='Plc.transformer_id == Transformer.transformer_id',
                               backref=u'plcs')


class PricePolicy(Base):
    __tablename__ = 'price_policy'

    price_policy_id = Column(Integer, primary_key=True)
    setting_update_time = Column(DateTime, nullable=False)
    time_type = Column(String(11), nullable=False)
    start_time = Column(Integer, nullable=False)
    end_time = Column(Integer, nullable=False)
    payment = Column(Float, nullable=False)
    project_id = Column(ForeignKey(u'project.project_id'), nullable=False, index=True)
    expect_update_time = Column(DateTime, nullable=False)
    expiration_time = Column(DateTime)

    project = relationship(u'Project', primaryjoin='PricePolicy.project_id == Project.project_id', backref=u'price_policies')


class Project(Base):
    __tablename__ = 'project'

    project_id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False, unique=True)
    app_group_id = Column(ForeignKey(u'app_group.app_group_id'), nullable=False, index=True)
    address = Column(String(255), nullable=False)
    location = Column(String(255), nullable=False)
    based_pay_mode = Column(String(255), nullable=False)
    device_power = Column(Integer, nullable=False)
    device_energy = Column(Integer, nullable=False)

    app_group = relationship(u'AppGroup', primaryjoin='Project.app_group_id == AppGroup.app_group_id', backref=u'projects')


class Transformer(Base):
    __tablename__ = 'transformer'

    transformer_id = Column(Integer, primary_key=True)
    ipc_id = Column(ForeignKey(u'ipc.ipc_id'), index=True)
    name = Column(String(255), nullable=False, unique=True)
    project_id = Column(ForeignKey(u'project.project_id'), nullable=False, index=True)
    serial_port = Column(String(31))
    rated_power = Column(Integer, nullable=False)
    online_time = Column(DateTime, nullable=False, server_default=FetchedValue())
    reversed2 = Column(String(11))

    ipc = relationship(u'Ipc', primaryjoin='Transformer.ipc_id == Ipc.ipc_id', backref=u'transformers')
    project = relationship(u'Project', primaryjoin='Transformer.project_id == Project.project_id', backref=u'transformers')
