#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# Created on 2016-10-09 15:16:04
# Project: douban_rent

from pyspider.libs.base_handler import *
from pyspider.database.mysql.mysqldb import MySQL
import sys

reload(sys)
sys.setdefaultencoding('utf-8')

groups = {'上海租房': 'https://www.douban.com/group/shanghaizufang/discussion?start=',
          '上海租房@长宁租房/徐汇/静安租房': 'https://www.douban.com/group/zufan/discussion?start=',
          '上海短租日租小组 ': 'https://www.douban.com/group/chuzu/discussion?start=',
          '上海短租': 'https://www.douban.com/group/275832/discussion?start=',
          }


class Handler(BaseHandler):
    crawl_config = {
    }

    # @every(minutes=24*60):on_start方法每天执行一次
    @every(minutes=24 * 60)
    def on_start(self):
        for i in groups:
            url = groups[i] + '0'
            # 传入要爬取的url,回调函数是index_page,关闭ssl验证
            self.crawl(url, callback=self.index_page, validate_cert=False)

    # @config(age=10 * 24 * 60 * 60)request(请求)过期时间是10天,10天内再遇到这个请求直接忽略
    @config(age=10 * 24 * 60 * 60)
    def index_page(self, response):
        # 抓取页面中所有话题内容的a标签
        for each in response.doc('.olt .title a').items():
            # 传入a标签href属性中的值,回调函数是detail_page,
            self.crawl(each.attr.href, callback=self.detail_page, validate_cert=False)

        # 提取页面中下一页的a标签链接
        for each in response.doc('.next a').items():
            # 传入页面中下一页按钮的url地址,回调函数是index_page(递归调用)
            self.crawl(each.attr.href, callback=self.index_page, validate_cert=False)

    @config(priority=2)
    def detail_page(self, response):
        count_not = 0
        notlist = []
        # 提取页面中评论用户的用户名(a标签)
        for i in response.doc('.bg-img-green a').items():
            # 如果评论用户不是发帖用户，那么记录评论人数,并把评论人用户名添加进列表
            if i.text() != response.doc('.from a').text():
                count_not += 1
                notlist.append(i.text())
        for i in notlist: print
        i

        return {
            "url": response.url,  # 页面地址
            "title": response.doc('title').text(),  # 页面标题
            "author": response.doc('.from a').text(),  # 发帖人
            "time": response.doc('.color-green').text(),  # 发帖时间
            "content": response.doc('#link-report p').text(),  # 帖子内容
            "回应数": len([x.text() for x in response.doc('h4').items()]),
            # "最后回帖时间": [x for x in response.doc('.pubtime').items()][-1].text(),
            "非lz回帖数": count_not,
            "非lz回帖人数": len(set(notlist)),
            # "主演": [x.text() for x in response.doc('.actor a').items()],
        }

    def on_result(self, result):
        mysql = MySQL()
        mysql.replace(result, tablename='douban_rent_shanghaizufang')



