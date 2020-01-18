# -*- coding: utf-8 -*-
from sqlalchemy import *
from sqlalchemy.ext.declarative import declarative_base
import datetime
from scrapy.conf import settings
Base = declarative_base()


class OrmTable(Base):
    __tablename__ = 'dsad'
    __table_args__ = {'comment': 'dsadsad'}
    date_created = Column(DateTime, default=datetime.datetime.now, comment='数据采集时间')
    date_modified = Column(DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now,
                           comment='数据更新时间')
    url = Column(String(255), primary_key=True, comment='数据url地址')
    title = Column(String(255), comment='文章标题')
    dsads = Column(String(255), comment='dsadsa')
    dsad = Column(String(255), comment='dsadsa')

if settings.get('COLLECTDATATYPE') != 'STRUCTURED':
    class FileOrmTable(Base):
        __tablename__ = 'dsad_attachment'
        __table_args__ = {'comment': 'dsad_附件信息表'}
        date_created = Column(DateTime, default=datetime.datetime.now, comment='数据采集时间')
        date_modified = Column(DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now,
                               comment='数据更新时间')
        url = Column(String(255), primary_key=True, comment='文件url地址')
        file_name = Column(String(255), comment='文件名')
        file_label = Column(String(255), comment='文件分类标签')
        file_type = Column(String(255), comment='文件类型')
        file_size = Column(String(255), comment='文件大小')
