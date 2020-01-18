# -*- coding: utf-8 -*-
import scrapy
import logging
from scrapy.loader import ItemLoader
from ..items import Item, FileItem
import base64
from scrapy.conf import settings


class GggsaSpider(scrapy.Spider):
    # 爬虫名
    name = 'gggsa'

    def start_requests(self):
        """
        爬虫起点函数，重写父类方法
        :return: None
        """
        url = 'http://www.gz.chinanews.com/dcsj/2020-01-09/doc-ifzspxvu3515362.shtml'
        # 判断是否有非结构化数据, 如果没有则终止后续代码的执行
        if settings.get('COLLECTDATATYPE') == 'STRUCTURED':
            callback_function = self.only_structured_parse
        elif settings.get('COLLECTDATATYPE') == 'UNSTRUCTURED':
            callback_function = self.only_unstructured_parse
        else:
            callback_function = self.both_parse
        yield scrapy.Request(url=url, callback=callback_function)

    """ 编写自己业务逻辑关系 """

    def only_structured_parse(self, response):
        """
        解析详情页, 采集数据仅有结构化类型数据
        :param response: 请求详情页后返回的 response
        :return: None
        """
        # 实例化正文文本 item， 并给item的各个字段添加值
        item = ItemLoader(item=Item(), response=response)
        item.add_value('url', response.url)
        item.add_xpath('title', 'yourxpath')
        item.add_xpath('dsads', 'yourxpath')
        item.add_xpath('dsad', 'yourxpath')
        yield item.load_item()

    def only_unstructured_parse(self, response):
        """
        解析详情页, 采集数据仅有非结构化类型数据
        :param response: 请求详情页后返回的 response
        :return: None
        """
        # 提取附件信息， 自己写xpath 提取
        attachment_urls = response.xpath('//div[@class="article"]//img/@src').extract()
        # 遍历附件
        for attachment_url in attachment_urls:
            # 请求附件函数
            yield scrapy.Request(
                url=attachment_url,
                callback=self.attachment_parse
            )

    def both_parse(self, response):
        """
        解析详情页
        :param response: 请求详情页后返回的 response
        :return: None
        """
        # 实例化正文文本 item， 并给item的各个字段添加值
        item = ItemLoader(item=Item(), response=response)
        item.add_value('url', response.url)
        item.add_xpath('title', 'yourxpath')
        item.add_xpath('dsads', 'yourxpath')
        item.add_xpath('dsad', 'yourxpath')
        yield item.load_item()
        # 提取附件信息， 自己写xpath 提取
        attachment_urls = response.xpath('//div[@class="article"]//img/@src').extract()
        # 遍历附件
        for attachment_url in attachment_urls:
            # 请求附件函数
            yield scrapy.Request(
                url=attachment_url,
                callback=self.attachment_parse
            )

    def attachment_parse(self, response):
        """
        附件解析函数
        :param response: 请求附件页面后返回的 response
        :return:
        """
        # 实例化附件item
        file_item = ItemLoader(item=FileItem())
        # 计算附件的大小
        file_size = int(len(response.body) / 1024)
        # 将文件bytes类型进行base64 编码
        file_content = base64.b64encode(response.body)
        file_name = response.url.split('/')[-1]
        # 给附件item的各个字段赋值以及返回
        file_item.add_value('url', response.url)
        file_item.add_value('file_name', file_name)
        file_item.add_value('file_label', 'sdsad')
        file_item.add_value('file_type', 'image')
        file_item.add_value('file_size', file_size)
        file_item.add_value('file_content', file_content)
        yield file_item.load_item()
