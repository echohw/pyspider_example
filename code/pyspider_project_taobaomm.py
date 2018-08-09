#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# Created on 2017-02-11 23:31:03
# Project: taobaomm

from pyspider.libs.base_handler import *

PAGE_START = 1
PAGE_END = 30  # 爬取30页
DIR_PATH = 'd:/var/py/mm'  # 定义保存路径


class Handler(BaseHandler):
    crawl_config = {
    }

    # 初始化
    def __init__(self):
        self.base_url = 'https://mm.taobao.com/json/request_top_list.htm?page='
        self.page_num = PAGE_START
        self.total_num = PAGE_END
        self.deal = Deal()

    def on_start(self):
        while self.page_num <= self.total_num:
            # 构建基础页面url地址
            url = self.base_url + str(self.page_num)
            # 生成爬取任务,并添加到待抓取队列,回调函数是index_page,关闭ssl验证
            self.crawl(url, callback=self.index_page, validate_cert=False)
            self.page_num += 1

    def index_page(self, response):
        for each in response.doc('.lady-name').items():
            # 提取页面中每个用户的链接并爬取,回调函数是detail_page,使用phantom进行页面渲染
            self.crawl(each.attr.href, callback=self.detail_page, fetch_type='js', validate_cert=False)

    def detail_page(self, response):
        # 提取域名地址(//mm.taobao.com/tyy6160)
        domain = response.doc('.mm-p-domain-info li > span').text()
        if domain:
            # 拼接域名地址
            page_url = 'https:' + domain
            # 如果域名地址存在,生成爬取任务并添加到待抓取队列,回调函数是domain_page,关闭ssl验证
            self.crawl(page_url, callback=self.domain_page, validate_cert=False)

    def domain_page(self, response):
        # 提取用户名
        name = response.doc('.mm-p-model-info-left-top dd > a').text()
        # 返回并接收下载路径
        dir_path = self.deal.mkDir(name)
        # 提取个人说明
        brief = response.doc('.mm-aixiu-content').text()
        if dir_path:
            # 提取图片url地址(img标签)
            imgs = response.doc('.mm-aixiu-content img').items()
            count = 1
            # 保存个人说明到文本文件(传入个人说明内容,地址,用户名)
            self.deal.saveBrief(brief, dir_path, name)
            for img in imgs:
                # 提取img标签内的图片url地址
                url = img.attr.src
                if url:
                    # 传入图片url地址,并接收返回后的图片类型(jpg)
                    extension = self.deal.getExtension(url)
                    # 拼接图片名称
                    file_name = name + str(count) + '.' + extension
                    count += 1
                    # 请求图片地址,回调函数是本类中的save_img,关闭ssl验证,并传入地址及图片名参数
                    self.crawl(img.attr.src, callback=self.save_img, validate_cert=False,
                               save={'dir_path': dir_path, 'file_name': file_name})

    # 保存图片
    def save_img(self, response):
        # 图片内容
        content = response.content
        # 保存图片的目录
        dir_path = response.save['dir_path']
        # 图片名
        file_name = response.save['file_name']
        # 拼接图片名
        file_path = dir_path + '/' + file_name
        # 保存图片(向图片中写入内容),传入图片内容,图片保存地址
        self.deal.saveImg(content, file_path)


import os


class Deal:
    # 初始化
    def __init__(self):
        self.path = DIR_PATH
        # 修正文件保存路径,如果不存在则创建
        if not self.path.endswith('/'):
            self.path = self.path + '/'
        if not os.path.exists(self.path):
            os.makedirs(self.path)

    def mkDir(self, path):
        # 接受name变量作为path，去除空格
        path = path.strip()
        # 修正下载路径
        dir_path = self.path + path
        exists = os.path.exists(dir_path)
        # 如果下载路径不存在,则创建,最后返回下载路径
        if not exists:
            os.makedirs(dir_path)
            return dir_path
        else:
            return dir_path

    # 接收图片内容,保存地址
    def saveImg(self, content, path):
        # 打开一张图片,以二进制形式写入内容
        f = open(path, 'wb')
        f.write(content)
        f.close()

    # 保存个人说明,接收个人说明内容,保存地址,用户名
    def saveBrief(self, content, dir_path, name):
        # 拼接文件保存地址,并写入个人说明内容到文本文件
        file_name = dir_path + "/" + name + ".txt"
        f = open(file_name, "w+")
        # 内容以utf-8编码
        f.write(content.encode('utf-8'))

    # 接收图片url地址,然后分割出图片格式并返回
    def getExtension(self, url):
        extension = url.split('.')[-1]
        return extension