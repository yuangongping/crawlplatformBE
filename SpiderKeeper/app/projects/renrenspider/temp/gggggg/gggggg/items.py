# -*- coding: utf-8 -*-
from .util.field_cleaning import *
import scrapy


class Item(scrapy.Item):
    url = scrapy.Field(output_processor=coommon_cleaning)
    # 文章标题
    title = scrapy.Field(output_processor=title_cleaning)
    # dsadsa
    dsads = scrapy.Field(output_processor=dsads_cleaning)
    # dsadsa
    dsad = scrapy.Field(output_processor=dsad_cleaning)

class FileItem(scrapy.Item):
    # 文件url
    url = scrapy.Field(output_processor=coommon_cleaning)
    # 文件名
    file_name = scrapy.Field(output_processor=coommon_cleaning)
    # 文件标签
    file_label = scrapy.Field(output_processor=coommon_cleaning)
    # 文件类型
    file_type = scrapy.Field(output_processor=coommon_cleaning)
    # 文件大小单位kb
    file_size = scrapy.Field(output_processor=coommon_cleaning)
    # 文件内容
    file_content = scrapy.Field(output_processor=coommon_cleaning)
