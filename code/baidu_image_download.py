#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# Created on 2017-12-04 21:54:55
# Project: 百度图片下载

import os
import re
import time
import string
import urllib.parse
from pyspider.libs.base_handler import *

js_script = """
function () {
    var check = function(){
        var text=$("#feed_friend_tips > div > p").text();
        var flag="没有更多动态显示";
        if(flag==text){
            return true;
        }else{
            return false;
        }
    };
    var scroll=function () {
        window.scrollTo(0,document.body.scrollHeight);
        if(check()){
            clearInterval(interval);
        }
    };
    var interval=setInterval(scroll,200)
}
"""


class Handler(BaseHandler):
    crawl_config = {
        "keywords": ["电脑壁纸"],
        "rootdir": r"C:\Users\Administrator\Desktop\BaiDuImages",
        "timeout": 20,
        "age": 10 * 24 * 60 * 60,
        "min_size": 204800,  # 200kb
        "itag": 201712051444
    }

    # @config(itag=str(time.time()))
    def on_start(self):
        baseurl = "http://image.baidu.com/search/index?tn=baiduimage&ipn=r&ct=201326592&cl=2&lm=-1&st=-1&fm=result&fr=&sf=1&fmq=1512395952947_R&pv=&ic=0&nc=1&z=&se=1&showtab=0&fb=0&width=&height=&face=0&istype=2&ie=utf-8&hs=2&word=%s"
        for keyword in self.__class__.crawl_config.get("keywords"):
            url = baseurl % urllib.parse.quote(keyword, safe=string.printable)
            self.crawl(url, callback=self.index_page, save={"keyword": keyword}, fetch_type='js', validate_cert=False,
                       js_script=js_script)

    @config(priority=2)
    def index_page(self, response):
        for li_tag in response.doc('li.imgitem').items():
            self.crawl(li_tag.attr("data-objurl"), callback=self.detail_page, save=response.save)

    @catch_status_code_error
    def detail_page(self, response):
        if response.error:
            return
        if len(response.content) < self.__class__.crawl_config["min_size"]:
            return
        image_name = re.sub(r".*/", "", response.url)
        image_dir = os.path.join(self.__class__.crawl_config["rootdir"], response.save.get("keyword"))
        if not os.path.exists(image_dir):
            os.makedirs(image_dir)
        image_path = os.path.join(image_dir, image_name)
        with open(image_path, "wb") as image:
            image.write(response.content)
