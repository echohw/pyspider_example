#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# Created on 2017-12-04 21:10:23
# Project: 拉钩

from pyspider.libs.base_handler import *
from mymodule.public import getHeaders, stripTag
from mymodule.db.MongoBase import MongoBase
from mymodule.Proxy import Proxy
import time, random

proxyFormat = "http://%s:%s"
mongo = MongoBase(database="pyspider", collection="lagou1204")
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
        self.crawl('https://www.lagou.com/', callback=self.index_page, headers=headers)

    def index_page(self, response):
        """
        对拉钩首页进行解析,提取职位链接并进行抓取
        """
        for tag_a in response.doc('div.menu_box > div.menu_sub.dn > dl > dd > a').items():
            # 保存类型,如java,python
            _type = tag_a.text()
            headers = getHeaders()
            # headers.update(**requests.utils.dict_from_cookiejar(requests.get("https://www.lagou.com/").cookies))
            self.crawl(tag_a.attr.href, save={"type": _type}, callback=self.list_page,headers=headers)  # fetch_type='js'

    @catch_status_code_error  # 应对使用代理时,代理有可能无效的情况
    def list_page(self, response):
        """
        解析职位列表页面
        """
        if isinstance(response.save, str): # 有bug,response.save有时为str
            response.save = {
                "type": response.save
            }
        recrawl = True if response.error else False # 判断代理是否失效,如果代理失效将导致599异常
        if recrawl:
            ip = response.save.get("ip")
            port = response.save.get("port")
            proxyObj.delete(ip, port) # 删除失效的代理
        if ("login" in response.url or recrawl):
            headers = getHeaders()
            ip, port = getProxy()
            response.save["ip"] = ip
            response.save["port"] = port
            self.crawl(response.orig_url, save=response.save, callback=self.list_page, headers=headers,proxy=proxyFormat % (ip, port), itag=str(time.time()))
            return
        for tag_div in response.doc('div#s_position_list > ul.item_con_list > li div.position').items():
            link = tag_div("div.p_top > a.position_link").attr.href  # 提取职位详细页面链接
            work_experi, edu_bg = stripTag(str(tag_div("div.p_bot span").next()), ["i", ""]).split("/")  # 提取工作经验及学历要求
            headers = getHeaders()
            save = {
                "type": response.save.get("type"),
                "work_experi": work_experi,
                "edu_bg": edu_bg
            }
            self.crawl(link, save=save, callback=self.detail_page, headers=headers)
        # 翻页save=response.save
        link_next = response.doc('div.pager_container > a:last').attr.href
        headers = getHeaders()
        self.crawl(link_next, save=response.save.get("type"), callback=self.list_page, headers=headers)

    @catch_status_code_error
    def detail_page(self, response):
        """
        解析职位详细信息页面,提取信息
        """
        if isinstance(response.save, str): # 有bug,response.save有时为str
            response.save = {}
        recrawl = True if response.error else False
        if recrawl:
            ip = response.save.get("ip")
            port = response.save.get("port")
            proxyObj.delete(ip, port)
        if ("login" in response.url or recrawl):
            headers = getHeaders()
            ip, port = getProxy()
            response.save["ip"] = ip
            response.save["port"] = port
            self.crawl(response.orig_url, save=response.save, callback=self.detail_page, headers=headers,proxy=proxyFormat % (ip, port), itag=str(time.time()))
            return
        position = response.doc('div.position-head div.job-name > span').text()  # 职位
        salary = response.doc('div.position-head dd.job_request > p > span:nth-child(1)').text()  # 工资
        require = response.doc('div.position-head dd.job_request > p:nth-child(1)').text().replace(salary, '')  # 要求
        release_time = response.doc('div.position-head dd.job_request > p.publish_time').text().replace('发布于拉勾网', '')  # 发布时间
        welfare = response.doc('dl#job_detail > dd.job-advantage > p').text()  # 职位诱惑
        job_description = response.doc('dl#job_detail > dd.job_bt > div').text()  # 职位描述
        company = response.doc('dl#job_company > dt h2').text().replace(response.doc('dl#job_company > dt h2 span').text(), '')  # 公司
        industry = response.doc('dl#job_company > dd li:nth-child(1)').text().replace("领域", "")  # 行业,领域
        type = response.save.get("type")  # 类型
        addr = response.doc('dl#job_detail > dd.job-address.clearfix > div.work_addr').text().replace('查看地图', '')  # 地址
        work_experi = response.save.get("work_experi")  # 工作经验
        edu_bg = response.save.get("edu_bg")  # 学历要求
        fetch_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())  # 抓取时间
        return {
            'url': response.url,
            '职位': position,
            '工资': salary,
            '要求': require.strip(),
            '发布时间': release_time.strip(),
            '职位诱惑': welfare.strip(),
            '职位描述': job_description.strip(),
            '公司': company.strip(),
            '行业,领域': industry.strip(),
            '类型': type,
            '工作地址': addr.strip(),
            "工作经验": work_experi.strip(),
            "学历要求": edu_bg.strip(),
            '抓取时间': fetch_time
        }

    def on_result(self, result):
        if result:
            mongo.insert(result)
