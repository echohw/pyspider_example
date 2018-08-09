#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# Created on 2017-12-20 07:35:20
# Project: 智联

from pyspider.libs.base_handler import *
from mymodule.public import getHeaders, stripTag
from mymodule.db.MongoBase import MongoBase
from mymodule.Proxy import Proxy
import time, random, re

proxyFormat = "http://%s:%s"
mongo = MongoBase(database="pyspider", collection="zhilian1220")
proxyObj = Proxy("proxys")

def getProxy():
    return random.choice(proxyObj.get(20, "https"))


class Handler(BaseHandler):
    crawl_config = {
        "validate_cert": False,
        "age": 10 * 24 * 60 * 60,
        "connect_timeout": 30
    }

    def on_start(self):
        headers = getHeaders()
        ip, port = getProxy()
        self.crawl("http://sou.zhaopin.com/", callback=self.index_page, headers=headers,proxy=proxyFormat % (ip, port))

    def index_page(self, response):
        """
        对智联职位搜索页面进行解析,提取职位链接并进行抓取
        """
        for tag_a in response.doc('#search_bottom_content_demo > div.clearfixed > h1 > a').items():
            link = re.sub(re.compile('jl=.*?&', re.S), 'jl=0&', tag_a.attr.href)
            headers = getHeaders()
            ip, port = getProxy()
            self.crawl(link, callback=self.list_page, headers=headers,proxy=proxyFormat % (ip, port))

    def list_page(self, response):
        """
        解析职位列表页面
        """
        for tag_a in response.doc("table.newlist tr:nth-child(1) > td.zwmc > div > a:nth-child(1)").items():
            link = tag_a.attr.href
            headers = getHeaders()
            ip, port = getProxy()
            self.crawl(link, callback=self.detail_page, headers=headers,proxy=proxyFormat % (ip, port))
        # 翻页
        ip, port = getProxy()
        self.crawl(response.doc('.next-page').attr.href, callback=self.list_page,proxy=proxyFormat % (ip, port))

    @config(priority=2)
    def detail_page(self, response):
        """
        解析职位详细信息页面,提取信息
        """
        if "xiaoyuan" in response.url: # 对不同的网页结构使用不同的解析方法
            return self.parse_xiaoyuan(response)
        position = response.doc('body div.fixed-inner-box > div.fl > h1').eq(0).text().strip()  # 职位
        salary = response.doc('div.clearfix > div.terminalpage-left > ul > li:nth-child(1) > strong').text().strip()  # 工资
        release_time = response.doc('#span4freshdate').text()  # 发布时间
        welfare = response.doc('div.fixed-inner-box > div.fl > div.welfare-tab-box').eq(0).text()  # 职位诱惑
        job_description = response.doc('div.clearfix > div.terminalpage-left > div.clearfix > div > div:nth-child(1) p').text().strip()  # 职位描述
        company = response.doc('div.fixed-inner-box > div.fl > h2 > a').eq(0).text()  # 公司
        industry = response.doc("div.company-box > ul > li:nth-child(3) > strong > a").text()  # 行业、领域
        addr = response.doc('div.terminalpage-left > div.clearfix > div > div:nth-child(1) > h2').text().replace(response.doc('.see-map').text(), '').strip()  # 地址
        work_experi = response.doc("div.clearfix > div.terminalpage-left > ul > li:nth-child(5) > strong").text()  # 工作经验
        edu_bg = response.doc("div.clearfix > div.terminalpage-left > ul > li:nth-child(6) > strong").text()  # 学历要求
        fetch_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())  # 抓取时间
        other_info = response.doc('ul.terminal-ul:nth-child(1)').text()  # 其他信息
        return {
            'url': response.url,
            '职位': position,
            '工资': salary,
            "发布时间": release_time,
            '职位诱惑': welfare,
            '职位描述': job_description,
            '公司': company,
            "行业,领域": industry,
            '工作地址': addr,
            "工作经验": work_experi,
            "学历要求": edu_bg,
            '抓取时间': fetch_time,
            '其他信息': other_info
        }

    def parse_xiaoyuan(self,response):
        position = response.doc('#JobName').text().strip()  # 职位
        salary = ""  # 工资
        release_time = response.doc('#liJobPublishDate').text()  # 发布时间
        welfare = ""  # 职位诱惑
        job_description = response.doc("#divMain div.cLeft.l > div.cJobDetail_tabSwitch > div.cJobDetail_tabSwitch_content > div p").text().strip()  # 职位描述
        company = response.doc("#jobCompany").text()  # 公司
        industry = response.doc("#divMain div.cLeft.l > div.cJobDetailInforWrap > ul.cJobDetailInforTopWrap > li:nth-child(4)").text()  # 行业、领域
        addr = response.doc('#currentJobCity').text().strip()  # 地址
        work_experi = ""  # 工作经验
        edu_bg = ""  # 学历要求
        fetch_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())  # 抓取时间
        other_info = response.doc('#divMain div.cLeft.l > div.cJobDetailInforWrap > ul.cJobDetailInforTopWrap.clearfix').text()  # 其他信息
        return {
            'url': response.url,
            '职位': position,
            '工资': salary,
            "发布时间": release_time,
            '职位诱惑': welfare,
            '职位描述': job_description,
            '公司': company,
            "行业,领域": industry,
            '工作地址': addr,
            "工作经验": work_experi,
            "学历要求": edu_bg,
            '抓取时间': fetch_time,
            '其他信息': other_info
        }

    def on_result(self, result):
        if result:
            mongo.insert(result)
