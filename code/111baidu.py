#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# Created on 2016-06-21 13:34:54
# Project: hc3i_medi_info

from pyspider.libs.base_handler import *
import urllib
import os
import uuid
import urllib2
import cookielib
# from cure4.net.hc3i.mysqldb import SQL
import mysql.connector
from six import itervalues

PAGE_START = 1
PAGE_END = 30
DIR_PATH = 'http://www.cure4.net/hc3i'


class Handler(BaseHandler):
    crawl_config = {
    }

    def __init__(self):
        self.base_url = 'http://www.hc3i.cn/php/search.php?q=医疗信息化'
        self.page_num = PAGE_START
        self.total_num = PAGE_END
        # self.deal = Deal()
        self.saveImage = SaveImage()

    def on_start(self):
        while self.page_num <= self.total_num:
            url = self.base_url + '&p=' + str(self.page_num)
            self.crawl(url, callback=self.index_page)
            self.page_num += 1

    def index_page(self, response):
        for each in response.doc('.res-doc>h2>a').items():
            self.crawl(each.attr.href, callback=self.detail_page)

    def detail_page(self, response):
        subtitle = response.doc('.neck')
        if response.doc('.neck') == None:
            subtitle = response.doc('.service')
        info = subtitle.text().split(' ')
        # 44
        urls = []
        url = UrlParser()
        url.feed(response.doc('.answer').html())
        urls += url.geturls()
        # self.downloadImg(urls)
        # for u in urls:
        # print u
        #   data = self.saveImage.get_file(u)
        #  self.saveImage.save_file(DIR_PATH, "123.jpg", data)
        urlsStr = ""
        if len(urls) > 0:
            urlsStr = urls[0]
            if len(urls) > 1:
                for i in range(len(urls)):
                    if i != 0:
                        urlsStr = urlsStr + " " + urls[i]
        return {
            "url": response.url,
            "title": response.doc('title').text(),
            "message": response.doc('.answer').html(),
            "img": urlsStr,  # urls, #response.doc('.answer>p>a').url,
            # "info":info,
            "time": info[0] + " " + info[1],
            "author": info[2][3:],
            "source": info[3][3:]
        }

    def on_result(self, result):
        # print result
        if not result or not result['title']:
            return
        sql = SQL()
        print
        result
        sql.into('healthnews', **result)


        # 从一个网页url中获取图片的地址，保存在

    # 一个list中返回
    def getUrlList(urlParam):
        urlStream = urllib.urlopen(urlParam)
        htmlString = urlStream.read()
        if (len(htmlString) != 0):
            patternString = r'http://.{0,50}\.jpg'
            searchPattern = re.compile(patternString)
            imgUrlList = searchPattern.findall(htmlString)
            return imgUrlList


            # 生成一个文件名字符串

    def generateFileName(self):
        return str(uuid.uuid1())

    # 根据文件名创建文件
    def createFileWithFileName(self, localPathParam, fileName):
        totalPath = localPathParam + '/' + fileName
        if not os.path.exists(totalPath):
            file = open(totalPath, 'a+')
            file.close()
            return totalPath


            # 根据图片的地址，下载图片并保存在本地

    def getAndSaveImg(self, imgUrl):
        if (len(imgUrl) != 0):
            fileName = self.generateFileName() + '.jpg'
            urllib.urlretrieve(imgUrl, self.createFileWithFileName(DIR_PATH, fileName))





            # 下载函数

    def downloadImg(self, urlList):
        # urlList=getUrlList(url)
        for urlString in urlList:
            self.getAndSaveImg(urlString)


import re


class UrlParser():
    def __init__(self):
        self.urls = []

    def feed(self, data):
        url = re.findall(r"src=\"http.*?jpg", data, re.S | re.I)
        for u in url:
            self.urls.append(u[5:])

    def geturls(self):
        return self.urls


class SaveImage:
    # path  #本地路径
    # file_name #文件名
    # data #文件内容

    def __init__(self):
        return

    # '''获取文件后缀名'''
    def get_file_extension(self, file):
        return os.path.splitext(file)[1]

    # '''創建文件目录，并返回该目录'''
    def mkdir(self, path):
        # 去除左右两边的空格
        path = path.strip()
        # 去除尾部 \符号
        path = path.rstrip("\\")

        if not os.path.exists(path):
            os.makedirs(path)

        return path

    # '''自动生成一个唯一的字符串，固定长度为36'''
    def unique_str(self):
        return str(uuid.uuid1())

    # ''抓取网页文件内容，保存到内存

    # @url 欲抓取文件 ，path+filename
    def get_file(self, url):
        try:
            cj = cookielib.LWPCookieJar()
            opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
            urllib2.install_opener(opener)

            req = urllib2.Request(url)
            operate = opener.open(req)
            data = operate.read()
            return data
        except BaseException, e:
            print
            e
            return None

    # 保存文件到本地



    def save_file(self, path, file_name, data):
        if data == None:
            return

        self.mkdir(path)
        if (not path.endswith("/")):
            path = path + "/"
        file = open(path + file_name, "wb")
        print
        path + file_name
        file.write(data)
        file.flush()
        file.close()

        # 获取文件后缀名
        print
        self.get_file_extension("123.jpg");

        # 創建文件目录，并返回该目录
        # print mkdir("d:/ljq")

        # 自动生成一个唯一的字符串，固定长度为36
        print
        self.unique_str()


import os


class Deal:
    def __init__(self):
        self.path = DIR_PATH
        if not self.path.endswith('/'):
            self.path = self.path + '/'
        if not os.path.exists(self.path):
            os.makedirs(self.path)

    def mkDir(self, path):
        path = path.strip()
        dir_path = self.path + path
        exists = os.path.exists(dir_path)
        if not exists:
            os.makedirs(dir_path)
            return dir_path
        else:
            return dir_path

    def saveImg(self, content, path):
        f = open(path, 'wb')
        f.write(content)
        f.close()

    def saveBrief(self, content, dir_path, name):
        file_name = dir_path + "/" + name + ".txt"
        f = open(file_name, "w+")
        f.write(content.encode('utf-8'))

    def getExtension(self, url):
        extension = url.split('.')[-1]
        return extension


class SQL:
    def __init__(self):

        kwargs = {'host': 'qdm115817567.my3w.com',
                  'user': 'qdm115817567',
                  'passwd': '',
                  'db': 'qdm115817567_db',
                  'charset': 'utf8'}

        hosts = kwargs['host']
        username = kwargs['user']
        password = kwargs['passwd']
        database = kwargs['db']
        charsets = kwargs['charset']

        self.connection = False
        try:
            self.conn = mysql.connector.connect(host=hosts, user=username, passwd=password, db=database,
                                                charset=charsets)
            self.cursor = self.conn.cursor()
            self.cursor.execute("set names " + charsets)
            self.connection = True
        except Exception e:
            print
            "Cannot Connect To Mysql!/n", e

    def escape(self, string):
        return '%s' % string

    def into(self, tablename=None, **values):

        if self.connection:
            tablename = self.escape(tablename)
            if values:
                _keys = ",".join(self.escape(k) for k in values)
                _values = ",".join(['%s', ] * len(values))
                sql_query = "insert into %s (%s) values (%s)" % (tablename, _keys, _values)
                print
                "values:" + sql_query
            else:
                sql_query = "replace into %s default values" % tablename
                print
                "else values:" + sql_query
            try:
                if values:
                    self.cursor.execute(sql_query, list(itervalues(values)))
                else:
                    self.cursor.execute(sql_query)
                self.conn.commit()
                return True
            except Exception, e:
                print
                "An Error Occured: ", e
                return False
