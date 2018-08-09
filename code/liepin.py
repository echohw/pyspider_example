#!/usr/bin/env python
# -*- encoding: utf-8 -*-

from pyspider.libs.base_handler import *
from pyspider.database.mysql.mysqldb import MySQL
import sys, random, time
import re

reload(sys)
sys.setdefaultencoding('utf-8')


class Handler(BaseHandler):
    my_headers = [
        'Mozilla/5.0 (Windows NT 5.2) AppleWebKit/534.30 (KHTML, like Gecko) Chrome/12.0.742.122 Safari/534.30',
        'Mozilla/5.0 (Windows NT 5.1; rv:5.0) Gecko/20100101 Firefox/5.0',
        'Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 5.2; Trident/4.0; .NET CLR 1.1.4322; .NET CLR 2.0.50727; .NET4.0E; .NET CLR 3.0.4506.2152; .NET CLR 3.5.30729; .NET4.0C)',
        'Opera/9.80 (Windows NT 5.1; U; zh-cn) Presto/2.9.168 Version/11.50',
        'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2272.101 Safari/537.36',
        'Mozilla/5.0 (Windows; U; Windows NT 5.1; zh-CN) AppleWebKit/533.21.1 (KHTML, like Gecko) Version/5.0.5 Safari/533.21.1',
        'Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 5.1; Trident/4.0; .NET CLR 2.0.50727; .NET CLR 3.0.04506.648; .NET CLR 3.5.21022; .NET4.0E; .NET CLR 3.0.4506.2152; .NET CLR 3.5.30729; .NET4.0C)']

    headers = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Encoding": "gzip, deflate, sdch",
        "Accept-Language": "zh-CN,zh;q=0.8",
        "Cache-Control": "max-age=0",
        "Connection": "keep-alive",
        "User-Agent": random.choice(my_headers)
    }

    # str(time.clock())
    crawl_config = {
        "headers": headers,
        "timeout": 100
    }

    @every(minutes=24 * 60)
    def on_start(self):
        self.crawl('https://www.liepin.com/', callback=self.index_page, validate_cert=False)

    @config(age=10 * 24 * 60 * 60)
    def index_page(self, response):
        for each in response.doc('.subsite-btn > a').items():
            # 行业：互联网、房地产、金融、消费品、汽车、医疗
            self.crawl(each.attr.href, callback=self.list_page, validate_cert=False, fetch_type='js')

    def list_page(self, response):
        for each in response.doc('.sidebar > li>dl').items():
            dt = list(each('dt').items())
            dd = list(each('dd').items())
            if not dt or not dd:
                raise Exception("提取dt,dd标签错误,页面地址为:%s" % response.url)
            for index in range(len(dt)):
                type = dt[index].text()
                for item in dd[index]('a').items():
                    self.crawl(item.attr.href, save={"type": type, "preUrl": item.attr.href}, callback=self.list_page_2,
                               validate_cert=False)

    def list_page_2(self, response):
        if response.doc('.selected-condition > dl> dd> span'):
            response.save['preUrl'] = response.url
            self.crawl(response.doc('.selected-condition > dl> dd> span:nth-of-type(1)> a').attr.href,
                       save=response.save, callback=self.list_page_2, validate_cert=False)
        else:
            if not response.doc('.sojob-list > li'):
                raise Exception("找不到li标签,页面地址为:%s" % response.url)
                # self.crawl(self.alterUrl(response.save.get('preUrl')),save=response.save,callback=self.list_page_2,validate_cert=False)
            else:
                for item in response.doc('.sojob-list > li').items():
                    response.save['preUrl'] = item('h3>a').attr.href
                    self.crawl(item('h3>a').attr.href, save=response.save, callback=self.detail_page,
                               validate_cert=False)
                # 翻页
                nextPage = response.doc('div.pagerbar>a:nth-last-of-type(2)').attr.href
                response.save['preUrl'] = nextPage
                self.crawl(nextPage, save=response.save, callback=self.list_page_2, validate_cert=False)

    @config(priority=2)
    def detail_page(self, response):
        if not response.doc('.title-info > h1').text():  # 如果页面中不存在职位信息,则重新抓取该页面
            raise Exception("无法抓取页面详细信息,页面地址为:%s" % response.url)
            # self.crawl(self.alterUrl(response.save.get('preUrl')),save=response.save,callback=self.detail_page,validate_cert=False)
        else:
            position = response.doc('.title-info > h1').text()  # 职位
            salary = response.doc('div.job-title-left>p:first-child').text().replace(
                response.doc('p.job-item-title>span').text(), '')  # 工资
            require = response.doc('div.job-qualifications').text() if response.doc(
                'div.job-qualifications').text() else response.doc('div.resume').text()  # 要求
            time = response.doc('.basic-infor > span:nth-child(2)').text()  # 发布时间
            welfare = response.doc('.tag-list').text() if response.doc('.tag-list').text() else response.doc(
                'div.main>div:first-child>div:nth-of-type(5)>div').text()  # 职位诱惑
            job_description = response.doc('div.main>div:first-child>div:nth-of-type(3)>div').text()  # 职位描述
            other_info = response.doc('div.main>div:first-child>div:nth-of-type(4)>div').text()  # 其他信息
            company = response.doc('.word').text() if response.doc('.word').text() else response.doc(
                'p.company-name').text()  # 公司
            type = response.save['type']  # 类型
            addr = response.doc('.company-infor > p').text() if response.doc(
                '.company-infor > p').text() else response.doc('.basic-infor > span:nth-child(1)').text()  # 地址
            return {
                'url': response.url,
                '职位': position,
                '工资': salary,
                '要求': require,
                '发布时间': time,
                '职位诱惑': welfare,
                '职位描述': job_description,
                '其他信息': other_info,
                '公司': company,
                '类型': type,
                '工作地址': addr
            }

    def on_result(self, result):
        if result:
            print
            result['url']
            if result['职位']:
                with open('C:\\Users\\Administrator\\Desktop\\result.txt', 'a+') as file:
                    for key, value in result.items():
                        file.write(key + ":" + value + "\n")
                    file.write("-------------------[%s]---------------------\n" % (
                    time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())))
                mysql = MySQL()
                mysql.replace(result, tablename='liepin')
            else:
                raise Exception("数据保存失败,页面地址为:%s" % result['url'])




