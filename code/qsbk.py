#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# Created on 2017-10-12 01:25:03
# Project: 糗事百科

from pyspider.libs.base_handler import *
from mymodule.public import USER_AGENTS
from mymodule.pyspider.Mysql import Mysql
import re


class Handler(BaseHandler):
    crawl_config = {
        "urls": [
            "https://www.qiushibaike.com/",
            "https://www.qiushibaike.com/hot/",
            "https://www.qiushibaike.com/text/"
        ]
    }

    @every(minutes=10 * 60)
    def on_start(self):
        for url in Handler.crawl_config["urls"]:
            self.crawl(url, callback=self.index_page, validate_cert=False, age=10 * 60 * 60)

    def index_page(self, response):  # 翻页处理
        for div in response.doc('div#content-left > div[id]').items():
            if (not div("div.thumb")):
                self.crawl(div("a.contentHerf").attr.href, callback=self.detail_page, validate_cert=False,
                           age=2 * 24 * 60 * 60)
        self.crawl(response.doc("div#content-left > ul > li:last > a").attr.href, callback=self.index_page,
                   validate_cert=False, age=10 * 60 * 60)

    def detail_page(self, response):
        sender = response.doc("div[id*='qiushi_tag'] > div.author.clearfix > a > h2").text()
        content = response.doc("div[id*='qiushi_tag'] > div#single-next-link > div.content").text()
        content = re.sub("<.*?>", "", content)
        return {
            "sender": sender if sender else "匿名用户",
            "content": content
        }

    def on_result(self, results):
        Mysql().replace(results, "qsbk_default")
