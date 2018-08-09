# -*- encoding: utf-8 -*-
# Created on 2016-05-14 00:16:04
# Project: 91weixinqun

from pyspider.libs.base_handler import *
import re
import urllib2
import datetime
import os
import random


class Handler(BaseHandler):
    crawl_config = {
    }

    @every(minutes=24 * 60)
    def on_start(self):
        self.crawl('http://m.91weixinqun.com/group/index/p/2.html', callback=self.index_page)

    @config(age=30 * 24 * 60 * 60)
    def index_page(self, response):
        for each in response.doc('a[href^="http"]').items():
            if re.match('http://m.91weixinqun.com/qun/\w+.html', each.attr.href, re.U):
                contenturl = each.attr.href
                contenturl = contenturl.replace('m.', 'www.')
                self.count('w')
                count = self.count('r')
                listurl = 'http://m.91weixinqun.com/group/index/p/' + str(random.randint(2, 3240)) + '.html'
                if count % 5 == 0:
                    self.crawl(listurl, callback=self.index_page)
                else:
                    self.crawl(contenturl, callback=self.detail_page)

    @config(priority=2)
    def detail_page(self, response):
        pic = response.doc('.detail_other img').attr.src
        filename = self.filename(response)
        down = self.savejpg(pic, filename[0])
        picurlfilename = filename[1]
        date1 = re.findall(
            r"(\d{2}|\d{4})(?:\-)?([0]{1}\d{1}|[1]{1}[0-2]{1})(?:\-)?([0-2]{1}\d{1}|[3]{1}[0-1]{1})(?:\s)?([0-1]{1}\d{1}|[2]{1}[0-3]{1})(?::)?([0-5]{1}\d{1})",
            response.doc('.detail_line > span').text())
        date = datetime.date(int(date1[0][0]), int(date1[0][1]), int(date1[0][2]))

        return {
            "date": str(date),
            "filename": picurlfilename,
            "url": response.url,
            "title": response.doc('.detail_line > h3').text(),
            "pic": pic,
            "content": response.doc('.detail_line > span').text(),
            "down": down

        }

    def count(self, methed):
        with open('1.txt', 'w+') as f:
            answer = f.read()
            if answer == '':
                answer = 10
                f.write('10')
            if methed == 'r':
                f.close()
                return int(answer)
            if methed == 'w':
                f.write(str(int(answer) + 1))
                f.close()
                return True

    # recoing result function

    def savejpg(self, url, filename):
        request = urllib2.Request(url)
        request.add_header('User-Agent',
                           'Mozilla/5.0 (Windows NT 5.1) AppleWebKit/534.55.3 (KHTML, like Gecko) Version/5.1.5 Safari/534.55.3')
        read = urllib2.urlopen(request).read()
        with open(filename, 'wb') as f:
            f.write(read)
        return True

    def filename(self, response):
        date = datetime.datetime.today()
        dir = '/home/kai/PycharmProjects/pyspiderwx/91wxq-img/'
        dirstr = str(date.year) + '/' + str(date.month) + '/' + str(date.day) + '/'
        filename = re.findall(r"[0-9]+(?=[^0-9]*$)", response.url)[0]
        if os.path.isdir(dir + dirstr):
            pass
        else:
            os.makedirs(dir + dirstr)
        filenamestr = dir + dirstr + filename + '.jpg'
        # '图片url链接放在hdqimg下!!!'
        dirstr = '/img/91wxq-img/' + dirstr + filename + '.jpg'
        return [filenamestr, dirstr]
