import os
import zipfile


class RenRenSpider:
    def __init__(self, settings):
        self.DISTROOTPATH = "./SpiderKeeper/app/projects/renrenspider/temp"
        self.new_projectname = settings.PROJECT_NAME
        self.ITEMS = settings.ITEMS
        self.DB_IP = settings.DB_IP
        self.DB_NAME = settings.DB_NAME
        self.DB_USERNAME = settings.DB_USERNAME
        self.DB_PASSWORD = settings.DB_PASSWORD
        self.SPIDER_NAME = settings.SPIDER_NAME
        self.TABLE_NAME = settings.TABLE_NAME
        self.TABLE_COMMENTS = settings.TABLE_COMMENTS
        self.DATATYPE = settings.DATATYPE

    def _makedirs(self, path):
        # 将文件与路径切开
        temp = path.split('/')
        # 获得路径与文件名
        filedirs = '/'.join(temp[:-1])
        # 新建路径, 目录是否存在,不存在则创建
        mkdirlambda = lambda x: os.makedirs(x) if not os.path.exists(x) else True
        mkdirlambda(filedirs)

    def process_scrapycfg(self):
        dis_filename = '/'.join([self.DISTROOTPATH, self.new_projectname, 'scrapy.cfg'])
        self._makedirs(dis_filename)
        content_list = [
            "[settings]",
            "default = {}.settings".format(self.new_projectname),
            "",
            "[deploy]",
            "url = http://localhost:6800/".format(self.new_projectname),
            "project = {}".format(self.new_projectname)
        ]
        with open(dis_filename, 'w', encoding='utf-8') as f:
            for content in content_list:
                f.write(content+'\n')

    def process_init(self):
        dis_filename = '/'.join([self.DISTROOTPATH, self.new_projectname,
                                 self.new_projectname, '__init__.py'])
        self._makedirs(dis_filename)
        content_list = ["\n"]
        with open(dis_filename, 'w', encoding='utf-8') as f:
            for content in content_list:
                f.write(content+'\n')

    def process_settings(self):
        dis_filename = '/'.join([self.DISTROOTPATH, self.new_projectname,
                                 self.new_projectname, 'settings.py'])
        self._makedirs(dis_filename)
        content_list = [
            "# -*- coding: utf-8 -*-",
            "import socket",
            "# 工程名",
            "BOT_NAME = '{}'".format(self.new_projectname),
            "SPIDER_MODULES = ['{}.spiders']".format(self.new_projectname),
            "NEWSPIDER_MODULE = '{}.spiders'".format(self.new_projectname),
            "",
            "# 爬虫机器协议，即那些内容可爬取， 那些不可以",
            "ROBOTSTXT_OBEY = False",
            "# 设置日志",
            "LOG_LEVEL = 'INFO'",
            "# 爬虫的并行请求量， 默认16",
            "CONCURRENT_REQUESTS = 1",
            "# 爬虫的下载延迟",
            "DOWNLOAD_DELAY = 0.5",
            "# spider中间件",
            "SPIDER_MIDDLEWARES = {",
            "   '{}.middlewares.{}SpiderMiddleware': 543,".format(self.new_projectname, self.new_projectname.title()),
            "}",
            "# 下载中间件",
            "DOWNLOADER_MIDDLEWARES = {",
            "  '{}.middlewares.{}DownloaderMiddleware': 543,".format(self.new_projectname, self.new_projectname.title()),
            "}",
            "# item 与 pipelines启动设置",
            "ITEM_PIPELINES = {",
            "   '{}.pipelines.{}Pipeline': 300,".format(self.new_projectname, self.new_projectname.title()),
            "}",
            "# 自定义数据采集调度平台数据采集记录系统接口地址",
            "DATARECORDADDRESS = 'http://172.16.119.6:5000/add_record'",
            "",
            "# 非结构化数据（文件、视频、音频、图像 4类）存储接口地址",
            "UNSTRUCTUREDDATASTORAGEADDRESS = 'http://172.16.119.3:1213/savefile'",
            "",
            "# 数据采集类型（STRUCTURED：仅结构化， UNSTRUCTURED: 仅（视频、图像、音频、文件）等非结构化；BOTH二者都有）",
            "COLLECTDATATYPE = '{}'".format(self.DATATYPE),
            "",
            "# 代码所处阶段，分为开发环境（development）与生产环境(production)两个阶段，开发环境表示调试阶段， 生产环境表示正常运行阶段",
            "hostname = socket.gethostname()  # 获取计算机名称",
            "# 获取本机IP",
            "ip = socket.gethostbyname(hostname)",
            "# 如果代码是在服务器上运行， 则连接的是服务器的地址， 否则连接的是自己本地数据库的地址",
            "ENVIRINMENT = 'production' if '172.16.119' in ip else 'development'"
        ]
        with open(dis_filename, 'w', encoding='utf-8') as f:
            for content in content_list:
                f.write(content + '\n')

    def process_middlewares(self):
        dis_filename = '/'.join([self.DISTROOTPATH, self.new_projectname,
                                 self.new_projectname, 'middlewares.py'])
        self._makedirs(dis_filename)
        content_list = [
            "# -*- coding: utf-8 -*-",
            "from scrapy import signals",
            "",
            "",
            "class {}SpiderMiddleware(object):".format(self.new_projectname.title()),
            "    @classmethod",
            "    def from_crawler(cls, crawler):",
            "        s = cls()",
            "        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)",
            "        return s",
            "",
            "    def process_spider_input(self, response, spider):",
            "        return None",
            "",
            "    def process_spider_output(self, response, result, spider):",
            "        for i in result:",
            "            yield i",
            "",
            "    def process_spider_exception(self, response, exception, spider):",
            "        pass",
            "",
            "    def process_start_requests(self, start_requests, spider):",
            "        for r in start_requests:",
            "            yield r",
            "",
            "    def spider_opened(self, spider):"
            "        spider.logger.info('Spider opened: %s' % spider.name)",
            "",
            "",
            "class {}DownloaderMiddleware(object):".format(self.new_projectname.title()),
            "    @classmethod",
            "    def from_crawler(cls, crawler):",
            "        s = cls()",
            "        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)",
            "        return s",
            "",
            "    def process_request(self, request, spider):",
            "        return None",
            "",
            "    def process_response(self, request, response, spider):",
            "        return response",
            "",
            "    def process_exception(self, request, exception, spider):",
            "        pass",
            "",
            "    def spider_opened(self, spider):",
            "        spider.logger.info('Spider opened: %s' % spider.name)",
        ]
        with open(dis_filename, 'w', encoding='utf-8') as f:
            for content in content_list:
                f.write(content + '\n')

    def process_item(self):
        dis_filename = '/'.join([self.DISTROOTPATH, self.new_projectname,
                                 self.new_projectname, 'items.py'])
        self._makedirs(dis_filename)
        content_list = [
            "# -*- coding: utf-8 -*-",
            "from .util.field_cleaning import *",
            "import scrapy",
            "",
            "",
            "class Item(scrapy.Item):",
            "    url = scrapy.Field(output_processor=coommon_cleaning)"
            "",
            "",
            "class FileItem(scrapy.Item):",
            "    # 文件url",
            "    url = scrapy.Field(output_processor=coommon_cleaning)",
            "    # 文件名",
            "    file_name = scrapy.Field(output_processor=coommon_cleaning)",
            "    # 文件标签",
            "    file_label = scrapy.Field(output_processor=coommon_cleaning)",
            "    # 文件类型",
            "    file_type = scrapy.Field(output_processor=coommon_cleaning)",
            "    # 文件大小单位kb",
            "    file_size = scrapy.Field(output_processor=coommon_cleaning)",
            "    # 文件内容",
            "    file_content = scrapy.Field(output_processor=coommon_cleaning)"
        ]
        start = 7
        for item in self.ITEMS:
            value = "    # {}".format(item['value'])
            content_list.insert(start, value)
            start += 1
            value = "    {} = scrapy.Field(output_processor={}_cleaning)".format(
                item['name'], item['name'])
            content_list.insert(start, value)
            start += 1
        # 创建文件
        with open(dis_filename, 'w', encoding='utf-8') as f:
            for content in content_list:
                f.write(content+'\n')

    def process_pipelines(self):
        dis_filename = '/'.join([self.DISTROOTPATH, self.new_projectname,
                                 self.new_projectname, 'pipelines.py'])
        self._makedirs(dis_filename)
        content_list = [
            "# -*- coding: utf-8 -*-",
            "from .items import Item, FileItem",
            "from .mysql_db.operate import session",
            "import logging",
            "import requests",
            "from scrapy.conf import settings",
            "# 判断是否有非结构化数据, 进而选择性导入，建表",
            """if settings.get('COLLECTDATATYPE') == "STRUCTURED":""",
            """    from .mysql_db.tables import OrmTable""",
            """elif settings.get('COLLECTDATATYPE') == "UNSTRUCTURED":""",
            """    from .mysql_db.tables import FileOrmTable""",
            "else:",
            "    from .mysql_db.tables import OrmTable, FileOrmTable"
            "",
            "",
            "class {}Pipeline(object):".format(self.new_projectname.title()),
            "    def __init__(self):",
            "        # 数据库session",
            "        self.session = session",
            "        # 数据总条数",
            "        self.count = 0",
            "        # 图像数量",
            "        self.image_number = 0",
            "        # 视频数量",
            "        self.video_number = 0",
            "        # 音频数据",
            "        self.audio_number = 0",
            "        # 文件数量",
            "        self.file_number = 0",
            "        # 图像大小（单位为kb）",
            "        self.image_size = 0",
            "        # 视频大小",
            "        self.video_size = 0",
            "        # 音频大小",
            "        self.audio_size = 0",
            "        # 文件大小",
            "        self.file_size = 0",
            "",
            "    def close_spider(self, spider):",
            "        self.session.close()",
            "        if settings.get('ENVIRINMENT') == 'production':",
            "            # 向平台发送请求， 保存数据采集量记录",
            "            data = {",
            "                'address': '172.16.119.3',",
            "                'db_name': '{}',".format(self.DB_NAME),
            "                'table_name': '{}',".format(self.TABLE_NAME),
            "                'project_name': settings.get('BOT_NAME'),",
            "                'number': self.count,",
            "                'image_number': self.image_number,",
            "                'video_number': self.video_number,",
            "                'audio_number': self.audio_number,",
            "                'file_number': self.file_number,",
            "                'image_size': self.image_size,",
            "                'video_size': self.video_size,",
            "                'audio_size': self.audio_size,",
            "                'file_size': self.file_size,",
            "            }",
            "            res = requests.post(",
            "                url=settings.get('DATARECORDADDRESS'),",
            "                data=data)",
            "            if not res.status_code == 200:",
            "                logging.info('关闭爬虫时错误，保存数据记录出错！')",
            "",
            "    def update_data_size(self, file_type, size):",
            "        if file_type == 'image':",
            "            self.image_number += 1",
            "            self.image_size += size",
            "        elif file_type == 'video':",
            "            self.video_number += 1",
            "            self.video_size += size",
            "        elif file_type == 'audio':",
            "            self.audio_number += 1",
            "            self.audio_size += size",
            "        elif file_type == 'file':",
            "            self.file_number += 1",
            "            self.file_size += size",
            "",
            "    def process_item(self, item, spider):",
            "        try:",
            "            if isinstance(item, Item):",
            "                obj_instance = OrmTable()",
            "                for k, v in item.items():",
            "                    setattr(obj_instance, k, v)",
            "                self.session.add(obj_instance)",
            "                self.session.commit()",
            "            elif isinstance(item, FileItem):",
            "                # 附件信息存储",
            "                attachment_instance = FileOrmTable()",
            "                for k, v in item.items():",
            "                    if k != 'file_content':",
            "                        setattr(attachment_instance, k, v)",
            "                self.session.add(attachment_instance)",
            "                self.session.commit()",
            "                # 存储附件文件, 以接口方式",
            "                if settings.get('ENVIRINMENT') == 'production':",
            "                    requests.post(",
            "                        url=settings.get('UNSTRUCTUREDDATASTORAGEADDRESS'),",
            "                        data={",
            "                            'project_name': settings.get('BOT_NAME'),",
            "                            'file_name': item.get('file_name'),",
            "                            'content': item.get('file_content')",
            "                        }",
            "                    )",
            "                # 数据统计信息更新",
            "                self.update_data_size(item.get('file_type'), item.get('file_size'))",
            "            # 数据总量变量自增",
            "            self.count += 1",
            "        except Exception as e:",
            "            logging.info(e, '数据存储错误, 字段类型定义出现错误，错误可能值的长度超过了字段定义的长度！')",
            "            self.session.rollback()"
        ]
        # 创建文件
        with open(dis_filename, 'w', encoding='utf-8') as f:
            for content in content_list:
                f.write(content + '\n')

    def process_mysqldb_init(self):
        dis_filename = '/'.join([self.DISTROOTPATH, self.new_projectname,
                                 self.new_projectname, 'mysql_db', '__init__.py'])
        self._makedirs(dis_filename)
        content_list = ["\n"]
        with open(dis_filename, 'w', encoding='utf-8') as f:
            for content in content_list:
                f.write(content+'\n')

    def process_mysqldb_config(self):
        dis_filename = '/'.join([self.DISTROOTPATH, self.new_projectname,
                                 self.new_projectname, 'mysql_db', 'config.py'])
        self._makedirs(dis_filename)
        content_list = [
            "DB_CONFIG_DEBUG = {",
            "    'dbtype': 'mysql+pymysql',",
            "    'host': '{}',".format(self.DB_IP),
            "    'dbname': '{}',".format(self.DB_NAME),
            "    'username': '{}',".format(self.DB_USERNAME),
            "    'password': '{}',".format(self.DB_PASSWORD),
            "    'port': '3306',",
            "    'charset': 'utf8mb4'",
            "}",
            "DB_CONFIG = {",
            "    'dbtype': 'mysql+pymysql',",
            "    'host': '172.16.119.3',",
            "    'dbname': '{}',".format(self.DB_NAME),
            "    'username': 'root',",
            "    'password': 'root',",
            "    'port': '3306',",
            "    'charset': 'utf8mb4'",
            "}",
        ]
        # 创建文件
        with open(dis_filename, 'w', encoding='utf-8') as f:
            for content in content_list:
                f.write(content + '\n')

    def process_mysqldb_operate(self):
        dis_filename = '/'.join([self.DISTROOTPATH, self.new_projectname,
                                 self.new_projectname, 'mysql_db', 'operate.py'])
        self._makedirs(dis_filename)
        content_list = [
            "# -*- coding: utf-8 -*-",
            "from sqlalchemy import create_engine",
            "from sqlalchemy.orm import sessionmaker",
            "from .config import DB_CONFIG, DB_CONFIG_DEBUG",
            "from .tables import Base",
            "from scrapy.conf import settings",
            "",
            "if settings.get('ENVIRINMENT') == 'development':",
            "    config = DB_CONFIG_DEBUG",
            "else:",
            "    config = DB_CONFIG",
            "engine_words = '{}://{}:{}@{}:{}/{}?charset={}'.format(",
            "    config.get('dbtype'),",
            "    config.get('username'),",
            "    config.get('password'),",
            "    config.get('host'),",
            "    config.get('port'),",
            "    config.get('dbname'),",
            "    config.get('charset')",
            ")",
            "engine = create_engine(engine_words)",
            "# 绑定引擎",
            "Session = sessionmaker(bind=engine)",
            "# 生成session",
            "session = Session()",
            "# 自动建表",
            "Base.metadata.create_all(engine)"
        ]
        # 创建文件
        with open(dis_filename, 'w', encoding='utf-8') as f:
            for content in content_list:
                f.write(content + '\n')

    def process_mysqldb_tables(self):
        dis_filename = '/'.join([self.DISTROOTPATH, self.new_projectname, self.new_projectname,
                                 'mysql_db', 'tables.py'])
        self._makedirs(dis_filename)
        content_list = [
            "# -*- coding: utf-8 -*-",
            "from sqlalchemy import *",
            "from sqlalchemy.ext.declarative import declarative_base",
            "import datetime",
            "from scrapy.conf import settings",
            "Base = declarative_base()",
            "",
            "",
            "class OrmTable(Base):",
            "    __tablename__ = '{}'".format(self.TABLE_NAME),
            "    __table_args__ = {{'comment': '{}'}}".format(self.TABLE_COMMENTS),
            "    date_created = Column(DateTime, default=datetime.datetime.now, comment='数据采集时间')",
            "    date_modified = Column(DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now,",
            "                           comment='数据更新时间')",
            "    url = Column(String(255), primary_key=True, comment='数据url地址')",
            "",
            "if settings.get('COLLECTDATATYPE') != 'STRUCTURED':",
            "    class FileOrmTable(Base):",
            "        __tablename__ = '{}_attachment'".format(self.TABLE_NAME),
            "        __table_args__ = {{'comment': '{}_附件信息表'}}".format(self.TABLE_NAME),
            "        date_created = Column(DateTime, default=datetime.datetime.now, comment='数据采集时间')",
            "        date_modified = Column(DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now,",
            "                               comment='数据更新时间')",
            "        url = Column(String(255), primary_key=True, comment='文件url地址')",
            "        file_name = Column(String(255), comment='文件名')",
            "        file_label = Column(String(255), comment='文件分类标签')",
            "        file_type = Column(String(255), comment='文件类型')",
            "        file_size = Column(String(255), comment='文件大小')"
        ]
        start = 15
        for item in self.ITEMS:
            value = "    {} = Column(String(255), comment='{}')".format(
                item['name'], item['value']
            )
            content_list.insert(start, value)
            start += 1
        # 创建文件
        with open(dis_filename, 'w', encoding='utf-8') as f:
            for content in content_list:
                f.write(content + '\n')

    def process_util_init(self):
        dis_filename = '/'.join([self.DISTROOTPATH, self.new_projectname, self.new_projectname,
                                 'util', '__init__.py'])
        self._makedirs(dis_filename)
        content_list = ["\n"]
        with open(dis_filename, 'w', encoding='utf-8') as f:
            for content in content_list:
                f.write(content + '\n')

    def process_util_field_cleaning(self):
        dis_filename = '/'.join([self.DISTROOTPATH, self.new_projectname, self.new_projectname,
                                    'util', 'field_cleaning.py'])
        self._makedirs(dis_filename)
        content_list = [
            "def coommon_cleaning(string, loader_context):",
            "    \"\"\"",
            "    :param string:依据xpath提取的value",
            "     :param loader_context: load的内容， 包括item的key， response， Selector",
            "    :return:修正后的值",
            "    \"\"\"",
            "    if string:",
            "        return string[0]",
            "    return None",
        ]
        # 创建文件
        with open(dis_filename, 'w', encoding='utf-8') as f:
            for content in content_list:
                f.write(content + '\n')

            for item in self.ITEMS:
                content_list_item = [
                    "",
                    "",
                    "def {}_cleaning(string, loader_context):".format(item['name']),
                    "    \"\"\"",
                    "    :param string:依据xpath提取的value",
                    "     :param loader_context: load的内容， 包括item的key， response， Selector",
                    "    :return:修正后的值",
                    "    \"\"\"",
                    "    if string:",
                    "        return string[0]",
                    "    return None",
                ]
                for content in content_list_item:
                    f.write(content + '\n')

    def process_spdiers_init(self):
        dis_filename = '/'.join([self.DISTROOTPATH, self.new_projectname, self.new_projectname,
                                 'spiders', '__init__.py'])
        self._makedirs(dis_filename)
        content_list = ["\n"]
        with open(dis_filename, 'w', encoding='utf-8') as f:
            for content in content_list:
                f.write(content + '\n')

    def process_spiders_spider(self):

        dis_filename = '/'.join([self.DISTROOTPATH, self.new_projectname, self.new_projectname,
                                    'spiders', '{}.py'.format(self.SPIDER_NAME)])
        self._makedirs(dis_filename)
        content_list = [
            "# -*- coding: utf-8 -*-",
            "import scrapy",
            "import logging",
            "from scrapy.loader import ItemLoader",
            "from ..items import Item, FileItem",
            "import base64",
            "from scrapy.conf import settings",
            "",
            "",
            "class {}Spider(scrapy.Spider):".format(self.SPIDER_NAME.title()),
            "    # 爬虫名",
            "    name = '{}'".format(self.SPIDER_NAME),
            "",
            "    def start_requests(self):",
            "        \"\"\"",
            "        爬虫起点函数，重写父类方法",
            "        :return: None",
            "        \"\"\"",
            "        url = 'http://www.gz.chinanews.com/dcsj/2020-01-09/doc-ifzspxvu3515362.shtml'",
            "        # 判断是否有非结构化数据, 如果没有则终止后续代码的执行",
            "        if settings.get('COLLECTDATATYPE') == 'STRUCTURED':",
            "            callback_function = self.only_structured_parse",
            "        elif settings.get('COLLECTDATATYPE') == 'UNSTRUCTURED':",
            "            callback_function = self.only_unstructured_parse",
            "        else:",
            "            callback_function = self.both_parse",
            "        yield scrapy.Request(url=url, callback=callback_function)",
            "",
            "    \"\"\" 编写自己业务逻辑关系 \"\"\"",
            "",
            "    def only_structured_parse(self, response):",
            "        \"\"\"",
            "        解析详情页, 采集数据仅有结构化类型数据",
            "        :param response: 请求详情页后返回的 response",
            "        :return: None",
            "        \"\"\"",
            "        # 实例化正文文本 item， 并给item的各个字段添加值",
            "        item = ItemLoader(item=Item(), response=response)",
            "        item.add_value('url', response.url)",
            "        yield item.load_item()",
            "",
            "    def only_unstructured_parse(self, response):",
            "        \"\"\"",
            "        解析详情页, 采集数据仅有非结构化类型数据",
            "        :param response: 请求详情页后返回的 response",
            "        :return: None",
            "        \"\"\"",
            "        # 提取附件信息， 自己写xpath 提取",
            """        attachment_urls = response.xpath('//div[@class="article"]//img/@src').extract()""",
            "        # 遍历附件",
            "        for attachment_url in attachment_urls:",
            "            # 请求附件函数",
            "            yield scrapy.Request(",
            "                url=attachment_url,",
            "                callback=self.attachment_parse",
            "            )",
            "",
            "    def both_parse(self, response):",
            "        \"\"\"",
            "        解析详情页",
            "        :param response: 请求详情页后返回的 response",
            "        :return: None",
            "        \"\"\"",
            "        # 实例化正文文本 item， 并给item的各个字段添加值",
            "        item = ItemLoader(item=Item(), response=response)",
            "        item.add_value('url', response.url)",
            "        yield item.load_item()",
            "        # 提取附件信息， 自己写xpath 提取",
            """        attachment_urls = response.xpath('//div[@class="article"]//img/@src').extract()""",
            "        # 遍历附件",
            "        for attachment_url in attachment_urls:",
            "            # 请求附件函数",
            "            yield scrapy.Request(",
            "                url=attachment_url,",
            "                callback=self.attachment_parse",
            "            )",
            "",
            "    def attachment_parse(self, response):",
            "        \"\"\"",
            "        附件解析函数",
            "        :param response: 请求附件页面后返回的 response",
            "        :return:",
            "        \"\"\"",
            "        # 实例化附件item",
            "        file_item = ItemLoader(item=FileItem())",
            "        # 计算附件的大小",
            "        file_size = int(len(response.body) / 1024)",
            "        # 将文件bytes类型进行base64 编码",
            "        file_content = base64.b64encode(response.body)",
            "        file_name = response.url.split('/')[-1]",
            "        # 给附件item的各个字段赋值以及返回",
            "        file_item.add_value('url', response.url)",
            "        file_item.add_value('file_name', file_name)",
            "        file_item.add_value('file_label', 'sdsad')",
            "        file_item.add_value('file_type', 'image')",
            "        file_item.add_value('file_size', file_size)",
            "        file_item.add_value('file_content', file_content)",
            "        yield file_item.load_item()",
        ]
        start = 39
        for item in self.ITEMS:
            value = "        item.add_xpath('{}', 'yourxpath')".format(item['name'])
            content_list.insert(start, value)
            start += 1
        start = len(self.ITEMS) + 66
        for item in self.ITEMS:
            value = "        item.add_xpath('{}', 'yourxpath')".format(item['name'])
            content_list.insert(start, value)
            start += 1
        # 创建文件
        with open(dis_filename, 'w', encoding='utf-8') as f:
            for content in content_list:
                f.write(content + '\n')

    def creat_all(self):
        self.process_scrapycfg()
        self.process_init()
        self.process_settings()
        self.process_middlewares()
        self.process_item()
        self.process_pipelines()
        self.process_mysqldb_init()
        self.process_mysqldb_config()
        self.process_mysqldb_operate()
        self.process_mysqldb_tables()
        self.process_util_init()
        self.process_util_field_cleaning()
        self.process_spdiers_init()
        self.process_spiders_spider()

    def zipFile(self):
        """
        压缩指定文件夹
        :param dirpath: 目标文件夹路径
        :param outFullName: 压缩文件保存路径+xxxx.zip
        :return: 无
        """
        dirpath = '/'.join([self.DISTROOTPATH, self.new_projectname])
        outFullName = '/'.join([self.DISTROOTPATH, self.new_projectname+'.zip'])
        zip = zipfile.ZipFile(outFullName, "w", zipfile.ZIP_DEFLATED)
        for path, dirnames, filenames in os.walk(dirpath):
            # 去掉目标跟路径，只对目标文件夹下边的文件及文件夹进行压缩
            fpath = path.replace(dirpath, '')
            for filename in filenames:
                zip.write(os.path.join(path, filename), os.path.join(fpath, filename))
        zip.close()

    def clean(self):
        pass
