# from sqlalchemy import *
from sqlalchemy.orm import create_session,sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
from sqlalchemy import create_engine, Table, MetaData, Column,Integer,Text,String,DateTime
# from sqlalchemy.orm import Session
from app.settings.config import DefaultConfig
DB_URI = DefaultConfig.SQLALCHEMY_DATABASE_URI
# DB_URI = 'mysql://product:pl,okm098@172.16.10.7/ps_flag'
Base = declarative_base()
engine = create_engine(DB_URI)
metadata = MetaData(bind=engine)
# 创建事务


def c_session():
    session = sessionmaker(bind=engine)()
    return session


class IndiaOrder(Base):
    # __table__ = Table('india_order_info', metadata, autoload=True)
    __tablename__ = 'india_order_info'
    __table_args__ = {'extend_existing': True}
    id = Column(Integer, primary_key=True, autoincrement=True, comment='id')
    user_id = Column(Integer, comment='用户id')
    username = Column(String(255), comment='用户名')
    agent = Column(String(255), comment='中介名')
    order_id = Column(String(255), comment='订单号')
    file_path = Column(Text, comment='文件路径')
    score = Column(String(255), comment='查重分数')
    status = Column(String(255), default=0, comment='查重状态')
    num_queue = Column(String(255), comment='查重排队情况')
    workload = Column(String(255), comment='工作量', default=0)
    detail_path = Column(Text, comment='查重细节文件位置')
    create_time = Column(DateTime, default=datetime.now, comment='创建时间')
    end_time = Column(DateTime, comment='结束时间')
    workload_time = Column(DateTime, comment='工作量打分时间')
    update_time = Column(DateTime, default=datetime.now, comment='更新时间')


class PublicFile(Base):
    # __table__ = Table('public_file', metadata, autoload=True)
    __tablename__ = 'public_file'
    __table_args__ = {'extend_existing': True}
    id = Column(Integer, primary_key=True, autoincrement=True, comment='id')
    status = Column(String(255), comment='文件状态，是否可以打开')
    file_path = Column(Text, comment='文件路径')
    create_time = Column(DateTime, default=datetime.now, comment='创建时间')


class PublicSent(Base):
    # __table__ = Table('sentence info', metadata, autoload=True)
    __tablename__ = 'sentence info'
    __table_args__ = {'extend_existing': True}
    id = Column(Integer, primary_key=True, autoincrement=True, comment='id')
    sent = Column(Text, comment='句子')
    len_sent = Column(String(255), comment='句子长度')
    p_i = Column(String(255), comment='段落号_句子序号')
    file_path = Column(Text, comment='文件路径')
    create_time = Column(DateTime, default=datetime.now, comment='创建时间')


class InvertTable(Base):
    # __table__ = Table('invert table', metadata, autoload=True)
    __tablename__ = 'invert table'
    __table_args__ = {'extend_existing': True}
    id = Column(Integer, primary_key=True, autoincrement=True, comment='id')
    word = Column(String(255), comment='单词')
    word_sent_list = Column(Text(4294967295), comment='包含单词的句子对应的id，组成的列表')
    create_time = Column(DateTime, default=datetime.now, comment='创建时间')



# with current_app.get_current_object().app_context():
# print(IndiaOrder.query.filter_by(status=0))
# session = c_session()
# data = session.query(IndiaOrder).all()
# # session.close()
# print(data)
# print(session.query(IndiaOrder).all())