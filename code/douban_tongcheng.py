#!/usr/bin/env python
# -*- encoding: utf-8 -*-


import os
import re
import json
import datetime
from libs.pprint import pprint
from pyspider.database.mysql.mysqldb import MySQL
from libs.base_handler import *
import sys

reload(sys)
sys.setdefaultencoding('utf-8')

class Handler(BaseHandler):
    def on_start(self):
        # 抓取豆瓣同城,回调函数是location_page,忽略ssl证书验证
        self.crawl('http://www.douban.com/location/china/', callback=self.location_page, validate_cert=False)

    @config(age=60)
    def location_page(self, response):
        # 抓取地区列表
        for each in response.doc('DIV.location>A').items():
            if 'douban.com/location/' in each.attr.href:
                # 从url中提取地区的拼音
                city = each.attr.href.split('/')[-2]
            else:
                city = each.attr.href.split('.')[0][7:]
            self.crawl('http://www.douban.com/location/%s/events/week-all' % city.replace('/', ""),
                       callback=self.location_page_2, validate_cert=False, fetch_type='js')

    def location_page_2(self, response):
        city = response.doc('div.nav-primary>div.local-label>a.label').text()
        # 抓取地区列表
        for each in response.doc('div#content div.location>a').items():
            # 使用save进行参数传递
            self.crawl(each.attr.href, callback=self.index_page, save=city, validate_cert=False, fetch_type='js')

    @config(age=24 * 60 * 60)
    def index_page(self, response):
        # 提取页面中活动的链接
        for each in response.doc('div#picked-events div.mod.event-mod div.bd div.title>a').items():
            # 传入活动的链接,回调函数是detail_page
            # response.save:获取传递过来的参数
            self.crawl(each.attr.href, callback=self.detail_page, save=response.save, validate_cert=False,
                       fetch_type='js')

    @config(age=24 * 60 * 60)
    def detail_page(self, response):
        generator = response.doc("div.event-detail").items()
        list_ = list(generator)
        return {
            "url": response.url,
            "title": response.doc('title').text()[:-3],
            "time": list_[0]('ul.calendar-strs ').text(),
            "place": list_[1]('span.micro-address[itemprop="address"]').text(),
            "price": list_[2].text().replace("费用:", ""),
            "type": list_[3]('a').text(),
            "city": response.save + "-" + response.doc('DIV.nav-primary>DIV.local-label>A.label').text(),
        }

    def on_result(self, result):
        mysql = MySQL()
        mysql.replace(result, tablename='douban_tongcheng')



