#!/usr/bin/env python
# -*- encoding: utf-8 -*-

import re
from pyspider.libs.base_handler import *
from pyspider.database.mysql.mysqldb import MySQL
import sys

reload(sys)
sys.setdefaultencoding('utf-8')


# validate_cert=False,fetch_type='js'

class Handler(BaseHandler):
    crawl_config = {
    }

    @every(minutes=24 * 60)
    def on_start(self):
        # 抓取中国POI数据
        self.crawl('http://www.poi86.com/poi/amap/province/360000.html', callback=self.city_page, validate_cert=False)

    @config(age=24 * 60 * 60)
    def city_page(self, response):
        # 提取地区列表
        for each in response.doc('body > div:nth-child(2) > div > div.panel-body > ul > li > a').items():
            self.crawl(each.attr.href, callback=self.district_page)

    @config(age=24 * 60 * 60)
    def district_page(self, response):
        # 提取子地区列表
        for each in response.doc('body > div:nth-child(2) > div > div.panel-body > ul > li > a').items():
            self.crawl(each.attr.href, callback=self.poi_idx_page)

    @config(age=24 * 60 * 60)
    def poi_idx_page(self, response):
        # 抓取名称的a标签
        for each in response.doc('td > a').items():
            self.crawl(each.attr.href, callback=self.poi_dtl_page)
        # 翻页
        for each in response.doc(
                'body > div:nth-child(2) > div > div.panel-body > div > ul.pagination > li:nth-child(13) > a').items():
            self.crawl(each.attr.href, callback=self.poi_idx_page)

    @config(priority=100)
    def poi_dtl_page(self, response):
        return {
            "url": response.url,
            "id": re.findall('\d+', response.url)[1],
            "name": response.doc('body > div:nth-child(2) > div:nth-child(2) > div.panel-heading > h1').text(),
            "province": response.doc(
                'body > div:nth-child(2) > div:nth-child(2) > div.panel-body > ul > li:nth-child(1) > a').text(),
            "city": response.doc(
                'body > div:nth-child(2) > div:nth-child(2) > div.panel-body > ul > li:nth-child(2) > a').text(),
            "district": response.doc(
                'body > div:nth-child(2) > div:nth-child(2) > div.panel-body > ul > li:nth-child(3) > a').text(),
            "addr": response.doc(
                'body > div:nth-child(2) > div:nth-child(2) > div.panel-body > ul > li:nth-child(4)').text().replace(
                '详细地址:', ''),
            "tel": response.doc(
                'body > div:nth-child(2) > div:nth-child(2) > div.panel-body > ul > li:nth-child(5)').text().replace(
                '电话号码:', ''),
            "type": response.doc(
                'body > div:nth-child(2) > div:nth-child(2) > div.panel-body > ul > li:nth-child(6)').text().replace(
                '所属分类:', ''),
            "dd_map": response.doc(
                'body > div:nth-child(2) > div:nth-child(2) > div.panel-body > ul > li:nth-child(7)').text().replace(
                '大地坐标:', ''),
            "hx_map": response.doc(
                'body > div:nth-child(2) > div:nth-child(2) > div.panel-body > ul > li:nth-child(8)').text().replace(
                '火星坐标:', ''),
            "bd_map": response.doc(
                'body > div:nth-child(2) > div:nth-child(2) > div.panel-body > ul > li:nth-child(9)').text().replace(
                '百度坐标:', ''),
        }

    def on_result(self, result):
        mysql = MySQL()
        mysql.replace(result, tablename='china_poi_data')
